from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_SRC = ROOT / "apps" / "py-runtime" / "src"

if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from bootstrap.container import RuntimeContainer
from bootstrap.settings import RuntimeSettings
from api.http.settings.routes import build_settings_router


class _SettingsFacade:
    def __init__(self) -> None:
        self._settings: dict[str, str] = {
            "theme": "system",
            "language": "zh-CN",
            "network.proxy_url": "",
            "network.timeout_seconds": "30",
            "network.concurrent_requests": "3",
            "default_market": "CN",
            "default_workflow": "内容创作",
            "onboarding.default_model": "gpt-4o-mini",
            "onboarding.completed": "0",
        }

    def get_license_status(self) -> dict[str, object]:
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

    def get_settings(self) -> dict[str, object]:
        items = [{"key": key, "value": value} for key, value in sorted(self._settings.items())]
        return {
            "values": dict(self._settings),
            "items": items,
            "theme": self._settings.get("theme", "system"),
            "total": len(items),
            "preferences": {
                "theme": self._settings.get("theme", "system"),
                "language": self._settings.get("language", "zh-CN"),
                "proxyUrl": self._settings.get("network.proxy_url", ""),
                "timeoutSeconds": int(self._settings.get("network.timeout_seconds", "30") or 30),
                "concurrency": int(self._settings.get("network.concurrent_requests", "3") or 3),
            },
            "setup": {
                "defaultMarket": self._settings.get("default_market", ""),
                "defaultWorkflow": self._settings.get("default_workflow", ""),
                "defaultModel": self._settings.get("onboarding.default_model", ""),
                "completed": self._settings.get("onboarding.completed", "0") in {"1", "true", "yes", "on"},
            },
        }

    def save_settings(self, payload: dict[str, object]) -> dict[str, object]:
        if "theme" in payload:
            self._settings["theme"] = str(payload["theme"] or "system")
        if "language" in payload:
            self._settings["language"] = str(payload["language"] or "zh-CN")
        if "proxyUrl" in payload:
            self._settings["network.proxy_url"] = str(payload["proxyUrl"] or "")
        if "timeoutSeconds" in payload:
            self._settings["network.timeout_seconds"] = str(int(payload["timeoutSeconds"] or 0))
        if "concurrency" in payload:
            self._settings["network.concurrent_requests"] = str(int(payload["concurrency"] or 0))
        return self.get_settings()

    def save_setup(self, payload: dict[str, object]) -> dict[str, object]:
        if "defaultMarket" in payload:
            self._settings["default_market"] = str(payload["defaultMarket"] or "")
        if "workflow" in payload:
            self._settings["default_workflow"] = str(payload["workflow"] or "")
        if "model" in payload:
            self._settings["onboarding.default_model"] = str(payload["model"] or "")
        self._settings["onboarding.completed"] = "1" if payload.get("completed", True) else "0"
        return self.get_settings()


def _build_client() -> TestClient:
    temp_dir = tempfile.TemporaryDirectory()
    container = RuntimeContainer(
        app_version="test",
        db_path=Path(temp_dir.name) / "tk_ops.db",
        runtime_settings=RuntimeSettings(
            host="127.0.0.1",
            port=8765,
            session_token="test",
            environment="test",
            data_dir=Path(temp_dir.name),
            log_dir=Path(temp_dir.name) / "logs",
            log_file=Path(temp_dir.name) / "logs" / "runtime.log",
            log_level="INFO",
            enable_request_logging=False,
        ),
        legacy_facade=_SettingsFacade(),
        initializer=lambda: None,
    )
    app = FastAPI()
    app.include_router(build_settings_router(container))
    client = TestClient(app)
    client._temp_dir = temp_dir  # type: ignore[attr-defined]
    return client


def _run_isolated_script(script: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temp_dir:
        env = os.environ.copy()
        env["TK_OPS_DATA_DIR"] = temp_dir
        env["TKOPS_DB_PATH"] = str(Path(temp_dir) / "tk_ops.db")
        env["PYTHONPATH"] = str(RUNTIME_SRC) + os.pathsep + env.get("PYTHONPATH", "")
        output = subprocess.check_output(
            [sys.executable, "-c", script],
            cwd=str(ROOT),
            env=env,
            text=True,
        )
    return json.loads(output.strip().splitlines()[-1])


def test_settings_routes_save_preferences_and_return_echo_snapshot() -> None:
    client = _build_client()

    response = client.post(
        "/settings",
        json={
            "theme": "dark",
            "language": "en-US",
            "proxyUrl": "http://127.0.0.1:7890",
            "timeoutSeconds": 12,
            "concurrency": 6,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["preferences"]["theme"] == "dark"
    assert payload["data"]["preferences"]["language"] == "en-US"
    assert payload["data"]["preferences"]["proxyUrl"] == "http://127.0.0.1:7890"
    assert payload["data"]["preferences"]["timeoutSeconds"] == 12
    assert payload["data"]["preferences"]["concurrency"] == 6
    assert payload["data"]["theme"] == "dark"
    assert payload["data"]["total"] >= 5
    client._temp_dir.cleanup()  # type: ignore[attr-defined]


def test_setup_route_saves_onboarding_defaults_and_marks_completed() -> None:
    client = _build_client()

    response = client.post(
        "/settings/setup",
        json={
            "defaultMarket": "US",
            "workflow": "创意工厂流程",
            "model": "gpt-4o-mini",
            "completed": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["setup"]["defaultMarket"] == "US"
    assert payload["data"]["setup"]["defaultWorkflow"] == "创意工厂流程"
    assert payload["data"]["setup"]["defaultModel"] == "gpt-4o-mini"
    assert payload["data"]["setup"]["completed"] is True
    client._temp_dir.cleanup()  # type: ignore[attr-defined]


def test_legacy_facade_persists_settings_and_setup_state() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.repository import Repository
from legacy_adapter.facade import LegacyRuntimeFacade

facade = LegacyRuntimeFacade()
saved_settings = facade.save_settings({
    "theme": "dark",
    "language": "en-US",
    "proxyUrl": "http://127.0.0.1:7890",
    "timeoutSeconds": 18,
    "concurrency": 5,
})
saved_setup = facade.save_setup({
    "defaultMarket": "US",
    "workflow": "创意工厂流程",
    "model": "gpt-4o-mini",
    "completed": True,
})
repo = Repository()
settings = repo.get_all_settings()
print(json.dumps({
    'saved_settings': saved_settings,
    'saved_setup': saved_setup,
    'settings': settings,
}, ensure_ascii=False))
"""
    )

    assert result["settings"]["theme"] == "dark"
    assert result["settings"]["language"] == "en-US"
    assert result["settings"]["network.proxy_url"] == "http://127.0.0.1:7890"
    assert result["settings"]["network.timeout_seconds"] == "18"
    assert result["settings"]["network.concurrent_requests"] == "5"
    assert result["settings"]["default_market"] == "US"
    assert result["settings"]["default_workflow"] == "创意工厂流程"
    assert result["settings"]["onboarding.default_model"] == "gpt-4o-mini"
    assert result["settings"]["onboarding.completed"] == "1"
