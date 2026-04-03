from __future__ import annotations

from fastapi import APIRouter, WebSocket

from api.ws.ws_common import WS_CLOSE_UNAUTHORIZED, send_runtime_handshake, websocket_has_valid_token
from bootstrap.settings import RuntimeSettings

RUNTIME_STATUS_EVENT = "runtime.status"


def build_runtime_status_payload(status: str) -> dict[str, object]:
    return {"type": RUNTIME_STATUS_EVENT, "payload": {"status": status}}


def build_runtime_status_router(version: str, settings: RuntimeSettings) -> APIRouter:
    router = APIRouter()

    @router.websocket("/ws/runtime-status")
    async def runtime_status(websocket: WebSocket) -> None:
        if not websocket_has_valid_token(websocket, settings):
            await websocket.close(code=WS_CLOSE_UNAUTHORIZED, reason="invalid runtime token")
            return
        await websocket.accept()
        await send_runtime_handshake(
            websocket,
            channel="runtime-status",
            app_version=version,
        )
        payload = build_runtime_status_payload("ready")
        payload["payload"]["version"] = version
        await websocket.send_json(payload)
        await websocket.close()

    return router
