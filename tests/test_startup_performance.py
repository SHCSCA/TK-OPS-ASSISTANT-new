from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_PY = ROOT / "desktop_app" / "app.py"


def test_app_boot_shows_window_before_db_warmup_thread() -> None:
    text = APP_PY.read_text(encoding="utf-8")

    assert "def _warm_up_database() -> None:" in text
    assert "threading.Thread(target=_warm_up_database" in text
    assert "window.show()" in text
    assert text.index("window.show()") < text.index("threading.Thread(target=_warm_up_database")

