from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    reviewer_name = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    review_title = Column(String, nullable=True)
    review_text = Column(String, nullable=False)
    predicted_recommended = Column(Boolean, nullable=True)
    recommended = Column(Boolean, nullable=True)
    user_overridden = Column(Boolean, default=False, nullable=False)
    ensemble_score = Column(Float, nullable=True)
    model_scores_json = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    product = relationship("Product", back_populates="reviews")
