from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_PY = ROOT / "desktop_app" / "ui" / "bridge.py"
BRIDGE_JS = ROOT / "desktop_app" / "assets" / "js" / "bridge.js"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
WEB_SHELL_PY = ROOT / "desktop_app" / "ui" / "web_shell.py"


def _extract_python_bridge_methods() -> set[str]:
    text = BRIDGE_PY.read_text(encoding="utf-8")
    return set(re.findall(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text))


def test_runtime_bridge_covers_current_primary_pages():
    methods = _extract_python_bridge_methods()
    expected = {
        "listAccounts",
        "listGroups",
        "listDevices",
        "listTasks",
        "listProviders",
        "listAssets",
        "listAssetsByType",
        "getAssetStats",
        "getAssetVideoPoster",
        "getAssetTextPreview",
        "getDashboardStats",
        "getAllSettings",
        "getTheme",
        "getAppVersion",
        "getLicenseStatus",
        "checkForUpdate",
    }
    missing = expected - methods
    assert not missing, f"Bridge missing runtime methods: {sorted(missing)}"


def test_bridge_stub_covers_current_primary_pages():
    text = BRIDGE_JS.read_text(encoding="utf-8")
    expected = [
        "listAccounts:",
        "listGroups:",
        "listDevices:",
        "listTasks:",
        "listProviders:",
        "listAssets:",
        "listAssetsByType:",
        "getAssetStats:",
        "getAssetVideoPoster:",
        "getAssetTextPreview:",
        "getDashboardStats:",
        "getAllSettings:",
        "getTheme:",
        "getAppVersion:",
        "getLicenseStatus:",
        "checkForUpdate:",
    ]
    missing = [method for method in expected if method not in text]
    assert not missing, f"bridge.js stub missing methods: {missing}"


def test_asset_api_exposes_video_poster_and_text_preview_methods():
    text = (ROOT / "desktop_app" / "assets" / "js" / "data.js").read_text(encoding="utf-8")
    assert "videoPoster: function (path)" in text
    assert "return callBackend('getAssetVideoPoster', path || '');" in text
    assert "previewText: function (path, maxChars)" in text
    assert "return callBackend('getAssetTextPreview', path || '', Number(maxChars || 220));" in text


def test_page_loaders_expose_page_audit_registry():
    text = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    assert "window.__pageAudits" in text
    assert "dataSources" in text
    assert "interactions" in text


def test_runtime_bridge_covers_new_persistence_pages():
    methods = _extract_python_bridge_methods()
    expected = {
        "getTrafficAnalysis",
        "getCompetitorAnalysis",
        "getBlueOceanAnalysis",
        "getInteractionAnalysis",
        "listAnalysisSnapshots",
        "createAnalysisSnapshot",
        "listReportRuns",
        "createReportRun",
        "listWorkflowDefinitions",
        "createWorkflowDefinition",
        "listWorkflowRuns",
        "startWorkflowRun",
        "listExperimentProjects",
        "createExperimentProject",
        "listExperimentViews",
        "createExperimentView",
        "listNotifications",
        "listActivityLogs",
        "createActivityLog",
    }
    missing = expected - methods
    assert not missing, f"Bridge missing new persistence methods: {sorted(missing)}"


def test_bridge_stub_covers_new_persistence_pages():
    text = BRIDGE_JS.read_text(encoding="utf-8")
    expected = [
        "getTrafficAnalysis:",
        "getCompetitorAnalysis:",
        "getBlueOceanAnalysis:",
        "getInteractionAnalysis:",
        "listAnalysisSnapshots:",
        "createAnalysisSnapshot:",
        "listReportRuns:",
        "createReportRun:",
        "listWorkflowDefinitions:",
        "createWorkflowDefinition:",
        "listWorkflowRuns:",
        "startWorkflowRun:",
        "listExperimentProjects:",
        "createExperimentProject:",
        "listExperimentViews:",
        "createExperimentView:",
        "listNotifications:",
        "listActivityLogs:",
        "createActivityLog:",
    ]
    missing = [method for method in expected if method not in text]
    assert not missing, f"bridge.js stub missing new persistence methods: {missing}"


def test_video_editor_bridge_and_data_layer_expose_project_actions() -> None:
    methods = _extract_python_bridge_methods()
    assert "listVideoProjects" in methods
    assert "appendAssetsToSequence" in methods
    assert "addAssetsToTimeline" in methods
    assert "reorderVideoClips" in methods
    assert "trimVideoClip" in methods
    assert "deleteVideoClip" in methods
    assert "createVideoSubtitle" in methods
    assert "updateVideoSubtitle" in methods
    assert "deleteVideoSubtitle" in methods
    assert "removeAssetsFromSequence" in methods
    assert "createVideoExport" in methods
    assert "prepareVideoMonitor" in methods
    assert "getVideoMonitorState" in methods
    assert "playVideoMonitor" in methods
    assert "pauseVideoMonitor" in methods
    assert "stopVideoMonitor" in methods
    assert "seekVideoMonitor" in methods
    assert "stepVideoMonitor" in methods

    bridge_text = BRIDGE_JS.read_text(encoding="utf-8")
    assert "listVideoProjects:" in bridge_text
    assert "appendAssetsToSequence:" in bridge_text
    assert "addAssetsToTimeline:" in bridge_text
    assert "reorderVideoClips:" in bridge_text
    assert "trimVideoClip:" in bridge_text
    assert "deleteVideoClip:" in bridge_text
    assert "createVideoSubtitle:" in bridge_text
    assert "updateVideoSubtitle:" in bridge_text
    assert "deleteVideoSubtitle:" in bridge_text
    assert "removeAssetsFromSequence:" in bridge_text
    assert "createVideoExport:" in bridge_text
    assert "prepareVideoMonitor:" in bridge_text
    assert "getVideoMonitorState:" in bridge_text
    assert "playVideoMonitor:" in bridge_text
    assert "pauseVideoMonitor:" in bridge_text
    assert "stopVideoMonitor:" in bridge_text
    assert "seekVideoMonitor:" in bridge_text
    assert "stepVideoMonitor:" in bridge_text

    data_text = (ROOT / "desktop_app" / "assets" / "js" / "data.js").read_text(encoding="utf-8")
    assert "videoProjects:" in data_text
    assert "listVideoProjects: function () { return callCached('videoProjects:list', DEFAULT_TTL, 'listVideoProjects'); }" in data_text
    assert "appendAssetsToSequence: function (data) { return callBackend('appendAssetsToSequence', JSON.stringify(data || {})); }" in data_text
    assert "addAssetsToTimeline: function (data) { return callBackend('addAssetsToTimeline', JSON.stringify(data || {})); }" in data_text
    assert "reorderVideoClips: function (data) { return callBackend('reorderVideoClips', JSON.stringify(data || {})); }" in data_text
    assert "trimVideoClip: function (data) { return callBackend('trimVideoClip', JSON.stringify(data || {})); }" in data_text
    assert "deleteVideoClip: function (data) { return callBackend('deleteVideoClip', JSON.stringify(data || {})); }" in data_text
    assert "createVideoSubtitle: function (data) { return callBackend('createVideoSubtitle', JSON.stringify(data || {})); }" in data_text
    assert "updateVideoSubtitle: function (data) { return callBackend('updateVideoSubtitle', JSON.stringify(data || {})); }" in data_text
    assert "deleteVideoSubtitle: function (data) { return callBackend('deleteVideoSubtitle', JSON.stringify(data || {})); }" in data_text
    assert "removeAssetsFromSequence: function (data) { return callBackend('removeAssetsFromSequence', JSON.stringify(data || {})); }" in data_text
    assert "createVideoExport: function (data) { return callBackend('createVideoExport', JSON.stringify(data || {})); }" in data_text
    assert "prepareVideoMonitor: function (data) { return callBackend('prepareVideoMonitor', JSON.stringify(data || {})); }" in data_text
    assert "getVideoMonitorState: function () { return callBackend('getVideoMonitorState'); }" in data_text
    assert "playVideoMonitor: function () { return callBackend('playVideoMonitor'); }" in data_text
    assert "pauseVideoMonitor: function () { return callBackend('pauseVideoMonitor'); }" in data_text
    assert "stopVideoMonitor: function () { return callBackend('stopVideoMonitor'); }" in data_text
    assert "seekVideoMonitor: function (positionMs) { return callBackend('seekVideoMonitor', Number(positionMs || 0)); }" in data_text
    assert "stepVideoMonitor: function (deltaMs) { return callBackend('stepVideoMonitor', Number(deltaMs || 0)); }" in data_text


def test_video_project_payload_keeps_active_sequence_assets_clips_and_validation() -> None:
    bridge_text = BRIDGE_PY.read_text(encoding="utf-8")
    assert 'payload["active_sequence_clips"]' in bridge_text
    assert 'payload["active_sequence_assets"]' in bridge_text
    assert 'payload["export_validation"]' in bridge_text
    assert 'sequence_payload["subtitles"]' in bridge_text
    assert 'asset_filename' in bridge_text


def test_web_shell_enables_local_media_playback_for_editor_preview() -> None:
    text = WEB_SHELL_PY.read_text(encoding="utf-8")
    assert 'LocalContentCanAccessFileUrls' in text
    assert 'LocalContentCanAccessRemoteUrls' in text
    assert 'PlaybackRequiresUserGesture' in text


def test_bridge_stub_exposes_device_environment_proxy_metadata():
    text = BRIDGE_JS.read_text(encoding="utf-8")
    assert "openDeviceEnvironment:" in text
    assert "browser_proxy" in text
    assert "validation" in text


def test_bridge_and_stub_cover_named_text_export():
    methods = _extract_python_bridge_methods()
    assert "exportNamedTextFile" in methods

    text = BRIDGE_JS.read_text(encoding="utf-8")
    assert "exportNamedTextFile:" in text
