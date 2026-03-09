from __future__ import annotations

"""Protocol definitions for pluggable multi-provider AI adapters."""

from typing import Iterable, Mapping, Protocol, Sequence, runtime_checkable

MessagePayload = Mapping[str, object]
ResponsePayload = Mapping[str, object]


@runtime_checkable
class ProviderAdapter(Protocol):
    """Adapter contract for LiteLLM-compatible provider integrations."""

    provider_name: str

    def list_models(self) -> Sequence[str]:
        """Return model identifiers supported by the provider."""

        ...

    def validate_configuration(self, config: Mapping[str, object]) -> bool:
        """Validate provider configuration before it is persisted or used."""

        ...

    def generate(
        self,
        *,
        model: str,
        messages: Sequence[MessagePayload],
        temperature: float = 0.0,
    ) -> ResponsePayload:
        """Return a non-streaming completion payload."""

        ...

    def stream(
        self,
        *,
        model: str,
        messages: Sequence[MessagePayload],
        temperature: float = 0.0,
    ) -> Iterable[ResponsePayload]:
        """Yield streaming completion chunks for the supplied request."""

        ...
