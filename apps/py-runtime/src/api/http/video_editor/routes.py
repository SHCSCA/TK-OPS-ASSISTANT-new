from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from api.http.common.envelope import err, ok
from bootstrap.container import RuntimeContainer
from desktop_app.database.models import VideoClip, VideoExport, VideoSubtitle
from desktop_app.database.repository import Repository
from desktop_app.services.video_editing_service import VideoEditingService
from desktop_app.services.video_export_service import VideoExportService
from legacy_adapter.serializers import (
    serialize_video_clip,
    serialize_video_export,
    serialize_video_project,
    serialize_video_sequence,
    serialize_video_snapshot,
    serialize_video_subtitle,
)


class CreateVideoProjectPayload(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None)
    meta_json: str | None = Field(default=None, alias='metaJson')

    model_config = {'populate_by_name': True}


class CreateVideoSequencePayload(BaseModel):
    project_id: int = Field(alias='projectId', gt=0)
    name: str = Field(min_length=1, max_length=200)
    fps: float | None = Field(default=None, ge=1)
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)
    meta_json: str | None = Field(default=None, alias='metaJson')

    model_config = {'populate_by_name': True}


class ActivateVideoSequencePayload(BaseModel):
    project_id: int = Field(alias='projectId', gt=0)
    sequence_id: int = Field(alias='sequenceId', gt=0)

    model_config = {'populate_by_name': True}


class AppendAssetsToSequencePayload(BaseModel):
    asset_ids: list[int] = Field(default_factory=list, alias='assetIds')
    asset_id: int | None = Field(default=None, alias='assetId', gt=0)

    model_config = {'populate_by_name': True}


class ReorderVideoClipsPayload(BaseModel):
    sequence_id: int = Field(alias='sequenceId', gt=0)
    clip_ids: list[int] = Field(alias='clipIds', min_length=1)

    model_config = {'populate_by_name': True}


class UpdateVideoClipPayload(BaseModel):
    source_in_ms: int | None = Field(default=None, alias='sourceInMs', ge=0)
    source_out_ms: int | None = Field(default=None, alias='sourceOutMs', ge=0)
    volume: float | None = Field(default=None, ge=0)
    speed: float | None = Field(default=None, gt=0)

    model_config = {'populate_by_name': True}


class TrimVideoClipPayload(BaseModel):
    clip_id: int = Field(alias='clipId', gt=0)
    source_in_ms: int = Field(alias='sourceInMs', ge=0)
    source_out_ms: int = Field(alias='sourceOutMs', ge=0)

    model_config = {'populate_by_name': True}


class CreateVideoSubtitlePayload(BaseModel):
    sequence_id: int = Field(alias='sequenceId', gt=0)
    start_ms: int = Field(alias='startMs', ge=0)
    end_ms: int = Field(alias='endMs', ge=0)
    text: str = Field(min_length=1)
    style_json: str | None = Field(default=None, alias='styleJson')

    model_config = {'populate_by_name': True}


class UpdateVideoSubtitlePayload(BaseModel):
    start_ms: int | None = Field(default=None, alias='startMs', ge=0)
    end_ms: int | None = Field(default=None, alias='endMs', ge=0)
    text: str | None = Field(default=None)
    style_json: str | None = Field(default=None, alias='styleJson')

    model_config = {'populate_by_name': True}


class CreateVideoExportPayload(BaseModel):
    project_id: int = Field(alias='projectId', gt=0)
    sequence_id: int = Field(alias='sequenceId', gt=0)
    preset: str = Field(default='final', min_length=1, max_length=80)

    model_config = {'populate_by_name': True}


class CreateVideoSnapshotPayload(BaseModel):
    project_id: int = Field(alias='projectId', gt=0)
    title: str = Field(min_length=1, max_length=200)

    model_config = {'populate_by_name': True}


def build_video_editor_router(container: RuntimeContainer) -> APIRouter:
    _ = container
    router = APIRouter(prefix='/video-editor', tags=['video-editor'])

    @router.get('/projects')
    def list_video_projects() -> dict[str, object]:
        repo = Repository()
        try:
            items = [serialize_video_project(item) for item in repo.list_video_projects()]
            return ok({'items': items, 'total': len(items)})
        finally:
            repo.reset_session()

    @router.post('/projects')
    def create_video_project(payload: CreateVideoProjectPayload):
        repo = Repository()
        try:
            service = VideoEditingService(repo)
            item = service.create_project(
                payload.name.strip(),
                description=payload.description,
                meta_json=payload.meta_json or '{}',
            )
            return ok(serialize_video_project(item))
        finally:
            repo.reset_session()

    @router.get('/projects/{project_id}/sequences')
    def list_video_sequences(project_id: int) -> dict[str, object]:
        repo = Repository()
        try:
            items = [serialize_video_sequence(item) for item in repo.list_video_sequences(int(project_id))]
            return ok({'items': items, 'total': len(items)})
        finally:
            repo.reset_session()

    @router.post('/sequences')
    def create_video_sequence(payload: CreateVideoSequencePayload):
        repo = Repository()
        try:
            service = VideoEditingService(repo)
            item = service.create_sequence(
                payload.project_id,
                payload.name.strip(),
                fps=payload.fps if payload.fps is not None else 30.0,
                width=payload.width if payload.width is not None else 1920,
                height=payload.height if payload.height is not None else 1080,
                meta_json=payload.meta_json or '{}',
            )
            return ok(serialize_video_sequence(item))
        finally:
            repo.reset_session()

    @router.post('/sequences/activate')
    def activate_video_sequence(payload: ActivateVideoSequencePayload):
        repo = Repository()
        try:
            item = repo.set_active_video_sequence(payload.project_id, payload.sequence_id)
            return ok(serialize_video_sequence(item))
        finally:
            repo.reset_session()

    @router.get('/sequences/{sequence_id}/clips')
    def list_video_clips(sequence_id: int) -> dict[str, object]:
        repo = Repository()
        try:
            items = [serialize_video_clip(item) for item in repo.list_video_clips(int(sequence_id))]
            return ok({'items': items, 'total': len(items)})
        finally:
            repo.reset_session()

    @router.post('/sequences/{sequence_id}/assets')
    def append_assets_to_sequence(sequence_id: int, payload: AppendAssetsToSequencePayload):
        repo = Repository()
        try:
            service = VideoEditingService(repo)
            asset_ids = [int(asset_id) for asset_id in payload.asset_ids if int(asset_id) > 0]
            if payload.asset_id is not None:
                asset_ids.append(int(payload.asset_id))
            asset_ids = list(dict.fromkeys(asset_ids))
            if not asset_ids:
                return err('video_editor.asset_ids_required', '请先选择至少一个素材')
            items = [serialize_video_clip(item) for item in service.append_assets_to_sequence(int(sequence_id), asset_ids)]
            return ok({'items': items, 'total': len(items)})
        except ValueError as exc:
            return err('video_editor.append_assets_failed', str(exc))
        finally:
            repo.reset_session()

    @router.post('/clips/reorder')
    def reorder_video_clips(payload: ReorderVideoClipsPayload):
        repo = Repository()
        try:
            items = [serialize_video_clip(item) for item in repo.reorder_video_clips(payload.sequence_id, payload.clip_ids)]
            return ok({'items': items, 'total': len(items)})
        except ValueError as exc:
            return err('video_editor.reorder_failed', str(exc))
        finally:
            repo.reset_session()

    @router.put('/clips/{clip_id}')
    def update_video_clip(clip_id: int, payload: UpdateVideoClipPayload):
        repo = Repository()
        try:
            clip = repo.get_by_id(VideoClip, int(clip_id))
            if clip is None:
                return err('video_editor.clip_not_found', '时间轴片段不存在')
            updates: dict[str, object] = {}
            if payload.source_in_ms is not None:
                updates['source_in_ms'] = payload.source_in_ms
            if payload.source_out_ms is not None:
                updates['source_out_ms'] = payload.source_out_ms
            if payload.volume is not None:
                updates['volume'] = payload.volume
            if payload.speed is not None:
                updates['speed'] = payload.speed
            if not updates:
                return ok(serialize_video_clip(clip))
            updated = repo.update(clip, **updates)
            return ok(serialize_video_clip(updated))
        finally:
            repo.reset_session()

    @router.post('/clips/trim')
    def trim_video_clip(payload: TrimVideoClipPayload):
        repo = Repository()
        try:
            service = VideoEditingService(repo)
            clip = service.update_clip_range(
                payload.clip_id,
                source_in_ms=payload.source_in_ms,
                source_out_ms=payload.source_out_ms,
            )
            return ok(serialize_video_clip(clip))
        except ValueError as exc:
            return err('video_editor.trim_failed', str(exc))
        finally:
            repo.reset_session()

    @router.delete('/clips/{clip_id}')
    def delete_video_clip(clip_id: int):
        repo = Repository()
        try:
            service = VideoEditingService(repo)
            deleted = service.delete_clip(int(clip_id))
            return ok({'deleted': deleted, 'clipId': int(clip_id)})
        except ValueError as exc:
            return err('video_editor.delete_clip_failed', str(exc))
        finally:
            repo.reset_session()

    @router.get('/sequences/{sequence_id}/subtitles')
    def list_video_subtitles(sequence_id: int) -> dict[str, object]:
        repo = Repository()
        try:
            items = [serialize_video_subtitle(item) for item in repo.list_video_subtitles(int(sequence_id))]
            return ok({'items': items, 'total': len(items)})
        finally:
            repo.reset_session()

    @router.post('/subtitles')
    def create_video_subtitle(payload: CreateVideoSubtitlePayload):
        repo = Repository()
        try:
            service = VideoEditingService(repo)
            item = service.create_subtitle(
                payload.sequence_id,
                start_ms=payload.start_ms,
                end_ms=payload.end_ms,
                text=payload.text.strip(),
                style_json=payload.style_json or '{}',
            )
            return ok(serialize_video_subtitle(item))
        except ValueError as exc:
            return err('video_editor.create_subtitle_failed', str(exc))
        finally:
            repo.reset_session()

    @router.put('/subtitles/{subtitle_id}')
    def update_video_subtitle(subtitle_id: int, payload: UpdateVideoSubtitlePayload):
        repo = Repository()
        try:
            service = VideoEditingService(repo)
            fields: dict[str, object] = {}
            if payload.start_ms is not None:
                fields['start_ms'] = payload.start_ms
            if payload.end_ms is not None:
                fields['end_ms'] = payload.end_ms
            if payload.text is not None:
                fields['text'] = payload.text.strip()
            if payload.style_json is not None:
                fields['style_json'] = payload.style_json
            item = service.update_subtitle(int(subtitle_id), **fields)
            return ok(serialize_video_subtitle(item))
        except ValueError as exc:
            return err('video_editor.update_subtitle_failed', str(exc))
        finally:
            repo.reset_session()

    @router.delete('/subtitles/{subtitle_id}')
    def delete_video_subtitle(subtitle_id: int):
        repo = Repository()
        try:
            service = VideoEditingService(repo)
            deleted = service.delete_subtitle(int(subtitle_id))
            return ok({'deleted': deleted, 'subtitleId': int(subtitle_id)})
        except ValueError as exc:
            return err('video_editor.delete_subtitle_failed', str(exc))
        finally:
            repo.reset_session()

    @router.get('/projects/{project_id}/exports')
    def list_video_exports(project_id: int) -> dict[str, object]:
        repo = Repository()
        try:
            items = [serialize_video_export(item) for item in repo.list_video_exports(int(project_id))]
            return ok({'items': items, 'total': len(items)})
        finally:
            repo.reset_session()

    @router.post('/exports')
    def create_video_export(payload: CreateVideoExportPayload):
        repo = Repository()
        try:
            service = VideoExportService(repo)
            result = service.validate_and_create_export(
                payload.project_id,
                payload.sequence_id,
                preset=payload.preset,
            )
            if not result.get('ok'):
                return err('video_editor.export_invalid', str(result.get('error') or '当前序列暂不可导出'))
            export_id = int(result['export_id'])
            export = repo.get_by_id(VideoExport, export_id)
            if export is None:
                return err('video_editor.export_not_found', '导出任务创建后未找到记录')
            return ok(serialize_video_export(export))
        finally:
            repo.reset_session()

    @router.post('/exports/{export_id}/run')
    def run_video_export(export_id: int):
        repo = Repository()
        try:
            service = VideoExportService(repo)
            item = service.run_export(int(export_id))
            return ok(serialize_video_export(item))
        except ValueError as exc:
            return err('video_editor.run_export_failed', str(exc))
        finally:
            repo.reset_session()

    @router.get('/projects/{project_id}/snapshots')
    def list_video_snapshots(project_id: int) -> dict[str, object]:
        repo = Repository()
        try:
            items = [serialize_video_snapshot(item) for item in repo.list_video_snapshots(int(project_id))]
            return ok({'items': items, 'total': len(items)})
        finally:
            repo.reset_session()

    @router.post('/snapshots')
    def create_video_snapshot(payload: CreateVideoSnapshotPayload):
        repo = Repository()
        try:
            service = VideoEditingService(repo)
            item = service.create_snapshot(payload.project_id, payload.title.strip())
            return ok(serialize_video_snapshot(item))
        except ValueError as exc:
            return err('video_editor.create_snapshot_failed', str(exc))
        finally:
            repo.reset_session()

    @router.post('/snapshots/{snapshot_id}/restore')
    def restore_video_snapshot(snapshot_id: int):
        repo = Repository()
        try:
            service = VideoEditingService(repo)
            item = service.restore_snapshot(int(snapshot_id))
            return ok(serialize_video_project(item))
        except ValueError as exc:
            return err('video_editor.restore_snapshot_failed', str(exc))
        finally:
            repo.reset_session()

    return router