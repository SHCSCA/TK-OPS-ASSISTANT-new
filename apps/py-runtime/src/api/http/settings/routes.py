from __future__ import annotations

from fastapi import APIRouter

from api.http.common.envelope import ok
from bootstrap.container import RuntimeContainer


def build_settings_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/settings", tags=["settings"])

    @router.get("")
    def get_settings() -> dict[str, object]:
        return ok(container.legacy_facade.get_settings())

    @router.post("")
    def save_settings(payload: dict[str, object]) -> dict[str, object]:
        return ok(container.legacy_facade.save_settings(payload))

    @router.post("/setup")
    def save_setup(payload: dict[str, object]) -> dict[str, object]:
        return ok(container.legacy_facade.save_setup(payload))

    return router
