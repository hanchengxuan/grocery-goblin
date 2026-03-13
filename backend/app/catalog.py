from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from .models import PriceSnapshot, Product, ProductOffer, Store
from .pricing import should_create_snapshot
from .schemas import ProductImportRecord, ProductSearchResult


def _fmt_unit_price(value: float | None, unit: str | None) -> str:
    if value is None or not unit:
        return ""
    return f"${value:.2f}/{unit}"


def upsert_product_record(db: Session, record: ProductImportRecord) -> Product:
    product = db.scalar(
        select(Product).where(func.lower(Product.canonical_name) == record.canonical_name.lower())
    )
    if not product:
        product = Product(
            canonical_name=record.canonical_name,
            brand=record.brand,
            size_label=record.size_label,
            category=record.category,
        )
        db.add(product)
        db.flush()
    else:
        product.brand = record.brand or product.brand
        product.size_label = record.size_label or product.size_label
        product.category = record.category or product.category

    now = datetime.now(timezone.utc)
    for offer_in in record.offers:
        store = db.scalar(select(Store).where(Store.code == offer_in.store_code))
        if not store:
            raise ValueError(f"Unknown store code: {offer_in.store_code}")

        offer = db.scalar(
            select(ProductOffer).where(
                ProductOffer.product_id == product.id,
                ProductOffer.store_id == store.id,
            )
        )
        latest_snapshot = None
        if offer:
            latest_snapshot = db.scalar(
                select(PriceSnapshot)
                .where(PriceSnapshot.product_offer_id == offer.id)
                .order_by(PriceSnapshot.observed_at.desc())
                .limit(1)
            )

        create_snapshot = should_create_snapshot(
            previous_offer=offer,
            incoming_price=offer_in.current_price,
            incoming_promo_flag=offer_in.promo_flag,
            incoming_unit_price_value=offer_in.unit_price_value,
            latest_snapshot=latest_snapshot,
            now=now,
        )

        if not offer:
            offer = ProductOffer(
                product_id=product.id,
                store_id=store.id,
                source_product_ref=offer_in.source_product_ref,
                current_price=offer_in.current_price,
                unit_price_value=offer_in.unit_price_value,
                unit_price_unit=offer_in.unit_price_unit,
                promo_flag=offer_in.promo_flag,
                promo_text=offer_in.promo_text,
                last_seen_at=now,
            )
            db.add(offer)
            db.flush()
        else:
            offer.source_product_ref = offer_in.source_product_ref or offer.source_product_ref
            offer.current_price = offer_in.current_price
            offer.unit_price_value = offer_in.unit_price_value
            offer.unit_price_unit = offer_in.unit_price_unit
            offer.promo_flag = offer_in.promo_flag
            offer.promo_text = offer_in.promo_text
            offer.last_seen_at = now

        if create_snapshot:
            db.add(
                PriceSnapshot(
                    product_offer_id=offer.id,
                    observed_price=offer_in.current_price,
                    promo_flag=offer_in.promo_flag,
                    unit_price_value=offer_in.unit_price_value,
                    observed_at=now,
                )
            )

    db.commit()
    db.refresh(product)
    return product


def search_products(db: Session, query: str) -> list[ProductSearchResult]:
    stmt = (
        select(ProductOffer, Product, Store)
        .join(Product, ProductOffer.product_id == Product.id)
        .join(Store, ProductOffer.store_id == Store.id)
        .order_by(Product.canonical_name.asc(), Store.name.asc())
    )
    if query.strip():
        like = f"%{query.strip().lower()}%"
        stmt = stmt.where(func.lower(Product.canonical_name).like(like))

    rows = db.execute(stmt.limit(50)).all()
    return [
        ProductSearchResult(
            product_id=str(product.id),
            name=product.canonical_name,
            brand=product.brand,
            store=store.name,
            price=offer.current_price,
            unit_price=_fmt_unit_price(offer.unit_price_value, offer.unit_price_unit),
            promo=offer.promo_flag,
            category=product.category,
        )
        for offer, product, store in rows
    ]
