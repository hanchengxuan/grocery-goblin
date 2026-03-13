from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import PriceSnapshot, Product, ProductOffer, Store
from .pricing import should_create_snapshot
from .schemas import (
    BasketItem,
    BasketResponse,
    BasketStoreTotal,
    GroupedProductSearchResult,
    ProductImportRecord,
    ProductSearchResult,
    StorePriceResult,
)


def _fmt_unit_price(value: float | None, unit: str | None) -> str:
    if value is None or not unit:
        return ""
    return f"${value:.2f}/{unit}"


def _query_tokens(query: str) -> list[str]:
    return [tok for tok in query.strip().lower().split() if tok]


def _base_product_offer_query():
    return (
        select(ProductOffer, Product, Store)
        .join(Product, ProductOffer.product_id == Product.id)
        .join(Store, ProductOffer.store_id == Store.id)
    )


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


def search_products_flat(db: Session, query: str) -> list[ProductSearchResult]:
    stmt = _base_product_offer_query().order_by(Product.canonical_name.asc(), Store.name.asc())
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


def search_products_grouped(db: Session, query: str) -> list[GroupedProductSearchResult]:
    stmt = _base_product_offer_query().order_by(Product.canonical_name.asc(), Store.name.asc())
    tokens = _query_tokens(query)
    if tokens:
        for token in tokens:
            stmt = stmt.where(func.lower(Product.canonical_name).like(f"%{token}%"))

    rows = db.execute(stmt.limit(200)).all()
    grouped: dict[int, GroupedProductSearchResult] = {}
    for offer, product, store in rows:
        entry = grouped.get(product.id)
        if not entry:
            entry = GroupedProductSearchResult(
                product_id=str(product.id),
                name=product.canonical_name,
                brand=product.brand,
                size_label=product.size_label,
                category=product.category,
                stores=[],
            )
            grouped[product.id] = entry

        entry.stores.append(
            StorePriceResult(
                store_code=store.code,
                store_name=store.name,
                price=offer.current_price,
                unit_price=_fmt_unit_price(offer.unit_price_value, offer.unit_price_unit),
                promo=offer.promo_flag,
                source_product_ref=offer.source_product_ref,
            )
        )

    for entry in grouped.values():
        entry.stores.sort(key=lambda s: (s.price, s.store_name))

    return sorted(grouped.values(), key=lambda item: (item.name.lower(), item.brand or ""))


def compare_basket(db: Session, items: list[BasketItem]) -> BasketResponse:
    store_totals: dict[str, float] = defaultdict(float)
    store_matches: dict[str, int] = defaultdict(int)

    for item in items:
        tokens = _query_tokens(item.query)
        stmt = _base_product_offer_query()
        for token in tokens:
            stmt = stmt.where(func.lower(Product.canonical_name).like(f"%{token}%"))
        rows = db.execute(stmt).all()

        best_by_store: dict[str, tuple[ProductOffer, Product, Store]] = {}
        for offer, product, store in rows:
            existing = best_by_store.get(store.name)
            if not existing or offer.current_price < existing[0].current_price:
                best_by_store[store.name] = (offer, product, store)

        for store_name, (offer, _product, _store) in best_by_store.items():
            store_totals[store_name] += offer.current_price * item.quantity
            store_matches[store_name] += 1

    totals = [
        BasketStoreTotal(store=store, total=round(total, 2), matched_items=store_matches[store])
        for store, total in sorted(store_totals.items(), key=lambda kv: (-(store_matches[kv[0]]), kv[1], kv[0]))
    ]

    if not totals:
        return BasketResponse(currency="AUD", totals=[], recommendation="No matching products found for the requested basket.")

    best = totals[0]
    recommendation = f"Best current basket: {best.store} with {best.matched_items}/{len(items)} items matched for ${best.total:.2f}."
    return BasketResponse(currency="AUD", totals=totals, recommendation=recommendation)
