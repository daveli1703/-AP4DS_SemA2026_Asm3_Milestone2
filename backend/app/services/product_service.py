from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ml.search_engine import product_search_engine
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductFiltersResponse, SearchResponse


class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def search(
        self,
        query: str,
        brand: str | None = None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> SearchResponse:
        ranked = product_search_engine.search(query)
        if not ranked:
            return SearchResponse(count=0, results=[])
        id_order = {pid: idx for idx, (pid, _) in enumerate(ranked)}
        products = self.repo.get_by_ids([pid for pid, _ in ranked])
        products.sort(key=lambda p: id_order[p.id])
        products = self._apply_filters(products, brand, category, min_price, max_price)
        return SearchResponse(count=len(products), results=products)

    def get_product(self, product_id: int) -> Product:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {product_id} not found")
        return product

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        brand: str | None = None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> list[Product]:
        return self.repo.get_all(skip, limit, brand, category, min_price, max_price)

    def get_filters(self) -> ProductFiltersResponse:
        brands, categories, price_min, price_max = self.repo.get_filter_options()
        return ProductFiltersResponse(
            brands=brands,
            categories=categories,
            price_min=price_min,
            price_max=price_max,
        )

    def create(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        return self.repo.create(product)

    @staticmethod
    def _apply_filters(
        products: list[Product],
        brand: str | None,
        category: str | None,
        min_price: float | None,
        max_price: float | None,
    ) -> list[Product]:
        if not any([brand, category, min_price is not None, max_price is not None]):
            return products
        filtered: list[Product] = []
        for p in products:
            if brand and p.brand != brand:
                continue
            if category and p.category != category:
                continue
            if min_price is not None and p.price < min_price:
                continue
            if max_price is not None and p.price > max_price:
                continue
            filtered.append(p)
        return filtered
