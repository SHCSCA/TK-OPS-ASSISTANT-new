"""Asset management service."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from desktop_app.database.models import Asset
from desktop_app.database.repository import Repository


class AssetService:
    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    def list_assets(self, *, asset_type: str | None = None) -> Sequence[Asset]:
        return self._repo.list_assets(asset_type=asset_type)

    def get_asset(self, pk: int) -> Asset | None:
        return self._repo.get_by_id(Asset, pk)

    def _detect_file_size(self, file_path: str | None, fallback: int = 0) -> int:
        path = str(file_path or '').strip()
        if not path:
            return int(fallback or 0)
        try:
            return int(Path(path).stat().st_size)
        except OSError:
            return int(fallback or 0)

    def create_asset(self, filename: str, **kwargs: Any) -> Asset:
        kwargs = dict(kwargs)
        kwargs["file_size"] = self._detect_file_size(
            kwargs.get("file_path"),
            int(kwargs.get("file_size") or 0),
        )
        return self._repo.add(Asset(filename=filename, **kwargs))

    def update_asset(self, pk: int, **fields: Any) -> Asset | None:
        asset = self._repo.get_by_id(Asset, pk)
        if asset is None:
            return None
        fields = dict(fields)
        if "file_path" in fields:
            fields["file_size"] = self._detect_file_size(
                fields.get("file_path"),
                int(fields.get("file_size") or asset.file_size or 0),
            )
        return self._repo.update(asset, **fields)

    def delete_asset(self, pk: int) -> bool:
        asset = self._repo.get_by_id(Asset, pk)
        if asset is None:
            return False
        self._repo.delete(asset)
        return True

    def count_by_type(self) -> dict[str, int]:
        """Return asset count broken down by asset_type."""
        from sqlalchemy import func, select
        stmt = select(Asset.asset_type, func.count(Asset.id)).group_by(Asset.asset_type)
        rows = self._repo.session.execute(stmt).all()
        return {row[0]: row[1] for row in rows if row[0]}
