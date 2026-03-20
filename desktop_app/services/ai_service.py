"""AI provider configuration service."""
from __future__ import annotations

from typing import Any, Sequence

from desktop_app.database.models import AIProvider
from desktop_app.database.repository import Repository


class AIService:
    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    def create_provider(self, name: str, **kwargs: Any) -> AIProvider:
        return self._repo.add(AIProvider(name=name, **kwargs))

    def list_providers(self) -> Sequence[AIProvider]:
        return self._repo.list_all(AIProvider)

    def get_active_provider(self) -> AIProvider | None:
        return self._repo.get_active_provider()

    def update_provider(self, pk: int, **fields: Any) -> AIProvider | None:
        provider = self._repo.get_by_id(AIProvider, pk)
        if provider is None:
            return None
        return self._repo.update(provider, **fields)

    def set_active(self, pk: int) -> AIProvider | None:
        """Activate one provider and deactivate all others."""
        session = self._repo.session
        for p in self._repo.list_all(AIProvider):
            p.is_active = (p.id == pk)
        session.commit()
        return self._repo.get_by_id(AIProvider, pk)

    def delete_provider(self, pk: int) -> bool:
        provider = self._repo.get_by_id(AIProvider, pk)
        if provider is None:
            return False
        self._repo.delete(provider)
        return True
