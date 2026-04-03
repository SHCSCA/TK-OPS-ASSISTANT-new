from __future__ import annotations

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from test_runtime_api import _build_client


def _open_ws(
    client: TestClient,
    path: str,
    *,
    token_query: str | None = None,
    token_header: str | None = None,
):
    target = path if token_query is None else f"{path}?token={token_query}"
    headers = {} if token_header is None else {"X-TKOPS-Token": token_header}
    return client.websocket_connect(target, headers=headers)


def test_runtime_status_ws_accepts_header_token_when_query_missing() -> None:
    client = _build_client()

    with _open_ws(client, "/ws/runtime-status", token_header="test") as websocket:
        handshake = websocket.receive_json()
        ready = websocket.receive_json()

    assert handshake["type"] == "runtime.handshake"
    assert handshake["payload"]["channel"] == "runtime-status"
    assert ready["type"] == "runtime.status"


def test_runtime_status_ws_prefers_query_token_when_both_provided() -> None:
    client = _build_client()

    try:
        with _open_ws(
            client,
            "/ws/runtime-status",
            token_query="invalid-query-token",
            token_header="test",
        ) as websocket:
            websocket.receive_json()
    except WebSocketDisconnect as exc:
        assert exc.code == 4401
    else:
        raise AssertionError("Expected websocket auth failure when query token is invalid")


def test_copywriter_ws_accepts_header_token_when_query_missing() -> None:
    client = _build_client()

    with _open_ws(client, "/ws/copywriter-stream", token_header="test") as websocket:
        handshake = websocket.receive_json()
        websocket.send_json({"prompt": "仅测试header token", "preset": "copywriter"})
        first = websocket.receive_json()

    assert handshake["type"] == "runtime.handshake"
    assert handshake["payload"]["channel"] == "copywriter-stream"
    assert first["type"] == "ai.stream.delta"


def test_copywriter_ws_prefers_query_token_when_both_provided() -> None:
    client = _build_client()

    try:
        with _open_ws(
            client,
            "/ws/copywriter-stream",
            token_query="invalid-query-token",
            token_header="test",
        ) as websocket:
            websocket.receive_json()
    except WebSocketDisconnect as exc:
        assert exc.code == 4401
    else:
        raise AssertionError("Expected websocket auth failure when query token is invalid")
