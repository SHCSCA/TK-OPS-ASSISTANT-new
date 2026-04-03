from __future__ import annotations

from fastapi import APIRouter

from api.http.common.envelope import err, ok
from bootstrap.container import RuntimeContainer


def build_assistant_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/assistant", tags=["assistant"])

    @router.post("/chat")
    def assistant_chat(payload: dict[str, object]) -> dict[str, object]:
        message = str(payload.get("message") or "").strip()
        if not message:
            return err("assistant.invalid_message", "消息不能为空")

        context_payload = payload.get("context")
        history_payload = payload.get("history")
        context = context_payload if isinstance(context_payload, dict) else {}
        history = history_payload if isinstance(history_payload, list) else []
        return ok(
            container.legacy_facade.chat_shell_assistant(
                message=message,
                context=context,
                history=history,
            )
        )

    return router

