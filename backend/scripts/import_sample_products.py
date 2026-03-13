from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.catalog import upsert_product_record
from app.db import SessionLocal
from app.schemas import ProductImportRecord

SAMPLE_DATA = [
    {
        "canonical_name": "Bananas",
        "brand": None,
        "size_label": "per kg",
        "category": "fruit",
        "image_url": "https://images.example.com/products/bananas.jpg",
        "offers": [
            {"store_code": "woolworths", "source_product_ref": "ww-bananas", "image_url": "https://images.example.com/offers/ww-bananas.jpg", "current_price": 3.9, "unit_price_value": 3.9, "unit_price_unit": "kg", "promo_flag": False, "promo_text": None},
            {"store_code": "coles", "source_product_ref": "co-bananas", "image_url": "https://images.example.com/offers/co-bananas.jpg", "current_price": 3.7, "unit_price_value": 3.7, "unit_price_unit": "kg", "promo_flag": False, "promo_text": None},
            {"store_code": "aldi", "source_product_ref": "al-bananas", "image_url": "https://images.example.com/offers/al-bananas.jpg", "current_price": 3.49, "unit_price_value": 3.49, "unit_price_unit": "kg", "promo_flag": False, "promo_text": None}
        ]
    },
    {
        "canonical_name": "Full Cream Milk",
        "brand": "Generic",
        "size_label": "2L",
        "category": "dairy",
        "image_url": "https://images.example.com/products/full-cream-milk-2l.jpg",
        "offers": [
            {"store_code": "woolworths", "source_product_ref": "ww-milk-2l", "image_url": "https://images.example.com/offers/ww-milk-2l.jpg", "current_price": 3.6, "unit_price_value": 1.8, "unit_price_unit": "L", "promo_flag": False, "promo_text": None},
            {"store_code": "coles", "source_product_ref": "co-milk-2l", "image_url": "https://images.example.com/offers/co-milk-2l.jpg", "current_price": 3.55, "unit_price_value": 1.775, "unit_price_unit": "L", "promo_flag": True, "promo_text": "Down Down"}
        ]
    }
]


def main() -> None:
    with SessionLocal() as db:
        for row in SAMPLE_DATA:
            upsert_product_record(db, ProductImportRecord.model_validate(row))
    print(json.dumps({"imported": len(SAMPLE_DATA)}))


if __name__ == "__main__":
    main()
