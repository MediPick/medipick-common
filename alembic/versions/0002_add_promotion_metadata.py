"""add_promotion_metadata

Revision ID: 0002_add_promotion_metadata
Revises: 0001_initial_pharmacy
Create Date: 2026-11-13 21:05:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0002_add_promotion_metadata'
down_revision: Union[str, None] = '0001_initial_pharmacy'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'pharmacy_promotions',
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('pharmacy_promotions', 'metadata')

