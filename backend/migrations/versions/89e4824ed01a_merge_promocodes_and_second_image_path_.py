"""Merge promocodes and second image path migrations

Revision ID: 89e4824ed01a
Revises: add_promocodes_table, 20260121000002
Create Date: 2026-01-22 02:28:24.248536

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89e4824ed01a'
down_revision: Union[str, Sequence[str], None] = ('add_promocodes_table', '20260121000002')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
