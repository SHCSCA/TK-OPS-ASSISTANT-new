from __future__ import annotations

import logging

from fastapi import APIRouter, WebSocket

from api.ws.ws_common import WS_CLOSE_UNAUTHORIZED, send_runtime_handshake, websocket_has_valid_token
from bootstrap.container import RuntimeContainer

log = logging.getLogger(__name__)


def build_copywriter_stream_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter()

    @router.websocket("/ws/copywriter-stream")
    async def copywriter_stream(websocket: WebSocket) -> None:
        if not websocket_has_valid_token(websocket, container.runtime_settings):
            await websocket.close(code=WS_CLOSE_UNAUTHORIZED, reason="invalid runtime token")
            return
        await websocket.accept()
        await send_runtime_handshake(
            websocket,
            channel="copywriter-stream",
            app_version=container.app_version,
        )
        request = await websocket.receive_json()

        prompt = str(request.get("prompt", "")).strip()
        if not prompt:
            await websocket.send_json(
                {
                    "type": "ai.stream.error",
                    "payload": {"message": "请输入产品信息或写作需求后再生成。"},
                }
            )
            await websocket.close()
            return

        log.info("AI 文案流式生成开始: preset=%s model=%s", request.get("preset"), request.get("model"))
        for event in container.legacy_facade.stream_copywriter(
            prompt=prompt,
            preset_key=request.get("preset"),
            model=request.get("model"),
            temperature=request.get("temperature"),
            max_tokens=request.get("max_tokens"),
        ):
            await websocket.send_json(event)
        await websocket.close()

    return router
