# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false

from __future__ import annotations

"""TK-OPS 壳层状态栏组件。"""

from datetime import datetime

from ...core.qt import QApplication, QHBoxLayout, QLabel, QWidget, Qt
from ...core.theme.tokens import STATIC_TOKENS, get_token_value
from ...core.types import ThemeMode

try:
    from PySide6.QtCore import QTimer
except ImportError:
    from ...core.qt import Signal

    class QTimer:
        """无 Qt 环境时的最小定时器。"""

        def __init__(self, _parent: QWidget | None = None) -> None:
            self.timeout = Signal()

        def setInterval(self, _interval: int) -> None:
            return None

        def start(self) -> None:
            self.timeout.emit()


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用兼容层方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _connect(signal_object: object, callback: object) -> None:
    """安全连接信号。"""

    connect = getattr(signal_object, "connect", None)
    if callable(connect):
        connect(callback)


def _set_object_name(widget: object, name: str) -> None:
    """安全设置对象名。"""

    _call(widget, "setObjectName", name)


def _set_text(widget: object, text: str) -> None:
    """安全更新文本。"""

    _call(widget, "setText", text)


def _set_stylesheet(widget: object, stylesheet: str) -> None:
    """安全设置样式。"""

    _call(widget, "setStyleSheet", stylesheet)


def _set_fixed_height(widget: object, height: int) -> None:
    """安全设置固定高度。"""

    _call(widget, "setFixedHeight", height)
    _call(widget, "setMinimumHeight", height)


def _theme_mode() -> ThemeMode:
    """尽量从应用实例解析主题模式。"""

    app = QApplication.instance() if hasattr(QApplication, "instance") else None
    if app is None:
        return ThemeMode.LIGHT

    property_reader = getattr(app, "property", None)
    if not callable(property_reader):
        return ThemeMode.LIGHT

    for key in ("theme.mode", "theme_mode", "themeMode"):
        resolved = property_reader(key)
        if isinstance(resolved, ThemeMode):
            return resolved
        if isinstance(resolved, str) and resolved.lower() == ThemeMode.DARK.value:
            return ThemeMode.DARK
    return ThemeMode.LIGHT


def _token(name: str) -> str:
    """读取当前主题的设计 token。"""

    return get_token_value(name, _theme_mode())


def _px_token(name: str, fallback: int) -> int:
    """将像素 token 转为整数。"""

    raw = STATIC_TOKENS.get(name, f"{fallback}px")
    digits = "".join(character for character in raw if character.isdigit())
    return int(digits) if digits else fallback


STATUS_BAR_HEIGHT = 32
SPACING_SM = _px_token("spacing.sm", 6)
SPACING_MD = _px_token("spacing.md", 8)
SPACING_LG = _px_token("spacing.lg", 12)
RADIUS_MD = _px_token("radius.md", 8)
ALIGN_LEFT = getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignLeft", 0)


class StatusBar(QWidget):
    """展示连接状态、任务量与时钟的底部状态栏。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._message = "系统就绪"
        self._connected = True
        self._connection_text = "已连接"
        self._task_count = 0

        _set_object_name(self, "statusBar")
        _set_fixed_height(self, STATUS_BAR_HEIGHT)

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(SPACING_LG, SPACING_SM, SPACING_LG, SPACING_SM)
        root_layout.setSpacing(SPACING_LG)

        self._connection_host = QWidget(self)
        _set_object_name(self._connection_host, "statusBarConnection")
        connection_layout = QHBoxLayout(self._connection_host)
        connection_layout.setContentsMargins(0, 0, 0, 0)
        connection_layout.setSpacing(SPACING_SM)

        self._connection_dot = QLabel("●", self._connection_host)
        _set_object_name(self._connection_dot, "statusBarConnectionDot")
        self._connection_label = QLabel(self._connection_text, self._connection_host)
        _set_object_name(self._connection_label, "statusBarConnectionLabel")

        connection_layout.addWidget(self._connection_dot)
        connection_layout.addWidget(self._connection_label)

        self._message_label = QLabel(self._message, self)
        _set_object_name(self._message_label, "statusBarMessage")
        _call(self._message_label, "setAlignment", ALIGN_LEFT)

        self._right_host = QWidget(self)
        _set_object_name(self._right_host, "statusBarMeta")
        right_layout = QHBoxLayout(self._right_host)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(SPACING_LG)

        self._task_label = QLabel("任务 0", self._right_host)
        _set_object_name(self._task_label, "statusBarTaskCount")
        self._time_label = QLabel("--:--:--", self._right_host)
        _set_object_name(self._time_label, "statusBarClock")

        right_layout.addWidget(self._task_label)
        right_layout.addWidget(self._time_label)

        root_layout.addWidget(self._connection_host)
        root_layout.addWidget(self._message_label, 1)
        root_layout.addWidget(self._right_host)

        self._clock_timer = QTimer()
        _call(self._clock_timer, "setInterval", 1000)
        _connect(getattr(self._clock_timer, "timeout", None), self._refresh_time)
        _call(self._clock_timer, "start")
        self._refresh_time()
        self._apply_styles()
        self._sync_text()

    def set_message(self, message: str) -> None:
        """更新中间状态文案。"""

        self._message = message or "系统就绪"
        _set_text(self._message_label, self._message)

    def set_connection_state(self, connected: bool, text: str | None = None) -> None:
        """更新连接状态与对应文案。"""

        self._connected = connected
        self._connection_text = text or ("已连接" if connected else "已断开")
        self._sync_text()
        self._apply_styles()

    def set_task_count(self, task_count: int) -> None:
        """更新右侧任务数量。"""

        self._task_count = max(0, task_count)
        self._sync_text()

    def _sync_text(self) -> None:
        _set_text(self._connection_label, self._connection_text)
        _set_text(self._message_label, self._message)
        _set_text(self._task_label, f"任务 {self._task_count}")

    def _refresh_time(self) -> None:
        _set_text(self._time_label, datetime.now().strftime("%H:%M:%S"))

    def _apply_styles(self) -> None:
        surface = _token("surface.secondary")
        border = _token("border.default")
        text_primary = _token("text.primary")
        text_secondary = _token("text.secondary")
        success = _token("status.success")
        error = _token("status.error")
        dot_color = success if self._connected else error

        _set_stylesheet(
            self,
            (
                "QWidget#statusBar {"
                f"background-color: {surface};"
                f"border-top: 1px solid {border};"
                "}"
                "QLabel#statusBarConnectionDot {"
                f"color: {dot_color};"
                f"font-size: {STATIC_TOKENS['font.size.sm']};"
                "background: transparent;"
                "padding-right: 2px;"
                "}"
                "QLabel#statusBarConnectionLabel, QLabel#statusBarTaskCount, QLabel#statusBarClock {"
                f"color: {text_secondary};"
                f"font-size: {STATIC_TOKENS['font.size.sm']};"
                "background: transparent;"
                "}"
                "QLabel#statusBarMessage {"
                f"color: {text_primary};"
                f"font-size: {STATIC_TOKENS['font.size.sm']};"
                f"font-weight: {STATIC_TOKENS['font.weight.medium']};"
                "background: transparent;"
                f"padding: 0 {SPACING_MD}px;"
                "}"
                "QWidget#statusBarConnection, QWidget#statusBarMeta {"
                "background: transparent;"
                "border: none;"
                f"border-radius: {RADIUS_MD}px;"
                "}"
            ),
        )


__all__ = ["StatusBar"]
