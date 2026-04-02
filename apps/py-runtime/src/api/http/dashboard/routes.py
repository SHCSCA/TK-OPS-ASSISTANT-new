from __future__ import annotations

from fastapi import APIRouter

from api.http.common.envelope import ok
from bootstrap.container import RuntimeContainer


def build_dashboard_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/dashboard", tags=["dashboard"])

    @router.get("/overview")
    def get_overview() -> dict[str, object]:
        return ok(container.legacy_facade.get_dashboard_overview())

    return router