from __future__ import annotations

"""Runtime theme engine for token resolution and QSS application."""

from dataclasses import dataclass
from importlib import import_module
from threading import RLock
from typing import Protocol, final

from ..config.bus import ConfigBus
from ..types import ConfigKey, ThemeMode, ThemeTokenName
from .qss import generate_qss, resolve_tokens
from .tokens import get_token_value

THEME_MODE_KEY = ConfigKey("theme.mode")


class _ColorFactory(Protocol):
    def __call__(self, value: str) -> object: ...


@final
class ThemeEngine:
    """Coordinates theme mode, token lookup, and QApplication stylesheet updates."""

    def __init__(self, config_bus: ConfigBus) -> None:
        self._config_bus: ConfigBus = config_bus
        self._lock: RLock = RLock()
        self.theme_changed: _SignalAdapter = _SignalAdapter()
        configured_mode = self._coerce_mode(self._config_bus.get(THEME_MODE_KEY, ThemeMode.LIGHT))
        self._current_mode: ThemeMode = configured_mode
        self._resolved_tokens: dict[str, str] = resolve_tokens(configured_mode)
        self._stylesheet: str = generate_qss(configured_mode)
        self._config_signal: object | None = getattr(self._config_bus, "theme_mode_changed", None)
        self._connect_config_signal()
        self.apply()

    @property
    def current_mode(self) -> ThemeMode:
        """Return the active theme mode."""

        with self._lock:
            return self._current_mode

    def set_mode(self, mode: ThemeMode) -> None:
        """Switch theme, regenerate QSS, apply to QApplication, emit signal."""

        normalized_mode = self._coerce_mode(mode)
        should_emit = False
        should_persist = False
        with self._lock:
            if normalized_mode == self._current_mode:
                return
            self._current_mode = normalized_mode
            self._resolved_tokens = resolve_tokens(normalized_mode)
            self._stylesheet = self.build_stylesheet_for_mode(normalized_mode)
            should_emit = True
            current_config_value = self._coerce_mode(self._config_bus.get(THEME_MODE_KEY, ThemeMode.LIGHT))
            should_persist = current_config_value != normalized_mode

        if should_persist:
            self._config_bus.set(THEME_MODE_KEY, normalized_mode)
        self.apply()
        if should_emit:
            self.theme_changed.emit(normalized_mode.value)

    def toggle(self) -> None:
        """Toggle between light and dark."""

        next_mode = ThemeMode.DARK if self.current_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
        self.set_mode(next_mode)

    def apply(self) -> None:
        """Apply current theme QSS to QApplication.instance()."""

        app = _get_qapplication_instance()
        if app is None:
            return
        with self._lock:
            stylesheet = self._stylesheet
            mode = self._current_mode.value
        set_property = getattr(app, "setProperty", None)
        if callable(set_property):
            _ = set_property("theme.mode", mode)
            _ = set_property("theme_mode", mode)
            _ = set_property("themeMode", mode)
        set_stylesheet = getattr(app, "setStyleSheet", None)
        if callable(set_stylesheet):
            _ = set_stylesheet(stylesheet)

    def get_token(self, name: str | ThemeTokenName) -> str:
        """Get resolved token value for current mode."""

        token_name = str(name)
        with self._lock:
            if token_name in self._resolved_tokens:
                return self._resolved_tokens[token_name]
            mode = self._current_mode
        return get_token_value(token_name, mode)

    def get_color(self, name: str | ThemeTokenName) -> object:
        """Get token as QColor."""

        color_value = self.get_token(name)
        qcolor_type = _get_qcolor_type()
        if qcolor_type is None:
            return _FallbackColor(color_value)
        return qcolor_type(color_value)

    def build_stylesheet(self) -> str:
        """Return the generated stylesheet for the active theme."""

        with self._lock:
            return self._stylesheet

    def build_stylesheet_for_mode(self, mode: ThemeMode) -> str:
        """Generate a stylesheet for a specific theme mode."""

        return generate_qss(mode)

    def _on_config_mode_changed(self, mode_value: str) -> None:
        normalized_mode = self._coerce_mode(mode_value)
        with self._lock:
            if normalized_mode == self._current_mode:
                return
            self._current_mode = normalized_mode
            self._resolved_tokens = resolve_tokens(normalized_mode)
            self._stylesheet = self.build_stylesheet_for_mode(normalized_mode)
        self.apply()
        self.theme_changed.emit(normalized_mode.value)

    def _connect_config_signal(self) -> None:
        connect = getattr(self._config_signal, "connect", None)
        if callable(connect):
            _ = connect(self._on_config_mode_changed)

    @staticmethod
    def _coerce_mode(value: object) -> ThemeMode:
        """Normalize runtime/config values into a ThemeMode."""

        if isinstance(value, ThemeMode):
            return value
        if isinstance(value, str):
            try:
                return ThemeMode(value.lower())
            except ValueError:
                return ThemeMode.LIGHT
        return ThemeMode.LIGHT


@final
class _SignalAdapter:
    """Minimal signal object with Qt-like API."""

    def __init__(self) -> None:
        self._callbacks: list[object] = []

    def connect(self, callback: object) -> None:
        if callable(callback):
            self._callbacks.append(callback)

    def emit(self, *args: object) -> None:
        for callback in tuple(self._callbacks):
            if callable(callback):
                _ = callback(*args)


@final
@dataclass(frozen=True)
class _FallbackColor:
    """Fallback color object when Qt is unavailable."""

    value: str


def _load_qt_module(module_name: str) -> object | None:
    try:
        return import_module(module_name)
    except Exception:
        return None


def _get_qapplication_instance() -> object | None:
    qtwidgets = _load_qt_module("PySide6.QtWidgets")
    if qtwidgets is None:
        return None
    application_type = getattr(qtwidgets, "QApplication", None)
    instance = getattr(application_type, "instance", None)
    if callable(instance):
        return instance()
    return None


def _get_qcolor_type() -> _ColorFactory | None:
    qtgui = _load_qt_module("PySide6.QtGui")
    if qtgui is None:
        return None
    qcolor_type = getattr(qtgui, "QColor", None)
    if callable(qcolor_type):
        return qcolor_type
    return None


__all__ = ["ThemeEngine"]
