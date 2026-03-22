from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYTICS_JS = ROOT / "desktop_app" / "assets" / "js" / "factories" / "analytics.js"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"


def _window(text: str, anchor: str, span: int = 2400) -> str:
    start = text.find(anchor)
    assert start >= 0, f"Missing anchor: {anchor}"
    return text[start:start + span]


def test_static_analytics_templates_do_not_freeze_unsupported_profit_or_order_metrics() -> None:
    text = ANALYTICS_JS.read_text(encoding='utf-8')
    forbidden = [
        "{ label: '总销售额'",
        "{ label: '总成本'",
        "{ label: '净利润'",
        "{ label: 'ROI'",
        "{ label: '曝光到点击'",
        "{ label: '点击到加购'",
        "{ label: '下单转化'",
    ]
    for marker in forbidden:
        assert marker not in text, marker


def test_profit_and_conversion_loaders_no_longer_use_fabricated_business_estimates() -> None:
    text = PAGE_LOADERS_JS.read_text(encoding='utf-8')
    profit_window = _window(text, "loaders['profit-analysis']")
    conversion_window = _window(text, "loaders['ecommerce-conversion']")

    assert '_estimateRevenue(' not in profit_window
    assert '_estimateCost(' not in profit_window
    assert 'providersFeeEstimate(' not in profit_window
    assert 'api.analytics.summary()' in profit_window

    assert '_trafficCtr(' not in conversion_window
    assert 'api.analytics.conversion()' in conversion_window
