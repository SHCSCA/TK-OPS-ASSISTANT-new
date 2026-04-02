from __future__ import annotations

import datetime as dt

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api.http.common.envelope import err, ok
from bootstrap.container import RuntimeContainer
from desktop_app.database.repository import Repository
from desktop_app.services.task_service import TaskService
from legacy_adapter.serializers import serialize_task


class CreateSchedulePayload(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    task_type: str = Field(default="maintenance", alias="taskType")
    priority: str = Field(default="medium")
    scheduled_at: dt.datetime = Field(alias="scheduledAt")
    account_id: int | None = Field(default=None, alias="accountId")
    result_summary: str | None = Field(default=None, alias="resultSummary")

    model_config = {"populate_by_name": True}


def _not_found(message: str) -> JSONResponse:
    return JSONResponse(status_code=404, content=err("resource.not_found", message))


def build_scheduler_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/scheduler", tags=["scheduler"])

    @router.get("")
    def get_scheduler_overview() -> dict[str, object]:
        return ok(container.legacy_facade.get_scheduler_overview())

    @router.post("")
    def create_schedule(payload: CreateSchedulePayload):
        repo = Repository()
        try:
            service = TaskService(repo)
            task = service.create_task(
                payload.title.strip(),
                task_type=payload.task_type,
                priority=payload.priority,
                account_id=payload.account_id,
                scheduled_at=payload.scheduled_at,
                result_summary=payload.result_summary or "新建调度任务",
            )
            return ok(serialize_task(task))
        finally:
            repo.reset_session()

    @router.post("/{task_id}/toggle")
    def toggle_schedule(task_id: int):
        repo = Repository()
        try:
            service = TaskService(repo)
            task = service.get_task(task_id)
            if task is None or task.scheduled_at is None:
                return _not_found("调度任务不存在，无法切换状态。")

            next_status = "pending" if task.status == "paused" else "paused"
            updated = service.update_task(task_id, status=next_status)
            if updated is None:
                return _not_found("调度任务不存在，无法切换状态。")
            return ok(serialize_task(updated))
        finally:
            repo.reset_session()

    @router.delete("/{task_id}")
    def delete_schedule(task_id: int):
        repo = Repository()
        try:
            service = TaskService(repo)
            task = service.get_task(task_id)
            if task is None or task.scheduled_at is None:
                return _not_found("调度任务不存在，无法删除。")
            service.delete_task(task_id)
            return ok({"deleted": True, "taskId": task_id})
        finally:
            repo.reset_session()

    return router
