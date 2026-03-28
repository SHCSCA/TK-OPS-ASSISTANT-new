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

    def read_text_preview(
        self,
        file_path: str | None,
        *,
        max_chars: int = 220,
        max_bytes: int = 8192,
    ) -> dict[str, Any]:
        path_text = str(file_path or "").strip()
        if not path_text:
            return {"preview": "", "encoding": "", "reason": "empty_path"}

        path = Path(path_text).expanduser()
        if not path.exists() or not path.is_file():
            return {"preview": "", "encoding": "", "reason": "missing_file"}

        if path.suffix.lower() in {".mp4", ".mov", ".avi", ".mkv", ".webm", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".xlsx", ".xls"}:
            return {"preview": "", "encoding": "", "reason": "binary_file"}

        raw = b""
        try:
            with path.open("rb") as stream:
                raw = stream.read(max(1024, int(max_bytes or 8192)))
        except OSError:
            return {"preview": "", "encoding": "", "reason": "read_failed"}

        encodings = ("utf-8", "utf-8-sig", "gb18030", "latin-1")
        decoded = ""
        encoding_used = ""
        for encoding in encodings:
            try:
                decoded = raw.decode(encoding)
                encoding_used = encoding
                break
            except UnicodeDecodeError:
                continue

        if not decoded:
            return {"preview": "", "encoding": "", "reason": "decode_failed"}

        text = decoded.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n").strip()
        limit = max(40, int(max_chars or 220))
        if len(text) > limit:
            text = text[:limit] + "…"
        return {"preview": text, "encoding": encoding_used, "reason": "ok"}

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
