"""add account risk and archive fields

Revision ID: c8f4a7b2d901
Revises: b9c9a7e8f102
Create Date: 2026-04-02 18:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c8f4a7b2d901"
down_revision: Union[str, None] = "b9c9a7e8f102"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    try:
        return {column["name"] for column in inspector.get_columns(table_name)}
    except Exception:
        return set()


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "accounts" not in inspector.get_table_names():
        return
    columns = _column_names("accounts")
    if "risk_status" not in columns:
        op.add_column(
            "accounts",
            sa.Column("risk_status", sa.String(length=20), nullable=False, server_default="normal"),
        )
    if "archived_at" not in columns:
        op.add_column("accounts", sa.Column("archived_at", sa.DateTime(), nullable=True))
    if "archived_reason" not in columns:
        op.add_column("accounts", sa.Column("archived_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "accounts" not in inspector.get_table_names():
        return
    columns = _column_names("accounts")
    if "archived_reason" in columns:
        op.drop_column("accounts", "archived_reason")
    if "archived_at" in columns:
        op.drop_column("accounts", "archived_at")
    if "risk_status" in columns:
        op.drop_column("accounts", "risk_status")
