"""Insert video CRUD methods into repository.py before the close() method."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
p = ROOT / "desktop_app" / "database" / "repository.py"
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)

# find the line with 'def close'
idx = next(i for i, l in enumerate(lines) if "    def close(self) -> None:" in l)
print(f"close() starts at line {idx + 1}")

video_methods = """
    # ── video editor CRUD ─────────────────────────────────────────────

    def create_video_project(self, *, name: str, **fields: Any) -> VideoProject:
        obj = VideoProject(name=name, **fields)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def list_video_projects(self) -> Sequence[VideoProject]:
        stmt = select(VideoProject).order_by(VideoProject.created_at.desc(), VideoProject.id.desc())
        return self.session.execute(stmt).scalars().all()

    def get_video_project(self, pk: int) -> VideoProject | None:
        return self.session.get(VideoProject, pk)

    def create_video_sequence(self, project_id: int, *, name: str, **fields: Any) -> VideoSequence:
        obj = VideoSequence(project_id=project_id, name=name, **fields)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def list_video_sequences(self, project_id: int) -> Sequence[VideoSequence]:
        stmt = (
            select(VideoSequence)
            .where(VideoSequence.project_id == project_id)
            .order_by(VideoSequence.id)
        )
        return self.session.execute(stmt).scalars().all()

    def set_active_video_sequence(self, project_id: int, sequence_id: int) -> VideoProject | None:
        project = self.session.get(VideoProject, project_id)
        if project is None:
            return None
        project.active_sequence_id = sequence_id
        self.session.commit()
        self.session.refresh(project)
        return project

    def append_video_clip(
        self,
        sequence_id: int,
        asset_id: int,
        *,
        track_type: str = "video",
        track_index: int = 0,
        start_ms: int = 0,
        source_in_ms: int = 0,
        source_out_ms: int = 0,
        **fields: Any,
    ) -> VideoClip:
        existing = self.session.execute(
            select(func.count()).select_from(VideoClip).where(VideoClip.sequence_id == sequence_id)
        ).scalar() or 0
        duration_ms = source_out_ms - source_in_ms
        obj = VideoClip(
            sequence_id=sequence_id,
            asset_id=asset_id,
            track_type=track_type,
            track_index=track_index,
            sort_order=existing,
            start_ms=start_ms,
            source_in_ms=source_in_ms,
            source_out_ms=source_out_ms,
            duration_ms=duration_ms,
            **fields,
        )
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def create_video_clip_placeholder(
        self,
        sequence_id: int,
        *,
        track_type: str = "video",
        track_index: int = 0,
        duration_ms: int = 0,
    ) -> VideoClip:
        existing = self.session.execute(
            select(func.count()).select_from(VideoClip).where(VideoClip.sequence_id == sequence_id)
        ).scalar() or 0
        obj = VideoClip(
            sequence_id=sequence_id,
            asset_id=None,
            track_type=track_type,
            track_index=track_index,
            sort_order=existing,
            duration_ms=duration_ms,
        )
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def list_video_clips(self, sequence_id: int) -> Sequence[VideoClip]:
        stmt = (
            select(VideoClip)
            .where(VideoClip.sequence_id == sequence_id)
            .order_by(VideoClip.sort_order, VideoClip.id)
        )
        return self.session.execute(stmt).scalars().all()

    def reorder_video_clips(self, sequence_id: int, ordered_ids: list[int]) -> None:
        clips = {
            c.id: c
            for c in self.session.execute(
                select(VideoClip).where(VideoClip.sequence_id == sequence_id)
            ).scalars().all()
        }
        for idx, clip_id in enumerate(ordered_ids):
            if clip_id in clips:
                clips[clip_id].sort_order = idx
        self.session.commit()

    def create_video_subtitle(
        self,
        sequence_id: int,
        *,
        start_ms: int,
        end_ms: int,
        text: str,
        **fields: Any,
    ) -> VideoSubtitle:
        obj = VideoSubtitle(
            sequence_id=sequence_id,
            start_ms=start_ms,
            end_ms=end_ms,
            text=text,
            **fields,
        )
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def list_video_subtitles(self, sequence_id: int) -> Sequence[VideoSubtitle]:
        stmt = (
            select(VideoSubtitle)
            .where(VideoSubtitle.sequence_id == sequence_id)
            .order_by(VideoSubtitle.start_ms)
        )
        return self.session.execute(stmt).scalars().all()

    def create_video_export(
        self,
        *,
        project_id: int,
        sequence_id: int | None = None,
        preset: str = "mp4_1080p",
        output_path: str | None = None,
        **fields: Any,
    ) -> VideoExport:
        obj = VideoExport(
            project_id=project_id,
            sequence_id=sequence_id,
            preset=preset,
            output_path=output_path,
            **fields,
        )
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def list_video_exports(self, project_id: int) -> Sequence[VideoExport]:
        stmt = (
            select(VideoExport)
            .where(VideoExport.project_id == project_id)
            .order_by(VideoExport.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()

    def create_video_snapshot(
        self,
        project_id: int,
        *,
        title: str,
        payload_json: str = "{}",
    ) -> VideoSnapshot:
        obj = VideoSnapshot(project_id=project_id, title=title, payload_json=payload_json)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def list_video_snapshots(self, project_id: int) -> Sequence[VideoSnapshot]:
        stmt = (
            select(VideoSnapshot)
            .where(VideoSnapshot.project_id == project_id)
            .order_by(VideoSnapshot.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()

"""

new_lines = lines[:idx] + [video_methods] + lines[idx:]
p.write_text("".join(new_lines), encoding="utf-8")
print(f"Done. Total lines: {len(p.read_text(encoding='utf-8').splitlines())}")
