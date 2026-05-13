import json
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Any, Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    reviewer_name: str
    rating: float = Field(..., ge=1.0, le=5.0)
    review_title: Optional[str] = None
    review_text: str
    recommended: Optional[bool] = None  # optional user override before prediction


class ReviewRead(BaseModel):
    id: int
    product_id: int
    reviewer_name: str
    rating: float
    review_title: Optional[str]
    review_text: str
    predicted_recommended: Optional[bool]
    recommended: Optional[bool]
    user_overridden: bool
    ensemble_score: Optional[float]
    model_scores: Optional[dict] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def _deserialise_model_scores(cls, data: Any) -> Any:
        # When reading from ORM, model_scores_json is a JSON string; parse it here.
        if hasattr(data, "model_scores_json"):
            raw = data.model_scores_json
            scores = None
            if raw:
                try:
                    scores = json.loads(raw)
                except Exception:
                    pass
            # Build a plain dict that Pydantic can consume
            return {
                "id": data.id,
                "product_id": data.product_id,
                "reviewer_name": data.reviewer_name,
                "rating": data.rating,
                "review_title": getattr(data, "review_title", None),
                "review_text": data.review_text,
                "predicted_recommended": data.predicted_recommended,
                "recommended": data.recommended,
                "user_overridden": data.user_overridden,
                "ensemble_score": getattr(data, "ensemble_score", None),
                "model_scores": scores,
                "created_at": data.created_at,
            }
        return data


class ReviewLabelOverride(BaseModel):
    recommended: bool
