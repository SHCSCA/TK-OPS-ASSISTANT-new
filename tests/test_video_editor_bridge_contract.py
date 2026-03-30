from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_PY = ROOT / "desktop_app" / "ui" / "bridge.py"
DATA_JS = ROOT / "desktop_app" / "assets" / "js" / "data.js"


def _extract_python_bridge_methods() -> set[str]:
    text = BRIDGE_PY.read_text(encoding="utf-8")
    return set(re.findall(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text))


def test_video_editor_bridge_methods_exist() -> None:
    methods = _extract_python_bridge_methods()
    expected = {
        "listVideoProjects",
        "createVideoProject",
        "listVideoSequences",
        "appendAssetsToSequence",
        "listVideoClips",
        "updateVideoClip",
        "createVideoSubtitle",
        "createVideoExport",
        "listVideoSnapshots",
        "restoreVideoSnapshot",
    }
    missing = expected - methods
    assert not missing, f"Bridge missing video editor methods: {sorted(missing)}"


def test_video_editor_data_api_groups_exist() -> None:
    text = DATA_JS.read_text(encoding="utf-8")
    expected = {
        "videoProjects",
        "videoSequences",
        "videoClips",
        "videoSubtitles",
        "videoExports",
        "videoSnapshots",
    }
    missing = {group for group in expected if f"{group}:" not in text}
    assert not missing, f"data.js missing video editor API groups: {sorted(missing)}"
