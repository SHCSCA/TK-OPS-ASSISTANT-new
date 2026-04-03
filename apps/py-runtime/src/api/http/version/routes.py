from __future__ import annotations

from fastapi import APIRouter

from api.http.common.envelope import ok
from bootstrap.container import RuntimeContainer


def build_version_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/version", tags=["version"])

    @router.get("/current")
    def current_version() -> dict[str, object]:
        return ok(container.legacy_facade.get_app_version())

    @router.get("/check")
    def check_update() -> dict[str, object]:
        return ok(container.legacy_facade.check_for_update())

    return router

