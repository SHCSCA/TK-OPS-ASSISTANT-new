"""Video editing service for TK-OPS."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from sqlalchemy import select

from desktop_app.database.models import (
    Asset,
    VideoClip,
    VideoExport,
    VideoProject,
    VideoSequence,
    VideoSequenceAsset,
    VideoSnapshot,
    VideoSubtitle,
)
from desktop_app.database.repository import Repository


class VideoEditingService:
    """Service layer for video editing operations."""

    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    # ── Project ──────────────────────────────────────────────────────

    def create_project(self, name: str, **kwargs) -> VideoProject:
        """创建视频项目。"""
        return self._repo.create_video_project(name=name, **kwargs)

    def get_project(self, project_id: int) -> VideoProject | None:
        return self._repo.get_video_project(project_id)

    def list_projects(self) -> Sequence[VideoProject]:
        return self._repo.list_video_projects()

    # ── Sequence ─────────────────────────────────────────────────────

    def create_sequence(
        self, project_id: int, name: str, **kwargs
    ) -> VideoSequence:
        """在项目中创建序列（时间线）。"""
        seq = self._repo.create_video_sequence(project_id, name=name, **kwargs)
        self._repo.set_active_video_sequence(project_id, seq.id)
        return seq

    def create_project_with_sequence(
        self, name: str, sequence_name: str = "主序列", **kwargs
    ) -> tuple[VideoProject, VideoSequence]:
        """同时创建项目与默认序列，返回 (project, sequence)。"""
        project = self.create_project(name, **kwargs)
        sequence = self.create_sequence(project.id, sequence_name)
        return project, sequence

    def list_sequences(self, project_id: int) -> Sequence[VideoSequence]:
        return self._repo.list_video_sequences(project_id)

    def list_subtitles(self, sequence_id: int) -> Sequence[VideoSubtitle]:
        return self._repo.list_video_subtitles(sequence_id)

    def create_subtitle(
        self, sequence_id: int, *, start_ms: int, end_ms: int, text: str
    ) -> VideoSubtitle:
        if end_ms <= start_ms:
            raise ValueError("字幕结束时间必须晚于开始时间")
        if not str(text or "").strip():
            raise ValueError("字幕内容不能为空")
        return self._repo.create_video_subtitle(
            sequence_id,
            start_ms=int(start_ms),
            end_ms=int(end_ms),
            text=str(text).strip(),
        )

    def update_subtitle(
        self,
        subtitle_id: int,
        *,
        start_ms: int,
        end_ms: int,
        text: str,
    ) -> VideoSubtitle:
        subtitle = self._repo.get_by_id(VideoSubtitle, subtitle_id)
        if subtitle is None:
            raise ValueError(f"字幕段不存在：id={subtitle_id}")
        if end_ms <= start_ms:
            raise ValueError("字幕结束时间必须晚于开始时间")
        if not str(text or "").strip():
            raise ValueError("字幕内容不能为空")
        return self._repo.update(
            subtitle,
            start_ms=int(start_ms),
            end_ms=int(end_ms),
            text=str(text).strip(),
        )

    def delete_subtitle(self, subtitle_id: int) -> bool:
        subtitle = self._repo.get_by_id(VideoSubtitle, subtitle_id)
        if subtitle is None:
            return False
        self._repo.delete(subtitle)
        return True

    def _default_clip_duration_ms(self, asset: Asset | None) -> int:
        asset_type = str(getattr(asset, "asset_type", "") or "").lower()
        if asset_type in {"image", "template"}:
            return 4000
        if asset_type in {"text", "subtitle"}:
            return 3000
        return 5000

    def _clip_track_type_for_asset(self, asset: Asset | None) -> str:
        asset_type = str(getattr(asset, "asset_type", "") or "").lower()
        return "audio" if asset_type == "audio" else "video"

    def _normalized_asset_path(self, file_path: str | None) -> str:
        return str(file_path or "").strip().replace("\\", "/").casefold()

    def normalize_sequence_clip_assets(self, sequence_id: int) -> dict[str, int]:
        """对齐历史 clip 与当前序列素材库，清理无效占位记录。"""
        session = self._repo.session
        library_rows = session.execute(
            select(VideoSequenceAsset)
            .where(VideoSequenceAsset.sequence_id == sequence_id)
            .order_by(VideoSequenceAsset.sort_order, VideoSequenceAsset.id)
        ).scalars().all()
        clips = session.execute(
            select(VideoClip)
            .where(VideoClip.sequence_id == sequence_id)
            .order_by(VideoClip.sort_order, VideoClip.id)
        ).scalars().all()

        library_asset_ids: set[int] = set()
        library_asset_by_path: dict[str, Asset] = {}
        changed = False
        imported = 0
        remapped = 0
        removed = 0

        for row in library_rows:
            asset = self._repo.get_by_id(Asset, row.asset_id)
            if asset is None:
                session.delete(row)
                changed = True
                continue
            asset_id = int(asset.id)
            library_asset_ids.add(asset_id)
            normalized_path = self._normalized_asset_path(asset.file_path)
            if normalized_path and normalized_path not in library_asset_by_path:
                library_asset_by_path[normalized_path] = asset

        for clip in clips:
            if clip.asset_id is None:
                session.delete(clip)
                removed += 1
                changed = True
                continue

            asset = self._repo.get_by_id(Asset, int(clip.asset_id))
            if asset is None:
                session.delete(clip)
                removed += 1
                changed = True
                continue

            asset_id = int(asset.id)
            if asset_id in library_asset_ids:
                continue

            normalized_path = self._normalized_asset_path(asset.file_path)
            canonical_asset = library_asset_by_path.get(normalized_path) if normalized_path else None
            if canonical_asset is not None and int(canonical_asset.id) != asset_id:
                clip.asset_id = int(canonical_asset.id)
                remapped += 1
                changed = True
                continue

            session.add(
                VideoSequenceAsset(
                    sequence_id=sequence_id,
                    asset_id=asset_id,
                    sort_order=len(library_asset_ids),
                )
            )
            library_asset_ids.add(asset_id)
            if normalized_path:
                library_asset_by_path[normalized_path] = asset
            imported += 1
            changed = True

        if not changed:
            return {"imported": 0, "remapped": 0, "removed": 0}

        session.flush()

        remaining_library_rows = session.execute(
            select(VideoSequenceAsset)
            .where(VideoSequenceAsset.sequence_id == sequence_id)
            .order_by(VideoSequenceAsset.sort_order, VideoSequenceAsset.id)
        ).scalars().all()
        for index, row in enumerate(remaining_library_rows):
            row.sort_order = index

        remaining_clips = session.execute(
            select(VideoClip)
            .where(VideoClip.sequence_id == sequence_id)
            .order_by(VideoClip.sort_order, VideoClip.id)
        ).scalars().all()
        for index, clip in enumerate(remaining_clips):
            clip.sort_order = index

        session.commit()
        self._reflow_sequence(sequence_id)
        return {"imported": imported, "remapped": remapped, "removed": removed}

    def _reflow_sequence(self, sequence_id: int) -> None:
        clips = list(self._repo.list_video_clips(sequence_id))
        if not clips:
            sequence = self._repo.get_by_id(VideoSequence, sequence_id)
            if sequence is not None:
                self._repo.update(sequence, duration_ms=0)
            return

        offsets: dict[tuple[str, int], int] = {}
        total_duration = 0
        session = self._repo.session
        for clip in clips:
            key = (str(clip.track_type or "video"), int(clip.track_index or 0))
            duration_ms = max(
                int(getattr(clip, "duration_ms", 0) or 0),
                int(getattr(clip, "source_out_ms", 0) or 0) - int(getattr(clip, "source_in_ms", 0) or 0),
                1000,
            )
            clip.duration_ms = duration_ms
            if int(getattr(clip, "source_out_ms", 0) or 0) <= int(getattr(clip, "source_in_ms", 0) or 0):
                clip.source_out_ms = int(getattr(clip, "source_in_ms", 0) or 0) + duration_ms
            clip.start_ms = offsets.get(key, 0)
            offsets[key] = clip.start_ms + duration_ms
            total_duration = max(total_duration, offsets[key])

        sequence = self._repo.get_by_id(VideoSequence, sequence_id)
        if sequence is not None:
            sequence.duration_ms = total_duration
        session.commit()

    # ── Clips ────────────────────────────────────────────────────────

    def append_assets_to_sequence(
        self, sequence_id: int, asset_ids: list[int]
    ) -> list[VideoSequenceAsset]:
        """将素材列表导入当前序列素材库，不自动加入时间线。"""
        imports: list[VideoSequenceAsset] = []
        for asset_id in asset_ids:
            asset_row = self._repo.add_video_sequence_asset(sequence_id, asset_id)
            imports.append(asset_row)
        return imports

    def add_assets_to_timeline(
        self,
        sequence_id: int,
        asset_ids: list[int],
        *,
        track_type: str | None = None,
        track_index: int = 0,
    ) -> list[VideoClip]:
        """将素材库中的素材拖入时间轴，生成真实片段。"""
        library_asset_ids = {
            int(item.asset_id)
            for item in self._repo.list_video_sequence_assets(sequence_id)
            if item.asset_id is not None
        }
        clips: list[VideoClip] = []
        for asset_id in asset_ids:
            normalized_asset_id = int(asset_id)
            if normalized_asset_id not in library_asset_ids:
                raise ValueError("请先将素材导入当前素材库，再拖拽到时间轴")
            asset = self._repo.get_by_id(Asset, normalized_asset_id)
            if asset is None:
                raise ValueError(f"素材不存在：id={normalized_asset_id}")
            resolved_track_type = str(track_type or self._clip_track_type_for_asset(asset) or "video").lower()
            if str(asset.asset_type or "").lower() == "audio" and resolved_track_type != "audio":
                raise ValueError("音频素材只能拖入音频轨")
            if str(asset.asset_type or "").lower() != "audio" and resolved_track_type == "audio":
                raise ValueError("当前素材只能拖入视频轨")
            duration_ms = self._default_clip_duration_ms(asset)
            clip = self._repo.append_video_clip(
                sequence_id,
                normalized_asset_id,
                track_type=resolved_track_type,
                track_index=track_index,
                start_ms=0,
                source_in_ms=0,
                source_out_ms=duration_ms,
            )
            clips.append(clip)
        self._reflow_sequence(sequence_id)
        return clips

    def reorder_clips(self, sequence_id: int, ordered_ids: list[int]) -> None:
        self._repo.reorder_video_clips(sequence_id, [int(clip_id) for clip_id in ordered_ids])
        self._reflow_sequence(sequence_id)

    def delete_clip(self, clip_id: int) -> bool:
        clip = self._repo.get_by_id(VideoClip, clip_id)
        if clip is None:
            return False
        sequence_id = int(clip.sequence_id)
        deleted = self._repo.delete_video_clip(clip_id)
        if not deleted:
            return False
        self._reflow_sequence(sequence_id)
        return True

    def update_clip_range(
        self, clip_id: int, *, source_in_ms: int, source_out_ms: int
    ) -> VideoClip:
        """更新片段的入出点，入点必须小于出点。"""
        if source_out_ms <= source_in_ms:
            raise ValueError(
                f"裁切范围无效：入点 {source_in_ms} ms 必须小于出点 {source_out_ms} ms"
            )
        clip = self._repo.get_by_id(VideoClip, clip_id)
        if clip is None:
            raise ValueError(f"片段不存在：id={clip_id}")
        duration_ms = source_out_ms - source_in_ms
        updated = self._repo.update(
            clip,
            source_in_ms=source_in_ms,
            source_out_ms=source_out_ms,
            duration_ms=duration_ms,
        )
        self._reflow_sequence(updated.sequence_id)
        return updated

    def update_audio_clip(
        self,
        clip_id: int,
        *,
        volume: float | None = None,
        muted: bool | None = None,
    ) -> VideoClip:
        """更新 A1 音频片段的基础音量状态。"""
        clip = self._repo.get_by_id(VideoClip, clip_id)
        if clip is None:
            raise ValueError(f"音频片段不存在：id={clip_id}")
        if str(clip.track_type or "").lower() != "audio":
            raise ValueError("当前片段不是音频轨片段")

        try:
            meta = json.loads(clip.meta_json or "{}")
        except json.JSONDecodeError:
            meta = {}
        if not isinstance(meta, dict):
            meta = {}

        current_volume = float(getattr(clip, "volume", 1.0) or 0.0)
        remembered_volume = float(meta.get("pre_mute_volume") or 0.0)
        if remembered_volume <= 0:
            remembered_volume = current_volume if current_volume > 0 else 1.0

        next_volume = current_volume
        if volume is not None:
            next_volume = max(0.0, min(float(volume), 2.0))
            if next_volume > 0:
                remembered_volume = next_volume

        if muted is True:
            meta["audio_muted"] = True
            meta["pre_mute_volume"] = round(max(remembered_volume, 0.05), 2)
            next_volume = 0.0
        elif muted is False:
            restored_volume = next_volume if next_volume > 0 else remembered_volume
            next_volume = max(0.0, min(restored_volume, 2.0))
            meta["audio_muted"] = False
            meta["pre_mute_volume"] = round(max(next_volume, 0.05), 2)
        else:
            meta["audio_muted"] = next_volume <= 0.0001
            if next_volume > 0:
                meta["pre_mute_volume"] = round(next_volume, 2)

        return self._repo.update(
            clip,
            volume=round(next_volume, 2),
            meta_json=json.dumps(meta, ensure_ascii=False),
        )

    def list_clips(self, sequence_id: int) -> Sequence[VideoClip]:
        return self._repo.list_video_clips(sequence_id)

    def list_sequence_assets(self, sequence_id: int) -> Sequence[Asset]:
        assets: list[Asset] = []
        for item in self._repo.list_video_sequence_assets(sequence_id):
            asset = self._repo.get_by_id(Asset, item.asset_id)
            if asset is None:
                continue
            assets.append(asset)
        return assets

    def remove_assets_from_sequence(self, sequence_id: int, asset_ids: list[int]) -> int:
        """从当前序列移除素材，同时清理对应时间轴片段，保留素材中心原始记录。"""
        normalized_ids = {int(asset_id) for asset_id in asset_ids if asset_id not in (None, "")}
        if not normalized_ids:
            return 0

        session = self._repo.session
        library_rows = session.execute(
            select(VideoSequenceAsset)
            .where(VideoSequenceAsset.sequence_id == sequence_id)
            .where(VideoSequenceAsset.asset_id.in_(normalized_ids))
            .order_by(VideoSequenceAsset.sort_order, VideoSequenceAsset.id)
        ).scalars().all()
        clips = session.execute(
            select(VideoClip)
            .where(VideoClip.sequence_id == sequence_id)
            .where(VideoClip.asset_id.in_(normalized_ids))
            .order_by(VideoClip.sort_order, VideoClip.id)
        ).scalars().all()
        if not clips and not library_rows:
            return 0

        removed = len(library_rows)
        for row in library_rows:
            session.delete(row)
        for clip in clips:
            session.delete(clip)
        session.flush()

        remaining_assets = session.execute(
            select(VideoSequenceAsset)
            .where(VideoSequenceAsset.sequence_id == sequence_id)
            .order_by(VideoSequenceAsset.sort_order, VideoSequenceAsset.id)
        ).scalars().all()
        for index, row in enumerate(remaining_assets):
            row.sort_order = index

        remaining = session.execute(
            select(VideoClip)
            .where(VideoClip.sequence_id == sequence_id)
            .order_by(VideoClip.sort_order, VideoClip.id)
        ).scalars().all()
        for index, clip in enumerate(remaining):
            clip.sort_order = index
        session.commit()
        self._reflow_sequence(sequence_id)
        return removed

    # ── Export validation ────────────────────────────────────────────

    def validate_export(
        self, project_id: int, sequence_id: int
    ) -> dict:
        """校验导出前的条件，返回 {ok, errors} 字典。"""
        errors: list[str] = []

        project = self._repo.get_video_project(project_id)
        if project is None:
            errors.append(f"项目不存在：id={project_id}")
            return {"ok": False, "errors": errors}

        clips = self._repo.list_video_clips(sequence_id)
        sequence_assets = self.list_sequence_assets(sequence_id)
        if not clips:
            errors.append("序列为空，至少需要一个片段才能导出")

        assets_to_validate: dict[int, Asset] = {}
        for asset in sequence_assets:
            if asset is None or asset.id is None:
                continue
            assets_to_validate[int(asset.id)] = asset

        for clip in clips:
            if clip.asset_id is None or int(clip.asset_id) in assets_to_validate:
                continue
            asset = self._repo.get_by_id(Asset, clip.asset_id)
            if asset is None:
                errors.append(f"片段 id={clip.id} 引用的素材 id={clip.asset_id} 不存在")
                continue
            assets_to_validate[int(asset.id)] = asset

        for asset in assets_to_validate.values():
            file_path = getattr(asset, "file_path", None) or ""
            if file_path and not Path(file_path).exists():
                errors.append(
                    f"素材 '{asset.filename}' 的源文件不存在：{file_path}"
                )

        return {"ok": len(errors) == 0, "errors": errors}

    # ── Snapshot ─────────────────────────────────────────────────────

    def create_snapshot(self, project_id: int, title: str) -> VideoSnapshot:
        """保存项目当前状态快照。"""
        project = self._repo.get_video_project(project_id)
        if project is None:
            raise ValueError(f"项目不存在：id={project_id}")

        sequences = self._repo.list_video_sequences(project_id)
        payload: dict = {
            "project_id": project_id,
            "project_name": project.name,
            "sequences": [],
        }
        for seq in sequences:
            clips = self._repo.list_video_clips(seq.id)
            payload["sequences"].append({
                "id": seq.id,
                "name": seq.name,
                "clip_count": len(clips),
            })

        return self._repo.create_video_snapshot(
            project_id,
            title=title,
            payload_json=json.dumps(payload, ensure_ascii=False),
        )

    def list_snapshots(self, project_id: int) -> Sequence[VideoSnapshot]:
        return self._repo.list_video_snapshots(project_id)

    # ── Export record ────────────────────────────────────────────────

    def create_export_record(
        self,
        project_id: int,
        sequence_id: int | None = None,
        *,
        preset: str = "mp4_1080p",
        output_path: str | None = None,
    ) -> VideoExport:
        """创建导出记录（不实际执行导出）。"""
        return self._repo.create_video_export(
            project_id=project_id,
            sequence_id=sequence_id,
            preset=preset,
            output_path=output_path,
        )

    def list_exports(self, project_id: int) -> Sequence[VideoExport]:
        return self._repo.list_video_exports(project_id)
