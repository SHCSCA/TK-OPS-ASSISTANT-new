from __future__ import annotations

"""Dialog component placeholders."""

from ...core.qt import QDialog, QLabel, QVBoxLayout, QWidget


class PlaceholderDialog(QDialog):
    """Modal placeholder for future flows."""

    def __init__(self, title: str = "Dialog", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        if hasattr(self, "setWindowTitle"):
            self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Pending implementation"))
