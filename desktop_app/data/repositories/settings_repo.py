from __future__ import annotations

# pyright: basic

"""Repository implementation for persisted application settings."""

from collections.abc import Callable
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.settings import AppSetting

from .base import BaseRepository


class SettingsRepository(BaseRepository[AppSetting]):
    """Persistence adapter for application settings."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        super().__init__(session_factory, AppSetting)

    def get_by_key(self, key: str) -> AppSetting | None:
        return self.get_by_id(key)

    def get_by_category(self, category: str) -> list[AppSetting]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            category_column = cast(Any, getattr(AppSetting, "category"))
            key_column = cast(Any, getattr(AppSetting, "key"))
            statement = cast(Any, select(AppSetting))
            statement = statement.where(category_column == category).order_by(key_column)
            return list(session_any.scalars(statement).all())

    def set_value(
        self,
        key: str,
        value: str | None,
        *,
        category: str = "general",
        schema_version: int = 1,
    ) -> AppSetting:
        with self._session_scope() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            setting = session_any.get(AppSetting, key)
            if setting is None:
                setting = AppSetting()
                setting.key = key
            setting.value = value
            setting.category = category
            setting.schema_version = schema_version
            session_any.add(setting)
            session_any.flush()
            session_any.refresh(setting)
            return setting
