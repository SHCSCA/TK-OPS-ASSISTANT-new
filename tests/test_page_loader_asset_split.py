from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_SHELL_HTML = ROOT / "desktop_app" / "assets" / "app_shell.html"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
ASSET_CENTER_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "asset-center-main.js"


def test_asset_center_loader_script_is_registered() -> None:
    html = APP_SHELL_HTML.read_text(encoding="utf-8")

    assert './js/page-loaders.js' in html
    assert './js/page-loaders/asset-center-main.js' in html


def test_asset_center_logic_is_split_from_page_loaders() -> None:
    page_loaders = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    asset_main = ASSET_CENTER_MAIN_JS.read_text(encoding="utf-8")

    assert "'asset-center': function (payload)" in page_loaders
    assert 'window.__pageLoaderShared' in page_loaders
    assert "loaders['asset-center'] = function ()" in asset_main
    assert '_renderAssetDetail' in asset_main
    assert '_buildAssetThumb' in asset_main
    assert 'window.__assetCenterPageMain' in asset_main


def test_asset_center_grid_does_not_request_video_poster_generation_on_route_load() -> None:
    asset_main = ASSET_CENTER_MAIN_JS.read_text(encoding="utf-8")

    assert "api.assets.videoPoster(" not in asset_main
    assert "_requestVideoPoster(" not in asset_main
