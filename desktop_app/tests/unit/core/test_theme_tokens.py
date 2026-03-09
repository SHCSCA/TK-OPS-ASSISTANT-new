from __future__ import annotations

import re

from ....core.theme.qss import generate_qss, resolve_tokens
from ....core.theme.tokens import STATIC_TOKENS, TOKENS, get_token_value
from ....core.types import ThemeMode

HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
RGBA_COLOR_RE = re.compile(
    r"^rgba\(\s*(?:[01]?\d?\d|2[0-4]\d|25[0-5])\s*,\s*(?:[01]?\d?\d|2[0-4]\d|25[0-5])\s*,\s*(?:[01]?\d?\d|2[0-4]\d|25[0-5])\s*,\s*(?:0|0?\.\d+|1(?:\.0+)?)\s*\)$"
)

REQUIRED_TOKENS = {
    "surface.primary",
    "surface.secondary",
    "surface.tertiary",
    "surface.elevated",
    "surface.sunken",
    "text.primary",
    "text.secondary",
    "text.tertiary",
    "text.disabled",
    "text.inverse",
    "brand.primary",
    "brand.primary_hover",
    "brand.primary_pressed",
    "brand.secondary",
    "brand.accent",
    "role.manager",
    "role.creator",
    "role.analyst",
    "role.automation",
    "status.success",
    "status.warning",
    "status.error",
    "status.info",
    "border.default",
    "border.strong",
    "border.focus",
    "tag.color.neutral",
    "table.header_bg",
}

COLOR_ONLY_TOKENS = {
    "surface.primary",
    "surface.secondary",
    "surface.tertiary",
    "surface.elevated",
    "surface.sunken",
    "text.primary",
    "text.secondary",
    "text.tertiary",
    "text.disabled",
    "text.inverse",
    "brand.primary",
    "brand.primary_hover",
    "brand.primary_pressed",
    "brand.secondary",
    "brand.accent",
    "role.manager",
    "role.creator",
    "role.analyst",
    "role.automation",
    "status.success",
    "status.warning",
    "status.error",
    "status.info",
    "border.default",
    "border.strong",
    "border.focus",
    "tag.color.neutral",
    "chart.series[0]",
    "chart.series[1]",
    "chart.series[2]",
    "chart.series[3]",
    "chart.series[4]",
    "chart.series[5]",
    "chart.series[6]",
    "chart.series[7]",
    "chart.series.0",
    "chart.series.1",
    "chart.series.2",
    "chart.series.3",
    "chart.series.4",
    "chart.series.5",
    "chart.series.6",
    "chart.series.7",
    "table.header_bg",
    "table.header_bg.dark",
    "tag.color.brand.bg",
    "tag.color.brand.fg",
    "tag.color.success.bg",
    "tag.color.success.fg",
    "tag.color.warning.bg",
    "tag.color.warning.fg",
    "tag.color.error.bg",
    "tag.color.error.fg",
}


def _is_valid_color(value: str) -> bool:
    return bool(HEX_COLOR_RE.fullmatch(value) or RGBA_COLOR_RE.fullmatch(value))


def _token_or_fallback(name: str, mode: ThemeMode, fallback: str = "brand.primary") -> str:
    try:
        return get_token_value(name, mode)
    except KeyError:
        return get_token_value(fallback, mode)


def test_light_mode_has_all_required_tokens() -> None:
    resolved = resolve_tokens(ThemeMode.LIGHT)
    assert REQUIRED_TOKENS.issubset(resolved)


def test_dark_mode_has_all_required_tokens() -> None:
    resolved = resolve_tokens(ThemeMode.DARK)
    assert REQUIRED_TOKENS.issubset(resolved)


def test_light_and_dark_tokens_differ() -> None:
    assert get_token_value("surface.primary", ThemeMode.LIGHT) != get_token_value("surface.primary", ThemeMode.DARK)
    assert get_token_value("surface.secondary", ThemeMode.LIGHT) != get_token_value("surface.secondary", ThemeMode.DARK)
    assert get_token_value("text.primary", ThemeMode.LIGHT) != get_token_value("text.primary", ThemeMode.DARK)


def test_brand_primary_consistent_across_modes() -> None:
    light_brand = get_token_value("brand.primary", ThemeMode.LIGHT).lower()
    dark_brand = get_token_value("brand.primary", ThemeMode.DARK).lower()
    assert light_brand == dark_brand
    assert light_brand in {"#00f2ea", "#00f0e8"}


def test_all_token_values_are_valid_hex_or_rgba() -> None:
    for mode in (ThemeMode.LIGHT, ThemeMode.DARK):
        resolved = resolve_tokens(mode)
        for token_name in COLOR_ONLY_TOKENS:
            assert _is_valid_color(resolved[token_name]), f"{token_name} should resolve to a color, got {resolved[token_name]!r}"


def test_resolve_tokens_returns_complete_dict() -> None:
    resolved = resolve_tokens(ThemeMode.LIGHT)
    assert len(resolved) == len(TOKENS) + len(STATIC_TOKENS)
    assert set(TOKENS).issubset(resolved)
    assert set(STATIC_TOKENS).issubset(resolved)


def test_get_token_value_returns_string() -> None:
    assert isinstance(get_token_value("surface.primary", ThemeMode.LIGHT), str)
    assert isinstance(get_token_value("font.size.md", ThemeMode.DARK), str)


def test_unknown_token_has_fallback() -> None:
    fallback_value = _token_or_fallback("unknown.token", ThemeMode.DARK)
    assert fallback_value == get_token_value("brand.primary", ThemeMode.DARK)


def test_domain_group_colors_present() -> None:
    resolved = resolve_tokens(ThemeMode.LIGHT)
    assert resolved["role.manager"] == "#FF6B6B"
    assert resolved["role.creator"] == "#4ECDC4"
    assert resolved["role.analyst"] == "#95E1D3"
    assert resolved["role.automation"] == "#F38181"


def test_qss_generation_nonempty_for_both_modes() -> None:
    for mode in (ThemeMode.LIGHT, ThemeMode.DARK):
        qss = generate_qss(mode)
        assert qss
        assert "QWidget" in qss


def test_dark_mode_uses_dark_table_header_override() -> None:
    dark_tokens = resolve_tokens(ThemeMode.DARK)
    assert dark_tokens["table.header_bg"] == get_token_value("table.header_bg.dark", ThemeMode.DARK)
    assert dark_tokens["table.header_bg"] != resolve_tokens(ThemeMode.LIGHT)["table.header_bg"]


def test_generated_qss_contains_resolved_brand_color_without_placeholders() -> None:
    qss = generate_qss(ThemeMode.LIGHT)
    assert "#00F2EA" in qss or "#00f0e8" in qss
    assert "${brand_primary}" not in qss
    assert "@brand.primary" not in qss
