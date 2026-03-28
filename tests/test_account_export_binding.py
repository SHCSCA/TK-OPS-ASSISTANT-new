from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINDINGS_JS = ROOT / "desktop_app" / "assets" / "js" / "bindings.js"
DATA_JS = ROOT / "desktop_app" / "assets" / "js" / "data.js"


def test_account_export_uses_named_csv_export_when_backend_utils_are_available() -> None:
    bindings = BINDINGS_JS.read_text(encoding="utf-8")
    data_js = DATA_JS.read_text(encoding="utf-8")

    assert "api.utils.exportTextFile('\\uFEFF' + csv, 'accounts-export.csv')" in bindings
    assert "tkopsAccountExportBound" in bindings
    assert ".page-header .header-actions .secondary-button" in bindings
    assert "currentRoute === 'account' && text === '导出账号清单'" in bindings
    assert 'showToast(saved && saved.saved ?' in bindings
    assert "return callBackend('exportNamedTextFile', text || '', suggestedName);" in data_js
