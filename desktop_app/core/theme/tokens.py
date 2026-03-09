from __future__ import annotations

"""Semantic design tokens used by the TK-OPS QSS theme engine."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from ..types import ThemeMode, ThemeTokenName


@dataclass(frozen=True)
class TokenValue:
    """Theme-dependent token value pair."""

    light: str
    dark: str

    def resolve(self, mode: ThemeMode) -> str:
        """Resolve the value for the active mode."""

        return self.dark if mode == ThemeMode.DARK else self.light


_THEMED_TOKENS: dict[str, TokenValue] = {
    # Surface
    "surface.primary": TokenValue(light="#F5F8F8", dark="#0F2323"),
    "surface.secondary": TokenValue(light="#FFFFFF", dark="#0F172A"),
    "surface.tertiary": TokenValue(light="#F8FAFC", dark="#1E293B"),
    "surface.elevated": TokenValue(light="#FFFFFF", dark="#0F172A"),
    "surface.sunken": TokenValue(light="#F1F5F9", dark="#1E293B"),
    # Text
    "text.primary": TokenValue(light="#0F172A", dark="#F1F5F9"),
    "text.secondary": TokenValue(light="#64748B", dark="#94A3B8"),
    "text.tertiary": TokenValue(light="#94A3B8", dark="#64748B"),
    "text.disabled": TokenValue(light="#CBD5E1", dark="#475569"),
    "text.inverse": TokenValue(light="#0F2323", dark="#0F2323"),
    # Brand
    "brand.primary": TokenValue(light="#00F2EA", dark="#00F2EA"),
    "brand.primary_hover": TokenValue(light="rgba(0,242,234,0.90)", dark="rgba(0,242,234,0.90)"),
    "brand.primary_pressed": TokenValue(light="rgba(0,242,234,0.80)", dark="rgba(0,242,234,0.80)"),
    "brand.secondary": TokenValue(light="#101818", dark="#101818"),
    "brand.accent": TokenValue(light="#5E8D8B", dark="#5E8D8B"),
    # Roles
    "role.manager": TokenValue(light="#FF6B6B", dark="#FF6B6B"),
    "role.creator": TokenValue(light="#4ECDC4", dark="#4ECDC4"),
    "role.analyst": TokenValue(light="#95E1D3", dark="#95E1D3"),
    "role.automation": TokenValue(light="#F38181", dark="#F38181"),
    # Status / semantic
    "status.success": TokenValue(light="#10B981", dark="#34D399"),
    "status.warning": TokenValue(light="#F59E0B", dark="#FBBF24"),
    "status.error": TokenValue(light="#EF4444", dark="#F87171"),
    "status.info": TokenValue(light="#3B82F6", dark="#60A5FA"),
    "border.default": TokenValue(light="#E2E8F0", dark="#1E293B"),
    "border.strong": TokenValue(light="#CBD5E1", dark="#334155"),
    "border.focus": TokenValue(light="rgba(0,242,234,0.50)", dark="rgba(0,242,234,0.50)"),
    "tag.color.neutral": TokenValue(light="#F1F5F9", dark="#1E293B"),
    # Shadows
    "shadow.sm": TokenValue(light="0 1px 2px rgba(0,0,0,0.05)", dark="0 1px 2px rgba(0,0,0,0.18)"),
    "shadow.md": TokenValue(
        light="0 4px 6px -1px rgba(0,0,0,0.10), 0 2px 4px -2px rgba(0,0,0,0.10)",
        dark="0 4px 6px -1px rgba(0,0,0,0.28), 0 2px 4px -2px rgba(0,0,0,0.28)",
    ),
    "shadow.lg": TokenValue(
        light="0 10px 15px -3px rgba(0,0,0,0.10), 0 4px 6px -4px rgba(0,0,0,0.10)",
        dark="0 10px 15px -3px rgba(0,0,0,0.32), 0 4px 6px -4px rgba(0,0,0,0.32)",
    ),
    "shadow.xl": TokenValue(
        light="0 20px 25px -5px rgba(0,0,0,0.10), 0 8px 10px -6px rgba(0,0,0,0.10)",
        dark="0 20px 25px -5px rgba(0,0,0,0.36), 0 8px 10px -6px rgba(0,0,0,0.36)",
    ),
    "shadow.glow.brand": TokenValue(light="0 0 10px rgba(0,242,234,0.50)", dark="0 0 10px rgba(0,242,234,0.50)"),
}

_STATIC_TOKENS: dict[str, str] = {
    # Charts
    "chart.series[0]": "#00F2EA",
    "chart.series[1]": "#F00078",
    "chart.series[2]": "#7800F0",
    "chart.series[3]": "#0078F0",
    "chart.series[4]": "#F0B400",
    "chart.series[5]": "#4ECDC4",
    "chart.series[6]": "#FF6B6B",
    "chart.series[7]": "#95E1D3",
    "chart.series.0": "#00F2EA",
    "chart.series.1": "#F00078",
    "chart.series.2": "#7800F0",
    "chart.series.3": "#0078F0",
    "chart.series.4": "#F0B400",
    "chart.series.5": "#4ECDC4",
    "chart.series.6": "#FF6B6B",
    "chart.series.7": "#95E1D3",
    # Typography
    "font.family.primary": '"Spline Sans", sans-serif',
    "font.family.chinese": '"Noto Sans SC", "Microsoft YaHei", sans-serif',
    "font.family.mono": 'ui-monospace, "SFMono-Regular", "SF Mono", Consolas, "Liberation Mono", Menlo, monospace',
    "font.size.xs": "11px",
    "font.size.sm": "12px",
    "font.size.md": "14px",
    "font.size.lg": "16px",
    "font.size.xl": "18px",
    "font.size.xxl": "24px",
    "font.size.display": "32px",
    "font.weight.regular": "400",
    "font.weight.medium": "500",
    "font.weight.semibold": "600",
    "font.weight.bold": "700",
    "line.height.tight": "1.2",
    "line.height.normal": "1.5",
    "line.height.relaxed": "1.75",
    # Spacing
    "spacing.2xs": "2px",
    "spacing.xs": "4px",
    "spacing.sm": "6px",
    "spacing.md": "8px",
    "spacing.lg": "12px",
    "spacing.xl": "16px",
    "spacing.2xl": "24px",
    "spacing.3xl": "32px",
    "spacing.4xl": "48px",
    # Layout
    "layout.content_padding": "32px",
    "layout.card_padding": "24px",
    "layout.section_gap": "24px",
    "layout.sidebar_width.raw": "240 / 256 / 288 / 320 / 400 / 480px",
    "layout.sidebar_width.canonical": "280px",
    # Radius
    "radius.sm": "4px",
    "radius.md": "8px",
    "radius.lg": "12px",
    "radius.xl": "16px",
    "radius.pill": "9999px",
    # Motion
    "duration.fast": "150ms",
    "duration.normal": "250ms",
    "duration.slow": "400ms",
    "easing.default": "cubic-bezier(0.4, 0, 0.2, 1)",
    "easing.bounce": "cubic-bezier(0.34, 1.56, 0.64, 1)",
    # Component tokens
    "sidebar.width.expanded": "280px",
    "sidebar.width.collapsed": "64px",
    "card.padding": "24px",
    "card.radius": "12px",
    "card.shadow": "shadow.md",
    "input.height": "40px",
    "input.padding": "12px 16px",
    "input.radius": "8px",
    "button.height.sm": "36px",
    "button.height.md": "40px",
    "button.height.lg": "48px",
    "button.padding": "8px 16px / 12px 24px",
    "button.padding.compact": "8px 16px",
    "button.padding.primary": "12px 24px",
    "button.radius": "8px",
    "table.row_height": "48px",
    "table.header_bg": "#F8FAFC",
    "table.header_bg.dark": "rgba(30,41,59,0.50)",
    "tag.font_size": "10px",
    "tag.padding": "2px 8px",
    "tag.radius": "4px or 9999px",
    "tag.radius.rect": "4px",
    "tag.radius.pill": "9999px",
    "tag.color.brand": "rgba(0,242,234,0.10) / #00F2EA",
    "tag.color.brand.bg": "rgba(0,242,234,0.10)",
    "tag.color.brand.fg": "#00F2EA",
    "tag.color.success": "#D1FAE5 / #10B981",
    "tag.color.success.bg": "#D1FAE5",
    "tag.color.success.fg": "#10B981",
    "tag.color.warning": "#FEF3C7 / #F59E0B",
    "tag.color.warning.bg": "#FEF3C7",
    "tag.color.warning.fg": "#F59E0B",
    "tag.color.error": "#FEE2E2 / #EF4444",
    "tag.color.error.bg": "#FEE2E2",
    "tag.color.error.fg": "#EF4444",
}

TOKENS: Mapping[str, TokenValue] = MappingProxyType(_THEMED_TOKENS)
STATIC_TOKENS: Mapping[str, str] = MappingProxyType(_STATIC_TOKENS)


def get_token_value(name: str | ThemeTokenName, mode: ThemeMode) -> str:
    """Resolve a semantic token by name for a specific theme mode."""

    token_name = str(name)
    if token_name in TOKENS:
        return TOKENS[token_name].resolve(mode)
    if token_name in STATIC_TOKENS:
        return STATIC_TOKENS[token_name]
    raise KeyError(f"Unknown theme token: {token_name}")


def get_all_token_names() -> tuple[str, ...]:
    """Return every exported token name in a stable order."""

    return tuple((*TOKENS.keys(), *STATIC_TOKENS.keys()))


__all__ = ["STATIC_TOKENS", "TOKENS", "TokenValue", "get_all_token_names", "get_token_value"]
