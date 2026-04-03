from __future__ import annotations

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


def test_runtime_accounts_support_create_update_delete_and_connection_test(monkeypatch) -> None:
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
                risk_status=payload.get("risk_status", "normal"),
                followers=payload.get("followers", 0),
                group=None,
                device=None,
                group_id=payload.get("group_id"),
                device_id=payload.get("device_id"),
                cookie_status=payload.get("cookie_status", "unknown"),
                last_connection_checked_at=None,
                last_login_check_status="unknown",
                last_login_check_at=None,
                last_login_check_message=None,
                last_connection_status=payload.get("last_connection_status", "unknown"),
                last_connection_message=payload.get("last_connection_message"),
                archived_at=None,
                archived_reason=None,
                created_at=None,
                updated_at=None,
            )

        def update_account(self, account_id: int, **payload: object) -> object | None:
            if account_id != 2:
                return None
            return SimpleNamespace(
                id=account_id,
                username=payload.get("username", "demo-new"),
                platform=payload.get("platform", "tiktok"),
                region=payload.get("region", "DE"),
                status=payload.get("status", "warming"),
                risk_status=payload.get("risk_status", "watch"),
                followers=payload.get("followers", 0),
                group=None,
                device=None,
                group_id=payload.get("group_id"),
                device_id=payload.get("device_id"),
                cookie_status=payload.get("cookie_status", "unknown"),
                last_connection_checked_at=None,
                last_login_check_status="unknown",
                last_login_check_at=None,
                last_login_check_message=None,
                last_connection_status=payload.get("last_connection_status", "unknown"),
                last_connection_message=payload.get("last_connection_message"),
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
    assert delete.status_code == 200
    assert delete.json()["data"]["deleted"] is True
    assert lifecycle_delete.status_code == 200
    assert lifecycle_delete.json()["data"]["deleted"] is True


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

