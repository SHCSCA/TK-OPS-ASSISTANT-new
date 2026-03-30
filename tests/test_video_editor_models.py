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


def test_can_create_video_project_sequence_clip_and_subtitle() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.models import Asset
from desktop_app.database.repository import Repository

repo = Repository()
asset = repo.add(Asset(filename='clip.mp4', asset_type='video', file_path='C:/tmp/clip.mp4'))
project = repo.create_video_project(name='Launch Sequence')
sequence = repo.create_video_sequence(project.id, name='Main Sequence')
clip = repo.append_video_clip(
    sequence.id,
    asset.id,
    track_type='video',
    track_index=0,
    start_ms=0,
    source_in_ms=0,
    source_out_ms=3000,
)
subtitle = repo.create_video_subtitle(
    sequence.id,
    start_ms=0,
    end_ms=1200,
    text='hello',
)
print(json.dumps({
    'project_id': project.id,
    'sequence_project_id': sequence.project_id,
    'clip_asset_id': clip.asset_id,
    'subtitle_sequence_id': subtitle.sequence_id,
}, ensure_ascii=False))
"""
    )

    assert result["project_id"] is not None
    assert result["sequence_project_id"] == result["project_id"]
    assert result["clip_asset_id"] is not None
    assert result["subtitle_sequence_id"] is not None


def test_reorder_video_clips_updates_sort_order() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.models import Asset
from desktop_app.database.repository import Repository

repo = Repository()
asset_a = repo.add(Asset(filename='a.mp4', asset_type='video', file_path='C:/tmp/a.mp4'))
asset_b = repo.add(Asset(filename='b.mp4', asset_type='video', file_path='C:/tmp/b.mp4'))
project = repo.create_video_project(name='Sort Test')
sequence = repo.create_video_sequence(project.id, name='Main Sequence')
first = repo.create_video_clip_placeholder(
    sequence.id,
    track_type='video',
    track_index=0,
    duration_ms=1000,
)
second = repo.append_video_clip(
    sequence.id,
    asset_b.id,
    track_type='video',
    track_index=0,
    start_ms=1000,
    source_in_ms=0,
    source_out_ms=1000,
)
repo.append_video_clip(
    sequence.id,
    asset_a.id,
    track_type='video',
    track_index=0,
    start_ms=2000,
    source_in_ms=0,
    source_out_ms=1000,
)
repo.reorder_video_clips(sequence.id, [second.id, first.id])
clips = repo.list_video_clips(sequence.id)
print(json.dumps({
    'ordered_ids': [clip.id for clip in clips],
}, ensure_ascii=False))
"""
    )

    assert len(result["ordered_ids"]) == 2
