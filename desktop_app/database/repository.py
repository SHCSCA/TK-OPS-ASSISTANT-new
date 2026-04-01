"""Generic CRUD repository for TK-OPS models."""
from __future__ import annotations

import datetime as dt
import threading

from typing import Any, Sequence, Type, TypeVar

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from desktop_app.database import get_session
from desktop_app.database.models import (
    Account,
    AIProvider,
    ActivityLog,
    AnalysisSnapshot,
    AppSetting,
    Asset,
    Base,
    Device,
    ExperimentProject,
    ExperimentView,
    Group,
    ReportRun,
    Task,
    VideoClip,
    VideoProject,
    VideoSequence,
    VideoSnapshot,
    VideoSubtitle,
    VideoExport,
    WorkflowDefinition,
    WorkflowRun,
)

T = TypeVar("T", bound=Base)


class Repository:
    """Thin wrapper around SQLAlchemy Session providing common CRUD ops."""

    def __init__(self, session: Session | None = None) -> None:
        self._owns_session = session is None
        self._session_lock = threading.Lock()
        self._session = session
        if self._session is not None:
            self._session.expire_on_commit = False

    @property
    def session(self) -> Session:
        if self._session is not None:
            return self._session
        if not self._owns_session:
            raise RuntimeError("Repository requires an explicit session")
        with self._session_lock:
            if self._session is None:
                self._session = get_session()
                self._session.expire_on_commit = False
        return self._session

    def reset_session(self) -> None:
        if not self._owns_session:
            return
        if self._session is None:
            return
        self._session.close()
        self._session = None

    # 鈹€鈹€ generic CRUD 鈹€鈹€

    def get_by_id(self, model: Type[T], pk: Any) -> T | None:
        return self.session.get(model, pk)

    def list_all(self, model: Type[T], *, limit: int = 500) -> Sequence[T]:
        return self.session.execute(select(model).limit(limit)).scalars().all()

    def count(self, model: Type[T]) -> int:
        return self.session.execute(select(func.count()).select_from(model)).scalar() or 0

    def add(self, instance: T) -> T:
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def update(self, instance: T, **fields: Any) -> T:
        for k, v in fields.items():
            setattr(instance, k, v)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def delete(self, instance: T) -> None:
        self.session.delete(instance)
        self.session.commit()
        self.session.expire_all()

    # 鈹€鈹€ specialized queries 鈹€鈹€

    def list_accounts(self, *, status: str | None = None) -> Sequence[Account]:
        stmt = select(Account)
        if status:
            stmt = stmt.where(Account.status == status)
        return self.session.execute(stmt.order_by(Account.id)).scalars().all()

    def list_devices(self, *, status: str | None = None) -> Sequence[Device]:
        stmt = select(Device)
        if status:
            stmt = stmt.where(Device.status == status)
        return self.session.execute(stmt.order_by(Device.id)).scalars().all()

    def list_tasks(self, *, status: str | None = None) -> Sequence[Task]:
        stmt = select(Task)
        if status:
            stmt = stmt.where(Task.status == status)
        return self.session.execute(stmt.order_by(Task.created_at.desc())).scalars().all()

    def get_active_provider(self) -> AIProvider | None:
        stmt = select(AIProvider).where(AIProvider.is_active == True).limit(1)  # noqa: E712
        return self.session.execute(stmt).scalars().first()

    def list_assets(self, *, asset_type: str | None = None) -> Sequence[Asset]:
        stmt = select(Asset)
        if asset_type:
            stmt = stmt.where(Asset.asset_type == asset_type)
        return self.session.execute(stmt.order_by(Asset.created_at.desc())).scalars().all()

    def list_groups(self) -> Sequence[Group]:
        return self.session.execute(select(Group).order_by(Group.id)).scalars().all()

    def create_video_project(self, *, name: str, **fields: Any) -> VideoProject:
        payload = dict(fields)
        payload.setdefault("status", "draft")
        payload.setdefault("canvas_ratio", "9:16")
        payload.setdefault("width", 1080)
        payload.setdefault("height", 1920)
        return self.add(VideoProject(name=name, **payload))

    def list_video_projects(self) -> Sequence[VideoProject]:
        stmt = select(VideoProject).order_by(VideoProject.updated_at.desc(), VideoProject.id.desc())
        return self.session.execute(stmt).scalars().all()

    def get_video_project(self, pk: int) -> VideoProject | None:
        return self.get_by_id(VideoProject, pk)

    def create_video_sequence(self, project_id: int, *, name: str, **fields: Any) -> VideoSequence:
        payload = dict(fields)
        existing = self.list_video_sequences(project_id)
        payload.setdefault("duration_ms", 0)
        payload.setdefault("sort_order", len(existing))
        payload.setdefault("is_active", not existing)
        sequence = self.add(VideoSequence(project_id=project_id, name=name, **payload))
        if bool(getattr(sequence, "is_active", False)):
            self.set_active_video_sequence(project_id, sequence.id)
            refreshed = self.get_by_id(VideoSequence, sequence.id)
            return refreshed or sequence
        return sequence

    def list_video_sequences(self, project_id: int) -> Sequence[VideoSequence]:
        stmt = (
            select(VideoSequence)
            .where(VideoSequence.project_id == project_id)
            .order_by(VideoSequence.sort_order.asc(), VideoSequence.id.asc())
        )
        return self.session.execute(stmt).scalars().all()

    def set_active_video_sequence(self, project_id: int, sequence_id: int) -> None:
        sequences = list(self.list_video_sequences(project_id))
        changed = False
        for sequence in sequences:
            should_be_active = int(sequence.id) == int(sequence_id)
            if bool(sequence.is_active) != should_be_active:
                sequence.is_active = should_be_active
                changed = True
        if changed:
            self.session.commit()
            self.session.expire_all()

    def append_video_clip(self, sequence_id: int, asset_id: int, **fields: Any) -> VideoClip:
        payload = dict(fields)
        source_in_ms = int(payload.pop("source_in_ms", 0) or 0)
        raw_source_out = payload.pop("source_out_ms", None)
        raw_duration = payload.pop("duration_ms", None)
        duration_ms = int(raw_duration if raw_duration is not None else 0)
        if raw_source_out is not None:
            source_out_ms = int(raw_source_out)
            if raw_duration is None:
                duration_ms = max(0, source_out_ms - source_in_ms)
        else:
            source_out_ms = source_in_ms + max(0, duration_ms)
        payload.setdefault("track_type", "video")
        payload.setdefault("track_index", 0)
        payload.setdefault("start_ms", 0)
        payload.setdefault("sort_order", self._next_video_clip_sort_order(sequence_id))
        payload.setdefault("transform_json", "{}")
        payload["source_in_ms"] = source_in_ms
        payload["source_out_ms"] = source_out_ms
        payload["duration_ms"] = max(0, duration_ms)
        clip = self.add(VideoClip(sequence_id=sequence_id, asset_id=asset_id, **payload))
        self._refresh_video_sequence_duration(sequence_id)
        refreshed = self.get_by_id(VideoClip, clip.id)
        return refreshed or clip

    def create_video_clip_placeholder(
        self,
        sequence_id: int,
        *,
        track_type: str,
        track_index: int,
        duration_ms: int,
    ) -> VideoClip:
        clip = self.add(
            VideoClip(
                sequence_id=sequence_id,
                asset_id=None,
                track_type=track_type,
                track_index=track_index,
                start_ms=0,
                source_in_ms=0,
                source_out_ms=max(0, int(duration_ms)),
                duration_ms=max(0, int(duration_ms)),
                sort_order=self._next_video_clip_sort_order(sequence_id),
                transform_json="{}",
            )
        )
        self._refresh_video_sequence_duration(sequence_id)
        refreshed = self.get_by_id(VideoClip, clip.id)
        return refreshed or clip

    def list_video_clips(self, sequence_id: int) -> Sequence[VideoClip]:
        stmt = (
            select(VideoClip)
            .where(VideoClip.sequence_id == sequence_id)
            .order_by(VideoClip.sort_order.asc(), VideoClip.id.asc())
        )
        return self.session.execute(stmt).scalars().all()

    def reorder_video_clips(self, sequence_id: int, ordered_ids: list[int]) -> Sequence[VideoClip]:
        order_map = {int(clip_id): index for index, clip_id in enumerate(ordered_ids)}
        clips = list(self.list_video_clips(sequence_id))
        base_index = len(order_map)
        for offset, clip in enumerate(clips):
            clip.sort_order = order_map.get(int(clip.id), base_index + offset)
        self.session.commit()
        self.session.expire_all()
        return self.list_video_clips(sequence_id)

    def create_video_subtitle(
        self,
        sequence_id: int,
        *,
        start_ms: int,
        end_ms: int,
        text: str,
        **fields: Any,
    ) -> VideoSubtitle:
        payload = dict(fields)
        payload.setdefault("style_json", "{}")
        payload.setdefault("sort_order", self._next_video_subtitle_sort_order(sequence_id))
        subtitle = self.add(
            VideoSubtitle(
                sequence_id=sequence_id,
                start_ms=int(start_ms),
                end_ms=int(end_ms),
                text=text,
                **payload,
            )
        )
        refreshed = self.get_by_id(VideoSubtitle, subtitle.id)
        return refreshed or subtitle

    def list_video_subtitles(self, sequence_id: int) -> Sequence[VideoSubtitle]:
        stmt = (
            select(VideoSubtitle)
            .where(VideoSubtitle.sequence_id == sequence_id)
            .order_by(VideoSubtitle.sort_order.asc(), VideoSubtitle.id.asc())
        )
        return self.session.execute(stmt).scalars().all()

    def list_analysis_snapshots(
        self, *, page_key: str | None = None
    ) -> Sequence[AnalysisSnapshot]:
        stmt = select(AnalysisSnapshot)
        if page_key:
            stmt = stmt.where(AnalysisSnapshot.page_key == page_key)
        return self.session.execute(
            stmt.order_by(AnalysisSnapshot.created_at.desc(), AnalysisSnapshot.id.desc())
        ).scalars().all()

    def list_report_runs(self) -> Sequence[ReportRun]:
        stmt = select(ReportRun).order_by(ReportRun.created_at.desc(), ReportRun.id.desc())
        return self.session.execute(stmt).scalars().all()

    def list_workflow_definitions(self) -> Sequence[WorkflowDefinition]:
        stmt = select(WorkflowDefinition).order_by(
            WorkflowDefinition.created_at.desc(), WorkflowDefinition.id.desc()
        )
        return self.session.execute(stmt).scalars().all()

    def list_workflow_runs(
        self, *, workflow_definition_id: int | None = None
    ) -> Sequence[WorkflowRun]:
        stmt = select(WorkflowRun)
        if workflow_definition_id is not None:
            stmt = stmt.where(WorkflowRun.workflow_definition_id == workflow_definition_id)
        return self.session.execute(
            stmt.order_by(WorkflowRun.created_at.desc(), WorkflowRun.id.desc())
        ).scalars().all()

    def list_experiment_projects(self) -> Sequence[ExperimentProject]:
        stmt = select(ExperimentProject).order_by(
            ExperimentProject.created_at.desc(), ExperimentProject.id.desc()
        )
        return self.session.execute(stmt).scalars().all()

    def list_experiment_views(
        self, *, experiment_project_id: int | None = None
    ) -> Sequence[ExperimentView]:
        stmt = select(ExperimentView)
        if experiment_project_id is not None:
            stmt = stmt.where(ExperimentView.experiment_project_id == experiment_project_id)
        return self.session.execute(
            stmt.order_by(ExperimentView.created_at.desc(), ExperimentView.id.desc())
        ).scalars().all()

    def list_activity_logs(self, *, category: str | None = None) -> Sequence[ActivityLog]:
        stmt = select(ActivityLog)
        if category:
            stmt = stmt.where(ActivityLog.category == category)
        return self.session.execute(
            stmt.order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())
        ).scalars().all()

    def list_recent_tasks(self, *, limit: int = 20) -> Sequence[Task]:
        stmt = select(Task).order_by(Task.created_at.desc(), Task.id.desc()).limit(limit)
        return self.session.execute(stmt).scalars().all()

    def list_recent_activity_logs(self, *, limit: int = 20) -> Sequence[ActivityLog]:
        stmt = select(ActivityLog).order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc()).limit(limit)
        return self.session.execute(stmt).scalars().all()

    # 鈹€鈹€ app settings 鈹€鈹€

    def get_setting(self, key: str, default: str = "") -> str:
        row = self.session.get(AppSetting, key)
        return row.value if row else default

    def set_setting(self, key: str, value: str) -> None:
        row = self.session.get(AppSetting, key)
        if row:
            row.value = value
        else:
            self.session.add(AppSetting(key=key, value=value))
        self.session.commit()
        self.session.expire_all()

    def get_all_settings(self) -> dict[str, str]:
        rows = self.session.execute(select(AppSetting)).scalars().all()
        return {r.key: r.value for r in rows}

    # 鈹€鈹€ aggregate queries (for dashboard) 鈹€鈹€

    def count_accounts_by_status(self) -> dict[str, int]:
        rows = self.session.execute(
            select(Account.status, func.count()).group_by(Account.status)
        ).all()
        return {status: cnt for status, cnt in rows}

    def count_tasks_by_status(self) -> dict[str, int]:
        rows = self.session.execute(
            select(Task.status, func.count()).group_by(Task.status)
        ).all()
        return {status: cnt for status, cnt in rows}

    def count_devices_by_status(self) -> dict[str, int]:
        rows = self.session.execute(
            select(Device.status, func.count()).group_by(Device.status)
        ).all()
        return {status: cnt for status, cnt in rows}

    def count_tasks_created_between(self, start: dt.datetime, end: dt.datetime) -> int:
        stmt = select(func.count()).select_from(Task).where(
            and_(Task.created_at >= start, Task.created_at < end)
        )
        return self.session.execute(stmt).scalar() or 0

    def count_tasks_completed_between(self, start: dt.datetime, end: dt.datetime) -> int:
        stmt = select(func.count()).select_from(Task).where(
            and_(Task.finished_at.is_not(None), Task.finished_at >= start, Task.finished_at < end)
        )
        return self.session.execute(stmt).scalar() or 0

    def count_tasks_failed_between(self, start: dt.datetime, end: dt.datetime) -> int:
        stmt = select(func.count()).select_from(Task).where(
            and_(Task.status == "failed", Task.created_at >= start, Task.created_at < end)
        )
        return self.session.execute(stmt).scalar() or 0

    def _next_video_clip_sort_order(self, sequence_id: int) -> int:
        stmt = select(func.max(VideoClip.sort_order)).where(VideoClip.sequence_id == sequence_id)
        current = self.session.execute(stmt).scalar()
        return int(current or 0) + 1 if current is not None else 0

    def _next_video_subtitle_sort_order(self, sequence_id: int) -> int:
        stmt = select(func.max(VideoSubtitle.sort_order)).where(VideoSubtitle.sequence_id == sequence_id)
        current = self.session.execute(stmt).scalar()
        return int(current or 0) + 1 if current is not None else 0

    def _refresh_video_sequence_duration(self, sequence_id: int) -> None:
        sequence = self.get_by_id(VideoSequence, sequence_id)
        if sequence is None:
            return
        clips = list(self.list_video_clips(sequence_id))
        duration_ms = 0
        for clip in clips:
            duration_ms = max(duration_ms, int(clip.start_ms or 0) + int(clip.duration_ms or 0))
        sequence.duration_ms = duration_ms
        self.session.commit()
        self.session.refresh(sequence)

    def close(self) -> None:
        if self._session is None:
            return
        self._session.close()
        self._session = None