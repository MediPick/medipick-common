"""Add pickup extension status, pickup failed attempts lockout, and ready_at to orders.

Revision ID: 0002_orders_pickup_ext
Revises: 0001_initial_customer
Create Date: 2026-11-12 02:25:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_orders_pickup_ext"
down_revision: Union[str, None] = "0001_initial_customer"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("pickup_extension_status", sa.String(length=20), nullable=True))
    op.add_column(
        "orders",
        sa.Column("pickup_failed_attempts", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column("orders", sa.Column("pickup_locked_until", sa.DateTime(timezone=True), nullable=True))
    op.add_column("orders", sa.Column("ready_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "ready_at")
    op.drop_column("orders", "pickup_locked_until")
    op.drop_column("orders", "pickup_failed_attempts")
    op.drop_column("orders", "pickup_extension_status")

