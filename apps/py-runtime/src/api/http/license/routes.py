from __future__ import annotations

from fastapi import APIRouter

from api.http.common.envelope import ok
from bootstrap.container import RuntimeContainer


def build_license_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/license", tags=["license"])

    @router.get("/status")
    def get_license_status() -> dict[str, object]:
        return ok(container.legacy_facade.get_license_status())

    return router