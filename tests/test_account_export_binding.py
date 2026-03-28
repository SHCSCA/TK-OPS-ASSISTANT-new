from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINDINGS_JS = ROOT / "desktop_app" / "assets" / "js" / "bindings.js"
DATA_JS = ROOT / "desktop_app" / "assets" / "js" / "data.js"


def test_account_export_uses_named_csv_export_when_backend_utils_are_available() -> None:
    bindings = BINDINGS_JS.read_text(encoding="utf-8")
    data_js = DATA_JS.read_text(encoding="utf-8")

    assert "api.utils.exportTextFile('\\uFEFF' + csv, 'accounts-export.csv')" in bindings
    assert "showToast(saved && saved.saved ? '账号清单已导出' : '已取消导出'" in bindings
    assert "showToast('账号清单已导出', 'success');" in bindings
    assert "return callBackend('exportNamedTextFile', text || '', suggestedName);" in data_js
