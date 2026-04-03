from __future__ import annotations

from fastapi import WebSocket

from api.common.session import build_ws_handshake_payload, extract_ws_token, is_authorized_session_token
from bootstrap.settings import RuntimeSettings


WS_CLOSE_UNAUTHORIZED = 4401


def websocket_has_valid_token(websocket: WebSocket, settings: RuntimeSettings) -> bool:
    return is_authorized_session_token(extract_ws_token(websocket), settings)


async def send_runtime_handshake(
    websocket: WebSocket,
    *,
    channel: str,
    app_version: str,
) -> None:
    await websocket.send_json(
        build_ws_handshake_payload(
            channel=channel,
            app_version=app_version,
        )
    )
