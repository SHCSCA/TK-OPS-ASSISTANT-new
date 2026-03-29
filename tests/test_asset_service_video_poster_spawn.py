from __future__ import annotations

from pathlib import Path

from desktop_app.services import asset_service as asset_service_module
from desktop_app.services.asset_service import AssetService


def test_schedule_video_poster_generation_prefers_pythonw_on_windows(tmp_path, monkeypatch) -> None:
    service = AssetService()
    video_path = tmp_path / "demo.mp4"
    video_path.write_bytes(b"video")
    python_exe = tmp_path / "python.exe"
    python_exe.write_bytes(b"")
    pythonw_exe = tmp_path / "pythonw.exe"
    pythonw_exe.write_bytes(b"")
    captured: dict[str, object] = {}

    monkeypatch.setattr(asset_service_module.sys, "executable", str(python_exe))
    monkeypatch.setattr(
        service,
        "_video_candidate",
        lambda file_path: (video_path, "ok"),
    )
    monkeypatch.setattr(
        service,
        "get_video_poster_cached",
        lambda file_path: {"poster_path": "", "reason": "missing_cache"},
    )

    def fake_popen(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs

        class _DummyProcess:
            pid = 1

        return _DummyProcess()

    monkeypatch.setattr(asset_service_module.subprocess, "Popen", fake_popen)

    assert service.schedule_video_poster_generation(str(video_path)) is True
    assert captured["args"][0] == str(pythonw_exe)
