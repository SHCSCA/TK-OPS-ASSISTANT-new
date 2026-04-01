from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_SHELL = ROOT / "desktop_app" / "assets" / "app_shell.html"
ROUTES = ROOT / "desktop_app" / "assets" / "js" / "routes.js"
PAGE_LOADERS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
VIDEO_EDITOR_FACTORY = ROOT / "desktop_app" / "assets" / "js" / "factories" / "video-editor.js"
VISUAL_EDITOR_FACTORY = ROOT / "desktop_app" / "assets" / "js" / "factories" / "visual-editor.js"
SHELL_CSS = ROOT / "desktop_app" / "assets" / "css" / "shell.css"
EDITOR_SHARED = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "editor-shared.js"


# ── Task 1: 当前结构错位与拆分契约 ──────────────────────────────

def test_video_editor_route_no_longer_hides_sidebar_and_detail_panel():
    text = ROUTES.read_text(encoding="utf-8")
    assert "'video-editor': makeVideoEditorRoute()" in text
    assert "'visual-editor': makeVisualEditorRoute()" in text
    assert "hideWorkbenchSidebar: true" not in text
    assert "hideDetailPanel: true" not in text


def test_video_editor_loader_is_moved_to_dedicated_module():
    html = APP_SHELL.read_text(encoding="utf-8")
    root = PAGE_LOADERS.read_text(encoding="utf-8")
    assert "./js/page-loaders/video-editor-main.js" in html
    assert "loaders['video-editor']" not in root


def test_video_editor_no_longer_depends_on_missing_bind_asset_thumbs():
    root = PAGE_LOADERS.read_text(encoding="utf-8")
    assert "_bindAssetThumbs(assets)" not in root


# ── Task 6: 模板工厂拆分 ─────────────────────────────────────────

def test_video_and_visual_editor_factories_are_registered_in_shell():
    html = APP_SHELL.read_text(encoding="utf-8")
    assert "./js/factories/video-editor.js" in html
    assert "./js/factories/visual-editor.js" in html


def test_video_editor_factory_exposes_real_canvas_layout():
    text = VIDEO_EDITOR_FACTORY.read_text(encoding="utf-8")
    assert "window.makeVideoEditorRoute = function makeVideoEditorRoute()" in text
    assert "source-thumb-grid" in text
    assert "source-thumb-grid--video-editor" in text
    assert "video-preview-shell" in text
    assert "video-timeline-board" in text
    assert "workbench-summary-strip" not in text
    assert "video-studio-topbar" not in text
    assert "js-video-monitor-surface" in text
    assert "js-video-monitor-chip" in text
    assert "js-video-project-copy" in text
    assert "js-video-project-meta" in text
    assert "当前序列 #18" not in text
    assert "待导出 7" not in text
    assert "拖到时间轴后才进入可编辑状态" in text
    assert "transport-bar" not in text
    assert "字幕段会按真实时间轴同步到这里。" not in text
    assert "音频素材拖到 A1 后，会在这里形成真实音频片段。" not in text


def test_video_editor_factory_moves_inspector_into_detail_panel():
    text = VIDEO_EDITOR_FACTORY.read_text(encoding="utf-8")
    assert "视频剪辑摘要" not in text
    assert "值班动作" not in text
    assert "detailHtml: '<div class=\"detail-root\"><section class=\"panel video-inspector-panel\"" in text
    assert "video-queue-block" not in text


def test_video_editor_factory_removes_duplicate_left_workbench_tools():
    text = VIDEO_EDITOR_FACTORY.read_text(encoding="utf-8")
    assert "workbench-tool" not in text
    assert "content-workbench-shell content-workbench-shell--main-only" in text


def test_video_editor_factory_exposes_real_asset_library_actions():
    text = VIDEO_EDITOR_FACTORY.read_text(encoding="utf-8")
    assert "js-video-import-asset-center" in text
    assert "js-video-import-external-assets" in text
    assert "source-mini-preview" not in text
    assert "js-video-delete-selected-asset" not in text
    assert "js-video-append-selected-asset" not in text


def test_video_editor_factory_library_defaults_to_empty_state():
    text = VIDEO_EDITOR_FACTORY.read_text(encoding="utf-8")
    assert "当前素材库还是空的" in text
    assert "节日 B-roll_03" not in text


def test_editor_shared_supports_real_media_preview_markup():
    text = EDITOR_SHARED.read_text(encoding="utf-8")
    assert "js-asset-media" in text
    assert "js-asset-text-preview" in text
    assert "source-thumb__preview-label" in text


def test_visual_editor_factory_exposes_dedicated_route_entrypoint():
    text = VISUAL_EDITOR_FACTORY.read_text(encoding="utf-8")
    assert "window.makeVisualEditorRoute = function makeVisualEditorRoute()" in text
    assert "makeContentWorkbenchRoute" in text


def test_video_editor_shell_layout_no_longer_uses_legacy_two_column_override():
    text = SHELL_CSS.read_text(encoding="utf-8")
    assert ".app-shell.route-video-editor" not in text


def test_content_factory_keeps_only_aggregate_editor_entrypoints():
    text = (ROOT / "desktop_app" / "assets" / "js" / "factories" / "content.js").read_text(encoding="utf-8")
    assert "if (config.workbenchType === 'video-editor')" not in text
    assert "if (config.workbenchType === 'visual-editor')" not in text


# ── Task 7: loader / binding 模块拆分 ────────────────────────────

def test_shell_registers_editor_loader_and_binding_modules():
    html = APP_SHELL.read_text(encoding="utf-8")
    assert "./js/bindings/video-editor-bindings.js" in html
    assert "./js/bindings/visual-editor-bindings.js" in html
    assert "./js/page-loaders/editor-shared.js" in html
    assert "./js/page-loaders/video-editor-main.js" in html
    assert "./js/page-loaders/visual-editor-main.js" in html


def test_root_page_loaders_keeps_only_registry_and_shared_exports():
    text = PAGE_LOADERS.read_text(encoding="utf-8")
    assert "window._pageLoaders = loaders;" in text
    assert "window.__pageAudits = pageAudits;" in text
    assert "loaders['video-editor'] = function ()" not in text
    assert "loaders['visual-editor'] = function ()" not in text
