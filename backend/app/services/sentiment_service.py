from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ml.predictor import buy_predictor
from app.ml.sentiment_analyser import SentimentSummary, analyse
from app.repositories.product_repository import ProductRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.sentiment import SentimentBreakdownSchema, SentimentSummaryResponse


def _to_response(summary: SentimentSummary) -> SentimentSummaryResponse:
    bd = summary.sentiment_breakdown
    return SentimentSummaryResponse(
        product_id=summary.product_id,
        review_count=summary.review_count,
        avg_rating=summary.avg_rating,
        buy_rate=summary.buy_rate,
        sentiment_breakdown=SentimentBreakdownSchema(
            positive=bd.positive,
            negative=bd.negative,
            neutral=bd.neutral,
            positive_pct=bd.positive_pct,
            negative_pct=bd.negative_pct,
            neutral_pct=bd.neutral_pct,
        ),
        top_keywords=summary.top_keywords,
        top_positive_keywords=summary.top_positive_keywords,
        top_negative_keywords=summary.top_negative_keywords,
    )


class SentimentService:
    def __init__(self, db: Session):
        self.product_repo = ProductRepository(db)
        self.review_repo = ReviewRepository(db)

    def get_summary(self, product_id: int) -> SentimentSummaryResponse:
        if not self.product_repo.get_by_id(product_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found",
            )
        reviews = self.review_repo.get_by_product(product_id)
        summary = analyse(product_id, reviews, buy_predictor.score_text)
        return _to_response(summary)
