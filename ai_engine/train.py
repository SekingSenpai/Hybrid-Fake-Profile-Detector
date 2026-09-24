import pandas as pd
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from pathlib import Path
import os

def train_model():
    # ---------------------------------------------------------------
    # 1. Load BOTH Kaggle datasets
    # ---------------------------------------------------------------
    profiles_path = r"model_traning\archive (2)\raw_user_profiles.csv"
    activities_path = r"model_traning\archive (2)\raw_user_activities.csv"

    if not os.path.exists(profiles_path):
        print(f"Error: {profiles_path} not found.")
        return
    if not os.path.exists(activities_path):
        print(f"Error: {activities_path} not found.")
        return

    profiles_df = pd.read_csv(profiles_path)
    activities_df = pd.read_csv(activities_path)

    print(f"Loaded {len(profiles_df)} profiles and {len(activities_df)} activity records.")

    # ---------------------------------------------------------------
    # 2. Engineer behavioral features from the activities dataset
    # ---------------------------------------------------------------
    # Group all activities by user_id and compute aggregated metrics
    behavior = activities_df.groupby("user_id").agg(
        avg_likes=("likes", "mean"),
        avg_comments=("comments", "mean"),
        total_posts=("activity_id", "count"),
        posts_with_url=("contains_url", "sum"),
    ).reset_index()

    # URL ratio: what fraction of a user's posts contain external links
    behavior["url_ratio"] = behavior["posts_with_url"] / behavior["total_posts"]
    behavior["url_ratio"] = behavior["url_ratio"].fillna(0.0)

    print(f"Computed behavioral features for {len(behavior)} unique users.")

    # ---------------------------------------------------------------
    # 3. Merge profiles + behavioral features on user_id
    # ---------------------------------------------------------------
    merged = profiles_df.merge(behavior, on="user_id", how="inner")
    print(f"Merged dataset contains {len(merged)} profiles with behavioral data.")

    # ---------------------------------------------------------------
    # 4. Preprocess profile-level features (same as before)
    # ---------------------------------------------------------------
    # Profile picture: boolean -> float
    merged['profile_pic'] = merged['profile_picture'].astype(float)

    # Calculate ratio of digits in username
    def calc_num_ratio(username):
        s = str(username)
        if len(s) == 0:
            return 0.0
        return sum(c.isdigit() for c in s) / len(s)

    merged['nums_in_username'] = merged['username'].apply(calc_num_ratio)

    # Map other columns directly
    merged['followers'] = merged['followers_count'].astype(float)
    merged['following'] = merged['following_count'].astype(float)
    merged['account_age'] = merged['account_age_days'].astype(float)

    # Behavioral features are already floats from the aggregation
    merged['avg_likes_per_post'] = merged['avg_likes'].astype(float)
    merged['avg_comments_per_post'] = merged['avg_comments'].astype(float)
    # url_ratio is already computed above

    # Target variable
    merged['is_fake_label'] = merged['is_fake'].astype(int)

    # ---------------------------------------------------------------
    # 5. Define the 8-feature vector and split
    # ---------------------------------------------------------------
    features = [
        'profile_pic',           # 0: Has profile picture (0/1)
        'nums_in_username',      # 1: Ratio of digits in username
        'followers',             # 2: Follower count
        'following',             # 3: Following count
        'account_age',           # 4: Account age in days
        'avg_likes_per_post',    # 5: Average likes per post   [NEW]
        'avg_comments_per_post', # 6: Average comments per post [NEW]
        'url_ratio',             # 7: Fraction of posts with URLs [NEW]
    ]

    X = merged[features]
    y = merged['is_fake_label']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\nTraining set: {len(X_train)} | Test set: {len(X_test)}")
    print("Training XGBoost Model with 8 features (profile + behavioral)...\n")

    # ---------------------------------------------------------------
    # 6. Train the XGBoost Model
    # ---------------------------------------------------------------
    model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric='logloss',
    )
    model.fit(X_train, y_train)

    # ---------------------------------------------------------------
    # 7. Evaluate
    # ---------------------------------------------------------------
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    print("Training Complete!")
    print(f"Model Accuracy on Test Data: {accuracy * 100:.2f}%\n")
    print("Classification Report:")
    print(classification_report(y_test, predictions, target_names=["Genuine", "Fake"]))

    # Feature importance
    print("Feature Importance:")
    for name, score in zip(features, model.feature_importances_):
        print(f"  {name:25s} -> {score:.4f}")

    # ---------------------------------------------------------------
    # 8. Save the Model
    # ---------------------------------------------------------------
    model_dir = Path("models")
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "xgboost_model.pkl"
    joblib.dump(model, model_path)
    print(f"\nModel successfully saved to: {model_path}")


if __name__ == "__main__":
    train_model()
