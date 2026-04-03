from __future__ import annotations

from fastapi import APIRouter, Query

from api.http.common.envelope import ok
from bootstrap.container import RuntimeContainer


def build_notifications_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/notifications", tags=["notifications"])

    @router.get("")
    def list_notifications(limit: int = Query(default=20, ge=1, le=50)) -> dict[str, object]:
        return ok(container.legacy_facade.list_notifications(limit=limit))

    return router

