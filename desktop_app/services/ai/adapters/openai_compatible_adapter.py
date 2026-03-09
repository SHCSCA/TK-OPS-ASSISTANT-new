from __future__ import annotations

"""OpenAI 兼容接口的 LiteLLM 适配器。"""

from collections.abc import Mapping, Sequence

from ....core.security.secret_store import SecretStore
from .litellm_adapter import LiteLLMAdapter


class OpenAICompatibleAdapter(LiteLLMAdapter):
    """适配任意 OpenAI 兼容协议端点。"""

    def __init__(
        self,
        provider_name: str = "openai_compatible",
        api_key: str | None = None,
        api_base: str | None = None,
        custom_headers: Mapping[str, str] | None = None,
        *,
        known_models: Sequence[str] | None = None,
        secret_store: SecretStore | None = None,
    ) -> None:
        super().__init__(
            provider_name=provider_name,
            api_key=api_key,
            api_base=api_base,
            custom_headers=custom_headers,
            known_models=known_models,
            requires_api_key=False,
            requires_api_base=True,
            litellm_provider="openai",
            secret_store=secret_store,
        )


__all__ = ["OpenAICompatibleAdapter"]
