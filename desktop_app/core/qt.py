from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false, reportUnusedCallResult=false, reportUnannotatedClassAttribute=false

"""Import-safe Qt compatibility layer for the desktop application.

Prefer real PySide6 classes when available; otherwise fall back to lightweight
stand-ins so non-GUI environments can still import modules safely.
"""

try:  # pragma: no cover - real Qt path
    from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
    from PySide6.QtWidgets import (
        QApplication,
        QDialog,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QPushButton,
        QScrollArea,
        QStackedWidget,
        QTableWidget,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover - fallback path

    class Signal:
        """Minimal Qt-like signal placeholder."""

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._subscribers: list[object] = []

        def connect(self, callback: object) -> None:
            self._subscribers.append(callback)

        def emit(self, *args: object, **kwargs: object) -> None:
            for callback in list(self._subscribers):
                if callable(callback):
                    callback(*args, **kwargs)


    def Slot(*_args: object, **_kwargs: object):
        """Minimal Slot decorator placeholder."""

        def decorator(func: object) -> object:
            return func

        return decorator


    class QObject:
        """Fallback QObject."""

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        def moveToThread(self, _thread: object) -> None:
            return None


    class QWidget:
        """Fallback QWidget."""

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        def show(self) -> None:
            return None


    class QApplication:
        """Fallback QApplication."""

        _instance: QApplication | None = None

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            QApplication._instance = self

        @staticmethod
        def instance() -> QApplication | None:
            return QApplication._instance

        def exec(self) -> int:
            return 0

        def quit(self) -> None:
            return None


    class QLabel(QWidget):
        """Fallback QLabel."""

        def __init__(self, text: str = "", *_args: object, **_kwargs: object) -> None:
            super().__init__()
            self._text = text

        def setText(self, text: str) -> None:
            self._text = text


    class QFrame(QWidget):
        """Fallback QFrame."""


    class QPushButton(QWidget):
        """Fallback QPushButton."""

        def __init__(self, text: str = "", *_args: object, **_kwargs: object) -> None:
            super().__init__()
            self.clicked = Signal()

        def setCheckable(self, _value: bool) -> None:
            return None

        def setChecked(self, _value: bool) -> None:
            return None


    class QLineEdit(QWidget):
        """Fallback QLineEdit."""

        def setPlaceholderText(self, _text: str) -> None:
            return None


    class QDialog(QWidget):
        """Fallback QDialog."""

        def setWindowTitle(self, _title: str) -> None:
            return None


    class QMainWindow(QWidget):
        """Fallback QMainWindow."""

        def setWindowTitle(self, _title: str) -> None:
            return None

        def resize(self, _width: int, _height: int) -> None:
            return None

        def setCentralWidget(self, _widget: QWidget) -> None:
            return None


    class _BaseLayout:
        """Fallback layout base."""

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._items: list[object] = []

        def setContentsMargins(self, *_args: int) -> None:
            return None

        def setSpacing(self, _spacing: int) -> None:
            return None

        def addWidget(self, widget: QWidget, *_args: int) -> None:
            self._items.append(widget)

        def addStretch(self, *_args: int) -> None:
            return None


    class QVBoxLayout(_BaseLayout):
        """Fallback vertical layout."""


    class QHBoxLayout(_BaseLayout):
        """Fallback horizontal layout."""


    class QTableWidget(QWidget):
        """Fallback QTableWidget."""

        def setColumnCount(self, _count: int) -> None:
            return None

        def setHorizontalHeaderLabels(self, _labels: list[str]) -> None:
            return None


    class QScrollArea(QWidget):
        """Fallback QScrollArea."""

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            super().__init__()
            self._widget: QWidget | None = None

        def setWidget(self, widget: QWidget) -> None:
            self._widget = widget

        def setWidgetResizable(self, _resizable: bool) -> None:
            return None

        def widget(self) -> QWidget | None:
            return self._widget


    class QStackedWidget(QWidget):
        """Fallback QStackedWidget."""

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            super().__init__()
            self._widgets: list[QWidget] = []
            self._current_index = 0

        def addWidget(self, widget: QWidget) -> int:
            self._widgets.append(widget)
            return len(self._widgets) - 1

        def setCurrentIndex(self, index: int) -> None:
            self._current_index = index


    class QThread:
        """Fallback QThread."""

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self.started = Signal()
            self.finished = Signal()

        def start(self) -> None:
            self.started.emit()

        def quit(self) -> None:
            self.finished.emit()

        def wait(self, _msecs: int | None = None) -> bool:
            return True


    class Qt:
        """Fallback Qt namespace."""

        class AlignmentFlag:
            AlignRight = 0


__all__ = [
    "QApplication",
    "QDialog",
    "QFrame",
    "QHBoxLayout",
    "QLabel",
    "QLineEdit",
    "QMainWindow",
    "QObject",
    "QPushButton",
    "QScrollArea",
    "QStackedWidget",
    "QTableWidget",
    "QThread",
    "QVBoxLayout",
    "QWidget",
    "Qt",
    "Signal",
    "Slot",
]
