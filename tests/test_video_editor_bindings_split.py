from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_SHELL = ROOT / "desktop_app" / "assets" / "app_shell.html"
BINDINGS_JS = ROOT / "desktop_app" / "assets" / "js" / "bindings.js"
VIDEO_BINDINGS_JS = ROOT / "desktop_app" / "assets" / "js" / "bindings" / "video-editor-bindings.js"
VISUAL_BINDINGS_JS = ROOT / "desktop_app" / "assets" / "js" / "bindings" / "visual-editor-bindings.js"


def test_bindings_js_exposes_module_registry_without_video_or_visual_hardcoding() -> None:
    text = BINDINGS_JS.read_text(encoding="utf-8")

    assert "window.registerBindingModule" in text
    assert "window.__tkopsBindingModules" in text
    assert "tkopsSourceBrowserTabsBound" in text
    assert "video-editor" not in text
    assert "visual-editor" not in text


def test_source_browser_tabs_are_bound_once_per_persistent_tab_node() -> None:
    text = BINDINGS_JS.read_text(encoding="utf-8")

    assert "function bindSourceBrowserTabs()" in text
    assert "tab.dataset.tkopsSourceBrowserTabsBound" in text
    assert "tab.dataset.tkopsSourceBrowserTabsBound = '1'" in text
    assert "if (tab.dataset.tkopsSourceBrowserTabsBound === '1') return;" in text


def test_split_binding_modules_are_registered_in_shell() -> None:
    html = APP_SHELL.read_text(encoding="utf-8")
    assert './js/bindings/video-editor-bindings.js' in html
    assert './js/bindings/visual-editor-bindings.js' in html


def test_split_binding_modules_cover_video_and_visual_editor_routes() -> None:
    video_text = VIDEO_BINDINGS_JS.read_text(encoding="utf-8")
    visual_text = VISUAL_BINDINGS_JS.read_text(encoding="utf-8")

    assert "registerBindingModule('video-editor'" in video_text
    assert "registerBindingModule('visual-editor'" in visual_text
    assert "_refresh('timeline'" in video_text
    assert "_refresh('outputs'" in video_text
    assert "_createQuickTask(" not in video_text
