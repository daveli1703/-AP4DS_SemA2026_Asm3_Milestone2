from fastapi import HTTPException, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.ml.recommender import ReviewStats, recommendation_index
from app.models.review import Review
from app.schemas.product import ProductRecommendation, RecommendationResponse


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    def get_recommendations(self, product_id: int, top_k: int = 5) -> RecommendationResponse:
        if not recommendation_index._ready or product_id not in recommendation_index._id_to_idx:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found",
            )
        results = recommendation_index.recommend(product_id, top_k)
        recommendations = [
            ProductRecommendation(
                id=sr.product.id,
                name=sr.product.name,
                brand=sr.product.brand,
                category=sr.product.category,
                price=sr.product.price,
                image_url=sr.product.image_url,
                similarity_score=sr.similarity_score,
            )
            for sr in results
        ]
        return RecommendationResponse(
            product_id=product_id,
            count=len(recommendations),
            results=recommendations,
        )

    @staticmethod
    def compute_review_stats(db: Session) -> dict[int, ReviewStats]:
        rows = (
            db.query(
                Review.product_id,
                func.avg(Review.rating).label("avg_rating"),
                func.count(Review.id).label("review_count"),
                func.sum(case((Review.recommended == True, 1), else_=0)).label("buyer_count"),
            )
            .group_by(Review.product_id)
            .all()
        )
        stats: dict[int, ReviewStats] = {}
        for row in rows:
            count = int(row.review_count or 0)
            buyers = int(row.buyer_count or 0)
            stats[row.product_id] = ReviewStats(
                avg_rating=float(row.avg_rating or 0.0),
                buy_rate=buyers / count if count > 0 else 0.5,
                review_count=count,
            )
        return stats
