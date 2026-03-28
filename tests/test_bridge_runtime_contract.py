from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_PY = ROOT / "desktop_app" / "ui" / "bridge.py"
BRIDGE_JS = ROOT / "desktop_app" / "assets" / "js" / "bridge.js"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"


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
