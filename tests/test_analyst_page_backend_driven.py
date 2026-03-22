from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYTICS_JS = ROOT / "desktop_app" / "assets" / "js" / "factories" / "analytics.js"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
BRIDGE_PY = ROOT / "desktop_app" / "ui" / "bridge.py"
BRIDGE_JS = ROOT / "desktop_app" / "assets" / "js" / "bridge.js"
DATA_JS = ROOT / "desktop_app" / "assets" / "js" / "data.js"


def _window(text: str, anchor: str, span: int = 2600) -> str:
    start = text.find(anchor)
    assert start >= 0, f"Missing anchor: {anchor}"
    return text[start:start + span]


def test_analytics_factories_no_longer_freeze_demo_metric_values() -> None:
    text = ANALYTICS_JS.read_text(encoding="utf-8")
    forbidden = [
        "value: '86%'",
        "value: '284万'",
        "value: '4.8%'",
        "value: '67%'",
        "value: '18', delta: '+2', note: '新增 2 个高增长对手'",
        "fans: '32.4万'",
        "value: '18', delta: '+4', note: '新增 4 个专题模板'",
        "value: '8,420'",
        "CTR 4.8%",
        "CVR 2.2%",
        "成本 -6%",
    ]
    for marker in forbidden:
        assert marker not in text, marker


def test_page_loaders_consume_backend_analyst_surfaces_for_primary_analyst_routes() -> None:
    text = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    for route in [
        "traffic-board",
        "competitor-monitor",
        "blue-ocean",
        "interaction-analysis",
    ]:
        window = _window(text, f"loaders['{route}']")
        assert "api.analytics." in window or "api.activity." in window, route


def test_bridge_and_frontend_expose_backend_driven_analyst_surfaces() -> None:
    bridge_py_text = BRIDGE_PY.read_text(encoding="utf-8")
    bridge_js_text = BRIDGE_JS.read_text(encoding="utf-8")
    data_js_text = DATA_JS.read_text(encoding="utf-8")

    for name in ["getTrafficAnalysis", "getCompetitorAnalysis", "getBlueOceanAnalysis", "getInteractionAnalysis"]:
        assert f"def {name}(" in bridge_py_text, name
        assert f"{name}:" in bridge_js_text, name
        assert f"callBackend('{name}')" in data_js_text, name
