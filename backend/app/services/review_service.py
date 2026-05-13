import csv
import os
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.ml.predictor import buy_predictor
from app.models.review import Review
from app.repositories.product_repository import ProductRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.review import ReviewCreate


class ReviewService:
    def __init__(self, db: Session):
        self.repo = ReviewRepository(db)
        self.product_repo = ProductRepository(db)
        self.db = db

    def get_review(self, review_id: int) -> Review:
        review = self.repo.get_by_id(review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Review {review_id} not found")
        return review

    def get_reviews_for_product(self, product_id: int) -> list[Review]:
        return self.repo.get_by_product(product_id)

    def create_review(self, product_id: int, data: ReviewCreate) -> Review:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found")

        # Compute product-level stats from existing reviews for the M3 model input
        agg = (
            self.db.query(
                func.avg(Review.rating).label("avg_rating"),
                func.count(Review.id).label("count"),
            )
            .filter(Review.product_id == product_id)
            .one()
        )
        avg_product_rating = float(agg.avg_rating or 0.0)
        product_rating_count = float(agg.count or 0.0)

        result = buy_predictor.predict_full(
            review_text=data.review_text,
            rating=data.rating,
            review_title=data.review_title or "",
            price=product.price,
            avg_product_rating=avg_product_rating,
            product_rating_count=product_rating_count,
            brand_name=product.brand,
            product_title=product.name,
        )

        predicted = result.predicted_recommended
        final_label = data.recommended if data.recommended is not None else predicted

        review = Review(
            product_id=product_id,
            reviewer_name=data.reviewer_name,
            rating=data.rating,
            review_title=data.review_title,
            review_text=data.review_text,
            predicted_recommended=predicted,
            recommended=final_label,
            user_overridden=data.recommended is not None,
            ensemble_score=result.ensemble_score,
            model_scores_json=result.scores_json(),
        )
        review = self.repo.create(review)
        self._append_to_csv(review)
        return review

    def override_label(self, review_id: int, recommended: bool) -> Review:
        review = self.get_review(review_id)
        review.recommended = recommended
        review.user_overridden = True
        return self.repo.save(review)

    def _append_to_csv(self, review: Review) -> None:
        path = settings.reviews_csv_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        file_exists = os.path.isfile(path)
        fields = [
            "id", "product_id", "reviewer_name", "rating", "review_title", "review_text",
            "predicted_recommended", "recommended", "user_overridden",
            "ensemble_score", "model_scores_json", "created_at",
        ]
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "id": review.id,
                "product_id": review.product_id,
                "reviewer_name": review.reviewer_name,
                "rating": review.rating,
                "review_title": review.review_title or "",
                "review_text": review.review_text,
                "predicted_recommended": review.predicted_recommended,
                "recommended": review.recommended,
                "user_overridden": review.user_overridden,
                "ensemble_score": review.ensemble_score,
                "model_scores_json": review.model_scores_json,
                "created_at": review.created_at.isoformat() if review.created_at else "",
            })
