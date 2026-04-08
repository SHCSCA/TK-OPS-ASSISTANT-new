from __future__ import annotations

import datetime as dt
from typing import Any

from desktop_app.database.models import (
    AIProvider,
    Account,
    ActivityLog,
    ExperimentProject,
    ExperimentView,
    Task,
    VideoClip,
    VideoExport,
    VideoProject,
    VideoSequence,
    VideoSnapshot,
    VideoSubtitle,
    WorkflowDefinition,
    WorkflowRun,
)


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
        "proxyIp": account.device.proxy_ip if account.device else None,
        "boundEnvironment": account.device.name if account.device else None,
        "tags": account.tags,
        "notes": account.notes,
        "cookieStatus": account.cookie_status,
        "cookieContent": account.cookie_content,
        "cookieUpdatedAt": to_iso(account.cookie_updated_at),
        "isolationEnabled": bool(account.isolation_enabled),
        "lastLoginAt": to_iso(account.last_login_at),
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


def serialize_experiment_project(project: ExperimentProject) -> dict[str, Any]:
    return {
        "id": project.id,
        "name": project.name,
        "goal": project.goal,
        "status": project.status,
        "configJson": project.config_json,
        "createdAt": to_iso(project.created_at),
        "updatedAt": to_iso(project.updated_at),
    }


def serialize_experiment_view(view: ExperimentView) -> dict[str, Any]:
    return {
        "id": view.id,
        "experimentProjectId": view.experiment_project_id,
        "name": view.name,
        "layoutJson": view.layout_json,
        "createdAt": to_iso(view.created_at),
        "updatedAt": to_iso(view.updated_at),
    }


def serialize_activity_log(item: ActivityLog) -> dict[str, Any]:
    return {
        "id": item.id,
        "category": item.category,
        "title": item.title,
        "payloadJson": item.payload_json,
        "relatedEntityType": item.related_entity_type,
        "relatedEntityId": item.related_entity_id,
        "createdAt": to_iso(item.created_at),
    }


def serialize_workflow_definition(item: WorkflowDefinition) -> dict[str, Any]:
    return {
        "id": item.id,
        "name": item.name,
        "status": item.status,
        "description": item.description,
        "configJson": item.config_json,
        "createdAt": to_iso(item.created_at),
        "updatedAt": to_iso(item.updated_at),
    }


def serialize_workflow_run(item: WorkflowRun) -> dict[str, Any]:
    return {
        "id": item.id,
        "workflowDefinitionId": item.workflow_definition_id,
        "status": item.status,
        "inputJson": item.input_json,
        "resultJson": item.result_json,
        "startedAt": to_iso(item.started_at),
        "finishedAt": to_iso(item.finished_at),
        "createdAt": to_iso(item.created_at),
    }


def serialize_video_project(item: VideoProject) -> dict[str, Any]:
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "activeSequenceId": item.active_sequence_id,
        "metaJson": item.meta_json,
        "createdAt": to_iso(item.created_at),
        "updatedAt": to_iso(item.updated_at),
    }


def serialize_video_sequence(item: VideoSequence) -> dict[str, Any]:
    return {
        "id": item.id,
        "projectId": item.project_id,
        "name": item.name,
        "durationMs": int(item.duration_ms or 0),
        "fps": float(item.fps or 0),
        "width": int(item.width or 0),
        "height": int(item.height or 0),
        "metaJson": item.meta_json,
        "isActive": bool(item.project and item.project.active_sequence_id == item.id),
        "createdAt": to_iso(item.created_at),
        "updatedAt": to_iso(item.updated_at),
    }


def serialize_video_clip(item: VideoClip) -> dict[str, Any]:
    return {
        "id": item.id,
        "sequenceId": item.sequence_id,
        "assetId": item.asset_id,
        "trackType": item.track_type,
        "trackIndex": int(item.track_index or 0),
        "sortOrder": int(item.sort_order or 0),
        "startMs": int(item.start_ms or 0),
        "sourceInMs": int(item.source_in_ms or 0),
        "sourceOutMs": int(item.source_out_ms or 0),
        "durationMs": int(item.duration_ms or 0),
        "speed": float(item.speed or 0),
        "volume": float(item.volume or 0),
        "metaJson": item.meta_json,
        "createdAt": to_iso(item.created_at),
        "updatedAt": to_iso(item.updated_at),
    }


def serialize_video_subtitle(item: VideoSubtitle) -> dict[str, Any]:
    return {
        "id": item.id,
        "sequenceId": item.sequence_id,
        "startMs": int(item.start_ms or 0),
        "endMs": int(item.end_ms or 0),
        "text": item.text,
        "styleJson": item.style_json,
        "createdAt": to_iso(item.created_at),
        "updatedAt": to_iso(item.updated_at),
    }


def serialize_video_export(item: VideoExport) -> dict[str, Any]:
    return {
        "id": item.id,
        "projectId": item.project_id,
        "sequenceId": item.sequence_id,
        "preset": item.preset,
        "status": item.status,
        "outputPath": item.output_path,
        "ffmpegCommand": item.ffmpeg_command,
        "errorMessage": item.error_message,
        "progress": int(item.progress or 0),
        "startedAt": to_iso(item.started_at),
        "finishedAt": to_iso(item.finished_at),
        "createdAt": to_iso(item.created_at),
    }


def serialize_video_snapshot(item: VideoSnapshot) -> dict[str, Any]:
    return {
        "id": item.id,
        "projectId": item.project_id,
        "title": item.title,
        "createdAt": to_iso(item.created_at),
    }
