from __future__ import annotations

# pyright: basic

"""Data layer package exposing database and repository primitives."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .database import Database as Database


def __getattr__(name: str) -> object:
    if name == "Database":
        from .database import Database

        return Database
    raise AttributeError(name)

__all__ = ["Database"]
