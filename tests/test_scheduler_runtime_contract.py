from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTES_TS = ROOT / "apps" / "desktop" / "src" / "app" / "router" / "routes.ts"
SIDEBAR_VUE = ROOT / "apps" / "desktop" / "src" / "layouts" / "Sidebar.vue"
RUNTIME_API_TS = ROOT / "apps" / "desktop" / "src" / "modules" / "runtime" / "runtimeApi.ts"
RUNTIME_TYPES_TS = ROOT / "apps" / "desktop" / "src" / "modules" / "runtime" / "types.ts"
APP_FACTORY_PY = ROOT / "apps" / "py-runtime" / "src" / "bootstrap" / "app_factory.py"
SCHEDULER_ROUTE_PY = ROOT / "apps" / "py-runtime" / "src" / "api" / "http" / "scheduler" / "routes.py"
DEV_SCRIPT = ROOT / "scripts" / "dev.ps1"
BUILD_DESKTOP_SCRIPT = ROOT / "scripts" / "build-desktop.ps1"
BUILD_RUNTIME_SCRIPT = ROOT / "scripts" / "build-runtime.ps1"


def test_new_desktop_routes_cover_scheduler_page() -> None:
    text = ROUTES_TS.read_text(encoding="utf-8")

    assert "path: '/scheduler'" in text
    assert "name: 'scheduler'" in text


def test_sidebar_exposes_scheduler_navigation_entry() -> None:
    text = SIDEBAR_VUE.read_text(encoding="utf-8")

    assert "'/scheduler'" in text


def test_runtime_api_and_types_expose_scheduler_overview() -> None:
    api_text = RUNTIME_API_TS.read_text(encoding="utf-8")
    types_text = RUNTIME_TYPES_TS.read_text(encoding="utf-8")

    assert "getSchedulerOverview(): Promise<SchedulerOverview>" in api_text
    assert "return httpClient.get('/scheduler');" in api_text
    assert "export interface SchedulerOverview" in types_text
    assert "export interface SchedulerTaskItem" in types_text


def test_runtime_app_factory_registers_scheduler_router() -> None:
    text = APP_FACTORY_PY.read_text(encoding="utf-8")

    assert "build_scheduler_router" in text
    assert "app.include_router(build_scheduler_router(container))" in text
    assert SCHEDULER_ROUTE_PY.exists()


def test_new_architecture_scripts_are_no_longer_placeholder_text() -> None:
    dev_text = DEV_SCRIPT.read_text(encoding="utf-8")
    desktop_text = BUILD_DESKTOP_SCRIPT.read_text(encoding="utf-8")
    runtime_text = BUILD_RUNTIME_SCRIPT.read_text(encoding="utf-8")

    assert "占位" not in dev_text
    assert "apps\\desktop" in dev_text
    assert "apps\\py-runtime" in dev_text
    assert "占位" not in desktop_text
    assert "apps\\desktop" in desktop_text
    assert "smoke-tauri-runtime.ps1" in desktop_text
    assert "占位" not in runtime_text
    assert "apps\\py-runtime" in runtime_text
