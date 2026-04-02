from __future__ import annotations

from fastapi import APIRouter

from api.http.common.envelope import ok
from bootstrap.container import RuntimeContainer


def build_copywriter_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/copywriter", tags=["copywriter"])

    @router.get("/bootstrap")
    def get_bootstrap() -> dict[str, object]:
        return ok(container.legacy_facade.get_copywriter_bootstrap())

    return router