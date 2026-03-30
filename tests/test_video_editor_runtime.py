from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
VIDEO_EDITOR_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "video-editor-main.js"
VISUAL_EDITOR_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "visual-editor-main.js"
VISUAL_EDITOR_FACTORY_JS = ROOT / "desktop_app" / "assets" / "js" / "factories" / "visual-editor.js"
VIDEO_BINDINGS_JS = ROOT / "desktop_app" / "assets" / "js" / "bindings" / "video-editor-bindings.js"


def _slice_between(text: str, start_marker: str, end_marker: str) -> str:
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    return text[start:end]


def test_video_editor_loader_reads_real_video_domain_data_sources() -> None:
    text = VIDEO_EDITOR_MAIN_JS.read_text(encoding="utf-8")

    for source in [
        "api.videoProjects.list()",
        "api.videoSequences.list(",
        "api.videoClips.list(",
        "api.videoSubtitles.list(",
        "api.videoExports.list(",
    ]:
        assert source in text, source


def test_video_editor_main_loader_has_valid_javascript_syntax() -> None:
    node = shutil.which("node")
    if not node:
        raise AssertionError("node 不可用，无法校验 video-editor-main.js 语法")

    completed = subprocess.run(
        [node, "--check", str(VIDEO_EDITOR_MAIN_JS)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout


def test_video_editor_loader_uses_local_refresh_instead_of_full_route_rerender() -> None:
    text = VIDEO_EDITOR_MAIN_JS.read_text(encoding="utf-8")

    assert "renderRoute('video-editor')" not in text
    assert "loaders['video-editor']();" not in text
    assert "runtimeSummaryHandlers['video-editor']" in text
    assert "refresh: function ()" in text
    assert "rerender: function ()" in text


def test_visual_editor_is_explicitly_about_cover_cards_templates_and_multi_size_export() -> None:
    factory_text = VISUAL_EDITOR_FACTORY_JS.read_text(encoding="utf-8")
    loader_text = VISUAL_EDITOR_MAIN_JS.read_text(encoding="utf-8")

    for snippet in [
        "封面",
        "图文卡片",
        "模板",
        "多尺寸导出",
    ]:
        assert snippet in factory_text, snippet

    for snippet in [
        "sequence",
        "clip",
        "subtitle",
        "video-editor",
    ]:
        assert snippet not in factory_text, snippet
        assert snippet not in loader_text, snippet


def test_video_editor_refresh_layers_keep_static_data_out_of_sequence_refresh() -> None:
    text = VIDEO_EDITOR_MAIN_JS.read_text(encoding="utf-8")

    assert "var staticContext = null;" in text
    assert "function _loadStaticContext()" in text
    assert "function _loadSequenceContext(baseContext)" in text
    assert "function _loadOutputContext(baseContext)" in text
    assert "function _reloadStaticAndRender()" in text
    assert "function _reloadSequenceAndRender()" in text
    assert "function _reloadOutputAndRender()" in text
    assert "handleDataChanged: function (detail)" in text

    static_block = _slice_between(text, "function _loadStaticContext()", "function _loadSequenceContext(baseContext)")
    sequence_block = _slice_between(text, "function _loadSequenceContext(baseContext)", "function _reloadStaticAndRender()")
    output_block = _slice_between(text, "function _loadOutputContext(baseContext)", "function _composeContext(baseContext, sequenceContext, outputContext)")

    assert "api.assets.list()" in static_block
    assert "api.tasks.list()" in static_block
    assert "api.assets.list()" not in sequence_block
    assert "api.tasks.list()" not in sequence_block
    assert "api.assets.list()" not in output_block
    assert "api.tasks.list()" not in output_block
    assert "refresh: function () { return _scheduleRefresh('timeline'" in text
    assert "refreshTimeline: function () { return _scheduleRefresh('timeline'" in text
    assert "refreshOutputs: function () { return _scheduleRefresh('outputs'" in text
    assert "selectSequence: function (sequenceId)" in text


def test_video_editor_project_change_events_stay_out_of_static_refresh() -> None:
    text = VIDEO_EDITOR_MAIN_JS.read_text(encoding="utf-8")

    tier_block = _slice_between(text, "function _refreshTierForEntity(entity, action)", "function _refreshSignature(detail, tier)")
    project_branch = _slice_between(tier_block, "if (normalized === 'video-project') {", "if (normalized === 'video-asset' || normalized === 'asset' || normalized === 'task')")

    assert "normalized === 'video-project'" in tier_block
    assert "return 'timeline'" in project_branch
    assert "return 'static'" not in project_branch
    assert "refreshStatic: function () { return _scheduleRefresh('static'" in text


def test_video_snapshot_restore_events_force_timeline_refresh() -> None:
    text = VIDEO_EDITOR_MAIN_JS.read_text(encoding="utf-8")

    tier_block = _slice_between(text, "function _refreshTierForEntity(entity", "function _refreshSignature(detail, tier)")

    assert "video-snapshot" in tier_block
    assert "restored" in tier_block
    assert "return 'timeline'" in tier_block
    assert "return 'outputs'" in tier_block
    assert "handleDataChanged: function (detail)" in text


def test_video_editor_data_changed_handler_is_used_by_global_page_loader() -> None:
    text = PAGE_LOADERS_JS.read_text(encoding="utf-8")

    assert "currentRoute === 'video-editor'" in text
    assert "var detail = event && event.detail ? event.detail : {};" in text
    assert "window.__videoEditorPageMain.handleDataChanged(detail);" in text
    assert text.index("currentRoute === 'video-editor'") < text.index("loaders[currentRoute]();")
    assert "data:changed" in text


def test_video_editor_actions_are_split_by_refresh_tier() -> None:
    text = VIDEO_BINDINGS_JS.read_text(encoding="utf-8")

    for snippet in [
        "_refresh('timeline', { entity: 'video-subtitle', action: 'created' })",
        "_refresh('timeline', { entity: 'video-sequence', action: 'activated' })",
        "_refresh('timeline', { entity: 'video-clip', edge: edge, action: 'trimmed' })",
        "_refresh('timeline', { entity: 'video-clip', direction: direction, action: 'moved' })",
        "_refresh('timeline', { entity: 'video-clip', action: 'deleted' })",
        "_refresh('timeline', { entity: 'video-subtitle', action: 'updated' })",
        "_refresh('timeline', { entity: 'video-subtitle', action: 'deleted' })",
        "_refresh('timeline', { entity: 'video-clip', action: 'imported' })",
        "_refresh('outputs', { entity: 'video-export', action: 'created' })",
        "_refresh('outputs', { entity: 'video-export', preset: preset || 'final', action: 'finished' })",
        "_refresh('outputs', { entity: 'video-snapshot', action: 'created' })",
    ]:
        assert snippet in text, snippet

    assert "_refresh('static'" not in text
    assert text.count("_refresh('timeline'") >= 8
    assert text.count("_refresh('outputs'") >= 3


def test_video_editor_double_click_append_uses_scheduled_timeline_refresh() -> None:
    text = VIDEO_EDITOR_MAIN_JS.read_text(encoding="utf-8")

    bind_asset_grid_block = _slice_between(text, "function _bindAssetGrid(assets, sequence)", "function _renderAssetGrid(assets, sequence)")

    assert "thumb.addEventListener('dblclick'" in bind_asset_grid_block
    assert "_reloadSequenceAndRender()" not in bind_asset_grid_block
    assert "_scheduleRefresh('timeline', { entity: 'video-clip', action: 'double-click-append'" in bind_asset_grid_block
