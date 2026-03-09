from __future__ import annotations

# pyright: basic

"""Repository implementation for AI providers, models, and agent roles."""

from collections.abc import Callable
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models.ai_provider import AIModel, AIProvider, AgentRole

from .base import BaseRepository


class AIRepository(BaseRepository[AIProvider]):
    """Persistence adapter for AI-related records."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        super().__init__(session_factory, AIProvider)

    def get_enabled_providers(self) -> list[AIProvider]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            provider_enabled = cast(Any, getattr(AIProvider, "is_enabled"))
            provider_sort = cast(Any, getattr(AIProvider, "sort_order"))
            provider_name = cast(Any, getattr(AIProvider, "name"))
            statement = cast(Any, select(AIProvider))
            statement = statement.where(provider_enabled.is_(True)).order_by(provider_sort, provider_name)
            return list(session_any.scalars(statement).all())

    def get_provider_with_models(self, provider_id: int) -> AIProvider | None:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            provider_models = cast(Any, getattr(AIProvider, "models"))
            provider_id_column = cast(Any, getattr(AIProvider, "id"))
            statement = cast(Any, select(AIProvider))
            statement = statement.options(selectinload(provider_models)).where(provider_id_column == provider_id)
            return session_any.scalars(statement).first()

    def get_enabled_models(self, provider_id: int | None = None) -> list[AIModel]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            model_enabled = cast(Any, getattr(AIModel, "is_enabled"))
            model_display = cast(Any, getattr(AIModel, "display_name"))
            model_provider_id = cast(Any, getattr(AIModel, "provider_id"))
            statement = cast(Any, select(AIModel))
            statement = statement.where(model_enabled.is_(True)).order_by(model_display)
            if provider_id is not None:
                statement = statement.where(model_provider_id == provider_id)
            return list(session_any.scalars(statement).all())

    def get_agent_role_by_name(self, name: str) -> AgentRole | None:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            role_name = cast(Any, getattr(AgentRole, "name"))
            statement = cast(Any, select(AgentRole))
            statement = statement.where(role_name == name)
            return session_any.scalars(statement).first()

    def get_system_roles(self) -> list[AgentRole]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            role_system = cast(Any, getattr(AgentRole, "is_system_role"))
            role_sort = cast(Any, getattr(AgentRole, "sort_order"))
            role_name = cast(Any, getattr(AgentRole, "name"))
            statement = cast(Any, select(AgentRole))
            statement = statement.where(role_system.is_(True)).order_by(role_sort, role_name)
            return list(session_any.scalars(statement).all())
