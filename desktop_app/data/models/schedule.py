from __future__ import annotations

# pyright: basic

"""Schedule persistence records for publishing workflows."""

from sqlalchemy import Column, DateTime, Index, Integer, JSON, String, Text

from .base import Base, TimestampMixin


class PublishSchedule(Base, TimestampMixin):
    """Stores scheduler definitions for publish operations."""

    __tablename__ = "publish_schedules"
    __table_args__ = (
        Index("ix_publish_schedules_status_time", "status", "scheduled_time"),
        Index("ix_publish_schedules_account_status", "account_id", "status"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    account_id = Column(String(120), nullable=False, index=True)
    content_type = Column(String(64), nullable=False, index=True)
    content_json = Column(JSON, default=dict, nullable=False)
    scheduled_time = Column(DateTime(timezone=True), nullable=False, index=True)
    timezone = Column(String(64), default="UTC", nullable=False)
    status = Column(String(32), default="pending", nullable=False, index=True)
    recurrence_rule = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"PublishSchedule(id={self.id!r}, title={self.title!r}, status={self.status!r}, scheduled_time={self.scheduled_time!r})"
