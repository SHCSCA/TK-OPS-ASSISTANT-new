# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportArgumentType=false, reportCallIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

from __future__ import annotations

"""分析场景使用的自绘可视化组件。"""

import re
from dataclasses import dataclass
from math import cos, pi, sin
from random import Random
from typing import Sequence

from ...core.qt import QApplication, Signal, QWidget
from ...core.theme.tokens import STATIC_TOKENS, get_token_value
from ...core.types import ThemeMode

try:
    from PySide6.QtCore import QPoint, QPointF, QRectF, QSize, Qt
    from PySide6.QtGui import QColor, QFont, QFontMetrics, QMouseEvent, QPaintEvent, QPainter, QPen, QPolygonF
    from PySide6.QtWidgets import QToolTip
except ImportError:
    class QPoint:
        """无 Qt 环境时的点坐标占位对象。"""

        def __init__(self, x: int = 0, y: int = 0) -> None:
            self._x = x
            self._y = y

        def x(self) -> int:
            return self._x

        def y(self) -> int:
            return self._y

    class QPointF:
        """无 Qt 环境时的浮点点坐标占位对象。"""

        def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
            self._x = float(x)
            self._y = float(y)

        def x(self) -> float:
            return self._x

        def y(self) -> float:
            return self._y

        def toPoint(self) -> QPoint:
            return QPoint(int(round(self._x)), int(round(self._y)))

    class QRectF:
        """无 Qt 环境时的矩形占位对象。"""

        def __init__(self, x: float | QRectF = 0.0, y: float = 0.0, width: float = 0.0, height: float = 0.0) -> None:
            if isinstance(x, QRectF):
                self._x = x.x()
                self._y = x.y()
                self._width = x.width()
                self._height = x.height()
                return
            self._x = float(x)
            self._y = float(y)
            self._width = float(width)
            self._height = float(height)

        def x(self) -> float:
            return self._x

        def y(self) -> float:
            return self._y

        def left(self) -> float:
            return self._x

        def top(self) -> float:
            return self._y

        def right(self) -> float:
            return self._x + self._width

        def bottom(self) -> float:
            return self._y + self._height

        def width(self) -> float:
            return self._width

        def height(self) -> float:
            return self._height

        def center(self) -> QPointF:
            return QPointF(self._x + self._width / 2.0, self._y + self._height / 2.0)

        def adjusted(self, left: float, top: float, right: float, bottom: float) -> QRectF:
            return QRectF(self._x + left, self._y + top, self._width - left + right, self._height - top + bottom)

        def contains(self, point: QPoint | QPointF) -> bool:
            x = float(point.x())
            y = float(point.y())
            return self.left() <= x <= self.right() and self.top() <= y <= self.bottom()

        def intersects(self, other: QRectF) -> bool:
            return not (
                self.right() <= other.left()
                or self.left() >= other.right()
                or self.bottom() <= other.top()
                or self.top() >= other.bottom()
            )

    class QSize:
        """无 Qt 环境时的尺寸占位对象。"""

        def __init__(self, width: int = 0, height: int = 0) -> None:
            self._width = width
            self._height = height

        def width(self) -> int:
            return self._width

        def height(self) -> int:
            return self._height

    class QColor:
        """无 Qt 环境时的颜色占位对象。"""

        def __init__(self, *args: object) -> None:
            self._red = 0
            self._green = 0
            self._blue = 0
            self._alpha = 255
            if len(args) == 1 and isinstance(args[0], str):
                self._apply_css_color(args[0])
            elif len(args) >= 3:
                self._red = int(args[0])
                self._green = int(args[1])
                self._blue = int(args[2])
                self._alpha = int(args[3]) if len(args) >= 4 else 255

        def _apply_css_color(self, value: str) -> None:
            text = value.strip()
            if text.startswith("#") and len(text) in {7, 9}:
                self._red = int(text[1:3], 16)
                self._green = int(text[3:5], 16)
                self._blue = int(text[5:7], 16)
                self._alpha = int(text[7:9], 16) if len(text) == 9 else 255
                return
            match = re.fullmatch(r"rgba?\(([^)]+)\)", text)
            if match:
                parts = [part.strip() for part in match.group(1).split(",")]
                if len(parts) >= 3:
                    self._red = int(float(parts[0]))
                    self._green = int(float(parts[1]))
                    self._blue = int(float(parts[2]))
                    if len(parts) == 4:
                        alpha_value = float(parts[3])
                        self._alpha = int(round(alpha_value * 255)) if alpha_value <= 1 else int(round(alpha_value))

        def red(self) -> int:
            return self._red

        def green(self) -> int:
            return self._green

        def blue(self) -> int:
            return self._blue

        def alpha(self) -> int:
            return self._alpha

        def setAlphaF(self, value: float) -> None:
            self._alpha = int(round(max(0.0, min(1.0, value)) * 255))

    class QFont:
        """无 Qt 环境时的字体占位对象。"""

        def __init__(self, family: str = "", parent: object | None = None) -> None:
            del parent
            self._family = family
            self._pixel_size = 12
            self._weight = 400
            self._bold = False

        def setPixelSize(self, value: int) -> None:
            self._pixel_size = value

        def setWeight(self, value: int) -> None:
            self._weight = value

        def setBold(self, value: bool) -> None:
            self._bold = value

        def pixelSize(self) -> int:
            return self._pixel_size

    class QFontMetrics:
        """无 Qt 环境时的字形测量占位对象。"""

        def __init__(self, font: QFont) -> None:
            self._font = font

        def horizontalAdvance(self, text: str) -> int:
            return int(len(text) * max(self._font.pixelSize(), 12) * 0.68)

        def height(self) -> int:
            return int(max(self._font.pixelSize(), 12) * 1.35)

    class QPaintEvent:
        """无 Qt 环境时的绘制事件占位对象。"""

    class QMouseEvent:
        """无 Qt 环境时的鼠标事件占位对象。"""

        def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
            self._point = QPointF(x, y)

        def position(self) -> QPointF:
            return self._point

        def globalPosition(self) -> QPointF:
            return self._point

        def pos(self) -> QPoint:
            return self._point.toPoint()

        def button(self) -> int:
            return 1

    class QPen:
        """无 Qt 环境时的画笔占位对象。"""

        def __init__(self, color: QColor | int | None = None, width: float = 1.0) -> None:
            self.color = color
            self.width = width

        def setCapStyle(self, style: object) -> None:
            del style

    class QPolygonF(list):
        """无 Qt 环境时的多边形占位对象。"""

    class QPainter:
        """无 Qt 环境时的绘图器占位对象。"""

        Antialiasing = 0

        def __init__(self, widget: QWidget) -> None:
            del widget
            self._font = QFont()

        def setRenderHint(self, hint: object, enabled: bool) -> None:
            del hint, enabled

        def setBrush(self, brush: object) -> None:
            del brush

        def setPen(self, pen: object) -> None:
            del pen

        def setFont(self, font: QFont) -> None:
            self._font = font

        def font(self) -> QFont:
            return self._font

        def fillRect(self, *args: object) -> None:
            del args

        def drawRoundedRect(self, *args: object) -> None:
            del args

        def drawRect(self, *args: object) -> None:
            del args

        def drawEllipse(self, *args: object) -> None:
            del args

        def drawLine(self, *args: object) -> None:
            del args

        def drawArc(self, *args: object) -> None:
            del args

        def drawText(self, *args: object) -> None:
            del args

        def drawPolygon(self, *args: object) -> None:
            del args

        def end(self) -> None:
            return None

    class QToolTip:
        """无 Qt 环境时的气泡提示占位对象。"""

        @staticmethod
        def showText(position: QPoint, text: str, widget: QWidget | None = None) -> None:
            del position, text, widget

        @staticmethod
        def hideText() -> None:
            return None

    class Qt:
        """无 Qt 环境时的 Qt 常量占位对象。"""

        NoPen = 0
        LeftButton = 1
        PointingHandCursor = 0
        ArrowCursor = 0
        AlignCenter = 0
        AlignLeft = 0
        AlignRight = 0
        AlignVCenter = 0
        AlignTop = 0
        AlignBottom = 0
        RoundCap = 0
        SolidLine = 0
        DashLine = 0

        class PenStyle:
            NoPen = 0
            SolidLine = 0
            DashLine = 0

        class CapStyle:
            RoundCap = 0

        class AlignmentFlag:
            AlignCenter = 0
            AlignLeft = 0
            AlignRight = 0
            AlignVCenter = 0
            AlignTop = 0
            AlignBottom = 0

        class CursorShape:
            PointingHandCursor = 0
            ArrowCursor = 0

        class MouseButton:
            LeftButton = 1


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用可能不存在的 Qt 方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _coerce_mode(value: object) -> ThemeMode:
    """将运行时主题值归一化为 ThemeMode。"""

    if isinstance(value, ThemeMode):
        return value
    if isinstance(value, str) and value.lower() == ThemeMode.DARK.value:
        return ThemeMode.DARK
    return ThemeMode.LIGHT


def _theme_mode() -> ThemeMode:
    """尽量从应用实例中读取当前主题模式。"""

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


def _px(name: str) -> int:
    """将 px token 转换为整数。"""

    return int(STATIC_TOKENS[name].replace("px", ""))


def _qt_flag(group_name: str, name: str, default: int = 0) -> object:
    """兼容 Qt6 枚举与兼容层常量。"""

    group = getattr(Qt, group_name, None)
    if group is not None:
        value = getattr(group, name, None)
        if value is not None:
            return value
    direct = getattr(Qt, name, None)
    return direct if direct is not None else default


def _font_family_name(raw_token: str) -> str:
    """从字体 token 中抽取首个字体名。"""

    return raw_token.split(",")[0].strip().strip('"')


def _make_color(value: str | QColor) -> QColor:
    """将 token 文本或已有颜色统一转为 QColor。"""

    if isinstance(value, QColor):
        if hasattr(value, "red") and hasattr(value, "green") and hasattr(value, "blue") and hasattr(value, "alpha"):
            return QColor(value.red(), value.green(), value.blue(), value.alpha())
        return QColor(value)
    return QColor(value)


def _alpha_color(color: QColor, alpha: float) -> QColor:
    """复制颜色并写入透明度。"""

    copied = _make_color(color)
    setter = getattr(copied, "setAlphaF", None)
    if callable(setter):
        setter(max(0.0, min(1.0, alpha)))
    return copied


def _mix_colors(left: QColor, right: QColor, ratio: float) -> QColor:
    """按照比例混合两种颜色。"""

    amount = max(0.0, min(1.0, ratio))
    left_color = _make_color(left)
    right_color = _make_color(right)
    return QColor(
        int(round(left_color.red() + (right_color.red() - left_color.red()) * amount)),
        int(round(left_color.green() + (right_color.green() - left_color.green()) * amount)),
        int(round(left_color.blue() + (right_color.blue() - left_color.blue()) * amount)),
        int(round(left_color.alpha() + (right_color.alpha() - left_color.alpha()) * amount)),
    )


def _font(pixel_size: int, weight_token: str = "font.weight.medium") -> QFont:
    """构建统一字体对象。"""

    font = QFont(_font_family_name(STATIC_TOKENS["font.family.chinese"]))
    _call(font, "setPixelSize", pixel_size)
    _call(font, "setWeight", int(STATIC_TOKENS[weight_token]))
    _call(font, "setBold", weight_token == "font.weight.bold")
    return font


def _set_antialiasing(painter: QPainter) -> None:
    """统一开启抗锯齿。"""

    render_hint = getattr(QPainter, "Antialiasing", None)
    if render_hint is None:
        render_hint = getattr(getattr(QPainter, "RenderHint", None), "Antialiasing", None)
    if render_hint is not None:
        painter.setRenderHint(render_hint, True)


def _widget_rect(widget: QWidget) -> QRectF:
    """读取当前部件矩形。"""

    rect = _call(widget, "rect")
    if isinstance(rect, QRectF):
        return QRectF(rect)
    if rect is not None:
        x_reader = getattr(rect, "x", None)
        y_reader = getattr(rect, "y", None)
        w_reader = getattr(rect, "width", None)
        h_reader = getattr(rect, "height", None)
        if callable(x_reader) and callable(y_reader) and callable(w_reader) and callable(h_reader):
            return QRectF(float(x_reader()), float(y_reader()), float(w_reader()), float(h_reader()))
    width_reader = getattr(widget, "width", None)
    height_reader = getattr(widget, "height", None)
    width = int(width_reader()) if callable(width_reader) else 0
    height = int(height_reader()) if callable(height_reader) else 0
    return QRectF(0.0, 0.0, float(width), float(height))


def _event_point(event: QMouseEvent) -> QPointF:
    """兼容 Qt5/Qt6 鼠标事件坐标读取。"""

    position_reader = getattr(event, "position", None)
    if callable(position_reader):
        point = position_reader()
        if isinstance(point, QPointF):
            return point
    pos_reader = getattr(event, "pos", None)
    if callable(pos_reader):
        point = pos_reader()
        return QPointF(float(point.x()), float(point.y()))
    return QPointF()


def _global_point(event: QMouseEvent) -> QPoint:
    """读取用于 tooltip 的全局坐标。"""

    global_position_reader = getattr(event, "globalPosition", None)
    if callable(global_position_reader):
        point = global_position_reader()
        to_point = getattr(point, "toPoint", None)
        if callable(to_point):
            converted = to_point()
            if isinstance(converted, QPoint):
                return converted
            x_reader = getattr(converted, "x", None)
            y_reader = getattr(converted, "y", None)
            if callable(x_reader) and callable(y_reader):
                return QPoint(int(x_reader()), int(y_reader()))
    global_pos_reader = getattr(event, "globalPos", None)
    if callable(global_pos_reader):
        result = global_pos_reader()
        if isinstance(result, QPoint):
            return result
    point = _event_point(event)
    return point.toPoint() if hasattr(point, "toPoint") else QPoint(int(point.x()), int(point.y()))


def _show_tooltip(widget: QWidget, event: QMouseEvent, text: str) -> None:
    """显示提示气泡。"""

    _call(widget, "setToolTip", text)
    show_text = getattr(QToolTip, "showText", None)
    if callable(show_text):
        show_text(_global_point(event), text, widget)


def _hide_tooltip(widget: QWidget) -> None:
    """隐藏提示气泡。"""

    _call(widget, "setToolTip", "")
    hide_text = getattr(QToolTip, "hideText", None)
    if callable(hide_text):
        hide_text()


def _format_number(value: float) -> str:
    """以中文运营场景常见格式展示数值。"""

    absolute = abs(value)
    if absolute >= 100000000:
        return f"{value / 100000000:.1f}亿"
    if absolute >= 10000:
        return f"{value / 10000:.1f}万"
    return f"{value:,.0f}"


def _format_percent(ratio: float) -> str:
    """格式化百分比。"""

    return f"{max(0.0, ratio) * 100:.1f}%"


def _safe_ratio(value: float, baseline: float) -> float:
    """避免除零的比率计算。"""

    if baseline <= 0:
        return 0.0
    return value / baseline


SPACING_XS = _px("spacing.xs")
SPACING_SM = _px("spacing.sm")
SPACING_MD = _px("spacing.md")
SPACING_LG = _px("spacing.lg")
SPACING_XL = _px("spacing.xl")
SPACING_2XL = _px("spacing.2xl")
SPACING_3XL = _px("spacing.3xl")
PANEL_PADDING = _px("layout.card_padding")
PANEL_RADIUS = _px("card.radius")
RADIUS_SM = _px("radius.sm")
RADIUS_MD = _px("radius.md")
FONT_XS = _px("font.size.xs")
FONT_SM = _px("font.size.sm")
FONT_MD = _px("font.size.md")
FONT_LG = _px("font.size.lg")
FONT_XL = _px("font.size.xl")

DAY_LABELS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
FUNNEL_STAGE_LABELS = ("曝光", "点击", "加购", "下单", "付款")


@dataclass(frozen=True)
class WordCloudEntry:
    """词云中的单个词条。"""

    text: str
    weight: float


@dataclass(frozen=True)
class FunnelStage:
    """漏斗图中的阶段数据。"""

    label: str
    value: float


@dataclass(frozen=True)
class DistributionItem:
    """分布图中的单行条目。"""

    label: str
    value: float


@dataclass(frozen=True)
class _Palette:
    """分析组件使用的局部色板。"""

    surface: QColor
    surface_alt: QColor
    text: QColor
    text_muted: QColor
    border: QColor
    brand: QColor
    brand_secondary: QColor
    success: QColor
    warning: QColor
    danger: QColor
    series: tuple[QColor, ...]


@dataclass(frozen=True)
class _HeatmapRegion:
    """热力图单元格命中区域。"""

    day_index: int
    hour: int
    value: float
    rect: QRectF


@dataclass(frozen=True)
class _WordPlacement:
    """词云词条布局结果。"""

    text: str
    weight: float
    rect: QRectF
    text_rect: QRectF
    font_size: int
    color: QColor


def _palette(mode: ThemeMode | None = None) -> _Palette:
    """根据当前主题解析分析组件色板。"""

    resolved = mode or _theme_mode()
    series = tuple(_make_color(STATIC_TOKENS[f"chart.series[{index}]"]) for index in range(8))
    return _Palette(
        surface=_make_color(_token("surface.secondary", resolved)),
        surface_alt=_make_color(_token("surface.sunken", resolved)),
        text=_make_color(_token("text.primary", resolved)),
        text_muted=_make_color(_token("text.secondary", resolved)),
        border=_make_color(_token("border.default", resolved)),
        brand=_make_color(_token("brand.primary", resolved)),
        brand_secondary=_make_color(_token("brand.secondary", resolved)),
        success=_make_color(_token("status.success", resolved)),
        warning=_make_color(_token("status.warning", resolved)),
        danger=_make_color(_token("status.error", resolved)),
        series=series,
    )


def _default_heatmap_values() -> list[list[float]]:
    """生成默认的周内活跃热度矩阵。"""

    values: list[list[float]] = []
    for day_index in range(7):
        row: list[float] = []
        weekend_boost = 1.18 if day_index >= 5 else 1.0
        weekday_bias = 0.92 + day_index * 0.03
        for hour in range(24):
            morning = max(0.0, 1.0 - abs(hour - 10) / 5.5)
            evening = max(0.0, 1.0 - abs(hour - 20) / 4.5)
            noon = max(0.0, 1.0 - abs(hour - 13) / 6.5) * 0.45
            value = (morning * 58 + noon * 24 + evening * 88 + 8) * weekend_boost * weekday_bias
            row.append(round(value, 2))
        values.append(row)
    return values


def _default_word_entries() -> list[WordCloudEntry]:
    """生成默认的分析词云词条。"""

    return [
        WordCloudEntry("高互动", 98),
        WordCloudEntry("转化增长", 86),
        WordCloudEntry("短视频爆发", 80),
        WordCloudEntry("复购提升", 74),
        WordCloudEntry("粉丝活跃", 71),
        WordCloudEntry("达人联动", 68),
        WordCloudEntry("点击率", 66),
        WordCloudEntry("短视频种草", 63),
        WordCloudEntry("停留时长", 58),
        WordCloudEntry("加购峰值", 56),
        WordCloudEntry("高净值用户", 49),
        WordCloudEntry("品牌心智", 45),
        WordCloudEntry("评论热词", 41),
        WordCloudEntry("老客复访", 38),
    ]


def _default_funnel_stages() -> list[FunnelStage]:
    """生成默认的漏斗阶段数据。"""

    values = (126000, 48200, 19300, 8200, 5100)
    return [FunnelStage(label, float(value)) for label, value in zip(FUNNEL_STAGE_LABELS, values)]


def _default_distribution_items() -> list[DistributionItem]:
    """生成默认的分布图数据。"""

    return [
        DistributionItem("18-24岁", 28),
        DistributionItem("25-30岁", 34),
        DistributionItem("31-35岁", 22),
        DistributionItem("36-40岁", 11),
        DistributionItem("40岁以上", 5),
    ]


class _AnalyticsWidgetBase(QWidget):
    """分析组件公共基类，统一背景、边框与尺寸提示。"""

    def __init__(self, object_name: str, parent: QWidget | None = None, *, min_height: int = 260) -> None:
        super().__init__(parent)
        self._palette = _palette()
        self._min_height = min_height
        _call(self, "setObjectName", object_name)
        _call(self, "setMinimumHeight", min_height)
        _call(self, "setMouseTracking", True)

    def sizeHint(self) -> QSize:
        """返回推荐尺寸。"""

        return QSize(460, self._min_height)

    def minimumSizeHint(self) -> QSize:
        """返回最小推荐尺寸。"""

        return QSize(320, max(self._min_height - PANEL_PADDING, 200))

    def _begin_paint(self) -> tuple[QPainter, QRectF, QRectF]:
        """创建 painter 并绘制基础面板。"""

        painter = QPainter(self)
        _set_antialiasing(painter)
        outer_rect = _widget_rect(self).adjusted(float(SPACING_SM), float(SPACING_SM), float(-SPACING_SM), float(-SPACING_SM))
        painter.setPen(QPen(_alpha_color(self._palette.border, 0.95), 1.0))
        painter.setBrush(self._palette.surface)
        painter.drawRoundedRect(outer_rect, PANEL_RADIUS, PANEL_RADIUS)
        content_rect = outer_rect.adjusted(float(PANEL_PADDING), float(PANEL_PADDING), float(-PANEL_PADDING), float(-PANEL_PADDING))
        return painter, outer_rect, content_rect

    def _draw_empty_state(self, painter: QPainter, rect: QRectF, text: str = "暂无数据") -> None:
        """绘制通用空状态。"""

        painter.setPen(self._palette.text_muted)
        painter.setFont(_font(FONT_MD, "font.weight.medium"))
        painter.drawText(rect, int(_qt_flag("AlignmentFlag", "AlignCenter", 0)), text)


class HeatmapWidget(_AnalyticsWidgetBase):
    """用于展示周内 7×24 活跃热区的自绘热力图。"""

    def __init__(self, parent: QWidget | None = None, values: Sequence[Sequence[float]] | None = None) -> None:
        super().__init__("heatmapWidget", parent, min_height=320)
        self._values: list[list[float]] = []
        self._regions: list[_HeatmapRegion] = []
        self._hovered: tuple[int, int] | None = None
        self.set_values(values or _default_heatmap_values())

    def set_values(self, values: Sequence[Sequence[float]]) -> None:
        """设置热力图矩阵数据，超出或不足部分会自动裁剪补零。"""

        normalized: list[list[float]] = []
        for day_index in range(7):
            source_row = values[day_index] if day_index < len(values) else ()
            normalized.append([float(source_row[hour]) if hour < len(source_row) else 0.0 for hour in range(24)])
        self._values = normalized
        self._regions = []
        _call(self, "update")

    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制热力图网格、轴标签与强度图例。"""

        del event
        painter, _outer_rect, content = self._begin_paint()
        if not self._values:
            self._draw_empty_state(painter, content, "暂无热力数据")
            painter.end()
            return

        day_font = _font(FONT_SM, "font.weight.semibold")
        day_metrics = QFontMetrics(day_font)
        label_width = max(day_metrics.horizontalAdvance(day) for day in DAY_LABELS) + SPACING_XL
        hour_axis_height = FONT_SM + SPACING_XL
        legend_height = FONT_SM + SPACING_2XL
        grid_rect = QRectF(
            content.left() + label_width,
            content.top() + hour_axis_height,
            content.width() - label_width,
            content.height() - hour_axis_height - legend_height,
        )

        cell_gap = float(SPACING_XS)
        cell_width = max((grid_rect.width() - cell_gap * 23.0) / 24.0, 1.0)
        cell_height = max((grid_rect.height() - cell_gap * 6.0) / 7.0, 1.0)
        max_value = max(max(row) for row in self._values) if self._values else 0.0

        painter.setFont(day_font)
        painter.setPen(self._palette.text_muted)

        for hour in range(24):
            if hour % 4 != 0 and hour != 23:
                continue
            x = grid_rect.left() + hour * (cell_width + cell_gap)
            label_rect = QRectF(x, content.top(), cell_width, float(hour_axis_height - SPACING_XS))
            painter.drawText(label_rect, int(_qt_flag("AlignmentFlag", "AlignCenter", 0)), f"{hour:02d}")

        self._regions = []
        for day_index, day in enumerate(DAY_LABELS):
            y = grid_rect.top() + day_index * (cell_height + cell_gap)
            label_rect = QRectF(content.left(), y, float(label_width - SPACING_SM), cell_height)
            painter.drawText(
                label_rect,
                int(_qt_flag("AlignmentFlag", "AlignRight", 0)) | int(_qt_flag("AlignmentFlag", "AlignVCenter", 0)),
                day,
            )

            for hour, value in enumerate(self._values[day_index]):
                x = grid_rect.left() + hour * (cell_width + cell_gap)
                cell_rect = QRectF(x, y, cell_width, cell_height)
                painter.setPen(QPen(_alpha_color(self._palette.border, 0.42), 1.0))
                painter.setBrush(self._palette.surface_alt)
                painter.drawRoundedRect(cell_rect, RADIUS_SM, RADIUS_SM)

                intensity = _safe_ratio(value, max_value)
                if intensity > 0:
                    painter.setPen(int(_qt_flag("PenStyle", "NoPen", 0)))
                    overlay_color = _alpha_color(self._palette.series[0], 0.16 + intensity * 0.78)
                    painter.setBrush(overlay_color)
                    painter.drawRoundedRect(cell_rect, RADIUS_SM, RADIUS_SM)

                self._regions.append(_HeatmapRegion(day_index, hour, value, cell_rect))

        legend_steps = 5
        swatch_width = float(SPACING_2XL)
        legend_y = content.bottom() - FONT_SM - SPACING_MD
        legend_right = content.right()
        legend_total_width = swatch_width * legend_steps + SPACING_SM * (legend_steps - 1) + FONT_SM * 4
        start_x = legend_right - legend_total_width

        painter.setFont(_font(FONT_XS, "font.weight.medium"))
        painter.setPen(self._palette.text_muted)
        painter.drawText(QRectF(start_x, legend_y - SPACING_XS, 28.0, 18.0), int(_qt_flag("AlignmentFlag", "AlignLeft", 0)), "低")
        for step in range(legend_steps):
            ratio = step / max(legend_steps - 1, 1)
            swatch_x = start_x + 22.0 + step * (swatch_width + SPACING_SM)
            swatch_rect = QRectF(swatch_x, legend_y, swatch_width, float(SPACING_MD + FONT_XS))
            painter.setPen(QPen(_alpha_color(self._palette.border, 0.42), 1.0))
            painter.setBrush(_alpha_color(self._palette.series[0], 0.16 + ratio * 0.78))
            painter.drawRoundedRect(swatch_rect, RADIUS_SM, RADIUS_SM)
        painter.setPen(self._palette.text_muted)
        painter.drawText(
            QRectF(start_x + 22.0 + legend_steps * (swatch_width + SPACING_SM), legend_y - SPACING_XS, 24.0, 18.0),
            int(_qt_flag("AlignmentFlag", "AlignLeft", 0)),
            "高",
        )
        painter.end()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """根据当前悬停单元格更新 tooltip。"""

        point = _event_point(event)
        matched = next((region for region in self._regions if region.rect.contains(point)), None)
        if matched is None:
            self._hovered = None
            _hide_tooltip(self)
            return
        current_key = (matched.day_index, matched.hour)
        if current_key != self._hovered:
            self._hovered = current_key
            _show_tooltip(self, event, f"{DAY_LABELS[matched.day_index]} {matched.hour:02d}:00 · 活跃度 {matched.value:.0f}")

    def leaveEvent(self, event: object) -> None:
        """鼠标离开时清理 tooltip。"""

        del event
        self._hovered = None
        _hide_tooltip(self)


class WordCloudWidget(_AnalyticsWidgetBase):
    """使用 QPainter 绘制权重词云并支持词条点击。"""

    word_clicked = Signal(str)

    def __init__(self, parent: QWidget | None = None, words: Sequence[WordCloudEntry | tuple[str, float]] | None = None) -> None:
        super().__init__("wordCloudWidget", parent, min_height=320)
        self._entries: list[WordCloudEntry] = []
        self._placements: list[_WordPlacement] = []
        self._layout_dirty = True
        self._hovered_word: str | None = None
        self.set_words(words or _default_word_entries())

    def set_words(self, words: Sequence[WordCloudEntry | tuple[str, float]]) -> None:
        """设置词云词条与权重。"""

        normalized: list[WordCloudEntry] = []
        for item in words:
            if isinstance(item, WordCloudEntry):
                normalized.append(item)
            else:
                normalized.append(WordCloudEntry(str(item[0]), float(item[1])))
        self._entries = [entry for entry in normalized if entry.text.strip()]
        self._placements = []
        self._layout_dirty = True
        _call(self, "update")

    def resizeEvent(self, event: object) -> None:
        """尺寸变化时重新生成词条布局。"""

        del event
        self._layout_dirty = True

    def _layout_rect(self) -> QRectF:
        """返回词云绘制区域。"""

        rect = _widget_rect(self).adjusted(float(SPACING_SM + PANEL_PADDING), float(SPACING_SM + PANEL_PADDING), float(-(SPACING_SM + PANEL_PADDING)), float(-(SPACING_SM + PANEL_PADDING)))
        return rect

    def _rebuild_layout(self) -> None:
        """按当前尺寸重新布局词条。"""

        self._placements = []
        content = self._layout_rect()
        if content.width() <= 0 or content.height() <= 0 or not self._entries:
            self._layout_dirty = False
            return

        max_weight = max(entry.weight for entry in self._entries)
        min_weight = min(entry.weight for entry in self._entries)
        sorted_entries = sorted(self._entries, key=lambda entry: entry.weight, reverse=True)
        center = content.center()
        random_seed = sum(sum(ord(character) for character in entry.text) for entry in sorted_entries)
        randomizer = Random(random_seed)

        font_min = FONT_MD + SPACING_LG
        font_max = FONT_XL + SPACING_3XL
        placed_rects: list[QRectF] = []

        for index, entry in enumerate(sorted_entries):
            ratio = 1.0 if max_weight == min_weight else (entry.weight - min_weight) / (max_weight - min_weight)
            font_size = int(round(font_min + (font_max - font_min) * ratio))
            font = _font(font_size, "font.weight.bold" if ratio >= 0.7 else "font.weight.semibold")
            metrics = QFontMetrics(font)
            text_width = float(max(metrics.horizontalAdvance(entry.text), font_size))
            text_height = float(max(metrics.height(), font_size))
            padding = float(SPACING_SM)
            placed_rect: QRectF | None = None
            text_rect: QRectF | None = None
            angle_offset = randomizer.random() * 2.0 * pi

            for attempt in range(180):
                progress = attempt / 179.0 if attempt else 0.0
                angle = angle_offset + attempt * 0.58
                radius_x = content.width() * (0.04 + progress * 0.44)
                radius_y = content.height() * (0.02 + progress * 0.35)
                center_x = center.x() + cos(angle) * radius_x
                center_y = center.y() + sin(angle) * radius_y
                candidate_text = QRectF(center_x - text_width / 2.0, center_y - text_height / 2.0, text_width, text_height)
                candidate_rect = candidate_text.adjusted(-padding, -padding, padding, padding)
                within_bounds = (
                    candidate_rect.left() >= content.left()
                    and candidate_rect.right() <= content.right()
                    and candidate_rect.top() >= content.top()
                    and candidate_rect.bottom() <= content.bottom()
                )
                if not within_bounds:
                    continue
                if any(candidate_rect.intersects(existing) for existing in placed_rects):
                    continue
                placed_rect = candidate_rect
                text_rect = candidate_text
                break

            if placed_rect is None or text_rect is None:
                row_height = float(font_max + SPACING_XL)
                fallback_row = index % max(int(max(content.height(), row_height) // max(row_height, 1.0)), 1)
                fallback_y = content.top() + fallback_row * row_height
                text_rect = QRectF(content.left() + SPACING_MD, fallback_y, min(text_width, content.width() - SPACING_2XL), text_height)
                placed_rect = text_rect.adjusted(-padding, -padding, padding, padding)

            color = self._palette.series[index % len(self._palette.series)]
            placed_rects.append(placed_rect)
            self._placements.append(_WordPlacement(entry.text, entry.weight, placed_rect, text_rect, font_size, color))

        self._layout_dirty = False

    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制词云文本。"""

        del event
        if self._layout_dirty:
            self._rebuild_layout()
        painter, _outer_rect, content = self._begin_paint()
        if not self._entries:
            self._draw_empty_state(painter, content, "暂无词云数据")
            painter.end()
            return

        for placement in self._placements:
            is_hovered = placement.text == self._hovered_word
            if is_hovered:
                painter.setPen(int(_qt_flag("PenStyle", "NoPen", 0)))
                painter.setBrush(_alpha_color(placement.color, 0.14))
                painter.drawRoundedRect(placement.rect, RADIUS_MD, RADIUS_MD)
            painter.setFont(_font(placement.font_size, "font.weight.bold" if placement.font_size >= FONT_XL + SPACING_XL else "font.weight.semibold"))
            painter.setPen(_make_color(_mix_colors(placement.color, self._palette.text, 0.14 if is_hovered else 0.05)))
            painter.drawText(placement.text_rect, int(_qt_flag("AlignmentFlag", "AlignCenter", 0)), placement.text)
        painter.end()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """处理词条悬停状态。"""

        point = _event_point(event)
        matched = next((placement for placement in self._placements if placement.rect.contains(point)), None)
        hovered_word = matched.text if matched is not None else None
        if hovered_word != self._hovered_word:
            self._hovered_word = hovered_word
            if matched is not None:
                _call(self, "setCursor", _qt_flag("CursorShape", "PointingHandCursor", 0))
                _show_tooltip(self, event, f"{matched.text} · 权重 {matched.weight:.0f}")
            else:
                _call(self, "setCursor", _qt_flag("CursorShape", "ArrowCursor", 0))
                _hide_tooltip(self)
            _call(self, "update")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """点击词条时发出选中信号。"""

        if int(getattr(event, "button", lambda: 0)()) != int(_qt_flag("MouseButton", "LeftButton", 1)):
            return
        point = _event_point(event)
        matched = next((placement for placement in self._placements if placement.rect.contains(point)), None)
        if matched is not None:
            self.word_clicked.emit(matched.text)

    def leaveEvent(self, event: object) -> None:
        """鼠标移出时清空高亮。"""

        del event
        self._hovered_word = None
        _call(self, "setCursor", _qt_flag("CursorShape", "ArrowCursor", 0))
        _hide_tooltip(self)
        _call(self, "update")


class SentimentGauge(_AnalyticsWidgetBase):
    """使用半圆仪表盘展示情绪倾向。"""

    def __init__(self, parent: QWidget | None = None, sentiment: float = 0.18) -> None:
        super().__init__("sentimentGauge", parent, min_height=300)
        self._sentiment = 0.0
        self.set_sentiment(sentiment)

    def sentiment(self) -> float:
        """返回当前情绪值。"""

        return self._sentiment

    def set_sentiment(self, value: float) -> None:
        """设置情绪值，范围为 -1.0 到 +1.0。"""

        self._sentiment = max(-1.0, min(1.0, float(value)))
        _call(self, "update")

    def _sentiment_meta(self) -> tuple[str, QColor]:
        """返回当前情绪标签与对应颜色。"""

        if self._sentiment <= -0.2:
            return "负面", self._palette.danger
        if self._sentiment >= 0.2:
            return "正面", self._palette.success
        return "中性", self._palette.warning

    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制半圆情绪仪表盘、渐变弧线与指针。"""

        del event
        painter, _outer_rect, content = self._begin_paint()
        diameter = min(content.width(), content.height() * 1.36)
        radius = diameter / 2.0
        center_x = content.center().x()
        center_y = content.bottom() - SPACING_XL
        arc_rect = QRectF(center_x - radius, center_y - radius, diameter, diameter)
        arc_thickness = max(float(SPACING_XL), radius * 0.12)

        background_pen = QPen(_alpha_color(self._palette.surface_alt, 1.0), arc_thickness)
        _call(background_pen, "setCapStyle", _qt_flag("CapStyle", "RoundCap", 0))
        painter.setPen(background_pen)
        painter.drawArc(arc_rect, 180 * 16, -180 * 16)

        segment_count = 60
        for segment in range(segment_count):
            start_ratio = segment / segment_count
            end_ratio = (segment + 1) / segment_count
            color_ratio = (start_ratio + end_ratio) / 2.0
            color = (
                _mix_colors(self._palette.danger, self._palette.warning, color_ratio * 2.0)
                if color_ratio <= 0.5
                else _mix_colors(self._palette.warning, self._palette.success, (color_ratio - 0.5) * 2.0)
            )
            segment_pen = QPen(color, arc_thickness)
            _call(segment_pen, "setCapStyle", _qt_flag("CapStyle", "RoundCap", 0))
            painter.setPen(segment_pen)
            start_degree = 180.0 - start_ratio * 180.0
            span_degree = -(end_ratio - start_ratio) * 180.0
            painter.drawArc(arc_rect, int(round(start_degree * 16.0)), int(round(span_degree * 16.0)))

        left_label_rect = QRectF(arc_rect.left() - SPACING_SM, center_y + SPACING_SM, 60.0, 22.0)
        center_label_rect = QRectF(center_x - 30.0, arc_rect.top() + radius - SPACING_MD, 60.0, 22.0)
        right_label_rect = QRectF(arc_rect.right() - 52.0, center_y + SPACING_SM, 60.0, 22.0)
        painter.setFont(_font(FONT_XS, "font.weight.medium"))
        painter.setPen(self._palette.text_muted)
        painter.drawText(left_label_rect, int(_qt_flag("AlignmentFlag", "AlignLeft", 0)), "-1.0")
        painter.drawText(center_label_rect, int(_qt_flag("AlignmentFlag", "AlignCenter", 0)), "0.0")
        painter.drawText(right_label_rect, int(_qt_flag("AlignmentFlag", "AlignRight", 0)), "+1.0")

        angle = pi - ((self._sentiment + 1.0) / 2.0) * pi
        needle_length = radius - arc_thickness * 1.35
        tip = QPointF(center_x + cos(angle) * needle_length, center_y - sin(angle) * needle_length)
        needle_pen = QPen(self._palette.brand_secondary, max(2.0, arc_thickness * 0.12))
        _call(needle_pen, "setCapStyle", _qt_flag("CapStyle", "RoundCap", 0))
        painter.setPen(needle_pen)
        painter.drawLine(QPointF(center_x, center_y), tip)
        painter.setPen(int(_qt_flag("PenStyle", "NoPen", 0)))
        painter.setBrush(self._palette.brand_secondary)
        painter.drawEllipse(QRectF(center_x - 7.0, center_y - 7.0, 14.0, 14.0))
        painter.setBrush(_alpha_color(self._palette.brand, 0.18))
        painter.drawEllipse(QRectF(tip.x() - 6.0, tip.y() - 6.0, 12.0, 12.0))

        sentiment_label, sentiment_color = self._sentiment_meta()
        center_rect = QRectF(center_x - radius * 0.62, center_y - radius * 0.30, radius * 1.24, radius * 0.58)
        painter.setFont(_font(FONT_XL, "font.weight.bold"))
        painter.setPen(sentiment_color)
        painter.drawText(center_rect.adjusted(0.0, -SPACING_SM, 0.0, 0.0), int(_qt_flag("AlignmentFlag", "AlignCenter", 0)), sentiment_label)
        painter.setFont(_font(FONT_MD, "font.weight.medium"))
        painter.setPen(self._palette.text)
        painter.drawText(
            center_rect.adjusted(0.0, FONT_XL + SPACING_MD, 0.0, 0.0),
            int(_qt_flag("AlignmentFlag", "AlignCenter", 0)),
            f"情绪值 {self._sentiment:+.2f}",
        )
        painter.end()


class FunnelChart(_AnalyticsWidgetBase):
    """展示曝光到付款转化过程的漏斗图。"""

    def __init__(self, parent: QWidget | None = None, stages: Sequence[FunnelStage | tuple[str, float] | float] | None = None) -> None:
        super().__init__("funnelChart", parent, min_height=320)
        self._stages: list[FunnelStage] = []
        self.set_stages(stages or _default_funnel_stages())

    def set_stages(self, stages: Sequence[FunnelStage | tuple[str, float] | float]) -> None:
        """设置漏斗阶段数据。"""

        normalized: list[FunnelStage] = []
        for index, item in enumerate(stages[: len(FUNNEL_STAGE_LABELS)]):
            if isinstance(item, FunnelStage):
                normalized.append(item)
            elif isinstance(item, tuple):
                normalized.append(FunnelStage(str(item[0]), float(item[1])))
            else:
                normalized.append(FunnelStage(FUNNEL_STAGE_LABELS[index], float(item)))
        if not normalized:
            normalized = _default_funnel_stages()
        self._stages = normalized
        _call(self, "update")

    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制梯形漏斗、阶段值与转化率。"""

        del event
        painter, _outer_rect, content = self._begin_paint()
        if not self._stages:
            self._draw_empty_state(painter, content, "暂无漏斗数据")
            painter.end()
            return

        stage_count = len(self._stages)
        row_gap = float(SPACING_MD)
        right_info_width = max(content.width() * 0.24, 78.0)
        funnel_width = content.width() - right_info_width - SPACING_XL
        stage_height = max((content.height() - row_gap * (stage_count - 1)) / stage_count, 28.0)
        max_value = max(stage.value for stage in self._stages) if self._stages else 1.0
        min_width = funnel_width * 0.26
        center_x = content.left() + funnel_width / 2.0

        for index, stage in enumerate(self._stages):
            top_ratio = _safe_ratio(stage.value, max_value)
            bottom_value = self._stages[index + 1].value if index + 1 < stage_count else stage.value * 0.74
            bottom_ratio = _safe_ratio(bottom_value, max_value)
            top_width = min_width + (funnel_width - min_width) * top_ratio
            bottom_width = min_width + (funnel_width - min_width) * bottom_ratio
            y = content.top() + index * (stage_height + row_gap)
            polygon = QPolygonF(
                [
                    QPointF(center_x - top_width / 2.0, y),
                    QPointF(center_x + top_width / 2.0, y),
                    QPointF(center_x + bottom_width / 2.0, y + stage_height),
                    QPointF(center_x - bottom_width / 2.0, y + stage_height),
                ]
            )
            fill_color = _alpha_color(self._palette.series[index % len(self._palette.series)], 0.22 + index * 0.10)
            border_color = self._palette.series[index % len(self._palette.series)]
            painter.setPen(QPen(border_color, 1.2))
            painter.setBrush(fill_color)
            painter.drawPolygon(polygon)

            label_rect = QRectF(center_x - top_width / 2.0 + SPACING_LG, y, max(top_width - SPACING_2XL, 10.0), stage_height)
            painter.setPen(self._palette.text)
            painter.setFont(_font(FONT_MD, "font.weight.semibold"))
            painter.drawText(
                label_rect.adjusted(0.0, -SPACING_XS, 0.0, 0.0),
                int(_qt_flag("AlignmentFlag", "AlignLeft", 0)) | int(_qt_flag("AlignmentFlag", "AlignVCenter", 0)),
                stage.label,
            )
            painter.setPen(self._palette.text_muted)
            painter.setFont(_font(FONT_SM, "font.weight.medium"))
            painter.drawText(
                label_rect.adjusted(0.0, FONT_SM + SPACING_SM, 0.0, 0.0),
                int(_qt_flag("AlignmentFlag", "AlignLeft", 0)) | int(_qt_flag("AlignmentFlag", "AlignVCenter", 0)),
                _format_number(stage.value),
            )

            info_rect = QRectF(content.left() + funnel_width + SPACING_XL, y, right_info_width, stage_height)
            if index == 0:
                conversion_text = "基准 100%"
            else:
                conversion_text = f"转化 {_format_percent(_safe_ratio(stage.value, self._stages[index - 1].value))}"
            painter.setPen(self._palette.text_muted)
            painter.setFont(_font(FONT_SM, "font.weight.semibold"))
            painter.drawText(info_rect, int(_qt_flag("AlignmentFlag", "AlignCenter", 0)), conversion_text)
        painter.end()


class TrendComparison(_AnalyticsWidgetBase):
    """用于对比两个周期走势的双折线图。"""

    def __init__(
        self,
        parent: QWidget | None = None,
        labels: Sequence[str] | None = None,
        current_values: Sequence[float] | None = None,
        compare_values: Sequence[float] | None = None,
        current_name: str = "本周期",
        compare_name: str = "对比周期",
    ) -> None:
        super().__init__("trendComparison", parent, min_height=320)
        self._labels: list[str] = list(labels or ("周一", "周二", "周三", "周四", "周五", "周六", "周日"))
        self._current_values: list[float] = list(current_values or (38, 46, 62, 58, 72, 91, 88))
        self._compare_values: list[float] = list(compare_values or (34, 41, 49, 53, 59, 67, 71))
        self._current_name = current_name
        self._compare_name = compare_name

    def set_series(
        self,
        labels: Sequence[str],
        current_values: Sequence[float],
        compare_values: Sequence[float],
        *,
        current_name: str | None = None,
        compare_name: str | None = None,
    ) -> None:
        """设置折线对比数据。"""

        point_count = min(len(labels), len(current_values), len(compare_values))
        self._labels = [str(labels[index]) for index in range(point_count)]
        self._current_values = [float(current_values[index]) for index in range(point_count)]
        self._compare_values = [float(compare_values[index]) for index in range(point_count)]
        if current_name is not None:
            self._current_name = current_name
        if compare_name is not None:
            self._compare_name = compare_name
        _call(self, "update")

    def _series_points(self, rect: QRectF, values: Sequence[float], minimum: float, maximum: float) -> list[QPointF]:
        """将数值序列映射到画布坐标。"""

        if not values:
            return []
        count = len(values)
        step_x = rect.width() / max(count - 1, 1)
        span = maximum - minimum if maximum != minimum else 1.0
        points: list[QPointF] = []
        for index, value in enumerate(values):
            x = rect.left() + step_x * index
            ratio = (value - minimum) / span
            y = rect.bottom() - ratio * rect.height()
            points.append(QPointF(x, y))
        return points

    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制对比网格、图例与两条趋势线。"""

        del event
        painter, _outer_rect, content = self._begin_paint()
        point_count = min(len(self._labels), len(self._current_values), len(self._compare_values))
        if point_count == 0:
            self._draw_empty_state(painter, content, "暂无趋势数据")
            painter.end()
            return

        y_label_width = 56.0
        legend_height = FONT_MD + SPACING_2XL
        x_axis_height = FONT_SM + SPACING_2XL
        chart_rect = QRectF(
            content.left() + y_label_width,
            content.top() + legend_height,
            content.width() - y_label_width,
            content.height() - legend_height - x_axis_height,
        )

        all_values = self._current_values[:point_count] + self._compare_values[:point_count]
        minimum = min(min(all_values), 0.0)
        maximum = max(all_values)
        if maximum <= minimum:
            maximum = minimum + 1.0

        grid_steps = 4
        painter.setFont(_font(FONT_XS, "font.weight.medium"))
        for step in range(grid_steps + 1):
            ratio = step / grid_steps
            y = chart_rect.bottom() - ratio * chart_rect.height()
            grid_pen = QPen(_alpha_color(self._palette.border, 0.55), 1.0)
            painter.setPen(grid_pen)
            painter.drawLine(QPointF(chart_rect.left(), y), QPointF(chart_rect.right(), y))
            value = minimum + (maximum - minimum) * ratio
            painter.setPen(self._palette.text_muted)
            painter.drawText(
                QRectF(content.left(), y - FONT_SM, y_label_width - SPACING_MD, FONT_SM * 2.0),
                int(_qt_flag("AlignmentFlag", "AlignRight", 0)) | int(_qt_flag("AlignmentFlag", "AlignVCenter", 0)),
                _format_number(value),
            )

        current_points = self._series_points(chart_rect, self._current_values[:point_count], minimum, maximum)
        compare_points = self._series_points(chart_rect, self._compare_values[:point_count], minimum, maximum)
        compare_color = self._palette.series[1]
        current_color = self._palette.series[0]

        legend_items = ((self._current_name, current_color), (self._compare_name, compare_color))
        legend_x = content.left()
        for name, color in legend_items:
            swatch_y = content.top() + FONT_SM / 2.0
            legend_pen = QPen(color, 2.6)
            _call(legend_pen, "setCapStyle", _qt_flag("CapStyle", "RoundCap", 0))
            painter.setPen(legend_pen)
            painter.drawLine(QPointF(legend_x, swatch_y), QPointF(legend_x + 22.0, swatch_y))
            painter.setPen(self._palette.text)
            painter.setFont(_font(FONT_SM, "font.weight.semibold"))
            painter.drawText(
                QRectF(legend_x + 28.0, content.top(), 86.0, 20.0),
                int(_qt_flag("AlignmentFlag", "AlignLeft", 0)) | int(_qt_flag("AlignmentFlag", "AlignVCenter", 0)),
                name,
            )
            legend_x += 116.0

        compare_pen = QPen(compare_color, 2.2)
        _call(compare_pen, "setCapStyle", _qt_flag("CapStyle", "RoundCap", 0))
        painter.setPen(compare_pen)
        for start, end in zip(compare_points, compare_points[1:]):
            painter.drawLine(start, end)

        current_pen = QPen(current_color, 3.0)
        _call(current_pen, "setCapStyle", _qt_flag("CapStyle", "RoundCap", 0))
        painter.setPen(current_pen)
        for start, end in zip(current_points, current_points[1:]):
            painter.drawLine(start, end)

        for point, color in [*(zip(compare_points, [compare_color] * len(compare_points))), *(zip(current_points, [current_color] * len(current_points)))]:
            painter.setPen(QPen(_alpha_color(color, 0.92), 1.0))
            painter.setBrush(_alpha_color(color, 0.26))
            painter.drawEllipse(QRectF(point.x() - 4.0, point.y() - 4.0, 8.0, 8.0))

        painter.setPen(self._palette.text_muted)
        painter.setFont(_font(FONT_XS, "font.weight.medium"))
        label_step = 1 if point_count <= 7 else max(point_count // 6, 1)
        for index, label in enumerate(self._labels[:point_count]):
            if index % label_step != 0 and index != point_count - 1:
                continue
            point = current_points[index]
            label_rect = QRectF(point.x() - 26.0, chart_rect.bottom() + SPACING_MD, 52.0, 18.0)
            painter.drawText(label_rect, int(_qt_flag("AlignmentFlag", "AlignCenter", 0)), label)
        painter.end()


class DistributionChart(_AnalyticsWidgetBase):
    """用于展示标签占比的水平条形分布图。"""

    def __init__(self, parent: QWidget | None = None, items: Sequence[DistributionItem | tuple[str, float]] | None = None) -> None:
        super().__init__("distributionChart", parent, min_height=300)
        self._items: list[DistributionItem] = []
        self.set_items(items or _default_distribution_items())

    def set_items(self, items: Sequence[DistributionItem | tuple[str, float]]) -> None:
        """设置分布图条目。"""

        normalized: list[DistributionItem] = []
        for item in items:
            if isinstance(item, DistributionItem):
                normalized.append(item)
            else:
                normalized.append(DistributionItem(str(item[0]), float(item[1])))
        self._items = normalized
        _call(self, "update")

    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制横向条形与百分比标签。"""

        del event
        painter, _outer_rect, content = self._begin_paint()
        if not self._items:
            self._draw_empty_state(painter, content, "暂无分布数据")
            painter.end()
            return

        total = sum(max(item.value, 0.0) for item in self._items)
        label_font = _font(FONT_SM, "font.weight.semibold")
        label_metrics = QFontMetrics(label_font)
        percent_font = _font(FONT_SM, "font.weight.medium")
        percent_metrics = QFontMetrics(percent_font)
        label_width = max(label_metrics.horizontalAdvance(item.label) for item in self._items) + SPACING_XL
        percent_width = percent_metrics.horizontalAdvance("100.0%") + SPACING_MD
        row_gap = float(SPACING_LG)
        bar_height = float(FONT_SM + SPACING_SM)
        row_height = bar_height + SPACING_SM
        bar_width = max(content.width() - label_width - percent_width - SPACING_2XL, 20.0)

        for index, item in enumerate(self._items):
            row_top = content.top() + index * (row_height + row_gap)
            label_rect = QRectF(content.left(), row_top, label_width, row_height)
            track_rect = QRectF(content.left() + label_width, row_top + SPACING_XS, bar_width, bar_height)
            percent_rect = QRectF(track_rect.right() + SPACING_LG, row_top, percent_width, row_height)
            ratio = _safe_ratio(item.value, total) if total > 0 else 0.0
            fill_rect = QRectF(track_rect.left(), track_rect.top(), track_rect.width() * ratio, track_rect.height())

            painter.setFont(label_font)
            painter.setPen(self._palette.text)
            painter.drawText(label_rect, int(_qt_flag("AlignmentFlag", "AlignLeft", 0)) | int(_qt_flag("AlignmentFlag", "AlignVCenter", 0)), item.label)

            painter.setPen(QPen(_alpha_color(self._palette.border, 0.48), 1.0))
            painter.setBrush(self._palette.surface_alt)
            painter.drawRoundedRect(track_rect, RADIUS_MD, RADIUS_MD)

            painter.setPen(int(_qt_flag("PenStyle", "NoPen", 0)))
            painter.setBrush(_alpha_color(self._palette.series[index % len(self._palette.series)], 0.84))
            painter.drawRoundedRect(fill_rect, RADIUS_MD, RADIUS_MD)

            painter.setFont(percent_font)
            painter.setPen(self._palette.text_muted)
            painter.drawText(percent_rect, int(_qt_flag("AlignmentFlag", "AlignRight", 0)) | int(_qt_flag("AlignmentFlag", "AlignVCenter", 0)), _format_percent(ratio))
        painter.end()


__all__ = [
    "DistributionChart",
    "DistributionItem",
    "FunnelChart",
    "FunnelStage",
    "HeatmapWidget",
    "SentimentGauge",
    "TrendComparison",
    "WordCloudEntry",
    "WordCloudWidget",
]
