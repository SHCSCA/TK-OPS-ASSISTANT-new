from __future__ import annotations

# pyright: basic

"""Typed Qt signal containers shared across the shell skeleton."""

from .qt import QObject, Signal


class CoreSignalHub(QObject):
    """Namespace-like QObject exposing reusable shell/runtime signals."""

    route_requested = Signal(str)
    route_changed = Signal(str)
    config_value_changed = Signal(str, object)
    theme_mode_changed = Signal(str)
    event_published = Signal(str, object)

    def __init__(self, parent: object | None = None) -> None:
        super().__init__(parent)
