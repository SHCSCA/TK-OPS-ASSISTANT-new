from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from api.http.common.envelope import ok
from bootstrap.container import RuntimeContainer
from desktop_app.database.repository import Repository
from desktop_app.services.activity_service import ActivityService
from legacy_adapter.serializers import serialize_activity_log


class CreateActivityLogPayload(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    payload_json: str | None = Field(default=None, alias="payloadJson")
    related_entity_type: str | None = Field(default=None, alias="relatedEntityType")
    related_entity_id: int | None = Field(default=None, alias="relatedEntityId")

    model_config = {"populate_by_name": True}


def build_activity_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/activity", tags=["activity"])

    @router.get("/logs")
    def list_activity_logs(
        limit: int = Query(default=20, ge=1, le=100),
        category: str | None = None,
    ) -> dict[str, object]:
        items = container.legacy_facade.list_activity_logs(category=category, limit=limit)
        return ok({"items": items, "total": len(items)})

    @router.post("/logs")
    def create_activity_log(payload: CreateActivityLogPayload):
        repo = Repository()
        try:
            service = ActivityService(repo)
            item = service.create_activity_log(
                payload.category,
                payload.title,
                payload_json=payload.payload_json,
                related_entity_type=payload.related_entity_type,
                related_entity_id=payload.related_entity_id,
            )
            return ok(serialize_activity_log(item))
        finally:
            repo.reset_session()

    return router