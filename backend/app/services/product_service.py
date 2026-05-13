from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ml.search_engine import product_search_engine
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, SearchResponse


class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def search(self, query: str) -> SearchResponse:
        ranked = product_search_engine.search(query)
        if not ranked:
            return SearchResponse(count=0, results=[])
        id_order = {pid: idx for idx, (pid, _) in enumerate(ranked)}
        products = self.repo.get_by_ids([pid for pid, _ in ranked])
        products.sort(key=lambda p: id_order[p.id])
        return SearchResponse(count=len(products), results=products)

    def get_product(self, product_id: int) -> Product:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found")
        return product

    def get_all(self, skip: int = 0, limit: int = 20) -> list[Product]:
        return self.repo.get_all(skip, limit)

    def create(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        return self.repo.create(product)
