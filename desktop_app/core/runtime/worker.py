from __future__ import annotations

# pyright: basic

"""Base worker abstractions for background Qt tasks."""

from ..qt import Signal


class WorkerSignals:
    """Signals emitted by placeholder background workers."""

    started = Signal()
    finished = Signal()
    failed = Signal(str)


class WorkerBase:
    """Placeholder worker base for future QThread/QRunnable integrations."""

    def __init__(self, parent: object | None = None) -> None:
        self.parent = parent
        self.signals = WorkerSignals()

    def run(self) -> None:
        """Execute worker logic in a background context."""

        raise NotImplementedError("WorkerBase.run() must be implemented by concrete workers.")
