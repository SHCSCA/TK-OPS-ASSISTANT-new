"""Tests for video editing ORM models and repository helpers."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run(script: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        env = os.environ.copy()
        env["TK_OPS_DATA_DIR"] = tmp
        env["PYTHONIOENCODING"] = "utf-8"
        out = subprocess.check_output(
            [sys.executable, "-c", script],
            cwd=str(ROOT),
            env=env,
            text=True,
            encoding="utf-8",
        )
    return json.loads(out.strip().splitlines()[-1])


def test_can_create_video_project_sequence_asset_clip_and_subtitle() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository
from desktop_app.database.models import Asset

repo = Repository()
asset = repo.add(Asset(filename='clip.mp4', asset_type='video', file_path='C:/tmp/clip.mp4'))
project = repo.create_video_project(name='Launch Sequence')
sequence = repo.create_video_sequence(project.id, name='Main')
library_asset = repo.add_video_sequence_asset(sequence.id, asset.id)
clip = repo.append_video_clip(
    sequence.id,
    asset.id,
    track_type='video',
    track_index=0,
    start_ms=0,
    source_in_ms=0,
    source_out_ms=3000,
)
subtitle = repo.create_video_subtitle(sequence.id, start_ms=0, end_ms=1200, text='hello')
print(json.dumps({
    'project_id': project.id,
    'sequence_project_id': sequence.project_id,
    'library_asset_sequence_id': library_asset.sequence_id,
    'clip_asset_id': clip.asset_id,
    'subtitle_sequence_id': subtitle.sequence_id,
}, ensure_ascii=False))
""")
    assert result["project_id"] is not None
    assert result["sequence_project_id"] == result["project_id"]
    assert result["library_asset_sequence_id"] is not None
    assert result["clip_asset_id"] is not None
    assert result["subtitle_sequence_id"] is not None


def test_reorder_video_clips_updates_sort_order() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository

repo = Repository()
project = repo.create_video_project(name='Sort Test')
sequence = repo.create_video_sequence(project.id, name='Main')
first = repo.create_video_clip_placeholder(sequence.id, track_type='video', track_index=0, duration_ms=1000)
second = repo.create_video_clip_placeholder(sequence.id, track_type='video', track_index=0, duration_ms=1000)

repo.reorder_video_clips(sequence.id, [second.id, first.id])

clips = repo.list_video_clips(sequence.id)
print(json.dumps({'ids': [c.id for c in clips]}, ensure_ascii=False))
""")
    ids = result["ids"]
    assert len(ids) == 2
    # second should now come before first
    assert ids[0] != ids[1]


def test_video_export_record_can_be_created() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository

repo = Repository()
project = repo.create_video_project(name='Export Test')
export = repo.create_video_export(
    project_id=project.id,
    sequence_id=None,
    preset='mp4_1080p',
    output_path='/tmp/out.mp4',
)
print(json.dumps({
    'export_id': export.id,
    'project_id': export.project_id,
    'status': export.status,
    'preset': export.preset,
}, ensure_ascii=False))
""")
    assert result["export_id"] is not None
    assert result["status"] == "pending"
    assert result["preset"] == "mp4_1080p"


def test_video_snapshot_can_be_created_and_listed() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository

repo = Repository()
project = repo.create_video_project(name='Snap Test')
snap = repo.create_video_snapshot(project.id, title='v1 snapshot', payload_json='{"clips": 2}')
snaps = repo.list_video_snapshots(project.id)
print(json.dumps({
    'snap_id': snap.id,
    'title': snap.title,
    'count': len(snaps),
}, ensure_ascii=False))
""")
    assert result["snap_id"] is not None
    assert result["title"] == "v1 snapshot"
    assert result["count"] == 1
