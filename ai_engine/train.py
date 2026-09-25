"""Train XGBoost from profiles plus real behavioral activity aggregates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
import xgboost as xgb
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

FEATURES = [
    "profile_pic",
    "nums_in_username",
    "followers",
    "following",
    "account_age",
    "avg_likes_per_post",
    "avg_comments_per_post",
    "url_ratio",
]


def load_dataset(profiles_path: Path, activities_path: Path) -> tuple[pd.DataFrame, pd.Series]:
    profiles = pd.read_csv(profiles_path)
    activities = pd.read_csv(activities_path)
    behavior = activities.groupby("user_id").agg(
        avg_likes=("likes", "mean"),
        avg_comments=("comments", "mean"),
        total_posts=("activity_id", "count"),
        posts_with_url=("contains_url", "sum"),
    ).reset_index()
    behavior["url_ratio"] = behavior["posts_with_url"] / behavior["total_posts"]
    data = profiles.merge(behavior, on="user_id", how="inner")

    username = data["username"].fillna("").astype(str)
    username_length = username.str.len().replace(0, np.nan)
    frame = pd.DataFrame(
        {
            "profile_pic": data["profile_picture"].astype(float),
            "nums_in_username": username.str.count(r"\d").div(username_length).fillna(0),
            "followers": data["followers_count"].astype(float),
            "following": data["following_count"].astype(float),
            "account_age": data["account_age_days"].astype(float),
            "avg_likes_per_post": data["avg_likes"].astype(float),
            "avg_comments_per_post": data["avg_comments"].astype(float),
            "url_ratio": data["url_ratio"].astype(float),
        }
    )
    labels = data["is_fake"].astype(int)
    valid = frame.notna().all(axis=1) & labels.isin([0, 1])
    return frame.loc[valid].astype("float32"), labels.loc[valid]


def make_model() -> xgb.XGBClassifier:
    return xgb.XGBClassifier(
        n_estimators=250,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.9,
        min_child_weight=5,
        reg_lambda=5.0,
        reg_alpha=0.1,
        eval_metric="logloss",
        tree_method="hist",
        device="cuda" if torch.cuda.is_available() else "cpu",
        random_state=42,
    )


def evaluate_model(
    name: str,
    model: xgb.XGBClassifier,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> dict[str, object]:
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    return {
        "experiment": name,
        "features": list(X_train.columns),
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probabilities),
        "classification_report": classification_report(
            y_test, predictions, target_names=["Genuine", "Fake"], output_dict=True
        ),
    }


def train_model(
    profiles_path: Path,
    activities_path: Path,
    output_path: Path,
    report_path: Path,
) -> None:
    X, y = load_dataset(profiles_path, activities_path)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = make_model()
    main_metrics = evaluate_model("all_features", model, X_train, X_test, y_train, y_test)
    print(
        f"Rows: {len(X)} | test: {len(X_test)} | "
        f"device: {model.get_xgb_params()['device']}"
    )
    print(json.dumps({key: main_metrics[key] for key in (
        "accuracy", "precision", "recall", "f1", "roc_auc"
    )}, indent=2))

    gain = model.feature_importances_
    permutation = permutation_importance(
        model, X_test, y_test, n_repeats=5, random_state=42, scoring="accuracy"
    ).importances_mean
    print("Feature importance (gain / permutation):")
    for name, gain_score, permutation_score in zip(FEATURES, gain, permutation):
        print(f"  {name:25s} {gain_score:.4f} / {permutation_score:.4f}")

    experiments = [main_metrics]
    ablations = {
        "without_account_age": [feature for feature in FEATURES if feature != "account_age"],
        "without_profile_picture": [
            feature for feature in FEATURES if feature != "profile_pic"
        ],
        "profile_only": [
            "profile_pic", "nums_in_username", "followers", "following", "account_age"
        ],
        "behavior_only": [
            "avg_likes_per_post", "avg_comments_per_post", "url_ratio"
        ],
    }
    for name, selected_features in ablations.items():
        ablation_model = make_model()
        experiments.append(
            evaluate_model(
                name,
                ablation_model,
                X_train[selected_features],
                X_test[selected_features],
                y_train,
                y_test,
            )
        )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "dataset": {
                    "profiles": str(profiles_path),
                    "activities": str(activities_path),
                    "rows": len(X),
                    "label_counts": y.value_counts().to_dict(),
                },
                "feature_importance": {
                    name: {
                        "gain": float(gain_score),
                        "permutation": float(permutation_score),
                    }
                    for name, gain_score, permutation_score in zip(
                        FEATURES, gain, permutation
                    )
                },
                "experiments": experiments,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Saved experiment report to {report_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    print(f"Saved XGBoost model to {output_path}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    data = root / "model_traning" / "archive (2)"
    parser.add_argument("--profiles", type=Path, default=data / "raw_user_profiles.csv")
    parser.add_argument("--activities", type=Path, default=data / "raw_user_activities.csv")
    parser.add_argument("--output", type=Path, default=root / "models" / "xgboost_model.pkl")
    parser.add_argument(
        "--report",
        type=Path,
        default=root / "models" / "xgboost_experiments.json",
    )
    args = parser.parse_args()
    train_model(args.profiles, args.activities, args.output, args.report)
