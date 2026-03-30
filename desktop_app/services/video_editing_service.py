"""Video editing service with basic project, timeline, subtitle, and export validation flows."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from desktop_app.database.models import Asset, VideoClip, VideoProject, VideoSequence, VideoSnapshot, VideoSubtitle
from desktop_app.database.repository import Repository


class VideoEditingService:
    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    def create_project(self, name: str, **fields: Any) -> VideoProject:
        return self._repo.create_video_project(name=name, **fields)

    def create_sequence(self, project_id: int, name: str, **fields: Any) -> VideoSequence:
        return self._repo.create_video_sequence(project_id, name=name, **fields)

    def create_project_with_sequence(self, name: str) -> tuple[VideoProject, VideoSequence]:
        project = self.create_project(name)
        sequence = self.create_sequence(project.id, "主序列")
        return project, sequence

    def append_assets_to_sequence(self, sequence_id: int, asset_ids: list[int]) -> list[VideoClip]:
        created: list[VideoClip] = []
        start_ms = self._sequence_end_ms(sequence_id)
        for asset_id in asset_ids:
            asset = self._require_asset(asset_id)
            duration_ms = self._default_asset_duration_ms(asset)
            clip = self._repo.append_video_clip(
                sequence_id,
                asset.id,
                track_type=self._asset_track_type(asset),
                track_index=0,
                start_ms=start_ms,
                source_in_ms=0,
                source_out_ms=duration_ms,
                duration_ms=duration_ms,
            )
            created.append(clip)
            start_ms += duration_ms
        return created

    def update_clip_range(self, clip_id: int, *, source_in_ms: int, source_out_ms: int) -> VideoClip:
        clip = self._require_clip(clip_id)
        source_in_ms = int(source_in_ms)
        source_out_ms = int(source_out_ms)
        if source_in_ms >= source_out_ms:
            raise ValueError("裁切区间无效：起点必须小于终点")
        source_limit = max(int(clip.source_out_ms or 0), int(clip.duration_ms or 0))
        if source_limit and source_out_ms > source_limit:
            raise ValueError("裁切区间不能超过素材长度")
        updated = self._repo.update(
            clip,
            source_in_ms=source_in_ms,
            source_out_ms=source_out_ms,
            duration_ms=source_out_ms - source_in_ms,
        )
        self._repo._refresh_video_sequence_duration(updated.sequence_id)
        refreshed = self._repo.get_by_id(VideoClip, updated.id)
        return refreshed or updated

    def delete_clip(self, clip_id: int) -> bool:
        clip = self._require_clip(clip_id)
        sequence_id = int(clip.sequence_id)
        self._repo.delete(clip)
        self._repo._refresh_video_sequence_duration(sequence_id)
        return True

    def move_clip(self, sequence_id: int, clip_id: int, direction: str) -> list[VideoClip]:
        clips = list(self._repo.list_video_clips(sequence_id))
        ids = [int(clip.id) for clip in clips]
        if int(clip_id) not in ids:
            raise ValueError("片段不存在")
        current_index = ids.index(int(clip_id))
        normalized = str(direction or "").strip().lower()
        if normalized == "left" and current_index > 0:
            swap_index = current_index - 1
        elif normalized == "right" and current_index < len(ids) - 1:
            swap_index = current_index + 1
        else:
            return clips
        ids[current_index], ids[swap_index] = ids[swap_index], ids[current_index]
        return list(self._repo.reorder_video_clips(sequence_id, ids))

    def create_subtitle(
        self,
        sequence_id: int,
        *,
        start_ms: int,
        end_ms: int,
        text: str,
        **fields: Any,
    ) -> VideoSubtitle:
        self._validate_subtitle_window(sequence_id, int(start_ms), int(end_ms))
        return self._repo.create_video_subtitle(
            sequence_id,
            start_ms=int(start_ms),
            end_ms=int(end_ms),
            text=text,
            **fields,
        )

    def update_subtitle(self, subtitle_id: int, **fields: Any) -> VideoSubtitle:
        subtitle = self._require_subtitle(subtitle_id)
        start_ms = int(fields.get("start_ms", subtitle.start_ms))
        end_ms = int(fields.get("end_ms", subtitle.end_ms))
        self._validate_subtitle_window(subtitle.sequence_id, start_ms, end_ms, exclude_id=subtitle.id)
        updated = self._repo.update(subtitle, **fields)
        refreshed = self._repo.get_by_id(VideoSubtitle, updated.id)
        return refreshed or updated

    def delete_subtitle(self, subtitle_id: int) -> bool:
        subtitle = self._require_subtitle(subtitle_id)
        self._repo.delete(subtitle)
        return True

    def create_snapshot(self, project_id: int, title: str) -> VideoSnapshot:
        payload = self._snapshot_payload(project_id)
        snapshot = self._repo.add(
            VideoSnapshot(
                project_id=project_id,
                title=title,
                snapshot_json=json.dumps(payload, ensure_ascii=False),
            )
        )
        refreshed = self._repo.get_by_id(VideoSnapshot, snapshot.id)
        return refreshed or snapshot

    def restore_snapshot(self, snapshot_id: int) -> VideoProject:
        snapshot = self._repo.get_by_id(VideoSnapshot, snapshot_id)
        if snapshot is None:
            raise ValueError("快照不存在")
        payload = self._load_snapshot(snapshot.snapshot_json)
        project = self._repo.get_video_project(int(snapshot.project_id))
        if project is None:
            raise ValueError("工程不存在")

        for sequence in list(self._repo.list_video_sequences(project.id)):
            self._repo.delete(sequence)

        for sequence_payload in payload.get("sequences", []):
            sequence = self._repo.create_video_sequence(
                project.id,
                name=str(sequence_payload.get("name") or "主序列"),
                duration_ms=int(sequence_payload.get("duration_ms") or 0),
                sort_order=int(sequence_payload.get("sort_order") or 0),
                is_active=bool(sequence_payload.get("is_active")),
            )
            clip_payloads = sequence_payload.get("clips", [])
            if clip_payloads:
                for clip_payload in clip_payloads:
                    if clip_payload.get("asset_id") is None:
                        self._repo.create_video_clip_placeholder(
                            sequence.id,
                            track_type=str(clip_payload.get("track_type") or "video"),
                            track_index=int(clip_payload.get("track_index") or 0),
                            duration_ms=int(clip_payload.get("duration_ms") or 0),
                        )
                    else:
                        self._repo.append_video_clip(
                            sequence.id,
                            int(clip_payload["asset_id"]),
                            track_type=str(clip_payload.get("track_type") or "video"),
                            track_index=int(clip_payload.get("track_index") or 0),
                            start_ms=int(clip_payload.get("start_ms") or 0),
                            source_in_ms=int(clip_payload.get("source_in_ms") or 0),
                            source_out_ms=int(clip_payload.get("source_out_ms") or 0),
                            duration_ms=int(clip_payload.get("duration_ms") or 0),
                        )
            for subtitle_payload in sequence_payload.get("subtitles", []):
                self._repo.create_video_subtitle(
                    sequence.id,
                    start_ms=int(subtitle_payload.get("start_ms") or 0),
                    end_ms=int(subtitle_payload.get("end_ms") or 0),
                    text=str(subtitle_payload.get("text") or ""),
                    style_json=str(subtitle_payload.get("style_json") or "{}"),
                    sort_order=int(subtitle_payload.get("sort_order") or 0),
                )

        refreshed = self._repo.get_video_project(project.id)
        return refreshed or project

    def validate_export(self, project_id: int, sequence_id: int) -> dict[str, object]:
        errors: list[str] = []
        project = self._repo.get_video_project(int(project_id))
        if project is None:
            return {"ok": False, "errors": ["工程不存在"]}
        sequence = self._repo.get_by_id(VideoSequence, int(sequence_id))
        if sequence is None or int(sequence.project_id) != int(project.id):
            return {"ok": False, "errors": ["序列不存在"]}

        clips = list(self._repo.list_video_clips(sequence.id))
        if not clips:
            errors.append("当前序列为空，不能导出")

        for clip in clips:
            if clip.asset_id is None:
                errors.append("片段缺少素材，不能导出")
                continue
            asset = self._repo.get_by_id(Asset, int(clip.asset_id))
            if asset is None:
                errors.append(f"素材不存在: {clip.asset_id}")
                continue
            if not self._path_exists(asset.file_path):
                errors.append(f"素材源文件不存在: {asset.file_path}")

        for subtitle in self._repo.list_video_subtitles(sequence.id):
            if int(subtitle.start_ms) >= int(subtitle.end_ms):
                errors.append("字幕时间重叠或越界")
                break
        subtitles = list(self._repo.list_video_subtitles(sequence.id))
        for previous, current in zip(subtitles, subtitles[1:]):
            if int(current.start_ms) < int(previous.end_ms):
                errors.append("字幕时间重叠或越界")
                break
        if int(sequence.duration_ms or 0) > 0:
            for subtitle in subtitles:
                if int(subtitle.end_ms) > int(sequence.duration_ms):
                    errors.append("字幕时间重叠或越界")
                    break

        return {"ok": not errors, "errors": errors}

    def _require_asset(self, asset_id: int) -> Asset:
        asset = self._repo.get_by_id(Asset, int(asset_id))
        if asset is None:
            raise ValueError("素材不存在")
        return asset

    def _require_clip(self, clip_id: int) -> VideoClip:
        clip = self._repo.get_by_id(VideoClip, int(clip_id))
        if clip is None:
            raise ValueError("片段不存在")
        return clip

    def _require_subtitle(self, subtitle_id: int) -> VideoSubtitle:
        subtitle = self._repo.get_by_id(VideoSubtitle, int(subtitle_id))
        if subtitle is None:
            raise ValueError("字幕不存在")
        return subtitle

    def _sequence_end_ms(self, sequence_id: int) -> int:
        clips = list(self._repo.list_video_clips(sequence_id))
        if not clips:
            return 0
        return max(int(clip.start_ms or 0) + int(clip.duration_ms or 0) for clip in clips)

    @staticmethod
    def _asset_track_type(asset: Asset) -> str:
        asset_type = str(asset.asset_type or "").lower()
        return "audio" if asset_type == "audio" else "video"

    @staticmethod
    def _default_asset_duration_ms(asset: Asset) -> int:
        asset_type = str(asset.asset_type or "").lower()
        return 1000 if asset_type in {"video", "audio"} else 0

    @staticmethod
    def _path_exists(file_path: str | None) -> bool:
        text = str(file_path or "").strip()
        return bool(text) and Path(text).expanduser().is_file()

    def _validate_subtitle_window(
        self,
        sequence_id: int,
        start_ms: int,
        end_ms: int,
        *,
        exclude_id: int | None = None,
    ) -> None:
        if start_ms >= end_ms:
            raise ValueError("字幕时间重叠或越界")
        sequence = self._repo.get_by_id(VideoSequence, int(sequence_id))
        if sequence is not None and int(sequence.duration_ms or 0) > 0 and end_ms > int(sequence.duration_ms):
            raise ValueError("字幕时间重叠或越界")
        for subtitle in self._repo.list_video_subtitles(sequence_id):
            if exclude_id is not None and int(subtitle.id) == int(exclude_id):
                continue
            if start_ms < int(subtitle.end_ms) and end_ms > int(subtitle.start_ms):
                raise ValueError("字幕时间重叠或越界")

    def _snapshot_payload(self, project_id: int) -> dict[str, object]:
        sequences_payload: list[dict[str, object]] = []
        for sequence in self._repo.list_video_sequences(project_id):
            sequences_payload.append(
                {
                    "name": sequence.name,
                    "duration_ms": int(sequence.duration_ms or 0),
                    "sort_order": int(sequence.sort_order or 0),
                    "is_active": bool(sequence.is_active),
                    "clips": [
                        {
                            "asset_id": clip.asset_id,
                            "track_type": clip.track_type,
                            "track_index": int(clip.track_index or 0),
                            "start_ms": int(clip.start_ms or 0),
                            "source_in_ms": int(clip.source_in_ms or 0),
                            "source_out_ms": int(clip.source_out_ms or 0),
                            "duration_ms": int(clip.duration_ms or 0),
                            "sort_order": int(clip.sort_order or 0),
                        }
                        for clip in self._repo.list_video_clips(sequence.id)
                    ],
                    "subtitles": [
                        {
                            "start_ms": int(subtitle.start_ms or 0),
                            "end_ms": int(subtitle.end_ms or 0),
                            "text": subtitle.text,
                            "style_json": subtitle.style_json,
                            "sort_order": int(subtitle.sort_order or 0),
                        }
                        for subtitle in self._repo.list_video_subtitles(sequence.id)
                    ],
                }
            )
        return {"project_id": int(project_id), "sequences": sequences_payload}

    @staticmethod
    def _load_snapshot(raw: str | None) -> dict[str, Any]:
        if not raw:
            return {}
        try:
            data = json.loads(raw)
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}
