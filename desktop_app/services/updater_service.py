"""Version check, download and auto-update service via GitHub Releases API."""
from __future__ import annotations

import hashlib
import logging
import os
import subprocess
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from desktop_app.database import APP_VERSION, DATA_DIR

log = logging.getLogger(__name__)

# Configure your GitHub repo here
_GITHUB_OWNER = "your-org"
_GITHUB_REPO = "TK-OPS-ASSISTANT"

_DOWNLOAD_DIR = DATA_DIR / "updates"


@dataclass(frozen=True)
class ReleaseInfo:
    tag: str
    version: str
    html_url: str
    download_url: str
    sha256_url: str          # URL for .sha256 checksum file (if available)
    body: str                # release notes (markdown)
    has_update: bool
    asset_name: str = ""     # e.g. "TK-OPS-ASSISTANT-1.2.0-setup.exe"
    asset_size: int = 0      # bytes


@dataclass
class DownloadProgress:
    """Mutable progress tracker shared with the download thread."""
    state: str = "idle"       # idle | downloading | verifying | done | error
    percent: int = 0
    downloaded: int = 0
    total: int = 0
    speed: str = ""           # human-readable speed
    file_path: str = ""
    error: str = ""


def _parse_version(tag: str) -> tuple[int, ...]:
    """Convert 'v1.2.3' or '1.2.3' to (1, 2, 3)."""
    clean = tag.lstrip("vV")
    parts: list[int] = []
    for p in clean.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024  # type: ignore[assignment]
    return f"{n:.1f} TB"


class UpdaterService:
    """Check GitHub releases for new versions, download and apply updates."""

    def __init__(
        self,
        owner: str = _GITHUB_OWNER,
        repo: str = _GITHUB_REPO,
    ) -> None:
        self._owner = owner
        self._repo = repo
        self._url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        self._current = _parse_version(APP_VERSION)
        self._progress = DownloadProgress()
        self._download_thread: threading.Thread | None = None
        self._latest_release: ReleaseInfo | None = None

    @property
    def current_version(self) -> str:
        return APP_VERSION

    # ── Check ──────────────────────────────────────

    def check_update(self) -> ReleaseInfo | None:
        """Query latest release. Returns ReleaseInfo or None on error."""
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(
                    self._url,
                    headers={"Accept": "application/vnd.github+json"},
                )
                if resp.status_code == 404:
                    log.info("No releases found.")
                    return None
                resp.raise_for_status()
                data: dict[str, Any] = resp.json()
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            log.warning("Update check failed: %s", exc)
            return None

        tag = data.get("tag_name", "")
        remote_ver = _parse_version(tag)
        has_update = remote_ver > self._current

        # Find Windows exe/zip asset and optional sha256 sidecar
        download_url = ""
        sha256_url = ""
        asset_name = ""
        asset_size = 0
        for asset in data.get("assets", []):
            name: str = asset.get("name", "")
            if name.endswith(".sha256"):
                sha256_url = asset.get("browser_download_url", "")
            elif name.endswith(".exe") or name.endswith(".zip"):
                download_url = asset.get("browser_download_url", "")
                asset_name = name
                asset_size = asset.get("size", 0)

        info = ReleaseInfo(
            tag=tag,
            version=".".join(str(x) for x in remote_ver),
            html_url=data.get("html_url", ""),
            download_url=download_url,
            sha256_url=sha256_url,
            body=data.get("body", ""),
            has_update=has_update,
            asset_name=asset_name,
            asset_size=asset_size,
        )
        self._latest_release = info
        return info

    # ── Download ───────────────────────────────────

    def start_download(self, download_url: str | None = None) -> bool:
        """Begin downloading the update asset in a background thread.
        Returns True if download started, False if already in progress."""
        if self._download_thread and self._download_thread.is_alive():
            return False

        url = download_url or (self._latest_release.download_url if self._latest_release else "")
        if not url:
            self._progress.state = "error"
            self._progress.error = "无下载链接"
            return False

        self._progress = DownloadProgress(state="downloading")
        self._download_thread = threading.Thread(
            target=self._download_worker, args=(url,), daemon=True
        )
        self._download_thread.start()
        return True

    def get_download_progress(self) -> dict:
        p = self._progress
        return {
            "state": p.state,
            "percent": p.percent,
            "downloaded": p.downloaded,
            "downloadedHuman": _human_size(p.downloaded),
            "total": p.total,
            "totalHuman": _human_size(p.total),
            "speed": p.speed,
            "filePath": p.file_path,
            "error": p.error,
        }

    def _download_worker(self, url: str) -> None:
        """Run in background thread: stream-download the asset."""
        try:
            _DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
            filename = url.rsplit("/", 1)[-1] or "update-package"
            dest = _DOWNLOAD_DIR / filename

            with httpx.Client(timeout=60, follow_redirects=True) as client:
                with client.stream("GET", url) as resp:
                    resp.raise_for_status()
                    total = int(resp.headers.get("content-length", 0))
                    self._progress.total = total
                    downloaded = 0

                    with open(dest, "wb") as f:
                        import time
                        last_time = time.monotonic()
                        last_bytes = 0
                        for chunk in resp.iter_bytes(chunk_size=65536):
                            f.write(chunk)
                            downloaded += len(chunk)
                            self._progress.downloaded = downloaded
                            if total > 0:
                                self._progress.percent = int(downloaded * 100 / total)

                            # Speed calc every 0.5s
                            now = time.monotonic()
                            dt = now - last_time
                            if dt >= 0.5:
                                speed = (downloaded - last_bytes) / dt
                                self._progress.speed = _human_size(int(speed)) + "/s"
                                last_time = now
                                last_bytes = downloaded

            self._progress.file_path = str(dest)

            # Verify SHA256 if sidecar available
            if self._latest_release and self._latest_release.sha256_url:
                self._progress.state = "verifying"
                if not self._verify_sha256(dest, self._latest_release.sha256_url):
                    self._progress.state = "error"
                    self._progress.error = "SHA256 校验失败，文件可能损坏"
                    try:
                        dest.unlink()
                    except OSError:
                        pass
                    return

            self._progress.state = "done"
            self._progress.percent = 100
            log.info("Update downloaded to %s", dest)
        except Exception as exc:
            log.exception("Download failed")
            self._progress.state = "error"
            self._progress.error = str(exc)

    # ── Verify ─────────────────────────────────────

    @staticmethod
    def _verify_sha256(filepath: Path, sha256_url: str) -> bool:
        """Download the .sha256 sidecar and compare with local file hash."""
        try:
            with httpx.Client(timeout=10, follow_redirects=True) as client:
                resp = client.get(sha256_url)
                resp.raise_for_status()
                expected = resp.text.strip().split()[0].lower()

            sha = hashlib.sha256()
            with open(filepath, "rb") as f:
                for block in iter(lambda: f.read(65536), b""):
                    sha.update(block)
            actual = sha.hexdigest().lower()
            if actual != expected:
                log.error("SHA256 mismatch: expected %s, got %s", expected, actual)
                return False
            log.info("SHA256 verified OK")
            return True
        except Exception as exc:
            log.warning("SHA256 verification skipped: %s", exc)
            # If we can't verify, we still allow the update (lenient mode)
            return True

    # ── Apply ──────────────────────────────────────

    def apply_update(self) -> dict:
        """Launch the downloaded installer and request app exit.
        Returns {"ok": True} or {"ok": False, "error": ...}."""
        filepath = self._progress.file_path
        if not filepath or not Path(filepath).exists():
            return {"ok": False, "error": "未找到已下载的更新文件"}

        try:
            if filepath.endswith(".exe"):
                # Launch installer detached
                subprocess.Popen(
                    [filepath],
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                    if sys.platform == "win32" else 0,
                    close_fds=True,
                )
            elif filepath.endswith(".zip"):
                # For zip, open the containing folder for manual extraction
                folder = str(Path(filepath).parent)
                if sys.platform == "win32":
                    os.startfile(folder)
                return {"ok": True, "action": "zip_opened"}

            return {"ok": True, "action": "installer_launched"}
        except Exception as exc:
            log.exception("Failed to apply update")
            return {"ok": False, "error": str(exc)}
