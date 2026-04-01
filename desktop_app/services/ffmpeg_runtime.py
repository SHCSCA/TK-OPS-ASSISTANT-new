"""FFmpeg runtime discovery helpers."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Final

FFMPEG_RELATIVE_DIR: Final[Path] = Path("tools") / "ffmpeg" / "win64"
FFMPEG_EXE_NAME: Final[str] = "ffmpeg.exe"
FFPROBE_EXE_NAME: Final[str] = "ffprobe.exe"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _packaged_roots() -> list[Path]:
    if not getattr(sys, "frozen", False):
        return []

    roots: list[Path] = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        roots.append(Path(meipass))

    exe_root = Path(sys.executable).resolve().parent
    if exe_root not in roots:
        roots.append(exe_root)
    return roots


def _candidate_roots(root: Path | None = None) -> list[Path]:
    roots: list[Path] = []
    if root is not None:
        roots.append(Path(root))

    repo_root = _repo_root()
    if repo_root not in roots:
        roots.append(repo_root)

    for packaged_root in _packaged_roots():
        if packaged_root not in roots:
            roots.append(packaged_root)
    return roots


def _resolve_from_root(candidate_root: Path) -> tuple[Path, Path] | None:
    tools_dir = Path(candidate_root) / FFMPEG_RELATIVE_DIR
    ffmpeg_path = tools_dir / FFMPEG_EXE_NAME
    ffprobe_path = tools_dir / FFPROBE_EXE_NAME
    if ffmpeg_path.is_file() and ffprobe_path.is_file():
        return ffmpeg_path, ffprobe_path
    return None


def resolve_ffmpeg_binaries(root: Path | None = None) -> tuple[Path, Path]:
    for candidate_root in _candidate_roots(root):
        resolved = _resolve_from_root(candidate_root)
        if resolved is not None:
            return resolved

    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    if ffmpeg_path and ffprobe_path:
        return Path(ffmpeg_path), Path(ffprobe_path)

    raise FileNotFoundError(
        "未找到可用的 ffmpeg 和 ffprobe。请将工具放入 tools/ffmpeg/win64，"
        "或在开发环境中先安装到 PATH。"
    )


def ensure_ffmpeg_available(root: Path | None = None) -> dict[str, object]:
    try:
        ffmpeg_path, ffprobe_path = resolve_ffmpeg_binaries(root=root)
    except FileNotFoundError as exc:
        return {"ok": False, "error": str(exc), "ffmpeg": "", "ffprobe": ""}
    return {
        "ok": True,
        "error": "",
        "ffmpeg": str(ffmpeg_path),
        "ffprobe": str(ffprobe_path),
    }
