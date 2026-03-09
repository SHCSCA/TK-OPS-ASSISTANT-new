# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false, reportOperatorIssue=false

from __future__ import annotations

"""主题化数据图表组件。"""

import math
from typing import Literal, Sequence

from .inputs import QSize, Qt, QWidget, _call, _palette, _static_token

try:
    from PySide6.QtCore import QPointF, QRectF
    from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen

    QT_CHARTS_AVAILABLE = True
except ImportError:
    from .inputs import QColor, QPainter

    QT_CHARTS_AVAILABLE = False

    class QPointF:
        """无 Qt 环境时的点对象。"""

        def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
            self.x = x
            self.y = y

    class QRectF:
        """无 Qt 环境时的矩形对象。"""

        def __init__(self, x: float, y: float, width: float, height: float) -> None:
            self._x = x
            self._y = y
            self._width = width
            self._height = height

        def left(self) -> float:
            return self._x

        def top(self) -> float:
            return self._y

        def width(self) -> float:
            return self._width

        def height(self) -> float:
            return self._height

        def right(self) -> float:
            return self._x + self._width

        def bottom(self) -> float:
            return self._y + self._height

    class QPen:
        """无 Qt 环境时的画笔对象。"""

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            return None

        def setWidth(self, _width: int) -> None:
            return None

    class QFont:
        """无 Qt 环境时的字体对象。"""

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            return None

    class QPainterPath:
        """无 Qt 环境时的路径对象。"""

        def __init__(self) -> None:
            self.points: list[QPointF] = []

        def moveTo(self, point: QPointF) -> None:
            self.points.append(point)

        def lineTo(self, point: QPointF) -> None:
            self.points.append(point)

ChartType = Literal["line", "bar", "pie"]


def _series_color(index: int) -> str:
    """读取图表序列色。"""

    palette = [
        "chart.series[0]",
        "chart.series[1]",
        "chart.series[2]",
        "chart.series[3]",
        "chart.series[4]",
        "chart.series[5]",
        "chart.series[6]",
        "chart.series[7]",
    ]
    return _static_token(palette[index % len(palette)])


def _rgba(hex_color: str, alpha: float) -> str:
    """十六进制转 rgba。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _qcolor(value: str, alpha: float | None = None) -> QColor:
    """创建兼容 Qt 的颜色对象。"""

    color = QColor(value)
    set_alpha = getattr(color, "setAlphaF", None)
    if callable(set_alpha) and alpha is not None and value.startswith("#"):
        set_alpha(alpha)
    return color


def _float_list(values: Sequence[float | int]) -> list[float]:
    """归一化数值序列。"""

    return [float(value) for value in values]


def _to_int(value: object, default: int = 0) -> int:
    """尽量将对象转换为整数。"""

    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return default
    return default


def _to_float(value: object, default: float = 0.0) -> float:
    """尽量将对象转换为浮点数。"""

    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def _widget_size(widget: QWidget) -> tuple[int, int]:
    """兼容读取部件尺寸。"""

    width_method = getattr(widget, "width", None)
    height_method = getattr(widget, "height", None)
    width = _to_int(width_method(), 0) if callable(width_method) else _to_int(getattr(widget, "_width", 0), 0)
    height = _to_int(height_method(), 0) if callable(height_method) else _to_int(getattr(widget, "_height", 0), 0)
    return max(width, 0), max(height, 0)


def _point_x(point: QPointF) -> float:
    """兼容读取 QPointF 的 x 坐标。"""

    reader = getattr(point, "x", None)
    value = reader() if callable(reader) else reader
    return _to_float(value, 0.0)


def _point_y(point: QPointF) -> float:
    """兼容读取 QPointF 的 y 坐标。"""

    reader = getattr(point, "y", None)
    value = reader() if callable(reader) else reader
    return _to_float(value, 0.0)


class MiniSparkline(QWidget):
    """紧凑型迷你趋势线，适合 KPI 卡片内联展示。"""

    def __init__(self, values: Sequence[float | int] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._values: list[float] = _float_list(values or [42, 44, 43, 47, 52, 58, 61])
        _call(self, "setObjectName", "miniSparkline")
        _call(self, "setFixedSize", 64, 24)
        _call(
            self,
            "setStyleSheet",
            f"QWidget#miniSparkline {{ background: transparent; border: none; min-width: 64px; min-height: 24px; }}",
        )

    def sizeHint(self) -> QSize:
        """返回建议尺寸。"""

        return QSize(64, 24)

    def set_values(self, values: Sequence[float | int]) -> None:
        """更新趋势数据。"""

        self._values = _float_list(values)
        _call(self, "update")

    def paintEvent(self, _event: object) -> None:
        """绘制迷你折线。"""

        if not self._values:
            return
        painter = QPainter(self)
        if hasattr(painter, "setRenderHint"):
            painter.setRenderHint(getattr(QPainter, "Antialiasing", 0), True)

        width, height = _widget_size(self)
        if width <= 0 or height <= 0:
            width, height = 64, 24
        color = _series_color(0)
        points = self._map_points(self._values, QRectF(2.0, 3.0, float(width - 4), float(height - 6)))
        if len(points) < 2 or not hasattr(painter, "drawPath"):
            return

        fill_path = QPainterPath()
        fill_path.moveTo(QPointF(_point_x(points[0]), float(height - 2)))
        for point in points:
            fill_path.lineTo(point)
        fill_path.lineTo(QPointF(_point_x(points[-1]), float(height - 2)))

        painter.setPen(getattr(Qt, "NoPen", 0))
        if hasattr(painter, "setBrush"):
            painter.setBrush(_qcolor(color, 0.18))
            if hasattr(painter, "drawPath"):
                painter.drawPath(fill_path)

        stroke = QPen(_qcolor(color))
        if hasattr(stroke, "setWidth"):
            stroke.setWidth(2)
        painter.setPen(stroke)
        line_path = QPainterPath()
        line_path.moveTo(points[0])
        for point in points[1:]:
            line_path.lineTo(point)
        if hasattr(painter, "drawPath"):
            painter.drawPath(line_path)

    @staticmethod
    def _map_points(values: Sequence[float], rect: QRectF) -> list[QPointF]:
        """将数据映射为绘制坐标。"""

        if not values:
            return []
        minimum = min(values)
        maximum = max(values)
        span = maximum - minimum or 1.0
        count = max(len(values) - 1, 1)
        points: list[QPointF] = []
        for index, value in enumerate(values):
            x = rect.left() + rect.width() * (index / count)
            y_ratio = (value - minimum) / span
            y = rect.bottom() - rect.height() * y_ratio
            points.append(QPointF(float(x), float(y)))
        return points


class ChartWidget(QWidget):
    """基于 QPainter 的主题图表，支持折线、柱状与饼图。"""

    def __init__(
        self,
        chart_type: ChartType = "line",
        *,
        title: str = "核心指标走势",
        labels: Sequence[str] | None = None,
        data: Sequence[float | int] | None = None,
        unit: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._chart_type: ChartType = chart_type
        self._title = title
        self._labels: list[str] = list(labels or ["周一", "周二", "周三", "周四", "周五", "周六", "周日"])
        self._data: list[float] = _float_list(data or [1.6, 1.9, 2.2, 2.0, 2.4, 2.8, 3.1])
        self._unit = unit
        _call(self, "setObjectName", "chartWidget")
        _call(self, "setMinimumHeight", 240)
        self._apply_styles()

    def set_chart_type(self, chart_type: ChartType) -> None:
        """切换图表类型。"""

        self._chart_type = chart_type
        _call(self, "update")

    def set_data(self, data: Sequence[float | int], labels: Sequence[str] | None = None) -> None:
        """更新图表数据。"""

        self._data = _float_list(data)
        if labels is not None:
            self._labels = list(labels)
        _call(self, "update")

    def set_unit(self, unit: str) -> None:
        """更新单位文案。"""

        self._unit = unit
        _call(self, "update")

    def paintEvent(self, _event: object) -> None:
        """按当前图表类型绘制。"""

        painter = QPainter(self)
        if hasattr(painter, "setRenderHint"):
            painter.setRenderHint(getattr(QPainter, "Antialiasing", 0), True)
        width, height = _widget_size(self)
        if width <= 0 or height <= 0:
            return

        colors = _palette()
        frame_rect = QRectF(0.5, 0.5, float(width - 1), float(height - 1))
        if hasattr(painter, "setBrush"):
            painter.setBrush(_qcolor(colors.surface_alt, 0.88))
        painter.setPen(QPen(_qcolor(colors.border)))
        if hasattr(painter, "drawRoundedRect"):
            painter.drawRoundedRect(frame_rect, 12.0, 12.0)

        self._draw_title(painter, width)
        if not self._data:
            self._draw_empty(painter, width, height)
            return

        if self._chart_type == "pie":
            self._draw_pie_chart(painter, width, height)
            return
        self._draw_xy_chart(painter, width, height)

    def _draw_title(self, painter: QPainter, width: int) -> None:
        """绘制标题。"""

        colors = _palette()
        if hasattr(painter, "setPen"):
            painter.setPen(_qcolor(colors.text))
        if hasattr(painter, "setFont"):
            painter.setFont(QFont("Microsoft YaHei", 10, 600))
        if hasattr(painter, "drawText"):
            painter.drawText(20, 28, self._title)
        if hasattr(painter, "setFont"):
            painter.setFont(QFont("Microsoft YaHei", 8, 400))
        if hasattr(painter, "setPen"):
            painter.setPen(_qcolor(colors.text_muted))
        if hasattr(painter, "drawText") and self._unit:
            painter.drawText(width - 120, 28, f"单位：{self._unit}")

    def _draw_empty(self, painter: QPainter, width: int, height: int) -> None:
        """绘制空状态。"""

        colors = _palette()
        if hasattr(painter, "setPen"):
            painter.setPen(_qcolor(colors.text_muted))
        if hasattr(painter, "drawText"):
            painter.drawText(int(width / 2) - 24, int(height / 2), "暂无数据")

    def _plot_rect(self, width: int, height: int) -> QRectF:
        """返回可绘图区域。"""

        return QRectF(54.0, 48.0, float(max(width - 86, 40)), float(max(height - 92, 40)))

    def _draw_xy_chart(self, painter: QPainter, width: int, height: int) -> None:
        """绘制折线或柱状图。"""

        colors = _palette()
        rect = self._plot_rect(width, height)
        minimum = min(0.0, min(self._data))
        maximum = max(self._data)
        if math.isclose(minimum, maximum):
            maximum += 1.0

        grid_pen = QPen(_qcolor(colors.border, 0.72))
        if hasattr(grid_pen, "setWidth"):
            grid_pen.setWidth(1)
        painter.setPen(grid_pen)
        for index in range(4):
            y = rect.top() + rect.height() * (index / 3)
            if hasattr(painter, "drawLine"):
                painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))

        axis_pen = QPen(_qcolor(colors.border))
        if hasattr(axis_pen, "setWidth"):
            axis_pen.setWidth(1)
        painter.setPen(axis_pen)
        if hasattr(painter, "drawLine"):
            painter.drawLine(int(rect.left()), int(rect.bottom()), int(rect.right()), int(rect.bottom()))
            painter.drawLine(int(rect.left()), int(rect.top()), int(rect.left()), int(rect.bottom()))

        self._draw_axis_labels(painter, rect, minimum, maximum)
        if self._chart_type == "bar":
            self._draw_bar_series(painter, rect, minimum, maximum)
        else:
            self._draw_line_series(painter, rect, minimum, maximum)

    def _draw_axis_labels(self, painter: QPainter, rect: QRectF, minimum: float, maximum: float) -> None:
        """绘制坐标轴标签。"""

        colors = _palette()
        if hasattr(painter, "setFont"):
            painter.setFont(QFont("Microsoft YaHei", 8, 400))
        if hasattr(painter, "setPen"):
            painter.setPen(_qcolor(colors.text_muted))

        for index in range(4):
            value = maximum - (maximum - minimum) * (index / 3)
            text = f"{value:.1f}{self._unit}" if self._unit else f"{value:.1f}"
            y = rect.top() + rect.height() * (index / 3)
            if hasattr(painter, "drawText"):
                painter.drawText(10, int(y + 4), text)

        if not self._labels:
            return
        visible_labels = self._labels
        count = max(len(visible_labels) - 1, 1)
        for index, label in enumerate(visible_labels):
            if len(visible_labels) > 6 and index not in {0, len(visible_labels) // 2, len(visible_labels) - 1}:
                continue
            x = rect.left() + rect.width() * (index / count)
            if hasattr(painter, "drawText"):
                painter.drawText(int(x - 10), int(rect.bottom() + 18), label)

    def _draw_line_series(self, painter: QPainter, rect: QRectF, minimum: float, maximum: float) -> None:
        """绘制折线序列。"""

        color = _series_color(0)
        points = self._map_points(rect, minimum, maximum)
        if len(points) < 2:
            return

        if hasattr(painter, "setBrush"):
            area = QPainterPath()
            area.moveTo(QPointF(_point_x(points[0]), rect.bottom()))
            for point in points:
                area.lineTo(point)
            area.lineTo(QPointF(_point_x(points[-1]), rect.bottom()))
            painter.setPen(getattr(Qt, "NoPen", 0))
            painter.setBrush(_qcolor(color, 0.12))
            if hasattr(painter, "drawPath"):
                painter.drawPath(area)

        pen = QPen(_qcolor(color))
        if hasattr(pen, "setWidth"):
            pen.setWidth(3)
        painter.setPen(pen)
        path = QPainterPath()
        path.moveTo(points[0])
        for point in points[1:]:
            path.lineTo(point)
        if hasattr(painter, "drawPath"):
            painter.drawPath(path)

        if hasattr(painter, "setBrush") and hasattr(painter, "drawEllipse"):
            painter.setBrush(_qcolor(color))
            for point in points:
                painter.drawEllipse(QRectF(_point_x(point) - 3.0, _point_y(point) - 3.0, 6.0, 6.0))

    def _draw_bar_series(self, painter: QPainter, rect: QRectF, minimum: float, maximum: float) -> None:
        """绘制柱状序列。"""

        bar_count = max(len(self._data), 1)
        slot_width = rect.width() / bar_count
        safe_span = maximum - minimum or 1.0
        painter.setPen(getattr(Qt, "NoPen", 0))
        for index, value in enumerate(self._data):
            normalized = (value - minimum) / safe_span
            bar_height = rect.height() * normalized
            x = rect.left() + slot_width * index + slot_width * 0.14
            y = rect.bottom() - bar_height
            color = _series_color(index)
            if hasattr(painter, "setBrush"):
                painter.setBrush(_qcolor(color, 0.92))
            if hasattr(painter, "drawRoundedRect"):
                painter.drawRoundedRect(QRectF(x, y, slot_width * 0.72, bar_height), 8.0, 8.0)

    def _draw_pie_chart(self, painter: QPainter, width: int, height: int) -> None:
        """绘制饼图与图例。"""

        colors = _palette()
        total = sum(max(value, 0.0) for value in self._data)
        if total <= 0:
            self._draw_empty(painter, width, height)
            return

        diameter = float(min(width, height) - 96)
        diameter = max(diameter, 80.0)
        pie_rect = QRectF(28.0, 52.0, diameter, diameter)
        start_angle = 90.0
        painter.setPen(getattr(Qt, "NoPen", 0))

        for index, value in enumerate(self._data):
            if value <= 0:
                continue
            color = _series_color(index)
            span = 360.0 * (value / total)
            if hasattr(painter, "setBrush"):
                painter.setBrush(_qcolor(color))
            if hasattr(painter, "drawPie"):
                painter.drawPie(
                    pie_rect,
                    int(start_angle * 16),
                    int(-span * 16),
                )
            start_angle -= span

        if hasattr(painter, "setPen"):
            painter.setPen(_qcolor(colors.text))
        if hasattr(painter, "setFont"):
            painter.setFont(QFont("Microsoft YaHei", 11, 700))
        if hasattr(painter, "drawText"):
            painter.drawText(int(pie_rect.left() + pie_rect.width() / 2 - 18), int(pie_rect.top() + pie_rect.height() / 2), "ROAS")

        if hasattr(painter, "setFont"):
            painter.setFont(QFont("Microsoft YaHei", 8, 400))
        legend_x = int(pie_rect.right() + 28)
        legend_y = 78
        for index, value in enumerate(self._data):
            color = _series_color(index)
            label = self._labels[index] if index < len(self._labels) else f"分类 {index + 1}"
            percentage = value / total * 100
            if hasattr(painter, "setBrush"):
                painter.setBrush(_qcolor(color))
            if hasattr(painter, "drawRoundedRect"):
                painter.drawRoundedRect(QRectF(float(legend_x), float(legend_y - 10), 10.0, 10.0), 3.0, 3.0)
            if hasattr(painter, "setPen"):
                painter.setPen(_qcolor(colors.text))
            if hasattr(painter, "drawText"):
                painter.drawText(legend_x + 18, legend_y, f"{label}  {percentage:.0f}%")
            if hasattr(painter, "setPen"):
                painter.setPen(_qcolor(colors.text_muted))
            if hasattr(painter, "drawText"):
                painter.drawText(legend_x + 18, legend_y + 16, f"{value:.1f}{self._unit}")
            legend_y += 34

    def _map_points(self, rect: QRectF, minimum: float, maximum: float) -> list[QPointF]:
        """计算折线绘制点。"""

        safe_span = maximum - minimum or 1.0
        count = max(len(self._data) - 1, 1)
        points: list[QPointF] = []
        for index, value in enumerate(self._data):
            x = rect.left() + rect.width() * (index / count)
            y_ratio = (value - minimum) / safe_span
            y = rect.bottom() - rect.height() * y_ratio
            points.append(QPointF(float(x), float(y)))
        return points

    def _apply_styles(self) -> None:
        """应用容器样式。"""

        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#chartWidget {{
                background-color: {_rgba(colors.surface, 0.82) if colors.surface.startswith('#') else colors.surface};
                border: 1px solid {colors.border};
                border-radius: {_static_token('radius.lg')};
            }}
            """,
        )


ChartPlaceholder = ChartWidget


__all__ = ["ChartPlaceholder", "ChartWidget", "MiniSparkline"]
