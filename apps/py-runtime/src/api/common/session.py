from __future__ import annotations

from fastapi import Request, WebSocket

from bootstrap.settings import RuntimeSettings

TOKEN_HEADER = "X-TKOPS-Token"
TOKEN_QUERY_KEY = "token"
PROTOCOL_VERSION = "2026-04-01"
WS_HANDSHAKE_EVENT = "runtime.handshake"
HEALTH_PATH = "/health"


def is_authorized_session_token(raw_token: str | None, settings: RuntimeSettings) -> bool:
    return bool(raw_token) and raw_token == settings.session_token


def extract_http_token(request: Request) -> str | None:
    return request.headers.get(TOKEN_HEADER)


def extract_ws_token(websocket: WebSocket) -> str | None:
    return websocket.query_params.get(TOKEN_QUERY_KEY) or websocket.headers.get(TOKEN_HEADER)


def build_ws_handshake_payload(*, channel: str, app_version: str) -> dict[str, object]:
    return {
        "type": WS_HANDSHAKE_EVENT,
        "payload": {
            "channel": channel,
            "protocolVersion": PROTOCOL_VERSION,
            "appVersion": app_version,
            "auth": {"scheme": "session_token"},
        },
    }


def is_public_http_path(path: str) -> bool:
    return path == HEALTH_PATH
