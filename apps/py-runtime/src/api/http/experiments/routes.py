from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from api.http.common.envelope import ok
from bootstrap.container import RuntimeContainer
from desktop_app.database.repository import Repository
from desktop_app.services.analytics_service import AnalyticsService
from legacy_adapter.serializers import serialize_experiment_project, serialize_experiment_view


class CreateExperimentProjectPayload(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    goal: str | None = Field(default=None)
    status: str = Field(default="active")
    config_json: str | None = Field(default=None, alias="configJson")

    model_config = {"populate_by_name": True}


class CreateExperimentViewPayload(BaseModel):
    experiment_project_id: int = Field(alias="experimentProjectId", gt=0)
    name: str = Field(min_length=1, max_length=160)
    layout_json: str | None = Field(default=None, alias="layoutJson")

    model_config = {"populate_by_name": True}


def build_experiments_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/experiments", tags=["experiments"])

    @router.get("/projects")
    def list_experiment_projects() -> dict[str, object]:
        projects = container.legacy_facade.list_experiment_projects()
        return ok({"items": projects, "total": len(projects)})

    @router.post("/projects")
    def create_experiment_project(payload: CreateExperimentProjectPayload):
        repo = Repository()
        try:
            service = AnalyticsService(repo)
            project = service.create_experiment_project(
                payload.name.strip(),
                goal=payload.goal,
                status=payload.status,
                config_json=payload.config_json or "{}",
            )
            return ok(serialize_experiment_project(project))
        finally:
            repo.reset_session()

    @router.get("/views")
    def list_experiment_views(
        project_id: int | None = Query(default=None, alias="projectId", ge=1),
    ) -> dict[str, object]:
        views = container.legacy_facade.list_experiment_views(project_id=project_id)
        return ok({"items": views, "total": len(views)})

    @router.post("/views")
    def create_experiment_view(payload: CreateExperimentViewPayload):
        repo = Repository()
        try:
            service = AnalyticsService(repo)
            view = service.create_experiment_view(
                payload.experiment_project_id,
                payload.name.strip(),
                layout_json=payload.layout_json or "{}",
            )
            return ok(serialize_experiment_view(view))
        finally:
            repo.reset_session()

    return router