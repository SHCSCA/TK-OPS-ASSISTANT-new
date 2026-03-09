from __future__ import annotations

# pyright: basic

"""Persistent settings records for shell and workspace preferences."""

from sqlalchemy import Column, Index, Integer, String, Text

from .base import Base, TimestampMixin


class AppSetting(Base, TimestampMixin):
    """Stores persisted configuration values by key."""

    __tablename__ = "app_settings"
    __table_args__ = (Index("ix_app_settings_category_key", "category", "key"),)

    key = Column(String(191), primary_key=True)
    value = Column(Text, nullable=True)
    category = Column(String(64), default="general", nullable=False, index=True)
    schema_version = Column(Integer, default=1, nullable=False)

    def __repr__(self) -> str:
        return f"AppSetting(key={self.key!r}, category={self.category!r}, schema_version={self.schema_version!r})"
