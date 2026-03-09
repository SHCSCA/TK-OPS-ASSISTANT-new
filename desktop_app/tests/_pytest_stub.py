from __future__ import annotations

"""Tiny pytest fixture decorator stub for skeleton-only environments."""

from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., object])


def fixture(*_args: object, **_kwargs: object) -> Callable[[F], F]:
    """Return a no-op fixture decorator compatible with skeleton imports."""

    def decorator(func: F) -> F:
        return func

    return decorator
