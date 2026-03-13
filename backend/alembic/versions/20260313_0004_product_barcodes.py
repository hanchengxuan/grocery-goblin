"""product barcodes

Revision ID: 20260313_0004
Revises: 20260313_0003
Create Date: 2026-03-13 09:50:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260313_0004"
down_revision = "20260313_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("products", sa.Column("barcode", sa.String(length=64), nullable=True))
    op.create_index("ix_products_barcode", "products", ["barcode"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_products_barcode", table_name="products")
    op.drop_column("products", "barcode")
