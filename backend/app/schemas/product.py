from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProductBase(BaseModel):
    name: str
    brand: str
    category: str
    description: str
    price: float
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ProductSummary(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    price: float
    image_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ProductRecommendation(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    price: float
    image_url: Optional[str] = None
    similarity_score: float
    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    count: int
    results: list[ProductSummary]


class RecommendationResponse(BaseModel):
    product_id: int
    count: int
    results: list[ProductRecommendation]
