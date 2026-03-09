from __future__ import annotations

# pyright: basic

"""Repository implementation for structured application logs."""

from collections.abc import Callable
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.log import LogEntry

from .base import BaseRepository


class LogRepository(BaseRepository[LogEntry]):
    """Persistence adapter for log entry records."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        super().__init__(session_factory, LogEntry)

    def get_recent(self, limit: int = 100) -> list[LogEntry]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            log_timestamp = cast(Any, getattr(LogEntry, "timestamp"))
            statement = cast(Any, select(LogEntry))
            statement = statement.order_by(log_timestamp.desc()).limit(max(limit, 0))
            return list(session_any.scalars(statement).all())

    def get_by_level(self, level: str, limit: int = 100) -> list[LogEntry]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            log_level = cast(Any, getattr(LogEntry, "level"))
            log_timestamp = cast(Any, getattr(LogEntry, "timestamp"))
            statement = cast(Any, select(LogEntry))
            statement = statement.where(log_level == level).order_by(log_timestamp.desc()).limit(max(limit, 0))
            return list(session_any.scalars(statement).all())

    def get_by_module(self, module: str, limit: int = 100) -> list[LogEntry]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            log_module = cast(Any, getattr(LogEntry, "module"))
            log_timestamp = cast(Any, getattr(LogEntry, "timestamp"))
            statement = cast(Any, select(LogEntry))
            statement = statement.where(log_module == module).order_by(log_timestamp.desc()).limit(max(limit, 0))
            return list(session_any.scalars(statement).all())
