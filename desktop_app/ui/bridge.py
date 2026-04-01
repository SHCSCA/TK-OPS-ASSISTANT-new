"""QWebChannel bridge – exposes Python services to the JS frontend.

Design decisions:
- Every slot returns a JSON envelope: ``{ok, data, error}``.
- ``@_safe`` decorator catches all exceptions → never crashes the bridge.
- ``dataChanged`` signal pushes mutations to JS for reactive UI updates.
"""
from __future__ import annotations

import json
import logging
import threading
import queue
import socket
from datetime import datetime
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QFileDialog

from desktop_app.database.models import (
    Account,
    AIProvider,
    Asset,
    Device,
    Group,
    Task,
    VideoClip,
    VideoSequence,
    VideoSubtitle,
)
from desktop_app.database.repository import Repository
from desktop_app.logging_config import LOG_FILE
from desktop_app.services.account_service import AccountEnvironmentError, AccountService
from desktop_app.services.activity_service import ActivityService
from desktop_app.services.ai_service import AIService
from desktop_app.services.analytics_service import AnalyticsService
from desktop_app.services.asset_service import AssetService
from desktop_app.services.chat_service import ChatService, list_presets, get_preset
from desktop_app.services.dev_seed_service import DevSeedService
from desktop_app.services.license_service import LicenseService
from desktop_app.version import APP_VERSION
from desktop_app.services.report_service import ReportService
from desktop_app.services.task_service import TaskService
from desktop_app.services.updater_service import UpdaterService
from desktop_app.services.usage_tracker import UsageTracker
from desktop_app.services.video_editing_service import VideoEditingService
from desktop_app.services.video_monitor_service import VideoMonitorService
from desktop_app.services.workflow_service import WorkflowService

log = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────

def _to_dict(obj: Any) -> dict:
    """Convert an ORM instance to a plain dict, preserving native types."""
    if obj is None:
        return {}
    d: dict[str, Any] = {}
    for c in obj.__table__.columns:
        v = getattr(obj, c.name, None)
        d[c.name] = str(v) if v is not None else None
    return d


def _ok(data: Any = None) -> str:
    return json.dumps({"ok": True, "data": data}, ensure_ascii=False, default=str)


def _err(msg: str) -> str:
    return json.dumps({"ok": False, "error": msg}, ensure_ascii=False)


def _safe(func):
    """Decorator: catch exceptions and return a JSON error envelope."""
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as exc:
            log.exception("Bridge slot error in %s", func.__name__)
            # Rollback to clear dirty session state
            try:
                self._repo.session.rollback()
            except Exception:
                pass
            return _err(f"{type(exc).__name__}: {exc}")
        finally:
            repo = getattr(self, "_repo", None)
            if repo is not None and hasattr(repo, "reset_session"):
                try:
                    repo.reset_session()
                except Exception:
                    log.exception("Bridge session reset failed after %s", func.__name__)
    wrapper.__name__ = func.__name__
    return wrapper


def _parse_bool(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on", "enabled", "已启用"}


def _parse_datetime(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value

    normalized = str(value).strip()
    if not normalized:
        return None
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(normalized, fmt)
            except ValueError:
                continue
    raise ValueError("时间格式不正确")


def _normalize_account_payload(data: dict[str, Any]) -> dict[str, Any]:
    fields = dict(data or {})

    for key in ("platform", "region", "status", "cookie_status"):
        if key in fields and fields[key] is not None:
            fields[key] = str(fields[key]).strip()

    for key in ("notes", "tags", "last_connection_message", "last_login_check_message"):
        if key in fields:
            text = str(fields[key]).strip() if fields[key] is not None else ""
            fields[key] = text or None

    if "cookie_content" in fields:
        text = str(fields["cookie_content"]).strip() if fields["cookie_content"] is not None else ""
        fields["cookie_content"] = text or None

    for key in ("followers", "group_id", "device_id"):
        if key in fields:
            value = fields[key]
            fields[key] = None if value in (None, "") else int(value)

    if "isolation_enabled" in fields:
        parsed = _parse_bool(fields["isolation_enabled"])
        fields["isolation_enabled"] = bool(parsed) if parsed is not None else False

    for key in ("last_login_at", "last_connection_checked_at", "cookie_updated_at", "last_login_check_at"):
        if key in fields:
            fields[key] = _parse_datetime(fields[key])

    return fields


# ── Bridge ───────────────────────────────────────────

class Bridge(QObject):
    """Exposed to JS via QWebChannel as ``window.backend``."""

    dataChanged = Signal(str)  # JSON: {entity, action, id}

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._repo = Repository()
        self._accounts = AccountService(self._repo)
        self._tasks = TaskService(self._repo)
        self._ai = AIService(self._repo)
        self._analytics = AnalyticsService(self._repo)
        self._assets = AssetService(self._repo)
        self._video_editing = VideoEditingService(self._repo)
        self._video_monitor = VideoMonitorService()
        self._dev_seed = DevSeedService(self._repo)
        self._reports = ReportService(self._repo)
        self._workflows = WorkflowService(self._repo)
        self._activity = ActivityService(self._repo)
        self._updater = UpdaterService()
        self._chat = ChatService(self._repo)
        self._usage = UsageTracker(self._repo)
        self._stream_queue: queue.Queue | None = None
        self._stream_thread: threading.Thread | None = None

    def _emit_change(self, entity: str, action: str, pk: Any = None) -> None:
        self.dataChanged.emit(
            json.dumps({"entity": entity, "action": action, "id": pk}, ensure_ascii=False)
        )

    def _resolve_video_context(
        self, *, project_id: int | None = None, sequence_id: int | None = None
    ) -> tuple[Any, Any]:
        project = None
        sequence = None

        if sequence_id is not None:
            sequence = self._repo.get_by_id(VideoSequence, int(sequence_id))
            if sequence is None:
                raise ValueError("剪辑序列不存在")
            project = self._video_editing.get_project(sequence.project_id)
        elif project_id is not None:
            project = self._video_editing.get_project(int(project_id))

        if project is None:
            projects = list(self._video_editing.list_projects())
            project = projects[0] if projects else None

        if project is None:
            project, sequence = self._video_editing.create_project_with_sequence("视频剪辑工作区", "主序列")
            return project, sequence

        sequences = list(self._video_editing.list_sequences(project.id))
        if sequence is None and project.active_sequence_id:
            sequence = next((item for item in sequences if item.id == project.active_sequence_id), None)
        if sequence is None:
            sequence = sequences[0] if sequences else None
        if sequence is None:
            sequence = self._video_editing.create_sequence(project.id, "主序列")
        if project.active_sequence_id != sequence.id:
            project = self._repo.set_active_video_sequence(project.id, sequence.id) or project
        return project, sequence

    def _serialize_video_asset(self, asset: Any) -> dict[str, Any]:
        payload = _to_dict(asset)
        cached = self._assets.get_video_poster_cached(payload.get("file_path"))
        payload["poster_path"] = cached.get("poster_path", "")
        return payload

    def _serialize_video_clip(self, clip: Any) -> dict[str, Any]:
        payload = _to_dict(clip)
        asset = self._repo.get_by_id(Asset, clip.asset_id) if getattr(clip, "asset_id", None) else None
        if asset is not None:
            payload["asset_filename"] = asset.filename
            payload["asset_type"] = asset.asset_type
            payload["asset_file_path"] = asset.file_path
        else:
            payload["asset_filename"] = ""
            payload["asset_type"] = ""
            payload["asset_file_path"] = ""
        return payload

    def _serialize_video_project(self, project: Any) -> dict[str, Any]:
        sequences = list(self._video_editing.list_sequences(project.id))
        active_sequence = None
        if project.active_sequence_id:
            active_sequence = next((item for item in sequences if item.id == project.active_sequence_id), None)
        if active_sequence is None and sequences:
            active_sequence = sequences[0]

        payload = _to_dict(project)
        payload["sequences"] = []
        payload["active_sequence_clips"] = []
        payload["active_sequence_assets"] = []
        payload["active_sequence_subtitles"] = []
        payload["export_validation"] = {"ok": False, "errors": ["当前还没有可导出的活动序列"]}

        for sequence in sequences:
            self._video_editing.normalize_sequence_clip_assets(sequence.id)
            clips = list(self._video_editing.list_clips(sequence.id))
            assets = [self._serialize_video_asset(asset) for asset in self._video_editing.list_sequence_assets(sequence.id)]
            subtitles = list(self._video_editing.list_subtitles(sequence.id))
            sequence_payload = _to_dict(sequence)
            sequence_payload["clip_count"] = len(clips)
            sequence_payload["clips"] = [self._serialize_video_clip(clip) for clip in clips]
            sequence_payload["asset_count"] = len(assets)
            sequence_payload["assets"] = assets
            sequence_payload["subtitles"] = [_to_dict(item) for item in subtitles]
            payload["sequences"].append(sequence_payload)
            if active_sequence is not None and sequence.id == active_sequence.id:
                payload["active_sequence_clips"] = [self._serialize_video_clip(clip) for clip in clips]
                payload["active_sequence_assets"] = assets
                payload["active_sequence_subtitles"] = [_to_dict(item) for item in subtitles]
                payload["export_validation"] = self._video_editing.validate_export(project.id, sequence.id)

        exports = list(self._video_editing.list_exports(project.id))
        payload["exports"] = [_to_dict(item) for item in exports]
        payload["export_count"] = len(exports)
        return payload

    # ── Account slots ──

    @Slot(result=str)
    @_safe
    def listAccounts(self) -> str:
        return _ok([_to_dict(a) for a in self._accounts.list_accounts()])

    @Slot(str, result=str)
    @_safe
    def getAccount(self, pk_str: str) -> str:
        account = self._accounts.get_account(int(pk_str))
        if account is None:
            return _err("账号不存在")
        return _ok(_to_dict(account))

    @Slot(str, result=str)
    @_safe
    def createAccount(self, payload: str) -> str:
        data = _normalize_account_payload(json.loads(payload))
        username = data.pop("username", "")
        if not username:
            return _err("用户名不能为空")
        account = self._accounts.create_account(username, **data)
        self._emit_change("account", "created", account.id)
        return _ok(_to_dict(account))

    @Slot(int, str, result=str)
    @_safe
    def updateAccount(self, pk: int, payload: str) -> str:
        fields = _normalize_account_payload(json.loads(payload))
        account = self._accounts.update_account(pk, **fields)
        if account is None:
            return _err("账号不存在")
        self._emit_change("account", "updated", pk)
        return _ok(_to_dict(account))

    @Slot(int, result=str)
    @_safe
    def testAccountConnection(self, pk: int) -> str:
        result = self._accounts.test_account_connection(pk)
        self._emit_change("account", "tested", pk)
        return _ok(result)

    @Slot(int, result=str)
    @_safe
    def validateAccountLogin(self, pk: int) -> str:
        result = self._accounts.validate_account_login(pk)
        self._emit_change("account", "validated", pk)
        return _ok(result)

    @Slot(int, result=str)
    @_safe
    def openAccountEnvironment(self, pk: int) -> str:
        account = self._accounts.get_account(pk)
        account_name = account.username if account is not None else str(pk)
        try:
            result = self._accounts.open_account_environment(pk)
        except Exception as exc:
            error_code = exc.code if isinstance(exc, AccountEnvironmentError) else "account_environment_failed"
            self._activity.create_activity_log(
                "account_environment_failed",
                f"打开账号环境失败 / {account_name}",
                payload_json=json.dumps(
                    {
                        "message": str(exc),
                        "error_code": error_code,
                        "account_id": pk,
                        "account_username": account_name,
                    },
                    ensure_ascii=False,
                    default=str,
                ),
                related_entity_type="account",
                related_entity_id=pk,
            )
            self._emit_change("activity_log", "created", pk)
            raise

        self._activity.create_activity_log(
            "account_environment",
            f"打开账号环境 / {result.get('account_username') or pk}",
            payload_json=json.dumps(
                {
                    "message": (
                        f"已启动账号隔离环境，PID {result.get('pid')}，设备 {result.get('device_code')}"
                        + (f"，Cookie {result.get('cookie_count')} 条" if result.get("cookie_count") else "")
                    ),
                    "account_id": result.get("account_id"),
                    "account_username": result.get("account_username"),
                    "device_id": result.get("device_id"),
                    "device_code": result.get("device_code"),
                    "browser_path": result.get("browser_path"),
                    "profile_dir": result.get("profile_dir"),
                    "extension_dir": result.get("extension_dir"),
                    "extension_name": result.get("extension_name"),
                    "extension_ready": result.get("extension_ready"),
                    "extension_install_required": result.get("extension_install_required"),
                    "extension_install_hint": result.get("extension_install_hint"),
                    "launch_mode": result.get("launch_mode"),
                    "proxy_server": result.get("proxy_server"),
                    "browser_proxy": result.get("browser_proxy"),
                    "validation": result.get("validation"),
                    "url": result.get("url"),
                },
                ensure_ascii=False,
                default=str,
            ),
            related_entity_type="account",
            related_entity_id=pk,
        )
        self._emit_change("account", "environment-opened", pk)
        self._emit_change("activity_log", "created", pk)
        return _ok(result)

    @Slot(int, result=str)
    @_safe
    def deleteAccount(self, pk: int) -> str:
        ok = self._accounts.delete_account(pk)
        if not ok:
            return _err("账号不存在")
        self._emit_change("account", "deleted", pk)
        return _ok({"deleted": pk})

    # ── Group slots ──

    @Slot(result=str)
    @_safe
    def listGroups(self) -> str:
        return _ok([_to_dict(g) for g in self._accounts.list_groups()])

    @Slot(str, result=str)
    @_safe
    def createGroup(self, payload: str) -> str:
        data = json.loads(payload)
        name = data.pop("name", "")
        if not name:
            return _err("分组名不能为空")
        group = self._accounts.create_group(name, **data)
        self._emit_change("group", "created", group.id)
        return _ok(_to_dict(group))

    @Slot(int, str, result=str)
    @_safe
    def updateGroup(self, pk: int, payload: str) -> str:
        fields = json.loads(payload)
        group = self._accounts.update_group(pk, **fields)
        if group is None:
            return _err("分组不存在")
        self._emit_change("group", "updated", pk)
        return _ok(_to_dict(group))

    @Slot(int, result=str)
    @_safe
    def deleteGroup(self, pk: int) -> str:
        ok = self._accounts.delete_group(pk)
        if not ok:
            return _err("分组不存在")
        self._emit_change("group", "deleted", pk)
        return _ok({"deleted": pk})

    # ── Device slots ──

    @Slot(result=str)
    @_safe
    def listDevices(self) -> str:
        return _ok([_to_dict(d) for d in self._accounts.list_devices()])

    @Slot(str, result=str)
    @_safe
    def createDevice(self, payload: str) -> str:
        data = json.loads(payload)
        device_code = data.pop("device_code", "")
        name = data.pop("name", "")
        if not device_code or not name:
            return _err("设备编码和名称不能为空")
        device = self._accounts.create_device(device_code, name, **data)
        self._emit_change("device", "created", device.id)
        return _ok(_to_dict(device))

    @Slot(int, str, result=str)
    @_safe
    def updateDevice(self, pk: int, payload: str) -> str:
        fields = json.loads(payload)
        device = self._accounts.update_device(pk, **fields)
        if device is None:
            return _err("设备不存在")
        self._emit_change("device", "updated", pk)
        return _ok(_to_dict(device))

    @Slot(int, result=str)
    @_safe
    def deleteDevice(self, pk: int) -> str:
        ok = self._accounts.delete_device(pk)
        if not ok:
            return _err("设备不存在")
        self._emit_change("device", "deleted", pk)
        return _ok({"deleted": pk})

    @Slot(int, result=str)
    @_safe
    def inspectDevice(self, pk: int) -> str:
        result = self._accounts.inspect_device(pk)
        self._activity.create_activity_log(
            "device_inspection",
            f"设备巡检 / {result['name']}",
            payload_json=json.dumps(
                {
                    "message": result.get("message") or "设备巡检已完成",
                    "status": result.get("status"),
                    "proxy_status": result.get("proxy_status"),
                    "latency_ms": result.get("latency_ms"),
                    "checked_at": result.get("checked_at"),
                },
                ensure_ascii=False,
                default=str,
            ),
            related_entity_type="device",
            related_entity_id=pk,
        )
        self._emit_change("device", "inspected", pk)
        self._emit_change("activity_log", "created", pk)
        return _ok(result)

    @Slot(int, result=str)
    @_safe
    def repairDeviceEnvironment(self, pk: int) -> str:
        result = self._accounts.repair_device_environment(pk)
        self._activity.create_activity_log(
            "device_repair",
            f"环境修复 / {result['device_code']}",
            payload_json=json.dumps(
                {
                    "message": "；".join(result.get("actions") or []) or "环境修复已完成",
                    "actions": result.get("actions") or [],
                    "status": result.get("status"),
                    "proxy_status": result.get("proxy_status"),
                    "profile_dir": result.get("profile_dir"),
                },
                ensure_ascii=False,
                default=str,
            ),
            related_entity_type="device",
            related_entity_id=pk,
        )
        self._emit_change("device", "repaired", pk)
        self._emit_change("activity_log", "created", pk)
        return _ok(result)

    @Slot(int, result=str)
    @_safe
    def openDeviceEnvironment(self, pk: int) -> str:
        result = self._accounts.open_device_environment(pk)
        self._activity.create_activity_log(
            "device_environment",
            f"打开环境 / {result['device_code']}",
            payload_json=json.dumps(
                {
                    "message": (
                        f"已启动外部浏览器隔离实例，PID {result.get('pid')}"
                        + (
                            f"，浏览器代理 {result.get('browser_proxy')}"
                            if result.get("browser_proxy")
                            else ""
                        )
                    ),
                    "browser_path": result.get("browser_path"),
                    "profile_dir": result.get("profile_dir"),
                    "proxy_server": result.get("proxy_server"),
                    "browser_proxy": result.get("browser_proxy"),
                    "upstream_proxy": result.get("upstream_proxy"),
                    "proxy_auth_present": result.get("proxy_auth_present"),
                    "launch_mode": result.get("launch_mode"),
                    "validation": result.get("validation"),
                    "url": result.get("url"),
                },
                ensure_ascii=False,
                default=str,
            ),
            related_entity_type="device",
            related_entity_id=pk,
        )
        self._emit_change("activity_log", "created", pk)
        return _ok(result)

    @Slot(int, result=str)
    @_safe
    def getDeviceLogs(self, pk: int) -> str:
        logs = []
        for item in self._activity.list_activity_logs():
            if str(item.related_entity_type or "") != "device":
                continue
            if int(item.related_entity_id or 0) != int(pk):
                continue
            payload = ActivityService._load_payload(item.payload_json)
            logs.append(
                {
                    "id": item.id,
                    "category": item.category,
                    "title": item.title,
                    "message": str(payload.get("message") or payload.get("summary") or "").strip(),
                    "payload": payload,
                    "created_at": item.created_at.isoformat(timespec="seconds")
                    if item.created_at
                    else "",
                }
            )
            if len(logs) >= 20:
                break
        return _ok(logs)

    # ── Task slots ──

    @Slot(result=str)
    @_safe
    def listTasks(self) -> str:
        return _ok([_to_dict(t) for t in self._tasks.list_tasks()])

    @Slot(str, result=str)
    @_safe
    def createTask(self, payload: str) -> str:
        data = json.loads(payload)
        title = data.pop("title", "")
        if not title:
            return _err("任务标题不能为空")
        task = self._tasks.create_task(title, **data)
        self._emit_change("task", "created", task.id)
        return _ok(_to_dict(task))

    @Slot(int, str, result=str)
    @_safe
    def updateTask(self, pk: int, payload: str) -> str:
        fields = json.loads(payload)
        task = self._tasks.update_task(pk, **fields)
        if task is None:
            return _err("任务不存在")
        self._emit_change("task", "updated", pk)
        return _ok(_to_dict(task))

    @Slot(int, result=str)
    @_safe
    def startTask(self, pk: int) -> str:
        task = self._tasks.start_task(pk)
        if task is None:
            return _err("任务不存在")
        self._emit_change("task", "started", pk)
        return _ok(_to_dict(task))

    @Slot(int, result=str)
    @_safe
    def completeTask(self, pk: int) -> str:
        task = self._tasks.complete_task(pk)
        if task is None:
            return _err("任务不存在")
        self._emit_change("task", "completed", pk)
        return _ok(_to_dict(task))

    @Slot(int, result=str)
    @_safe
    def failTask(self, pk: int) -> str:
        task = self._tasks.fail_task(pk)
        if task is None:
            return _err("任务不存在")
        self._emit_change("task", "failed", pk)
        return _ok(_to_dict(task))

    @Slot(int, result=str)
    @_safe
    def deleteTask(self, pk: int) -> str:
        ok = self._tasks.delete_task(pk)
        if not ok:
            return _err("任务不存在")
        self._emit_change("task", "deleted", pk)
        return _ok({"deleted": pk})

    @Slot(str, result=str)
    @_safe
    def createTaskAction(self, payload: str) -> str:
        data = json.loads(payload)
        action_key = str(data.get("action_key") or "").strip()
        title = str(data.get("title") or "").strip()
        if not action_key:
            return _err("动作标识不能为空")
        if not title:
            return _err("任务标题不能为空")

        metadata = data.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            metadata = {"value": metadata}

        account_id = data.get("account_id")
        if account_id in ("", None):
            account_id = None
        elif isinstance(account_id, str):
            account_id = int(account_id)

        task = self._tasks.create_action_task(
            action_key,
            title=title,
            summary=str(data.get("summary") or ""),
            metadata=metadata,
            task_type=str(data.get("task_type") or "maintenance"),
            priority=str(data.get("priority") or "medium"),
            status=str(data.get("status") or "pending"),
            account_id=account_id,
        )
        self._emit_change("task", "created", task.id)
        return _ok(_to_dict(task))

    # ── AI Provider slots ──

    @Slot(result=str)
    @_safe
    def listProviders(self) -> str:
        return _ok([_to_dict(p) for p in self._ai.list_providers()])

    @Slot(str, result=str)
    @_safe
    def createProvider(self, payload: str) -> str:
        data = json.loads(payload)
        name = data.pop("name", "")
        if not name:
            return _err("供应商名称不能为空")
        provider = self._ai.create_provider(name, **data)
        self._emit_change("provider", "created", provider.id)
        return _ok(_to_dict(provider))

    @Slot(int, str, result=str)
    @_safe
    def updateProvider(self, pk: int, payload: str) -> str:
        fields = json.loads(payload)
        provider = self._ai.update_provider(pk, **fields)
        if provider is None:
            return _err("供应商不存在")
        self._emit_change("provider", "updated", pk)
        return _ok(_to_dict(provider))

    @Slot(int, result=str)
    @_safe
    def setActiveProvider(self, pk: int) -> str:
        provider = self._ai.set_active(pk)
        if provider is None:
            return _err("供应商不存在")
        self._emit_change("provider", "activated", pk)
        return _ok(_to_dict(provider))

    @Slot(int, result=str)
    @_safe
    def deleteProvider(self, pk: int) -> str:
        ok = self._ai.delete_provider(pk)
        if not ok:
            return _err("供应商不存在")
        self._emit_change("provider", "deleted", pk)
        return _ok({"deleted": pk})

    # ── Asset slots ──

    @Slot(result=str)
    @_safe
    def listAssets(self) -> str:
        rows: list[dict[str, Any]] = []
        for asset in self._assets.list_assets():
            payload = _to_dict(asset)
            cached = self._assets.get_video_poster_cached(payload.get("file_path"))
            payload["poster_path"] = cached.get("poster_path", "")
            rows.append(payload)
        return _ok(rows)

    @Slot(str, result=str)
    @_safe
    def listAssetsByType(self, asset_type: str) -> str:
        rows: list[dict[str, Any]] = []
        for asset in self._assets.list_assets(asset_type=asset_type):
            payload = _to_dict(asset)
            cached = self._assets.get_video_poster_cached(payload.get("file_path"))
            payload["poster_path"] = cached.get("poster_path", "")
            rows.append(payload)
        return _ok(rows)

    @Slot(str, result=str)
    @_safe
    def createAsset(self, payload: str) -> str:
        data = json.loads(payload)
        filename = data.pop("filename", "")
        if not filename:
            return _err("文件名不能为空")
        asset = self._assets.create_asset(filename, **data)
        self._assets.schedule_video_poster_generation(asset.file_path)
        self._emit_change("asset", "created", asset.id)
        return _ok(_to_dict(asset))

    @Slot(int, str, result=str)
    @_safe
    def updateAsset(self, pk: int, payload: str) -> str:
        fields = json.loads(payload)
        asset = self._assets.update_asset(pk, **fields)
        if asset is None:
            return _err("素材不存在")
        self._assets.schedule_video_poster_generation(asset.file_path)
        self._emit_change("asset", "updated", pk)
        return _ok(_to_dict(asset))

    @Slot(int, result=str)
    @_safe
    def deleteAsset(self, pk: int) -> str:
        ok = self._assets.delete_asset(pk)
        if not ok:
            return _err("素材不存在")
        self._emit_change("asset", "deleted", pk)
        return _ok({"deleted": pk})

    @Slot(result=str)
    @_safe
    def getAssetStats(self) -> str:
        total = self._repo.count(Asset)
        by_type = self._assets.count_by_type()
        return _ok({"total": total, "byType": by_type})

    @Slot(str, result=str)
    @_safe
    def getAssetVideoPoster(self, file_path: str) -> str:
        result = self._assets.get_video_poster_cached(file_path)
        return _ok(result)

    @Slot(str, int, result=str)
    @_safe
    def getAssetTextPreview(self, file_path: str, max_chars: int = 220) -> str:
        preview = self._assets.read_text_preview(file_path, max_chars=max_chars)
        return _ok(preview)

    @Slot(result=str)
    @_safe
    def listVideoProjects(self) -> str:
        projects = list(self._video_editing.list_projects())
        if not projects:
            self._resolve_video_context()
            projects = list(self._video_editing.list_projects())
        return _ok([self._serialize_video_project(project) for project in projects])

    @Slot(str, result=str)
    @_safe
    def appendAssetsToSequence(self, payload: str) -> str:
        data = json.loads(payload or "{}")
        raw_asset_ids = data.get("asset_ids") or []
        asset_ids = [int(asset_id) for asset_id in raw_asset_ids if str(asset_id).strip()]
        if not asset_ids:
            return _err("请先选择至少一个素材")

        project, sequence = self._resolve_video_context(
            project_id=int(data["project_id"]) if data.get("project_id") not in (None, "") else None,
            sequence_id=int(data["sequence_id"]) if data.get("sequence_id") not in (None, "") else None,
        )
        assets = self._video_editing.append_assets_to_sequence(sequence.id, asset_ids)
        self._emit_change("video_project", "updated", project.id)
        return _ok({
            "project_id": project.id,
            "sequence_id": sequence.id,
            "asset_ids": [item.asset_id for item in assets],
            "clip_ids": [],
            "count": len(assets),
        })

    @Slot(str, result=str)
    @_safe
    def addAssetsToTimeline(self, payload: str) -> str:
        data = json.loads(payload or "{}")
        raw_asset_ids = data.get("asset_ids") or []
        asset_ids = [int(asset_id) for asset_id in raw_asset_ids if str(asset_id).strip()]
        if not asset_ids:
            return _err("请先选择至少一个素材")

        project, sequence = self._resolve_video_context(
            project_id=int(data["project_id"]) if data.get("project_id") not in (None, "") else None,
            sequence_id=int(data["sequence_id"]) if data.get("sequence_id") not in (None, "") else None,
        )
        clips = self._video_editing.add_assets_to_timeline(
            sequence.id,
            asset_ids,
            track_type=data.get("track_type"),
            track_index=int(data.get("track_index") or 0),
        )
        self._emit_change("video_project", "updated", project.id)
        return _ok({
            "project_id": project.id,
            "sequence_id": sequence.id,
            "clip_ids": [clip.id for clip in clips],
            "count": len(clips),
        })

    @Slot(str, result=str)
    @_safe
    def reorderVideoClips(self, payload: str) -> str:
        data = json.loads(payload or "{}")
        ordered_ids = [int(clip_id) for clip_id in (data.get("clip_ids") or []) if str(clip_id).strip()]
        if not ordered_ids:
            return _err("请先提供时间轴片段顺序")

        project, sequence = self._resolve_video_context(
            project_id=int(data["project_id"]) if data.get("project_id") not in (None, "") else None,
            sequence_id=int(data["sequence_id"]) if data.get("sequence_id") not in (None, "") else None,
        )
        self._video_editing.reorder_clips(sequence.id, ordered_ids)
        self._emit_change("video_project", "updated", project.id)
        return _ok({
            "project_id": project.id,
            "sequence_id": sequence.id,
            "count": len(ordered_ids),
        })

    @Slot(str, result=str)
    @_safe
    def trimVideoClip(self, payload: str) -> str:
        data = json.loads(payload or "{}")
        clip_id = int(data.get("clip_id") or 0)
        if not clip_id:
            return _err("请先选择时间轴片段")
        clip = self._video_editing.update_clip_range(
            clip_id,
            source_in_ms=int(data.get("source_in_ms") or 0),
            source_out_ms=int(data.get("source_out_ms") or 0),
        )
        sequence = self._repo.get_by_id(VideoSequence, clip.sequence_id)
        project = self._video_editing.get_project(sequence.project_id) if sequence is not None else None
        if project is not None:
            self._emit_change("video_project", "updated", project.id)
        return _ok(_to_dict(clip))

    @Slot(str, result=str)
    @_safe
    def deleteVideoClip(self, payload: str) -> str:
        data = json.loads(payload or "{}")
        clip_id = int(data.get("clip_id") or 0)
        if not clip_id:
            return _err("请先选择时间轴片段")
        clip = self._repo.get_by_id(VideoClip, clip_id)
        if clip is None:
            return _err("时间轴片段不存在")
        sequence = self._repo.get_by_id(VideoSequence, clip.sequence_id)
        project = self._video_editing.get_project(sequence.project_id) if sequence is not None else None
        deleted = self._video_editing.delete_clip(clip_id)
        if not deleted:
            return _err("时间轴片段不存在")
        if project is not None:
            self._emit_change("video_project", "updated", project.id)
        return _ok({"deleted": True, "clip_id": clip_id})

    @Slot(str, result=str)
    @_safe
    def updateVideoClipAudio(self, payload: str) -> str:
        data = json.loads(payload or "{}")
        clip_id = int(data.get("clip_id") or 0)
        if not clip_id:
            return _err("请先选择 A1 音频片段")

        raw_volume = data.get("volume")
        volume = None if raw_volume in (None, "") else float(raw_volume)
        muted = _parse_bool(data.get("muted"))
        clip = self._video_editing.update_audio_clip(
            clip_id,
            volume=volume,
            muted=muted,
        )
        sequence = self._repo.get_by_id(VideoSequence, clip.sequence_id)
        project = self._video_editing.get_project(sequence.project_id) if sequence is not None else None
        if project is not None:
            self._emit_change("video_project", "updated", project.id)
        return _ok(_to_dict(clip))

    @Slot(str, result=str)
    @_safe
    def createVideoSubtitle(self, payload: str) -> str:
        data = json.loads(payload or "{}")
        project, sequence = self._resolve_video_context(
            project_id=int(data["project_id"]) if data.get("project_id") not in (None, "") else None,
            sequence_id=int(data["sequence_id"]) if data.get("sequence_id") not in (None, "") else None,
        )
        subtitle = self._video_editing.create_subtitle(
            sequence.id,
            start_ms=int(data.get("start_ms") or 0),
            end_ms=int(data.get("end_ms") or 0),
            text=str(data.get("text") or ""),
        )
        self._emit_change("video_project", "updated", project.id)
        return _ok(_to_dict(subtitle))

    @Slot(str, result=str)
    @_safe
    def updateVideoSubtitle(self, payload: str) -> str:
        data = json.loads(payload or "{}")
        subtitle_id = int(data.get("subtitle_id") or 0)
        if not subtitle_id:
            return _err("请先选择字幕段")
        subtitle = self._video_editing.update_subtitle(
            subtitle_id,
            start_ms=int(data.get("start_ms") or 0),
            end_ms=int(data.get("end_ms") or 0),
            text=str(data.get("text") or ""),
        )
        sequence = self._repo.get_by_id(VideoSequence, subtitle.sequence_id)
        project = self._video_editing.get_project(sequence.project_id) if sequence is not None else None
        if project is not None:
            self._emit_change("video_project", "updated", project.id)
        return _ok(_to_dict(subtitle))

    @Slot(str, result=str)
    @_safe
    def deleteVideoSubtitle(self, payload: str) -> str:
        data = json.loads(payload or "{}")
        subtitle_id = int(data.get("subtitle_id") or 0)
        if not subtitle_id:
            return _err("请先选择字幕段")
        subtitle = self._repo.get_by_id(VideoSubtitle, subtitle_id)
        if subtitle is None:
            return _err("字幕段不存在")
        sequence = self._repo.get_by_id(VideoSequence, subtitle.sequence_id)
        project = self._video_editing.get_project(sequence.project_id) if sequence is not None else None
        deleted = self._video_editing.delete_subtitle(subtitle_id)
        if not deleted:
            return _err("字幕段不存在")
        if project is not None:
            self._emit_change("video_project", "updated", project.id)
        return _ok({"deleted": subtitle_id})

    @Slot(str, result=str)
    @_safe
    def prepareVideoMonitor(self, payload: str) -> str:
        data = json.loads(payload or "{}")
        state = self._video_monitor.prepare(
            data.get("file_path"),
            start_ms=int(data.get("start_ms") or 0),
            end_ms=int(data.get("end_ms") or 0),
            autoplay=bool(data.get("autoplay")),
        )
        return _ok(state)

    @Slot(result=str)
    @_safe
    def getVideoMonitorState(self) -> str:
        return _ok(self._video_monitor.state())

    @Slot(result=str)
    @_safe
    def playVideoMonitor(self) -> str:
        return _ok(self._video_monitor.play())

    @Slot(result=str)
    @_safe
    def pauseVideoMonitor(self) -> str:
        return _ok(self._video_monitor.pause())

    @Slot(result=str)
    @_safe
    def stopVideoMonitor(self) -> str:
        return _ok(self._video_monitor.stop())

    @Slot(int, result=str)
    @_safe
    def seekVideoMonitor(self, position_ms: int) -> str:
        return _ok(self._video_monitor.seek(position_ms))

    @Slot(int, result=str)
    @_safe
    def stepVideoMonitor(self, delta_ms: int) -> str:
        return _ok(self._video_monitor.step(delta_ms))

    @Slot(str, result=str)
    @_safe
    def removeAssetsFromSequence(self, payload: str) -> str:
        data = json.loads(payload or "{}")
        raw_asset_ids = data.get("asset_ids") or []
        asset_ids = [int(asset_id) for asset_id in raw_asset_ids if str(asset_id).strip()]
        if not asset_ids:
            return _err("请先选择至少一个素材")

        project, sequence = self._resolve_video_context(
            project_id=int(data["project_id"]) if data.get("project_id") not in (None, "") else None,
            sequence_id=int(data["sequence_id"]) if data.get("sequence_id") not in (None, "") else None,
        )
        removed = self._video_editing.remove_assets_from_sequence(sequence.id, asset_ids)
        self._emit_change("video_project", "updated", project.id)
        return _ok({
            "project_id": project.id,
            "sequence_id": sequence.id,
            "removed": removed,
        })

    @Slot(str, result=str)
    @_safe
    def createVideoExport(self, payload: str) -> str:
        data = json.loads(payload or "{}")
        project, sequence = self._resolve_video_context(
            project_id=int(data["project_id"]) if data.get("project_id") not in (None, "") else None,
            sequence_id=int(data["sequence_id"]) if data.get("sequence_id") not in (None, "") else None,
        )
        validation = self._video_editing.validate_export(project.id, sequence.id)
        if not validation.get("ok"):
            errors = validation.get("errors") or ["当前序列暂不可导出"]
            return _err("；".join(str(item) for item in errors if str(item).strip()) or "当前序列暂不可导出")
        export = self._video_editing.create_export_record(
            project_id=project.id,
            sequence_id=sequence.id,
            preset=str(data.get("preset") or "mp4_1080p"),
            output_path=data.get("output_path"),
        )
        self._emit_change("video_project", "updated", project.id)
        return _ok(_to_dict(export))

    # ── Dashboard aggregate ──

    @Slot(result=str)
    @_safe
    def getDashboardStats(self) -> str:
        return _ok({
            "accounts": {
                "total": self._repo.count(Account),
                "byStatus": self._repo.count_accounts_by_status(),
            },
            "tasks": {
                "total": self._repo.count(Task),
                "byStatus": self._repo.count_tasks_by_status(),
            },
            "devices": {
                "total": self._repo.count(Device),
                "byStatus": self._repo.count_devices_by_status(),
            },
            "groups": self._repo.count(Group),
            "assets": self._repo.count(Asset),
            "providers": self._repo.count(AIProvider),
        })

    @Slot(str, result=str)
    @_safe
    def getDashboardOverview(self, range_key: str = "today") -> str:
        import datetime as dt

        now = dt.datetime.now()
        if range_key == "7d":
            bucket_count = 7
            start = now - dt.timedelta(days=6)
            bucket_starts = [
                dt.datetime.combine((start.date() + dt.timedelta(days=index)), dt.time.min)
                for index in range(bucket_count)
            ]
            labels = [(start.date() + dt.timedelta(days=index)).strftime("%m-%d") for index in range(bucket_count)]
        elif range_key == "30d":
            bucket_count = 30
            start = now - dt.timedelta(days=29)
            bucket_starts = [
                dt.datetime.combine((start.date() + dt.timedelta(days=index)), dt.time.min)
                for index in range(bucket_count)
            ]
            labels = [(start.date() + dt.timedelta(days=index)).strftime("%m-%d") for index in range(bucket_count)]
        else:
            bucket_count = 24
            start_hour = now.replace(minute=0, second=0, microsecond=0) - dt.timedelta(hours=23)
            bucket_starts = [start_hour + dt.timedelta(hours=index) for index in range(bucket_count)]
            labels = [(start_hour + dt.timedelta(hours=index)).strftime("%H:00") for index in range(bucket_count)]

        trend = []
        for index, bucket_start in enumerate(bucket_starts):
            bucket_end = bucket_starts[index + 1] if index + 1 < len(bucket_starts) else (now + dt.timedelta(seconds=1))
            trend.append({
                "label": labels[index],
                "created": self._repo.count_tasks_created_between(bucket_start, bucket_end),
                "completed": self._repo.count_tasks_completed_between(bucket_start, bucket_end),
                "failed": self._repo.count_tasks_failed_between(bucket_start, bucket_end),
            })

        recent_logs = self._repo.list_recent_activity_logs(limit=8)
        recent_tasks = self._repo.list_recent_tasks(limit=8)
        activity = [
            {
                "title": item.title,
                "entity": item.related_entity_type or "activity",
                "category": item.category,
                "status": "已记录",
                "time": item.created_at.isoformat() if item.created_at else "",
            }
            for item in recent_logs
        ]
        if not activity:
            activity = [
                {
                    "title": item.title,
                    "entity": "task",
                    "category": item.task_type,
                    "status": item.status,
                    "time": item.created_at.isoformat() if item.created_at else "",
                }
                for item in recent_tasks
            ]

        providers = self._repo.list_all(AIProvider, limit=20)
        tasks_by_status = self._repo.count_tasks_by_status()
        devices_by_status = self._repo.count_devices_by_status()

        systems = [
            {
                "key": "tasks",
                "title": "任务执行状态",
                "summary": "运行中 %s / 排队 %s" % (tasks_by_status.get("running", 0), tasks_by_status.get("pending", 0)),
                "status": "异常" if tasks_by_status.get("failed", 0) else "正常",
                "tone": "error" if tasks_by_status.get("failed", 0) else "success",
            },
            {
                "key": "providers",
                "title": "AI 供应商接入",
                "summary": "启用 %s / 总计 %s" % (len([p for p in providers if p.is_active]), len(providers)),
                "status": "未配置" if not providers else "已接入",
                "tone": "warning" if not providers else "success",
            },
            {
                "key": "accounts",
                "title": "账号同步准备",
                "summary": "账号 %s / 分组 %s" % (self._repo.count(Account), self._repo.count(Group)),
                "status": "正常",
                "tone": "info",
            },
            {
                "key": "devices",
                "title": "设备与链路状态",
                "summary": "健康 %s / 警告 %s / 错误 %s" % (
                    devices_by_status.get("healthy", 0),
                    devices_by_status.get("warning", 0),
                    devices_by_status.get("error", 0),
                ),
                "status": "需关注" if devices_by_status.get("error", 0) or devices_by_status.get("warning", 0) else "正常",
                "tone": "warning" if devices_by_status.get("error", 0) or devices_by_status.get("warning", 0) else "success",
            },
        ]

        return _ok({
            "range": range_key,
            "stats": {
                "accounts": {"total": self._repo.count(Account), "byStatus": self._repo.count_accounts_by_status()},
                "tasks": {"total": self._repo.count(Task), "byStatus": tasks_by_status},
                "devices": {"total": self._repo.count(Device), "byStatus": devices_by_status},
                "groups": self._repo.count(Group),
                "assets": self._repo.count(Asset),
                "providers": len(providers),
            },
            "trend": trend,
            "activity": activity,
            "systems": systems,
        })

    @Slot(result=str)
    @_safe
    def getAnalyticsSummary(self) -> str:
        return _ok(self._analytics.get_analytics_summary())

    @Slot(result=str)
    @_safe
    def getConversionAnalysis(self) -> str:
        return _ok(self._analytics.get_conversion_analysis())

    @Slot(result=str)
    @_safe
    def getPersonaAnalysis(self) -> str:
        return _ok(self._analytics.get_persona_analysis())

    @Slot(result=str)
    @_safe
    def getTrafficAnalysis(self) -> str:
        return _ok(self._analytics.get_traffic_analysis())

    @Slot(result=str)
    @_safe
    def getCompetitorAnalysis(self) -> str:
        return _ok(self._analytics.get_competitor_analysis())

    @Slot(result=str)
    @_safe
    def getBlueOceanAnalysis(self) -> str:
        return _ok(self._analytics.get_blue_ocean_analysis())

    @Slot(result=str)
    @_safe
    def getInteractionAnalysis(self) -> str:
        return _ok(self._analytics.get_interaction_analysis())

    # ── Analytics / Reports / Workflows / Experiments ──

    @Slot(result=str)
    @_safe
    def listAnalysisSnapshots(self) -> str:
        return _ok([_to_dict(item) for item in self._analytics.list_analysis_snapshots()])

    @Slot(str, result=str)
    @_safe
    def createAnalysisSnapshot(self, payload: str) -> str:
        data = json.loads(payload)
        page_key = data.pop("page_key", "")
        title = data.pop("title", "")
        if not page_key or not title:
            return _err("page_key 和 title 不能为空")
        item = self._analytics.create_analysis_snapshot(page_key, title, **data)
        self._emit_change("analysis_snapshot", "created", item.id)
        return _ok(_to_dict(item))

    @Slot(result=str)
    @_safe
    def listReportRuns(self) -> str:
        return _ok([_to_dict(item) for item in self._reports.list_report_runs()])

    @Slot(str, result=str)
    @_safe
    def createReportRun(self, payload: str) -> str:
        data = json.loads(payload)
        title = data.pop("title", "")
        if not title:
            return _err("title 不能为空")
        item = self._reports.create_report_run(title, **data)
        self._emit_change("report_run", "created", item.id)
        return _ok(_to_dict(item))

    @Slot(result=str)
    @_safe
    def listWorkflowDefinitions(self) -> str:
        return _ok([_to_dict(item) for item in self._workflows.list_workflow_definitions()])

    @Slot(str, result=str)
    @_safe
    def createWorkflowDefinition(self, payload: str) -> str:
        data = json.loads(payload)
        name = data.pop("name", "")
        if not name:
            return _err("name 不能为空")
        item = self._workflows.create_workflow_definition(name, **data)
        self._emit_change("workflow_definition", "created", item.id)
        return _ok(_to_dict(item))

    @Slot(result=str)
    @_safe
    def listWorkflowRuns(self) -> str:
        return _ok([_to_dict(item) for item in self._workflows.list_workflow_runs()])

    @Slot(str, result=str)
    @_safe
    def startWorkflowRun(self, payload: str) -> str:
        data = json.loads(payload)
        workflow_definition_id = data.pop("workflow_definition_id", None)
        if workflow_definition_id is None:
            return _err("workflow_definition_id 不能为空")
        item = self._workflows.create_workflow_run(int(workflow_definition_id), **data)
        self._emit_change("workflow_run", "created", item.id)
        return _ok(_to_dict(item))

    @Slot(result=str)
    @_safe
    def listExperimentProjects(self) -> str:
        return _ok([_to_dict(item) for item in self._analytics.list_experiment_projects()])

    @Slot(str, result=str)
    @_safe
    def createExperimentProject(self, payload: str) -> str:
        data = json.loads(payload)
        name = data.pop("name", "")
        if not name:
            return _err("name 不能为空")
        item = self._analytics.create_experiment_project(name, **data)
        self._emit_change("experiment_project", "created", item.id)
        return _ok(_to_dict(item))

    @Slot(result=str)
    @_safe
    def listExperimentViews(self) -> str:
        return _ok([_to_dict(item) for item in self._analytics.list_experiment_views()])

    @Slot(str, result=str)
    @_safe
    def createExperimentView(self, payload: str) -> str:
        data = json.loads(payload)
        experiment_project_id = data.pop("experiment_project_id", None)
        name = data.pop("name", "")
        if experiment_project_id is None or not name:
            return _err("experiment_project_id 和 name 不能为空")
        item = self._analytics.create_experiment_view(int(experiment_project_id), name, **data)
        self._emit_change("experiment_view", "created", item.id)
        return _ok(_to_dict(item))

    @Slot(result=str)
    @_safe
    def listActivityLogs(self) -> str:
        return _ok([_to_dict(item) for item in self._activity.list_activity_logs()])

    @Slot(result=str)
    @_safe
    def listNotifications(self) -> str:
        return _ok(self._activity.list_notifications())

    @Slot(str, result=str)
    @_safe
    def createActivityLog(self, payload: str) -> str:
        data = json.loads(payload)
        category = data.pop("category", "")
        title = data.pop("title", "")
        if not category or not title:
            return _err("category 和 title 不能为空")
        item = self._activity.create_activity_log(category, title, **data)
        self._emit_change("activity_log", "created", item.id)
        return _ok(_to_dict(item))

    @Slot(result=str)
    @_safe
    def runDevSeed(self) -> str:
        result = self._dev_seed.seed_development_data()
        self._emit_change("dev_seed", "completed", result.get("created", 0))
        return _ok(result)

    # ── Settings slots ──

    @Slot(str, result=str)
    @_safe
    def getSetting(self, key: str) -> str:
        return _ok(self._repo.get_setting(key))

    @Slot(str, str, result=str)
    @_safe
    def setSetting(self, key: str, value: str) -> str:
        self._repo.set_setting(key, value)
        return _ok({"key": key, "value": value})

    @Slot(str, result=str)
    @_safe
    def setSettingsBatch(self, payload: str) -> str:
        data = json.loads(payload or "{}")
        if not isinstance(data, dict):
            return _err("批量设置参数必须为对象")
        updated = []
        for key, value in data.items():
            self._repo.set_setting(str(key), "" if value is None else str(value))
            updated.append(str(key))
        return _ok({"updated": updated, "count": len(updated)})

    @Slot(result=str)
    @_safe
    def getAllSettings(self) -> str:
        return _ok(self._repo.get_all_settings())

    # ── Theme (persisted in AppSetting) ──

    @Slot(str, result=str)
    @_safe
    def setTheme(self, theme: str) -> str:
        self._repo.set_setting("theme", theme)
        return _ok({"theme": theme})

    @Slot(result=str)
    @_safe
    def getTheme(self) -> str:
        return _ok(self._repo.get_setting("theme", "light"))

    # ── Version & Update ──

    @Slot(result=str)
    @_safe
    def getAppVersion(self) -> str:
        return _ok({"version": APP_VERSION})

    @Slot(result=str)
    @_safe
    def checkForUpdate(self) -> str:
        info = self._updater.check_update()
        if info is None:
            return _ok({"hasUpdate": False, "current": APP_VERSION})
        return _ok({
            "hasUpdate": info.has_update,
            "current": APP_VERSION,
            "latest": info.version,
            "tag": info.tag,
            "downloadUrl": info.download_url,
            "htmlUrl": info.html_url,
            "releaseNotes": info.body,
            "assetName": info.asset_name,
            "assetSize": info.asset_size,
        })

    @Slot(str, result=str)
    @_safe
    def startDownloadUpdate(self, download_url: str) -> str:
        ok = self._updater.start_download(download_url or None)
        if not ok:
            return _err("下载已在进行中或无下载链接")
        return _ok(True)

    @Slot(result=str)
    @_safe
    def getDownloadProgress(self) -> str:
        return _ok(self._updater.get_download_progress())

    @Slot(result=str)
    @_safe
    def applyUpdate(self) -> str:
        result = self._updater.apply_update()
        if not result.get("ok"):
            return _err(result.get("error", "应用更新失败"))
        return _ok(result)

    # ── License ──

    # Rate limiter: max 5 activation attempts per 300s
    _activate_timestamps: list = []

    @Slot(result=str)
    @_safe
    def getLicenseStatus(self) -> str:
        svc = LicenseService()
        status = svc.get_status()
        log.debug("Bridge.getLicenseStatus -> %s", status)
        return _ok(status)

    @Slot(str, result=str)
    @_safe
    def activateLicense(self, key: str) -> str:
        import time as _time
        now = _time.monotonic()
        self._activate_timestamps = [t for t in self._activate_timestamps if now - t < 300]
        if len(self._activate_timestamps) >= 5:
            return _err("激活尝试过于频繁，请 5 分钟后重试")
        self._activate_timestamps.append(now)
        svc = LicenseService()
        result = svc.activate(key.strip())
        if not result.get("ok"):
            return _err(result.get("error", "激活失败"))
        return _ok(result["info"])

    @Slot(str, int, str, result=str)
    @_safe
    def issueLicense(self, machine_id: str, days: int, tier: str) -> str:
        svc = LicenseService()
        mid = machine_id.strip()
        d = max(0, int(days or 0))
        t = (tier or "pro").strip()
        from desktop_app.services.license_codec import _is_compound_id
        if _is_compound_id(mid):
            result = svc.issue_compound(compound_id=mid, days=d, tier=t)
        else:
            result = svc.issue(machine_id=mid, days=d, tier=t)
        if not result.get("ok"):
            return _err(result.get("error", "签发失败"))
        return _ok(result)

    @Slot(str, str, result=str)
    @_safe
    def verifyLicenseKey(self, machine_id: str, key: str) -> str:
        svc = LicenseService()
        result = svc.verify(key=key.strip(), machine_id=machine_id.strip())
        if not result.get("ok"):
            return _err(result.get("error", "校验失败"))
        return _ok(result["info"])

    @Slot(result=str)
    @_safe
    def deactivateLicense(self) -> str:
        svc = LicenseService()
        return _ok(svc.deactivate())

    @Slot(str, result=str)
    @_safe
    def checkRouteAccess(self, route: str) -> str:
        svc = LicenseService()
        return _ok(svc.check_route_access(route.strip()))

    # ── AI Chat ──

    @Slot(str, result=str)
    @_safe
    def chatSync(self, payload: str) -> str:
        """Synchronous chat completion.

        payload JSON: {messages: [{role,content}], model?, preset?, temperature?, max_tokens?}
        """
        p = json.loads(payload)
        msgs = [{"role": m["role"], "content": m["content"]} for m in p.get("messages", [])]
        result = self._chat.chat(
            messages=msgs,
            model=p.get("model"),
            preset_key=p.get("preset"),
            temperature=p.get("temperature"),
            max_tokens=p.get("max_tokens"),
        )
        self._usage.record(
            result.provider_name, result.model,
            result.prompt_tokens, result.completion_tokens,
        )
        return _ok({
            "content": result.content,
            "model": result.model,
            "provider": result.provider_name,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "total_tokens": result.total_tokens,
            "elapsed_ms": result.elapsed_ms,
        })

    @Slot(str, result=str)
    @_safe
    def startChatStream(self, payload: str) -> str:
        """Start a streaming chat in a background thread.

        payload JSON: same as chatSync.
        Returns immediately. JS polls via pollChatStream().
        """
        if self._stream_thread and self._stream_thread.is_alive():
            return _err("已有流式请求进行中")

        p = json.loads(payload)
        msgs = [{"role": m["role"], "content": m["content"]} for m in p.get("messages", [])]
        self._stream_queue = queue.Queue()

        def _worker():
            try:
                for chunk in self._chat.chat_stream(
                    messages=msgs,
                    model=p.get("model"),
                    preset_key=p.get("preset"),
                    temperature=p.get("temperature"),
                    max_tokens=p.get("max_tokens"),
                ):
                    self._stream_queue.put({
                        "delta": chunk.delta,
                        "done": chunk.done,
                        "content": chunk.content,
                        "model": chunk.model,
                        "provider": chunk.provider_name,
                        "tokens": {"prompt": chunk.prompt_tokens, "completion": chunk.completion_tokens} if chunk.done else None,
                        "elapsed_ms": chunk.elapsed_ms,
                    })
                    if chunk.done and chunk.prompt_tokens:
                        self._usage.record(
                            chunk.provider_name, chunk.model,
                            chunk.prompt_tokens,
                            chunk.completion_tokens,
                        )
            except Exception as exc:
                log.exception("Stream worker error")
                self._stream_queue.put({"delta": "", "done": True, "error": str(exc)})

        self._stream_thread = threading.Thread(target=_worker, daemon=True)
        self._stream_thread.start()
        return _ok({"started": True})

    @Slot(result=str)
    @_safe
    def pollChatStream(self) -> str:
        """Drain all available chunks from the stream queue."""
        if not self._stream_queue:
            return _ok({"chunks": [], "finished": True})
        chunks = []
        finished = False
        while not self._stream_queue.empty():
            try:
                c = self._stream_queue.get_nowait()
                chunks.append(c)
                if c.get("done"):
                    finished = True
            except queue.Empty:
                break
        return _ok({"chunks": chunks, "finished": finished})

    @Slot(result=str)
    @_safe
    def listAiPresets(self) -> str:
        return _ok(list_presets())

    @Slot(str, result=str)
    @_safe
    def getAiPreset(self, key: str) -> str:
        p = get_preset(key)
        if not p:
            return _err(f"预设 '{key}' 不存在")
        return _ok(p)

    @Slot(int, result=str)
    @_safe
    def testAiProvider(self, pk: int) -> str:
        result = self._chat.test_provider(pk)
        return _ok(result)

    @Slot(result=str)
    @_safe
    def getAiUsageStats(self) -> str:
        return _ok(self._usage.get_stats())

    @Slot(result=str)
    @_safe
    def getAiUsageToday(self) -> str:
        return _ok(self._usage.get_today())

    @Slot(result=str)
    @_safe
    def getRecentLogs(self) -> str:
        path = LOG_FILE
        if not path.exists():
            return _ok({
                "path": str(path),
                "lines": [],
                "lineCount": 0,
                "errorCount": 0,
                "warningCount": 0,
                "size": 0,
            })

        content = path.read_text(encoding="utf-8", errors="replace")
        lines = [line for line in content.splitlines() if line.strip()]
        recent = lines[-200:]
        upper_recent = [line.upper() for line in recent]
        return _ok({
            "path": str(path),
            "lines": recent,
            "lineCount": len(recent),
            "errorCount": sum(" ERROR " in line for line in upper_recent),
            "warningCount": sum(" WARNING " in line for line in upper_recent),
            "size": path.stat().st_size,
        })

    @Slot(str, result=str)
    @_safe
    def copyToClipboard(self, text: str) -> str:
        from PySide6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        return _ok({"copied": True})

    @Slot(result=str)
    @_safe
    def pickLocalFiles(self) -> str:
        files, _ = QFileDialog.getOpenFileNames(
            None,
            "选择文件",
            str(Path.home()),
            "All Files (*.*)",
        )
        return _ok(files or [])

    @Slot(result=str)
    @_safe
    def importTextFile(self) -> str:
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "导入文本文件",
            str(Path.home()),
            "Text Files (*.txt *.json *.cookie *.cookies);;All Files (*.*)",
        )
        if not file_path:
            return _ok({"selected": False, "path": "", "name": "", "content": ""})

        path = Path(file_path)
        content = None
        for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
            try:
                content = path.read_text(encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        if content is None:
            raise ValueError("文件编码无法识别，请先转成 UTF-8 后再导入")
        return _ok({
            "selected": True,
            "path": str(path),
            "name": path.name,
            "content": content,
        })

    @Slot(str, result=str)
    @_safe
    def exportTextFile(self, content: str) -> str:
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "导出文本",
            str(Path.home() / "diagnostics-report.txt"),
            "Text Files (*.txt);;All Files (*.*)",
        )
        if not file_path:
            return _ok({"saved": False, "path": ""})
        path = Path(file_path)
        path.write_text(content or "", encoding="utf-8")
        return _ok({"saved": True, "path": str(path)})

    @Slot(str, str, result=str)
    @_safe
    def exportNamedTextFile(self, content: str, suggested_name: str) -> str:
        suggested = str(suggested_name or "").strip() or "export.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "导出文本",
            str(Path.home() / suggested),
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*.*)",
        )
        if not file_path:
            return _ok({"saved": False, "path": ""})
        path = Path(file_path)
        path.write_text(content or "", encoding="utf-8")
        return _ok({"saved": True, "path": str(path)})

    @Slot(result=str)
    @_safe
    def runNetworkDiagnostics(self) -> str:
        providers = self._ai.list_providers()
        checks: list[dict[str, Any]] = []

        try:
            ip = socket.gethostbyname("example.com")
            checks.append({
                "name": "DNS 解析",
                "status": "ok",
                "detail": f"example.com -> {ip}",
            })
        except Exception as exc:
            checks.append({
                "name": "DNS 解析",
                "status": "error",
                "detail": f"解析失败: {exc}",
            })

        if providers:
            active = next((p for p in providers if p.is_active), providers[0])
            checks.append({
                "name": "AI 供应商配置",
                "status": "ok" if active.api_key else "warning",
                "detail": f"{active.name} / {active.default_model or '未配置模型'}",
            })
        else:
            checks.append({
                "name": "AI 供应商配置",
                "status": "error",
                "detail": "未检测到可用供应商",
            })

        log_path = Path(LOG_FILE)
        checks.append({
            "name": "日志文件",
            "status": "ok" if log_path.exists() else "warning",
            "detail": str(log_path),
        })

        tasks_failed = self._repo.count_tasks_by_status().get("failed", 0)
        checks.append({
            "name": "任务失败率",
            "status": "warning" if tasks_failed else "ok",
            "detail": f"失败任务 {tasks_failed} 条",
        })

        error_count = sum(1 for item in checks if item["status"] == "error")
        warning_count = sum(1 for item in checks if item["status"] == "warning")
        score = max(0, 100 - error_count * 30 - warning_count * 12)
        report_lines = [
            f"TK-OPS 网络诊断报告 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 48,
        ]
        for item in checks:
            report_lines.append(f"[{item['status'].upper()}] {item['name']}: {item['detail']}")

        return _ok({
            "score": score,
            "checks": checks,
            "errorCount": error_count,
            "warningCount": warning_count,
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "reportText": "\n".join(report_lines),
        })

    # ── Logging ──

    @Slot(str)
    def logFrontend(self, message: str) -> None:
        try:
            payload = json.loads(message)
            if isinstance(payload, dict):
                level = str(payload.get("level", "info")).lower()
                event = str(payload.get("event", "frontend.event"))
                route = str(payload.get("route", ""))
                data = payload.get("data")
                text = f"[前端][事件:{event}] 路由={route or '-'} 数据={data!r}"
                if level in {"error", "critical"}:
                    log.error(text)
                elif level in {"warn", "warning"}:
                    log.warning(text)
                elif level == "debug":
                    log.debug(text)
                else:
                    log.info(text)
                return
        except Exception:
            pass
        log.info("[JS] %s", message)
