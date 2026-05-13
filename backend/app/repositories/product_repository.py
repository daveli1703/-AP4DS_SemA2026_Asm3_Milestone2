from sqlalchemy import func
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

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        brand: str | None = None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> list[Product]:
        query = self.db.query(Product)
        if brand:
            query = query.filter(Product.brand == brand)
        if category:
            query = query.filter(Product.category == category)
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        return query.offset(skip).limit(limit).all()

    def get_all_products(self) -> list[Product]:
        return self.db.query(Product).all()

    def get_filter_options(self) -> tuple[list[str], list[str], float | None, float | None]:
        brands = [
            row[0]
            for row in self.db.query(Product.brand)
            .filter(Product.brand.is_not(None))
            .distinct()
            .order_by(Product.brand)
            .all()
            if row[0]
        ]
        categories = [
            row[0]
            for row in self.db.query(Product.category)
            .filter(Product.category.is_not(None))
            .distinct()
            .order_by(Product.category)
            .all()
            if row[0]
        ]
        price_min, price_max = self.db.query(
            func.min(Product.price), func.max(Product.price)
        ).one()
        return brands, categories, price_min, price_max

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
