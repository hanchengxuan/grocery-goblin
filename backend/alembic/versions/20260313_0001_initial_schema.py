"""initial schema

Revision ID: 20260313_0001
Revises: 
Create Date: 2026-03-13 07:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260313_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("loyalty_program", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_stores_code", "stores", ["code"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("canonical_name", sa.String(length=255), nullable=False),
        sa.Column("brand", sa.String(length=120), nullable=True),
        sa.Column("size_label", sa.String(length=120), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_products_canonical_name", "products", ["canonical_name"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "product_offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("store_id", sa.Integer(), sa.ForeignKey("stores.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_product_ref", sa.String(length=255), nullable=True),
        sa.Column("current_price", sa.Float(), nullable=False),
        sa.Column("unit_price_value", sa.Float(), nullable=True),
        sa.Column("unit_price_unit", sa.String(length=50), nullable=True),
        sa.Column("promo_flag", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("promo_text", sa.Text(), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_product_offers_product_id", "product_offers", ["product_id"], unique=False)
    op.create_index("ix_product_offers_store_id", "product_offers", ["store_id"], unique=False)

    op.create_table(
        "price_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_offer_id", sa.Integer(), sa.ForeignKey("product_offers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("observed_price", sa.Float(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_price_snapshots_product_offer_id", "price_snapshots", ["product_offer_id"], unique=False)

    op.create_table(
        "loyalty_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("external_ref", sa.String(length=255), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_loyalty_accounts_provider", "loyalty_accounts", ["provider"], unique=False)
    op.create_index("ix_loyalty_accounts_user_id", "loyalty_accounts", ["user_id"], unique=False)

    op.create_table(
        "loyalty_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("loyalty_account_id", sa.Integer(), sa.ForeignKey("loyalty_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_spend", sa.Float(), nullable=True),
        sa.Column("reward_points", sa.Integer(), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_loyalty_tasks_loyalty_account_id", "loyalty_tasks", ["loyalty_account_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_loyalty_tasks_loyalty_account_id", table_name="loyalty_tasks")
    op.drop_table("loyalty_tasks")
    op.drop_index("ix_loyalty_accounts_user_id", table_name="loyalty_accounts")
    op.drop_index("ix_loyalty_accounts_provider", table_name="loyalty_accounts")
    op.drop_table("loyalty_accounts")
    op.drop_index("ix_price_snapshots_product_offer_id", table_name="price_snapshots")
    op.drop_table("price_snapshots")
    op.drop_index("ix_product_offers_store_id", table_name="product_offers")
    op.drop_index("ix_product_offers_product_id", table_name="product_offers")
    op.drop_table("product_offers")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_products_canonical_name", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_stores_code", table_name="stores")
    op.drop_table("stores")
