from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_SRC = ROOT / "apps" / "py-runtime" / "src"
PROVIDERS_PAGE = ROOT / "apps" / "desktop" / "src" / "pages" / "providers" / "ProvidersPage.vue"
PROVIDERS_DATA = ROOT / "apps" / "desktop" / "src" / "modules" / "providers" / "useProvidersData.ts"


import sys

if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from api.http.providers.routes import build_providers_router
from bootstrap.container import RuntimeContainer
from bootstrap.settings import RuntimeSettings


class _FakeFacade:
    def __init__(self) -> None:
        self.providers = [
            {
                "id": 1,
                "name": "OpenAI",
                "providerType": "openai",
                "apiBase": "https://api.openai.com/v1",
                "defaultModel": "gpt-4o-mini",
                "temperature": 0.7,
                "maxTokens": 2048,
                "isActive": True,
                "createdAt": "2026-04-01T00:00:00",
            }
        ]
        self.next_id = 2

    def list_providers(self):
        return list(self.providers)

    def create_provider(self, **payload):
        provider = {
            "id": self.next_id,
            "createdAt": "2026-04-01T00:00:00",
            **payload,
        }
        self.next_id += 1
        self.providers.append(provider)
        return provider

    def update_provider(self, provider_id: int, **payload):
        for item in self.providers:
            if item["id"] == provider_id:
                item.update(payload)
                return item
        return None

    def set_active_provider(self, provider_id: int):
        found = None
        for item in self.providers:
            item["isActive"] = item["id"] == provider_id
            if item["isActive"]:
                found = item
        return found

    def delete_provider(self, provider_id: int):
        before = len(self.providers)
        self.providers = [item for item in self.providers if item["id"] != provider_id]
        return len(self.providers) < before

    def test_provider(self, provider_id: int):
        provider = next((item for item in self.providers if item["id"] == provider_id), None)
        if provider is None:
            return {"ok": False, "error": "provider not found"}
        return {
            "ok": True,
            "provider": provider["name"],
            "model": provider["defaultModel"] if "defaultModel" in provider else provider["default_model"],
            "latencyMs": 12,
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
    app = FastAPI()
    app.include_router(build_providers_router(container))
    return TestClient(app, headers={"X-TKOPS-Token": "test"})


def test_providers_api_supports_create_update_enable_delete_and_connection_test() -> None:
    client = _build_client()

    created = client.post(
        "/providers",
        json={
            "name": "Anthropic",
            "providerType": "anthropic",
            "apiBase": "https://api.anthropic.com/v1",
            "defaultModel": "claude-3-5-sonnet-latest",
            "temperature": 0.3,
            "maxTokens": 4096,
            "isActive": False,
        },
    )
    updated = client.put(
        "/providers/2",
        json={
            "name": "Anthropic Pro",
            "providerType": "anthropic",
            "apiBase": "https://api.anthropic.com/v1",
            "defaultModel": "claude-3-5-sonnet-latest",
            "temperature": 0.2,
            "maxTokens": 4096,
            "isActive": False,
        },
    )
    enabled = client.post("/providers/2/activate")
    tested = client.post("/providers/2/test")
    deleted = client.delete("/providers/2")
    missing_delete = client.delete("/providers/999")
    missing_test = client.post("/providers/999/test")

    assert created.status_code == 200
    assert created.json()["data"]["name"] == "Anthropic"
    assert updated.status_code == 200
    assert updated.json()["data"]["name"] == "Anthropic Pro"
    assert enabled.status_code == 200
    assert enabled.json()["data"]["isActive"] is True
    assert tested.status_code == 200
    assert tested.json()["data"]["ok"] is True
    assert deleted.status_code == 200
    assert deleted.json()["data"]["deleted"] is True
    assert missing_delete.status_code == 404
    assert missing_delete.json()["error"]["code"] == "resource.not_found"
    assert missing_test.status_code == 400
    assert missing_test.json()["error"]["code"] == "provider.test_failed"


def test_providers_page_exposes_inline_editing_and_error_feedback() -> None:
    page_text = PROVIDERS_PAGE.read_text(encoding="utf-8")
    data_text = PROVIDERS_DATA.read_text(encoding="utf-8")

    for snippet in [
        "@submit.prevent",
        "新建 Provider",
        "编辑 Provider",
        "测试连接",
        "启用",
        "删除",
        "actionError",
        "actionMessage",
    ]:
        assert snippet in page_text, snippet

    for snippet in [
        "deleteProvider",
        "setActiveProvider",
        "testProviderConnection",
        "saveProvider",
        "prepareCreate",
        "beginEdit",
    ]:
        assert snippet in data_text, snippet
