"""add video sequence library assets

Revision ID: 9f4e7c1b2d11
Revises: 7a43a4c9d4f9
Create Date: 2026-03-31 09:15:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f4e7c1b2d11'
down_revision: Union[str, None] = '7a43a4c9d4f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'video_sequence_assets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sequence_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['sequence_id'], ['video_sequences.id']),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sequence_id', 'asset_id', name='uq_video_sequence_asset'),
    )


def downgrade() -> None:
    op.drop_table('video_sequence_assets')