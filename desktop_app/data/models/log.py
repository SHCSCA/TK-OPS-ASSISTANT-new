from __future__ import annotations

# pyright: basic

"""Persistent log entry records for diagnostics and audit trails."""

from sqlalchemy import Column, DateTime, Index, Integer, JSON, String, Text, func

from .base import Base


class LogEntry(Base):
    """Stores structured log events for later retrieval."""

    __tablename__ = "log_entries"
    __table_args__ = (
        Index("ix_log_entries_timestamp", "timestamp"),
        Index("ix_log_entries_level_module", "level", "module"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False, index=True)
    level = Column(String(32), nullable=False, index=True)
    module = Column(String(120), nullable=False, index=True)
    message = Column(Text, nullable=False)
    details_json = Column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return f"LogEntry(id={self.id!r}, level={self.level!r}, module={self.module!r}, timestamp={self.timestamp!r})"
