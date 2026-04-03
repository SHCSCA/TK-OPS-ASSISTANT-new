from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from api.common.session import TOKEN_HEADER, extract_http_token, is_authorized_session_token
from api.http.common.envelope import err
from bootstrap.settings import RuntimeSettings


def is_authorized_token(raw_token: str | None, settings: RuntimeSettings) -> bool:
    return is_authorized_session_token(raw_token, settings)


def request_has_valid_token(request: Request, settings: RuntimeSettings) -> bool:
    return is_authorized_token(extract_http_token(request), settings)


def unauthorized_response() -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content=err(
            "auth.invalid_token",
            "运行时令牌无效，请重新连接桌面宿主。",
            retryable=False,
        ),
    )
