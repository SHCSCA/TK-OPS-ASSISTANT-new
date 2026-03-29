from __future__ import annotations

import json

from desktop_app.ui.bridge import Bridge


def test_bridge_get_asset_video_poster_stays_cached_only_on_cache_miss() -> None:
    bridge = Bridge()
    scheduled: list[str] = []

    bridge._assets.get_video_poster_cached = lambda path: {  # type: ignore[method-assign]
        "poster_path": "",
        "reason": "missing_cache",
    }
    bridge._assets.schedule_video_poster_generation = lambda path: scheduled.append(path) or True  # type: ignore[method-assign]

    response = json.loads(bridge.getAssetVideoPoster(r"C:\assets\demo.mp4"))

    assert response["ok"] is True
    assert response["data"]["poster_path"] == ""
    assert response["data"]["reason"] == "missing_cache"
    assert scheduled == []
