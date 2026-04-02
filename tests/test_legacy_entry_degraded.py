from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_PY = ROOT / "desktop_app" / "main.py"


def test_legacy_desktop_entry_explicitly_marks_reference_only_runtime() -> None:
    text = MAIN_PY.read_text(encoding="utf-8")

    assert "REFERENCE ONLY" in text or "reference only" in text.lower()
    assert "apps/desktop" in text
    assert "apps/py-runtime" in text
