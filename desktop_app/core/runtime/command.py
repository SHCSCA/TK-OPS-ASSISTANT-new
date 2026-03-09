from __future__ import annotations

"""Command registration and dispatch primitives for the runtime layer."""

from threading import RLock
from typing import Callable, Protocol, runtime_checkable

from ..types import CommandName


@runtime_checkable
class Command(Protocol):
    """Protocol describing an executable command object."""

    name: CommandName

    def execute(self) -> object:
        """Execute the command and return its result."""

    def undo(self) -> None:
        """Undo the command if the implementation supports it."""


class CommandDispatcher:
    """Dispatch commands by name to registered callables."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[..., object]] = {}
        self._lock: RLock = RLock()

    def register(self, name: CommandName, handler: Callable[..., object]) -> None:
        """Register a handler for a command name.

        Raises:
            ValueError: If a different handler is already registered.
        """

        key = str(name)
        with self._lock:
            existing = self._handlers.get(key)
            if existing is not None and existing is not handler:
                raise ValueError(f"Handler already registered for command '{key}'.")

            self._handlers[key] = handler

    def dispatch(self, name: CommandName, **kwargs: object) -> object:
        """Dispatch the named command to its handler.

        Raises:
            KeyError: If no handler is registered for ``name``.
        """

        key = str(name)
        with self._lock:
            handler = self._handlers.get(key)

        if handler is None:
            raise KeyError(f"No handler registered for command '{key}'.")

        return handler(**kwargs)

    def has_handler(self, name: CommandName) -> bool:
        """Return whether a handler is registered for ``name``."""

        with self._lock:
            return str(name) in self._handlers


CommandBus = CommandDispatcher
