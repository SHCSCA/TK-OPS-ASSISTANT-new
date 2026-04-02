from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_SRC = ROOT / "apps" / "py-runtime" / "src"

if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from api.http.tasks import routes as task_routes
from api.http.scheduler import routes as scheduler_routes
from bootstrap.container import RuntimeContainer
from bootstrap.settings import RuntimeSettings


def _build_container() -> RuntimeContainer:
    class _FakeFacade:
        def get_scheduler_overview(self):
            return {
                "generatedAt": "2026-04-02T00:00:00",
                "summary": {"total": 0, "scheduled": 0, "running": 0, "failed": 0},
                "windows": {
                    "quietHours": "23:00-07:00",
                    "timezone": "Asia/Shanghai",
                    "defaultWorkflow": "内容创作",
                },
                "items": [],
            }

        def list_tasks(self, *, status: str | None = None, limit: int = 20):
            return [{"id": 1, "title": "demo", "status": status or "pending"}][:limit]

    return RuntimeContainer(
        app_version="test",
        db_path=Path("test.db"),
        runtime_settings=RuntimeSettings(
            host="127.0.0.1",
            port=8765,
            session_token="test",
            environment="test",
            data_dir=Path("data"),
            log_dir=Path("logs"),
            log_file=Path("logs/runtime.log"),
            log_level="INFO",
            enable_request_logging=True,
        ),
        legacy_facade=_FakeFacade(),
        initializer=lambda: None,
    )


class _FakeRepository:
    def reset_session(self) -> None:
        return None


def _fake_task(**overrides: object) -> SimpleNamespace:
    values = {
        "id": 1,
        "title": "demo",
        "task_type": "maintenance",
        "priority": "medium",
        "status": "pending",
        "account_id": None,
        "account": None,
        "scheduled_at": None,
        "started_at": None,
        "finished_at": None,
        "result_summary": None,
        "created_at": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_task_routes_support_create_start_and_delete(monkeypatch) -> None:
    created = _fake_task(id=11, title="日报任务")
    started = _fake_task(id=11, title="日报任务", status="running")

    class _FakeTaskService:
        def __init__(self, _repo) -> None:
            pass

        def create_task(self, title: str, **kwargs):
            assert title == "日报任务"
            assert kwargs["task_type"] == "report"
            return created

        def start_task(self, task_id: int):
            return started if task_id == 11 else None

        def delete_task(self, task_id: int):
            return task_id == 11

    monkeypatch.setattr(task_routes, "Repository", _FakeRepository)
    monkeypatch.setattr(task_routes, "TaskService", _FakeTaskService)

    app = FastAPI()
    app.include_router(task_routes.build_tasks_router(_build_container()))
    client = TestClient(app)

    create_response = client.post(
        "/tasks",
        json={"title": "日报任务", "taskType": "report", "priority": "high"},
    )
    start_response = client.post("/tasks/11/start")
    delete_response = client.delete("/tasks/11")

    assert create_response.status_code == 200
    assert create_response.json()["data"]["title"] == "日报任务"
    assert start_response.status_code == 200
    assert start_response.json()["data"]["status"] == "running"
    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["deleted"] is True


def test_scheduler_routes_support_create_toggle_and_delete(monkeypatch) -> None:
    scheduled = _fake_task(
        id=31,
        title="晚高峰评论分流",
        scheduled_at=__import__("datetime").datetime(2026, 4, 2, 19, 0, 0),
    )
    paused = _fake_task(
        id=31,
        title="晚高峰评论分流",
        status="paused",
        scheduled_at=__import__("datetime").datetime(2026, 4, 2, 19, 0, 0),
    )

    class _FakeTaskService:
        def __init__(self, _repo) -> None:
            pass

        def create_task(self, title: str, **kwargs):
            assert title == "晚高峰评论分流"
            assert kwargs["scheduled_at"] is not None
            return scheduled

        def get_task(self, task_id: int):
            return scheduled if task_id == 31 else None

        def update_task(self, task_id: int, **kwargs):
            assert kwargs["status"] == "paused"
            return paused if task_id == 31 else None

        def delete_task(self, task_id: int):
            return task_id == 31

    monkeypatch.setattr(scheduler_routes, "Repository", _FakeRepository)
    monkeypatch.setattr(scheduler_routes, "TaskService", _FakeTaskService)

    app = FastAPI()
    app.include_router(scheduler_routes.build_scheduler_router(_build_container()))
    client = TestClient(app)

    create_response = client.post(
        "/scheduler",
        json={
            "title": "晚高峰评论分流",
            "taskType": "maintenance",
            "priority": "medium",
            "scheduledAt": "2026-04-02T19:00:00",
        },
    )
    toggle_response = client.post("/scheduler/31/toggle")
    delete_response = client.delete("/scheduler/31")

    assert create_response.status_code == 200
    assert create_response.json()["data"]["id"] == 31
    assert toggle_response.status_code == 200
    assert toggle_response.json()["data"]["status"] == "paused"
    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["deleted"] is True
