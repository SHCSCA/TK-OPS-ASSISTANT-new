from __future__ import annotations

"""Anthropic Provider 的 LiteLLM 适配器。"""

from collections.abc import Mapping

from ....core.security.secret_store import SecretStore
from .litellm_adapter import LiteLLMAdapter


class AnthropicAdapter(LiteLLMAdapter):
    """封装 Anthropic 官方接口的 LiteLLM 适配器。"""

    KNOWN_MODELS: tuple[str, ...] = (
        "claude-3-5-sonnet",
        "claude-3-opus",
        "claude-3-haiku",
    )

    def __init__(
        self,
        api_key: str | None = None,
        api_base: str | None = None,
        custom_headers: Mapping[str, str] | None = None,
        *,
        secret_store: SecretStore | None = None,
    ) -> None:
        super().__init__(
            provider_name="anthropic",
            api_key=api_key,
            api_base=api_base,
            custom_headers=custom_headers,
            known_models=self.KNOWN_MODELS,
            requires_api_key=True,
            litellm_provider="anthropic",
            secret_store=secret_store,
            default_env_var="ANTHROPIC_API_KEY",
        )


__all__ = ["AnthropicAdapter"]
