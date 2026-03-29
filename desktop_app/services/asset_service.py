"""Asset management service."""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse
from typing import Any, Sequence

from desktop_app.database import DATA_DIR
from desktop_app.database.models import Asset
from desktop_app.database.repository import Repository


class AssetService:
    _VIDEO_EXTENSIONS = {
        ".mp4",
        ".mov",
        ".m4v",
        ".avi",
        ".mkv",
        ".webm",
        ".wmv",
        ".qt",
    }

    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    def _normalize_local_path(self, file_path: str | None) -> Path | None:
        text = str(file_path or "").strip()
        if not text:
            return None

        if text.startswith("file://"):
            parsed = urlparse(text)
            if parsed.scheme != "file":
                return None
            if parsed.netloc:
                text = f"//{parsed.netloc}{parsed.path}"
            else:
                text = parsed.path
            text = unquote(text)
            if len(text) > 2 and text[0] == "/" and text[2] == ":":
                text = text.lstrip("/")

        return Path(text).expanduser()

    def _video_poster_path(self, source_path: Path, stat_result: Any) -> Path:
        key = "|".join(
            [
                str(source_path.resolve(strict=False)),
                str(int(getattr(stat_result, "st_mtime_ns", 0) or 0)),
                str(int(getattr(stat_result, "st_size", 0) or 0)),
                "v1",
            ]
        )
        digest = hashlib.sha1(key.encode("utf-8", errors="ignore")).hexdigest()
        return DATA_DIR / "asset-posters" / f"{digest}.jpg"

    def _video_candidate(self, file_path: str | None) -> tuple[Path | None, str]:
        source_path = self._normalize_local_path(file_path)
        if source_path is None:
            return None, "empty_path"
        if not source_path.exists() or not source_path.is_file():
            return None, "missing_file"
        if source_path.suffix.lower() not in self._VIDEO_EXTENSIONS:
            return None, "not_video"
        return source_path, "ok"

    def _save_first_video_frame(self, source_path: Path, poster_path: Path, timeout_ms: int = 8000) -> str:
        try:
            from PySide6.QtCore import QEventLoop, QTimer, QUrl
            from PySide6.QtGui import QGuiApplication
            from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer, QVideoSink
        except Exception:
            return "multimedia_unavailable"

        if QGuiApplication.instance() is None:
            return "no_qapplication"

        poster_path.parent.mkdir(parents=True, exist_ok=True)

        loop = QEventLoop()
        player = QMediaPlayer()
        audio = QAudioOutput()
        sink = QVideoSink()
        audio.setVolume(0.0)
        player.setAudioOutput(audio)
        player.setVideoSink(sink)

        tmp_path = poster_path.parent / f"{poster_path.name}.tmp"
        outcome = {"reason": "timeout", "saved": False}
        finished = False

        def finish(reason: str) -> None:
            nonlocal finished
            if finished:
                return
            finished = True
            outcome["reason"] = reason
            if loop.isRunning():
                loop.quit()

        def capture_frame(frame: Any) -> None:
            if outcome["saved"] or not frame.isValid():
                return
            image = frame.toImage()
            if image.isNull():
                return
            if not image.save(str(tmp_path), "JPG", 92):
                return
            try:
                if poster_path.exists():
                    poster_path.unlink()
                tmp_path.replace(poster_path)
            except OSError:
                try:
                    tmp_path.unlink(missing_ok=True)
                except OSError:
                    pass
                finish("write_failed")
                return
            outcome["saved"] = True
            finish("ok")

        def on_status(status: Any) -> None:
            loaded_statuses = {
                QMediaPlayer.MediaStatus.LoadedMedia,
                QMediaPlayer.MediaStatus.BufferedMedia,
                QMediaPlayer.MediaStatus.BufferingMedia,
            }
            if status not in loaded_statuses:
                return
            try:
                player.setPosition(0)
            except Exception:
                pass
            try:
                player.play()
            except Exception:
                pass

        def on_error(*_: Any) -> None:
            finish("playback_error")

        sink.videoFrameChanged.connect(capture_frame)
        player.mediaStatusChanged.connect(on_status)
        player.errorOccurred.connect(on_error)
        player.setSource(QUrl.fromLocalFile(str(source_path)))

        try:
            player.play()
        except Exception:
            finish("playback_error")
        if finished:
            player.stop()
            return outcome["reason"]

        QTimer.singleShot(timeout_ms, lambda: finish("timeout"))
        loop.exec()
        player.stop()
        return outcome["reason"]

    def _poster_worker_executable(self) -> str:
        python_path = Path(sys.executable)
        if os.name == "nt":
            pythonw_path = python_path.with_name("pythonw.exe")
            if pythonw_path.exists():
                return str(pythonw_path)
        return str(python_path)

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

    def get_video_poster(self, file_path: str | None) -> dict[str, Any]:
        source_path, reason = self._video_candidate(file_path)
        if source_path is None:
            return {"poster_path": "", "reason": reason}

        try:
            stat_result = source_path.stat()
        except OSError:
            return {"poster_path": "", "reason": "stat_failed"}

        poster_path = self._video_poster_path(source_path, stat_result)
        if poster_path.exists() and poster_path.stat().st_size > 0:
            return {"poster_path": str(poster_path), "reason": "cached"}

        poster_path.parent.mkdir(parents=True, exist_ok=True)
        poster_path.unlink(missing_ok=True)
        capture_reason = self._save_first_video_frame(source_path, poster_path)
        if capture_reason != "ok" or not poster_path.exists():
            try:
                poster_path.unlink(missing_ok=True)
            except OSError:
                pass
            return {"poster_path": "", "reason": capture_reason}

        return {"poster_path": str(poster_path), "reason": "generated"}

    def get_video_poster_cached(self, file_path: str | None) -> dict[str, Any]:
        source_path, reason = self._video_candidate(file_path)
        if source_path is None:
            return {"poster_path": "", "reason": reason}
        try:
            stat_result = source_path.stat()
        except OSError:
            return {"poster_path": "", "reason": "stat_failed"}
        poster_path = self._video_poster_path(source_path, stat_result)
        if poster_path.exists() and poster_path.stat().st_size > 0:
            return {"poster_path": str(poster_path), "reason": "cached"}
        return {"poster_path": "", "reason": "missing_cache"}

    def schedule_video_poster_generation(self, file_path: str | None) -> bool:
        source_path, reason = self._video_candidate(file_path)
        if source_path is None or reason != "ok":
            return False
        cached = self.get_video_poster_cached(str(source_path))
        if cached.get("poster_path"):
            return True
        python_exe = self._poster_worker_executable()
        if not python_exe:
            return False

        code = (
            "import sys;"
            "from PySide6.QtGui import QGuiApplication;"
            "from desktop_app.services.asset_service import AssetService;"
            "app=QGuiApplication(sys.argv);"
            "AssetService().get_video_poster(sys.argv[1]);"
        )
        kwargs: dict[str, Any] = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
        }
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            kwargs["startupinfo"] = startupinfo

        try:
            subprocess.Popen([python_exe, "-c", code, str(source_path)], **kwargs)
            return True
        except Exception:
            return False

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
