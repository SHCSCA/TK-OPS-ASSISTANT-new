from __future__ import annotations

from fastapi import WebSocket

from bootstrap.settings import RuntimeSettings


WS_CLOSE_UNAUTHORIZED = 4401


def websocket_has_valid_token(websocket: WebSocket, settings: RuntimeSettings) -> bool:
    token = websocket.query_params.get("token") or websocket.headers.get("x-tkops-token")
    return bool(token) and token == settings.session_token
