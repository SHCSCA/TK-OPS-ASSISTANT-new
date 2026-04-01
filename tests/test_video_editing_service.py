"""Tests for VideoEditingService."""
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


def test_append_assets_to_sequence_imports_only_into_library() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository
from desktop_app.database.models import Asset
from desktop_app.services.video_editing_service import VideoEditingService

repo = Repository()
service = VideoEditingService(repo)
project = service.create_project('Editor Project')
sequence = service.create_sequence(project.id, 'Main')
asset = repo.add(Asset(filename='clip.mp4', asset_type='video', file_path='C:/tmp/clip.mp4'))
created = service.append_assets_to_sequence(sequence.id, [asset.id])
clips = service.list_clips(sequence.id)
print(json.dumps({'count': len(created), 'asset_id': created[0].asset_id, 'clip_count': len(clips)}, ensure_ascii=False))
""")
    assert result["count"] == 1
    assert result["asset_id"] is not None
    assert result["clip_count"] == 0


def test_add_assets_to_timeline_creates_real_clips_from_library_asset() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository
from desktop_app.database.models import Asset
from desktop_app.services.video_editing_service import VideoEditingService

repo = Repository()
service = VideoEditingService(repo)
project = service.create_project('Timeline Project')
sequence = service.create_sequence(project.id, 'Main')
asset = repo.add(Asset(filename='clip.mp4', asset_type='video', file_path='C:/tmp/clip.mp4'))
service.append_assets_to_sequence(sequence.id, [asset.id])
created = service.add_assets_to_timeline(sequence.id, [asset.id])
clips = service.list_clips(sequence.id)
print(json.dumps({'count': len(created), 'clip_count': len(clips), 'asset_id': created[0].asset_id}, ensure_ascii=False))
""")
    assert result["count"] == 1
    assert result["clip_count"] == 1
    assert result["asset_id"] is not None


def test_trim_clip_rejects_invalid_ranges() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository
from desktop_app.services.video_editing_service import VideoEditingService

repo = Repository()
service = VideoEditingService(repo)
project = service.create_project('Trim Test')
sequence = service.create_sequence(project.id, 'Main')
clip = repo.create_video_clip_placeholder(sequence.id, track_type='video', track_index=0, duration_ms=3000)
try:
    service.update_clip_range(clip.id, source_in_ms=2800, source_out_ms=1200)
    print(json.dumps({'error': None}))
except ValueError as exc:
    print(json.dumps({'error': str(exc)}, ensure_ascii=False))
""")
    assert result["error"] is not None
    assert "裁切" in result["error"]


def test_export_validation_blocks_empty_sequence() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository
from desktop_app.services.video_editing_service import VideoEditingService

repo = Repository()
service = VideoEditingService(repo)
project, sequence = service.create_project_with_sequence('Empty')
result = service.validate_export(project.id, sequence.id)
print(json.dumps(result, ensure_ascii=False))
""")
    assert result["ok"] is False
    assert len(result["errors"]) > 0


def test_export_validation_blocks_missing_source_file() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository
from desktop_app.database.models import Asset
from desktop_app.services.video_editing_service import VideoEditingService

repo = Repository()
service = VideoEditingService(repo)
project, sequence = service.create_project_with_sequence('Validation')
asset = repo.add(Asset(filename='missing.mp4', asset_type='video', file_path='C:/tmp/missing.mp4'))
service.append_assets_to_sequence(sequence.id, [asset.id])
result = service.validate_export(project.id, sequence.id)
print(json.dumps(result, ensure_ascii=False))
""")
    assert result["ok"] is False
    assert any("源文件" in e or "不存在" in e for e in result["errors"])


def test_create_snapshot_saves_project_state() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository
from desktop_app.services.video_editing_service import VideoEditingService

repo = Repository()
service = VideoEditingService(repo)
project = service.create_project('Snap Project')
snap = service.create_snapshot(project.id, 'v1')
print(json.dumps({'snap_id': snap.id, 'title': snap.title}, ensure_ascii=False))
""")
    assert result["snap_id"] is not None
    assert result["title"] == "v1"


def test_remove_assets_from_sequence_only_removes_editor_library_clip() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository
from desktop_app.database.models import Asset
from desktop_app.services.video_editing_service import VideoEditingService

repo = Repository()
service = VideoEditingService(repo)
project, sequence = service.create_project_with_sequence('Remove Clip')
asset = repo.add(Asset(filename='clip.mp4', asset_type='video', file_path=''))
service.append_assets_to_sequence(sequence.id, [asset.id])
service.add_assets_to_timeline(sequence.id, [asset.id])
removed = service.remove_assets_from_sequence(sequence.id, [asset.id])
remaining_assets = repo.list_assets()
remaining_clips = service.list_clips(sequence.id)
print(json.dumps({
    'removed': removed,
    'asset_count': len(remaining_assets),
    'clip_count': len(remaining_clips),
}, ensure_ascii=False))
""")
    assert result['removed'] == 1
    assert result['asset_count'] == 1
    assert result['clip_count'] == 0


def test_service_can_create_update_and_delete_video_subtitle() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository
from desktop_app.services.video_editing_service import VideoEditingService

repo = Repository()
service = VideoEditingService(repo)
project, sequence = service.create_project_with_sequence('Subtitle Flow')
subtitle = service.create_subtitle(sequence.id, start_ms=0, end_ms=1500, text='第一版文案')
updated = service.update_subtitle(subtitle.id, start_ms=300, end_ms=2100, text='终版文案')
deleted = service.delete_subtitle(updated.id)
remaining = service.list_subtitles(sequence.id)
print(json.dumps({
    'created_id': subtitle.id,
    'updated_text': updated.text,
    'deleted': deleted,
    'remaining': len(remaining),
}, ensure_ascii=False))
""")
    assert result['created_id'] is not None
    assert result['updated_text'] == '终版文案'
    assert result['deleted'] is True
    assert result['remaining'] == 0


def test_service_can_update_audio_clip_volume_and_mute_state() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository
from desktop_app.database.models import Asset
from desktop_app.services.video_editing_service import VideoEditingService

repo = Repository()
service = VideoEditingService(repo)
project, sequence = service.create_project_with_sequence('Audio Flow')
asset = repo.add(Asset(filename='bed.mp3', asset_type='audio', file_path='C:/tmp/bed.mp3'))
service.append_assets_to_sequence(sequence.id, [asset.id])
clip = service.add_assets_to_timeline(sequence.id, [asset.id], track_type='audio', track_index=0)[0]
service.update_audio_clip(clip.id, volume=0.65, muted=True)
muted_volume = repo.get_by_id(type(clip), clip.id).volume
restored = service.update_audio_clip(clip.id, muted=False)
print(json.dumps({
    'track_type': restored.track_type,
    'muted_volume': muted_volume,
    'restored_volume': restored.volume,
    'meta_json': restored.meta_json,
}, ensure_ascii=False))
""")
    assert result['track_type'] == 'audio'
    assert float(result['muted_volume']) == 0.0
    assert float(result['restored_volume']) == 0.65
    assert 'audio_muted' in result['meta_json']


def test_delete_clip_removes_selected_timeline_block_and_reflows_following_clips() -> None:
    result = _run("""
import json
from desktop_app.database.repository import Repository
from desktop_app.database.models import Asset
from desktop_app.services.video_editing_service import VideoEditingService

repo = Repository()
service = VideoEditingService(repo)
project, sequence = service.create_project_with_sequence('Delete Clip Flow')
first = repo.add(Asset(filename='first.mp4', asset_type='video', file_path='C:/tmp/first.mp4'))
second = repo.add(Asset(filename='second.mp4', asset_type='video', file_path='C:/tmp/second.mp4'))
service.append_assets_to_sequence(sequence.id, [first.id, second.id])
service.add_assets_to_timeline(sequence.id, [first.id, second.id])
clips_before = service.list_clips(sequence.id)
deleted = service.delete_clip(clips_before[0].id)
clips_after = service.list_clips(sequence.id)
print(json.dumps({
    'deleted': deleted,
    'before': len(clips_before),
    'after': len(clips_after),
    'remaining_start_ms': clips_after[0].start_ms if clips_after else None,
    'remaining_asset_id': clips_after[0].asset_id if clips_after else None,
}, ensure_ascii=False))
""")
    assert result['deleted'] is True
    assert result['before'] == 2
    assert result['after'] == 1
    assert result['remaining_start_ms'] == 0


def test_bridge_can_delete_selected_video_clip() -> None:
    result = _run("""
import json
from desktop_app.database.models import Asset
from desktop_app.ui.bridge import Bridge

bridge = Bridge()
asset = bridge._repo.add(Asset(filename='delete-me.mp4', asset_type='video', file_path='C:/tmp/delete-me.mp4'))
bridge.appendAssetsToSequence(json.dumps({'asset_ids': [asset.id]}, ensure_ascii=False))
timeline_response = json.loads(bridge.addAssetsToTimeline(json.dumps({'asset_ids': [asset.id]}, ensure_ascii=False)))
clip_id = timeline_response['data']['clip_ids'][0]
delete_response = json.loads(bridge.deleteVideoClip(json.dumps({'clip_id': clip_id}, ensure_ascii=False)))
project = json.loads(bridge.listVideoProjects())['data'][0]
print(json.dumps({
    'delete_ok': delete_response['ok'],
    'deleted': delete_response['data']['deleted'],
    'clip_count': len(project.get('active_sequence_clips') or []),
}, ensure_ascii=False))
""")
    assert result['delete_ok'] is True
    assert result['deleted'] is True
    assert result['clip_count'] == 0


def test_bridge_can_update_selected_audio_clip_settings() -> None:
    result = _run("""
import json
from desktop_app.database.models import Asset
from desktop_app.ui.bridge import Bridge

bridge = Bridge()
asset = bridge._repo.add(Asset(filename='music.mp3', asset_type='audio', file_path='C:/tmp/music.mp3'))
bridge.appendAssetsToSequence(json.dumps({'asset_ids': [asset.id]}, ensure_ascii=False))
timeline_response = json.loads(bridge.addAssetsToTimeline(json.dumps({'asset_ids': [asset.id], 'track_type': 'audio', 'track_index': 0}, ensure_ascii=False)))
clip_id = timeline_response['data']['clip_ids'][0]
update_response = json.loads(bridge.updateVideoClipAudio(json.dumps({'clip_id': clip_id, 'volume': 0.45, 'muted': True}, ensure_ascii=False)))
project = json.loads(bridge.listVideoProjects())['data'][0]
clip = project.get('active_sequence_clips')[0]
print(json.dumps({
    'update_ok': update_response['ok'],
    'volume': update_response['data']['volume'],
    'clip_volume': clip['volume'],
    'meta_json': clip['meta_json'],
}, ensure_ascii=False))
""")
    assert result['update_ok'] is True
    assert float(result['volume']) == 0.0
    assert float(result['clip_volume']) == 0.0
    assert 'audio_muted' in result['meta_json']


def test_bridge_video_actions_import_library_then_add_clip_and_export_record() -> None:
    result = _run("""
import json
from desktop_app.database.models import Asset
from desktop_app.ui.bridge import Bridge

bridge = Bridge()
asset = bridge._repo.add(Asset(filename='video.mp4', asset_type='video', file_path=''))
append_response = json.loads(bridge.appendAssetsToSequence(json.dumps({'asset_ids': [asset.id]}, ensure_ascii=False)))
timeline_response = json.loads(bridge.addAssetsToTimeline(json.dumps({'asset_ids': [asset.id]}, ensure_ascii=False)))
projects_response = json.loads(bridge.listVideoProjects())
export_response = json.loads(bridge.createVideoExport(json.dumps({}, ensure_ascii=False)))
project = projects_response['data'][0]
print(json.dumps({
    'append_ok': append_response['ok'],
    'append_count': append_response['data']['count'],
    'timeline_ok': timeline_response['ok'],
    'timeline_count': timeline_response['data']['count'],
    'project_count': len(projects_response['data']),
    'clip_count': len(project.get('active_sequence_clips') or []),
    'asset_count': len(project.get('active_sequence_assets') or []),
    'export_ok': export_response['ok'],
    'export_status': export_response['data']['status'],
}, ensure_ascii=False))
""")
    assert result['append_ok'] is True
    assert result['append_count'] == 1
    assert result['timeline_ok'] is True
    assert result['timeline_count'] == 1
    assert result['project_count'] >= 1
    assert result['clip_count'] >= 1
    assert result['asset_count'] >= 1
    assert result['export_ok'] is True
    assert result['export_status'] == 'pending'


def test_bridge_can_remove_assets_from_current_video_sequence() -> None:
    result = _run("""
import json
from desktop_app.database.models import Asset
from desktop_app.ui.bridge import Bridge

bridge = Bridge()
asset = bridge._repo.add(Asset(filename='remove.mp4', asset_type='video', file_path=''))
append_response = json.loads(bridge.appendAssetsToSequence(json.dumps({'asset_ids': [asset.id]}, ensure_ascii=False)))
timeline_response = json.loads(bridge.addAssetsToTimeline(json.dumps({'asset_ids': [asset.id]}, ensure_ascii=False)))
remove_response = json.loads(bridge.removeAssetsFromSequence(json.dumps({'asset_ids': [asset.id]}, ensure_ascii=False)))
project = json.loads(bridge.listVideoProjects())['data'][0]
print(json.dumps({
    'append_ok': append_response['ok'],
    'timeline_ok': timeline_response['ok'],
    'remove_ok': remove_response['ok'],
    'removed': remove_response['data']['removed'],
    'clip_count': len(project.get('active_sequence_clips') or []),
    'asset_count': len(project.get('active_sequence_assets') or []),
}, ensure_ascii=False))
""")
    assert result['append_ok'] is True
    assert result['timeline_ok'] is True
    assert result['remove_ok'] is True
    assert result['removed'] == 1
    assert result['clip_count'] == 0
    assert result['asset_count'] == 0


def test_bridge_list_video_projects_normalizes_legacy_clip_assets() -> None:
    result = _run("""
import json
from desktop_app.database.models import Asset
from desktop_app.ui.bridge import Bridge

bridge = Bridge()
project = bridge._video_editing.create_project('Legacy Normalize')
sequence = bridge._video_editing.create_sequence(project.id, '主序列')
legacy_asset = bridge._repo.add(Asset(filename='legacy.mp4', asset_type='video', file_path='C:/tmp/legacy.mp4'))
canonical_asset = bridge._repo.add(Asset(filename='legacy.mp4', asset_type='video', file_path='C:/tmp/legacy.mp4'))
bridge._repo.add_video_sequence_asset(sequence.id, canonical_asset.id)
bridge._repo.append_video_clip(
    sequence.id,
    legacy_asset.id,
    track_type='video',
    track_index=0,
    start_ms=0,
    source_in_ms=0,
    source_out_ms=5000,
)

project_payload = next(item for item in json.loads(bridge.listVideoProjects())['data'] if item['name'] == 'Legacy Normalize')
clip = project_payload['active_sequence_clips'][0]
assets = project_payload['active_sequence_assets']
print(json.dumps({
    'clip_asset_id': clip['asset_id'],
    'clip_asset_filename': clip['asset_filename'],
    'asset_ids': [item['id'] for item in assets],
    'asset_filenames': [item['filename'] for item in assets],
}, ensure_ascii=False))
""")
    assert result['clip_asset_filename'] == 'legacy.mp4'
    assert result['clip_asset_id'] in result['asset_ids']
    assert result['asset_filenames'].count('legacy.mp4') == 1
