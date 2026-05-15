import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models.product import Product
from app.models.review import Review

CSV_PATH = Path(__file__).parent / "cosmetics_beauty_products_reviews.csv"


def _float(val: str, default: float = 0.0) -> float:
    try:
        return float(val.strip())
    except (ValueError, AttributeError):
        return default


def _bool(val: str) -> bool:
    return val.strip().upper() == "TRUE"


def _date(val: str) -> datetime:
    try:
        return datetime.strptime(val.strip(), "%d/%m/%Y %H:%M")
    except ValueError:
        return datetime.utcnow()


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(Product).first():
            print("Database already has data — skipping seed. Delete beauty_shop.db to re-seed.")
            return

        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        print(f"Loaded {len(rows)} rows from CSV.")

        # ext product_id (from CSV) → internal SQLAlchemy Product.id
        product_map: dict[str, int] = {}
        products_added = 0
        reviews_added = 0

        for row in rows:
            ext_id = row["product_id"].strip()

            if ext_id not in product_map:
                tags = row["product_tags"].strip()
                category = tags.split(",")[0].strip() if tags else "General"

                product = Product(
                    name=row["product_title"].strip(),
                    brand=row["brand_name"].strip(),
                    category=category,
                    description=row["product_title"].strip(),
                    price=_float(row["price"]),
                    image_url=f"https://picsum.photos/seed/product{ext_id}/400/400",
                )
                db.add(product)
                db.flush()  # populate product.id before referencing it
                product_map[ext_id] = product.id
                products_added += 1

            title = row["review_title"].strip()
            body = row["review_text"].strip()
            combined_text = f"{title}. {body}".strip(". ") if title else body

            review = Review(
                product_id=product_map[ext_id],
                reviewer_name=row["author"].strip() or "Anonymous",
                rating=_float(row["review_rating"], default=3.0),
                review_text=combined_text,
                recommended=_bool(row["is_a_buyer"]),   # ground-truth label
                predicted_recommended=None,
                user_overridden=False,
                created_at=_date(row["review_date"]),
            )
            db.add(review)
            reviews_added += 1

        db.commit()
        print(f"Done — {products_added} products, {reviews_added} reviews.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
