from __future__ import annotations

"""Thread-safe cooperative cancellation primitives for runtime workers."""

from threading import Event, Lock
from weakref import WeakSet


class CancelledException(Exception):
    """Raised when an operation detects that cancellation was requested."""


class CancellationToken:
    """Thread-safe cooperative cancellation token.

    The token is intentionally lightweight and can be shared across worker
    functions, streaming callbacks, and long-running command handlers.
    """

    def __init__(self) -> None:
        self._event: Event = Event()

    @property
    def is_cancelled(self) -> bool:
        """Return ``True`` when cancellation has been requested."""

        return self._event.is_set()

    def cancel(self) -> None:
        """Request cancellation for all code paths using this token."""

        self._event.set()

    def reset(self) -> None:
        """Clear the cancellation request so the token can be reused."""

        self._event.clear()

    def check(self) -> None:
        """Raise :class:`CancelledException` if cancellation was requested."""

        if self.is_cancelled:
            raise CancelledException("Operation was cancelled.")


class CancellationTokenSource:
    """Creates and manages multiple cancellation tokens.

    Tokens are tracked in a :class:`weakref.WeakSet` to avoid retaining them
    longer than necessary.
    """

    def __init__(self) -> None:
        self._tokens: WeakSet[CancellationToken] = WeakSet()
        self._lock: Lock = Lock()

    def create_token(self) -> CancellationToken:
        """Create a new token and register it with the source."""

        token = CancellationToken()
        with self._lock:
            self._tokens.add(token)
        return token

    def cancel_all(self) -> None:
        """Request cancellation for every live token created by this source."""

        with self._lock:
            tokens = tuple(self._tokens)

        for token in tokens:
            token.cancel()
