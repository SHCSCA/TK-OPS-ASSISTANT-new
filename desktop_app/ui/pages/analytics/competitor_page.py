# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportPrivateUsage=false, reportUntypedBaseClass=false, reportUnannotatedClassAttribute=false, reportAny=false, reportImplicitOverride=false, reportReturnType=false, reportCallIssue=false, reportAssignmentType=false, reportGeneralTypeIssues=false

from __future__ import annotations

"""竞争对手监控页面。"""

from dataclasses import dataclass
from typing import Sequence

from ....core.types import RouteId
from ...components import (
    ChartWidget,
    ContentSection,
    DataTable,
    FilterDropdown,
    PageContainer,
    PrimaryButton,
    SearchBar,
    StatusBadge,
    TagChip,
)
from ...components.charts import (
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QPointF,
    QRectF,
    _point_x,
    _point_y,
    _qcolor,
    _series_color,
    _widget_size,
)
from ...components.inputs import (
    RADIUS_LG,
    SPACING_2XL,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    QFrame,
    QHBoxLayout,
    QLabel,
    Qt,
    QVBoxLayout,
    QWidget,
    Signal,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ...components.tags import BadgeTone
from ..base_page import BasePage


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba 字符串。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


@dataclass(frozen=True)
class CompetitorSnapshot:
    """单个竞品监控实体的静态展示数据。"""

    competitor_id: str
    shop_name: str
    handle: str
    category: str
    follower_count: str
    video_count: int
    daily_sales: str
    rating: str
    growth_rate: float
    trend_points: tuple[float, ...]

    @property
    def growth_text(self) -> str:
        """返回格式化后的增长率文案。"""

        return f"{self.growth_rate:+.1f}%"

    @property
    def growth_arrow(self) -> str:
        """返回趋势箭头。"""

        if self.growth_rate > 0:
            return "↑"
        if self.growth_rate < 0:
            return "↓"
        return "→"

    @property
    def growth_tone(self) -> BadgeTone:
        """返回增长率对应的状态色调。"""

        if self.growth_rate > 0:
            return "success"
        if self.growth_rate < 0:
            return "error"
        return "info"


class CompetitorCard(QFrame):
    """可点击的竞品概览卡片。"""

    clicked = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._snapshot: CompetitorSnapshot | None = None
        self._selected = False
        _call(self, "setObjectName", "competitorMonitorCard")
        _call(self, "setCursor", getattr(Qt, "PointingHandCursor", 0))

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        root.setSpacing(SPACING_LG)

        header = QHBoxLayout()
        header.setSpacing(SPACING_MD)

        avatar_size = SPACING_2XL * 2 + SPACING_SM
        self._avatar = QLabel("竞品", self)
        _call(self._avatar, "setObjectName", "competitorMonitorCardAvatar")
        _call(self._avatar, "setAlignment", getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignCenter", 0))
        _call(self._avatar, "setFixedSize", avatar_size, avatar_size)

        title_column = QVBoxLayout()
        title_column.setContentsMargins(0, 0, 0, 0)
        title_column.setSpacing(SPACING_XS)

        self._name_label = QLabel("", self)
        _call(self._name_label, "setObjectName", "competitorMonitorCardTitle")

        self._handle_label = QLabel("", self)
        _call(self._handle_label, "setObjectName", "competitorMonitorCardHandle")

        title_column.addWidget(self._name_label)
        title_column.addWidget(self._handle_label)

        self._growth_badge = StatusBadge("↑ +0.0%", tone="info", parent=self)

        header.addWidget(self._avatar)
        header.addLayout(title_column, 1)
        header.addWidget(self._growth_badge)

        meta_row = QHBoxLayout()
        meta_row.setContentsMargins(0, 0, 0, 0)
        meta_row.setSpacing(SPACING_SM)

        self._category_chip = TagChip("类目", tone="neutral", parent=self)
        self._monitor_badge = StatusBadge("监控中", tone="brand", parent=self)

        meta_row.addWidget(self._category_chip)
        meta_row.addWidget(self._monitor_badge)
        meta_row.addStretch(1)

        metric_column = QVBoxLayout()
        metric_column.setContentsMargins(0, 0, 0, 0)
        metric_column.setSpacing(SPACING_XS)

        self._metric_eyebrow = QLabel("粉丝数", self)
        _call(self._metric_eyebrow, "setObjectName", "competitorMonitorCardEyebrow")

        self._metric_value = QLabel("", self)
        _call(self._metric_value, "setObjectName", "competitorMonitorCardValue")

        self._metric_caption = QLabel("", self)
        _call(self._metric_caption, "setObjectName", "competitorMonitorCardCaption")

        metric_column.addWidget(self._metric_eyebrow)
        metric_column.addWidget(self._metric_value)
        metric_column.addWidget(self._metric_caption)

        root.addLayout(header)
        root.addLayout(meta_row)
        root.addLayout(metric_column)
        self._apply_styles()

    @property
    def competitor_id(self) -> str | None:
        """返回当前卡片绑定的竞品 ID。"""

        return self._snapshot.competitor_id if self._snapshot else None

    def set_snapshot(self, snapshot: CompetitorSnapshot) -> None:
        """更新卡片展示数据。"""

        self._snapshot = snapshot
        _call(self._avatar, "setText", self._initials(snapshot.shop_name))
        _call(self._name_label, "setText", snapshot.shop_name)
        _call(self._handle_label, "setText", snapshot.handle)
        self._category_chip.set_text(snapshot.category)
        self._category_chip.set_tone(self._category_tone(snapshot.category))
        _call(self._growth_badge, "setText", f"{snapshot.growth_arrow} {snapshot.growth_text}")
        self._growth_badge.set_tone(snapshot.growth_tone)
        _call(self._metric_value, "setText", snapshot.follower_count)
        _call(self._metric_caption, "setText", f"视频 {snapshot.video_count} 条 · 日均销售 {snapshot.daily_sales}")
        self._apply_styles()

    def set_selected(self, selected: bool) -> None:
        """切换卡片选中态。"""

        self._selected = selected
        self._apply_styles()

    def mousePressEvent(self, event: object) -> None:
        """点击卡片时抛出对应竞品 ID。"""

        del event
        if self._snapshot is not None:
            self.clicked.emit(self._snapshot.competitor_id)

    @staticmethod
    def _initials(name: str) -> str:
        """提取店铺名首字作为头像占位。"""

        compact = "".join(part for part in name.strip().split() if part)
        if not compact:
            return "竞品"
        return compact[:2]

    @staticmethod
    def _category_tone(category: str) -> BadgeTone:
        """根据类目映射标签色调。"""

        mapping = {
            "3C数码": "brand",
            "家居生活": "info",
            "美妆个护": "warning",
            "运动户外": "success",
            "综合百货": "neutral",
            "宠物用品": "error",
        }
        return mapping.get(category, "neutral")

    def _apply_styles(self) -> None:
        colors = _palette()
        border_color = _token("brand.primary") if self._selected else colors.border
        background = _rgba(_token("brand.primary"), 0.08) if self._selected else colors.surface
        avatar_background = _rgba(_token("brand.primary"), 0.14 if self._selected else 0.10)
        avatar_border = _rgba(_token("brand.primary"), 0.28 if self._selected else 0.18)
        _call(
            self,
            "setStyleSheet",
            f"""
            QFrame#competitorMonitorCard {{
                background-color: {background};
                border: 1px solid {border_color};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#competitorMonitorCardAvatar {{
                background-color: {avatar_background};
                border: 1px solid {avatar_border};
                border-radius: {SPACING_2XL + SPACING_MD}px;
                color: {_token('brand.primary')};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#competitorMonitorCardTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#competitorMonitorCardHandle, QLabel#competitorMonitorCardCaption {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QLabel#competitorMonitorCardEyebrow {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.xs')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QLabel#competitorMonitorCardValue {{
                color: {colors.text};
                font-size: {_static_token('font.size.xxl')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            """,
        )


class CompetitorTrendChart(ChartWidget):
    """支持多竞品折线对比的图表组件。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            chart_type="line",
            title="近 7 天粉丝增长趋势对比",
            labels=("周一", "周二", "周三", "周四", "周五", "周六", "周日"),
            data=(0.0,),
            unit="%",
            parent=parent,
        )
        self._series: list[tuple[str, list[float]]] = []
        _call(self, "setObjectName", "competitorTrendChart")

    def set_series(self, series: Sequence[tuple[str, Sequence[float | int]]], labels: Sequence[str] | None = None, unit: str = "%") -> None:
        """更新折线图的多序列数据。"""

        self._series = [(name, [float(value) for value in values]) for name, values in series if values]
        if labels is not None:
            self._labels = [str(label) for label in labels]
        self._unit = unit
        self._data = self._series[0][1] if self._series else []
        _call(self, "update")

    def paintEvent(self, _event: object) -> None:
        """绘制多竞品趋势对比折线。"""

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
        if not self._series:
            self._draw_empty(painter, width, height)
            return

        plot_rect = self._plot_rect(width, height)
        all_values = [value for _name, values in self._series for value in values]
        minimum = min(0.0, min(all_values))
        maximum = max(all_values)
        if maximum <= minimum:
            maximum = minimum + 1.0

        grid_pen = QPen(_qcolor(colors.border, 0.72))
        if hasattr(grid_pen, "setWidth"):
            grid_pen.setWidth(1)
        painter.setPen(grid_pen)
        for index in range(4):
            y = plot_rect.top() + plot_rect.height() * (index / 3)
            if hasattr(painter, "drawLine"):
                painter.drawLine(int(plot_rect.left()), int(y), int(plot_rect.right()), int(y))

        axis_pen = QPen(_qcolor(colors.border))
        if hasattr(axis_pen, "setWidth"):
            axis_pen.setWidth(1)
        painter.setPen(axis_pen)
        if hasattr(painter, "drawLine"):
            painter.drawLine(int(plot_rect.left()), int(plot_rect.bottom()), int(plot_rect.right()), int(plot_rect.bottom()))
            painter.drawLine(int(plot_rect.left()), int(plot_rect.top()), int(plot_rect.left()), int(plot_rect.bottom()))

        self._draw_axis_labels(painter, plot_rect, minimum, maximum)

        for index, (_name, values) in enumerate(self._series):
            points = self._map_series_points(plot_rect, values, minimum, maximum)
            if len(points) < 2:
                continue
            color = _series_color(index)

            if index == 0 and hasattr(painter, "setBrush"):
                area = QPainterPath()
                area.moveTo(QPointF(_point_x(points[0]), plot_rect.bottom()))
                for point in points:
                    area.lineTo(point)
                area.lineTo(QPointF(_point_x(points[-1]), plot_rect.bottom()))
                painter.setPen(getattr(Qt, "NoPen", 0))
                painter.setBrush(_qcolor(color, 0.12))
                if hasattr(painter, "drawPath"):
                    painter.drawPath(area)

            pen = QPen(_qcolor(color))
            if hasattr(pen, "setWidth"):
                pen.setWidth(3 if index == 0 else 2)
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
                    radius = 4.0 if index == 0 else 3.0
                    painter.drawEllipse(QRectF(_point_x(point) - radius, _point_y(point) - radius, radius * 2, radius * 2))

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
        count = max(len(self._labels) - 1, 1)
        for index, label in enumerate(self._labels):
            x = rect.left() + rect.width() * (index / count)
            if hasattr(painter, "drawText"):
                painter.drawText(int(x - SPACING_MD), int(rect.bottom() + SPACING_XL), label)

    @staticmethod
    def _map_series_points(rect: QRectF, values: Sequence[float], minimum: float, maximum: float) -> list[QPointF]:
        """将数值序列映射到折线坐标。"""

        safe_span = maximum - minimum or 1.0
        count = max(len(values) - 1, 1)
        points: list[QPointF] = []
        for index, value in enumerate(values):
            x = rect.left() + rect.width() * (index / count)
            ratio = (value - minimum) / safe_span
            y = rect.bottom() - rect.height() * ratio
            points.append(QPointF(float(x), float(y)))
        return points


class CompetitorPage(BasePage):
    """竞争对手监控分析页。"""

    default_route_id: RouteId = RouteId("competitor_monitoring")
    default_display_name: str = "竞争对手监控"
    default_icon_name: str = "bar_chart"

    def setup_ui(self) -> None:
        """构建竞品搜索、监控卡片、表现表与趋势图。"""

        self._active_competitors = self._default_competitors()
        self._backup_competitors = self._extra_competitors()
        self._filtered_competitors: list[CompetitorSnapshot] = []
        self._selected_competitor_id = self._active_competitors[0].competitor_id if self._active_competitors else None
        self._syncing_table_selection = False

        _call(self, "setObjectName", "competitorPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#competitorPage {{
                background-color: {colors.surface_alt};
            }}
            QFrame#competitorToolbar {{
                background-color: {colors.surface};
                border: 1px solid {_rgba(_token('brand.primary'), 0.18)};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#competitorPanelTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#competitorToolbarHint, QLabel#competitorEmptyLabel {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                background: transparent;
            }}
            QLabel#competitorToolbarSummary {{
                color: {colors.primary};
                background-color: {_rgba(_token('brand.primary'), 0.08)};
                border: 1px solid {_rgba(_token('brand.primary'), 0.22)};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_SM}px {SPACING_LG}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            """,
        )

        page_container = PageContainer(
            title=self.display_name,
            description="集中查看竞品店铺的粉丝规模、内容产能与增长趋势，快速定位值得追踪的运营信号。",
            parent=self,
        )
        self.layout.addWidget(page_container)

        page_container.add_widget(self._build_toolbar())
        page_container.add_widget(self._build_cards_section())
        page_container.add_widget(self._build_table_section())
        page_container.add_widget(self._build_chart_section())

        self._refresh_add_button_state()
        self._apply_filters()

    def _build_toolbar(self) -> QWidget:
        """构建顶部交互工具条。"""

        toolbar = QFrame(self)
        _call(toolbar, "setObjectName", "competitorToolbar")
        root_layout = QVBoxLayout(toolbar)
        root_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        root_layout.setSpacing(SPACING_LG)

        title_row = QWidget(toolbar)
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_MD)

        title_column = QWidget(title_row)
        title_column_layout = QVBoxLayout(title_column)
        title_column_layout.setContentsMargins(0, 0, 0, 0)
        title_column_layout.setSpacing(SPACING_XS)
        title_label = QLabel("竞品筛选", title_column)
        _call(title_label, "setObjectName", "competitorPanelTitle")
        helper_label = QLabel("按关键词与类目快速切片监控矩阵，联动下方竞品表与趋势对比。", title_column)
        _call(helper_label, "setObjectName", "competitorToolbarHint")
        _call(helper_label, "setWordWrap", True)
        title_column_layout.addWidget(title_label)
        title_column_layout.addWidget(helper_label)

        self._toolbar_summary = QLabel("当前监控 0 个竞品对象", title_row)
        _call(self._toolbar_summary, "setObjectName", "competitorToolbarSummary")

        title_layout.addWidget(title_column, 1)
        title_layout.addWidget(self._toolbar_summary)

        filter_row = QWidget(toolbar)
        toolbar_layout = QHBoxLayout(filter_row)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(SPACING_XL)

        self._search_bar = SearchBar("搜索店铺名 / 账号 / 类目", toolbar)
        self._add_button = PrimaryButton("添加竞品", toolbar)
        self._filter_dropdown = FilterDropdown("类目筛选", self._all_categories(), parent=toolbar)
        self._toolbar_hint = QLabel("点击竞品卡片可同步联动下方表格与趋势图。", toolbar)
        _call(self._toolbar_hint, "setObjectName", "competitorToolbarHint")

        toolbar_layout.addWidget(self._search_bar, 1)
        toolbar_layout.addWidget(self._filter_dropdown)
        toolbar_layout.addWidget(self._add_button)

        root_layout.addWidget(title_row)
        root_layout.addWidget(filter_row)
        root_layout.addWidget(self._toolbar_hint)

        _connect(self._search_bar.search_changed, self._on_search_changed)
        _connect(self._filter_dropdown.filter_changed, self._on_filter_changed)
        _connect(getattr(self._add_button, "clicked", None), self._handle_add_competitor)
        return toolbar

    def _build_cards_section(self) -> ContentSection:
        """构建竞品监控卡片区。"""

        section = ContentSection("竞品监控矩阵", icon="◎", parent=self)

        self._cards_empty_label = QLabel("暂无匹配的竞品监控对象。", section)
        _call(self._cards_empty_label, "setObjectName", "competitorEmptyLabel")

        card_grid = QWidget(section)
        card_grid_layout = QVBoxLayout(card_grid)
        card_grid_layout.setContentsMargins(0, 0, 0, 0)
        card_grid_layout.setSpacing(SPACING_LG)

        self._card_widgets: list[CompetitorCard] = []
        for _row_index in range(2):
            row = QWidget(card_grid)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(SPACING_LG)
            for _column_index in range(3):
                card = CompetitorCard(row)
                _connect(card.clicked, self._select_competitor)
                row_layout.addWidget(card, 1)
                self._card_widgets.append(card)
            card_grid_layout.addWidget(row)

        section.add_widget(self._cards_empty_label)
        section.add_widget(card_grid)
        return section

    def _build_table_section(self) -> ContentSection:
        """构建竞品表现表格区。"""

        section = ContentSection("竞品表现表", icon="▦", parent=self)
        self._performance_table = DataTable(
            headers=("店铺名", "粉丝数", "视频数", "日均销售", "评分", "增长率"),
            rows=(),
            page_size=6,
            empty_text="暂无符合条件的竞品数据",
            parent=section,
        )
        _connect(self._performance_table.row_selected, self._handle_table_selection)
        section.add_widget(self._performance_table)
        return section

    def _build_chart_section(self) -> ContentSection:
        """构建趋势对比区。"""

        section = ContentSection("趋势对比", icon="∿", parent=self)

        legend_widget = QWidget(section)
        legend_layout = QHBoxLayout(legend_widget)
        legend_layout.setContentsMargins(0, 0, 0, 0)
        legend_layout.setSpacing(SPACING_SM)

        self._legend_chips: list[TagChip] = []
        for tone in ("brand", "info", "warning"):
            chip = TagChip("", tone=tone, parent=legend_widget)
            _call(chip, "setVisible", False)
            legend_layout.addWidget(chip)
            self._legend_chips.append(chip)
        legend_layout.addStretch(1)

        self._trend_chart = CompetitorTrendChart(section)
        section.add_widget(legend_widget)
        section.add_widget(self._trend_chart)
        return section

    def _on_search_changed(self, _text: str) -> None:
        """搜索条件变化时刷新页面。"""

        self._apply_filters()

    def _on_filter_changed(self, _text: str) -> None:
        """类目筛选变化时刷新页面。"""

        self._apply_filters()

    def _apply_filters(self) -> None:
        """根据搜索词与类目筛选刷新卡片、表格与图表。"""

        keyword = self._search_bar.text().strip().lower()
        category = self._filter_dropdown.current_text()

        self._filtered_competitors = []
        for snapshot in self._active_competitors:
            haystack = f"{snapshot.shop_name} {snapshot.handle} {snapshot.category}".lower()
            matches_keyword = not keyword or keyword in haystack
            matches_category = category in ("", "全部") or snapshot.category == category
            if matches_keyword and matches_category:
                self._filtered_competitors.append(snapshot)

        if keyword or category not in ("", "全部"):
            self._toolbar_summary.setText(f"已筛选 {len(self._filtered_competitors)} / {len(self._active_competitors)} 个竞品对象")
        else:
            self._toolbar_summary.setText(f"当前监控 {len(self._active_competitors)} 个竞品对象")

        available_ids = {snapshot.competitor_id for snapshot in self._filtered_competitors}
        if self._selected_competitor_id not in available_ids:
            self._selected_competitor_id = self._filtered_competitors[0].competitor_id if self._filtered_competitors else None

        self._refresh_cards()
        self._refresh_table()
        self._refresh_chart()

    def _refresh_cards(self) -> None:
        """同步卡片区内容与显隐状态。"""

        has_cards = bool(self._filtered_competitors)
        _call(self._cards_empty_label, "setVisible", not has_cards)

        for index, card in enumerate(self._card_widgets):
            if index < len(self._filtered_competitors):
                snapshot = self._filtered_competitors[index]
                card.set_snapshot(snapshot)
                card.set_selected(snapshot.competitor_id == self._selected_competitor_id)
                _call(card, "setVisible", True)
            else:
                _call(card, "setVisible", False)

    def _refresh_table(self) -> None:
        """刷新表格数据并同步行选中态。"""

        rows = [
            (
                snapshot.shop_name,
                snapshot.follower_count,
                str(snapshot.video_count),
                snapshot.daily_sales,
                snapshot.rating,
                f"{snapshot.growth_arrow} {snapshot.growth_text}",
            )
            for snapshot in self._filtered_competitors
        ]
        self._performance_table.set_rows(rows)

        if not self._selected_competitor_id:
            return
        target_index = next(
            (
                index
                for index, snapshot in enumerate(self._filtered_competitors)
                if snapshot.competitor_id == self._selected_competitor_id
            ),
            -1,
        )
        if target_index >= 0:
            self._syncing_table_selection = True
            self._performance_table.select_absolute_row(target_index)
            self._syncing_table_selection = False

    def _refresh_chart(self) -> None:
        """刷新底部趋势图与图例。"""

        if not self._filtered_competitors:
            self._trend_chart.set_series((), labels=("周一", "周二", "周三", "周四", "周五", "周六", "周日"))
            for chip in self._legend_chips:
                _call(chip, "setVisible", False)
            return

        selected_snapshot = next(
            (
                snapshot
                for snapshot in self._filtered_competitors
                if snapshot.competitor_id == self._selected_competitor_id
            ),
            self._filtered_competitors[0],
        )
        comparison_snapshots = [selected_snapshot]
        for snapshot in self._filtered_competitors:
            if snapshot.competitor_id == selected_snapshot.competitor_id:
                continue
            comparison_snapshots.append(snapshot)
            if len(comparison_snapshots) == 3:
                break

        self._trend_chart.set_series(
            [(snapshot.shop_name, snapshot.trend_points) for snapshot in comparison_snapshots],
            labels=("周一", "周二", "周三", "周四", "周五", "周六", "周日"),
            unit="%",
        )

        legend_tones: tuple[BadgeTone, ...] = ("brand", "info", "warning")
        for index, chip in enumerate(self._legend_chips):
            if index < len(comparison_snapshots):
                snapshot = comparison_snapshots[index]
                chip.set_text(f"{snapshot.shop_name} {snapshot.growth_arrow}{snapshot.growth_text}")
                chip.set_tone(legend_tones[index])
                _call(chip, "setVisible", True)
            else:
                _call(chip, "setVisible", False)

    def _handle_table_selection(self, row_index: int) -> None:
        """表格选中行变化时联动卡片与图表。"""

        if self._syncing_table_selection:
            return
        if not (0 <= row_index < len(self._filtered_competitors)):
            return
        self._select_competitor(self._filtered_competitors[row_index].competitor_id, sync_table=False)

    def _select_competitor(self, competitor_id: str, sync_table: bool = True) -> None:
        """选中指定竞品并刷新联动状态。"""

        self._selected_competitor_id = competitor_id
        for card in self._card_widgets:
            card.set_selected(card.competitor_id == competitor_id)
        self._refresh_chart()

        if not sync_table:
            return
        target_index = next(
            (
                index
                for index, snapshot in enumerate(self._filtered_competitors)
                if snapshot.competitor_id == competitor_id
            ),
            -1,
        )
        if target_index >= 0:
            self._syncing_table_selection = True
            self._performance_table.select_absolute_row(target_index)
            self._syncing_table_selection = False

    def _handle_add_competitor(self) -> None:
        """将预置竞品加入当前监控池。"""

        if not self._backup_competitors:
            self._refresh_add_button_state()
            return
        self._active_competitors.append(self._backup_competitors.pop(0))
        self._refresh_add_button_state()
        self._refresh_filter_items()
        self._apply_filters()

    def _refresh_filter_items(self) -> None:
        """刷新类目下拉框选项并尽量保留当前值。"""

        current_text = self._filter_dropdown.current_text()
        self._filter_dropdown.set_items(self._all_categories())
        if current_text:
            self._filter_dropdown.set_current_text(current_text)

    def _refresh_add_button_state(self) -> None:
        """根据剩余候选数据刷新按钮文案与可用态。"""

        if self._backup_competitors:
            self._add_button.set_label_text("添加竞品")
            _call(self._add_button, "setEnabled", True)
            return
        self._add_button.set_label_text("竞品已全部加入")
        _call(self._add_button, "setEnabled", False)

    def _all_categories(self) -> list[str]:
        """返回当前页面全部类目选项。"""

        categories = {snapshot.category for snapshot in [*self._active_competitors, *self._backup_competitors]}
        return sorted(categories)

    @staticmethod
    def _default_competitors() -> list[CompetitorSnapshot]:
        """返回默认展示的竞品数据。"""

        return [
            CompetitorSnapshot(
                competitor_id="stellar_digital",
                shop_name="星澜数码旗舰店",
                handle="@StellarDigital",
                category="3C数码",
                follower_count="142.8万",
                video_count=86,
                daily_sales="¥23.6万",
                rating="4.9",
                growth_rate=12.6,
                trend_points=(3.2, 4.1, 5.4, 6.2, 8.1, 9.8, 12.6),
            ),
            CompetitorSnapshot(
                competitor_id="aurora_home",
                shop_name="北极光家居",
                handle="@AuroraHome",
                category="家居生活",
                follower_count="98.3万",
                video_count=63,
                daily_sales="¥15.8万",
                rating="4.8",
                growth_rate=8.4,
                trend_points=(2.4, 2.9, 3.7, 4.6, 5.4, 6.7, 8.4),
            ),
            CompetitorSnapshot(
                competitor_id="nova_beauty",
                shop_name="NovaBeauty Lab",
                handle="@NovaBeautyLab",
                category="美妆个护",
                follower_count="187.5万",
                video_count=118,
                daily_sales="¥31.2万",
                rating="4.7",
                growth_rate=-3.1,
                trend_points=(5.8, 5.4, 4.8, 4.2, 3.6, 3.2, 3.1),
            ),
            CompetitorSnapshot(
                competitor_id="trendfit_sport",
                shop_name="TrendFit 运动仓",
                handle="@TrendFitSport",
                category="运动户外",
                follower_count="76.9万",
                video_count=72,
                daily_sales="¥12.4万",
                rating="4.8",
                growth_rate=15.8,
                trend_points=(2.1, 3.1, 4.8, 6.9, 9.2, 12.4, 15.8),
            ),
            CompetitorSnapshot(
                competitor_id="goodlab_store",
                shop_name="好物研究局",
                handle="@GoodLabStore",
                category="综合百货",
                follower_count="54.2万",
                video_count=49,
                daily_sales="¥8.9万",
                rating="4.6",
                growth_rate=6.3,
                trend_points=(1.6, 2.4, 3.0, 3.8, 4.7, 5.5, 6.3),
            ),
        ]

    @staticmethod
    def _extra_competitors() -> list[CompetitorSnapshot]:
        """返回待加入的补充竞品数据。"""

        return [
            CompetitorSnapshot(
                competitor_id="bloom_pet",
                shop_name="BloomPet 官方店",
                handle="@BloomPetOfficial",
                category="宠物用品",
                follower_count="61.7万",
                video_count=57,
                daily_sales="¥10.6万",
                rating="4.8",
                growth_rate=9.7,
                trend_points=(2.0, 2.7, 3.4, 4.6, 6.1, 8.2, 9.7),
            )
        ]


__all__ = ["CompetitorPage"]
