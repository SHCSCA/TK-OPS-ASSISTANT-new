from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_app_shell_does_not_reference_removed_prototype_stylesheet() -> None:
    html = (ROOT / "desktop_app" / "assets" / "app_shell.html").read_text(encoding="utf-8")

    assert "../../prototype/assets/styles.css" not in html


def test_variables_css_defines_core_theme_tokens() -> None:
    css = (ROOT / "desktop_app" / "assets" / "css" / "variables.css").read_text(encoding="utf-8")

    required_tokens = [
        ":root",
        "--brand-primary:",
        "--surface-primary:",
        "--surface-secondary:",
        "--text-primary:",
        "--text-secondary:",
        "--border-default:",
        "--sidebar-width:",
        "--shadow-lg:",
        "--page-gutter:",
        "--panel-padding:",
        "--content-max-width:",
    ]

    for token in required_tokens:
        assert token in css


def test_core_css_defines_shell_and_component_basics() -> None:
    shell_css = (ROOT / "desktop_app" / "assets" / "css" / "shell.css").read_text(encoding="utf-8")
    component_css = (ROOT / "desktop_app" / "assets" / "css" / "components.css").read_text(encoding="utf-8")
    combined = shell_css + "\n" + component_css

    required_selectors = [
        ".app-shell {",
        ".title-bar {",
        ".sidebar {",
        ".main {",
        ".detail-panel {",
        ".status-bar {",
        ".primary-button {",
        ".secondary-button {",
        ".icon-button {",
        ".page-header {",
        ".panel {",
        ".stat-card {",
        ".search-bar {",
        ".breadcrumbs {",
        ".pill {",
        ".status-chip {",
        ".table-card {",
        ".page-shell {",
        ".page-section {",
        ".panel--subtle {",
    ]

    for selector in required_selectors:
        assert selector in combined


def test_shell_contains_sticky_footer_and_floating_panel_markers() -> None:
    html = (ROOT / "desktop_app" / "assets" / "app_shell.html").read_text(encoding="utf-8")
    shell_css = (ROOT / "desktop_app" / "assets" / "css" / "shell.css").read_text(encoding="utf-8")
    component_css = (ROOT / "desktop_app" / "assets" / "css" / "components.css").read_text(encoding="utf-8")
    combined = html + "\n" + shell_css + "\n" + component_css

    required_shell_markers = [
        'id="notificationPanel"',
        'id="sidebarSummary"',
        '.sidebar__footer {',
        '.sidebar__content {',
        '.notification-panel {',
        '.notification-panel.is-open {',
        '.shell-floating-panel {',
    ]

    for marker in required_shell_markers:
        assert marker in combined


def test_ui_hardening_selectors_exist_for_controls_and_analytics() -> None:
    component_css = (ROOT / "desktop_app" / "assets" / "css" / "components.css").read_text(encoding="utf-8")
    config_css = (ROOT / "desktop_app" / "assets" / "css" / "pages-config.css").read_text(encoding="utf-8")
    analytics_css = (ROOT / "desktop_app" / "assets" / "css" / "pages-analytics.css").read_text(encoding="utf-8")
    shell_css = (ROOT / "desktop_app" / "assets" / "css" / "shell.css").read_text(encoding="utf-8")
    interactions_css = (ROOT / "desktop_app" / "assets" / "css" / "interactions.css").read_text(encoding="utf-8")
    app_shell = (ROOT / "desktop_app" / "assets" / "app_shell.html").read_text(encoding="utf-8")
    combined = "\n".join([component_css, config_css, analytics_css, shell_css, interactions_css, app_shell])

    required_selectors = [
        ".filter-bar {",
        ".pagination {",
        ".pagination__info {",
        ".pagination__actions {",
        ".config-native-select {",
        ".list-footer {",
        ".config-section__footer {",
        ".analytics-chart-card {",
        ".analytics-chart-card__summary {",
        ".analytics-chart-meta {",
        ".analytics-key-takeaway {",
        ".analytics-side-panel {",
        ".analytics-empty-state {",
        ".funnel-step.is-active {",
        ".persona-grid article.is-active {",
        ".toolbar {",
        ".filter-row {",
        ".pill-button {",
        ".mini-list {",
        ".status-summary-panel {",
        'id="statusSummaryToggle"',
    ]

    for selector in required_selectors:
        assert selector in combined
