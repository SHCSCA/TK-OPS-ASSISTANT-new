from __future__ import annotations

import datetime as dt
from typing import Any

from desktop_app.database.models import AIProvider, Account, Task


def to_iso(value: dt.datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def serialize_account(account: Account) -> dict[str, Any]:
    last_login_status = str(account.last_login_check_status or "unknown")
    last_connection_status = str(account.last_connection_status or "unknown")
    if last_login_status and last_login_status != "unknown":
        system_status = last_login_status
    elif last_connection_status:
        system_status = last_connection_status
    else:
        system_status = "unknown"

    return {
        "id": account.id,
        "username": account.username,
        "platform": account.platform,
        "region": account.region,
        "status": account.status,
        "manualStatus": account.status,
        "systemStatus": system_status,
        "riskStatus": getattr(account, "risk_status", "normal") or "normal",
        "followers": int(account.followers or 0),
        "groupId": account.group_id,
        "groupName": account.group.name if account.group else None,
        "deviceId": account.device_id,
        "deviceName": account.device.name if account.device else None,
        "boundEnvironment": account.device.name if account.device else None,
        "cookieStatus": account.cookie_status,
        "lastLoginCheckStatus": account.last_login_check_status,
        "lastLoginCheckAt": to_iso(account.last_login_check_at),
        "lastLoginCheckMessage": account.last_login_check_message,
        "lastConnectionStatus": account.last_connection_status,
        "lastConnectionCheckedAt": to_iso(account.last_connection_checked_at),
        "lastConnectionMessage": account.last_connection_message,
        "recentError": account.last_login_check_message or account.last_connection_message,
        "isArchived": bool(getattr(account, "archived_at", None)),
        "archivedAt": to_iso(getattr(account, "archived_at", None)),
        "archivedReason": getattr(account, "archived_reason", None),
        "createdAt": to_iso(account.created_at),
        "updatedAt": to_iso(account.updated_at),
    }


def serialize_provider(provider: AIProvider | None) -> dict[str, Any] | None:
    if provider is None:
        return None
    return {
        "id": provider.id,
        "name": provider.name,
        "providerType": provider.provider_type,
        "apiBase": provider.api_base,
        "defaultModel": provider.default_model,
        "temperature": float(provider.temperature or 0),
        "maxTokens": int(provider.max_tokens or 0),
        "isActive": bool(provider.is_active),
        "createdAt": to_iso(provider.created_at),
    }


def serialize_task(task: Task) -> dict[str, Any]:
    return {
        "id": task.id,
        "title": task.title,
        "taskType": task.task_type,
        "priority": task.priority,
        "status": task.status,
        "accountId": task.account_id,
        "accountUsername": task.account.username if task.account else None,
        "scheduledAt": to_iso(task.scheduled_at),
        "startedAt": to_iso(task.started_at),
        "finishedAt": to_iso(task.finished_at),
        "resultSummary": task.result_summary,
        "createdAt": to_iso(task.created_at),
    }
