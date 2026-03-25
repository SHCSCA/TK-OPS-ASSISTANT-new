"""add account runtime fields and tags

Revision ID: 6f0c9b8a2a4d
Revises: ebd66c04b861
Create Date: 2026-03-25 00:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f0c9b8a2a4d'
down_revision: Union[str, None] = 'ebd66c04b861'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('accounts', sa.Column('tags', sa.Text(), nullable=True))
    op.add_column('accounts', sa.Column('cookie_status', sa.String(length=20), nullable=False, server_default='unknown'))
    op.add_column('accounts', sa.Column('isolation_enabled', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    op.add_column('accounts', sa.Column('last_login_at', sa.DateTime(), nullable=True))
    op.add_column('accounts', sa.Column('last_connection_status', sa.String(length=20), nullable=False, server_default='unknown'))
    op.add_column('accounts', sa.Column('last_connection_checked_at', sa.DateTime(), nullable=True))
    op.add_column('accounts', sa.Column('last_connection_message', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('accounts', 'last_connection_message')
    op.drop_column('accounts', 'last_connection_checked_at')
    op.drop_column('accounts', 'last_connection_status')
    op.drop_column('accounts', 'last_login_at')
    op.drop_column('accounts', 'isolation_enabled')
    op.drop_column('accounts', 'cookie_status')
    op.drop_column('accounts', 'tags')