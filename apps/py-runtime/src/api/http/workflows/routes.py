from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from api.http.common.envelope import ok
from bootstrap.container import RuntimeContainer
from desktop_app.database.repository import Repository
from desktop_app.services.workflow_service import WorkflowService
from legacy_adapter.serializers import serialize_workflow_definition, serialize_workflow_run


class CreateWorkflowDefinitionPayload(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    status: str = Field(default="draft")
    description: str | None = Field(default=None)
    config_json: str | None = Field(default=None, alias="configJson")

    model_config = {"populate_by_name": True}


class CreateWorkflowRunPayload(BaseModel):
    workflow_definition_id: int = Field(alias="workflowDefinitionId", gt=0)
    status: str = Field(default="pending")
    input_json: str | None = Field(default=None, alias="inputJson")
    result_json: str | None = Field(default=None, alias="resultJson")

    model_config = {"populate_by_name": True}


def build_workflows_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/workflows", tags=["workflows"])

    @router.get("/definitions")
    def list_workflow_definitions() -> dict[str, object]:
        repo = Repository()
        try:
            service = WorkflowService(repo)
            items = [serialize_workflow_definition(item) for item in service.list_workflow_definitions()]
            return ok({"items": items, "total": len(items)})
        finally:
            repo.reset_session()

    @router.post("/definitions")
    def create_workflow_definition(payload: CreateWorkflowDefinitionPayload):
        repo = Repository()
        try:
            service = WorkflowService(repo)
            item = service.create_workflow_definition(
                payload.name.strip(),
                status=payload.status,
                description=payload.description,
                config_json=payload.config_json or "{}",
            )
            return ok(serialize_workflow_definition(item))
        finally:
            repo.reset_session()

    @router.get("/runs")
    def list_workflow_runs(
        definition_id: int | None = Query(default=None, alias="definitionId", ge=1),
    ) -> dict[str, object]:
        repo = Repository()
        try:
            service = WorkflowService(repo)
            items = [
                serialize_workflow_run(item)
                for item in service.list_workflow_runs(workflow_definition_id=definition_id)
            ]
            return ok({"items": items, "total": len(items)})
        finally:
            repo.reset_session()

    @router.post("/runs")
    def start_workflow_run(payload: CreateWorkflowRunPayload):
        repo = Repository()
        try:
            service = WorkflowService(repo)
            item = service.create_workflow_run(
                payload.workflow_definition_id,
                status=payload.status,
                input_json=payload.input_json,
                result_json=payload.result_json,
            )
            return ok(serialize_workflow_run(item))
        finally:
            repo.reset_session()

    return router