from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api.http.common.envelope import err, ok
from bootstrap.container import RuntimeContainer
from desktop_app.database.repository import Repository
from desktop_app.services.task_service import TaskService
from legacy_adapter.serializers import serialize_task


class CreateTaskPayload(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    task_type: str = Field(default="maintenance", alias="taskType")
    priority: str = Field(default="medium")
    account_id: int | None = Field(default=None, alias="accountId")
    scheduled_at: dt.datetime | None = Field(default=None, alias="scheduledAt")
    result_summary: str | None = Field(default=None, alias="resultSummary")

    model_config = {"populate_by_name": True}


def _not_found(message: str) -> JSONResponse:
    return JSONResponse(status_code=404, content=err("resource.not_found", message))


def build_tasks_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/tasks", tags=["tasks"])

    @router.get("")
    def list_tasks(
        status: str | None = None,
        limit: int = Query(default=20, ge=1, le=100),
    ) -> dict[str, object]:
        tasks = container.legacy_facade.list_tasks(status=status, limit=limit)
        return ok({"items": tasks, "total": len(tasks)})

    @router.post("")
    def create_task(payload: CreateTaskPayload):
        repo = Repository()
        try:
            service = TaskService(repo)
            task = service.create_task(
                payload.title.strip(),
                task_type=payload.task_type,
                priority=payload.priority,
                account_id=payload.account_id,
                scheduled_at=payload.scheduled_at,
                result_summary=payload.result_summary,
            )
            return ok(serialize_task(task))
        finally:
            repo.reset_session()

    @router.post("/{task_id}/start")
    def start_task(task_id: int):
        repo = Repository()
        try:
            service = TaskService(repo)
            task = service.start_task(task_id)
            if task is None:
                return _not_found("任务不存在，无法启动。")
            return ok(serialize_task(task))
        finally:
            repo.reset_session()

    @router.delete("/{task_id}")
    def delete_task(task_id: int):
        repo = Repository()
        try:
            service = TaskService(repo)
            deleted = service.delete_task(task_id)
            if not deleted:
                return _not_found("任务不存在，无法删除。")
            return ok({"deleted": True, "taskId": task_id})
        finally:
            repo.reset_session()

    return router
