from __future__ import annotations

"""Ollama 本地模型的 LiteLLM 适配器。"""

from collections.abc import Mapping, Sequence

from .litellm_adapter import LiteLLMAdapter


class OllamaAdapter(LiteLLMAdapter):
    """封装 Ollama 本地推理端点的 LiteLLM 适配器。"""

    KNOWN_MODELS: tuple[str, ...] = (
        "llama3.1",
        "qwen2.5",
        "mistral",
        "deepseek-r1",
    )

    def __init__(
        self,
        api_key: str | None = None,
        api_base: str | None = "http://localhost:11434",
        custom_headers: Mapping[str, str] | None = None,
        *,
        known_models: Sequence[str] | None = None,
    ) -> None:
        super().__init__(
            provider_name="ollama",
            api_key=api_key,
            api_base=api_base,
            custom_headers=custom_headers,
            known_models=known_models or self.KNOWN_MODELS,
            requires_api_key=False,
            litellm_provider="ollama",
        )


__all__ = ["OllamaAdapter"]
