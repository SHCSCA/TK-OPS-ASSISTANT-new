from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENTS_CSS = ROOT / "desktop_app" / "assets" / "css" / "components.css"


def test_account_card_grid_keeps_fixed_card_columns_and_pins_actions() -> None:
    text = COMPONENTS_CSS.read_text(encoding="utf-8")

    assert ".account-grid {" in text
    assert "align-items: stretch;" in text
    assert "grid-template-columns: repeat(auto-fill, minmax(300px, 300px));" in text
    assert "justify-content: flex-start;" in text
    assert ".account-card__meta {" in text
    assert "flex: 1 1 auto;" in text
    assert ".account-card__actions {" in text
    assert "margin-top: auto;" in text
