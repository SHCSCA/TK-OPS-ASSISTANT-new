from __future__ import annotations

# pyright: basic

"""Job and task persistence records for automation and AI runtime work."""

from typing import Any, cast

from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin

_relationship = cast(Any, relationship)


class Job(Base, TimestampMixin):
    """Stores high-level job execution metadata."""

    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'running', 'completed', 'failed', 'cancelled')", name="job_status_valid"),
        CheckConstraint("progress >= 0 AND progress <= 100", name="job_progress_range"),
        Index("ix_jobs_status_priority", "status", "priority"),
        Index("ix_jobs_type_status", "job_type", "status"),
        Index("ix_jobs_scheduled_at", "scheduled_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_type = Column(String(120), nullable=False, index=True)
    status = Column(String(32), default="pending", nullable=False, index=True)
    payload_json = Column(JSON, default=dict, nullable=False)
    result_json = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    progress = Column(Float, default=0.0, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    priority = Column(Integer, default=0, nullable=False, index=True)

    tasks = _relationship(
        "Task",
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Task.sort_order",
    )

    def __repr__(self) -> str:
        return f"Job(id={self.id!r}, job_type={self.job_type!r}, status={self.status!r}, priority={self.priority!r})"


class Task(Base, TimestampMixin):
    """Stores fine-grained task rows under a parent job."""

    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'running', 'completed', 'failed', 'cancelled')", name="task_status_valid"),
        Index("ix_tasks_job_status", "job_id", "status"),
        Index("ix_tasks_sort_order", "sort_order"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    task_name = Column(String(120), nullable=False)
    status = Column(String(32), default="pending", nullable=False, index=True)
    payload_json = Column(JSON, default=dict, nullable=False)
    result_json = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)

    job = _relationship("Job", back_populates="tasks")

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, job_id={self.job_id!r}, task_name={self.task_name!r}, status={self.status!r})"
