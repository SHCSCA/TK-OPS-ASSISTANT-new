from __future__ import annotations

# pyright: basic

"""Runtime event bus contract for decoupled shell communication."""

from typing import Any


class EventBus:
    """Placeholder event bus for app-wide pub/sub communication."""

    def subscribe(self, event_name: str, handler: object) -> None:
        """Subscribe a handler to an event stream."""

        _ = (event_name, handler)
        raise NotImplementedError("EventBus.subscribe() will be implemented with runtime dispatching.")

    def publish(self, event_name: str, payload: Any | None = None) -> None:
        """Publish an event to interested subscribers."""

        _ = (event_name, payload)
        raise NotImplementedError("EventBus.publish() will be implemented with runtime dispatching.")
