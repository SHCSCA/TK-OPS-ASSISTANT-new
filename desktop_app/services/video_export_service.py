"""Video export service backed by real ffmpeg execution."""
from __future__ import annotations

import datetime as dt
import logging
import os
import shlex
import subprocess
from pathlib import Path

from desktop_app.database import DATA_DIR
from desktop_app.database.models import Asset, VideoClip, VideoExport, VideoSequence
from desktop_app.database.repository import Repository
from desktop_app.services.ffmpeg_runtime import ensure_ffmpeg_available, resolve_ffmpeg_binaries
from desktop_app.services.video_editing_service import VideoEditingService

log = logging.getLogger(__name__)


class VideoExportService(VideoEditingService):
    def __init__(self, repo: Repository | None = None, *, ffmpeg_root: Path | None = None) -> None:
        super().__init__(repo)
        self._ffmpeg_root = ffmpeg_root

    def validate_and_create_export(self, project_id: int, sequence_id: int, *, preset: str) -> dict[str, object]:
        project = self._repo.get_video_project(int(project_id))
        sequence = self._repo.get_by_id(VideoSequence, int(sequence_id))
        if sequence is None or project is None or int(sequence.project_id) != int(project.id):
            return {"ok": False, "error": "序列不存在", "errors": ["序列不存在"]}

        validation = self.validate_export(project.id, sequence.id)
        if not validation.get("ok"):
            errors = [str(item) for item in validation.get("errors", []) if str(item).strip()]
            message = errors[0] if errors else "当前序列暂时无法导出"
            return {"ok": False, "error": message, "errors": errors or [message]}

        runtime = ensure_ffmpeg_available(root=self._ffmpeg_root)
        if not bool(runtime.get("ok")):
            message = str(runtime.get("error") or "未找到可用的 ffmpeg")
            return {"ok": False, "error": message, "errors": [message]}

        export = self._repo.add(
            VideoExport(
                project_id=int(project.id),
                sequence_id=int(sequence.id),
                status="pending",
                preset=str(preset or "").strip() or "final",
                output_path="",
                ffmpeg_command="",
                error_message=None,
                started_at=None,
                finished_at=None,
            )
        )
        output_path = self._default_output_path(export)
        export = self._repo.update(export, output_path=str(output_path))
        return {
            "ok": True,
            "export_id": int(export.id),
            "status": export.status,
            "preset": export.preset,
            "output_path": export.output_path,
        }

    def build_export_command(self, export_id: int) -> list[str]:
        export = self._require_export(export_id)
        ffmpeg_path, _ = resolve_ffmpeg_binaries(root=self._ffmpeg_root)
        clip_specs = self._clip_specs(export)
        if not clip_specs:
            raise ValueError("没有可导出的素材")

        output_path = self._ensure_output_path(export)
        if len(clip_specs) == 1:
            return self._single_clip_command(Path(ffmpeg_path), clip_specs[0], output_path)

        return self._concat_command(Path(ffmpeg_path), clip_specs, output_path)

    def run_export(self, export_id: int) -> VideoExport:
        export = self._require_export(export_id)
        output_path = self._ensure_output_path(export)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        command = self.build_export_command(export_id)
        export = self._repo.update(
            export,
            status="running",
            started_at=dt.datetime.now(),
            finished_at=None,
            error_message=None,
            ffmpeg_command=self._format_command(command),
        )

        try:
            completed = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                **self._subprocess_kwargs(),
            )
            if completed.stderr:
                log.debug("ffmpeg stderr for export %s: %s", export_id, completed.stderr.strip())
            if not output_path.exists() or output_path.stat().st_size <= 0:
                raise RuntimeError("导出流程已执行，但没有生成输出文件")
        except subprocess.CalledProcessError as exc:
            return self._mark_failed(export, self._command_error(exc))
        except Exception as exc:
            return self._mark_failed(export, str(exc))

        return self._repo.update(
            export,
            status="completed",
            finished_at=dt.datetime.now(),
            error_message=None,
        )

    def _require_export(self, export_id: int) -> VideoExport:
        export = self._repo.get_by_id(VideoExport, int(export_id))
        if export is None:
            raise ValueError("导出任务不存在")
        return export

    def _ensure_output_path(self, export: VideoExport) -> Path:
        if str(export.output_path or "").strip():
            return Path(str(export.output_path))
        output_path = self._default_output_path(export)
        refreshed = self._repo.update(export, output_path=str(output_path))
        return Path(str(refreshed.output_path or output_path))

    def _default_output_path(self, export: VideoExport) -> Path:
        base_dir = Path(os.environ.get("TK_OPS_DATA_DIR") or DATA_DIR)
        export_dir = (
            base_dir
            / "video-exports"
            / f"project_{int(export.project_id)}"
            / f"sequence_{int(export.sequence_id or 0)}"
        )
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir / f"export_{int(export.id)}_{self._safe_name(export.preset)}.mp4"

    def _clip_specs(self, export: VideoExport) -> list[dict[str, object]]:
        clips = list(self._repo.list_video_clips(int(export.sequence_id or 0)))
        specs: list[dict[str, object]] = []
        for clip in clips:
            if clip.asset_id is None:
                continue
            asset = self._repo.get_by_id(Asset, int(clip.asset_id))
            if asset is None:
                raise ValueError(f"素材不存在: {clip.asset_id}")
            source_path = Path(str(asset.file_path or "")).expanduser()
            if not source_path.is_file():
                raise ValueError(f"素材源文件不存在: {asset.file_path}")
            specs.append(
                {
                    "clip": clip,
                    "asset": asset,
                    "source_path": source_path,
                    "source_in_ms": int(clip.source_in_ms or 0),
                    "duration_ms": self._clip_duration_ms(clip),
                }
            )
        return specs

    def _single_clip_command(
        self,
        ffmpeg_path: Path,
        clip_spec: dict[str, object],
        output_path: Path,
    ) -> list[str]:
        return [
            str(ffmpeg_path),
            "-y",
            "-ss",
            self._seconds_text(int(clip_spec["source_in_ms"])),
            "-t",
            self._seconds_text(int(clip_spec["duration_ms"])),
            "-i",
            str(clip_spec["source_path"]),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(output_path),
        ]

    def _concat_command(
        self,
        ffmpeg_path: Path,
        clip_specs: list[dict[str, object]],
        output_path: Path,
    ) -> list[str]:
        concat_path = output_path.with_suffix(".concat.txt")
        lines: list[str] = []
        for clip_spec in clip_specs:
            source_path = Path(str(clip_spec["source_path"])).as_posix().replace("'", "'\\''")
            lines.append(f"file '{source_path}'")
        concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return [
            str(ffmpeg_path),
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(output_path),
        ]

    @staticmethod
    def _clip_duration_ms(clip: VideoClip) -> int:
        duration_ms = int(clip.duration_ms or 0)
        if duration_ms > 0:
            return duration_ms
        return max(0, int(clip.source_out_ms or 0) - int(clip.source_in_ms or 0))

    @staticmethod
    def _seconds_text(duration_ms: int) -> str:
        return f"{max(0, int(duration_ms)) / 1000:.3f}"

    @staticmethod
    def _format_command(command: list[str]) -> str:
        if os.name == "nt":
            return subprocess.list2cmdline(command)
        return shlex.join(command)

    @staticmethod
    def _safe_name(value: str) -> str:
        safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in str(value or "").strip())
        return safe or "final"

    @staticmethod
    def _subprocess_kwargs() -> dict[str, object]:
        if os.name != "nt":
            return {}
        return {"creationflags": subprocess.CREATE_NO_WINDOW}

    @staticmethod
    def _command_error(exc: subprocess.CalledProcessError) -> str:
        message = (exc.stderr or exc.stdout or str(exc)).strip()
        return message or "FFmpeg 导出失败"

    def _mark_failed(self, export: VideoExport, message: str) -> VideoExport:
        log.exception("Video export failed: export_id=%s", export.id)
        return self._repo.update(
            export,
            status="failed",
            finished_at=dt.datetime.now(),
            error_message=f"FFmpeg 导出失败：{message}",
        )
