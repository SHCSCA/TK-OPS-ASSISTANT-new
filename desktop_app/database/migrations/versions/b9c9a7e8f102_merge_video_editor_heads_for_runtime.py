"""merge video editor heads for runtime

Revision ID: b9c9a7e8f102
Revises: 3c7a6f5e9d21, 9f4e7c1b2d11
Create Date: 2026-04-01 23:10:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "b9c9a7e8f102"
down_revision: Union[str, None] = ("3c7a6f5e9d21", "9f4e7c1b2d11")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass