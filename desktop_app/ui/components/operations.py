# pyright: basic, reportMissingImports=false, reportUnusedImport=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportAttributeAccessIssue=false

from __future__ import annotations

"""运营场景专用 UI 组件。"""

import calendar as month_calendar
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date as _date
from datetime import datetime
from ...core.theme.tokens import STATIC_TOKENS, get_token_value
from ...core.types import ThemeMode

try:
    from PySide6.QtCore import QDate, QRect, Qt, Signal
    from PySide6.QtGui import QColor, QPaintEvent, QPainter, QTextCharFormat, QTextCursor
    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPlainTextEdit,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    from ...core.qt import QApplication as _BaseApplication
    from ...core.qt import QFrame as _BaseFrame
    from ...core.qt import QHBoxLayout as _BaseHBoxLayout
    from ...core.qt import QLabel as _BaseLabel
    from ...core.qt import QLineEdit as _BaseLineEdit
    from ...core.qt import QPushButton as _BasePushButton
    from ...core.qt import QVBoxLayout as _BaseVBoxLayout
    from ...core.qt import QWidget as _BaseWidget
    from ...core.qt import Signal

    QT_AVAILABLE = False

    class QRect:
        """无 Qt 环境时的最小矩形对象。"""

        def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0) -> None:
            self._x = x
            self._y = y
            self._width = width
            self._height = height

        def x(self) -> int:
            return self._x

        def y(self) -> int:
            return self._y

        def width(self) -> int:
            return self._width

        def height(self) -> int:
            return self._height

        def right(self) -> int:
            return self._x + self._width

        def bottom(self) -> int:
            return self._y + self._height

    class QSize:
        """无 Qt 环境时的最小尺寸对象。"""

        def __init__(self, width: int = 0, height: int = 0) -> None:
            self._width = width
            self._height = height

        def width(self) -> int:
            return self._width

        def height(self) -> int:
            return self._height

    class QApplication(_BaseApplication):
        """无 Qt 环境时的最小应用对象。"""

        def property(self, _name: str) -> object | None:
            return None

    class QWidget(_BaseWidget):
        """无 Qt 环境时的最小部件。"""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._parent = parent
            self._layout: object | None = None
            self._object_name = ""
            self._style_sheet = ""
            self._properties: dict[str, object] = {}
            self._visible = True
            self._width = 320
            self._height = 120

        def setObjectName(self, name: str) -> None:
            self._object_name = name

        def objectName(self) -> str:
            return self._object_name

        def setStyleSheet(self, style: str) -> None:
            self._style_sheet = style

        def styleSheet(self) -> str:
            return self._style_sheet

        def setProperty(self, name: str, value: object) -> None:
            self._properties[name] = value

        def property(self, name: str) -> object | None:
            return self._properties.get(name)

        def setToolTip(self, _text: str) -> None:
            return None

        def setMinimumHeight(self, height: int) -> None:
            self._height = max(self._height, height)

        def setMinimumWidth(self, width: int) -> None:
            self._width = max(self._width, width)

        def setFixedHeight(self, height: int) -> None:
            self._height = height

        def setFixedWidth(self, width: int) -> None:
            self._width = width

        def setMaximumWidth(self, width: int) -> None:
            self._width = min(self._width, width) if self._width else width

        def setFixedSize(self, width: int, height: int) -> None:
            self._width = width
            self._height = height

        def setCursor(self, _cursor: object) -> None:
            return None

        def setVisible(self, visible: bool) -> None:
            self._visible = visible

        def show(self) -> None:
            self._visible = True

        def hide(self) -> None:
            self._visible = False

        def setParent(self, parent: QWidget | None) -> None:
            self._parent = parent

        def setLayout(self, layout: object) -> None:
            self._layout = layout

        def layout(self) -> object | None:
            return self._layout

        def update(self) -> None:
            return None

        def deleteLater(self) -> None:
            return None

        def rect(self) -> QRect:
            return QRect(0, 0, self._width, self._height)

    class QLabel(_BaseLabel):
        """无 Qt 环境时的最小标签。"""

        def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
            super().__init__(text, parent)
            self._text = text
            self._object_name = ""

        def setObjectName(self, name: str) -> None:
            self._object_name = name

        def setText(self, text: str) -> None:
            self._text = text

        def text(self) -> str:
            return self._text

        def setWordWrap(self, _enabled: bool) -> None:
            return None

        def setAlignment(self, _alignment: object) -> None:
            return None

    class QPushButton(_BasePushButton):
        """无 Qt 环境时的最小按钮。"""

        def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
            super().__init__(text, parent)
            self._text = text
            self._checked = False
            self._enabled = True
            self._object_name = ""
            self.clicked = Signal()

        def setObjectName(self, name: str) -> None:
            self._object_name = name

        def setText(self, text: str) -> None:
            self._text = text

        def text(self) -> str:
            return self._text

        def setCheckable(self, _value: bool) -> None:
            return None

        def setChecked(self, value: bool) -> None:
            self._checked = value

        def isChecked(self) -> bool:
            return self._checked

        def setEnabled(self, value: bool) -> None:
            self._enabled = value

        def click(self) -> None:
            if self._enabled:
                self.clicked.emit()

    class QLineEdit(_BaseLineEdit):
        """无 Qt 环境时的最小单行输入框。"""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._text = ""
            self._placeholder = ""
            self._object_name = ""
            self.textChanged = Signal(str)
            self.editingFinished = Signal()

        def setObjectName(self, name: str) -> None:
            self._object_name = name

        def setPlaceholderText(self, text: str) -> None:
            self._placeholder = text

        def setText(self, text: str) -> None:
            self._text = text
            self.textChanged.emit(text)

        def text(self) -> str:
            return self._text

        def clear(self) -> None:
            self.setText("")

        def setFrame(self, _enabled: bool) -> None:
            return None

    class QComboBox(QWidget):
        """无 Qt 环境时的最小下拉框。"""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._items: list[str] = []
            self._current_index = -1
            self.currentTextChanged = Signal(str)

        def addItem(self, text: str) -> None:
            self._items.append(text)
            if self._current_index == -1:
                self.setCurrentIndex(0)

        def addItems(self, items: Sequence[str]) -> None:
            for item in items:
                self.addItem(str(item))

        def clear(self) -> None:
            self._items.clear()
            self._current_index = -1

        def currentText(self) -> str:
            if 0 <= self._current_index < len(self._items):
                return self._items[self._current_index]
            return ""

        def setCurrentIndex(self, index: int) -> None:
            if 0 <= index < len(self._items):
                self._current_index = index
                self.currentTextChanged.emit(self._items[index])

        def setCurrentText(self, text: str) -> None:
            if text in self._items:
                self.setCurrentIndex(self._items.index(text))

    class _FallbackLayoutItem:
        """无 Qt 环境时的最小布局项。"""

        def __init__(self, widget: QWidget | None = None, layout: object | None = None) -> None:
            self._widget = widget
            self._layout = layout

        def widget(self) -> QWidget | None:
            return self._widget

        def layout(self) -> object | None:
            return self._layout

    class _BaseLayout:
        """无 Qt 环境时的最小布局。"""

        def __init__(self, parent: QWidget | None = None) -> None:
            self._parent = parent
            self._items: list[_FallbackLayoutItem] = []
            if parent is not None and hasattr(parent, "setLayout"):
                parent.setLayout(self)

        def setContentsMargins(self, *_args: int) -> None:
            return None

        def setSpacing(self, _spacing: int) -> None:
            return None

        def addWidget(self, widget: QWidget, *_args: int) -> None:
            self._items.append(_FallbackLayoutItem(widget=widget))

        def addLayout(self, layout: object, *_args: int) -> None:
            self._items.append(_FallbackLayoutItem(layout=layout))

        def addStretch(self, *_args: int) -> None:
            self._items.append(_FallbackLayoutItem())

        def count(self) -> int:
            return len(self._items)

        def itemAt(self, index: int) -> _FallbackLayoutItem | None:
            if 0 <= index < len(self._items):
                return self._items[index]
            return None

        def takeAt(self, index: int) -> _FallbackLayoutItem | None:
            if 0 <= index < len(self._items):
                return self._items.pop(index)
            return None

    class QVBoxLayout(_BaseLayout, _BaseVBoxLayout):
        """无 Qt 环境时的最小垂直布局。"""

    class QHBoxLayout(_BaseLayout, _BaseHBoxLayout):
        """无 Qt 环境时的最小水平布局。"""

    class QGridLayout(_BaseLayout):
        """无 Qt 环境时的最小网格布局。"""

        def addWidget(self, widget: QWidget, *_args: int) -> None:
            super().addWidget(widget)

    @dataclass(order=True, frozen=True)
    class QDate:
        """无 Qt 环境时的最小日期对象。"""

        year_value: int
        month_value: int
        day_value: int

        @classmethod
        def currentDate(cls) -> "QDate":
            today = _date.today()
            return cls(today.year, today.month, today.day)

        def year(self) -> int:
            return self.year_value

        def month(self) -> int:
            return self.month_value

        def day(self) -> int:
            return self.day_value

        def addDays(self, days: int) -> "QDate":
            next_value = _date.fromordinal(_date(self.year_value, self.month_value, self.day_value).toordinal() + days)
            return QDate(next_value.year, next_value.month, next_value.day)

    class _FallbackTextCursor:
        """无 Qt 环境时的最小文本游标。"""

        End = 0

        def __init__(self, editor: "QPlainTextEdit") -> None:
            self._editor = editor

        def movePosition(self, _position: int) -> None:
            return None

        def insertText(self, text: str, _format: object | None = None) -> None:
            self._editor._append_raw(text)

    class _FallbackScrollBar:
        """无 Qt 环境时的最小滚动条。"""

        def maximum(self) -> int:
            return 0

        def setValue(self, _value: int) -> None:
            return None

    class QPlainTextEdit(QWidget):
        """无 Qt 环境时的最小纯文本编辑器。"""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._text = ""
            self._max_blocks = 1000
            self.textChanged = Signal()

        def setReadOnly(self, _enabled: bool) -> None:
            return None

        def setPlaceholderText(self, _text: str) -> None:
            return None

        def setMaximumBlockCount(self, count: int) -> None:
            self._max_blocks = count

        def setUndoRedoEnabled(self, _enabled: bool) -> None:
            return None

        def clear(self) -> None:
            self._text = ""
            self.textChanged.emit()

        def setPlainText(self, text: str) -> None:
            self._text = text
            self.textChanged.emit()

        def appendPlainText(self, text: str) -> None:
            lines = self.toPlainText().splitlines()
            lines.append(text)
            self._text = "\n".join(lines[-self._max_blocks :])
            self.textChanged.emit()

        def toPlainText(self) -> str:
            return self._text

        def textCursor(self) -> _FallbackTextCursor:
            return _FallbackTextCursor(self)

        def setTextCursor(self, _cursor: object) -> None:
            return None

        def ensureCursorVisible(self) -> None:
            return None

        def moveCursor(self, _position: int) -> None:
            return None

        def verticalScrollBar(self) -> _FallbackScrollBar:
            return _FallbackScrollBar()

        def _append_raw(self, text: str) -> None:
            self._text += text
            self.textChanged.emit()

    class QFrame(_BaseFrame, QWidget):
        """无 Qt 环境时的最小容器。"""

        def __init__(self, parent: QWidget | None = None) -> None:
            QWidget.__init__(self, parent)

    class QColor:
        """无 Qt 环境时的最小颜色对象。"""

        def __init__(self, value: str) -> None:
            self.value = value

    class QTextCharFormat:
        """无 Qt 环境时的最小字符格式对象。"""

        def setForeground(self, _color: object) -> None:
            return None

    class QTextCursor(_FallbackTextCursor):
        """无 Qt 环境时的最小 QTextCursor。"""

    class QPainter:
        """无 Qt 环境时的最小绘图对象。"""

        Antialiasing = 0

        def __init__(self, _widget: QWidget) -> None:
            return None

        def setRenderHint(self, _hint: object, _enabled: bool) -> None:
            return None

        def setPen(self, _pen: object) -> None:
            return None

        def setBrush(self, _brush: object) -> None:
            return None

        def drawRoundedRect(self, *_args: object) -> None:
            return None

        def drawEllipse(self, *_args: object) -> None:
            return None

        def drawText(self, *_args: object) -> None:
            return None

        def drawLine(self, *_args: object) -> None:
            return None

        def end(self) -> None:
            return None

    class QPaintEvent:
        """无 Qt 环境时的最小绘制事件。"""

    class Qt:
        """无 Qt 环境时的最小 Qt 常量集合。"""

        NoPen = 0
        PointingHandCursor = 0

        class AlignmentFlag:
            AlignCenter = 0
            AlignLeft = 0
            AlignRight = 0
            AlignVCenter = 0


MAX_LOG_LINES = 1000


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用 Qt 方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _connect(signal_like: object, callback: object) -> None:
    """安全连接信号。"""

    connect_method = getattr(signal_like, "connect", None)
    if callable(connect_method):
        connect_method(callback)


def _clear_layout(layout: object) -> None:
    """清空布局中的所有子项。"""

    count_method = getattr(layout, "count", None)
    take_at_method = getattr(layout, "takeAt", None)
    if callable(count_method) and callable(take_at_method):
        while True:
            count_value = count_method()
            if not isinstance(count_value, int) or count_value <= 0:
                break
            item = take_at_method(0)
            if item is None:
                break
            widget_method = getattr(item, "widget", None)
            if callable(widget_method):
                widget = widget_method()
                if widget is not None:
                    _call(widget, "setParent", None)
                    _call(widget, "deleteLater")
            child_layout_method = getattr(item, "layout", None)
            if callable(child_layout_method):
                child_layout = child_layout_method()
                if child_layout is not None:
                    _clear_layout(child_layout)
        return
    items = getattr(layout, "_items", None)
    if isinstance(items, list):
        items.clear()


def _coerce_mode(value: object) -> ThemeMode:
    """将运行时主题值归一化。"""

    if isinstance(value, ThemeMode):
        return value
    if isinstance(value, str) and value.lower() == ThemeMode.DARK.value:
        return ThemeMode.DARK
    return ThemeMode.LIGHT


def _theme_mode() -> ThemeMode:
    """尽量从应用实例中读取当前主题。"""

    app = QApplication.instance() if hasattr(QApplication, "instance") else None
    if app is not None:
        property_reader = getattr(app, "property", None)
        if callable(property_reader):
            for key in ("theme.mode", "theme_mode", "themeMode"):
                resolved = property_reader(key)
                if resolved is not None:
                    return _coerce_mode(resolved)
    return ThemeMode.LIGHT


def _token(name: str, mode: ThemeMode | None = None) -> str:
    """读取当前主题 token。"""

    return get_token_value(name, mode or _theme_mode())


def _px(name: str) -> int:
    """将 px token 转成整数。"""

    raw = str(STATIC_TOKENS[name]).split("/")[0].strip().split()[0]
    return int(float(raw.replace("px", ""))) if raw.endswith("px") else 0


def _qt_flag(group_name: str, name: str, default: int = 0) -> object:
    """安全获取 Qt 常量。"""

    group = getattr(Qt, group_name, None)
    nested = getattr(group, name, None) if group is not None else None
    if nested is not None:
        return nested
    direct = getattr(Qt, name, None)
    if direct is not None:
        return direct
    return default


def _date_key(date_value: QDate) -> str:
    """将日期对象格式化为稳定键。"""

    return f"{date_value.year():04d}-{date_value.month():02d}-{date_value.day():02d}"


def _coerce_date(value: object) -> QDate | None:
    """将输入值转换为 QDate。"""

    if isinstance(value, QDate):
        return value
    if isinstance(value, datetime):
        return QDate(value.year, value.month, value.day)
    if isinstance(value, _date):
        return QDate(value.year, value.month, value.day)
    if isinstance(value, str):
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None
        return QDate(parsed.year, parsed.month, parsed.day)
    return None


def _format_timestamp(value: object | None) -> str:
    """标准化日志与时间线时间文本。"""

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


SPACING_XS = _px("spacing.xs")
SPACING_SM = _px("spacing.sm")
SPACING_MD = _px("spacing.md")
SPACING_LG = _px("spacing.lg")
SPACING_XL = _px("spacing.xl")
SPACING_2XL = _px("spacing.2xl")
SPACING_3XL = _px("spacing.3xl")
SPACING_4XL = _px("spacing.4xl")
RADIUS_SM = _px("radius.sm")
RADIUS_MD = _px("radius.md")
RADIUS_LG = _px("radius.lg")
CARD_PADDING = _px("card.padding")
INPUT_HEIGHT = _px("input.height")
BUTTON_HEIGHT_MD = _px("button.height.md")
BUTTON_HEIGHT_LG = _px("button.height.lg")
TIMELINE_TIME_WIDTH = SPACING_4XL * 2
TIMELINE_MARKER_WIDTH = SPACING_3XL
TIMELINE_DOT_SIZE = SPACING_LG
CALENDAR_CELL_HEIGHT = BUTTON_HEIGHT_LG + SPACING_4XL
DEVICE_ICON_SIZE = BUTTON_HEIGHT_LG + SPACING_XL
PROGRESS_BAR_HEIGHT = SPACING_LG
PERCENTAGE_WIDTH = SPACING_4XL + SPACING_XL


@dataclass(frozen=True)
class _Palette:
    """组件共用调色板。"""

    surface: str
    surface_alt: str
    surface_sunken: str
    text: str
    text_muted: str
    text_inverse: str
    border: str
    border_strong: str
    focus: str
    primary: str
    primary_hover: str
    primary_pressed: str
    success: str
    warning: str
    error: str
    info: str
    tag_background: str


def _palette(mode: ThemeMode | None = None) -> _Palette:
    """构建当前主题的颜色集合。"""

    resolved_mode = mode or _theme_mode()
    return _Palette(
        surface=_token("surface.secondary", resolved_mode),
        surface_alt=_token("surface.primary", resolved_mode),
        surface_sunken=_token("surface.sunken", resolved_mode),
        text=_token("text.primary", resolved_mode),
        text_muted=_token("text.secondary", resolved_mode),
        text_inverse=_token("text.inverse", resolved_mode),
        border=_token("border.default", resolved_mode),
        border_strong=_token("border.strong", resolved_mode),
        focus=_token("border.focus", resolved_mode),
        primary=_token("brand.primary", resolved_mode),
        primary_hover=_token("brand.primary_hover", resolved_mode),
        primary_pressed=_token("brand.primary_pressed", resolved_mode),
        success=_token("status.success", resolved_mode),
        warning=_token("status.warning", resolved_mode),
        error=_token("status.error", resolved_mode),
        info=_token("status.info", resolved_mode),
        tag_background=_token("tag.color.neutral", resolved_mode),
    )


def _surface_panel_style(object_name: str) -> str:
    """生成基础面板样式。"""

    colors = _palette()
    return f"""
        QWidget#{object_name}, QFrame#{object_name} {{
            background-color: {colors.surface};
            border: 1px solid {colors.border};
            border-radius: {RADIUS_LG}px;
            color: {colors.text};
            font-family: {STATIC_TOKENS['font.family.chinese']};
        }}
    """


def _field_style() -> str:
    """统一输入控件样式。"""

    colors = _palette()
    return f"""
        background-color: {colors.surface_alt};
        color: {colors.text};
        border: 1px solid {colors.border};
        border-radius: {RADIUS_MD}px;
        min-height: {INPUT_HEIGHT}px;
        padding: {SPACING_SM}px {SPACING_XL}px;
        selection-background-color: {colors.primary};
        selection-color: {colors.text_inverse};
    """


def _secondary_button_style() -> str:
    """统一次级按钮样式。"""

    colors = _palette()
    return f"""
        background-color: {colors.surface_alt};
        color: {colors.text};
        border: 1px solid {colors.border};
        border-radius: {RADIUS_MD}px;
        min-height: {BUTTON_HEIGHT_MD}px;
        padding: {SPACING_SM}px {SPACING_XL}px;
        font-size: {STATIC_TOKENS['font.size.md']};
        font-weight: {STATIC_TOKENS['font.weight.semibold']};
    """


def _primary_button_style() -> str:
    """统一主按钮样式。"""

    colors = _palette()
    return f"""
        background-color: {colors.primary};
        color: {colors.text_inverse};
        border: 1px solid {colors.primary};
        border-radius: {RADIUS_MD}px;
        min-height: {BUTTON_HEIGHT_MD}px;
        padding: {SPACING_SM}px {SPACING_2XL}px;
        font-size: {STATIC_TOKENS['font.size.md']};
        font-weight: {STATIC_TOKENS['font.weight.bold']};
    """


class TaskProgressBar(QWidget):
    """用于任务流转的三段式步骤进度条。"""

    _steps = ("等待中", "处理中", "完成")

    def __init__(self, progress: int = 0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "taskProgressBar")
        _call(self, "setMinimumHeight", BUTTON_HEIGHT_LG + SPACING_4XL)
        self._progress = 0
        self.set_progress(progress)

    def progress(self) -> int:
        """返回当前百分比。"""

        return self._progress

    def set_progress(self, value: int) -> None:
        """更新进度百分比。"""

        self._progress = max(0, min(100, int(value)))
        _call(self, "update")

    def paintEvent(self, _event: QPaintEvent) -> None:
        """绘制步骤分段与百分比。"""

        colors = _palette()
        painter = QPainter(self)
        _call(painter, "setRenderHint", getattr(QPainter, "Antialiasing", 0), True)

        rect = self.rect()
        segment_gap = SPACING_MD
        segment_area_width = max(rect.width() - PERCENTAGE_WIDTH - SPACING_XL, SPACING_4XL)
        segment_width = max((segment_area_width - (segment_gap * 2)) // 3, SPACING_3XL)
        bar_height = PROGRESS_BAR_HEIGHT
        bar_y = SPACING_XL
        label_y = bar_y + bar_height + SPACING_MD

        step_colors = (colors.info, colors.primary, colors.success)
        thresholds = (34, 67, 100)
        previous_threshold = 0
        align_center = _qt_flag("AlignmentFlag", "AlignCenter", 0)

        for index, label in enumerate(self._steps):
            x = rect.x() + index * (segment_width + segment_gap)
            track_rect = QRect(x, bar_y, segment_width, bar_height)
            label_rect = QRect(x, label_y, segment_width, SPACING_3XL)
            threshold = thresholds[index]
            span = threshold - previous_threshold
            current_value = max(0, min(self._progress - previous_threshold, span))
            fill_ratio = current_value / span if span else 0.0
            fill_width = int(segment_width * fill_ratio)
            previous_threshold = threshold

            _call(painter, "setPen", QColor(colors.border))
            _call(painter, "setBrush", QColor(colors.surface_sunken))
            _call(painter, "drawRoundedRect", track_rect, RADIUS_MD, RADIUS_MD)

            if fill_width > 0:
                _call(painter, "setPen", QColor(step_colors[index]))
                _call(painter, "setBrush", QColor(step_colors[index]))
                _call(painter, "drawRoundedRect", QRect(x, bar_y, fill_width, bar_height), RADIUS_MD, RADIUS_MD)

            label_color = step_colors[index] if self._progress >= previous_threshold - 1 else colors.text_muted
            _call(painter, "setPen", QColor(label_color))
            _call(painter, "drawText", label_rect, align_center, label)

        percentage_rect = QRect(rect.x() + segment_area_width + SPACING_XL, bar_y - SPACING_XS, PERCENTAGE_WIDTH, SPACING_4XL)
        _call(painter, "setPen", QColor(colors.text))
        _call(painter, "drawText", percentage_rect, align_center, f"{self._progress}%")
        _call(painter, "end")


class _RuleConditionRow(QWidget):
    """规则编辑器中的单条条件行。"""

    changed = Signal()
    remove_requested = Signal(object)

    FIELD_OPTIONS = ("任务类型", "优先级", "执行状态", "设备分组", "账号标签")
    OPERATOR_OPTIONS = ("等于", "不等于", "包含", "大于", "小于")

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "ruleConditionRow")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)

        self.field_box = QComboBox(self)
        _call(self.field_box, "addItems", list(self.FIELD_OPTIONS))

        self.operator_box = QComboBox(self)
        _call(self.operator_box, "addItems", list(self.OPERATOR_OPTIONS))

        self.value_edit = QLineEdit(self)
        _call(self.value_edit, "setPlaceholderText", "请输入条件值")

        self.remove_button = QPushButton("移除", self)
        _call(self.remove_button, "setCursor", _qt_flag("CursorShape", "PointingHandCursor", 0))

        for widget in (self.field_box, self.operator_box, self.value_edit):
            _call(widget, "setStyleSheet", _field_style())
        _call(self.remove_button, "setStyleSheet", _secondary_button_style())

        layout.addWidget(self.field_box)
        layout.addWidget(self.operator_box)
        layout.addWidget(self.value_edit, 1)
        layout.addWidget(self.remove_button)

        _connect(getattr(self.field_box, "currentTextChanged", None), self._emit_changed)
        _connect(getattr(self.operator_box, "currentTextChanged", None), self._emit_changed)
        _connect(getattr(self.value_edit, "textChanged", None), self._emit_changed)
        _connect(getattr(self.remove_button, "clicked", None), lambda: self.remove_requested.emit(self))

    def set_condition(self, condition: Mapping[str, object]) -> None:
        """回填条件数据。"""

        field_value = str(condition.get("field", self.FIELD_OPTIONS[0]))
        operator_value = str(condition.get("operator", self.OPERATOR_OPTIONS[0]))
        raw_value = str(condition.get("value", ""))
        _call(self.field_box, "setCurrentText", field_value)
        _call(self.operator_box, "setCurrentText", operator_value)
        _call(self.value_edit, "setText", raw_value)

    def to_dict(self) -> dict[str, str]:
        """导出当前条件。"""

        field_reader = getattr(self.field_box, "currentText", None)
        operator_reader = getattr(self.operator_box, "currentText", None)
        value_reader = getattr(self.value_edit, "text", None)
        return {
            "field": str(field_reader()) if callable(field_reader) else "",
            "operator": str(operator_reader()) if callable(operator_reader) else "",
            "value": str(value_reader()) if callable(value_reader) else "",
        }

    def _emit_changed(self, *_args: object) -> None:
        self.changed.emit()


class RuleEditorWidget(QFrame):
    """用于任务分流、自动回复与调度的可视化规则编辑器。"""

    rule_changed = Signal(dict)

    ACTION_OPTIONS = ("执行任务", "暂停任务", "发送提醒", "分配设备", "标记完成")

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "ruleEditor")

        self._logic = "AND"
        self._rows: list[_RuleConditionRow] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        root.setSpacing(SPACING_XL)

        title = QLabel("规则编辑器", self)
        _call(title, "setObjectName", "ruleEditorTitle")

        logic_row = QHBoxLayout()
        logic_row.setContentsMargins(0, 0, 0, 0)
        logic_row.setSpacing(SPACING_MD)

        logic_label = QLabel("条件关系", self)
        self._and_button = QPushButton("AND", self)
        self._or_button = QPushButton("OR", self)
        _call(self._and_button, "setCheckable", True)
        _call(self._or_button, "setCheckable", True)

        logic_row.addWidget(logic_label)
        logic_row.addWidget(self._and_button)
        logic_row.addWidget(self._or_button)
        logic_row.addStretch(1)

        self._rows_host = QWidget(self)
        self._rows_layout = QVBoxLayout(self._rows_host)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(SPACING_MD)

        self._add_button = QPushButton("添加条件", self)

        self._action_section = QFrame(self)
        _call(self._action_section, "setObjectName", "ruleEditorActionSection")
        action_layout = QVBoxLayout(self._action_section)
        action_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        action_layout.setSpacing(SPACING_MD)

        action_title = QLabel("执行动作", self._action_section)
        self._action_type_box = QComboBox(self._action_section)
        _call(self._action_type_box, "addItems", list(self.ACTION_OPTIONS))
        self._action_value_edit = QLineEdit(self._action_section)
        _call(self._action_value_edit, "setPlaceholderText", "请输入动作目标、备注或输出内容")

        action_layout.addWidget(action_title)
        action_layout.addWidget(self._action_type_box)
        action_layout.addWidget(self._action_value_edit)

        root.addWidget(title)
        root.addLayout(logic_row)
        root.addWidget(self._rows_host)
        root.addWidget(self._add_button)
        root.addWidget(self._action_section)

        _connect(getattr(self._and_button, "clicked", None), lambda: self.set_logic("AND"))
        _connect(getattr(self._or_button, "clicked", None), lambda: self.set_logic("OR"))
        _connect(getattr(self._add_button, "clicked", None), self.add_condition)
        _connect(getattr(self._action_type_box, "currentTextChanged", None), self._emit_rule_changed)
        _connect(getattr(self._action_value_edit, "textChanged", None), self._emit_rule_changed)

        self._apply_styles()
        self.add_condition()
        self.set_logic("AND")

    def add_condition(self, condition: Mapping[str, object] | None = None) -> None:
        """新增一条条件行。"""

        row = _RuleConditionRow(self._rows_host)
        if condition is not None:
            row.set_condition(condition)
        self._rows.append(row)
        self._rows_layout.addWidget(row)
        _connect(row.changed, self._emit_rule_changed)
        _connect(row.remove_requested, self._remove_condition_row)
        self._emit_rule_changed()

    def set_logic(self, logic: str) -> None:
        """设置条件之间的逻辑关系。"""

        resolved = "OR" if logic.upper() == "OR" else "AND"
        self._logic = resolved
        _call(self._and_button, "setChecked", resolved == "AND")
        _call(self._or_button, "setChecked", resolved == "OR")
        self._update_logic_styles()
        self._emit_rule_changed()

    def get_rule(self) -> dict[str, object]:
        """导出当前规则定义。"""

        action_reader = getattr(self._action_type_box, "currentText", None)
        action_value_reader = getattr(self._action_value_edit, "text", None)
        return {
            "logic": self._logic,
            "conditions": [row.to_dict() for row in self._rows],
            "action": {
                "type": str(action_reader()) if callable(action_reader) else "",
                "value": str(action_value_reader()) if callable(action_value_reader) else "",
            },
        }

    def set_rule(self, rule: Mapping[str, object]) -> None:
        """整体回填规则。"""

        self._logic = str(rule.get("logic", "AND")).upper()
        _clear_layout(self._rows_layout)
        self._rows.clear()
        conditions = rule.get("conditions", [])
        if isinstance(conditions, Sequence) and not isinstance(conditions, (str, bytes)):
            for item in conditions:
                if isinstance(item, Mapping):
                    self.add_condition(item)
        if not self._rows:
            self.add_condition()

        action_value = rule.get("action", {})
        if isinstance(action_value, Mapping):
            _call(self._action_type_box, "setCurrentText", str(action_value.get("type", self.ACTION_OPTIONS[0])))
            _call(self._action_value_edit, "setText", str(action_value.get("value", "")))

        self.set_logic(self._logic)
        self._emit_rule_changed()

    def _remove_condition_row(self, row: object) -> None:
        if not isinstance(row, _RuleConditionRow):
            return
        if len(self._rows) <= 1:
            row.set_condition({"field": _RuleConditionRow.FIELD_OPTIONS[0], "operator": _RuleConditionRow.OPERATOR_OPTIONS[0], "value": ""})
            self._emit_rule_changed()
            return
        self._rows = [item for item in self._rows if item is not row]
        _call(row, "setParent", None)
        _call(row, "deleteLater")
        self._emit_rule_changed()

    def _emit_rule_changed(self, *_args: object) -> None:
        self.rule_changed.emit(self.get_rule())

    def _update_logic_styles(self) -> None:
        colors = _palette()
        active_style = f"""
            background-color: {colors.primary};
            color: {colors.text_inverse};
            border: 1px solid {colors.primary};
            border-radius: {RADIUS_MD}px;
            min-height: {BUTTON_HEIGHT_MD}px;
            padding: {SPACING_SM}px {SPACING_XL}px;
            font-weight: {STATIC_TOKENS['font.weight.bold']};
        """
        inactive_style = _secondary_button_style()
        _call(self._and_button, "setStyleSheet", active_style if self._logic == "AND" else inactive_style)
        _call(self._or_button, "setStyleSheet", active_style if self._logic == "OR" else inactive_style)

    def _apply_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            _surface_panel_style("ruleEditor")
            + f"""
            QLabel#ruleEditorTitle {{
                background: transparent;
                color: {colors.text};
                font-size: {STATIC_TOKENS['font.size.xl']};
                font-weight: {STATIC_TOKENS['font.weight.bold']};
            }}
            QFrame#ruleEditorActionSection {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            """,
        )
        _call(self._add_button, "setStyleSheet", _primary_button_style())
        _call(self._action_type_box, "setStyleSheet", _field_style())
        _call(self._action_value_edit, "setStyleSheet", _field_style())


class _CalendarDayCell(QPushButton):
    """日历中的单个日期单元。"""

    def __init__(self, date_value: QDate, event_count: int, selected: bool, today: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._date_value = date_value
        self._event_count = event_count
        self._selected = selected
        self._today = today
        _call(self, "setObjectName", "calendarDayCell")
        _call(self, "setFixedHeight", CALENDAR_CELL_HEIGHT)
        _call(self, "setCursor", _qt_flag("CursorShape", "PointingHandCursor", 0))
        self._apply_text()
        self._apply_style()

    @property
    def date_value(self) -> QDate:
        """返回该单元对应日期。"""

        return self._date_value

    def _apply_text(self) -> None:
        dots = "".join("●" for _ in range(min(self._event_count, 3)))
        line_text = f"{self._date_value.day()}"
        display = f"{line_text}\n{dots}" if dots else f"{line_text}\n"
        _call(self, "setText", display)

    def _apply_style(self) -> None:
        colors = _palette()
        if self._selected:
            background = colors.primary
            border_color = colors.primary
            text_color = colors.text_inverse
        elif self._today:
            background = colors.tag_background
            border_color = colors.focus
            text_color = colors.text
        else:
            background = colors.surface_alt
            border_color = colors.border
            text_color = colors.text if self._event_count else colors.text_muted
        _call(
            self,
            "setStyleSheet",
            f"""
            QPushButton#calendarDayCell {{
                background-color: {background};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_MD}px;
                text-align: center;
                font-size: {STATIC_TOKENS['font.size.md']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            """,
        )


class CalendarWidget(QFrame):
    """带事件标记与月份导航的月视图日历。"""

    date_selected = Signal(QDate)

    WEEKDAY_LABELS = ("一", "二", "三", "四", "五", "六", "日")

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "calendarWidget")

        current = QDate.currentDate()
        self._display_year = current.year()
        self._display_month = current.month()
        self._selected_date = current
        self._events: dict[str, int] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        root.setSpacing(SPACING_XL)

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(SPACING_MD)

        self._prev_button = QPushButton("上月", self)
        self._next_button = QPushButton("下月", self)
        self._today_button = QPushButton("今天", self)
        self._month_label = QLabel("", self)
        _call(self._month_label, "setObjectName", "calendarMonthLabel")

        nav_layout.addWidget(self._prev_button)
        nav_layout.addWidget(self._month_label)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self._today_button)
        nav_layout.addWidget(self._next_button)

        self._grid_host = QWidget(self)
        self._grid_layout = QGridLayout(self._grid_host)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setSpacing(SPACING_MD)

        root.addLayout(nav_layout)
        root.addWidget(self._grid_host)

        _connect(getattr(self._prev_button, "clicked", None), lambda: self._shift_month(-1))
        _connect(getattr(self._next_button, "clicked", None), lambda: self._shift_month(1))
        _connect(getattr(self._today_button, "clicked", None), self.go_today)

        self._apply_styles()
        self._refresh_grid()

    def selected_date(self) -> QDate:
        """返回当前选中日期。"""

        return self._selected_date

    def set_events(self, events: Mapping[str, object]) -> None:
        """设置日期与事件数量映射。"""

        normalized: dict[str, int] = {}
        for raw_date, raw_events in events.items():
            date_value = _coerce_date(raw_date)
            if date_value is None:
                continue
            if isinstance(raw_events, int):
                count = max(raw_events, 0)
            elif isinstance(raw_events, str):
                count = 1 if raw_events.strip() else 0
            elif isinstance(raw_events, Sequence):
                count = len(raw_events)
            else:
                count = 1
            normalized[_date_key(date_value)] = count
        self._events = normalized
        self._refresh_grid()

    def go_today(self) -> None:
        """跳转到今天并触发选中。"""

        today = QDate.currentDate()
        self._display_year = today.year()
        self._display_month = today.month()
        self.select_date(today)

    def select_date(self, date_value: QDate) -> None:
        """设置选中日期。"""

        self._selected_date = date_value
        self._display_year = date_value.year()
        self._display_month = date_value.month()
        self._refresh_grid()
        self.date_selected.emit(date_value)

    def _shift_month(self, offset: int) -> None:
        month_value = self._display_month + offset
        year_value = self._display_year
        if month_value < 1:
            month_value = 12
            year_value -= 1
        elif month_value > 12:
            month_value = 1
            year_value += 1
        self._display_year = year_value
        self._display_month = month_value
        self._refresh_grid()

    def _refresh_grid(self) -> None:
        colors = _palette()
        _clear_layout(self._grid_layout)
        _call(self._month_label, "setText", f"{self._display_year}年{self._display_month:02d}月")

        for column, weekday in enumerate(self.WEEKDAY_LABELS):
            header = QLabel(weekday, self._grid_host)
            _call(header, "setAlignment", _qt_flag("AlignmentFlag", "AlignCenter", 0))
            _call(
                header,
                "setStyleSheet",
                f"color: {colors.text_muted}; font-size: {STATIC_TOKENS['font.size.sm']}; font-weight: {STATIC_TOKENS['font.weight.bold']};",
            )
            self._grid_layout.addWidget(header, 0, column)

        first_weekday, month_days = month_calendar.monthrange(self._display_year, self._display_month)
        total_cells = 42
        for day_offset in range(total_cells):
            grid_row = 1 + (day_offset // 7)
            grid_column = day_offset % 7
            day_number = day_offset - first_weekday + 1
            if day_number < 1 or day_number > month_days:
                placeholder = QLabel("", self._grid_host)
                _call(
                    placeholder,
                    "setStyleSheet",
                    f"background-color: {colors.surface}; border: 1px solid transparent; border-radius: {RADIUS_MD}px;",
                )
                _call(placeholder, "setMinimumHeight", CALENDAR_CELL_HEIGHT)
                self._grid_layout.addWidget(placeholder, grid_row, grid_column)
                continue

            date_value = QDate(self._display_year, self._display_month, day_number)
            key = _date_key(date_value)
            cell = _CalendarDayCell(
                date_value=date_value,
                event_count=self._events.get(key, 0),
                selected=key == _date_key(self._selected_date),
                today=key == _date_key(QDate.currentDate()),
                parent=self._grid_host,
            )
            _connect(getattr(cell, "clicked", None), lambda dv=date_value: self.select_date(dv))
            self._grid_layout.addWidget(cell, grid_row, grid_column)

    def _apply_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            _surface_panel_style("calendarWidget")
            + f"""
            QLabel#calendarMonthLabel {{
                background: transparent;
                color: {colors.text};
                font-size: {STATIC_TOKENS['font.size.xl']};
                font-weight: {STATIC_TOKENS['font.weight.bold']};
            }}
            """,
        )
        for button in (self._prev_button, self._today_button, self._next_button):
            _call(button, "setStyleSheet", _secondary_button_style())


class _TimelineMarker(QWidget):
    """时间线中部的轴线与节点标记。"""

    def __init__(self, color: str, first: bool, last: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = color
        self._first = first
        self._last = last
        _call(self, "setFixedWidth", TIMELINE_MARKER_WIDTH)
        _call(self, "setMinimumHeight", BUTTON_HEIGHT_LG + SPACING_3XL)

    def paintEvent(self, _event: QPaintEvent) -> None:
        """绘制时间线竖线与圆点。"""

        colors = _palette()
        rect = self.rect()
        center_x = rect.x() + rect.width() // 2
        center_y = rect.y() + rect.height() // 2
        dot_radius = TIMELINE_DOT_SIZE // 2

        painter = QPainter(self)
        _call(painter, "setRenderHint", getattr(QPainter, "Antialiasing", 0), True)
        _call(painter, "setPen", QColor(colors.border_strong))
        if not self._first:
            _call(painter, "drawLine", center_x, rect.y(), center_x, center_y - dot_radius)
        if not self._last:
            _call(painter, "drawLine", center_x, center_y + dot_radius, center_x, rect.bottom())
        _call(painter, "setPen", QColor(self._color))
        _call(painter, "setBrush", QColor(self._color))
        _call(painter, "drawEllipse", center_x - dot_radius, center_y - dot_radius, TIMELINE_DOT_SIZE, TIMELINE_DOT_SIZE)
        _call(painter, "end")


@dataclass(frozen=True)
class _TimelineEntry:
    """时间线条目数据。"""

    timestamp: str
    title: str
    content: str
    event_type: str


class _TimelineItemWidget(QWidget):
    """单条时间线内容块。"""

    def __init__(self, entry: _TimelineEntry, color: str, first: bool, last: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(SPACING_XL)

        time_label = QLabel(entry.timestamp, self)
        _call(time_label, "setFixedWidth", TIMELINE_TIME_WIDTH)
        _call(time_label, "setAlignment", _qt_flag("AlignmentFlag", "AlignRight", 0))
        _call(time_label, "setObjectName", "timelineTimestamp")

        marker = _TimelineMarker(color=color, first=first, last=last, parent=self)

        content_card = QFrame(self)
        _call(content_card, "setObjectName", "timelineItemCard")
        content_layout = QVBoxLayout(content_card)
        content_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        content_layout.setSpacing(SPACING_SM)

        title_label = QLabel(entry.title, content_card)
        detail_label = QLabel(entry.content, content_card)
        _call(detail_label, "setWordWrap", True)

        content_layout.addWidget(title_label)
        content_layout.addWidget(detail_label)

        root.addWidget(time_label)
        root.addWidget(marker)
        root.addWidget(content_card, 1)

        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QLabel#timelineTimestamp {{
                color: {colors.text_muted};
                background: transparent;
                font-size: {STATIC_TOKENS['font.size.sm']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            QFrame#timelineItemCard {{
                background-color: {colors.surface_alt};
                border: 1px solid {color};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#timelineItemCard QLabel {{
                background: transparent;
                color: {colors.text};
                font-size: {STATIC_TOKENS['font.size.md']};
            }}
            """,
        )


class TimelineWidget(QFrame):
    """按时间顺序展示任务事件的垂直时间线。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "timelineWidget")

        self._entries: list[_TimelineEntry] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        root.setSpacing(SPACING_XL)

        title = QLabel("任务时间线", self)
        _call(title, "setObjectName", "timelineTitle")
        self._content_host = QWidget(self)
        self._content_layout = QVBoxLayout(self._content_host)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(SPACING_LG)

        root.addWidget(title)
        root.addWidget(self._content_host)

        self._apply_styles()
        self.set_events([])

    def add_event(self, timestamp: object, title: str, content: str, event_type: str = "info") -> None:
        """追加一个时间线节点。"""

        self._entries.append(
            _TimelineEntry(
                timestamp=_format_timestamp(timestamp),
                title=title or "未命名节点",
                content=content or "暂无详情",
                event_type=event_type,
            )
        )
        self._rebuild()

    def set_events(self, events: Sequence[Mapping[str, object]]) -> None:
        """批量设置时间线内容。"""

        self._entries = []
        for item in events:
            timestamp = _format_timestamp(item.get("timestamp") or item.get("time"))
            title = str(item.get("title") or item.get("label") or "未命名节点")
            content = str(item.get("content") or item.get("description") or item.get("detail") or "暂无详情")
            event_type = str(item.get("type") or item.get("level") or "info")
            self._entries.append(_TimelineEntry(timestamp=timestamp, title=title, content=content, event_type=event_type))
        self._rebuild()

    def clear_events(self) -> None:
        """清空时间线。"""

        self._entries.clear()
        self._rebuild()

    def _type_color(self, event_type: str) -> str:
        colors = _palette()
        normalized = event_type.strip().lower()
        mapping = {
            "success": colors.success,
            "成功": colors.success,
            "warning": colors.warning,
            "警告": colors.warning,
            "error": colors.error,
            "失败": colors.error,
            "异常": colors.error,
            "info": colors.info,
            "信息": colors.info,
        }
        return mapping.get(normalized, colors.primary)

    def _rebuild(self) -> None:
        _clear_layout(self._content_layout)
        if not self._entries:
            empty = QLabel("暂无时间线事件", self._content_host)
            _call(empty, "setStyleSheet", f"color: {_palette().text_muted}; background: transparent;")
            self._content_layout.addWidget(empty)
            return

        for index, entry in enumerate(self._entries):
            row = _TimelineItemWidget(
                entry=entry,
                color=self._type_color(entry.event_type),
                first=index == 0,
                last=index == len(self._entries) - 1,
                parent=self._content_host,
            )
            self._content_layout.addWidget(row)
        self._content_layout.addStretch(1)

    def _apply_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            _surface_panel_style("timelineWidget")
            + f"""
            QLabel#timelineTitle {{
                background: transparent;
                color: {colors.text};
                font-size: {STATIC_TOKENS['font.size.xl']};
                font-weight: {STATIC_TOKENS['font.weight.bold']};
            }}
            """,
        )


@dataclass(frozen=True)
class _LogEntry:
    """日志条目数据。"""

    timestamp: str
    level: str
    message: str


class LogViewer(QFrame):
    """支持分级着色、搜索和自动滚动的日志查看器。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "logViewer")

        self._entries: list[_LogEntry] = []
        self._search_text = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        root.setSpacing(SPACING_XL)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setSpacing(SPACING_MD)

        self._search_edit = QLineEdit(self)
        _call(self._search_edit, "setPlaceholderText", "搜索日志关键字或级别")
        self._summary_label = QLabel("显示 0 / 0 条", self)
        self._clear_button = QPushButton("清空日志", self)

        toolbar.addWidget(self._search_edit, 1)
        toolbar.addWidget(self._summary_label)
        toolbar.addWidget(self._clear_button)

        self._editor = QPlainTextEdit(self)
        _call(self._editor, "setReadOnly", True)
        _call(self._editor, "setUndoRedoEnabled", False)
        _call(self._editor, "setPlaceholderText", "日志将在此处实时输出")
        _call(self._editor, "setMaximumBlockCount", MAX_LOG_LINES)
        _call(self._editor, "setMinimumHeight", BUTTON_HEIGHT_LG * 4)

        root.addLayout(toolbar)
        root.addWidget(self._editor)

        _connect(getattr(self._search_edit, "textChanged", None), self._on_search_changed)
        _connect(getattr(self._clear_button, "clicked", None), self.clear_logs)

        self._apply_styles()

    def append_log(self, level: str, message: str, timestamp: object | None = None) -> None:
        """追加单条日志记录。"""

        normalized_level = level.strip().upper() if level.strip() else "INFO"
        sanitized_message = str(message).replace("\n", " | ")
        self._entries.append(_LogEntry(timestamp=_format_timestamp(timestamp), level=normalized_level, message=sanitized_message))
        if len(self._entries) > MAX_LOG_LINES:
            self._entries = self._entries[-MAX_LOG_LINES:]
        self._render_entries()

    def append_info(self, message: str, timestamp: object | None = None) -> None:
        """追加 INFO 级别日志。"""

        self.append_log("INFO", message, timestamp)

    def append_warning(self, message: str, timestamp: object | None = None) -> None:
        """追加 WARNING 级别日志。"""

        self.append_log("WARNING", message, timestamp)

    def append_error(self, message: str, timestamp: object | None = None) -> None:
        """追加 ERROR 级别日志。"""

        self.append_log("ERROR", message, timestamp)

    def clear_logs(self) -> None:
        """清空所有日志。"""

        self._entries.clear()
        self._render_entries()

    def _level_color(self, level: str) -> str:
        colors = _palette()
        return {
            "INFO": colors.success,
            "WARNING": colors.warning,
            "ERROR": colors.error,
        }.get(level, colors.text)

    def _format_entry(self, entry: _LogEntry) -> str:
        return f"[{entry.timestamp}] [{entry.level}] {entry.message}"

    def _filtered_entries(self) -> list[_LogEntry]:
        query = self._search_text.strip().lower()
        if not query:
            return list(self._entries)
        return [entry for entry in self._entries if query in self._format_entry(entry).lower()]

    def _on_search_changed(self, text: str) -> None:
        self._search_text = text
        self._render_entries()

    def _render_entries(self) -> None:
        filtered_entries = self._filtered_entries()
        _call(self._editor, "clear")

        if QT_AVAILABLE:
            cursor = self._editor.textCursor()
            move_method = getattr(cursor, "movePosition", None)
            insert_method = getattr(cursor, "insertText", None)
            end_position = getattr(QTextCursor, "End", None)
            for entry in filtered_entries:
                if callable(move_method) and end_position is not None:
                    move_method(end_position)
                char_format = QTextCharFormat()
                char_format.setForeground(QColor(self._level_color(entry.level)))
                if callable(insert_method):
                    insert_method(self._format_entry(entry) + "\n", char_format)
            _call(self._editor, "setTextCursor", cursor)
        else:
            joined_text = "\n".join(self._format_entry(entry) for entry in filtered_entries)
            _call(self._editor, "setPlainText", joined_text)

        _call(self._summary_label, "setText", f"显示 {len(filtered_entries)} / {len(self._entries)} 条")
        _call(self._editor, "ensureCursorVisible")
        scroll_bar = _call(self._editor, "verticalScrollBar")
        maximum_reader = getattr(scroll_bar, "maximum", None)
        set_value = getattr(scroll_bar, "setValue", None)
        if callable(maximum_reader) and callable(set_value):
            set_value(maximum_reader())

    def _apply_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            _surface_panel_style("logViewer")
            + f"""
            QLineEdit {{
                {_field_style()}
            }}
            QLabel {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {STATIC_TOKENS['font.size.sm']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            QPlainTextEdit {{
                background-color: {colors.surface_alt};
                color: {colors.text};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_XL}px;
                font-family: {STATIC_TOKENS['font.family.mono']};
                font-size: {STATIC_TOKENS['font.size.sm']};
            }}
            """,
        )
        _call(self._clear_button, "setStyleSheet", _secondary_button_style())


class _InlineProgressBar(QWidget):
    """设备卡片使用的紧凑型进度条。"""

    def __init__(self, value: int = 0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._value = 0
        _call(self, "setMinimumHeight", PROGRESS_BAR_HEIGHT)
        self.set_value(value)

    def set_value(self, value: int) -> None:
        """设置进度百分比。"""

        self._value = max(0, min(100, int(value)))
        _call(self, "update")

    def paintEvent(self, _event: QPaintEvent) -> None:
        """绘制线性进度。"""

        colors = _palette()
        rect = self.rect()
        painter = QPainter(self)
        _call(painter, "setRenderHint", getattr(QPainter, "Antialiasing", 0), True)
        _call(painter, "setPen", QColor(colors.border))
        _call(painter, "setBrush", QColor(colors.surface_sunken))
        _call(painter, "drawRoundedRect", rect, RADIUS_MD, RADIUS_MD)

        fill_width = int(rect.width() * (self._value / 100))
        if fill_width > 0:
            _call(painter, "setPen", QColor(colors.primary))
            _call(painter, "setBrush", QColor(colors.primary))
            _call(painter, "drawRoundedRect", QRect(rect.x(), rect.y(), fill_width, rect.height()), RADIUS_MD, RADIUS_MD)
        _call(painter, "end")


class DeviceCard(QFrame):
    """展示局域网设备状态、传输进度与快捷操作的卡片。"""

    action_requested = Signal(str)

    def __init__(
        self,
        name: str = "主控工作站",
        ip: str = "192.168.1.10",
        status: str = "在线",
        transfer_progress: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "deviceCard")

        self._status = status

        root = QHBoxLayout(self)
        root.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        root.setSpacing(SPACING_XL)

        self._icon_label = QLabel("▣", self)
        _call(self._icon_label, "setObjectName", "deviceCardIcon")
        _call(self._icon_label, "setAlignment", _qt_flag("AlignmentFlag", "AlignCenter", 0))
        _call(self._icon_label, "setFixedSize", DEVICE_ICON_SIZE, DEVICE_ICON_SIZE)

        info_host = QWidget(self)
        info_layout = QVBoxLayout(info_host)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(SPACING_SM)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_MD)

        self._name_label = QLabel(name, info_host)
        _call(self._name_label, "setObjectName", "deviceCardName")
        self._status_label = QLabel(status, info_host)
        _call(self._status_label, "setObjectName", "deviceCardStatus")

        header_layout.addWidget(self._name_label)
        header_layout.addWidget(self._status_label)
        header_layout.addStretch(1)

        self._ip_label = QLabel(f"IP：{ip}", info_host)
        _call(self._ip_label, "setObjectName", "deviceCardIp")
        self._progress_label = QLabel(f"传输进度 {transfer_progress}%", info_host)
        _call(self._progress_label, "setObjectName", "deviceCardProgressText")
        self._progress_bar = _InlineProgressBar(transfer_progress, info_host)

        info_layout.addLayout(header_layout)
        info_layout.addWidget(self._ip_label)
        info_layout.addWidget(self._progress_label)
        info_layout.addWidget(self._progress_bar)

        action_host = QWidget(self)
        action_layout = QVBoxLayout(action_host)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(SPACING_MD)

        self._connect_button = QPushButton("连接", action_host)
        self._transfer_button = QPushButton("传输", action_host)
        self._detail_button = QPushButton("详情", action_host)

        action_layout.addWidget(self._connect_button)
        action_layout.addWidget(self._transfer_button)
        action_layout.addWidget(self._detail_button)
        action_layout.addStretch(1)

        root.addWidget(self._icon_label)
        root.addWidget(info_host, 1)
        root.addWidget(action_host)

        _connect(getattr(self._connect_button, "clicked", None), lambda: self.action_requested.emit("connect"))
        _connect(getattr(self._transfer_button, "clicked", None), lambda: self.action_requested.emit("transfer"))
        _connect(getattr(self._detail_button, "clicked", None), lambda: self.action_requested.emit("detail"))

        self._apply_styles()
        self.set_status(status)
        self.set_transfer_progress(transfer_progress)

    def set_device_info(self, name: str, ip: str) -> None:
        """更新设备名称与地址。"""

        _call(self._name_label, "setText", name)
        _call(self._ip_label, "setText", f"IP：{ip}")

    def set_status(self, status: str) -> None:
        """更新设备状态展示。"""

        self._status = status
        colors = _palette()
        status_color = {
            "在线": colors.success,
            "忙碌": colors.warning,
            "离线": colors.error,
            "待机": colors.info,
        }.get(status, colors.primary)
        _call(self._status_label, "setText", status)
        _call(
            self._status_label,
            "setStyleSheet",
            f"""
            background-color: {colors.tag_background};
            color: {status_color};
            border: 1px solid {status_color};
            border-radius: {RADIUS_MD}px;
            padding: {SPACING_XS}px {SPACING_LG}px;
            font-size: {STATIC_TOKENS['font.size.sm']};
            font-weight: {STATIC_TOKENS['font.weight.bold']};
            """,
        )

    def set_transfer_progress(self, value: int) -> None:
        """更新传输进度。"""

        progress_value = max(0, min(100, int(value)))
        _call(self._progress_label, "setText", f"传输进度 {progress_value}%")
        self._progress_bar.set_value(progress_value)

    def _apply_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            _surface_panel_style("deviceCard")
            + f"""
            QLabel#deviceCardIcon {{
                background-color: {colors.tag_background};
                color: {colors.primary};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
                font-size: {STATIC_TOKENS['font.size.xxl']};
                font-weight: {STATIC_TOKENS['font.weight.bold']};
            }}
            QLabel#deviceCardName {{
                background: transparent;
                color: {colors.text};
                font-size: {STATIC_TOKENS['font.size.lg']};
                font-weight: {STATIC_TOKENS['font.weight.bold']};
            }}
            QLabel#deviceCardIp, QLabel#deviceCardProgressText {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {STATIC_TOKENS['font.size.sm']};
                font-weight: {STATIC_TOKENS['font.weight.medium']};
            }}
            """,
        )
        _call(self._connect_button, "setStyleSheet", _primary_button_style())
        _call(self._transfer_button, "setStyleSheet", _secondary_button_style())
        _call(self._detail_button, "setStyleSheet", _secondary_button_style())


__all__ = [
    "CalendarWidget",
    "DeviceCard",
    "LogViewer",
    "RuleEditorWidget",
    "TaskProgressBar",
    "TimelineWidget",
]
