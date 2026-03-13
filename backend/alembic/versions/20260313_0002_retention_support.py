"""retention support

Revision ID: 20260313_0002
Revises: 20260313_0001
Create Date: 2026-03-13 08:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260313_0002"
down_revision = "20260313_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("price_snapshots", sa.Column("promo_flag", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("price_snapshots", sa.Column("unit_price_value", sa.Float(), nullable=True))

    op.create_table(
        "daily_price_aggregates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_offer_id", sa.Integer(), sa.ForeignKey("product_offers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day", sa.DateTime(timezone=True), nullable=False),
        sa.Column("min_price", sa.Float(), nullable=False),
        sa.Column("max_price", sa.Float(), nullable=False),
        sa.Column("avg_price", sa.Float(), nullable=False),
        sa.Column("observed_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_daily_price_aggregates_product_offer_id", "daily_price_aggregates", ["product_offer_id"], unique=False)
    op.create_index("ix_daily_price_aggregates_day", "daily_price_aggregates", ["day"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_daily_price_aggregates_day", table_name="daily_price_aggregates")
    op.drop_index("ix_daily_price_aggregates_product_offer_id", table_name="daily_price_aggregates")
    op.drop_table("daily_price_aggregates")
    op.drop_column("price_snapshots", "unit_price_value")
    op.drop_column("price_snapshots", "promo_flag")
