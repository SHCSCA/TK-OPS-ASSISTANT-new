from __future__ import annotations

import base64
import time
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

try:
    from PySide6.QtCore import QBuffer, QIODevice, Qt, QUrl
    from PySide6.QtGui import QGuiApplication, QImage
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer, QVideoSink
except Exception:
    QBuffer = None
    QIODevice = None
    Qt = None
    QUrl = None
    QGuiApplication = None
    QImage = None
    QAudioOutput = None
    QMediaPlayer = None
    QVideoSink = None


class VideoMonitorService:
    """Bridge-friendly native video preview controller for QWebEngine pages."""

    def __init__(self) -> None:
        self._player = None
        self._audio = None
        self._sink = None
        self._source_path = ""
        self._duration_ms = 0
        self._position_ms = 0
        self._clip_start_ms = 0
        self._clip_end_ms = 0
        self._frame_data = ""
        self._frame_token = 0
        self._last_frame_emit = 0.0
        self._error = ""
        self._status = "idle"
        self._playing = False
        self._pause_after_first_frame = False
        self._ready = False
        self._initialize_backend()

    def _initialize_backend(self) -> None:
        if (
            QMediaPlayer is None
            or QAudioOutput is None
            or QVideoSink is None
            or QGuiApplication is None
            or QGuiApplication.instance() is None
        ):
            self._status = "unsupported"
            return

        self._player = QMediaPlayer()
        self._audio = QAudioOutput()
        self._sink = QVideoSink()
        self._audio.setVolume(1.0)
        self._player.setAudioOutput(self._audio)
        self._player.setVideoSink(self._sink)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.positionChanged.connect(self._on_position_changed)
        self._player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)
        self._player.errorOccurred.connect(self._on_error)
        self._sink.videoFrameChanged.connect(self._on_video_frame_changed)
        self._ready = True

    def _normalize_local_path(self, file_path: str | None) -> Path | None:
        text = str(file_path or "").strip()
        if not text:
            return None
        if text.startswith("file://"):
            parsed = urlparse(text)
            if parsed.scheme != "file":
                return None
            text = f"//{parsed.netloc}{parsed.path}" if parsed.netloc else parsed.path
            text = unquote(text)
            if len(text) > 2 and text[0] == "/" and text[2] == ":":
                text = text.lstrip("/")
        return Path(text).expanduser()

    def _reset_frame(self) -> None:
        self._frame_data = ""
        self._frame_token += 1

    def _serialize_state(self) -> dict[str, Any]:
        return {
            "ready": self._ready,
            "source_path": self._source_path,
            "duration_ms": int(self._duration_ms or 0),
            "position_ms": int(self._position_ms or 0),
            "clip_start_ms": int(self._clip_start_ms or 0),
            "clip_end_ms": int(self._clip_end_ms or 0),
            "playing": bool(self._playing),
            "status": self._status,
            "error": self._error,
            "frame_token": int(self._frame_token or 0),
            "frame_data": self._frame_data,
        }

    def _on_duration_changed(self, duration_ms: int) -> None:
        self._duration_ms = int(duration_ms or 0)

    def _on_position_changed(self, position_ms: int) -> None:
        self._position_ms = int(position_ms or 0)
        if self._clip_end_ms > 0 and self._position_ms >= self._clip_end_ms and self._player is not None:
            self._player.pause()
            self._player.setPosition(self._clip_end_ms)
            self._position_ms = int(self._clip_end_ms)
            self._playing = False
            self._status = "paused"

    def _on_playback_state_changed(self, state: Any) -> None:
        if self._player is None or QMediaPlayer is None:
            self._playing = False
            return
        self._playing = state == QMediaPlayer.PlaybackState.PlayingState
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._status = "playing"
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self._status = "paused"
        else:
            self._status = "stopped"

    def _on_media_status_changed(self, status: Any) -> None:
        if QMediaPlayer is None:
            return
        mapping = {
            QMediaPlayer.MediaStatus.NoMedia: "idle",
            QMediaPlayer.MediaStatus.LoadingMedia: "loading",
            QMediaPlayer.MediaStatus.LoadedMedia: "loaded",
            QMediaPlayer.MediaStatus.BufferedMedia: "buffered",
            QMediaPlayer.MediaStatus.BufferingMedia: "buffering",
            QMediaPlayer.MediaStatus.EndOfMedia: "ended",
            QMediaPlayer.MediaStatus.InvalidMedia: "error",
        }
        self._status = mapping.get(status, self._status)
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self._player is not None:
            self._player.pause()
            self._playing = False

    def _on_error(self, *_: Any) -> None:
        if self._player is None:
            self._error = "播放器不可用"
        else:
            self._error = self._player.errorString() or "预览不可用"
        self._status = "error"
        self._playing = False

    def _on_video_frame_changed(self, frame: Any) -> None:
        if QImage is None or QBuffer is None or QIODevice is None or Qt is None:
            return
        if frame is None or not frame.isValid():
            return
        now = time.monotonic()
        if self._playing and now - self._last_frame_emit < 0.12:
            return
        image = frame.toImage()
        if image.isNull():
            return
        target = image.scaled(
            960,
            960,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not target.save(buffer, "JPG", 82):
            return
        encoded = base64.b64encode(bytes(buffer.data())).decode("ascii")
        self._frame_data = "data:image/jpeg;base64," + encoded
        self._frame_token += 1
        self._last_frame_emit = now
        if self._pause_after_first_frame and self._player is not None:
            self._pause_after_first_frame = False
            self._player.pause()
            self._playing = False
            self._status = "paused"

    def prepare(self, file_path: str | None, *, start_ms: int = 0, end_ms: int = 0, autoplay: bool = False) -> dict[str, Any]:
        self._error = ""
        self._clip_start_ms = max(0, int(start_ms or 0))
        self._clip_end_ms = max(0, int(end_ms or 0))
        self._position_ms = self._clip_start_ms
        self._reset_frame()
        if not self._ready or self._player is None or QUrl is None:
            self._status = "unsupported"
            self._error = "当前环境暂不支持原生视频预览"
            return self._serialize_state()

        source_path = self._normalize_local_path(file_path)
        if source_path is None or not source_path.exists() or not source_path.is_file():
            self.stop()
            self._status = "error"
            self._error = "未找到可播放文件"
            return self._serialize_state()

        self._source_path = str(source_path)
        self._pause_after_first_frame = not autoplay
        self._status = "loading"
        self._player.stop()
        self._player.setSource(QUrl.fromLocalFile(self._source_path))
        self._player.setPosition(self._clip_start_ms)
        self._player.play()
        return self._serialize_state()

    def play(self) -> dict[str, Any]:
        if self._player is None or not self._source_path:
            return self._serialize_state()
        if self._clip_end_ms > 0 and self._position_ms >= self._clip_end_ms:
            self._player.setPosition(self._clip_start_ms)
        self._pause_after_first_frame = False
        self._player.play()
        return self._serialize_state()

    def pause(self) -> dict[str, Any]:
        if self._player is not None:
            self._player.pause()
        self._playing = False
        if self._status != "error":
            self._status = "paused"
        return self._serialize_state()

    def stop(self) -> dict[str, Any]:
        if self._player is not None:
            self._player.stop()
        self._source_path = ""
        self._duration_ms = 0
        self._position_ms = 0
        self._clip_start_ms = 0
        self._clip_end_ms = 0
        self._playing = False
        self._status = "idle"
        self._error = ""
        self._reset_frame()
        return self._serialize_state()

    def seek(self, position_ms: int) -> dict[str, Any]:
        if self._player is None:
            return self._serialize_state()
        lower = self._clip_start_ms if self._clip_end_ms > 0 else 0
        upper = self._clip_end_ms if self._clip_end_ms > 0 else self._duration_ms
        bounded = max(lower, int(position_ms or 0))
        if upper > 0:
            bounded = min(upper, bounded)
        self._player.setPosition(bounded)
        self._position_ms = bounded
        return self._serialize_state()

    def step(self, delta_ms: int = 40) -> dict[str, Any]:
        return self.seek(self._position_ms + int(delta_ms or 0))

    def state(self) -> dict[str, Any]:
        return self._serialize_state()