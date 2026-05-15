from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.product import (
    ProductFiltersResponse,
    ProductRead,
    ProductSummary,
    RecommendationResponse,
    SearchResponse,
)
from app.schemas.review import ReviewCreate, ReviewRead
from app.schemas.sentiment import SentimentSummaryResponse
from app.services.product_service import ProductService
from app.services.recommendation_service import RecommendationService
from app.services.review_service import ReviewService
from app.services.sentiment_service import SentimentService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/search", response_model=SearchResponse)
def search_products(
    q: str = Query(..., min_length=1),
    brand: str | None = None,
    category: str | None = None,
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    return ProductService(db).search(q, brand, category, min_price, max_price)


@router.get("/filters", response_model=ProductFiltersResponse)
def get_product_filters(db: Session = Depends(get_db)):
    return ProductService(db).get_filters()


@router.get("", response_model=list[ProductSummary])
def list_products(
    skip: int = 0,
    limit: int = 20,
    brand: str | None = None,
    category: str | None = None,
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    return ProductService(db).get_all(skip, limit, brand, category, min_price, max_price)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return ProductService(db).get_product(product_id)


@router.get("/{product_id}/reviews", response_model=list[ReviewRead])
def get_product_reviews(
    product_id: int,
    sort: str = "newest",
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return ReviewService(db).get_reviews_for_product(product_id, sort, skip, limit)


@router.post("/{product_id}/reviews", response_model=ReviewRead, status_code=201)
def create_review(product_id: int, data: ReviewCreate, db: Session = Depends(get_db)):
    return ReviewService(db).create_review(product_id, data)


@router.get("/{product_id}/recommendations", response_model=RecommendationResponse)
def get_recommendations(product_id: int, top_k: int = 5, db: Session = Depends(get_db)):
    return RecommendationService(db).get_recommendations(product_id, top_k)


@router.get("/{product_id}/sentiment-summary", response_model=SentimentSummaryResponse)
def get_sentiment_summary(product_id: int, db: Session = Depends(get_db)):
    return SentimentService(db).get_summary(product_id)
