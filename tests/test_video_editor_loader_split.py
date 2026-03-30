from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_SHELL = ROOT / "desktop_app" / "assets" / "app_shell.html"
ROUTES = ROOT / "desktop_app" / "assets" / "js" / "routes.js"
PAGE_LOADERS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"


def test_video_editor_route_no_longer_hides_sidebar_and_detail_panel() -> None:
    text = ROUTES.read_text(encoding="utf-8")
    assert "'video-editor': makeContentWorkbenchRoute({" in text
    assert "hideWorkbenchSidebar: true" not in text
    assert "hideDetailPanel: true" not in text


def test_video_editor_loader_is_moved_to_dedicated_module() -> None:
    html = APP_SHELL.read_text(encoding="utf-8")
    root = PAGE_LOADERS.read_text(encoding="utf-8")
    assert './js/page-loaders/video-editor-main.js' in html
    assert "loaders['video-editor']" not in root


def test_video_editor_no_longer_depends_on_missing_bind_asset_thumbs() -> None:
    root = PAGE_LOADERS.read_text(encoding="utf-8")
    assert "_bindAssetThumbs(assets)" not in root
