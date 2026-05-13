from sqlalchemy.orm import Session
from app.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, review_id: int) -> Review | None:
        return self.db.query(Review).filter(Review.id == review_id).first()

    def get_by_product(self, product_id: int) -> list[Review]:
        return self.db.query(Review).filter(Review.product_id == product_id).all()

    def get_by_product_page(
        self,
        product_id: int,
        sort: str = "newest",
        skip: int = 0,
        limit: int = 10,
    ) -> list[Review]:
        query = self.db.query(Review).filter(Review.product_id == product_id)

        if sort == "oldest":
            order_by = (Review.created_at.asc(), Review.id.asc())
        elif sort == "rating_desc":
            order_by = (Review.rating.desc(), Review.created_at.desc())
        elif sort == "rating_asc":
            order_by = (Review.rating.asc(), Review.created_at.desc())
        else:
            order_by = (Review.created_at.desc(), Review.id.desc())

        return query.order_by(*order_by).offset(skip).limit(limit).all()

    def create(self, review: Review) -> Review:
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def save(self, review: Review) -> Review:
        self.db.commit()
        self.db.refresh(review)
        return review
