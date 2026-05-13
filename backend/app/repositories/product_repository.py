from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_ids(self, ids: list[int]) -> list[Product]:
        if not ids:
            return []
        return self.db.query(Product).filter(Product.id.in_(ids)).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Product]:
        return self.db.query(Product).offset(skip).limit(limit).all()

    def get_all_products(self) -> list[Product]:
        return self.db.query(Product).all()

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
