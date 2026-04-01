from __future__ import annotations

from pathlib import Path
import shutil

from desktop_app.services.ffmpeg_runtime import resolve_ffmpeg_binaries


ROOT = Path(__file__).resolve().parents[1]


def test_tk_ops_spec_includes_ffmpeg_bundle_path() -> None:
    spec_text = (ROOT / "tk_ops.spec").read_text(encoding="utf-8")
    assert "tools/ffmpeg/win64" in spec_text


def test_build_py_contains_ffmpeg_packaging_sync_contract() -> None:
    build_text = (ROOT / "build.py").read_text(encoding="utf-8")
    assert "ffmpeg" in build_text.lower()
    assert "tools/ffmpeg/win64" in build_text


def test_resolve_ffmpeg_binaries_prefers_bundled_tools_over_path(tmp_path: Path, monkeypatch) -> None:
    tools_dir = tmp_path / "tools" / "ffmpeg" / "win64"
    tools_dir.mkdir(parents=True)
    bundled_ffmpeg = tools_dir / "ffmpeg.exe"
    bundled_ffprobe = tools_dir / "ffprobe.exe"
    bundled_ffmpeg.write_bytes(b"")
    bundled_ffprobe.write_bytes(b"")

    path_ffmpeg = Path(r"D:\ffmpeg\bin\ffmpeg.exe")
    path_ffprobe = Path(r"D:\ffmpeg\bin\ffprobe.exe")

    monkeypatch.setattr(
        shutil,
        "which",
        lambda executable: str(path_ffmpeg if executable == "ffmpeg" else path_ffprobe),
    )

    resolved_ffmpeg, resolved_ffprobe = resolve_ffmpeg_binaries(root=tmp_path)

    assert resolved_ffmpeg == bundled_ffmpeg
    assert resolved_ffprobe == bundled_ffprobe
