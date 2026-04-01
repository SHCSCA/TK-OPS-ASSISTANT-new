from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _run_isolated_script(script: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temp_dir:
        env = os.environ.copy()
        env["TK_OPS_DATA_DIR"] = temp_dir
        env["PYTHONIOENCODING"] = "utf-8"
        output = subprocess.check_output(
            [sys.executable, "-c", script],
            cwd=str(ROOT),
            env=env,
            text=True,
            encoding="utf-8",
        )
    return json.loads(output.strip().splitlines()[-1])


def _write_sample_video(target_path: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        pytest.skip("ffmpeg not available in PATH")
    subprocess.check_call(
        [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=320x240:d=1",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=stereo",
            "-shortest",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(target_path),
        ]
    )


def test_resolve_ffmpeg_binaries_prefers_bundled_tools(tmp_path: Path) -> None:
    tools_dir = tmp_path / "tools" / "ffmpeg" / "win64"
    tools_dir.mkdir(parents=True)
    (tools_dir / "ffmpeg.exe").write_bytes(b"")
    (tools_dir / "ffprobe.exe").write_bytes(b"")

    script = f"""
import json
from pathlib import Path
from desktop_app.services.ffmpeg_runtime import resolve_ffmpeg_binaries

ffmpeg, ffprobe = resolve_ffmpeg_binaries(root=Path(r"{tmp_path}"))
print(json.dumps({{
    'ffmpeg_name': ffmpeg.name,
    'ffprobe_name': ffprobe.name,
    'ffmpeg_path': str(ffmpeg),
    'ffprobe_path': str(ffprobe),
}}, ensure_ascii=False))
"""

    result = _run_isolated_script(script)
    assert result["ffmpeg_name"] == "ffmpeg.exe"
    assert result["ffprobe_name"] == "ffprobe.exe"
    assert str(tmp_path / "tools" / "ffmpeg" / "win64" / "ffmpeg.exe") == result["ffmpeg_path"]
    assert str(tmp_path / "tools" / "ffmpeg" / "win64" / "ffprobe.exe") == result["ffprobe_path"]


def test_validate_and_create_export_rejects_invalid_sequence() -> None:
    script = """
import json
from desktop_app.services.video_export_service import VideoExportService
from desktop_app.database.repository import Repository

repo = Repository()
service = VideoExportService(repo)
result = service.validate_and_create_export(project_id=1, sequence_id=1, preset='mp4_1080p')
print(json.dumps(result, ensure_ascii=False))
"""

    result = _run_isolated_script(script)
    assert result["ok"] is False
    assert "序列不存在" in str(result["error"])


def test_minimal_export_writes_output_file() -> None:
    sample_source = Path(tempfile.mkdtemp()) / "demo.mp4"
    _write_sample_video(sample_source)
    script = """
import json
import os
from pathlib import Path
from desktop_app.database.models import Asset
from desktop_app.database.repository import Repository
from desktop_app.services.video_export_service import VideoExportService

repo = Repository()
media_dir = Path(os.environ['TK_OPS_DATA_DIR']) / 'media'
media_dir.mkdir(parents=True, exist_ok=True)
source_path = media_dir / 'demo.mp4'
source_path.write_bytes(Path(r'__SOURCE_PATH__').read_bytes())
asset = repo.add(Asset(filename='demo.mp4', asset_type='video', file_path=str(source_path)))
service = VideoExportService(repo)
project, sequence = service.create_project_with_sequence('Minimal Export')
service.append_assets_to_sequence(sequence.id, [asset.id])
created = service.validate_and_create_export(project.id, sequence.id, preset='mp4_1080p')
completed = service.run_export(created['export_id'])
print(json.dumps({
    'status': completed.status,
    'output_path_exists': Path(completed.output_path).exists(),
}, ensure_ascii=False))
"""
    script = script.replace("__SOURCE_PATH__", str(sample_source))

    result = _run_isolated_script(script)
    assert result["status"] == "completed"
    assert result["output_path_exists"] is True
