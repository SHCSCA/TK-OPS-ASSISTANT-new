from __future__ import annotations

# pyright: basic

"""SQLAlchemy engine and session management for the data layer."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from . import models as _models
from .models.base import Base


class Database:
    """SQLAlchemy engine and session management."""

    def __init__(self, db_url: str = "sqlite:///tk_ops.db") -> None:
        self._db_url = db_url
        self._engine = create_engine(db_url, **self._build_engine_kwargs(db_url))
        self._session_factory = sessionmaker(bind=self._engine, autoflush=False, expire_on_commit=False)

    @property
    def engine(self) -> Engine:
        return self._engine

    def create_session(self) -> Session:
        return self._session_factory()

    def create_all(self) -> None:
        _ = _models
        metadata = getattr(Base, "metadata")
        metadata.create_all(self._engine)

    def drop_all(self) -> None:
        _ = _models
        metadata = getattr(Base, "metadata")
        metadata.drop_all(self._engine)

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        session = self.create_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def _build_engine_kwargs(db_url: str) -> dict[str, object]:
        kwargs: dict[str, object] = {"future": True}
        if db_url.startswith("sqlite"):
            kwargs["connect_args"] = {"check_same_thread": False}
            if Database._is_in_memory_sqlite(db_url):
                kwargs["poolclass"] = StaticPool
        return kwargs

    @staticmethod
    def _is_in_memory_sqlite(db_url: str) -> bool:
        normalized = db_url.lower()
        return normalized in {"sqlite://", "sqlite:///:memory:"} or "mode=memory" in normalized
