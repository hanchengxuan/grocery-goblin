from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from .models import DailyPriceAggregate, PriceSnapshot, ProductOffer


def should_create_snapshot(
    previous_offer: ProductOffer | None,
    incoming_price: float,
    incoming_promo_flag: bool,
    incoming_unit_price_value: float | None,
    latest_snapshot: PriceSnapshot | None,
    now: datetime | None = None,
) -> bool:
    now = now or datetime.now(timezone.utc)
    if previous_offer is None or latest_snapshot is None:
        return True

    if previous_offer.current_price != incoming_price:
        return True
    if previous_offer.promo_flag != incoming_promo_flag:
        return True
    if previous_offer.unit_price_value != incoming_unit_price_value:
        return True
    if latest_snapshot.observed_at <= now - timedelta(hours=24):
        return True
    return False


def rollup_daily_snapshots(db: Session, older_than_days: int = 0) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    day_bucket = func.date_trunc('day', PriceSnapshot.observed_at).label('day')
    rows = db.execute(
        select(
            PriceSnapshot.product_offer_id,
            day_bucket,
            func.min(PriceSnapshot.observed_price),
            func.max(PriceSnapshot.observed_price),
            func.avg(PriceSnapshot.observed_price),
            func.count(PriceSnapshot.id),
            func.max(PriceSnapshot.observed_at),
        )
        .where(PriceSnapshot.observed_at <= cutoff)
        .group_by(PriceSnapshot.product_offer_id, day_bucket)
    ).all()

    upserts = 0
    for product_offer_id, day, min_price, max_price, avg_price, count, last_observed_at in rows:
        existing = db.scalar(
            select(DailyPriceAggregate).where(
                DailyPriceAggregate.product_offer_id == product_offer_id,
                DailyPriceAggregate.day == day,
            )
        )
        if existing:
            existing.min_price = min_price
            existing.max_price = max_price
            existing.avg_price = float(avg_price)
            existing.observed_count = count
            existing.last_observed_at = last_observed_at
        else:
            db.add(
                DailyPriceAggregate(
                    product_offer_id=product_offer_id,
                    day=day,
                    min_price=min_price,
                    max_price=max_price,
                    avg_price=float(avg_price),
                    observed_count=count,
                    last_observed_at=last_observed_at,
                )
            )
        upserts += 1
    db.commit()
    return upserts


def purge_old_snapshots(db: Session, retention_days: int = 30) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    result = db.execute(delete(PriceSnapshot).where(PriceSnapshot.observed_at < cutoff))
    db.commit()
    return result.rowcount or 0
