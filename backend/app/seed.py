from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Store

DEFAULT_STORES = [
    {"code": "woolworths", "name": "Woolworths", "loyalty_program": "Woolworths Rewards"},
    {"code": "coles", "name": "Coles", "loyalty_program": "Flybuys"},
    {"code": "aldi", "name": "ALDI", "loyalty_program": None},
]


def seed_reference_data(db: Session) -> None:
    existing_codes = set(db.scalars(select(Store.code)).all())
    for item in DEFAULT_STORES:
        if item["code"] not in existing_codes:
            db.add(Store(**item))
    db.commit()
