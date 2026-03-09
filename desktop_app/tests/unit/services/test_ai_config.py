from __future__ import annotations

from dataclasses import FrozenInstanceError
from collections.abc import Mapping, Sequence

from ....services.ai.config_service import AIConfigService, AIModelDescriptor, ProviderSelection
from ....services.ai.provider_adapter import MessagePayload, ProviderAdapter, ResponsePayload
from ...fakes.services import FakeAIConfigService


class DummyAdapter:
    provider_name: str = "dummy-provider"

    def list_models(self) -> list[str]:
        return ["dummy-model", "dummy-model-2"]

    def validate_configuration(self, config: Mapping[str, object]) -> bool:
        return bool(config)

    def generate(
        self,
        *,
        model: str,
        messages: Sequence[MessagePayload],
        temperature: float = 0.0,
    ) -> ResponsePayload:
        return {"ok": True, "model": model, "messages": messages, "temperature": temperature}

    def stream(
        self,
        *,
        model: str,
        messages: Sequence[MessagePayload],
        temperature: float = 0.0,
    ) -> Sequence[ResponsePayload]:
        return [{"ok": True, "model": model, "messages": messages, "temperature": temperature}]


def test_ai_config_service_name_constant() -> None:
    assert AIConfigService.service_name == "ai_config"


def test_ai_model_descriptor_creation() -> None:
    descriptor = AIModelDescriptor(
        provider_name="openai",
        model_name="gpt-4o",
        display_name="GPT-4o",
        supports_streaming=True,
    )

    assert descriptor.provider_name == "openai"
    assert descriptor.model_name == "gpt-4o"
    assert descriptor.display_name == "GPT-4o"
    assert descriptor.supports_streaming is True


def test_provider_selection_creation() -> None:
    selection = ProviderSelection(provider_name="anthropic", model_name="claude-3-5-sonnet")

    assert selection.provider_name == "anthropic"
    assert selection.model_name == "claude-3-5-sonnet"


def test_fake_ai_config_service_initialize_shutdown() -> None:
    service = FakeAIConfigService()

    assert service.initialize() is None
    assert service.shutdown() is None


def test_fake_ai_config_service_list_providers() -> None:
    service = FakeAIConfigService()

    assert service.list_provider_names() == ["mock-provider"]


def test_fake_ai_config_service_list_models() -> None:
    service = FakeAIConfigService()

    models = service.list_models("mock-provider")

    assert len(models) == 1
    assert models[0] == AIModelDescriptor(
        provider_name="mock-provider",
        model_name="mock-model",
        display_name="Mock Model",
        supports_streaming=False,
    )


def test_fake_ai_config_service_get_set_active_selection() -> None:
    service = FakeAIConfigService()
    selection = ProviderSelection(provider_name="mock-provider", model_name="alternate-model")

    service.set_active_selection(selection)

    assert service.get_active_selection() == selection


def test_fake_ai_config_service_set_active_selection_adds_missing_model() -> None:
    service = FakeAIConfigService()
    selection = ProviderSelection(provider_name="mock-provider", model_name="new-model")

    service.set_active_selection(selection)
    models = service.list_models("mock-provider")

    assert any(model.model_name == "new-model" for model in models)
    assert service.get_active_selection().model_name == "new-model"


def test_fake_ai_config_service_register_provider() -> None:
    service = FakeAIConfigService()
    adapter: ProviderAdapter = DummyAdapter()

    service.register_provider(adapter)

    assert "dummy-provider" in service.list_provider_names()
    models = service.list_models("dummy-provider")
    assert len(models) == 1
    assert models[0].display_name == "dummy-provider Default Model"


def test_fake_ai_config_service_unregister_provider() -> None:
    service = FakeAIConfigService()
    service.register_provider(DummyAdapter())

    service.unregister_provider("dummy-provider")

    assert "dummy-provider" not in service.list_provider_names()
    assert service.list_models("dummy-provider") == []


def test_fake_ai_config_service_unregister_provider_reassigns_active_selection() -> None:
    service = FakeAIConfigService()
    service.register_provider(DummyAdapter())
    service.set_active_selection(ProviderSelection(provider_name="dummy-provider", model_name="default-model"))

    service.unregister_provider("dummy-provider")

    assert service.get_active_selection() == ProviderSelection(
        provider_name="mock-provider",
        model_name="mock-model",
    )


def test_fake_ai_config_service_healthcheck() -> None:
    service = FakeAIConfigService(provider_name="provider-a", model_name="model-a")

    health = service.healthcheck()

    assert health == {
        "service": "ai_config",
        "status": "ok",
        "active_provider": "provider-a",
        "active_model": "model-a",
    }


def test_provider_selection_immutable() -> None:
    selection = ProviderSelection(provider_name="openai", model_name="gpt-4o")

    try:
        setattr(selection, "model_name", "gpt-4o-mini")
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("ProviderSelection should be immutable")
