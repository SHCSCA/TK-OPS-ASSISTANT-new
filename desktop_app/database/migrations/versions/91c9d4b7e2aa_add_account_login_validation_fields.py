"""add account login validation fields

Revision ID: 91c9d4b7e2aa
Revises: 8a7d9fd32c11
Create Date: 2026-03-25 02:15:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91c9d4b7e2aa'
down_revision: Union[str, None] = '8a7d9fd32c11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('accounts', sa.Column('last_login_check_status', sa.String(length=20), nullable=False, server_default='unknown'))
    op.add_column('accounts', sa.Column('last_login_check_at', sa.DateTime(), nullable=True))
    op.add_column('accounts', sa.Column('last_login_check_message', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('accounts', 'last_login_check_message')
    op.drop_column('accounts', 'last_login_check_at')
    op.drop_column('accounts', 'last_login_check_status')