from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.review import ReviewLabelOverride, ReviewRead
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/{review_id}", response_model=ReviewRead)
def get_review(review_id: int, db: Session = Depends(get_db)):
    return ReviewService(db).get_review(review_id)


@router.patch("/{review_id}/label", response_model=ReviewRead)
def override_label(review_id: int, data: ReviewLabelOverride, db: Session = Depends(get_db)):
    return ReviewService(db).override_label(review_id, data.recommended)
