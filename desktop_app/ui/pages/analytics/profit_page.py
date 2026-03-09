# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportArgumentType=false, reportCallIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportPrivateUsage=false, reportImplicitOverride=false, reportUnusedCallResult=false, reportUninitializedInstanceVariable=false

from __future__ import annotations

"""利润分析系统页面。"""

from dataclasses import dataclass
from typing import Sequence

from ....core.types import RouteId
from ...components import (
    ChartWidget,
    ContentSection,
    DataTable,
    FilterDropdown,
    KPICard,
    PageContainer,
    PrimaryButton,
    SearchBar,
    StatusBadge,
    TabBar,
)
from ...components.charts import QFont, QPainter, QPen, QRectF, _qcolor, _series_color, _widget_size
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
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ...components.tags import BadgeTone
from ..base_page import BasePage

TREND_LABELS: tuple[str, ...] = ("10/01", "10/05", "10/10", "10/15", "10/20", "10/25", "10/31")
HIGH_MARGIN_THRESHOLD = 0.35
STABLE_MARGIN_THRESHOLD = 0.20
LEGEND_MARK_SIZE = SPACING_MD
LEGEND_RIGHT_PADDING = SPACING_2XL * 5
Y_AXIS_WIDTH = SPACING_2XL * 2 + SPACING_MD
CHART_RADIUS = float(RADIUS_LG)


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba 字符串。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _format_currency(value: float | int) -> str:
    """格式化货币。"""

    return f"¥{float(value):,.0f}"


def _format_compact_currency(value: float | int) -> str:
    """格式化紧凑货币。"""

    amount = float(value)
    if abs(amount) >= 10000:
        return f"¥{amount / 10000:.1f}万"
    return _format_currency(amount)


def _format_percent(value: float) -> str:
    """格式化百分比。"""

    return f"{value * 100:.1f}%"


def _safe_ratio(numerator: float, denominator: float) -> float:
    """避免除零。"""

    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _normalize_series(total: float, weights: Sequence[float]) -> tuple[float, ...]:
    """按权重将总量拆分为时间序列。"""

    safe_weights = [max(0.0, float(weight)) for weight in weights]
    total_weight = sum(safe_weights)
    if total_weight <= 0:
        average = total / max(len(safe_weights), 1)
        return tuple(round(average, 2) for _ in safe_weights)

    points: list[float] = []
    consumed = 0.0
    for weight in safe_weights[:-1]:
        point = round(total * weight / total_weight, 2)
        points.append(point)
        consumed += point
    points.append(round(total - consumed, 2))
    return tuple(points)


def _tone_for_margin(margin: float) -> BadgeTone:
    """按利润率映射 tone。"""

    if margin >= HIGH_MARGIN_THRESHOLD:
        return "success"
    if margin >= STABLE_MARGIN_THRESHOLD:
        return "info"
    return "warning"


def _bucket_for_margin(margin: float) -> str:
    """按利润率返回分层名称。"""

    if margin >= HIGH_MARGIN_THRESHOLD:
        return "高利润"
    if margin >= STABLE_MARGIN_THRESHOLD:
        return "稳健"
    return "待优化"


@dataclass(frozen=True)
class ProfitProductRecord:
    """单个商品的利润分析静态数据。"""

    name: str
    category: str
    unit_price: int
    unit_cost: int
    units_sold: int
    revenue_weights: tuple[float, ...]
    cost_weights: tuple[float, ...]

    @property
    def revenue_total(self) -> float:
        return float(self.unit_price * self.units_sold)

    @property
    def cost_total(self) -> float:
        return float(self.unit_cost * self.units_sold)

    @property
    def profit_total(self) -> float:
        return self.revenue_total - self.cost_total

    @property
    def profit_margin(self) -> float:
        return _safe_ratio(self.profit_total, self.revenue_total)

    @property
    def roi_ratio(self) -> float:
        return _safe_ratio(self.profit_total, self.cost_total)

    @property
    def revenue_points(self) -> tuple[float, ...]:
        return _normalize_series(self.revenue_total, self.revenue_weights)

    @property
    def cost_points(self) -> tuple[float, ...]:
        return _normalize_series(self.cost_total, self.cost_weights)

    @property
    def profit_points(self) -> tuple[float, ...]:
        return tuple(revenue - cost for revenue, cost in zip(self.revenue_points, self.cost_points))

    @property
    def margin_bucket(self) -> str:
        return _bucket_for_margin(self.profit_margin)

    @property
    def margin_tone(self) -> BadgeTone:
        return _tone_for_margin(self.profit_margin)

    @property
    def trend_direction(self) -> str:
        first_point = self.profit_points[0] if self.profit_points else 0.0
        last_point = self.profit_points[-1] if self.profit_points else 0.0
        if last_point > first_point * 1.06:
            return "上升"
        if last_point < first_point * 0.94:
            return "回落"
        return "平稳"


class RevenueCostBarChart(ChartWidget):
    """双序列营收/成本柱状对比图。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            chart_type="bar",
            title="营收 vs 成本对比",
            labels=TREND_LABELS,
            data=(0.0,),
            unit="万",
            parent=parent,
        )
        self._revenue_values: list[float] = []
        self._cost_values: list[float] = []
        _call(self, "setObjectName", "revenueCostBarChart")

    def set_series(
        self,
        revenue_values: Sequence[float | int],
        cost_values: Sequence[float | int],
        *,
        labels: Sequence[str] | None = None,
        unit: str = "万",
    ) -> None:
        """更新图表数据。"""

        self._revenue_values = [float(value) for value in revenue_values]
        self._cost_values = [float(value) for value in cost_values]
        self._data = list(self._revenue_values)
        if labels is not None:
            self._labels = [str(label) for label in labels]
        self._unit = unit
        _call(self, "update")

    def paintEvent(self, _event: object) -> None:
        """绘制双序列柱状图。"""

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
            painter.drawRoundedRect(frame_rect, CHART_RADIUS, CHART_RADIUS)

        self._draw_title(painter, width)
        self._draw_legend(painter, width)

        if not self._revenue_values and not self._cost_values:
            self._draw_empty(painter, width, height)
            return

        plot_rect = self._plot_rect(width, height)
        values = [*self._revenue_values, *self._cost_values]
        maximum = max(values) if values else 0.0
        if maximum <= 0:
            maximum = 1.0

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

        self._draw_axis_labels(painter, plot_rect, 0.0, maximum)
        self._draw_grouped_bars(painter, plot_rect, maximum)

    def _draw_legend(self, painter: QPainter, width: int) -> None:
        """绘制顶部图例。"""

        colors = _palette()
        revenue_x = width - LEGEND_RIGHT_PADDING
        legend_y = SPACING_2XL + SPACING_XS
        painter.setPen(QPen(_qcolor(colors.text_muted)))
        if hasattr(painter, "setFont"):
            painter.setFont(QFont("Microsoft YaHei", 8, 400))

        if hasattr(painter, "setBrush") and hasattr(painter, "drawRoundedRect") and hasattr(painter, "drawText"):
            painter.setBrush(_qcolor(_series_color(0), 0.92))
            painter.drawRoundedRect(QRectF(float(revenue_x), float(legend_y), float(LEGEND_MARK_SIZE), float(LEGEND_MARK_SIZE)), 3.0, 3.0)
            painter.drawText(revenue_x + LEGEND_MARK_SIZE + SPACING_SM, legend_y + LEGEND_MARK_SIZE, "营收")

            cost_x = revenue_x + SPACING_2XL * 2 + SPACING_LG
            painter.setBrush(_qcolor(colors.text_muted, 0.78))
            painter.drawRoundedRect(QRectF(float(cost_x), float(legend_y), float(LEGEND_MARK_SIZE), float(LEGEND_MARK_SIZE)), 3.0, 3.0)
            painter.drawText(cost_x + LEGEND_MARK_SIZE + SPACING_SM, legend_y + LEGEND_MARK_SIZE, "成本")

    def _draw_grouped_bars(self, painter: QPainter, rect: QRectF, maximum: float) -> None:
        """绘制成组柱体。"""

        if not self._labels:
            return

        colors = _palette()
        slot_count = max(len(self._labels), 1)
        slot_width = rect.width() / slot_count
        revenue_width = slot_width * 0.28
        cost_width = slot_width * 0.28
        pair_gap = slot_width * 0.10
        left_padding = slot_width * 0.17
        safe_span = maximum or 1.0

        painter.setPen(getattr(Qt, "NoPen", 0))
        for index in range(slot_count):
            revenue_value = self._revenue_values[index] if index < len(self._revenue_values) else 0.0
            cost_value = self._cost_values[index] if index < len(self._cost_values) else 0.0
            slot_left = rect.left() + slot_width * index

            revenue_height = rect.height() * (revenue_value / safe_span)
            cost_height = rect.height() * (cost_value / safe_span)
            revenue_x = slot_left + left_padding
            cost_x = revenue_x + revenue_width + pair_gap

            if hasattr(painter, "setBrush") and hasattr(painter, "drawRoundedRect"):
                painter.setBrush(_qcolor(_series_color(0), 0.92))
                painter.drawRoundedRect(
                    QRectF(revenue_x, rect.bottom() - revenue_height, revenue_width, revenue_height),
                    CHART_RADIUS,
                    CHART_RADIUS,
                )

                painter.setBrush(_qcolor(colors.text_muted, 0.78))
                painter.drawRoundedRect(
                    QRectF(cost_x, rect.bottom() - cost_height, cost_width, cost_height),
                    CHART_RADIUS,
                    CHART_RADIUS,
                )


class ProfitAnalysisPage(BasePage):
    """利润分析系统主页面。"""

    default_route_id: RouteId = RouteId("profit_analysis")
    default_display_name: str = "利润分析系统"
    default_icon_name: str = "bar_chart"

    def setup_ui(self) -> None:
        """构建利润分析布局。"""

        self._records = self._mock_records()
        self._visible_records: list[ProfitProductRecord] = []
        self._selected_product_name: str | None = None
        self._syncing_selection = False

        _call(self, "setObjectName", "profitAnalysisPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#profitAnalysisPage {{
                background-color: {colors.surface_alt};
            }}
            QWidget#profitFilterToolbar {{
                background-color: {colors.surface};
                border: 1px solid {_rgba(_token('brand.primary'), 0.18)};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#profitInsightPanel {{
                background-color: {_rgba(_token('brand.primary'), 0.07)};
                border: 1px solid {_rgba(_token('brand.primary'), 0.18)};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#profitPanelTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#profitToolbarHint, QLabel#profitSelectionBody, QLabel#profitTrendNarrative {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                background: transparent;
            }}
            QLabel#profitSelectionTitle, QLabel#profitTrendTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#profitEmptyHint {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.md')};
                padding: {SPACING_XL}px 0;
            }}
            """,
        )

        page_container = PageContainer(
            title=self.display_name,
            description="围绕营收、成本、净利润与 ROI 观察商品组合表现，适合在运营复盘中快速定位高利润 SKU。",
            parent=self,
        )
        self.layout.addWidget(page_container)

        self._data_status_badge = StatusBadge("本地 Mock 数据", tone="info", parent=page_container)
        self._export_button = PrimaryButton("导出利润快照", parent=page_container, icon_text="↓")
        page_container.add_action(self._data_status_badge)
        page_container.add_action(self._export_button)

        page_container.add_widget(self._build_toolbar())

        self._tab_bar = TabBar(self)
        self._tab_bar.add_tab("概览", self._build_overview_tab())
        self._tab_bar.add_tab("商品分析", self._build_product_analysis_tab())
        self._tab_bar.add_tab("趋势报告", self._build_trend_report_tab())
        page_container.add_widget(self._tab_bar)

        _connect(getattr(self._export_button, "clicked", None), self._handle_export)
        self._apply_filters()

    def _build_toolbar(self) -> QWidget:
        """构建顶部筛选工具条。"""

        toolbar = QWidget(self)
        _call(toolbar, "setObjectName", "profitFilterToolbar")
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
        title_label = QLabel("利润筛选", title_column)
        _call(title_label, "setObjectName", "profitPanelTitle")
        helper_label = QLabel("按关键词、类目与利润分层切片利润池，联动下方图表、KPI 与趋势报告。", title_column)
        _call(helper_label, "setObjectName", "profitToolbarHint")
        _call(helper_label, "setWordWrap", True)
        title_column_layout.addWidget(title_label)
        title_column_layout.addWidget(helper_label)

        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        badge_row.setSpacing(SPACING_SM)
        self._portfolio_badge = StatusBadge("利润池待计算", tone="info", parent=toolbar)
        self._selection_badge = StatusBadge("未选择商品", tone="neutral", parent=toolbar)
        badge_row.addWidget(self._portfolio_badge)
        badge_row.addWidget(self._selection_badge)
        badge_row.addStretch(1)

        title_layout.addWidget(title_column, 1)
        title_layout.addLayout(badge_row)

        filter_row = QWidget(toolbar)
        layout = QHBoxLayout(filter_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        self._search_bar = SearchBar("搜索商品名称 / 类目", filter_row)
        self._category_filter = FilterDropdown("类目", self._category_options(), parent=filter_row)
        self._margin_filter = FilterDropdown("利润分层", ("高利润", "稳健", "待优化"), parent=filter_row)

        self._toolbar_hint = QLabel("支持按类目与利润分层过滤，图表、KPI 与表格会实时联动。", toolbar)
        _call(self._toolbar_hint, "setObjectName", "profitToolbarHint")
        _call(self._toolbar_hint, "setWordWrap", True)

        layout.addWidget(self._search_bar, 2)
        layout.addWidget(self._category_filter)
        layout.addWidget(self._margin_filter)
        root_layout.addWidget(title_row)
        root_layout.addWidget(filter_row)
        root_layout.addWidget(self._toolbar_hint)

        _connect(self._search_bar.search_changed, self._on_filters_changed)
        _connect(self._category_filter.filter_changed, self._on_filters_changed)
        _connect(self._margin_filter.filter_changed, self._on_filters_changed)
        return toolbar

    def _build_overview_tab(self) -> QWidget:
        """构建概览标签内容。"""

        tab = QWidget(self)
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        kpi_row = QWidget(tab)
        kpi_layout = QHBoxLayout(kpi_row)
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        kpi_layout.setSpacing(SPACING_LG)

        self._revenue_card = KPICard("总收入", "¥0", trend="up", percentage="0.0%", caption="过滤后营收", parent=kpi_row)
        self._cost_card = KPICard("总成本", "¥0", trend="down", percentage="0.0%", caption="采购与履约", parent=kpi_row)
        self._profit_card = KPICard("净利润", "¥0", trend="up", percentage="0.0%", caption="净收益", parent=kpi_row)
        self._margin_card = KPICard("利润率", "0.0%", trend="up", percentage="0.0%", caption="净利润 / 总收入", parent=kpi_row)

        for card in (self._revenue_card, self._cost_card, self._profit_card, self._margin_card):
            kpi_layout.addWidget(card, 1)

        chart_row = QWidget(tab)
        chart_layout = QHBoxLayout(chart_row)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.setSpacing(SPACING_LG)

        revenue_section = ContentSection("营收 / 成本柱状对比", icon="▥", parent=chart_row)
        self._revenue_cost_chart = RevenueCostBarChart(revenue_section)
        self._overview_health_badge = StatusBadge("利润健康度待计算", tone="info", parent=revenue_section)
        revenue_section.add_widget(self._overview_health_badge)
        revenue_section.add_widget(self._revenue_cost_chart)

        trend_section = ContentSection("净利润趋势折线", icon="∿", parent=chart_row)
        self._profit_trend_chart = ChartWidget(
            chart_type="line",
            title="净利润趋势",
            labels=TREND_LABELS,
            data=(0.0,),
            unit="万",
            parent=trend_section,
        )
        self._profit_trend_badge = StatusBadge("利润动能待计算", tone="info", parent=trend_section)
        trend_section.add_widget(self._profit_trend_badge)
        trend_section.add_widget(self._profit_trend_chart)

        chart_layout.addWidget(revenue_section, 1)
        chart_layout.addWidget(trend_section, 1)

        table_section = ContentSection("SKU 盈利明细", icon="▦", parent=tab)
        self._overview_table = DataTable(
            headers=("商品名", "售价", "成本", "利润", "利润率", "销量", "ROI"),
            rows=(),
            page_size=6,
            empty_text="当前筛选条件下暂无商品",
            parent=table_section,
        )
        self._overview_empty_hint = QLabel("选择任一商品后，下方标签页会同步高亮重点结论。", table_section)
        _call(self._overview_empty_hint, "setObjectName", "profitEmptyHint")
        table_section.add_widget(self._overview_empty_hint)
        table_section.add_widget(self._overview_table)

        _connect(self._overview_table.row_selected, self._on_overview_row_selected)

        layout.addWidget(kpi_row)
        layout.addWidget(chart_row)
        layout.addWidget(table_section)
        return tab

    def _build_product_analysis_tab(self) -> QWidget:
        """构建商品分析标签内容。"""

        tab = QWidget(self)
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        summary_section = ContentSection("利润分层总览", icon="◎", parent=tab)
        summary_widget = QWidget(summary_section)
        summary_layout = QVBoxLayout(summary_widget)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(SPACING_LG)

        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        badge_row.setSpacing(SPACING_SM)
        self._high_margin_badge = StatusBadge("高利润 0", tone="success", parent=summary_widget)
        self._stable_margin_badge = StatusBadge("稳健 0", tone="info", parent=summary_widget)
        self._optimize_badge = StatusBadge("待优化 0", tone="warning", parent=summary_widget)
        badge_row.addWidget(self._high_margin_badge)
        badge_row.addWidget(self._stable_margin_badge)
        badge_row.addWidget(self._optimize_badge)
        badge_row.addStretch(1)

        self._selection_panel = QFrame(summary_widget)
        _call(self._selection_panel, "setObjectName", "profitInsightPanel")
        selection_layout = QVBoxLayout(self._selection_panel)
        selection_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        selection_layout.setSpacing(SPACING_SM)

        self._selection_title = QLabel("尚未选择商品", self._selection_panel)
        _call(self._selection_title, "setObjectName", "profitSelectionTitle")
        self._selection_body = QLabel("在概览或商品分析表中点击任意行，可查看该商品的利润效率与趋势判断。", self._selection_panel)
        _call(self._selection_body, "setObjectName", "profitSelectionBody")
        _call(self._selection_body, "setWordWrap", True)

        selection_layout.addWidget(self._selection_title)
        selection_layout.addWidget(self._selection_body)

        summary_layout.addLayout(badge_row)
        summary_layout.addWidget(self._selection_panel)
        summary_section.add_widget(summary_widget)

        table_section = ContentSection("商品利润分析表", icon="▦", parent=tab)
        self._product_table = DataTable(
            headers=("商品名", "售价", "成本", "利润", "利润率", "销量", "ROI"),
            rows=(),
            page_size=8,
            empty_text="暂无利润分析数据",
            parent=table_section,
        )
        table_section.add_widget(self._product_table)
        _connect(self._product_table.row_selected, self._on_product_row_selected)

        layout.addWidget(summary_section)
        layout.addWidget(table_section)
        return tab

    def _build_trend_report_tab(self) -> QWidget:
        """构建趋势报告标签内容。"""

        tab = QWidget(self)
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        trend_section = ContentSection("趋势报告", icon="∿", parent=tab)

        trend_badge_row = QWidget(trend_section)
        trend_badge_layout = QHBoxLayout(trend_badge_row)
        trend_badge_layout.setContentsMargins(0, 0, 0, 0)
        trend_badge_layout.setSpacing(SPACING_SM)
        self._trend_scope_badge = StatusBadge("覆盖范围待计算", tone="info", parent=trend_badge_row)
        self._trend_efficiency_badge = StatusBadge("效率状态待计算", tone="neutral", parent=trend_badge_row)
        self._trend_focus_badge = StatusBadge("重点商品待计算", tone="brand", parent=trend_badge_row)
        trend_badge_layout.addWidget(self._trend_scope_badge)
        trend_badge_layout.addWidget(self._trend_efficiency_badge)
        trend_badge_layout.addWidget(self._trend_focus_badge)
        trend_badge_layout.addStretch(1)

        chart_row = QWidget(trend_section)
        chart_layout = QHBoxLayout(chart_row)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.setSpacing(SPACING_LG)

        self._trend_profit_chart = ChartWidget(
            chart_type="line",
            title="净利润趋势报告",
            labels=TREND_LABELS,
            data=(0.0,),
            unit="万",
            parent=chart_row,
        )
        self._trend_margin_chart = ChartWidget(
            chart_type="line",
            title="利润率变化",
            labels=TREND_LABELS,
            data=(0.0,),
            unit="%",
            parent=chart_row,
        )
        chart_layout.addWidget(self._trend_profit_chart, 1)
        chart_layout.addWidget(self._trend_margin_chart, 1)

        trend_section.add_widget(trend_badge_row)
        trend_section.add_widget(chart_row)

        narrative_section = ContentSection("阶段结论", icon="◌", parent=tab)
        self._trend_title = QLabel("趋势结论待生成", narrative_section)
        _call(self._trend_title, "setObjectName", "profitTrendTitle")
        self._trend_narrative = QLabel("图表会根据筛选结果自动更新，对比 7 个时间节点的营收、成本与利润率变化。", narrative_section)
        _call(self._trend_narrative, "setObjectName", "profitTrendNarrative")
        _call(self._trend_narrative, "setWordWrap", True)
        self._trend_table = DataTable(
            headers=("阶段", "营收", "成本", "利润", "利润率"),
            rows=(),
            page_size=7,
            empty_text="暂无趋势阶段数据",
            parent=narrative_section,
        )
        narrative_section.add_widget(self._trend_title)
        narrative_section.add_widget(self._trend_narrative)
        narrative_section.add_widget(self._trend_table)

        layout.addWidget(trend_section)
        layout.addWidget(narrative_section)
        return tab

    def _on_filters_changed(self, *_args: object) -> None:
        """筛选变化时刷新页面。"""

        self._apply_filters()

    def _apply_filters(self) -> None:
        """按搜索词、类目、利润分层筛选。"""

        keyword = self._search_bar.text().strip().lower()
        category = self._category_filter.current_text()
        margin_bucket = self._margin_filter.current_text()

        filtered: list[ProfitProductRecord] = []
        for record in self._records:
            haystack = f"{record.name} {record.category}".lower()
            matches_keyword = not keyword or keyword in haystack
            matches_category = category in ("", "全部") or record.category == category
            matches_margin = margin_bucket in ("", "全部") or record.margin_bucket == margin_bucket
            if matches_keyword and matches_category and matches_margin:
                filtered.append(record)

        self._visible_records = sorted(filtered, key=lambda item: item.profit_total, reverse=True)
        available_names = {record.name for record in self._visible_records}
        if self._selected_product_name not in available_names:
            self._selected_product_name = self._visible_records[0].name if self._visible_records else None

        self._refresh_kpis()
        self._refresh_tables()
        self._refresh_selection_summary(sync_tables=True)
        self._refresh_charts()
        self._refresh_status_surfaces()

    def _refresh_kpis(self) -> None:
        """刷新顶部 KPI 卡片。"""

        totals = self._aggregate_totals(self._visible_records)
        revenue = totals["revenue"]
        cost = totals["cost"]
        profit = totals["profit"]
        margin = totals["margin"]
        high_margin_count = len([record for record in self._visible_records if record.margin_bucket == "高利润"])

        self._revenue_card.set_value(_format_currency(revenue))
        self._revenue_card.set_trend("up", self._trend_percentage(revenue, revenue * 0.89))
        self._revenue_card.set_sparkline_data(self._aggregate_series(self._visible_records)["revenue"])
        _call(self._revenue_card._caption_label, "setText", f"{len(self._visible_records)} 个 SKU 贡献营收")

        self._cost_card.set_value(_format_currency(cost))
        self._cost_card.set_trend("down", self._trend_percentage(cost, cost * 1.04))
        self._cost_card.set_sparkline_data(self._aggregate_series(self._visible_records)["cost"])
        _call(self._cost_card._caption_label, "setText", "采购与履约成本合计")

        self._profit_card.set_value(_format_currency(profit))
        self._profit_card.set_trend("up" if profit > 0 else "flat", self._trend_percentage(profit, max(profit * 0.84, 1.0)))
        self._profit_card.set_sparkline_data(self._aggregate_series(self._visible_records)["profit"])
        _call(self._profit_card._caption_label, "setText", f"高利润 SKU {high_margin_count} 个")

        self._margin_card.set_value(_format_percent(margin))
        self._margin_card.set_trend("up" if margin >= STABLE_MARGIN_THRESHOLD else "flat", self._trend_percentage(margin, max(margin * 0.93, 0.001)))
        self._margin_card.set_sparkline_data([point * 100 for point in self._aggregate_series(self._visible_records)["margin"]])
        _call(self._margin_card._caption_label, "setText", "净利润 / 总收入")

    def _refresh_tables(self) -> None:
        """刷新概览表、商品表与趋势表。"""

        rows = [
            (
                record.name,
                _format_currency(record.unit_price),
                _format_currency(record.unit_cost),
                _format_currency(record.profit_total),
                _format_percent(record.profit_margin),
                f"{record.units_sold}",
                f"{record.roi_ratio:.2f}x",
            )
            for record in self._visible_records
        ]
        self._overview_table.set_rows(rows)
        self._product_table.set_rows(rows)

        aggregate = self._aggregate_series(self._visible_records)
        trend_rows = []
        for index, label in enumerate(TREND_LABELS):
            revenue_value = aggregate["revenue"][index] if index < len(aggregate["revenue"]) else 0.0
            cost_value = aggregate["cost"][index] if index < len(aggregate["cost"]) else 0.0
            profit_value = revenue_value - cost_value
            margin_value = _safe_ratio(profit_value, revenue_value)
            trend_rows.append(
                (
                    label,
                    _format_currency(revenue_value),
                    _format_currency(cost_value),
                    _format_currency(profit_value),
                    _format_percent(margin_value),
                )
            )
        self._trend_table.set_rows(trend_rows)

    def _refresh_charts(self) -> None:
        """刷新三张趋势图。"""

        aggregate = self._aggregate_series(self._visible_records)
        revenue_points = [value / 10000 for value in aggregate["revenue"]]
        cost_points = [value / 10000 for value in aggregate["cost"]]
        profit_points = [value / 10000 for value in aggregate["profit"]]
        margin_points = [value * 100 for value in aggregate["margin"]]

        self._revenue_cost_chart.set_series(revenue_points, cost_points, labels=TREND_LABELS, unit="万")
        self._profit_trend_chart.set_data(profit_points, TREND_LABELS)
        self._profit_trend_chart.set_unit("万")
        self._trend_profit_chart.set_data(profit_points, TREND_LABELS)
        self._trend_profit_chart.set_unit("万")
        self._trend_margin_chart.set_data(margin_points, TREND_LABELS)
        self._trend_margin_chart.set_unit("%")

    def _refresh_status_surfaces(self) -> None:
        """刷新 badge 与叙事文案。"""

        totals = self._aggregate_totals(self._visible_records)
        margin = totals["margin"]
        health_tone = _tone_for_margin(margin)
        high_margin_count = len([record for record in self._visible_records if record.margin_bucket == "高利润"])
        stable_count = len([record for record in self._visible_records if record.margin_bucket == "稳健"])
        optimize_count = len([record for record in self._visible_records if record.margin_bucket == "待优化"])
        selected_record = self._selected_record()

        _call(self._portfolio_badge, "setText", f"覆盖 {len(self._visible_records)} 个商品 · {_format_compact_currency(totals['profit'])} 净利润")
        self._portfolio_badge.set_tone(health_tone)

        selection_text = selected_record.name if selected_record is not None else "未选择商品"
        _call(self._selection_badge, "setText", selection_text)
        self._selection_badge.set_tone(selected_record.margin_tone if selected_record is not None else "neutral")

        _call(self._overview_health_badge, "setText", f"利润健康度：{_bucket_for_margin(margin)}")
        self._overview_health_badge.set_tone(health_tone)

        profit_series = self._aggregate_series(self._visible_records)["profit"]
        trend_tone: BadgeTone = "success" if profit_series[-1] >= profit_series[0] else "warning"
        trend_label = "净利润动能走强" if profit_series[-1] >= profit_series[0] else "净利润波动需关注"
        _call(self._profit_trend_badge, "setText", trend_label)
        self._profit_trend_badge.set_tone(trend_tone)

        _call(self._high_margin_badge, "setText", f"高利润 {high_margin_count}")
        _call(self._stable_margin_badge, "setText", f"稳健 {stable_count}")
        _call(self._optimize_badge, "setText", f"待优化 {optimize_count}")

        _call(self._trend_scope_badge, "setText", f"样本范围：{len(self._visible_records)} 个商品")
        self._trend_scope_badge.set_tone("info")
        _call(self._trend_efficiency_badge, "setText", f"整体利润率 {_format_percent(margin)}")
        self._trend_efficiency_badge.set_tone(health_tone)
        focus_text = selected_record.name if selected_record is not None else "暂无焦点商品"
        _call(self._trend_focus_badge, "setText", f"重点商品：{focus_text}")
        self._trend_focus_badge.set_tone(selected_record.margin_tone if selected_record is not None else "brand")

        if selected_record is None:
            _call(self._trend_title, "setText", "当前筛选条件下暂无可分析商品")
            _call(self._trend_narrative, "setText", "尝试放宽搜索词、类目或利润分层，系统会重新生成 7 个时间节点的趋势对比。")
            return

        _call(self._trend_title, "setText", f"{selected_record.name} 为当前利润焦点")
        _call(
            self._trend_narrative,
            "setText",
            f"{selected_record.name} 当前利润率 {_format_percent(selected_record.profit_margin)}，ROI {selected_record.roi_ratio:.2f}x，趋势判断为“{selected_record.trend_direction}”。",
        )

    def _refresh_selection_summary(self, *, sync_tables: bool) -> None:
        """刷新当前选中商品摘要。"""

        selected_record = self._selected_record()
        if selected_record is None:
            _call(self._selection_title, "setText", "当前筛选下暂无焦点商品")
            _call(self._selection_body, "setText", "可以切换类目或利润分层，重新查看商品利润结构。")
            if sync_tables:
                self._sync_table_selection(-1, source="all")
            return

        _call(self._selection_title, "setText", f"{selected_record.name} · {selected_record.margin_bucket}")
        _call(
            self._selection_body,
            "setText",
            f"售价 {_format_currency(selected_record.unit_price)}，单件成本 {_format_currency(selected_record.unit_cost)}，累计销量 {selected_record.units_sold}，累计净利润 {_format_currency(selected_record.profit_total)}。",
        )

        if not sync_tables:
            return
        selected_index = next(
            (index for index, record in enumerate(self._visible_records) if record.name == selected_record.name),
            -1,
        )
        self._sync_table_selection(selected_index, source="all")

    def _sync_table_selection(self, row_index: int, *, source: str) -> None:
        """同步两个表格的选中行。"""

        if row_index < 0:
            return

        self._syncing_selection = True
        if source != "overview":
            self._overview_table.select_absolute_row(row_index)
        if source != "product":
            self._product_table.select_absolute_row(row_index)
        self._syncing_selection = False

    def _on_overview_row_selected(self, row_index: int) -> None:
        """概览表格选中联动。"""

        self._handle_row_selection(row_index, source="overview")

    def _on_product_row_selected(self, row_index: int) -> None:
        """商品分析表格选中联动。"""

        self._handle_row_selection(row_index, source="product")

    def _handle_row_selection(self, row_index: int, *, source: str) -> None:
        """统一处理表格选中行为。"""

        if self._syncing_selection:
            return
        if not (0 <= row_index < len(self._visible_records)):
            return
        self._selected_product_name = self._visible_records[row_index].name
        self._refresh_selection_summary(sync_tables=False)
        self._refresh_status_surfaces()
        self._sync_table_selection(row_index, source=source)

    def _handle_export(self) -> None:
        """本地导出动作占位反馈。"""

        _call(self._data_status_badge, "setText", "已生成本地快照")
        self._data_status_badge.set_tone("success")
        self._export_button.set_label_text("已生成快照")
        _call(self._toolbar_hint, "setText", "当前仅生成本地快照提示，不会发起任何服务调用。")

    def _selected_record(self) -> ProfitProductRecord | None:
        """返回当前选中的商品。"""

        return next((record for record in self._visible_records if record.name == self._selected_product_name), None)

    @staticmethod
    def _aggregate_totals(records: Sequence[ProfitProductRecord]) -> dict[str, float]:
        """汇总总收入、总成本、总利润与利润率。"""

        revenue = sum(record.revenue_total for record in records)
        cost = sum(record.cost_total for record in records)
        profit = revenue - cost
        return {
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
            "margin": _safe_ratio(profit, revenue),
        }

    @staticmethod
    def _aggregate_series(records: Sequence[ProfitProductRecord]) -> dict[str, list[float]]:
        """汇总时间序列。"""

        revenue_points = [0.0 for _ in TREND_LABELS]
        cost_points = [0.0 for _ in TREND_LABELS]
        for record in records:
            for index, value in enumerate(record.revenue_points):
                if index < len(revenue_points):
                    revenue_points[index] += value
            for index, value in enumerate(record.cost_points):
                if index < len(cost_points):
                    cost_points[index] += value

        profit_points = [revenue - cost for revenue, cost in zip(revenue_points, cost_points)]
        margin_points = [_safe_ratio(profit, revenue) for revenue, profit in zip(revenue_points, profit_points)]
        return {
            "revenue": revenue_points,
            "cost": cost_points,
            "profit": profit_points,
            "margin": margin_points,
        }

    @staticmethod
    def _trend_percentage(current: float, previous: float) -> str:
        """生成环比百分比文本。"""

        if previous <= 0:
            return "0.0%"
        return f"{abs((current - previous) / previous) * 100:.1f}%"

    def _category_options(self) -> list[str]:
        """返回全部类目。"""

        return sorted({record.category for record in self._records})

    @staticmethod
    def _mock_records() -> list[ProfitProductRecord]:
        """返回页面使用的静态 mock 数据。"""

        return [
            ProfitProductRecord(
                name="无线降噪耳机 X1",
                category="3C数码",
                unit_price=399,
                unit_cost=232,
                units_sold=224,
                revenue_weights=(0.08, 0.11, 0.12, 0.14, 0.16, 0.17, 0.22),
                cost_weights=(0.09, 0.12, 0.13, 0.15, 0.15, 0.16, 0.20),
            ),
            ProfitProductRecord(
                name="智能运动手表 V4",
                category="智能穿戴",
                unit_price=599,
                unit_cost=451,
                units_sold=108,
                revenue_weights=(0.10, 0.12, 0.13, 0.13, 0.15, 0.17, 0.20),
                cost_weights=(0.11, 0.13, 0.13, 0.14, 0.15, 0.16, 0.18),
            ),
            ProfitProductRecord(
                name="便携式移动电源 20K",
                category="充电配件",
                unit_price=159,
                unit_cost=146,
                units_sold=202,
                revenue_weights=(0.12, 0.13, 0.13, 0.14, 0.15, 0.16, 0.17),
                cost_weights=(0.14, 0.14, 0.14, 0.15, 0.14, 0.15, 0.14),
            ),
            ProfitProductRecord(
                name="4K 智能家用投影仪",
                category="家居影音",
                unit_price=1299,
                unit_cost=851,
                units_sold=97,
                revenue_weights=(0.07, 0.09, 0.12, 0.14, 0.16, 0.19, 0.23),
                cost_weights=(0.08, 0.10, 0.13, 0.15, 0.16, 0.18, 0.20),
            ),
            ProfitProductRecord(
                name="桌面补光灯 Pro",
                category="数码配件",
                unit_price=279,
                unit_cost=144,
                units_sold=188,
                revenue_weights=(0.09, 0.11, 0.11, 0.14, 0.16, 0.18, 0.21),
                cost_weights=(0.10, 0.11, 0.12, 0.14, 0.16, 0.17, 0.20),
            ),
            ProfitProductRecord(
                name="磁吸车载支架 Max",
                category="车载配件",
                unit_price=89,
                unit_cost=47,
                units_sold=315,
                revenue_weights=(0.11, 0.12, 0.12, 0.13, 0.15, 0.17, 0.20),
                cost_weights=(0.12, 0.13, 0.13, 0.14, 0.15, 0.16, 0.17),
            ),
            ProfitProductRecord(
                name="AI 翻译录音笔 S2",
                category="办公数码",
                unit_price=699,
                unit_cost=512,
                units_sold=76,
                revenue_weights=(0.08, 0.10, 0.12, 0.13, 0.16, 0.18, 0.23),
                cost_weights=(0.09, 0.10, 0.12, 0.14, 0.16, 0.18, 0.21),
            ),
            ProfitProductRecord(
                name="智能香薰机 Air",
                category="家居生活",
                unit_price=239,
                unit_cost=132,
                units_sold=141,
                revenue_weights=(0.09, 0.10, 0.12, 0.14, 0.15, 0.18, 0.22),
                cost_weights=(0.10, 0.11, 0.12, 0.14, 0.15, 0.17, 0.21),
            ),
        ]


__all__ = ["ProfitAnalysisPage"]
