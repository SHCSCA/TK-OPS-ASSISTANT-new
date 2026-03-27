"""Activity feed persistence service."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Sequence

from desktop_app.database.models import ActivityLog
from desktop_app.database.repository import Repository


class ActivityService:
    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    def create_activity_log(self, category: str, title: str, **kwargs: Any) -> ActivityLog:
        return self._repo.add(ActivityLog(category=category, title=title, **kwargs))

    def list_activity_logs(self, category: str | None = None) -> Sequence[ActivityLog]:
        return self._repo.list_activity_logs(category=category)

    def list_notifications(self, limit: int = 20) -> list[dict[str, Any]]:
        notifications: list[dict[str, Any]] = []

        for item in self._repo.list_activity_logs()[:limit]:
            payload = self._load_payload(item.payload_json)
            notifications.append(
                {
                    "id": f"activity-{item.id}",
                    "title": item.title,
                    "body": self._notification_body(payload, item.related_entity_type),
                    "tone": self._tone_from_category(item.category),
                    "created_at": self._iso(item.created_at),
                    "source": "activity",
                }
            )

        if len(notifications) < limit:
            remaining = limit - len(notifications)
            for task in self._repo.list_tasks()[:remaining]:
                notifications.append(
                    {
                        "id": f"task-{task.id}",
                        "title": task.title,
                        "body": task.result_summary or self._task_body(task.status, task.task_type),
                        "tone": self._tone_from_task_status(task.status),
                        "created_at": self._iso(task.created_at),
                        "source": "task",
                    }
                )

        notifications.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return notifications[:limit]

    @staticmethod
    def _load_payload(raw: str | None) -> dict[str, Any]:
        if not raw:
            return {}
        try:
            data = json.loads(raw)
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _notification_body(payload: dict[str, Any], related_entity_type: str | None) -> str:
        body = str(payload.get("message") or payload.get("summary") or "").strip()
        if body:
            return body
        if related_entity_type:
            return f"关联实体：{related_entity_type}"
        return "系统记录已同步。"

    @staticmethod
    def _tone_from_category(category: str | None) -> str:
        value = str(category or "").lower()
        if "failed" in value or "error" in value:
            return "error"
        if value in {"error", "warning", "risk"}:
            return "warning"
        if value in {"task", "report", "workflow", "experiment", "seed"}:
            return "success"
        return "info"

    @staticmethod
    def _tone_from_task_status(status: str | None) -> str:
        value = str(status or "").lower()
        if value == "failed":
            return "error"
        if value == "completed":
            return "success"
        if value in {"pending", "paused"}:
            return "warning"
        return "info"

    @staticmethod
    def _task_body(status: str | None, task_type: str | None) -> str:
        status_label = str(status or "pending")
        type_label = str(task_type or "maintenance")
        return f"任务状态：{status_label} / 类型：{type_label}"

    @staticmethod
    def _iso(value: datetime | None) -> str:
        if value is None:
            return ""
        return value.isoformat(timespec="seconds")
