from __future__ import annotations

# pyright: basic

"""Repository implementation for media assets and derived artifacts."""

from collections.abc import Callable
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.asset import Asset

from .base import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    """Persistence adapter for content asset records."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        super().__init__(session_factory, Asset)

    def get_active_assets(self, asset_type: str | None = None) -> list[Asset]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            asset_deleted = cast(Any, getattr(Asset, "is_deleted"))
            asset_created = cast(Any, getattr(Asset, "created_at"))
            asset_type_column = cast(Any, getattr(Asset, "asset_type"))
            statement = cast(Any, select(Asset))
            statement = statement.where(asset_deleted.is_(False)).order_by(asset_created.desc())
            if asset_type is not None:
                statement = statement.where(asset_type_column == asset_type)
            return list(session_any.scalars(statement).all())

    def get_by_file_path(self, file_path: str) -> Asset | None:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            path_column = cast(Any, getattr(Asset, "file_path"))
            statement = cast(Any, select(Asset))
            statement = statement.where(path_column == file_path)
            return session_any.scalars(statement).first()

    def get_deleted_assets(self) -> list[Asset]:
        with self._read_session() as session:  # type: ignore[attr-defined]
            session_any = cast(Any, session)
            asset_deleted = cast(Any, getattr(Asset, "is_deleted"))
            deleted_at = cast(Any, getattr(Asset, "deleted_at"))
            statement = cast(Any, select(Asset))
            statement = statement.where(asset_deleted.is_(True)).order_by(deleted_at.desc())
            return list(session_any.scalars(statement).all())
