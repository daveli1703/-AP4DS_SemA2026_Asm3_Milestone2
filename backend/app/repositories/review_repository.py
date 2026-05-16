from sqlalchemy.orm import Session
from app.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, review_id: int) -> Review | None:
        return self.db.query(Review).filter(Review.id == review_id).first()

    def get_by_product(self, product_id: int) -> list[Review]:
        return self.db.query(Review).filter(Review.product_id == product_id).all()

    def create(self, review: Review) -> Review:
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def save(self, review: Review) -> Review:
        self.db.commit()
        self.db.refresh(review)
        return review
