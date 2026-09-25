"""
Hybrid Fake Profile Detector — AI Engine
=========================================
FastAPI service that exposes a /predict endpoint.

Scoring pipeline
----------------
1. XGBoost   → trained on 8 tabular features (profile + behavioral)
2. DistilBERT → sentiment/authenticity from bio text

Combined score = 0.6 * xgboost_prob + 0.4 * distilbert_prob
A `conflict_flag` is raised when |xgboost - distilbert| > 0.5.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import xgboost as xgb
import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("ai_engine")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
XGBOOST_MODEL_PATH = os.getenv(
    "XGBOOST_MODEL_PATH",
    str(Path(__file__).resolve().parent / "models" / "xgboost_model.pkl"),
)
DISTILBERT_MODEL_NAME = os.getenv(
    "DISTILBERT_MODEL_NAME",
    str(Path(__file__).resolve().parent / "models" / "distilbert-finetuned"),
)
DISTILBERT_FALLBACK_MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
XGBOOST_WEIGHT = 0.6
DISTILBERT_WEIGHT = 0.4
CONFLICT_THRESHOLD = 0.5

# ---------------------------------------------------------------------------
# Global model holders (populated during lifespan startup)
# ---------------------------------------------------------------------------
xgb_model: xgb.XGBClassifier | None = None
tokenizer: AutoTokenizer | None = None
bert_model: AutoModelForSequenceClassification | None = None
device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
distilbert_fake_label = 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_placeholder_xgboost() -> xgb.XGBClassifier:
    """Train a tiny placeholder XGBoost model so the pipeline works end‑to‑end
    even without a real pre‑trained artefact."""
    logger.warning("No pre-trained XGBoost model found – building placeholder.")
    rng = np.random.RandomState(42)
    X = rng.rand(200, 8)  # 8 features now
    y = (X.sum(axis=1) > 4.0).astype(int)
    model = xgb.XGBClassifier(
        n_estimators=50,
        max_depth=3,
        use_label_encoder=False,
        eval_metric="logloss",
    )
    model.fit(X, y)

    # Persist so subsequent restarts reuse the same weights.
    model_dir = Path(XGBOOST_MODEL_PATH).parent
    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, XGBOOST_MODEL_PATH)
    logger.info("Placeholder XGBoost model saved to %s", XGBOOST_MODEL_PATH)
    return model


def _load_xgboost() -> xgb.XGBClassifier:
    if Path(XGBOOST_MODEL_PATH).is_file():
        logger.info("Loading XGBoost model from %s", XGBOOST_MODEL_PATH)
        return joblib.load(XGBOOST_MODEL_PATH)
    return _build_placeholder_xgboost()


def _load_distilbert() -> tuple[AutoTokenizer, AutoModelForSequenceClassification]:
    model_name = (
        DISTILBERT_MODEL_NAME
        if Path(DISTILBERT_MODEL_NAME).exists()
        else DISTILBERT_FALLBACK_MODEL_NAME
    )
    if model_name != DISTILBERT_MODEL_NAME:
        logger.warning(
            "Fine-tuned DistilBERT not found at %s; using fallback checkpoint %s",
            DISTILBERT_MODEL_NAME,
            model_name,
        )
    logger.info("Loading DistilBERT tokenizer & model: %s", model_name)
    tok = AutoTokenizer.from_pretrained(model_name)
    mdl = AutoModelForSequenceClassification.from_pretrained(model_name)
    mdl.to(device)
    mdl.eval()
    global distilbert_fake_label
    labels = {str(value).upper() for value in mdl.config.id2label.values()}
    distilbert_fake_label = next(
        (index for index, label in mdl.config.id2label.items() if "FAKE" in str(label).upper()),
        0 if "NEGATIVE" in labels else 1,
    )
    return tok, mdl


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Load heavy artefacts once at startup."""
    global xgb_model, tokenizer, bert_model  # noqa: PLW0603

    xgb_model = _load_xgboost()
    tokenizer, bert_model = _load_distilbert()
    logger.info("All models loaded – AI Engine ready.")
    yield
    logger.info("AI Engine shutting down.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Hybrid Fake Profile Detector – AI Engine",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ProfileFeatures(BaseModel):
    """Tabular features expected by the XGBoost model.

    The model uses 8 numeric features in this order:
      0: profile_pic           (0.0 or 1.0)
      1: nums_in_username       (ratio of digits in username)
      2: followers              (follower count)
      3: following              (following count)
      4: account_age            (days since creation)
      5: avg_likes_per_post     (mean likes across posts)
      6: avg_comments_per_post  (mean comments across posts)
      7: url_ratio              (fraction of posts containing URLs)
    """
    features: list[float] = Field(
        ...,
        min_length=8,
        max_length=8,
        description="8-element numeric feature vector for XGBoost.",
    )
    bio_text: str = Field(
        ...,
        min_length=1,
        description="Profile biography / description text for DistilBERT.",
    )


class PredictionResponse(BaseModel):
    combined_probability: float = Field(
        ..., description="Weighted average: 0.6·XGB + 0.4·BERT"
    )
    xgboost_score: float
    distilbert_score: float
    conflict_flag: bool = Field(
        ...,
        description="True when |xgboost_score − distilbert_score| > 0.5",
    )


# ---------------------------------------------------------------------------
# Inference helpers
# ---------------------------------------------------------------------------

def predict_xgboost(features: list[float]) -> float:
    """Return the positive‑class probability from the XGBoost model."""
    arr = np.asarray(features).reshape(1, -1)
    proba = xgb_model.predict_proba(arr)  # type: ignore[union-attr]
    return float(proba[0][1])


def predict_distilbert(text: str) -> float:
    """Return the probability assigned to the model's fake-risk label."""
    inputs = tokenizer(  # type: ignore[misc]
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        logits = bert_model(**inputs).logits  # type: ignore[union-attr]
    probs = torch.softmax(logits, dim=-1)

    # Check for strong spam / promotional keywords in bio
    text_lower = text.lower()
    spam_keywords = ["crypto", "free", "dm me", "link in bio", "whatsapp", "telegram", "cash", "giveaway", "invest", "bonus", "http", "www"]
    has_spam_keyword = any(kw in text_lower for kw in spam_keywords)

    fake_prob = float(probs[0][distilbert_fake_label].item())

    if has_spam_keyword and fake_prob < 0.7:
        fake_prob = max(fake_prob, 0.85)

    return fake_prob


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["ops"])
async def health_check():
    """Lightweight liveness probe."""
    return {"status": "healthy"}


@app.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["inference"],
    summary="Predict whether a profile is fake",
)
async def predict(payload: ProfileFeatures) -> PredictionResponse:
    """Run the hybrid scoring pipeline and return a combined probability."""
    try:
        xgb_score = predict_xgboost(payload.features)
    except Exception as exc:
        logger.exception("XGBoost prediction failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"XGBoost inference error: {exc}",
        ) from exc

    try:
        bert_score = predict_distilbert(payload.bio_text)
    except Exception as exc:
        logger.exception("DistilBERT prediction failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DistilBERT inference error: {exc}",
        ) from exc

    combined = XGBOOST_WEIGHT * xgb_score + DISTILBERT_WEIGHT * bert_score
    conflict = abs(xgb_score - bert_score) > CONFLICT_THRESHOLD

    logger.info(
        "Prediction → XGB=%.4f  BERT=%.4f  combined=%.4f  conflict=%s",
        xgb_score,
        bert_score,
        combined,
        conflict,
    )

    return PredictionResponse(
        combined_probability=round(combined, 6),
        xgboost_score=round(xgb_score, 6),
        distilbert_score=round(bert_score, 6),
        conflict_flag=conflict,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
