from __future__ import annotations

from typing import Any


def ok(data: Any) -> dict[str, Any]:
    return {"ok": True, "data": data}


def err(code: str, message: str, *, details: dict[str, Any] | None = None, retryable: bool = False) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "retryable": retryable,
        },
    }