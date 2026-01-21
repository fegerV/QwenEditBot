"""Add promocodes table

Revision ID: add_promocodes_table
Revises: e81267faf28b
Create Date: 2024-01-21 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_promocodes_table'
down_revision = 'e81267faf28b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create promocodes table
    op.create_table(
        'promocodes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('is_used', sa.Boolean(), default=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('used_by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['used_by_user_id'], ['users.user_id'], ),
    )
    op.create_index('ix_promocodes_code', 'promocodes', ['code'], unique=True)
    op.create_index('ix_promocodes_id', 'promocodes', ['id'], unique=False)


def downgrade() -> None:
    # Drop promocodes table
    op.drop_index('ix_promocodes_id', table_name='promocodes')
    op.drop_index('ix_promocodes_code', table_name='promocodes')
    op.drop_table('promocodes')
