import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.session import SessionLocal
from app.models.product import Product


def main() -> None:
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        for p in products:
            p.image_url = f"https://picsum.photos/seed/product{p.id}/400/400"
        db.commit()
        print(f"Updated image_url for {len(products)} products.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
