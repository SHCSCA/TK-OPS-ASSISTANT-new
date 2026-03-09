from __future__ import annotations

# pyright: basic

"""Generic repository primitives for persistence adapters."""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any, Generic, Protocol, TypeVar, cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session

T = TypeVar("T")


class RepositoryProtocol(Protocol[T]):
    """Protocol describing common CRUD behavior for repositories."""

    def get_by_id(self, id: Any) -> T | None: ...
    def get_all(self, skip: int = 0, limit: int = 100) -> list[T]: ...
    def create(self, **kwargs: Any) -> T: ...
    def update(self, id: Any, **kwargs: Any) -> T | None: ...
    def delete(self, id: Any) -> bool: ...
    def count(self) -> int: ...


class BaseRepository(Generic[T]):
    """Generic repository with CRUD operations."""

    def __init__(self, session_factory: Callable[[], Session], model_class: type[T]) -> None:
        self._session_factory = session_factory
        self._model_class = model_class

    @contextmanager
    def _session_scope(self) -> Generator[Session, None, None]:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def _read_session(self) -> Generator[Session, None, None]:
        session = self._session_factory()
        try:
            yield session
        finally:
            session.close()

    def get_by_id(self, id: Any) -> T | None:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            return session_any.get(self._model_class, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            statement = cast(Any, select(self._model_class))
            statement = statement.offset(max(skip, 0)).limit(max(limit, 0))
            return list(session_any.scalars(statement).all())

    def create(self, **kwargs: Any) -> T:
        instance = self._model_class(**kwargs)
        with self._session_scope() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            session_any.add(instance)
            session_any.flush()
            session_any.refresh(instance)
            return instance

    def update(self, id: Any, **kwargs: Any) -> T | None:
        with self._session_scope() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            instance = session_any.get(self._model_class, id)
            if instance is None:
                return None
            for key, value in kwargs.items():
                setattr(instance, key, value)
            session_any.add(instance)
            session_any.flush()
            session_any.refresh(instance)
            return instance

    def delete(self, id: Any) -> bool:
        with self._session_scope() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            instance = session_any.get(self._model_class, id)
            if instance is None:
                return False
            session_any.delete(instance)
            return True

    def count(self) -> int:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            statement = cast(Any, select(func.count()))
            statement = statement.select_from(self._model_class)
            return int(session_any.scalar(statement) or 0)
