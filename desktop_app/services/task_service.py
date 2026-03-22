"""Task queue service."""
from __future__ import annotations

import datetime as _dt
import json
from typing import Any, Sequence

from desktop_app.database.models import Task
from desktop_app.database.repository import Repository


class TaskService:
    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    @staticmethod
    def _normalize_task_type(task_type: str | None) -> str:
        value = str(task_type or "").strip().lower()
        if value in {"publish", "interact", "scrape", "report", "maintenance"}:
            return value
        alias_map = {
            "analytics_action": "report",
            "analytics_workflow": "report",
            "onboarding_finalize": "maintenance",
            "onboarding_followup": "maintenance",
            "permission_role": "maintenance",
        }
        return alias_map.get(value, "maintenance")

    def create_task(self, title: str, **kwargs: Any) -> Task:
        if "task_type" in kwargs:
            kwargs["task_type"] = self._normalize_task_type(kwargs.get("task_type"))
        return self._repo.add(Task(title=title, **kwargs))

    def create_action_task(
        self,
        action_key: str,
        *,
        title: str,
        summary: str = "",
        metadata: dict[str, Any] | None = None,
        task_type: str = "maintenance",
        priority: str = "medium",
        status: str = "pending",
        account_id: int | None = None,
    ) -> Task:
        parts: list[str] = []
        if summary:
            parts.append(summary)
        parts.append(f"action={action_key}")
        if metadata:
            parts.append(json.dumps(metadata, ensure_ascii=False, sort_keys=True))
        return self._repo.add(
            Task(
                title=title,
                task_type=self._normalize_task_type(task_type),
                priority=priority,
                status=status,
                account_id=account_id,
                result_summary=" | ".join(parts),
            )
        )

    def list_tasks(self, *, status: str | None = None) -> Sequence[Task]:
        return self._repo.list_tasks(status=status)

    def get_task(self, pk: int) -> Task | None:
        return self._repo.get_by_id(Task, pk)

    def update_task(self, pk: int, **fields: Any) -> Task | None:
        task = self._repo.get_by_id(Task, pk)
        if task is None:
            return None
        return self._repo.update(task, **fields)

    def start_task(self, pk: int) -> Task | None:
        task = self._repo.get_by_id(Task, pk)
        if task is None:
            return None
        return self._repo.update(task, status="running", started_at=_dt.datetime.now())

    def complete_task(self, pk: int, *, summary: str = "") -> Task | None:
        task = self._repo.get_by_id(Task, pk)
        if task is None:
            return None
        return self._repo.update(
            task,
            status="completed",
            finished_at=_dt.datetime.now(),
            result_summary=summary,
        )

    def fail_task(self, pk: int, *, summary: str = "") -> Task | None:
        task = self._repo.get_by_id(Task, pk)
        if task is None:
            return None
        return self._repo.update(
            task,
            status="failed",
            finished_at=_dt.datetime.now(),
            result_summary=summary,
        )

    def delete_task(self, pk: int) -> bool:
        task = self._repo.get_by_id(Task, pk)
        if task is None:
            return False
        self._repo.delete(task)
        return True
