from __future__ import annotations

"""Shared service-layer protocols for domain service skeletons."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ServiceBase(Protocol):
    """Common contract implemented by all domain service placeholders."""

    service_name: str

    def initialize(self) -> None:
        """Prepare the service for runtime usage."""

        ...

    def shutdown(self) -> None:
        """Release any runtime resources held by the service."""

        ...

    def healthcheck(self) -> dict[str, object]:
        """Return service health metadata for shell diagnostics."""

        ...
