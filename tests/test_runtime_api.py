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

    def get_dashboard_overview(self):
        return {
            "generatedAt": "2026-04-01T00:00:00",
            "metrics": [{"key": "accounts", "label": "账号总数", "value": 1, "meta": "活跃 1"}],
            "accountStatus": [{"key": "active", "count": 1}],
            "taskStatus": [{"key": "pending", "count": 1}],
            "regions": [{"key": "US", "count": 1}],
            "recentTasks": [{"id": 1, "title": "seed", "status": "pending"}],
            "activeProvider": {"id": 1, "name": "OpenAI", "providerType": "openai", "defaultModel": "gpt-4o-mini"},
            "settingsSummary": {"theme": "light", "total": 1},
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
    overview = client.get("/dashboard/overview")
    copywriter = client.get("/copywriter/bootstrap")

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
    assert overview.json()["data"]["metrics"][0]["label"] == "账号总数"
    assert copywriter.json()["data"]["defaultPreset"] == "copywriter"
    assert copywriter.json()["data"]["usageToday"]["requests"] == 1


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

        def list_account_activity_summary(self, account_id: int, *, limit: int = 5) -> list[dict[str, object]]:
            if account_id != 2:
                return []
            base = [
                {
                    "id": "activity-1",
                    "title": "账号检测完成",
                    "createdAt": "2026-04-01T12:00:00",
                },
                {
                    "id": "activity-2",
                    "title": "账号已归档",
                    "createdAt": "2026-04-01T13:00:00",
                },
            ]
            return base[:limit]

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
    test_result = client.post("/accounts/2/test")
    delete = client.delete("/accounts/2")

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
    assert test_result.status_code == 200
    assert test_result.json()["data"]["ok"] is True
    assert delete.status_code == 200
    assert delete.json()["data"]["deleted"] is True


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
