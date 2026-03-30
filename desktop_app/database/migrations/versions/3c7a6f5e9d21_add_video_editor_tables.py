"""add video editor tables

Revision ID: 3c7a6f5e9d21
Revises: 91c9d4b7e2aa
Create Date: 2026-03-30 12:30:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3c7a6f5e9d21"
down_revision: Union[str, None] = "91c9d4b7e2aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    try:
        indexes = inspector.get_indexes(table_name)
    except Exception:
        return False
    return any(index.get("name") == index_name for index in indexes)


def upgrade() -> None:
    if not _table_exists("video_projects"):
        op.create_table(
            "video_projects",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(length=160), nullable=False),
            sa.Column("status", sa.String(length=40), nullable=False, server_default="draft"),
            sa.Column("canvas_ratio", sa.String(length=20), nullable=False, server_default="9:16"),
            sa.Column("width", sa.Integer(), nullable=False, server_default="1080"),
            sa.Column("height", sa.Integer(), nullable=False, server_default="1920"),
            sa.Column("cover_asset_id", sa.Integer(), nullable=True),
            sa.Column("last_opened_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["cover_asset_id"], ["assets.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _table_exists("video_sequences"):
        op.create_table(
            "video_sequences",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=160), nullable=False),
            sa.Column("duration_ms", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["video_projects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _table_exists("video_clips"):
        op.create_table(
            "video_clips",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("sequence_id", sa.Integer(), nullable=False),
            sa.Column("asset_id", sa.Integer(), nullable=True),
            sa.Column("track_type", sa.Enum("video", "audio", name="video_track_type"), nullable=False, server_default="video"),
            sa.Column("track_index", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("start_ms", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("source_in_ms", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("source_out_ms", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("duration_ms", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("transform_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
            sa.ForeignKeyConstraint(["sequence_id"], ["video_sequences.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _table_exists("video_subtitles"):
        op.create_table(
            "video_subtitles",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("sequence_id", sa.Integer(), nullable=False),
            sa.Column("start_ms", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("end_ms", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("text", sa.Text(), nullable=False, server_default=""),
            sa.Column("style_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["sequence_id"], ["video_sequences.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _table_exists("video_exports"):
        op.create_table(
            "video_exports",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("sequence_id", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(length=40), nullable=False, server_default="pending"),
            sa.Column("preset", sa.String(length=80), nullable=False, server_default="final"),
            sa.Column("output_path", sa.Text(), nullable=True),
            sa.Column("ffmpeg_command", sa.Text(), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("started_at", sa.DateTime(), nullable=True),
            sa.Column("finished_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["video_projects.id"]),
            sa.ForeignKeyConstraint(["sequence_id"], ["video_sequences.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _table_exists("video_snapshots"):
        op.create_table(
            "video_snapshots",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=160), nullable=False),
            sa.Column("snapshot_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["video_projects.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _index_exists("video_sequences", "ix_video_sequences_project_id"):
        op.create_index("ix_video_sequences_project_id", "video_sequences", ["project_id"], unique=False)
    if not _index_exists("video_clips", "ix_video_clips_sequence_id"):
        op.create_index("ix_video_clips_sequence_id", "video_clips", ["sequence_id"], unique=False)
    if not _index_exists("video_clips", "ix_video_clips_asset_id"):
        op.create_index("ix_video_clips_asset_id", "video_clips", ["asset_id"], unique=False)
    if not _index_exists("video_subtitles", "ix_video_subtitles_sequence_id"):
        op.create_index("ix_video_subtitles_sequence_id", "video_subtitles", ["sequence_id"], unique=False)
    if not _index_exists("video_exports", "ix_video_exports_project_id"):
        op.create_index("ix_video_exports_project_id", "video_exports", ["project_id"], unique=False)
    if not _index_exists("video_exports", "ix_video_exports_sequence_id"):
        op.create_index("ix_video_exports_sequence_id", "video_exports", ["sequence_id"], unique=False)
    if not _index_exists("video_snapshots", "ix_video_snapshots_project_id"):
        op.create_index("ix_video_snapshots_project_id", "video_snapshots", ["project_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_video_snapshots_project_id", table_name="video_snapshots")
    op.drop_index("ix_video_exports_sequence_id", table_name="video_exports")
    op.drop_index("ix_video_exports_project_id", table_name="video_exports")
    op.drop_index("ix_video_subtitles_sequence_id", table_name="video_subtitles")
    op.drop_index("ix_video_clips_asset_id", table_name="video_clips")
    op.drop_index("ix_video_clips_sequence_id", table_name="video_clips")
    op.drop_index("ix_video_sequences_project_id", table_name="video_sequences")
    op.drop_table("video_snapshots")
    op.drop_table("video_exports")
    op.drop_table("video_subtitles")
    op.drop_table("video_clips")
    op.drop_table("video_sequences")
    op.drop_table("video_projects")
