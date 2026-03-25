"""add account cookie content fields

Revision ID: 8a7d9fd32c11
Revises: 6f0c9b8a2a4d
Create Date: 2026-03-25 00:30:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a7d9fd32c11'
down_revision: Union[str, None] = '6f0c9b8a2a4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('accounts', sa.Column('cookie_content', sa.Text(), nullable=True))
    op.add_column('accounts', sa.Column('cookie_updated_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('accounts', 'cookie_updated_at')
    op.drop_column('accounts', 'cookie_content')