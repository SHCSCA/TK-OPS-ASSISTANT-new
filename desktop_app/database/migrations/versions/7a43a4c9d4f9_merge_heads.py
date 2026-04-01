"""merge heads

Revision ID: 7a43a4c9d4f9
Revises: 91c9d4b7e2aa, c31b3b654b07
Create Date: 2026-03-30 17:45:44.480648
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a43a4c9d4f9'
down_revision: Union[str, None] = ('91c9d4b7e2aa', 'c31b3b654b07')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
