# pyright: basic, reportMissingImports=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportIncompatibleMethodOverride=false

from __future__ import annotations

"""表单与筛选场景使用的主题输入组件。"""

import calendar
import re
from dataclasses import dataclass
from datetime import date as _date
from typing import Any, Iterable

from ...core.theme.tokens import STATIC_TOKENS, get_token_value
from ...core.types import ThemeMode

try:
    from PySide6.QtCore import QEasingCurve, Property, QDate, QPropertyAnimation, QRect, QSize, Qt, QTimer, Signal
    from PySide6.QtGui import QColor, QMouseEvent, QPaintEvent, QPainter
    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QDateEdit,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLayout,
        QLayoutItem,
        QLineEdit,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
        QWidgetItem,
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

    class QApplication(_BaseApplication):
        """无 Qt 环境时的最小应用对象。"""

        def property(self, _name: str) -> object | None:
            return None

    class QWidget(_BaseWidget):
        """无 Qt 环境时的最小部件。"""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._parent = parent
            self._object_name = ""
            self._style_sheet = ""
            self._properties: dict[str, object] = {}
            self._visible = True
            self._width = 0
            self._height = 0

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

        def setFixedSize(self, width: int, height: int) -> None:
            self._width = width
            self._height = height

        def setCursor(self, _cursor: object) -> None:
            return None

        def setSizePolicy(self, *_args: object) -> None:
            return None

        def update(self) -> None:
            return None

        def deleteLater(self) -> None:
            return None

        def setVisible(self, visible: bool) -> None:
            self._visible = visible

        def show(self) -> None:
            self._visible = True

        def hide(self) -> None:
            self._visible = False

        def setParent(self, parent: QWidget | None) -> None:
            self._parent = parent

    class QLabel(_BaseLabel):
        """无 Qt 环境时的最小文本标签。"""

        def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
            super().__init__(text, parent)
            self._text = text
            self._object_name = ""

        def setObjectName(self, name: str) -> None:
            self._object_name = name

        def setWordWrap(self, _enabled: bool) -> None:
            return None

        def setAlignment(self, _alignment: object) -> None:
            return None

        def text(self) -> str:
            return self._text

        def setText(self, text: str) -> None:
            self._text = text

        def setStyleSheet(self, _style: str) -> None:
            return None

    class QPushButton(_BasePushButton):
        """无 Qt 环境时的最小按钮。"""

        def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
            super().__init__(text, parent)
            self._text = text
            self._checked = False
            self._object_name = ""

        def setText(self, text: str) -> None:
            self._text = text

        def text(self) -> str:
            return self._text

        def setObjectName(self, name: str) -> None:
            self._object_name = name

        def setStyleSheet(self, _style: str) -> None:
            return None

        def setToolTip(self, _text: str) -> None:
            return None

        def setFixedSize(self, _width: int, _height: int) -> None:
            return None

        def setMinimumHeight(self, _height: int) -> None:
            return None

        def setMinimumWidth(self, _width: int) -> None:
            return None

        def setCursor(self, _cursor: object) -> None:
            return None

        def setCheckable(self, _value: bool) -> None:
            return None

        def setChecked(self, value: bool) -> None:
            self._checked = value

        def isChecked(self) -> bool:
            return self._checked

        def setVisible(self, _visible: bool) -> None:
            return None

    class QLineEdit(_BaseLineEdit):
        """无 Qt 环境时的最小单行输入框。"""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._text = ""
            self._placeholder = ""
            self._object_name = ""
            self.textChanged = Signal(str)
            self.returnPressed = Signal()
            self.editingFinished = Signal()

        def setObjectName(self, name: str) -> None:
            self._object_name = name

        def setStyleSheet(self, _style: str) -> None:
            return None

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

        def setMinimumWidth(self, _width: int) -> None:
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

        def addItems(self, items: Iterable[str]) -> None:
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

        def setObjectName(self, _name: str) -> None:
            return None

        def setStyleSheet(self, _style: str) -> None:
            return None

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

        def dayOfWeek(self) -> int:
            return _date(self.year_value, self.month_value, self.day_value).isoweekday()

        def addDays(self, days: int) -> "QDate":
            result = _date(self.year_value, self.month_value, self.day_value).toordinal() + days
            new_date = _date.fromordinal(result)
            return QDate(new_date.year, new_date.month, new_date.day)

    class QDateEdit(QWidget):
        """无 Qt 环境时的最小日期输入框。"""

        def __init__(self, date: QDate | None = None, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._date = date or QDate.currentDate()
            self.dateChanged = Signal(object)

        def setDate(self, date: QDate) -> None:
            self._date = date
            self.dateChanged.emit(date)

        def date(self) -> QDate:
            return self._date

        def setCalendarPopup(self, _enabled: bool) -> None:
            return None

        def setDisplayFormat(self, _fmt: str) -> None:
            return None

        def setObjectName(self, _name: str) -> None:
            return None

        def setStyleSheet(self, _style: str) -> None:
            return None

    class QTextEdit(QWidget):
        """无 Qt 环境时的最小多行文本框。"""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._text = ""
            self.textChanged = Signal()

        def toPlainText(self) -> str:
            return self._text

        def setPlainText(self, text: str) -> None:
            self._text = text
            self.textChanged.emit()

        def setPlaceholderText(self, _text: str) -> None:
            return None

        def setObjectName(self, _name: str) -> None:
            return None

        def setStyleSheet(self, _style: str) -> None:
            return None

        def setMinimumHeight(self, _height: int) -> None:
            return None

    class QFrame(_BaseFrame):
        """无 Qt 环境时的最小容器。"""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)

        def setObjectName(self, _name: str) -> None:
            return None

        def setStyleSheet(self, _style: str) -> None:
            return None

    class _SimpleMargins:
        def left(self) -> int:
            return 0

        def top(self) -> int:
            return 0

        def right(self) -> int:
            return 0

        def bottom(self) -> int:
            return 0

    class QLayout:
        """无 Qt 环境时的最小布局。"""

        def __init__(self, _parent: QWidget | None = None) -> None:
            self._items: list[object] = []

        def setContentsMargins(self, *_args: int) -> None:
            return None

        def setSpacing(self, _spacing: int) -> None:
            return None

        def addWidget(self, widget: QWidget, *_args: int) -> None:
            self._items.append(widget)

        def addLayout(self, layout: "QLayout", *_args: int) -> None:
            self._items.append(layout)

        def addStretch(self, *_args: int) -> None:
            return None

        def addChildWidget(self, widget: QWidget) -> None:
            self._items.append(widget)

        def contentsMargins(self) -> _SimpleMargins:
            return _SimpleMargins()

    class QVBoxLayout(QLayout, _BaseVBoxLayout):
        """无 Qt 环境时的最小垂直布局。"""

    class QHBoxLayout(QLayout, _BaseHBoxLayout):
        """无 Qt 环境时的最小水平布局。"""

    class QSize:
        """无 Qt 环境时的最小尺寸对象。"""

        def __init__(self, width: int = 0, height: int = 0) -> None:
            self._width = width
            self._height = height

        def width(self) -> int:
            return self._width

        def height(self) -> int:
            return self._height

        def expandedTo(self, other: "QSize") -> "QSize":
            return QSize(max(self._width, other.width()), max(self._height, other.height()))

        def __iadd__(self, other: "QSize") -> "QSize":
            self._width += other.width()
            self._height += other.height()
            return self

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

    class QLayoutItem:
        """无 Qt 环境时的最小布局项。"""

        def sizeHint(self) -> QSize:
            return QSize(0, 0)

        def minimumSize(self) -> QSize:
            return QSize(0, 0)

        def widget(self) -> QWidget | None:
            return None

        def setGeometry(self, _rect: QRect) -> None:
            return None

    class QWidgetItem(QLayoutItem):
        """无 Qt 环境时的最小部件布局项。"""

        def __init__(self, widget: QWidget) -> None:
            self._widget = widget

        def sizeHint(self) -> QSize:
            return QSize(120, 40)

        def minimumSize(self) -> QSize:
            return QSize(60, 32)

        def widget(self) -> QWidget | None:
            return self._widget

    class QSizePolicy:
        """无 Qt 环境时的最小尺寸策略。"""

        Expanding = 0
        Fixed = 1

    class QTimer:
        """无 Qt 环境时的最小定时器。"""

        def __init__(self, _parent: QWidget | None = None) -> None:
            self.timeout = Signal()

        def setSingleShot(self, _enabled: bool) -> None:
            return None

        def setInterval(self, _interval: int) -> None:
            return None

        def start(self) -> None:
            self.timeout.emit()

        def stop(self) -> None:
            return None

    class QPropertyAnimation:
        """无 Qt 环境时的最小动画对象。"""

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._end_value = 0.0

        def setDuration(self, _duration: int) -> None:
            return None

        def setEasingCurve(self, _curve: object) -> None:
            return None

        def setStartValue(self, _value: float) -> None:
            return None

        def setEndValue(self, value: float) -> None:
            self._end_value = value

        def start(self) -> None:
            return None

    class QEasingCurve:
        """无 Qt 环境时的最小缓动枚举。"""

        OutCubic = 0

    class QColor:
        """无 Qt 环境时的最小颜色对象。"""

        def __init__(self, value: str) -> None:
            self.value = value

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

    class QPaintEvent:
        """无 Qt 环境时的最小绘制事件。"""

    class QMouseEvent:
        """无 Qt 环境时的最小鼠标事件。"""

        def button(self) -> int:
            return 1

    class Qt:
        """无 Qt 环境时的最小 Qt 常量集合。"""

        LeftButton = 1
        NoPen = 0
        PointingHandCursor = 0

        @staticmethod
        def Orientation(value: int) -> int:
            return value

    def Property(_type: object, getter: Any, setter: Any) -> property:
        """无 Qt 环境时的最小属性工厂。"""

        return property(getter, setter)


def _call(target: object, method_name: str, *args: object) -> None:
    """安全调用可能不存在的 Qt 方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        method(*args)


def _connect(signal_object: object, callback: object) -> None:
    """安全连接 Qt 风格信号。"""

    connect = getattr(signal_object, "connect", None)
    if callable(connect):
        connect(callback)


def _coerce_mode(value: object) -> ThemeMode:
    """将运行时值归一化为主题模式。"""

    if isinstance(value, ThemeMode):
        return value
    if isinstance(value, str) and value.lower() == ThemeMode.DARK.value:
        return ThemeMode.DARK
    return ThemeMode.LIGHT


def _theme_mode() -> ThemeMode:
    """尽量从应用实例读取当前主题模式。"""

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
    """读取主题 token。"""

    return get_token_value(name, mode or _theme_mode())


def _static_token(name: str) -> str:
    """读取静态 token。"""

    return STATIC_TOKENS[name]


def _px(name: str) -> int:
    """将像素 token 转为整数。"""

    return int(_static_token(name).replace("px", ""))


SPACING_XS = _px("spacing.xs")
SPACING_SM = _px("spacing.sm")
SPACING_MD = _px("spacing.md")
SPACING_LG = _px("spacing.lg")
SPACING_XL = _px("spacing.xl")
SPACING_2XL = _px("spacing.2xl")
RADIUS_SM = _px("radius.sm")
RADIUS_MD = _px("radius.md")
RADIUS_LG = _px("radius.lg")
INPUT_HEIGHT = _px("input.height")
BUTTON_HEIGHT = _px("button.height.sm")


@dataclass(frozen=True)
class _Palette:
    """组件局部使用的主题色板。"""

    surface: str
    surface_alt: str
    text: str
    text_muted: str
    text_inverse: str
    border: str
    border_strong: str
    border_focus: str
    primary: str
    primary_hover: str
    primary_pressed: str
    danger: str
    tag_background: str


def _palette(mode: ThemeMode | None = None) -> _Palette:
    """生成当前主题的常用色板。"""

    resolved_mode = mode or _theme_mode()
    return _Palette(
        surface=_token("surface.secondary", resolved_mode),
        surface_alt=_token("surface.sunken", resolved_mode),
        text=_token("text.primary", resolved_mode),
        text_muted=_token("text.secondary", resolved_mode),
        text_inverse=_token("text.inverse", resolved_mode),
        border=_token("border.default", resolved_mode),
        border_strong=_token("border.strong", resolved_mode),
        border_focus=_token("border.focus", resolved_mode),
        primary=_token("brand.primary", resolved_mode),
        primary_hover=_token("brand.primary_hover", resolved_mode),
        primary_pressed=_token("brand.primary_pressed", resolved_mode),
        danger=_token("status.error", resolved_mode),
        tag_background=_token("tag.color.neutral", resolved_mode),
    )


def _label_style() -> str:
    """上方标签的统一样式。"""

    colors = _palette()
    return (
        f"color: {colors.text};"
        f"font-size: {_static_token('font.size.sm')};"
        f"font-weight: {_static_token('font.weight.semibold')};"
    )


def _helper_style(error: bool = False) -> str:
    """辅助说明与错误文案样式。"""

    colors = _palette()
    color = colors.danger if error else colors.text_muted
    return f"color: {color}; font-size: {_static_token('font.size.xs')};"


def _input_style(*, error: bool = False, min_height: int = INPUT_HEIGHT, padding_vertical: int = SPACING_LG) -> str:
    """基础输入控件样式。"""

    colors = _palette()
    border_color = colors.danger if error else colors.border
    focus_color = colors.danger if error else colors.primary
    return f"""
        background-color: {colors.surface_alt};
        color: {colors.text};
        border: 1px solid {border_color};
        border-radius: {RADIUS_MD}px;
        padding: {padding_vertical}px {SPACING_XL}px;
        min-height: {min_height}px;
        selection-background-color: {colors.primary};
        selection-color: {colors.text_inverse};
    """ + (
        f"QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {{ border: 1px solid {focus_color}; }}"
    )


class FlowLayout(QLayout):
    """用于标签芯片的流式布局。"""

    def __init__(self, parent: QWidget | None = None, margin: int = 0, h_spacing: int = SPACING_SM, v_spacing: int = SPACING_SM) -> None:
        super().__init__(parent)
        self._items: list[QLayoutItem] = []
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        _call(self, "setContentsMargins", margin, margin, margin, margin)

    def addItem(self, item: QLayoutItem) -> None:
        self._items.append(item)

    def addWidget(self, widget: QWidget) -> None:
        self.insertWidget(self.count(), widget)

    def insertWidget(self, index: int, widget: QWidget) -> None:
        add_child = getattr(self, "addChildWidget", None)
        if callable(add_child):
            add_child(widget)
        self._items.insert(index, QWidgetItem(widget))

    def removeWidget(self, widget: QWidget) -> None:
        for index, item in enumerate(list(self._items)):
            if item.widget() is widget:
                self.takeAt(index)
                _call(widget, "setParent", None)
                return

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int) -> QLayoutItem | None:
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int) -> QLayoutItem | None:
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self) -> object:
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect: QRect) -> None:
        parent_method = getattr(super(), "setGeometry", None)
        if callable(parent_method):
            parent_method(rect)
        self._do_layout(rect, False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize(0, 0)
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins() if hasattr(self, "contentsMargins") else None
        if margins is not None:
            size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        x = rect.x()
        y = rect.y()
        line_height = 0

        for item in self._items:
            hint = item.sizeHint()
            next_x = x + hint.width() + self._h_spacing
            if line_height and next_x - self._h_spacing > rect.right():
                x = rect.x()
                y += line_height + self._v_spacing
                next_x = x + hint.width() + self._h_spacing
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(x, y, hint.width(), hint.height()))

            x = next_x
            line_height = max(line_height, hint.height())

        return y + line_height - rect.y()


class TagChip(QFrame):
    """可移除的标签芯片。"""

    close_requested = Signal(str)

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._text = text
        _call(self, "setObjectName", "tagInputChip")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING_MD, SPACING_XS, SPACING_SM, SPACING_XS)
        layout.setSpacing(SPACING_XS)

        self._label = QLabel(text)
        _call(self._label, "setObjectName", "tagInputChipLabel")

        self._close_button = QPushButton("×")
        _call(self._close_button, "setObjectName", "tagInputChipClose")
        _call(self._close_button, "setToolTip", "移除标签")
        _call(self._close_button, "setFixedSize", 18, 18)
        _connect(getattr(self._close_button, "clicked", None), lambda: self.close_requested.emit(self._text))

        layout.addWidget(self._label)
        layout.addWidget(self._close_button)
        self._apply_styles()

    @property
    def text(self) -> str:
        """返回芯片文本。"""

        return self._text

    def _apply_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QFrame#tagInputChip {{
                background-color: {colors.tag_background};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#tagInputChipLabel {{
                color: {colors.text};
                background: transparent;
                font-size: {_static_token('font.size.sm')};
            }}
            QPushButton#tagInputChipClose {{
                background-color: transparent;
                border: none;
                border-radius: {RADIUS_SM}px;
                color: {colors.text_muted};
                padding: 0;
                font-size: {_static_token('font.size.sm')};
                min-height: 18px;
                min-width: 18px;
            }}
            QPushButton#tagInputChipClose:hover {{
                color: {colors.text};
                background-color: {colors.surface};
            }}
            """,
        )


class SearchBar(QWidget):
    """带搜索图标、清空按钮和防抖信号的搜索框。"""

    search_changed = Signal(str)

    def __init__(self, placeholder: str = "搜索...", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "searchBar")
        _call(self, "setMinimumHeight", INPUT_HEIGHT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_XS, SPACING_LG, SPACING_XS)
        layout.setSpacing(SPACING_MD)

        self._icon = QLabel("⌕")
        _call(self._icon, "setObjectName", "searchBarIcon")

        self._line_edit = QLineEdit(self)
        _call(self._line_edit, "setObjectName", "searchBarField")
        _call(self._line_edit, "setPlaceholderText", placeholder)
        _call(self._line_edit, "setFrame", False)

        self._clear_button = QPushButton("×", self)
        _call(self._clear_button, "setObjectName", "searchBarClear")
        _call(self._clear_button, "setToolTip", "清空搜索")
        _call(self._clear_button, "setFixedSize", 24, 24)
        _call(self._clear_button, "setVisible", False)

        self._debounce_timer = QTimer(self)
        _call(self._debounce_timer, "setSingleShot", True)
        _call(self._debounce_timer, "setInterval", 300)

        _connect(getattr(self._line_edit, "textChanged", None), self._on_text_changed)
        _connect(getattr(self._clear_button, "clicked", None), self.clear)
        _connect(getattr(self._debounce_timer, "timeout", None), self._emit_search_changed)

        layout.addWidget(self._icon)
        layout.addWidget(self._line_edit, 1)
        layout.addWidget(self._clear_button)
        self._apply_styles()

    def text(self) -> str:
        """返回当前搜索文本。"""

        text_reader = getattr(self._line_edit, "text", None)
        return str(text_reader()) if callable(text_reader) else ""

    def setText(self, text: str) -> None:
        """设置搜索文本。"""

        _call(self._line_edit, "setText", text)
        self._on_text_changed(text)

    def clear(self) -> None:
        """清空搜索文本并立即触发变更。"""

        _call(self._line_edit, "clear")
        self._on_text_changed("")
        self._emit_search_changed()

    @property
    def line_edit(self) -> QLineEdit:
        """暴露内部 QLineEdit 以便集成。"""

        return self._line_edit

    def _on_text_changed(self, text: str) -> None:
        _call(self._clear_button, "setVisible", bool(text))
        _call(self._debounce_timer, "start")

    def _emit_search_changed(self) -> None:
        self.search_changed.emit(self.text())

    def _apply_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#searchBar {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {_px('radius.pill')}px;
            }}
            QLabel#searchBarIcon {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.lg')};
            }}
            QLineEdit#searchBarField {{
                background: transparent;
                border: none;
                color: {colors.text};
                padding: 0;
                min-height: {INPUT_HEIGHT - SPACING_MD}px;
                font-size: {_static_token('font.size.md')};
            }}
            QLineEdit#searchBarField:focus {{
                border: none;
            }}
            QPushButton#searchBarClear {{
                background-color: transparent;
                border: none;
                color: {colors.text_muted};
                border-radius: {RADIUS_SM}px;
                padding: 0;
                min-height: 24px;
                min-width: 24px;
            }}
            QPushButton#searchBarClear:hover {{
                background-color: {colors.surface};
                color: {colors.text};
            }}
            """,
        )


class FilterDropdown(QWidget):
    """带标签与统一主题样式的筛选下拉框。"""

    filter_changed = Signal(str)

    def __init__(
        self,
        label: str = "筛选条件",
        items: Iterable[str] | None = None,
        include_all: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "filterDropdown")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        self._label = QLabel(label)
        _call(self._label, "setObjectName", "filterDropdownLabel")
        self._combo_box = QComboBox(self)
        _call(self._combo_box, "setObjectName", "filterDropdownField")

        layout.addWidget(self._label)
        layout.addWidget(self._combo_box)

        self.set_items(items or [], include_all=include_all)
        _connect(getattr(self._combo_box, "currentTextChanged", None), self.filter_changed.emit)
        self._apply_styles()

    def set_items(self, items: Iterable[str], include_all: bool = True) -> None:
        """重置筛选选项。"""

        resolved_items = [str(item) for item in items]
        if include_all and "全部" not in resolved_items:
            resolved_items.insert(0, "全部")
        _call(self._combo_box, "clear")
        add_items = getattr(self._combo_box, "addItems", None)
        if callable(add_items):
            add_items(resolved_items)
        else:
            for item in resolved_items:
                _call(self._combo_box, "addItem", item)

    def current_text(self) -> str:
        """返回当前筛选值。"""

        reader = getattr(self._combo_box, "currentText", None)
        return str(reader()) if callable(reader) else ""

    def set_current_text(self, text: str) -> None:
        """设置当前筛选值。"""

        _call(self._combo_box, "setCurrentText", text)

    @property
    def combo_box(self) -> QComboBox:
        """暴露内部下拉框。"""

        return self._combo_box

    def _apply_styles(self) -> None:
        _call(self._label, "setStyleSheet", _label_style())
        _call(self._combo_box, "setStyleSheet", _input_style())


class DateRangePicker(QWidget):
    """支持快捷范围选择的日期区间选择器。"""

    range_changed = Signal(QDate, QDate)

    def __init__(self, label: str = "日期范围", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "dateRangePicker")
        self._updating = False
        self._active_preset = "本周"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        self._label = QLabel(label)
        _call(self._label, "setObjectName", "dateRangePickerLabel")
        layout.addWidget(self._label)

        field_row = QHBoxLayout()
        field_row.setSpacing(SPACING_MD)

        self._start_edit = QDateEdit(QDate.currentDate(), self)
        self._end_edit = QDateEdit(QDate.currentDate(), self)
        _call(self._start_edit, "setObjectName", "dateRangeStart")
        _call(self._end_edit, "setObjectName", "dateRangeEnd")
        _call(self._start_edit, "setCalendarPopup", True)
        _call(self._end_edit, "setCalendarPopup", True)
        _call(self._start_edit, "setDisplayFormat", "yyyy-MM-dd")
        _call(self._end_edit, "setDisplayFormat", "yyyy-MM-dd")

        self._separator = QLabel("至")
        _call(self._separator, "setObjectName", "dateRangeSeparator")

        field_row.addWidget(self._start_edit)
        field_row.addWidget(self._separator)
        field_row.addWidget(self._end_edit)
        layout.addLayout(field_row)

        preset_row = QHBoxLayout()
        preset_row.setSpacing(SPACING_SM)
        self._preset_buttons: dict[str, QPushButton] = {}
        for name in ("今天", "本周", "本月", "自定义"):
            button = QPushButton(name, self)
            _call(button, "setObjectName", "dateRangePreset")
            _call(button, "setCheckable", True)
            self._preset_buttons[name] = button
            preset_row.addWidget(button)
        preset_row.addStretch(1)
        layout.addLayout(preset_row)

        _connect(getattr(self._start_edit, "dateChanged", None), self._on_date_edited)
        _connect(getattr(self._end_edit, "dateChanged", None), self._on_date_edited)
        _connect(getattr(self._preset_buttons["今天"], "clicked", None), self._apply_today)
        _connect(getattr(self._preset_buttons["本周"], "clicked", None), self._apply_this_week)
        _connect(getattr(self._preset_buttons["本月"], "clicked", None), self._apply_this_month)
        _connect(getattr(self._preset_buttons["自定义"], "clicked", None), self._set_custom_mode)

        self._apply_styles()
        self._apply_this_week()

    def range(self) -> tuple[QDate, QDate]:
        """返回当前日期区间。"""

        return (self._start_edit.date(), self._end_edit.date())

    def set_range(self, start_date: QDate, end_date: QDate, preset: str = "自定义") -> None:
        """设置日期区间并同步状态。"""

        self._updating = True
        if end_date < start_date:
            start_date, end_date = end_date, start_date
        _call(self._start_edit, "setDate", start_date)
        _call(self._end_edit, "setDate", end_date)
        self._updating = False
        self._set_active_preset(preset)
        self.range_changed.emit(start_date, end_date)

    def _on_date_edited(self, _date: QDate) -> None:
        if self._updating:
            return
        start_date, end_date = self.range()
        if end_date < start_date:
            self._updating = True
            _call(self._end_edit, "setDate", start_date)
            end_date = start_date
            self._updating = False
        self._set_active_preset("自定义")
        self.range_changed.emit(start_date, end_date)

    def _apply_today(self) -> None:
        today = QDate.currentDate()
        self.set_range(today, today, preset="今天")

    def _apply_this_week(self) -> None:
        today = QDate.currentDate()
        start_date = today.addDays(1 - today.dayOfWeek())
        end_date = start_date.addDays(6)
        self.set_range(start_date, end_date, preset="本周")

    def _apply_this_month(self) -> None:
        today = QDate.currentDate()
        start_date = QDate(today.year(), today.month(), 1)
        month_days = calendar.monthrange(today.year(), today.month())[1]
        end_date = QDate(today.year(), today.month(), month_days)
        self.set_range(start_date, end_date, preset="本月")

    def _set_custom_mode(self) -> None:
        self._set_active_preset("自定义")
        start_date, end_date = self.range()
        self.range_changed.emit(start_date, end_date)

    def _set_active_preset(self, preset_name: str) -> None:
        self._active_preset = preset_name
        for name, button in self._preset_buttons.items():
            _call(button, "setChecked", name == preset_name)
        self._apply_styles()

    def _apply_styles(self) -> None:
        colors = _palette()
        _call(self._label, "setStyleSheet", _label_style())
        _call(self._separator, "setStyleSheet", f"color: {colors.text_muted};")
        _call(self._start_edit, "setStyleSheet", _input_style())
        _call(self._end_edit, "setStyleSheet", _input_style())

        for name, button in self._preset_buttons.items():
            is_active = name == self._active_preset
            background = colors.primary if is_active else colors.surface
            foreground = colors.text_inverse if is_active else colors.text_muted
            border = colors.primary if is_active else colors.border
            _call(
                button,
                "setStyleSheet",
                f"""
                QPushButton#dateRangePreset {{
                    background-color: {background};
                    color: {foreground};
                    border: 1px solid {border};
                    border-radius: {RADIUS_MD}px;
                    padding: {SPACING_MD}px {SPACING_LG}px;
                    min-height: {BUTTON_HEIGHT}px;
                }}
                QPushButton#dateRangePreset:hover {{
                    border-color: {colors.primary};
                    color: {colors.text if not is_active else colors.text_inverse};
                }}
                """,
            )


class TagInput(QWidget):
    """将输入内容转为可移除标签芯片的标签输入框。"""

    tags_changed = Signal(list)

    def __init__(
        self,
        label: str = "标签",
        placeholder: str = "输入标签后按回车",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "tagInput")
        self._tags: list[str] = []
        self._chips: dict[str, TagChip] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        self._label = QLabel(label)
        _call(self._label, "setObjectName", "tagInputLabel")
        layout.addWidget(self._label)

        self._container = QFrame(self)
        _call(self._container, "setObjectName", "tagInputContainer")
        self._flow = FlowLayout(self._container, h_spacing=SPACING_SM, v_spacing=SPACING_SM)

        self._input = QLineEdit(self._container)
        _call(self._input, "setObjectName", "tagInputEditor")
        _call(self._input, "setPlaceholderText", placeholder)
        _call(self._input, "setFrame", False)
        _call(self._input, "setMinimumWidth", 120)
        self._flow.addWidget(self._input)

        layout.addWidget(self._container)
        _connect(getattr(self._input, "returnPressed", None), self._commit_pending_input)
        self._apply_styles()

    def tags(self) -> list[str]:
        """返回当前标签列表。"""

        return list(self._tags)

    def set_tags(self, tags: Iterable[str]) -> None:
        """批量设置标签列表。"""

        self.clear_tags()
        for tag in tags:
            self.add_tag(str(tag), emit_signal=False)
        self.tags_changed.emit(self.tags())

    def add_tag(self, tag: str, *, emit_signal: bool = True) -> None:
        """添加单个标签。"""

        cleaned = tag.strip()
        if not cleaned or cleaned in self._chips:
            return

        chip = TagChip(cleaned, self._container)
        _connect(chip.close_requested, self.remove_tag)
        self._chips[cleaned] = chip
        self._tags.append(cleaned)
        self._flow.insertWidget(max(self._flow.count() - 1, 0), chip)

        if emit_signal:
            self.tags_changed.emit(self.tags())

    def remove_tag(self, tag: str) -> None:
        """移除单个标签。"""

        chip = self._chips.pop(tag, None)
        if chip is None:
            return

        self._tags = [item for item in self._tags if item != tag]
        self._flow.removeWidget(chip)
        _call(chip, "deleteLater")
        self.tags_changed.emit(self.tags())

    def clear_tags(self) -> None:
        """清空全部标签。"""

        for tag in list(self._tags):
            self.remove_tag(tag)

    @property
    def line_edit(self) -> QLineEdit:
        """暴露内部输入框。"""

        return self._input

    def _commit_pending_input(self) -> None:
        text_reader = getattr(self._input, "text", None)
        raw_text = str(text_reader()) if callable(text_reader) else ""
        for token in [part.strip() for part in re.split(r"[,，;；\n]+", raw_text) if part.strip()]:
            self.add_tag(token, emit_signal=False)
        _call(self._input, "clear")
        self.tags_changed.emit(self.tags())

    def _apply_styles(self) -> None:
        colors = _palette()
        _call(self._label, "setStyleSheet", _label_style())
        _call(
            self._container,
            "setStyleSheet",
            f"""
            QFrame#tagInputContainer {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_MD}px;
            }}
            QLineEdit#tagInputEditor {{
                background: transparent;
                border: none;
                color: {colors.text};
                min-height: {INPUT_HEIGHT - SPACING_MD}px;
                padding: {SPACING_XS}px {SPACING_SM}px;
                font-size: {_static_token('font.size.md')};
            }}
            """,
        )


class ThemedLineEdit(QWidget):
    """带标签、辅助文案与错误态的主题单行输入框。"""

    def __init__(
        self,
        label: str = "输入字段",
        placeholder: str = "请输入内容",
        helper_text: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "themedLineEdit")
        self._helper_text = helper_text
        self._error_text = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        self._label = QLabel(label)
        _call(self._label, "setObjectName", "themedLineEditLabel")
        self._line_edit = QLineEdit(self)
        _call(self._line_edit, "setObjectName", "themedLineEditField")
        _call(self._line_edit, "setPlaceholderText", placeholder)
        self._message = QLabel(helper_text)
        _call(self._message, "setObjectName", "themedLineEditMessage")
        _call(self._message, "setWordWrap", True)

        layout.addWidget(self._label)
        layout.addWidget(self._line_edit)
        layout.addWidget(self._message)
        self._apply_styles()

    def text(self) -> str:
        """返回输入值。"""

        reader = getattr(self._line_edit, "text", None)
        return str(reader()) if callable(reader) else ""

    def setText(self, text: str) -> None:
        """设置输入值。"""

        _call(self._line_edit, "setText", text)

    def set_error(self, message: str) -> None:
        """切换到错误态。"""

        self._error_text = message
        _call(self._message, "setText", message)
        self._apply_styles()

    def clear_error(self) -> None:
        """清除错误态。"""

        self._error_text = ""
        _call(self._message, "setText", self._helper_text)
        self._apply_styles()

    def set_helper_text(self, text: str) -> None:
        """设置辅助说明。"""

        self._helper_text = text
        if not self._error_text:
            _call(self._message, "setText", text)
            self._apply_styles()

    @property
    def line_edit(self) -> QLineEdit:
        """暴露内部输入框。"""

        return self._line_edit

    def _apply_styles(self) -> None:
        _call(self._label, "setStyleSheet", _label_style())
        _call(self._line_edit, "setStyleSheet", _input_style(error=bool(self._error_text)))
        _call(self._message, "setStyleSheet", _helper_style(error=bool(self._error_text)))


class ThemedComboBox(QWidget):
    """带上方标签的主题下拉选择框。"""

    def __init__(
        self,
        label: str = "选择项",
        items: Iterable[str] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "themedComboBox")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        self._label = QLabel(label)
        _call(self._label, "setObjectName", "themedComboBoxLabel")
        self._combo_box = QComboBox(self)
        _call(self._combo_box, "setObjectName", "themedComboBoxField")

        layout.addWidget(self._label)
        layout.addWidget(self._combo_box)

        if items:
            add_items = getattr(self._combo_box, "addItems", None)
            if callable(add_items):
                add_items([str(item) for item in items])
        self._apply_styles()

    def current_text(self) -> str:
        """返回当前选项文案。"""

        reader = getattr(self._combo_box, "currentText", None)
        return str(reader()) if callable(reader) else ""

    def add_items(self, items: Iterable[str]) -> None:
        """追加多个选项。"""

        add_items = getattr(self._combo_box, "addItems", None)
        if callable(add_items):
            add_items([str(item) for item in items])

    @property
    def combo_box(self) -> QComboBox:
        """暴露内部下拉框。"""

        return self._combo_box

    def _apply_styles(self) -> None:
        _call(self._label, "setStyleSheet", _label_style())
        _call(self._combo_box, "setStyleSheet", _input_style())


class ThemedTextEdit(QWidget):
    """带字符统计的主题多行输入框。"""

    def __init__(
        self,
        label: str = "文本内容",
        placeholder: str = "请输入详细内容",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "themedTextEdit")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        self._label = QLabel(label)
        _call(self._label, "setObjectName", "themedTextEditLabel")
        self._text_edit = QTextEdit(self)
        _call(self._text_edit, "setObjectName", "themedTextEditField")
        _call(self._text_edit, "setPlaceholderText", placeholder)
        _call(self._text_edit, "setMinimumHeight", 120)
        self._count_label = QLabel("0 字")
        _call(self._count_label, "setObjectName", "themedTextEditCount")

        layout.addWidget(self._label)
        layout.addWidget(self._text_edit)
        layout.addWidget(self._count_label)

        _connect(getattr(self._text_edit, "textChanged", None), self._update_count)
        self._apply_styles()
        self._update_count()

    def toPlainText(self) -> str:
        """返回当前文本内容。"""

        reader = getattr(self._text_edit, "toPlainText", None)
        return str(reader()) if callable(reader) else ""

    def setPlainText(self, text: str) -> None:
        """设置文本内容。"""

        _call(self._text_edit, "setPlainText", text)
        self._update_count()

    @property
    def text_edit(self) -> QTextEdit:
        """暴露内部多行输入框。"""

        return self._text_edit

    def _update_count(self) -> None:
        _call(self._count_label, "setText", f"{len(self.toPlainText())} 字")

    def _apply_styles(self) -> None:
        _call(self._label, "setStyleSheet", _label_style())
        _call(self._text_edit, "setStyleSheet", _input_style(min_height=96, padding_vertical=SPACING_MD))
        _call(self._count_label, "setStyleSheet", _helper_style())


class ToggleSwitch(QWidget):
    """带平滑滑块动画的自绘切换开关。"""

    toggled = Signal(bool)

    def __init__(self, checked: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "toggleSwitch")
        _call(self, "setFixedSize", 52, 30)
        _call(self, "setCursor", getattr(Qt, "PointingHandCursor", 0))
        self._checked = checked
        self._offset = 1.0 if checked else 0.0
        self._animation = QPropertyAnimation(self, b"offset", self) if QT_AVAILABLE else None
        if self._animation is not None:
            self._animation.setDuration(180)
            self._animation.setEasingCurve(QEasingCurve.OutCubic)

    def isChecked(self) -> bool:
        """返回当前开关状态。"""

        return self._checked

    def setChecked(self, checked: bool) -> None:
        """设置开关状态。"""

        if self._checked == checked:
            return
        self._checked = checked
        target = 1.0 if checked else 0.0
        if self._animation is not None:
            self._animation.setStartValue(self._offset)
            self._animation.setEndValue(target)
            self._animation.start()
        else:
            self.offset = target
        self.toggled.emit(checked)
        _call(self, "update")

    def toggle(self) -> None:
        """切换当前状态。"""

        self.setChecked(not self._checked)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """点击时切换状态。"""

        button = getattr(event, "button", None)
        if callable(button) and button() == getattr(Qt, "LeftButton", 1):
            self.toggle()
        parent_method = getattr(super(), "mousePressEvent", None)
        if callable(parent_method):
            parent_method(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制轨道和滑块。"""

        if not QT_AVAILABLE:
            return

        colors = _palette()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.setPen(Qt.NoPen)

        track_color = QColor(colors.primary if self._checked else colors.border_strong)
        painter.setBrush(track_color)
        painter.drawRoundedRect(rect, rect.height() / 2, rect.height() / 2)

        knob_size = rect.height() - 4
        knob_x = rect.x() + 2 + ((rect.width() - knob_size - 4) * self._offset)
        painter.setBrush(QColor(colors.surface))
        painter.drawEllipse(int(knob_x), rect.y() + 2, knob_size, knob_size)

        parent_method = getattr(super(), "paintEvent", None)
        if callable(parent_method):
            parent_method(event)

    def _get_offset(self) -> float:
        return self._offset

    def _set_offset(self, value: float) -> None:
        self._offset = value
        _call(self, "update")

    offset = Property(float, _get_offset, _set_offset)


class LabeledLineEdit(ThemedLineEdit):
    """兼容旧命名的主题单行输入框。"""

    def __init__(self, label: str = "输入字段", parent: QWidget | None = None) -> None:
        super().__init__(label=label, parent=parent)


class SearchInput(SearchBar):
    """兼容旧命名的搜索输入框。"""

    def __init__(self, placeholder: str = "搜索...", parent: QWidget | None = None) -> None:
        super().__init__(placeholder=placeholder, parent=parent)


__all__ = [
    "DateRangePicker",
    "FilterDropdown",
    "FlowLayout",
    "LabeledLineEdit",
    "SearchBar",
    "SearchInput",
    "TagInput",
    "ThemedComboBox",
    "ThemedLineEdit",
    "ThemedTextEdit",
    "ToggleSwitch",
]
