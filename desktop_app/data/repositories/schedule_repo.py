from __future__ import annotations

# pyright: basic

"""Repository implementation for scheduled work definitions."""

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.schedule import PublishSchedule

from .base import BaseRepository


class ScheduleRepository(BaseRepository[PublishSchedule]):
    """Persistence adapter for scheduler records."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        super().__init__(session_factory, PublishSchedule)

    def get_by_status(self, status: str) -> list[PublishSchedule]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            schedule_status = cast(Any, getattr(PublishSchedule, "status"))
            schedule_time = cast(Any, getattr(PublishSchedule, "scheduled_time"))
            statement = cast(Any, select(PublishSchedule))
            statement = statement.where(schedule_status == status).order_by(schedule_time)
            return list(session_any.scalars(statement).all())

    def get_due_schedules(self, before: datetime | None = None) -> list[PublishSchedule]:
        cutoff = before or datetime.now(timezone.utc)
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            schedule_status = cast(Any, getattr(PublishSchedule, "status"))
            schedule_time = cast(Any, getattr(PublishSchedule, "scheduled_time"))
            statement = cast(Any, select(PublishSchedule))
            statement = statement.where(schedule_status == "pending")
            statement = statement.where(schedule_time <= cutoff).order_by(schedule_time)
            return list(session_any.scalars(statement).all())

    def get_for_account(self, account_id: str) -> list[PublishSchedule]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            schedule_account = cast(Any, getattr(PublishSchedule, "account_id"))
            schedule_time = cast(Any, getattr(PublishSchedule, "scheduled_time"))
            statement = cast(Any, select(PublishSchedule))
            statement = statement.where(schedule_account == account_id).order_by(schedule_time.desc())
            return list(session_any.scalars(statement).all())
