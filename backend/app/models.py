from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Store(TimestampMixin, Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    loyalty_program: Mapped[str | None] = mapped_column(String(120), nullable=True)

    offers: Mapped[list["ProductOffer"]] = relationship(back_populates="store")


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    canonical_name: Mapped[str] = mapped_column(String(255), index=True)
    brand: Mapped[str | None] = mapped_column(String(120), nullable=True)
    size_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)

    offers: Mapped[list["ProductOffer"]] = relationship(back_populates="product")


class ProductOffer(TimestampMixin, Base):
    __tablename__ = "product_offers"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), index=True)
    source_product_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_price: Mapped[float] = mapped_column(Float)
    unit_price_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit_price_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    promo_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    promo_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product: Mapped["Product"] = relationship(back_populates="offers")
    store: Mapped["Store"] = relationship(back_populates="offers")
    snapshots: Mapped[list["PriceSnapshot"]] = relationship(back_populates="offer")


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_offer_id: Mapped[int] = mapped_column(ForeignKey("product_offers.id", ondelete="CASCADE"), index=True)
    observed_price: Mapped[float] = mapped_column(Float)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    offer: Mapped["ProductOffer"] = relationship(back_populates="snapshots")


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    loyalty_accounts: Mapped[list["LoyaltyAccount"]] = relationship(back_populates="user")


class LoyaltyAccount(TimestampMixin, Base):
    __tablename__ = "loyalty_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(80), index=True)
    external_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="loyalty_accounts")
    tasks: Mapped[list["LoyaltyTask"]] = relationship(back_populates="loyalty_account")


class LoyaltyTask(TimestampMixin, Base):
    __tablename__ = "loyalty_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    loyalty_account_id: Mapped[int] = mapped_column(ForeignKey("loyalty_accounts.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_spend: Mapped[float | None] = mapped_column(Float, nullable=True)
    reward_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    loyalty_account: Mapped["LoyaltyAccount"] = relationship(back_populates="tasks")
