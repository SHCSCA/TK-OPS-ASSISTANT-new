from __future__ import annotations

# pyright: basic

"""Repository implementation for jobs and task queues."""

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models.job import Job, Task

from .base import BaseRepository


class JobRepository(BaseRepository[Job]):
    """Persistence adapter for runtime job records."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        super().__init__(session_factory, Job)

    def get_by_status(self, status: str) -> list[Job]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            job_status = cast(Any, getattr(Job, "status"))
            job_priority = cast(Any, getattr(Job, "priority"))
            job_created_at = cast(Any, getattr(Job, "created_at"))
            statement = cast(Any, select(Job))
            statement = statement.where(job_status == status).order_by(job_priority.desc(), job_created_at)
            return list(session_any.scalars(statement).all())

    def get_ready_jobs(self, now: datetime | None = None) -> list[Job]:
        ready_at = now or datetime.now(timezone.utc)
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            job_status = cast(Any, getattr(Job, "status"))
            job_scheduled_at = cast(Any, getattr(Job, "scheduled_at"))
            job_priority = cast(Any, getattr(Job, "priority"))
            job_created_at = cast(Any, getattr(Job, "created_at"))
            statement = cast(Any, select(Job))
            statement = statement.where(job_status == "pending")
            statement = statement.where((job_scheduled_at.is_(None)) | (job_scheduled_at <= ready_at))
            statement = statement.order_by(job_priority.desc(), job_scheduled_at, job_created_at)
            return list(session_any.scalars(statement).all())

    def get_job_with_tasks(self, job_id: int) -> Job | None:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            job_tasks = cast(Any, getattr(Job, "tasks"))
            job_id_column = cast(Any, getattr(Job, "id"))
            statement = cast(Any, select(Job))
            statement = statement.options(selectinload(job_tasks)).where(job_id_column == job_id)
            return session_any.scalars(statement).first()

    def get_tasks_for_job(self, job_id: int) -> list[Task]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            task_job_id = cast(Any, getattr(Task, "job_id"))
            task_sort_order = cast(Any, getattr(Task, "sort_order"))
            task_id_column = cast(Any, getattr(Task, "id"))
            statement = cast(Any, select(Task))
            statement = statement.where(task_job_id == job_id).order_by(task_sort_order, task_id_column)
            return list(session_any.scalars(statement).all())
