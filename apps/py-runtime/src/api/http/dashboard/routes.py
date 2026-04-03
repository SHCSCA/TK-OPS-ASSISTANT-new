from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Query

from api.http.common.envelope import ok
from bootstrap.container import RuntimeContainer


def build_dashboard_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/dashboard", tags=["dashboard"])

    @router.get("/overview")
    def get_overview(
        range: Literal["today", "7d", "30d"] = Query(default="today"),
    ) -> dict[str, object]:
        return ok(container.legacy_facade.get_dashboard_overview(range))

    return router
