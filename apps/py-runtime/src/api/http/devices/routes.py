from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api.http.common.envelope import err, ok
from bootstrap.container import RuntimeContainer
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService
from desktop_app.services.activity_service import ActivityService


class DeviceCreatePayload(BaseModel):
    device_code: str = Field(min_length=1, max_length=80, alias="deviceCode")
    name: str = Field(min_length=1, max_length=120)
    proxy_ip: str | None = Field(default=None, alias="proxyIp")
    region: str = Field(default="US", max_length=20)
    status: str = Field(default="healthy", max_length=20)
    proxy_status: str | None = Field(default=None, alias="proxyStatus")
    fingerprint_status: str | None = Field(default=None, alias="fingerprintStatus")

    model_config = {"populate_by_name": True}


class DeviceUpdatePayload(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    proxy_ip: str | None = Field(default=None, alias="proxyIp")
    region: str | None = Field(default=None, max_length=20)
    status: str | None = Field(default=None, max_length=20)
    proxy_status: str | None = Field(default=None, alias="proxyStatus")
    fingerprint_status: str | None = Field(default=None, alias="fingerprintStatus")

    model_config = {"populate_by_name": True}


def _not_found(message: str) -> JSONResponse:
    return JSONResponse(status_code=404, content=err("resource.not_found", message))


def _bad_request(message: str) -> JSONResponse:
    return JSONResponse(status_code=400, content=err("validation.invalid_input", message))


def _serialize_device(item: object) -> dict[str, object]:
    return {
        "id": int(getattr(item, "id")),
        "deviceCode": str(getattr(item, "device_code", "") or ""),
        "name": str(getattr(item, "name", "") or ""),
        "proxyIp": getattr(item, "proxy_ip", None),
        "region": str(getattr(item, "region", "") or ""),
        "status": str(getattr(item, "status", "") or ""),
        "proxyStatus": str(getattr(item, "proxy_status", "") or ""),
        "fingerprintStatus": str(getattr(item, "fingerprint_status", "") or ""),
        "createdAt": getattr(item, "created_at", None),
        "updatedAt": getattr(item, "updated_at", None),
    }


def _serialize_inspection_result(result: dict[str, object]) -> dict[str, object]:
    return {
        "deviceId": result.get("device_id"),
        "deviceCode": result.get("device_code"),
        "name": result.get("name"),
        "ok": bool(result.get("ok")),
        "target": result.get("target"),
        "latencyMs": result.get("latency_ms"),
        "checkedAt": result.get("checked_at"),
        "message": result.get("message"),
        "scope": result.get("scope"),
        "scopeLabel": result.get("scope_label"),
        "status": result.get("status"),
        "proxyStatus": result.get("proxy_status"),
        "fingerprintStatus": result.get("fingerprint_status"),
        "boundAccounts": int(result.get("bound_accounts") or 0),
    }


def _serialize_repair_result(result: dict[str, object]) -> dict[str, object]:
    return {
        "deviceId": result.get("device_id"),
        "deviceCode": result.get("device_code"),
        "status": result.get("status"),
        "proxyStatus": result.get("proxy_status"),
        "profileDir": result.get("profile_dir"),
        "actions": list(result.get("actions") or []),
        "inspection": _serialize_inspection_result(dict(result.get("inspection") or {})),
    }


def _serialize_environment_open_result(result: dict[str, object]) -> dict[str, object]:
    validation = dict(result.get("validation") or {})
    return {
        "deviceId": result.get("device_id"),
        "deviceCode": result.get("device_code"),
        "name": result.get("name"),
        "browserPath": result.get("browser_path") or "",
        "profileDir": result.get("profile_dir") or "",
        "launcherPath": result.get("launcher_path") or "",
        "launcherUrl": result.get("launcher_url") or "",
        "configuredProxy": result.get("configured_proxy") or "",
        "configuredProxyDisplay": result.get("configured_proxy_display") or "",
        "upstreamProxy": result.get("upstream_proxy") or "",
        "upstreamTransport": result.get("upstream_transport") or "",
        "browserProxy": result.get("browser_proxy") or "",
        "proxyServer": result.get("proxy_server") or "",
        "proxyAuthPresent": bool(result.get("proxy_auth_present")),
        "validation": {
            "ok": bool(validation.get("ok")),
            "message": str(validation.get("message") or ""),
            "detail": str(validation.get("detail") or ""),
        },
        "launchMode": result.get("launch_mode") or "",
        "pid": int(result.get("pid") or 0),
        "url": result.get("url") or "",
        "autoOpenDelayMs": int(result.get("auto_open_delay_ms") or 0),
        "monitorIntervalMs": int(result.get("monitor_interval_ms") or 0),
        "proxyProbeUrl": result.get("proxy_probe_url") or "",
        "extensionName": result.get("extension_name") or "",
        "extensionReady": bool(result.get("extension_ready")),
        "extensionInstallRequired": bool(result.get("extension_install_required")),
        "extensionInstallHint": result.get("extension_install_hint") or "",
    }


def _serialize_device_log(item: object) -> dict[str, object]:
    payload = ActivityService._load_payload(getattr(item, "payload_json", None))
    return {
        "id": int(getattr(item, "id")),
        "category": str(getattr(item, "category", "") or ""),
        "title": str(getattr(item, "title", "") or ""),
        "message": str(payload.get("message") or payload.get("summary") or "").strip(),
        "payload": payload,
        "createdAt": getattr(item, "created_at", None),
    }


def build_devices_router(container: RuntimeContainer) -> APIRouter:
    _ = container
    router = APIRouter(prefix="/devices", tags=["devices"])

    @router.get("")
    def list_devices(status: str | None = None) -> dict[str, object]:
        repo = Repository()
        try:
            service = AccountService(repo)
            rows = [_serialize_device(item) for item in service.list_devices(status=status)]
            return ok({"items": rows, "total": len(rows)})
        finally:
            repo.reset_session()

    @router.post("", response_model=None)
    def create_device(payload: DeviceCreatePayload):
        repo = Repository()
        try:
            service = AccountService(repo)
            body = payload.model_dump(by_alias=False)
            device_code = str(body.pop("device_code", "")).strip()
            name = str(body.pop("name", "")).strip()
            if not device_code:
                return _bad_request("设备编码不能为空")
            if not name:
                return _bad_request("设备名称不能为空")
            device = service.create_device(device_code, name, **body)
            return ok(_serialize_device(device))
        except ValueError as exc:
            return _bad_request(str(exc))
        finally:
            repo.reset_session()

    @router.put("/{device_id}", response_model=None)
    def update_device(device_id: int, payload: DeviceUpdatePayload):
        repo = Repository()
        try:
            service = AccountService(repo)
            body = payload.model_dump(by_alias=False, exclude_unset=True)
            if not body:
                return _bad_request("请至少提供一个待更新字段")
            device = service.update_device(device_id, **body)
            if device is None:
                return _not_found("设备不存在，无法更新")
            return ok(_serialize_device(device))
        except ValueError as exc:
            return _bad_request(str(exc))
        finally:
            repo.reset_session()

    @router.delete("/{device_id}", response_model=None)
    def delete_device(device_id: int):
        repo = Repository()
        try:
            service = AccountService(repo)
            deleted = service.delete_device(device_id)
            if not deleted:
                return _not_found("设备不存在，无法删除")
            return ok({"deleted": True, "deviceId": device_id})
        finally:
            repo.reset_session()

    @router.post("/{device_id}/inspect", response_model=None)
    def inspect_device(device_id: int):
        repo = Repository()
        try:
            service = AccountService(repo)
            result = service.inspect_device(device_id)
            return ok(_serialize_inspection_result(result))
        except ValueError as exc:
            return _bad_request(str(exc))
        finally:
            repo.reset_session()

    @router.post("/{device_id}/repair", response_model=None)
    def repair_device(device_id: int):
        repo = Repository()
        try:
            service = AccountService(repo)
            result = service.repair_device_environment(device_id)
            return ok(_serialize_repair_result(result))
        except ValueError as exc:
            return _bad_request(str(exc))
        finally:
            repo.reset_session()

    @router.post("/{device_id}/environment/open", response_model=None)
    def open_device_environment(device_id: int):
        repo = Repository()
        try:
            service = AccountService(repo)
            result = service.open_device_environment(device_id)
            return ok(_serialize_environment_open_result(result))
        except ValueError as exc:
            return _bad_request(str(exc))
        finally:
            repo.reset_session()

    @router.get("/{device_id}/logs", response_model=None)
    def get_device_logs(device_id: int, limit: int = 20):
        normalized_limit = max(1, min(int(limit), 100))
        repo = Repository()
        try:
            service = AccountService(repo)
            device = service.get_device(device_id)
            if device is None:
                return _not_found("设备不存在，无法查看日志")
            activity_service = ActivityService(repo)
            rows = []
            for item in activity_service.list_activity_logs():
                if str(getattr(item, "related_entity_type", "") or "") != "device":
                    continue
                if int(getattr(item, "related_entity_id", 0) or 0) != int(device_id):
                    continue
                rows.append(_serialize_device_log(item))
                if len(rows) >= normalized_limit:
                    break
            return ok({"items": rows, "total": len(rows), "limit": normalized_limit})
        finally:
            repo.reset_session()

    return router

