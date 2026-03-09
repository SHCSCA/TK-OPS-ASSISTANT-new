from __future__ import annotations

# pyright: basic

"""Asset and media persistence records for creator workflows."""

from sqlalchemy import BigInteger, CheckConstraint, Column, Index, Integer, JSON, String

from .base import Base, SoftDeleteMixin, TimestampMixin


class Asset(Base, TimestampMixin, SoftDeleteMixin):
    """Stores top-level media asset metadata."""

    __tablename__ = "assets"
    __table_args__ = (
        CheckConstraint("asset_type IN ('image', 'video', 'audio', 'document')", name="asset_type_valid"),
        Index("ix_assets_type_deleted", "asset_type", "is_deleted"),
        Index("ix_assets_name", "name"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(32), nullable=False, index=True)
    file_path = Column(String(1024), nullable=False)
    thumbnail_path = Column(String(1024), nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    tags_json = Column(JSON, default=list, nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return f"Asset(id={self.id!r}, name={self.name!r}, asset_type={self.asset_type!r}, is_deleted={self.is_deleted!r})"
