from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "tasks" / "TasksPage.vue"
SCHEDULER_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "scheduler" / "SchedulerPage.vue"
TASKS_DATA_TS = ROOT / "apps" / "desktop" / "src" / "modules" / "tasks" / "useTasksData.ts"
SCHEDULER_DATA_TS = ROOT / "apps" / "desktop" / "src" / "modules" / "scheduler" / "useSchedulerData.ts"
RUNTIME_API_TS = ROOT / "apps" / "desktop" / "src" / "modules" / "runtime" / "runtimeApi.ts"
RUNTIME_TYPES_TS = ROOT / "apps" / "desktop" / "src" / "modules" / "runtime" / "types.ts"
TASKS_ROUTE_PY = ROOT / "apps" / "py-runtime" / "src" / "api" / "http" / "tasks" / "routes.py"
SCHEDULER_ROUTE_PY = ROOT / "apps" / "py-runtime" / "src" / "api" / "http" / "scheduler" / "routes.py"


def test_runtime_api_exposes_task_and_scheduler_mutations() -> None:
    api_text = RUNTIME_API_TS.read_text(encoding="utf-8")
    types_text = RUNTIME_TYPES_TS.read_text(encoding="utf-8")

    assert "createTask(" in api_text
    assert "startTask(" in api_text
    assert "deleteTask(" in api_text
    assert "createSchedule(" in api_text
    assert "toggleSchedule(" in api_text
    assert "deleteSchedule(" in api_text
    assert "export interface CreateTaskPayload" in types_text
    assert "export interface CreateSchedulePayload" in types_text


def test_tasks_page_and_module_offer_action_closure() -> None:
    page_text = TASKS_PAGE_VUE.read_text(encoding="utf-8")
    module_text = TASKS_DATA_TS.read_text(encoding="utf-8")

    assert "handleCreateTask" in page_text
    assert "handleStartTask" in page_text
    assert "handleDeleteTask" in page_text
    assert "statusFilter" in page_text
    assert "createTask" in module_text
    assert "startTask" in module_text
    assert "deleteTask" in module_text


def test_scheduler_page_and_module_offer_mutations() -> None:
    page_text = SCHEDULER_PAGE_VUE.read_text(encoding="utf-8")
    module_text = SCHEDULER_DATA_TS.read_text(encoding="utf-8")

    assert "handleCreateSchedule" in page_text
    assert "handleToggleSchedule" in page_text
    assert "handleDeleteSchedule" in page_text
    assert "createSchedule" in module_text
    assert "toggleSchedule" in module_text
    assert "deleteSchedule" in module_text


def test_runtime_routes_expose_task_and_scheduler_write_endpoints() -> None:
    tasks_text = TASKS_ROUTE_PY.read_text(encoding="utf-8")
    scheduler_text = SCHEDULER_ROUTE_PY.read_text(encoding="utf-8")

    assert '@router.post("")' in tasks_text
    assert '@router.post("/{task_id}/start")' in tasks_text
    assert '@router.delete("/{task_id}")' in tasks_text
    assert '@router.post("")' in scheduler_text
    assert '@router.post("/{task_id}/toggle")' in scheduler_text
    assert '@router.delete("/{task_id}")' in scheduler_text
