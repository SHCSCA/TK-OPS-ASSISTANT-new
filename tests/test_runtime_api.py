from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_SRC = ROOT / "apps" / "py-runtime" / "src"

if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from bootstrap.app_factory import build_app
from bootstrap.container import RuntimeContainer
from bootstrap.settings import RuntimeSettings


class _FakeFacade:
    def get_scheduler_overview(self):
        return {
            "generatedAt": "2026-04-01T00:00:00",
            "summary": {
                "total": 2,
                "scheduled": 1,
                "running": 1,
                "failed": 0,
            },
            "windows": {
                "quietHours": "23:00-07:00",
                "timezone": "Asia/Shanghai",
                "defaultWorkflow": "内容创作",
            },
            "items": [
                {
                    "id": 1,
                    "title": "晚高峰评论分流",
                    "taskType": "maintenance",
                    "status": "pending",
                    "priority": "medium",
                    "scheduledAt": "2026-04-01T19:00:00",
                    "accountUsername": "demo",
                    "resultSummary": "等待时间窗触发",
                },
                {
                    "id": 2,
                    "title": "日报汇总",
                    "taskType": "report",
                    "status": "running",
                    "priority": "high",
                    "scheduledAt": "2026-04-01T10:00:00",
                    "accountUsername": None,
                    "resultSummary": "已进入执行队列",
                },
            ],
        }

    def get_copywriter_bootstrap(self):
        return {
            "presets": [{"key": "copywriter", "name": "AI 文案师", "icon": "✍️", "system": "system prompt"}],
            "defaultPreset": "copywriter",
            "activePreset": {"key": "copywriter", "name": "AI 文案师", "icon": "✍️", "system": "system prompt"},
            "providers": [{"id": 1, "name": "OpenAI", "isActive": True, "defaultModel": "gpt-4o-mini"}],
            "activeProvider": {"id": 1, "name": "OpenAI", "providerType": "openai", "defaultModel": "gpt-4o-mini"},
            "usageToday": {"prompt": 20, "completion": 10, "requests": 1},
            "usageStats": {"total": {"prompt": 20, "completion": 10, "requests": 1}},
        }

    def stream_copywriter(self, **_: object):
        yield {"type": "ai.stream.delta", "payload": {"delta": "第一段"}}
        yield {
            "type": "ai.stream.done",
            "payload": {
                "delta": "完成",
                "content": "第一段完成",
                "model": "gpt-4o-mini",
                "provider": "OpenAI",
                "tokens": {"prompt": 20, "completion": 10, "total": 30},
                "elapsedMs": 120,
            },
        }

    def get_license_status(self):
        return {
            "activated": True,
            "machineId": "abc123",
            "machineIdShort": "ABCD-1234-5678-9ABC",
            "compoundId": "1111222233334444:5555666677778888:9999aaaabbbbcccc:ddddeeeeffff0000",
            "tier": "pro",
            "expiry": None,
            "daysRemaining": None,
            "isPermanent": True,
            "error": None,
        }

    def list_accounts(
        self,
        *,
        status: str | None = None,
        query: str | None = None,
        manual_status: str | None = None,
        system_status: str | None = None,
        risk_status: str | None = None,
        include_archived: bool = False,
    ):
        return [
            {
                "id": 1,
                "username": query or "demo",
                "platform": "tiktok",
                "region": "US",
                "status": manual_status or status or "active",
                "manualStatus": manual_status or status or "active",
                "systemStatus": system_status or "reachable",
                "riskStatus": risk_status or "normal",
                "followers": 0,
                "groupId": None,
                "groupName": None,
                "deviceId": None,
                "deviceName": None,
                "cookieStatus": "unknown",
                "lastConnectionStatus": system_status or "reachable",
                "lastConnectionMessage": None,
                "lastConnectionCheckedAt": "2026-04-01T00:00:00",
                "lastLoginCheckStatus": "unknown",
                "lastLoginCheckAt": None,
                "lastLoginCheckMessage": None,
                "archivedAt": "2026-04-01T08:00:00" if include_archived else None,
                "archivedReason": None,
                "createdAt": "2026-04-01T00:00:00",
                "updatedAt": "2026-04-01T00:00:00",
            }
        ]

    def create_account(self, **payload):
        data = {
            "id": 2,
            "username": payload.get("username", "created"),
            "platform": payload.get("platform", "tiktok"),
            "region": payload.get("region", "US"),
            "status": payload.get("status", "active"),
            "followers": int(payload.get("followers", 0) or 0),
            "groupId": None,
            "groupName": None,
            "deviceId": None,
            "deviceName": None,
            "cookieStatus": payload.get("cookie_status") or payload.get("cookieStatus") or "unknown",
            "lastConnectionStatus": "unknown",
            "lastConnectionMessage": None,
            "createdAt": "2026-04-01T00:00:00",
            "updatedAt": "2026-04-01T00:00:00",
        }
        self._created_account = data
        return data

    def update_account(self, account_id: int, **payload):
        if account_id != 2:
            return None
        data = dict(getattr(self, "_created_account", {}))
        data.update(
            {
                "id": account_id,
                "username": payload.get("username", data.get("username", "created")),
                "region": payload.get("region", data.get("region", "US")),
                "status": payload.get("status", data.get("status", "active")),
            }
        )
        self._created_account = data
        return data

    def delete_account(self, account_id: int):
        return account_id == 2

    def test_account_connection(self, account_id: int):
        return {"ok": True, "accountId": account_id, "status": "reachable", "latencyMs": 12}

    def list_providers(self):
        return [{"id": 1, "name": "OpenAI", "isActive": True}]

    def list_tasks(self, *, status: str | None = None, limit: int = 20):
        return [{"id": 1, "title": "seed", "status": status or "pending"}][:limit]

    def list_experiment_projects(self):
        return [
            {
                "id": 1,
                "name": "实验项目 A",
                "goal": "验证创意主视角",
                "status": "active",
                "configJson": "{}",
                "createdAt": "2026-04-08T10:00:00",
                "updatedAt": "2026-04-08T10:05:00",
            },
            {
                "id": 2,
                "name": "实验项目 B",
                "goal": "验证素材钩子组合",
                "status": "draft",
                "configJson": "{}",
                "createdAt": "2026-04-08T09:00:00",
                "updatedAt": "2026-04-08T09:30:00",
            },
        ]

    def list_experiment_views(self, *, project_id: int | None = None):
        rows = [
            {
                "id": 11,
                "experimentProjectId": 1,
                "name": "实验项目 A / 默认视图",
                "layoutJson": "{}",
                "createdAt": "2026-04-08T10:06:00",
                "updatedAt": "2026-04-08T10:06:00",
            },
            {
                "id": 12,
                "experimentProjectId": 2,
                "name": "实验项目 B / 对比视图",
                "layoutJson": "{}",
                "createdAt": "2026-04-08T09:35:00",
                "updatedAt": "2026-04-08T09:35:00",
            },
        ]
        if project_id is None:
            return rows
        return [item for item in rows if item["experimentProjectId"] == project_id]

    def list_activity_logs(self, *, category: str | None = None, limit: int = 20):
        rows = [
            {
                "id": 21,
                "category": "experiment",
                "title": "创意方案 A 已保存",
                "payloadJson": "{}",
                "relatedEntityType": "experiment_project",
                "relatedEntityId": 1,
                "createdAt": "2026-04-08T10:07:00",
            },
            {
                "id": 22,
                "category": "experiment",
                "title": "创意方案 B 已复盘",
                "payloadJson": "{}",
                "relatedEntityType": "experiment_project",
                "relatedEntityId": 2,
                "createdAt": "2026-04-08T09:40:00",
            },
        ]
        if category:
            rows = [item for item in rows if item["category"] == category]
        return rows[:limit]

    def list_workflow_definitions(self):
        return [
            {
                "id": 101,
                "name": "短视频自动化生产",
                "status": "active",
                "description": "用于批量生产内容工厂脚本与剪辑任务。",
                "configJson": "{}",
                "createdAt": "2026-04-08T08:30:00",
                "updatedAt": "2026-04-08T09:10:00",
            },
            {
                "id": 102,
                "name": "播客拆条工厂",
                "status": "draft",
                "description": "用于播客内容提取与字幕生成。",
                "configJson": "{}",
                "createdAt": "2026-04-08T07:10:00",
                "updatedAt": "2026-04-08T07:40:00",
            },
        ]

    def list_workflow_runs(self, *, workflow_definition_id: int | None = None):
        rows = [
            {
                "id": 201,
                "workflowDefinitionId": 101,
                "status": "running",
                "inputJson": "{}",
                "resultJson": None,
                "startedAt": "2026-04-08T09:20:00",
                "finishedAt": None,
                "createdAt": "2026-04-08T09:20:00",
            },
            {
                "id": 202,
                "workflowDefinitionId": 102,
                "status": "failed",
                "inputJson": "{}",
                "resultJson": "{}",
                "startedAt": "2026-04-08T08:00:00",
                "finishedAt": "2026-04-08T08:15:00",
                "createdAt": "2026-04-08T08:00:00",
            },
        ]
        if workflow_definition_id is None:
            return rows
        return [item for item in rows if item["workflowDefinitionId"] == workflow_definition_id]

    def get_settings(self):
        return {"values": {"theme": "light"}, "items": [{"key": "theme", "value": "light"}], "theme": "light", "total": 1}

    def get_dashboard_overview(self, range_key: str = "today"):
        return {
            "generatedAt": "2026-04-01T00:00:00",
            "range": range_key,
            "metrics": [{"key": "accounts", "label": "账号总数", "value": 1, "meta": "活跃 1"}],
            "accountStatus": [{"key": "active", "count": 1}],
            "taskStatus": [{"key": "pending", "count": 1}],
            "regions": [{"key": "US", "count": 1}],
            "recentTasks": [{"id": 1, "title": "seed", "status": "pending"}],
            "trend": [{"label": "近7天", "created": 3, "completed": 2, "failed": 1}],
            "activity": [
                {
                    "title": "任务创建",
                    "entity": "task",
                    "category": "task",
                    "status": "info",
                    "time": "2026-04-01T00:00:00",
                }
            ],
            "systems": [
                {
                    "key": "runtime",
                    "title": "Runtime 状态",
                    "status": "ok",
                    "tone": "success",
                    "summary": "runtime 在线",
                }
            ],
            "activeProvider": {"id": 1, "name": "OpenAI", "providerType": "openai", "defaultModel": "gpt-4o-mini"},
            "settingsSummary": {"theme": "light", "total": 1},
        }

    def list_notifications(self, *, limit: int = 20):
        _ = limit
        return [
            {
                "id": "activity-1",
                "title": "系统摘要已刷新",
                "body": "dashboard 指标已更新",
                "tone": "info",
                "createdAt": "2026-04-01T00:00:00",
                "source": "activity",
                "read": False,
            }
        ]

    def get_app_version(self):
        return {"version": "1.3.1"}

    def check_for_update(self):
        return {
            "hasUpdate": False,
            "state": "latest",
            "current": "1.3.1",
            "latest": "1.3.1",
        }

    def chat_shell_assistant(self, *, message: str, context: dict[str, object], history: list[dict[str, object]]):
        _ = (context, history)
        return {
            "answer": f"收到：{message}",
            "source": "fallback",
            "suggestions": [{"id": "toggle-theme", "label": "切换主题", "action": "toggle_theme"}],
        }


def _build_client() -> TestClient:
    container = RuntimeContainer(
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
    return TestClient(build_app(container), headers={"X-TKOPS-Token": "test"})


def test_runtime_health_and_resources_return_envelopes() -> None:
    client = _build_client()

    health = client.get("/health")
    license_status = client.get("/license/status")
    settings = client.get("/settings")
    accounts = client.get("/accounts")
    providers = client.get("/providers")
    tasks = client.get("/tasks")
    scheduler = client.get("/scheduler")
    overview = client.get("/dashboard/overview?range=7d")
    copywriter = client.get("/copywriter/bootstrap")
    notifications = client.get("/notifications")
    version_current = client.get("/version/current")
    version_check = client.get("/version/check")
    assistant = client.post(
        "/assistant/chat",
        json={
            "message": "切换主题",
            "context": {"routeName": "dashboard"},
            "history": [],
        },
    )

    assert health.status_code == 200
    assert health.json()["ok"] is True
    assert health.json()["data"]["version"] == "test"
    assert health.json()["data"]["environment"] == "test"
    assert health.json()["data"]["logLevel"] == "INFO"
    assert health.json()["data"]["protocol"]["version"] == "2026-04-01"
    assert health.json()["data"]["protocol"]["auth"]["header"] == "X-TKOPS-Token"
    assert health.json()["data"]["protocol"]["auth"]["wsQuery"] == "token"

    assert license_status.json()["data"]["activated"] is True
    assert license_status.json()["data"]["tier"] == "pro"
    assert settings.json()["data"]["theme"] == "light"
    assert accounts.json()["data"]["items"][0]["username"] == "demo"
    assert accounts.json()["data"]["items"][0]["manualStatus"] == "active"
    assert accounts.json()["data"]["items"][0]["systemStatus"] == "reachable"
    assert accounts.json()["data"]["items"][0]["riskStatus"] == "normal"
    assert providers.json()["data"]["items"][0]["name"] == "OpenAI"
    assert tasks.json()["data"]["items"][0]["title"] == "seed"
    assert scheduler.json()["data"]["summary"]["total"] == 2
    assert scheduler.json()["data"]["items"][0]["title"] == "晚高峰评论分流"
    assert overview.json()["data"]["range"] == "7d"
    assert overview.json()["data"]["metrics"][0]["label"] == "账号总数"
    assert overview.json()["data"]["trend"][0]["label"] == "近7天"
    assert overview.json()["data"]["activity"][0]["entity"] == "task"
    assert overview.json()["data"]["systems"][0]["key"] == "runtime"
    assert copywriter.json()["data"]["defaultPreset"] == "copywriter"
    assert copywriter.json()["data"]["usageToday"]["requests"] == 1
    assert notifications.json()["data"][0]["title"] == "系统摘要已刷新"
    assert version_current.json()["data"]["version"] == "1.3.1"
    assert version_check.json()["data"]["state"] == "latest"
    assert assistant.json()["data"]["answer"] == "收到：切换主题"
    assert assistant.json()["data"]["suggestions"][0]["action"] == "toggle_theme"


def test_runtime_assistant_rejects_empty_message() -> None:
    client = _build_client()

    response = client.post(
        "/assistant/chat",
        json={"message": "   ", "context": {}, "history": []},
    )

    assert response.status_code == 200
    assert response.json()["ok"] is False
    assert response.json()["error"]["code"] == "assistant.invalid_message"


def test_dashboard_overview_supports_empty_trend_activity_systems() -> None:
    class _EmptyFacade(_FakeFacade):
        def get_dashboard_overview(self, range_key: str = "today"):
            return {
                "generatedAt": "2026-04-01T00:00:00",
                "range": range_key,
                "metrics": [],
                "accountStatus": [],
                "taskStatus": [],
                "regions": [],
                "recentTasks": [],
                "trend": [],
                "activity": [],
                "systems": [],
                "activeProvider": None,
                "settingsSummary": {"theme": "system", "total": 0},
            }

    container = RuntimeContainer(
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
        legacy_facade=_EmptyFacade(),
        initializer=lambda: None,
    )
    client = TestClient(build_app(container), headers={"X-TKOPS-Token": "test"})

    response = client.get("/dashboard/overview?range=30d")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["range"] == "30d"
    assert payload["trend"] == []
    assert payload["activity"] == []
    assert payload["systems"] == []


def test_runtime_status_websocket_emits_ready_event() -> None:
    client = _build_client()

    with client.websocket_connect("/ws/runtime-status?token=test") as websocket:
        handshake = websocket.receive_json()
        payload = websocket.receive_json()

    assert handshake["type"] == "runtime.handshake"
    assert handshake["payload"]["channel"] == "runtime-status"
    assert handshake["payload"]["protocolVersion"] == "2026-04-01"
    assert handshake["payload"]["auth"]["scheme"] == "session_token"
    assert payload["type"] == "runtime.status"
    assert payload["payload"]["status"] == "ready"
    assert payload["payload"]["version"] == "test"


def test_copywriter_websocket_streams_delta_and_done_events() -> None:
    client = _build_client()

    with client.websocket_connect("/ws/copywriter-stream?token=test") as websocket:
        handshake = websocket.receive_json()
        websocket.send_json({"prompt": "生成一段护肤产品短视频文案", "preset": "copywriter"})
        first = websocket.receive_json()
        second = websocket.receive_json()

    assert handshake["type"] == "runtime.handshake"
    assert handshake["payload"]["channel"] == "copywriter-stream"
    assert first["type"] == "ai.stream.delta"
    assert first["payload"]["delta"] == "第一段"
    assert second["type"] == "ai.stream.done"
    assert second["payload"]["content"] == "第一段完成"


def test_runtime_http_requires_valid_token() -> None:
    container = RuntimeContainer(
        app_version="test",
        db_path=Path("test.db"),
        runtime_settings=RuntimeSettings(
            host="127.0.0.1",
            port=8765,
            session_token="token-required",
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
    client = TestClient(build_app(container))

    response = client.get("/settings")

    assert response.status_code == 401
    assert response.json()["ok"] is False
    assert response.json()["error"]["code"] == "auth.invalid_token"


def test_runtime_preflight_options_bypasses_token_and_returns_cors_headers() -> None:
    client = _build_client()

    response = client.options(
        "/accounts",
        headers={
            "Origin": "http://127.0.0.1:4173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-TKOPS-Token, Content-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:4173"
    allow_headers = response.headers["access-control-allow-headers"].lower()
    assert "x-tkops-token" in allow_headers


def test_runtime_websocket_requires_valid_token() -> None:
    container = RuntimeContainer(
        app_version="test",
        db_path=Path("test.db"),
        runtime_settings=RuntimeSettings(
            host="127.0.0.1",
            port=8765,
            session_token="token-required",
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
    client = TestClient(build_app(container))

    try:
        with client.websocket_connect("/ws/runtime-status") as websocket:
            websocket.receive_json()
    except WebSocketDisconnect as exc:
        assert exc.code == 4401
    else:
        raise AssertionError("Expected websocket auth failure")


def test_runtime_accounts_environment_login_proxy_binding_and_crud_support(monkeypatch) -> None:
    import api.http.accounts.routes as accounts_routes

    class _FakeRepository:
        def reset_session(self) -> None:
            return None

    class _FakeAccountService:
        _bound_device_id = 11
        _devices = {
            11: SimpleNamespace(
                id=11,
                device_code="DEV-US-11",
                name="US Relay 11",
                region="US",
                proxy_ip="10.10.10.11:18080",
                status="healthy",
                proxy_status="online",
                fingerprint_status="ok",
            ),
            12: SimpleNamespace(
                id=12,
                device_code="DEV-DE-12",
                name="DE Relay 12",
                region="DE",
                proxy_ip="10.10.10.12:28080",
                status="warning",
                proxy_status="online",
                fingerprint_status="drifted",
            ),
        }

        def __init__(self, repo: object) -> None:
            self._repo = repo

        @classmethod
        def _current_account(cls) -> SimpleNamespace:
            device = cls._devices.get(cls._bound_device_id)
            return SimpleNamespace(
                id=2,
                username="demo-renamed",
                device_id=cls._bound_device_id,
                device=device,
            )

        def create_account(self, username: str, **payload: object) -> object:
            device = self._devices.get(self.__class__._bound_device_id)
            return SimpleNamespace(
                id=2,
                username=username,
                platform=payload.get("platform", "tiktok"),
                region=payload.get("region", "US"),
                status=payload.get("status", "active"),
                risk_status=payload.get("risk_status", "normal"),
                followers=payload.get("followers", 0),
                group=None,
                device=device,
                group_id=payload.get("group_id"),
                device_id=payload.get("device_id", self.__class__._bound_device_id),
                cookie_status=payload.get("cookie_status", "unknown"),
                cookie_content=payload.get("cookie_content"),
                cookie_updated_at=None,
                isolation_enabled=bool(payload.get("isolation_enabled", False)),
                last_login_at=None,
                last_connection_checked_at=None,
                last_login_check_status="unknown",
                last_login_check_at=None,
                last_login_check_message=None,
                last_connection_status=payload.get("last_connection_status", "unknown"),
                last_connection_message=payload.get("last_connection_message"),
                tags=payload.get("tags"),
                notes=payload.get("notes"),
                archived_at=None,
                archived_reason=None,
                created_at=None,
                updated_at=None,
            )

        def update_account(self, account_id: int, **payload: object) -> object | None:
            if account_id != 2:
                return None
            device = self._devices.get(self.__class__._bound_device_id)
            return SimpleNamespace(
                id=account_id,
                username=payload.get("username", "demo-new"),
                platform=payload.get("platform", "tiktok"),
                region=payload.get("region", "DE"),
                status=payload.get("status", "warming"),
                risk_status=payload.get("risk_status", "watch"),
                followers=payload.get("followers", 0),
                group=None,
                device=device,
                group_id=payload.get("group_id"),
                device_id=payload.get("device_id", self.__class__._bound_device_id),
                cookie_status=payload.get("cookie_status", "unknown"),
                cookie_content=payload.get("cookie_content"),
                cookie_updated_at=None,
                isolation_enabled=bool(payload.get("isolation_enabled", False)),
                last_login_at=None,
                last_connection_checked_at=None,
                last_login_check_status="unknown",
                last_login_check_at=None,
                last_login_check_message=None,
                last_connection_status=payload.get("last_connection_status", "unknown"),
                last_connection_message=payload.get("last_connection_message"),
                tags=payload.get("tags"),
                notes=payload.get("notes"),
                archived_at=None,
                archived_reason=None,
                created_at=None,
                updated_at=None,
            )

        def get_account_detail(self, account_id: int) -> dict[str, object] | None:
            if account_id != 2:
                return None
            return {
                "id": 2,
                "username": "demo-renamed",
                "manualStatus": "warming",
                "systemStatus": "reachable",
                "riskStatus": "watch",
                "activitySummary": [
                    {
                        "id": "activity-1",
                        "title": "账号检测完成",
                        "createdAt": "2026-04-01T12:00:00",
                    }
                ],
            }

        def list_account_activity_summary(
            self,
            account_id: int,
            *,
            limit: int = 5,
            query: str | None = None,
            category: str | None = None,
            severity: str | None = None,
        ) -> list[dict[str, object]]:
            if account_id != 2:
                return []
            base = [
                {
                    "id": 101,
                    "category": "account_tested",
                    "severity": "info",
                    "title": "账号检测完成",
                    "summary": "网络连通性正常",
                    "occurredAt": "2026-04-01T12:00:00",
                },
                {
                    "id": 102,
                    "category": "account_archived",
                    "severity": "warning",
                    "title": "账号已归档",
                    "summary": "账号处于归档状态",
                    "reason": "批量收口",
                    "occurredAt": "2026-04-01T13:00:00",
                },
            ]
            if query:
                lowered = query.lower()
                base = [
                    item
                    for item in base
                    if lowered in f"{item.get('title', '')} {item.get('summary', '')}".lower()
                ]
            if category:
                base = [item for item in base if item.get("category") == category]
            if severity:
                base = [item for item in base if item.get("severity") == severity]
            return base[:limit]

        def preview_account_import(
            self,
            content: str,
            *,
            delimiter: str = ",",
            has_header: bool = True,
        ) -> dict[str, object]:
            _ = (delimiter, has_header)
            if not content.strip():
                raise ValueError("导入内容不能为空")
            return {
                "total": 2,
                "valid": 1,
                "invalid": 1,
                "create": 1,
                "update": 0,
                "items": [
                    {
                        "line": 2,
                        "username": "demo-new",
                        "action": "create",
                        "valid": True,
                        "reason": "账号不存在，将创建新账号",
                        "existingAccountId": None,
                    },
                    {
                        "line": 3,
                        "username": "",
                        "action": "invalid",
                        "valid": False,
                        "reason": "用户名不能为空",
                        "existingAccountId": None,
                    },
                ],
            }

        def apply_account_import(
            self,
            content: str,
            *,
            delimiter: str = ",",
            has_header: bool = True,
            update_existing: bool = False,
        ) -> dict[str, object]:
            _ = (content, delimiter, has_header)
            return {
                "total": 2,
                "created": 1,
                "updated": 1 if update_existing else 0,
                "skipped": 0 if update_existing else 1,
                "invalid": 0,
                "updateExisting": update_existing,
                "items": [
                    {
                        "line": 2,
                        "username": "demo-new",
                        "status": "created",
                        "message": "账号 demo-new 已创建",
                    }
                ],
            }

        def bulk_update_accounts(
            self,
            account_ids: list[int],
            *,
            action: str,
            manual_status: str | None = None,
            risk_status: str | None = None,
            group_id: int | None = None,
            archive_reason: str | None = None,
        ) -> dict[str, object]:
            return {
                "action": action,
                "processed": len(account_ids),
                "accountIds": account_ids,
                "manualStatus": manual_status,
                "riskStatus": risk_status,
                "groupId": group_id,
                "archiveReason": archive_reason,
            }

        def archive_account(self, account_id: int, reason: str | None = None) -> dict[str, object] | None:
            if account_id != 2:
                return None
            return {"accountId": 2, "archived": True, "archiveReason": reason}

        def unarchive_account(self, account_id: int) -> dict[str, object] | None:
            if account_id != 2:
                return None
            return {"accountId": 2, "archived": False}

        def apply_lifecycle_action(
            self,
            account_id: int,
            *,
            action: str,
            reason: str | None = None,
        ) -> dict[str, object] | None:
            if account_id != 2:
                return None
            if action == "suspend":
                return {"accountId": 2, "manualStatus": "suspended"}
            if action == "restore":
                return {"accountId": 2, "manualStatus": "active", "archived": False}
            if action == "archive":
                return {"accountId": 2, "archived": True, "archiveReason": reason}
            if action == "delete":
                return {"accountId": 2, "deleted": True}
            raise ValueError("不支持的生命周期动作")

        def delete_account(self, account_id: int) -> bool:
            return account_id == 2

        def test_account_connection(self, account_id: int) -> dict[str, object]:
            return {"ok": True, "accountId": account_id, "status": "reachable", "latencyMs": 12}

        def get_account(self, account_id: int) -> object | None:
            if account_id != 2:
                return None
            return self.__class__._current_account()

        def list_devices(self, *, status: str | None = None) -> list[object]:
            _ = status
            return list(self.__class__._devices.values())

        def bind_device(self, account_id: int, device_id: int) -> object | None:
            if account_id != 2:
                return None
            if device_id not in self.__class__._devices:
                return None
            self.__class__._bound_device_id = device_id
            return self.__class__._current_account()

        def update_device(self, pk: int, **fields: object) -> object | None:
            target = self.__class__._devices.get(pk)
            if target is None:
                return None
            if "proxy_ip" in fields:
                target.proxy_ip = fields.get("proxy_ip")
            if "region" in fields and fields.get("region") is not None:
                target.region = str(fields.get("region"))
            return target

        def validate_account_login(self, pk: int, *, timeout: float = 10.0) -> dict[str, object]:
            _ = timeout
            if pk != 2:
                raise ValueError("账号不存在")
            return {
                "account_id": 2,
                "username": "demo-renamed",
                "status": "valid",
                "label": "已通过",
                "message": "登录态有效",
                "checked_at": "2026-04-01T13:30:00",
                "platform": "tiktok",
                "target": "www.tiktok.com",
                "http_status": 200,
                "via_proxy": True,
                "cookie_status": "valid",
            }

        def open_account_environment(self, pk: int) -> dict[str, object]:
            if pk != 2:
                raise ValueError("账号不存在")
            return {
                "account_id": 2,
                "account_username": "demo-renamed",
                "device_id": self.__class__._bound_device_id,
                "device_code": "DEV-US-11",
                "name": "US Relay 11",
                "browser_path": "C:/Program Files/Chrome/chrome.exe",
                "profile_dir": "C:/profiles/account-2",
                "extension_dir": "C:/profiles/account-2/ext",
                "extension_name": "TKOPS Login Helper",
                "extension_ready": True,
                "extension_install_required": False,
                "extension_install_hint": "",
                "proxy_server": "127.0.0.1:19080",
                "browser_proxy": "127.0.0.1:19080",
                "upstream_proxy": "10.10.10.11:18080",
                "pid": 4567,
                "url": "https://www.tiktok.com/",
                "cookie_count": 16,
                "validation": {"ok": True, "message": "代理可用", "detail": ""},
            }

    monkeypatch.setattr(accounts_routes, "Repository", _FakeRepository)
    monkeypatch.setattr(accounts_routes, "AccountService", _FakeAccountService)

    client = _build_client()

    create = client.post(
        "/accounts",
        json={
            "username": "demo-new",
            "platform": "tiktok",
            "region": "US",
            "status": "active",
            "followers": 123,
            "cookieStatus": "valid",
        },
    )
    update = client.put(
        "/accounts/2",
        json={
            "username": "demo-renamed",
            "platform": "tiktok",
            "region": "DE",
            "status": "warming",
            "riskStatus": "watch",
        },
    )
    detail = client.get("/accounts/2")
    bulk = client.post(
        "/accounts/bulk",
        json={
            "action": "set_risk_status",
            "accountIds": [2],
            "riskStatus": "watch",
        },
    )
    archive = client.post("/accounts/2/archive", json={"reason": "批量收口"})
    unarchive = client.post("/accounts/2/unarchive")
    activity = client.get("/accounts/2/activity?limit=1")
    filtered_activity = client.get("/accounts/2/activity?limit=5&query=归档&category=account_archived&severity=warning")
    lifecycle_suspend = client.post("/accounts/2/lifecycle", json={"action": "suspend", "reason": "风险隔离"})
    lifecycle_restore = client.post("/accounts/2/lifecycle", json={"action": "restore"})
    import_preview = client.post(
        "/accounts/import/preview",
        json={
            "content": "username,platform\\ndemo-new,tiktok\\n,tiktok",
            "delimiter": ",",
            "hasHeader": True,
        },
    )
    import_apply = client.post(
        "/accounts/import/apply",
        json={
            "content": "username,platform\\ndemo-new,tiktok",
            "delimiter": ",",
            "hasHeader": True,
            "updateExisting": True,
        },
    )
    test_result = client.post("/accounts/2/test")
    open_environment = client.post("/accounts/2/environment/open")
    login_validation = client.post("/accounts/2/login/validate")
    proxy_binding_get = client.get("/accounts/2/proxy-binding")
    proxy_binding_post = client.post(
        "/accounts/2/proxy-binding",
        json={
            "deviceId": 12,
            "proxyIp": "10.10.10.99:39080",
            "region": "de",
            "validateAfterSave": True,
        },
    )
    proxy_binding_bad_device = client.post("/accounts/2/proxy-binding", json={"deviceId": 9999})
    delete = client.delete("/accounts/2")
    lifecycle_delete = client.post("/accounts/2/lifecycle", json={"action": "delete"})

    assert create.status_code == 200
    assert create.json()["data"]["username"] == "demo-new"
    assert create.json()["data"]["riskStatus"] == "normal"
    assert update.status_code == 200
    assert update.json()["data"]["username"] == "demo-renamed"
    assert update.json()["data"]["riskStatus"] == "watch"
    assert detail.status_code == 200
    assert detail.json()["data"]["activitySummary"][0]["title"] == "账号检测完成"
    assert bulk.status_code == 200
    assert bulk.json()["data"]["processed"] == 1
    assert archive.status_code == 200
    assert archive.json()["data"]["archived"] is True
    assert unarchive.status_code == 200
    assert unarchive.json()["data"]["archived"] is False
    assert activity.status_code == 200
    assert activity.json()["data"]["accountId"] == 2
    assert activity.json()["data"]["total"] == 1
    assert activity.json()["data"]["items"][0]["title"] == "账号检测完成"
    assert filtered_activity.status_code == 200
    assert filtered_activity.json()["data"]["total"] == 1
    assert filtered_activity.json()["data"]["items"][0]["title"] == "账号已归档"
    assert filtered_activity.json()["data"]["filters"]["category"] == "account_archived"
    assert filtered_activity.json()["data"]["filters"]["severity"] == "warning"
    assert lifecycle_suspend.status_code == 200
    assert lifecycle_suspend.json()["data"]["manualStatus"] == "suspended"
    assert lifecycle_restore.status_code == 200
    assert lifecycle_restore.json()["data"]["manualStatus"] == "active"
    assert import_preview.status_code == 200
    assert import_preview.json()["data"]["valid"] == 1
    assert import_preview.json()["data"]["invalid"] == 1
    assert import_apply.status_code == 200
    assert import_apply.json()["data"]["created"] == 1
    assert import_apply.json()["data"]["updated"] == 1
    assert import_apply.json()["data"]["updateExisting"] is True
    assert test_result.status_code == 200
    assert test_result.json()["data"]["ok"] is True
    assert open_environment.status_code == 200
    assert open_environment.json()["data"]["accountId"] == 2
    assert open_environment.json()["data"]["pid"] == 4567
    assert login_validation.status_code == 200
    assert login_validation.json()["data"]["status"] == "valid"
    assert login_validation.json()["data"]["viaProxy"] is True
    assert proxy_binding_get.status_code == 200
    assert proxy_binding_get.json()["data"]["boundDeviceId"] == 11
    assert len(proxy_binding_get.json()["data"]["availableDevices"]) == 2
    assert proxy_binding_post.status_code == 200
    assert proxy_binding_post.json()["data"]["boundDeviceId"] == 12
    assert proxy_binding_post.json()["data"]["region"] == "DE"
    assert proxy_binding_post.json()["data"]["validation"]["status"] == "valid"
    assert proxy_binding_bad_device.status_code == 400
    assert proxy_binding_bad_device.json()["ok"] is False
    assert delete.status_code == 200
    assert delete.json()["data"]["deleted"] is True
    assert lifecycle_delete.status_code == 200
    assert lifecycle_delete.json()["data"]["deleted"] is True


def test_runtime_devices_crud_and_actions_support(monkeypatch) -> None:
    import api.http.devices.routes as devices_routes

    class _FakeRepository:
        def reset_session(self) -> None:
            return None

    class _FakeActivityService:
        def __init__(self, repo: object) -> None:
            self._repo = repo

        @staticmethod
        def _load_payload(payload_json: object) -> dict[str, object]:
            return dict(payload_json or {})

        def list_activity_logs(self) -> list[object]:
            return [
                SimpleNamespace(
                    id=901,
                    category="device_inspection",
                    title="设备巡检完成",
                    payload_json={"message": "代理与浏览器环境已完成探测"},
                    created_at="2026-04-06T10:30:00",
                    related_entity_type="device",
                    related_entity_id=11,
                ),
                SimpleNamespace(
                    id=902,
                    category="device_repair",
                    title="设备修复完成",
                    payload_json={"summary": "已重建 profile 并刷新指纹"},
                    created_at="2026-04-06T11:00:00",
                    related_entity_type="device",
                    related_entity_id=11,
                ),
            ]

    class _FakeAccountService:
        _devices = {
            11: SimpleNamespace(
                id=11,
                device_code="DEV-US-11",
                name="US Relay 11",
                proxy_ip="10.10.10.11:18080",
                region="US",
                status="healthy",
                proxy_status="healthy",
                fingerprint_status="ready",
                created_at="2026-04-01T08:00:00",
                updated_at="2026-04-06T10:00:00",
            ),
        }

        def __init__(self, repo: object) -> None:
            self._repo = repo

        def list_devices(self, *, status: str | None = None) -> list[object]:
            rows = list(self.__class__._devices.values())
            if status:
                rows = [item for item in rows if str(getattr(item, "status", "")) == status]
            return rows

        def create_device(self, device_code: str, name: str, **payload: object) -> object:
            created = SimpleNamespace(
                id=12,
                device_code=device_code,
                name=name,
                proxy_ip=payload.get("proxy_ip"),
                region=payload.get("region", "DE"),
                status=payload.get("status", "warning"),
                proxy_status=payload.get("proxy_status", "warning"),
                fingerprint_status=payload.get("fingerprint_status", "warning"),
                created_at="2026-04-06T12:00:00",
                updated_at="2026-04-06T12:00:00",
            )
            self.__class__._devices[12] = created
            return created

        def update_device(self, device_id: int, **payload: object) -> object | None:
            target = self.__class__._devices.get(device_id)
            if target is None:
                return None
            for field, value in payload.items():
              setattr(target, field, value)
            target.updated_at = "2026-04-06T13:00:00"
            return target

        def delete_device(self, device_id: int) -> bool:
            return self.__class__._devices.pop(device_id, None) is not None

        def inspect_device(self, device_id: int) -> dict[str, object]:
            if device_id not in self.__class__._devices:
                raise ValueError("设备不存在")
            return {
                "device_id": device_id,
                "device_code": "DEV-US-11",
                "name": "US Relay 11",
                "ok": True,
                "target": "https://www.tiktok.com/",
                "latency_ms": 18,
                "checked_at": "2026-04-06T10:30:00",
                "message": "代理链路可用",
                "scope": "browser",
                "scope_label": "浏览器环境",
                "status": "healthy",
                "proxy_status": "healthy",
                "fingerprint_status": "ready",
                "bound_accounts": 2,
            }

        def repair_device_environment(self, device_id: int) -> dict[str, object]:
            if device_id not in self.__class__._devices:
                raise ValueError("设备不存在")
            return {
                "device_id": device_id,
                "device_code": "DEV-US-11",
                "status": "healthy",
                "proxy_status": "healthy",
                "profile_dir": "C:/profiles/device-11",
                "actions": ["重建 profile", "刷新指纹"],
                "inspection": self.inspect_device(device_id),
            }

        def open_device_environment(self, device_id: int) -> dict[str, object]:
            if device_id not in self.__class__._devices:
                raise ValueError("设备不存在")
            return {
                "device_id": device_id,
                "device_code": "DEV-US-11",
                "name": "US Relay 11",
                "browser_path": "C:/Program Files/Chrome/chrome.exe",
                "profile_dir": "C:/profiles/device-11",
                "launcher_path": "C:/tkops/browser-launcher.exe",
                "launcher_url": "http://127.0.0.1:4555",
                "configured_proxy": "10.10.10.11:18080",
                "configured_proxy_display": "US relay",
                "upstream_proxy": "10.10.10.11:18080",
                "upstream_transport": "http",
                "browser_proxy": "127.0.0.1:19080",
                "proxy_server": "127.0.0.1:19080",
                "proxy_auth_present": False,
                "validation": {"ok": True, "message": "代理可用", "detail": ""},
                "launch_mode": "managed",
                "pid": 5566,
                "url": "https://www.tiktok.com/",
                "auto_open_delay_ms": 1200,
                "monitor_interval_ms": 5000,
                "proxy_probe_url": "https://www.tiktok.com/",
                "extension_name": "TKOPS Device Helper",
                "extension_ready": True,
                "extension_install_required": False,
                "extension_install_hint": "",
            }

        def get_device(self, device_id: int) -> object | None:
            return self.__class__._devices.get(device_id)

    monkeypatch.setattr(devices_routes, "Repository", _FakeRepository)
    monkeypatch.setattr(devices_routes, "AccountService", _FakeAccountService)
    monkeypatch.setattr(devices_routes, "ActivityService", _FakeActivityService)

    client = _build_client()

    listed = client.get("/devices")
    created = client.post(
        "/devices",
        json={
            "deviceCode": "DEV-DE-12",
            "name": "DE Relay 12",
            "proxyIp": "10.10.10.12:28080",
            "region": "DE",
            "status": "warning",
            "proxyStatus": "warning",
            "fingerprintStatus": "warning",
        },
    )
    updated = client.put(
        "/devices/11",
        json={
            "proxyIp": "10.10.10.99:39080",
            "region": "SG",
            "status": "warning",
        },
    )
    inspected = client.post("/devices/11/inspect")
    repaired = client.post("/devices/11/repair")
    opened = client.post("/devices/11/environment/open")
    logs = client.get("/devices/11/logs?limit=5")
    missing_logs = client.get("/devices/999/logs")
    deleted = client.delete("/devices/12")

    assert listed.status_code == 200
    assert listed.json()["data"]["total"] == 1
    assert listed.json()["data"]["items"][0]["deviceCode"] == "DEV-US-11"
    assert created.status_code == 200
    assert created.json()["data"]["id"] == 12
    assert created.json()["data"]["proxyIp"] == "10.10.10.12:28080"
    assert updated.status_code == 200
    assert updated.json()["data"]["proxyIp"] == "10.10.10.99:39080"
    assert updated.json()["data"]["region"] == "SG"
    assert inspected.status_code == 200
    assert inspected.json()["data"]["ok"] is True
    assert inspected.json()["data"]["boundAccounts"] == 2
    assert repaired.status_code == 200
    assert repaired.json()["data"]["actions"] == ["重建 profile", "刷新指纹"]
    assert repaired.json()["data"]["inspection"]["status"] == "healthy"
    assert opened.status_code == 200
    assert opened.json()["data"]["pid"] == 5566
    assert opened.json()["data"]["extensionReady"] is True
    assert logs.status_code == 200
    assert logs.json()["data"]["total"] == 2
    assert logs.json()["data"]["items"][0]["title"] == "设备巡检完成"
    assert missing_logs.status_code == 404
    assert missing_logs.json()["ok"] is False
    assert deleted.status_code == 200
    assert deleted.json()["data"]["deleted"] is True


def test_runtime_accounts_reject_empty_username_with_chinese_error(monkeypatch) -> None:
    import api.http.accounts.routes as accounts_routes

    class _FakeRepository:
        def reset_session(self) -> None:
            return None

    class _FakeAccountService:
        def __init__(self, repo: object) -> None:
            self._repo = repo

        def create_account(self, username: str, **payload: object) -> object:
            return SimpleNamespace(
                id=2,
                username=username,
                platform=payload.get("platform", "tiktok"),
                region=payload.get("region", "US"),
                status=payload.get("status", "active"),
                followers=payload.get("followers", 0),
                group=None,
                device=None,
                group_id=payload.get("group_id"),
                device_id=payload.get("device_id"),
                cookie_status=payload.get("cookie_status", "unknown"),
                last_connection_status=payload.get("last_connection_status", "unknown"),
                last_connection_message=payload.get("last_connection_message"),
                created_at=None,
                updated_at=None,
            )

    monkeypatch.setattr(accounts_routes, "Repository", _FakeRepository)
    monkeypatch.setattr(accounts_routes, "AccountService", _FakeAccountService)

    client = _build_client()
    response = client.post("/accounts", json={"username": "   "})

    assert response.status_code == 400
    assert response.json()["ok"] is False
    assert response.json()["error"]["message"] == "用户名不能为空"


def test_runtime_accounts_import_rejects_blank_content(monkeypatch) -> None:
    import api.http.accounts.routes as accounts_routes

    class _FakeRepository:
        def reset_session(self) -> None:
            return None

    class _FakeAccountService:
        def __init__(self, repo: object) -> None:
            self._repo = repo

        def preview_account_import(self, content: str, *, delimiter: str = ",", has_header: bool = True) -> dict[str, object]:
            _ = (delimiter, has_header)
            if not content.strip():
                raise ValueError("导入内容不能为空")
            return {"total": 0, "valid": 0, "invalid": 0, "create": 0, "update": 0, "items": []}

    monkeypatch.setattr(accounts_routes, "Repository", _FakeRepository)
    monkeypatch.setattr(accounts_routes, "AccountService", _FakeAccountService)

    client = _build_client()
    response = client.post(
        "/accounts/import/preview",
        json={"content": "   ", "delimiter": ",", "hasHeader": True},
    )

    assert response.status_code == 400
    assert response.json()["ok"] is False
    assert response.json()["error"]["message"] == "导入内容不能为空"


def test_runtime_experiments_and_activity_routes(monkeypatch) -> None:
    import api.http.activity.routes as activity_routes
    import api.http.experiments.routes as experiments_routes

    class _FakeRepository:
        def reset_session(self) -> None:
            return None

    class _FakeAnalyticsService:
        def __init__(self, repo: object) -> None:
            self._repo = repo

        def create_experiment_project(self, name: str, **kwargs: object) -> object:
            return SimpleNamespace(
                id=31,
                name=name,
                goal=kwargs.get("goal"),
                status=kwargs.get("status", "active"),
                config_json=kwargs.get("config_json", "{}"),
                created_at=dt.datetime.fromisoformat("2026-04-08T10:00:00"),
                updated_at=dt.datetime.fromisoformat("2026-04-08T10:05:00"),
            )

        def create_experiment_view(self, experiment_project_id: int, name: str, **kwargs: object) -> object:
            return SimpleNamespace(
                id=41,
                experiment_project_id=experiment_project_id,
                name=name,
                layout_json=kwargs.get("layout_json", "{}"),
                created_at=dt.datetime.fromisoformat("2026-04-08T10:06:00"),
                updated_at=dt.datetime.fromisoformat("2026-04-08T10:06:00"),
            )

    class _FakeActivityService:
        def __init__(self, repo: object) -> None:
            self._repo = repo

        def create_activity_log(self, category: str, title: str, **kwargs: object) -> object:
            return SimpleNamespace(
                id=51,
                category=category,
                title=title,
                payload_json=kwargs.get("payload_json"),
                related_entity_type=kwargs.get("related_entity_type"),
                related_entity_id=kwargs.get("related_entity_id"),
                created_at=dt.datetime.fromisoformat("2026-04-08T10:07:00"),
            )

    monkeypatch.setattr(experiments_routes, "Repository", _FakeRepository)
    monkeypatch.setattr(experiments_routes, "AnalyticsService", _FakeAnalyticsService)
    monkeypatch.setattr(activity_routes, "Repository", _FakeRepository)
    monkeypatch.setattr(activity_routes, "ActivityService", _FakeActivityService)

    client = _build_client()

    listed_projects = client.get("/experiments/projects")
    created_project = client.post(
        "/experiments/projects",
        json={
            "name": "创意方案 A",
            "goal": "验证达人实测与卖点钩子",
            "status": "active",
            "configJson": "{}",
        },
    )
    listed_views = client.get("/experiments/views?projectId=1")
    created_view = client.post(
        "/experiments/views",
        json={
            "experimentProjectId": 31,
            "name": "创意方案 A / 默认视图",
            "layoutJson": "{}",
        },
    )
    listed_logs = client.get("/activity/logs?limit=5&category=experiment")
    created_log = client.post(
        "/activity/logs",
        json={
            "category": "experiment",
            "title": "创意方案 A 已保存",
            "payloadJson": "{}",
            "relatedEntityType": "experiment_project",
            "relatedEntityId": 31,
        },
    )

    assert listed_projects.status_code == 200
    assert listed_projects.json()["data"]["total"] == 2
    assert listed_projects.json()["data"]["items"][0]["name"] == "实验项目 A"
    assert created_project.status_code == 200
    assert created_project.json()["data"]["id"] == 31
    assert created_project.json()["data"]["goal"] == "验证达人实测与卖点钩子"
    assert listed_views.status_code == 200
    assert listed_views.json()["data"]["total"] == 1
    assert listed_views.json()["data"]["items"][0]["experimentProjectId"] == 1
    assert created_view.status_code == 200
    assert created_view.json()["data"]["experimentProjectId"] == 31
    assert listed_logs.status_code == 200
    assert listed_logs.json()["data"]["total"] == 2
    assert listed_logs.json()["data"]["items"][0]["category"] == "experiment"
    assert created_log.status_code == 200
    assert created_log.json()["data"]["relatedEntityType"] == "experiment_project"


def test_runtime_workflow_routes(monkeypatch) -> None:
    import api.http.workflows.routes as workflow_routes

    class _FakeRepository:
        def reset_session(self) -> None:
            return None

    class _FakeWorkflowService:
        def __init__(self, repo: object) -> None:
            self._repo = repo

        def list_workflow_definitions(self) -> list[object]:
            return [
                SimpleNamespace(
                    id=71,
                    name="短视频自动化生产",
                    status="active",
                    description="用于批量生成脚本与剪辑任务。",
                    config_json="{}",
                    created_at=dt.datetime.fromisoformat("2026-04-08T09:00:00"),
                    updated_at=dt.datetime.fromisoformat("2026-04-08T09:10:00"),
                ),
            ]

        def create_workflow_definition(self, name: str, **kwargs: object) -> object:
            return SimpleNamespace(
                id=81,
                name=name,
                status=kwargs.get("status", "draft"),
                description=kwargs.get("description"),
                config_json=kwargs.get("config_json", "{}"),
                created_at=dt.datetime.fromisoformat("2026-04-08T10:00:00"),
                updated_at=dt.datetime.fromisoformat("2026-04-08T10:05:00"),
            )

        def list_workflow_runs(self, workflow_definition_id: int | None = None) -> list[object]:
            rows = [
                SimpleNamespace(
                    id=91,
                    workflow_definition_id=71,
                    status="running",
                    input_json="{}",
                    result_json=None,
                    started_at=dt.datetime.fromisoformat("2026-04-08T10:06:00"),
                    finished_at=None,
                    created_at=dt.datetime.fromisoformat("2026-04-08T10:06:00"),
                ),
                SimpleNamespace(
                    id=92,
                    workflow_definition_id=81,
                    status="failed",
                    input_json="{}",
                    result_json="{}",
                    started_at=dt.datetime.fromisoformat("2026-04-08T10:10:00"),
                    finished_at=dt.datetime.fromisoformat("2026-04-08T10:20:00"),
                    created_at=dt.datetime.fromisoformat("2026-04-08T10:10:00"),
                ),
            ]
            if workflow_definition_id is None:
                return rows
            return [item for item in rows if item.workflow_definition_id == workflow_definition_id]

        def create_workflow_run(self, workflow_definition_id: int, **kwargs: object) -> object:
            return SimpleNamespace(
                id=101,
                workflow_definition_id=workflow_definition_id,
                status=kwargs.get("status", "pending"),
                input_json=kwargs.get("input_json"),
                result_json=kwargs.get("result_json"),
                started_at=None,
                finished_at=None,
                created_at=dt.datetime.fromisoformat("2026-04-08T10:30:00"),
            )

    monkeypatch.setattr(workflow_routes, "Repository", _FakeRepository)
    monkeypatch.setattr(workflow_routes, "WorkflowService", _FakeWorkflowService)

    client = _build_client()

    listed_definitions = client.get("/workflows/definitions")
    created_definition = client.post(
        "/workflows/definitions",
        json={
            "name": "内容工厂工作流 A",
            "status": "active",
            "description": "用于短视频脚本和剪辑批次。",
            "configJson": "{}",
        },
    )
    listed_runs = client.get("/workflows/runs?definitionId=71")
    started_run = client.post(
        "/workflows/runs",
        json={
            "workflowDefinitionId": 81,
            "status": "pending",
            "inputJson": "{}",
            "resultJson": None,
        },
    )

    assert listed_definitions.status_code == 200
    assert listed_definitions.json()["data"]["total"] == 1
    assert listed_definitions.json()["data"]["items"][0]["name"] == "短视频自动化生产"
    assert created_definition.status_code == 200
    assert created_definition.json()["data"]["id"] == 81
    assert created_definition.json()["data"]["status"] == "active"
    assert listed_runs.status_code == 200
    assert listed_runs.json()["data"]["total"] == 1
    assert listed_runs.json()["data"]["items"][0]["workflowDefinitionId"] == 71
    assert started_run.status_code == 200
    assert started_run.json()["data"]["workflowDefinitionId"] == 81


def test_runtime_video_editor_routes(monkeypatch) -> None:
    import api.http.video_editor.routes as video_editor_routes

    class _FakeRepository:
        def __init__(self) -> None:
            self._project = SimpleNamespace(
                id=301,
                name="视频工程 A",
                description="用于视频编辑页验证。",
                active_sequence_id=401,
                meta_json="{}",
                created_at=dt.datetime.fromisoformat("2026-04-08T11:00:00"),
                updated_at=dt.datetime.fromisoformat("2026-04-08T11:05:00"),
            )
            self._sequence = SimpleNamespace(
                id=401,
                project_id=301,
                project=self._project,
                name="主序列",
                duration_ms=6000,
                fps=30.0,
                width=1080,
                height=1920,
                meta_json="{}",
                created_at=dt.datetime.fromisoformat("2026-04-08T11:00:00"),
                updated_at=dt.datetime.fromisoformat("2026-04-08T11:05:00"),
            )
            self._clip = SimpleNamespace(
                id=501,
                sequence_id=401,
                asset_id=601,
                track_type="video",
                track_index=0,
                sort_order=0,
                start_ms=0,
                source_in_ms=0,
                source_out_ms=3000,
                duration_ms=3000,
                speed=1.0,
                volume=1.0,
                meta_json="{}",
                created_at=dt.datetime.fromisoformat("2026-04-08T11:00:00"),
                updated_at=dt.datetime.fromisoformat("2026-04-08T11:05:00"),
            )
            self._subtitle = SimpleNamespace(
                id=551,
                sequence_id=401,
                start_ms=0,
                end_ms=1200,
                text="字幕 A",
                style_json="{}",
                created_at=dt.datetime.fromisoformat("2026-04-08T11:00:00"),
                updated_at=dt.datetime.fromisoformat("2026-04-08T11:05:00"),
            )
            self._export = SimpleNamespace(
                id=701,
                project_id=301,
                sequence_id=401,
                preset="final",
                status="pending",
                output_path="C:/tmp/export.mp4",
                ffmpeg_command=None,
                error_message=None,
                progress=0,
                started_at=None,
                finished_at=None,
                created_at=dt.datetime.fromisoformat("2026-04-08T11:06:00"),
            )
            self._snapshot = SimpleNamespace(
                id=801,
                project_id=301,
                title="快照 A",
                created_at=dt.datetime.fromisoformat("2026-04-08T11:07:00"),
            )

        def reset_session(self) -> None:
            return None

        def list_video_projects(self):
            return [self._project]

        def list_video_sequences(self, project_id: int):
            return [self._sequence] if project_id == 301 else []

        def set_active_video_sequence(self, project_id: int, sequence_id: int):
            self._project.active_sequence_id = sequence_id
            return self._sequence if project_id == 301 else None

        def list_video_clips(self, sequence_id: int):
            return [self._clip] if sequence_id == 401 else []

        def reorder_video_clips(self, sequence_id: int, ordered_ids: list[int]):
            _ = ordered_ids
            return [self._clip] if sequence_id == 401 else []

        def get_by_id(self, model: object, pk: int):
            name = getattr(model, '__name__', '')
            if name == 'VideoClip' and pk == self._clip.id:
                return self._clip
            if name == 'VideoSubtitle' and pk == self._subtitle.id:
                return self._subtitle
            if name == 'VideoExport' and pk == self._export.id:
                return self._export
            return None

        def update(self, item: object, **fields: object):
            for key, value in fields.items():
                setattr(item, key, value)
            return item

        def list_video_subtitles(self, sequence_id: int):
            return [self._subtitle] if sequence_id == 401 else []

        def list_video_exports(self, project_id: int):
            return [self._export] if project_id == 301 else []

        def list_video_snapshots(self, project_id: int):
            return [self._snapshot] if project_id == 301 else []

    class _FakeVideoEditingService:
        def __init__(self, repo: object) -> None:
            self._repo = repo

        def create_project(self, name: str, **_: object):
            return SimpleNamespace(
                id=302,
                name=name,
                description="新工程",
                active_sequence_id=None,
                meta_json="{}",
                created_at=dt.datetime.fromisoformat("2026-04-08T11:08:00"),
                updated_at=dt.datetime.fromisoformat("2026-04-08T11:08:00"),
            )

        def create_sequence(self, project_id: int, name: str, **_: object):
            return SimpleNamespace(
                id=402,
                project_id=project_id,
                project=SimpleNamespace(active_sequence_id=402),
                name=name,
                duration_ms=0,
                fps=30.0,
                width=1080,
                height=1920,
                meta_json="{}",
                created_at=dt.datetime.fromisoformat("2026-04-08T11:09:00"),
                updated_at=dt.datetime.fromisoformat("2026-04-08T11:09:00"),
            )

        def append_assets_to_sequence(self, sequence_id: int, asset_ids: list[int]):
            return [
                SimpleNamespace(
                    id=510,
                    sequence_id=sequence_id,
                    asset_id=asset_ids[0],
                    track_type="video",
                    track_index=0,
                    sort_order=0,
                    start_ms=0,
                    source_in_ms=0,
                    source_out_ms=3000,
                    duration_ms=3000,
                    speed=1.0,
                    volume=1.0,
                    meta_json="{}",
                    created_at=dt.datetime.fromisoformat("2026-04-08T11:10:00"),
                    updated_at=dt.datetime.fromisoformat("2026-04-08T11:10:00"),
                )
            ]

        def update_clip_range(self, clip_id: int, *, source_in_ms: int, source_out_ms: int):
            return SimpleNamespace(
                id=clip_id,
                sequence_id=401,
                asset_id=601,
                track_type="video",
                track_index=0,
                sort_order=0,
                start_ms=0,
                source_in_ms=source_in_ms,
                source_out_ms=source_out_ms,
                duration_ms=source_out_ms - source_in_ms,
                speed=1.0,
                volume=1.0,
                meta_json="{}",
                created_at=dt.datetime.fromisoformat("2026-04-08T11:11:00"),
                updated_at=dt.datetime.fromisoformat("2026-04-08T11:11:00"),
            )

        def delete_clip(self, clip_id: int):
            return clip_id == 501

        def create_subtitle(self, sequence_id: int, *, start_ms: int, end_ms: int, text: str, **_: object):
            return SimpleNamespace(
                id=560,
                sequence_id=sequence_id,
                start_ms=start_ms,
                end_ms=end_ms,
                text=text,
                style_json="{}",
                created_at=dt.datetime.fromisoformat("2026-04-08T11:12:00"),
                updated_at=dt.datetime.fromisoformat("2026-04-08T11:12:00"),
            )

        def update_subtitle(self, subtitle_id: int, **fields: object):
            return SimpleNamespace(
                id=subtitle_id,
                sequence_id=401,
                start_ms=int(fields.get("start_ms", 0) or 0),
                end_ms=int(fields.get("end_ms", 1200) or 1200),
                text=str(fields.get("text", "字幕已更新")),
                style_json="{}",
                created_at=dt.datetime.fromisoformat("2026-04-08T11:13:00"),
                updated_at=dt.datetime.fromisoformat("2026-04-08T11:13:00"),
            )

        def delete_subtitle(self, subtitle_id: int):
            return subtitle_id == 551

        def create_snapshot(self, project_id: int, title: str):
            return SimpleNamespace(
                id=802,
                project_id=project_id,
                title=title,
                created_at=dt.datetime.fromisoformat("2026-04-08T11:14:00"),
            )

        def restore_snapshot(self, snapshot_id: int):
            _ = snapshot_id
            return SimpleNamespace(
                id=301,
                name="视频工程 A",
                description="已恢复",
                active_sequence_id=401,
                meta_json="{}",
                created_at=dt.datetime.fromisoformat("2026-04-08T11:00:00"),
                updated_at=dt.datetime.fromisoformat("2026-04-08T11:15:00"),
            )

    class _FakeVideoExportService:
        def __init__(self, repo: object) -> None:
            self._repo = repo

        def validate_and_create_export(self, project_id: int, sequence_id: int, *, preset: str):
            _ = (project_id, sequence_id, preset)
            return {"ok": True, "export_id": 701}

        def run_export(self, export_id: int):
            return SimpleNamespace(
                id=export_id,
                project_id=301,
                sequence_id=401,
                preset="final",
                status="completed",
                output_path="C:/tmp/export.mp4",
                ffmpeg_command=None,
                error_message=None,
                progress=100,
                started_at=dt.datetime.fromisoformat("2026-04-08T11:16:00"),
                finished_at=dt.datetime.fromisoformat("2026-04-08T11:17:00"),
                created_at=dt.datetime.fromisoformat("2026-04-08T11:16:00"),
            )

    monkeypatch.setattr(video_editor_routes, "Repository", _FakeRepository)
    monkeypatch.setattr(video_editor_routes, "VideoEditingService", _FakeVideoEditingService)
    monkeypatch.setattr(video_editor_routes, "VideoExportService", _FakeVideoExportService)

    client = _build_client()

    listed_projects = client.get("/video-editor/projects")
    created_project = client.post("/video-editor/projects", json={"name": "新工程"})
    listed_sequences = client.get("/video-editor/projects/301/sequences")
    created_sequence = client.post("/video-editor/sequences", json={"projectId": 301, "name": "序列 2"})
    activated_sequence = client.post("/video-editor/sequences/activate", json={"projectId": 301, "sequenceId": 401})
    listed_clips = client.get("/video-editor/sequences/401/clips")
    appended_assets = client.post("/video-editor/sequences/401/assets", json={"assetIds": [601]})
    reordered_clips = client.post("/video-editor/clips/reorder", json={"sequenceId": 401, "clipIds": [501]})
    trimmed_clip = client.post("/video-editor/clips/trim", json={"clipId": 501, "sourceInMs": 120, "sourceOutMs": 2200})
    deleted_clip = client.delete("/video-editor/clips/501")
    listed_subtitles = client.get("/video-editor/sequences/401/subtitles")
    created_subtitle = client.post("/video-editor/subtitles", json={"sequenceId": 401, "startMs": 0, "endMs": 1000, "text": "新字幕"})
    updated_subtitle = client.put("/video-editor/subtitles/551", json={"text": "字幕已更新", "startMs": 0, "endMs": 1200})
    deleted_subtitle = client.delete("/video-editor/subtitles/551")
    listed_exports = client.get("/video-editor/projects/301/exports")
    created_export = client.post("/video-editor/exports", json={"projectId": 301, "sequenceId": 401, "preset": "final"})
    ran_export = client.post("/video-editor/exports/701/run")
    listed_snapshots = client.get("/video-editor/projects/301/snapshots")
    created_snapshot = client.post("/video-editor/snapshots", json={"projectId": 301, "title": "快照 B"})
    restored_snapshot = client.post("/video-editor/snapshots/801/restore")

    assert listed_projects.status_code == 200
    assert listed_projects.json()["data"]["items"][0]["name"] == "视频工程 A"
    assert created_project.status_code == 200
    assert created_project.json()["data"]["id"] == 302
    assert listed_sequences.json()["data"]["items"][0]["isActive"] is True
    assert created_sequence.json()["data"]["name"] == "序列 2"
    assert activated_sequence.json()["data"]["id"] == 401
    assert listed_clips.json()["data"]["items"][0]["assetId"] == 601
    assert appended_assets.json()["data"]["total"] == 1
    assert reordered_clips.json()["data"]["total"] == 1
    assert trimmed_clip.json()["data"]["sourceOutMs"] == 2200
    assert deleted_clip.json()["data"]["deleted"] is True
    assert listed_subtitles.json()["data"]["items"][0]["text"] == "字幕 A"
    assert created_subtitle.json()["data"]["text"] == "新字幕"
    assert updated_subtitle.json()["data"]["text"] == "字幕已更新"
    assert deleted_subtitle.json()["data"]["deleted"] is True
    assert listed_exports.json()["data"]["items"][0]["status"] == "pending"
    assert created_export.json()["data"]["id"] == 701
    assert ran_export.json()["data"]["status"] == "completed"
    assert listed_snapshots.json()["data"]["items"][0]["title"] == "快照 A"
    assert created_snapshot.json()["data"]["title"] == "快照 B"
    assert restored_snapshot.json()["data"]["name"] == "视频工程 A"

