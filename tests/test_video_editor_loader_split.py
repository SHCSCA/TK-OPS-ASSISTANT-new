from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_SHELL = ROOT / "desktop_app" / "assets" / "app_shell.html"
ROUTES = ROOT / "desktop_app" / "assets" / "js" / "routes.js"
PAGE_LOADERS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
VIDEO_EDITOR_MAIN = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "video-editor-main.js"


def _slice_between(text: str, start_marker: str, end_marker: str) -> str:
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    return text[start:end]


def _video_editor_route_block() -> str:
    text = ROUTES.read_text(encoding="utf-8")
    if "'video-editor': makeVideoEditorRoute()," in text:
        return _slice_between(
            text,
            "'video-editor': makeVideoEditorRoute(),",
            "    'traffic-board':",
        )
    return _slice_between(
        text,
        "'video-editor': makeContentWorkbenchRoute({",
        "    'traffic-board':",
    )


def _video_editor_loader_text() -> str:
    if VIDEO_EDITOR_MAIN.exists():
        return VIDEO_EDITOR_MAIN.read_text(encoding="utf-8")
    return _slice_between(
        PAGE_LOADERS.read_text(encoding="utf-8"),
        "    loaders['video-editor'] = function () {",
        "    loaders['creative-workshop'] = function () {",
    )


def test_video_editor_route_no_longer_hides_sidebar_and_detail_panel() -> None:
    text = _video_editor_route_block()
    assert "'video-editor': makeVideoEditorRoute()," in text
    assert "hideWorkbenchSidebar: true" not in text
    assert "hideDetailPanel: true" not in text


def test_video_editor_loader_is_moved_to_dedicated_module() -> None:
    html = APP_SHELL.read_text(encoding="utf-8")
    root = PAGE_LOADERS.read_text(encoding="utf-8")
    module = VIDEO_EDITOR_MAIN.read_text(encoding="utf-8") if VIDEO_EDITOR_MAIN.exists() else ""
    assert './js/page-loaders/video-editor-main.js' in html
    assert VIDEO_EDITOR_MAIN.exists()
    assert "loaders['video-editor'] = function () {" not in root
    assert "loaders['video-editor'] = function () {" in module


def test_video_editor_no_longer_depends_on_missing_bind_asset_thumbs() -> None:
    assert "_bindAssetThumbs(assets)" not in _video_editor_loader_text()


def test_video_and_visual_editor_factories_are_registered_in_shell() -> None:
    html = APP_SHELL.read_text(encoding="utf-8")
    assert './js/factories/video-editor.js' in html
    assert './js/factories/visual-editor.js' in html


def test_content_factory_keeps_only_aggregate_editor_entrypoints() -> None:
    text = (ROOT / "desktop_app" / "assets" / "js" / "factories" / "content.js").read_text(encoding="utf-8")
    assert "if (config.workbenchType === 'video-editor')" not in text
    assert "if (config.workbenchType === 'visual-editor')" not in text
