"""Task queue service."""
from __future__ import annotations

import datetime as _dt
from typing import Any, Sequence

from desktop_app.database.models import Task
from desktop_app.database.repository import Repository


class TaskService:
    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    def create_task(self, title: str, **kwargs: Any) -> Task:
        return self._repo.add(Task(title=title, **kwargs))

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
