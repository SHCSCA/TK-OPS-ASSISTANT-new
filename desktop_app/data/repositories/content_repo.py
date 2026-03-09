from __future__ import annotations

# pyright: basic

"""内容域仓储实现，提供脚本与模板查询能力。"""

from collections.abc import Callable
from datetime import datetime, timezone
from importlib import import_module
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from .base import BaseRepository


def _content_template_model() -> type[Any]:
    """延迟加载内容模板模型。"""

    module = import_module("desktop_app.data.models.content")
    return cast(type[Any], getattr(module, "ContentTemplate"))


def _script_model() -> type[Any]:
    """延迟加载脚本模型。"""

    module = import_module("desktop_app.data.models.content")
    return cast(type[Any], getattr(module, "Script"))


class ScriptRepository(BaseRepository[Any]):
    """脚本记录仓储。"""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        super().__init__(session_factory, _script_model())

    def list_active(self) -> list[Any]:
        with self._read_session() as session:
            session_any = cast(Any, session)
            script_model = _script_model()
            script_deleted = cast(Any, getattr(script_model, "is_deleted"))
            script_created = cast(Any, getattr(script_model, "created_at"))
            statement = cast(Any, select(script_model))
            statement = statement.where(script_deleted.is_(False)).order_by(script_created.desc())
            return list(session_any.scalars(statement).all())

    def list_scheduled(self, after: datetime | None = None) -> list[Any]:
        cutoff = after or datetime.now(timezone.utc)
        with self._read_session() as session:
            session_any = cast(Any, session)
            script_model = _script_model()
            script_deleted = cast(Any, getattr(script_model, "is_deleted"))
            script_scheduled = cast(Any, getattr(script_model, "scheduled_at"))
            statement = cast(Any, select(script_model))
            statement = statement.where(script_deleted.is_(False))
            statement = statement.where(script_scheduled.is_not(None))
            statement = statement.where(script_scheduled >= cutoff).order_by(script_scheduled.asc())
            return list(session_any.scalars(statement).all())


class ContentTemplateRepository(BaseRepository[Any]):
    """内容模板仓储。"""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        super().__init__(session_factory, _content_template_model())

    def list_active(self) -> list[Any]:
        with self._read_session() as session:
            session_any = cast(Any, session)
            template_model = _content_template_model()
            template_deleted = cast(Any, getattr(template_model, "is_deleted"))
            template_created = cast(Any, getattr(template_model, "created_at"))
            statement = cast(Any, select(template_model))
            statement = statement.where(template_deleted.is_(False)).order_by(template_created.desc())
            return list(session_any.scalars(statement).all())

    def get_by_name(self, name: str) -> Any | None:
        with self._read_session() as session:
            session_any = cast(Any, session)
            template_model = _content_template_model()
            template_name = cast(Any, getattr(template_model, "name"))
            statement = cast(Any, select(template_model))
            statement = statement.where(template_name == name)
            return session_any.scalars(statement).first()
