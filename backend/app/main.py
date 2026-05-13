from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.base import Base
from app.database.migrations import run_migrations
from app.database.session import SessionLocal, engine
from app.ml.recommender import recommendation_index
from app.ml.search_engine import product_search_engine
from app.models.product import Product
from app.routers import products, reviews
from app.services.recommendation_service import RecommendationService

Base.metadata.create_all(bind=engine)
run_migrations(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        all_products = db.query(Product).all()
        product_search_engine.build(all_products)
        review_stats = RecommendationService.compute_review_stats(db)
        recommendation_index.build(all_products, review_stats)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(reviews.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "app": settings.app_name}
