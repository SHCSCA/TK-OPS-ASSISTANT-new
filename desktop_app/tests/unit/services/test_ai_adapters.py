from __future__ import annotations

from collections.abc import Sequence

from ....services.ai.adapters.anthropic_adapter import AnthropicAdapter
from ....services.ai.adapters.ollama_adapter import OllamaAdapter
from ....services.ai.adapters.openai_adapter import OpenAIAdapter
from ....services.ai.adapters.openai_compatible_adapter import OpenAICompatibleAdapter
from ....services.ai.provider_adapter import ProviderAdapter


def test_provider_adapter_is_runtime_checkable() -> None:
    assert getattr(ProviderAdapter, "_is_runtime_protocol", False) is True


def test_openai_adapter_implements_protocol() -> None:
    adapter = OpenAIAdapter(api_key="test-key")

    assert isinstance(adapter, ProviderAdapter)
    assert hasattr(adapter, "provider_name")
    assert callable(adapter.list_models)
    assert callable(adapter.validate_configuration)
    assert callable(adapter.generate)
    assert callable(adapter.stream)


def test_anthropic_adapter_implements_protocol() -> None:
    adapter = AnthropicAdapter(api_key="test-key")

    assert isinstance(adapter, ProviderAdapter)
    assert hasattr(adapter, "provider_name")
    assert callable(adapter.list_models)
    assert callable(adapter.validate_configuration)
    assert callable(adapter.generate)
    assert callable(adapter.stream)


def test_ollama_adapter_implements_protocol() -> None:
    adapter = OllamaAdapter()

    assert isinstance(adapter, ProviderAdapter)
    assert hasattr(adapter, "provider_name")
    assert callable(adapter.list_models)
    assert callable(adapter.validate_configuration)
    assert callable(adapter.generate)
    assert callable(adapter.stream)


def test_openai_compatible_adapter_implements_protocol() -> None:
    adapter = OpenAICompatibleAdapter(api_base="http://localhost:8000/v1")

    assert isinstance(adapter, ProviderAdapter)
    assert hasattr(adapter, "provider_name")
    assert callable(adapter.list_models)
    assert callable(adapter.validate_configuration)
    assert callable(adapter.generate)
    assert callable(adapter.stream)


def test_adapter_provider_name_is_string() -> None:
    adapters = [
        OpenAIAdapter(api_key="test-key"),
        AnthropicAdapter(api_key="test-key"),
        OllamaAdapter(),
        OpenAICompatibleAdapter(api_base="http://localhost:8000/v1"),
    ]

    assert all(isinstance(adapter.provider_name, str) for adapter in adapters)
    assert all(adapter.provider_name for adapter in adapters)


def test_adapter_list_models_returns_sequence() -> None:
    adapters = [
        OpenAIAdapter(api_key="test-key"),
        AnthropicAdapter(api_key="test-key"),
        OllamaAdapter(),
        OpenAICompatibleAdapter(api_base="http://localhost:8000/v1", known_models=["custom-model"]),
    ]

    for adapter in adapters:
        models = adapter.list_models()
        assert isinstance(models, Sequence)
        assert all(isinstance(model, str) for model in models)


def test_adapter_validate_configuration_callable() -> None:
    adapter = OpenAICompatibleAdapter(api_base="http://localhost:8000/v1", known_models=["custom-model"])

    assert callable(adapter.validate_configuration)
    assert adapter.validate_configuration(
        {
            "provider_name": "openai_compatible",
            "api_base": "http://localhost:8000/v1",
            "model": "custom-model",
        }
    ) is True


def test_openai_compatible_adapter_accepts_custom_provider_name() -> None:
    adapter = OpenAICompatibleAdapter(provider_name="my-gateway", api_base="http://localhost:8000/v1")

    assert adapter.provider_name == "my-gateway"
