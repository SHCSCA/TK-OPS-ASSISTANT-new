from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


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


def test_append_assets_to_sequence_creates_real_clips() -> None:
    _run_isolated_script(
        """
import json
from desktop_app.database.models import Asset
from desktop_app.database.repository import Repository
from desktop_app.services.video_editing_service import VideoEditingService

repo = Repository()
service = VideoEditingService(repo)
asset = repo.add(Asset(filename='clip.mp4', asset_type='video', file_path='C:/tmp/clip.mp4'))
project = service.create_project('Editor Project')
sequence = service.create_sequence(project.id, 'Main Sequence')
clips = service.append_assets_to_sequence(sequence.id, [asset.id])
print(json.dumps({
    'project_id': project.id,
    'sequence_project_id': sequence.project_id,
    'clip_count': len(clips),
    'first_clip_asset_id': clips[0].asset_id if clips else None,
}, ensure_ascii=False))
"""
    )


def test_update_clip_range_rejects_invalid_ranges() -> None:
    _run_isolated_script(
        """
import json
from desktop_app.database.models import Asset
from desktop_app.database.repository import Repository
from desktop_app.services.video_editing_service import VideoEditingService

repo = Repository()
service = VideoEditingService(repo)
asset = repo.add(Asset(filename='clip.mp4', asset_type='video', file_path='C:/tmp/clip.mp4'))
project = service.create_project('Trim Project')
sequence = service.create_sequence(project.id, 'Main Sequence')
clip = service.append_assets_to_sequence(sequence.id, [asset.id])[0]

try:
    service.update_clip_range(clip.id, source_in_ms=2800, source_out_ms=1200)
except ValueError as exc:
    print(json.dumps({
        'error': str(exc),
    }, ensure_ascii=False))
else:
    raise AssertionError('expected ValueError')
"""
    )


def test_validate_export_blocks_missing_source_file() -> None:
    _run_isolated_script(
        """
import json
from desktop_app.database.models import Asset
from desktop_app.database.repository import Repository
from desktop_app.services.video_editing_service import VideoEditingService

repo = Repository()
service = VideoEditingService(repo)
asset = repo.add(Asset(filename='missing.mp4', asset_type='video', file_path='C:/tmp/missing.mp4'))
project = service.create_project('Export Project')
sequence = service.create_sequence(project.id, 'Main Sequence')
service.append_assets_to_sequence(sequence.id, [asset.id])
result = service.validate_export(project.id, sequence.id)
print(json.dumps(result, ensure_ascii=False))
"""
    )
