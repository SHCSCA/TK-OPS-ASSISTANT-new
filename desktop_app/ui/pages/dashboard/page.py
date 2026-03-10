from __future__ import annotations

# pyright: basic, reportPrivateUsage=false, reportImplicitOverride=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnusedCallResult=false, reportAttributeAccessIssue=false

"""TK-OPS 概览数据看板页面。"""

from dataclasses import dataclass
from typing import Literal, Mapping, Sequence

from ....core.qt import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components.buttons import PrimaryButton
from ...components.cards import KPICard
from ...components.charts import ChartWidget
from ...components.inputs import (
    BUTTON_HEIGHT,
    SPACING_LG,
    SPACING_MD,
    SPACING_XL,
    SPACING_2XL,
    SearchBar,
    ThemedComboBox,
    _call,
    _connect,
    _input_style,
    _token,
)
from ...components.layouts import ContentSection, PageContainer, qss_label_rule, qss_panel_rule
from ...components.tables import DataTable
from ...components.tags import StatusBadge, TagChip
from ..base_page import BasePage

TrendDirection = Literal["up", "down", "flat"]
METRICS_PER_ROW = 6
DESKTOP_PAGE_MAX_WIDTH = 1880


@dataclass(frozen=True)
class DashboardMetric:
    """单张 KPI 卡片所需的展示数据。"""

    title: str
    value: str
    trend: TrendDirection
    percentage: str
    caption: str
    sparkline: tuple[float, ...]


@dataclass(frozen=True)
class ChartDataset:
    """图表绘制使用的标签、数值与单位。"""

    labels: tuple[str, ...]
    values: tuple[float, ...]
    unit: str


@dataclass(frozen=True)
class OrderRecord:
    """最近订单表格中的一条演示记录。"""

    order_id: str
    product_name: str
    amount: str
    status: str
    order_time: str

    def to_row(self) -> list[str]:
        """转换为 DataTable 可消费的行数据。"""

        return [self.order_id, self.product_name, self.amount, self.status, self.order_time]


@dataclass(frozen=True)
class DashboardSnapshot:
    """某个统计视角下的一组完整看板演示数据。"""

    summary: str
    metrics: tuple[DashboardMetric, ...]
    trend_series: Mapping[str, ChartDataset]
    category_series: Mapping[str, ChartDataset]
    orders: tuple[OrderRecord, ...]


class DashboardPage(BasePage):
    """概览数据看板，展示经营 KPI、趋势图与最近订单。"""

    default_route_id: RouteId = RouteId("dashboard_home")
    default_display_name: str = "概览数据看板"
    default_icon_name: str = "dashboard"

    def __init__(
        self,
        route_id: RouteId | None = None,
        display_name: str | None = None,
        icon_name: str | None = None,
        parent: object | None = None,
    ) -> None:
        """初始化页面状态与演示数据。"""

        self._view_options: tuple[str, ...] = ("今日概览", "近7天概览", "近30天概览")
        self._trend_options: tuple[str, ...] = ("销售额", "订单数", "访客数", "ROAS")
        self._category_options: tuple[str, ...] = ("商品分类", "渠道来源")
        self._active_view: str = self._view_options[1]
        self._active_trend: str = self._trend_options[0]
        self._active_category: str = self._category_options[0]
        self._refresh_round: int = 0
        self._variant_cursor: dict[str, int] = {option: 0 for option in self._view_options}
        self._catalog: dict[str, tuple[DashboardSnapshot, ...]] = self._build_mock_catalog()
        self._current_orders: list[OrderRecord] = []
        self._filtered_orders: list[OrderRecord] = []
        self._metric_cards: list[KPICard] = []

        self._page_container: PageContainer | None = None
        self._search_bar: SearchBar | None = None
        self._view_combo: ThemedComboBox | None = None
        self._trend_combo: ThemedComboBox | None = None
        self._category_combo: ThemedComboBox | None = None
        self._refresh_button: PrimaryButton | None = None
        self._summary_label: QLabel | None = None
        self._selection_label: QLabel | None = None
        self._orders_hint_label: QLabel | None = None
        self._view_chip: TagChip | None = None
        self._refresh_badge: StatusBadge | None = None
        self._chart_status_badge: StatusBadge | None = None
        self._table_status_badge: StatusBadge | None = None
        self._line_meta_label: QLabel | None = None
        self._bar_meta_label: QLabel | None = None
        self._line_chart: ChartWidget | None = None
        self._bar_chart: ChartWidget | None = None
        self._orders_table: DataTable | None = None

        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        """构建完整交互式 Dashboard 布局。"""

        _call(self, "setObjectName", "dashboardPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self._page_container = PageContainer(
            title=self.display_name,
            description="围绕成交、流量与投放回报构建的交互式演示看板，帮助团队快速掌握 TikTok Shop 经营节奏。",
            max_width=DESKTOP_PAGE_MAX_WIDTH,
            parent=self,
        )

        action_bar = QFrame(self._page_container)
        _call(action_bar, "setObjectName", "dashboardActionBar")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(SPACING_XL, SPACING_MD, SPACING_XL, SPACING_MD)
        action_layout.setSpacing(SPACING_LG)

        self._search_bar = SearchBar("搜索订单号、商品名或状态")
        _call(self._search_bar, "setMinimumWidth", 260)

        self._view_combo = self._create_combo_group("统计视角", self._view_options, self._active_view, "dashboardViewCombo")
        self._refresh_button = PrimaryButton("刷新演示数据", action_bar, icon_text="↻")
        _call(self._refresh_button, "setMinimumHeight", BUTTON_HEIGHT)

        action_layout.addWidget(self._search_bar, 1)
        action_layout.addWidget(self._view_combo)
        action_layout.addStretch(1)
        action_layout.addWidget(self._refresh_button)
        self._page_container.add_widget(action_bar)

        overview_section = ContentSection("核心经营指标", icon="◉", parent=self._page_container)
        overview_meta = QFrame(overview_section)
        _call(overview_meta, "setObjectName", "dashboardInsightStrip")
        overview_meta_layout = QHBoxLayout(overview_meta)
        overview_meta_layout.setContentsMargins(SPACING_XL, SPACING_MD, SPACING_XL, SPACING_MD)
        overview_meta_layout.setSpacing(SPACING_MD)

        self._refresh_badge = StatusBadge("演示实时波动", tone="brand")
        self._view_chip = TagChip(self._active_view, tone="info")
        self._summary_label = QLabel("", overview_meta)
        _call(self._summary_label, "setObjectName", "dashboardSummaryLabel")
        _call(self._summary_label, "setWordWrap", True)

        overview_meta_layout.addWidget(self._refresh_badge)
        overview_meta_layout.addWidget(self._view_chip)
        overview_meta_layout.addWidget(self._summary_label, 1)
        overview_section.add_widget(overview_meta)

        metrics_grid = QWidget(overview_section)
        _call(metrics_grid, "setObjectName", "dashboardMetricGrid")
        metrics_grid_layout = QVBoxLayout(metrics_grid)
        metrics_grid_layout.setContentsMargins(0, 0, 0, 0)
        metrics_grid_layout.setSpacing(SPACING_MD)

        placeholders = self._default_metric_placeholders()
        for row_start in range(0, len(placeholders), METRICS_PER_ROW):
            metrics_row = QWidget(metrics_grid)
            _call(metrics_row, "setObjectName", "dashboardMetricRow")
            metrics_layout = QHBoxLayout(metrics_row)
            metrics_layout.setContentsMargins(0, 0, 0, 0)
            metrics_layout.setSpacing(SPACING_MD)

            for metric in placeholders[row_start : row_start + METRICS_PER_ROW]:
                card = KPICard(
                    title=metric.title,
                    value=metric.value,
                    trend=metric.trend,
                    percentage=metric.percentage,
                    caption=metric.caption,
                    sparkline_data=metric.sparkline,
                )
                _call(card, "setMinimumWidth", 200)
                metrics_layout.addWidget(card, 1)
                self._metric_cards.append(card)

            metrics_grid_layout.addWidget(metrics_row)
        overview_section.add_widget(metrics_grid)

        chart_section = ContentSection("经营趋势与分类销售", icon="◌", parent=self._page_container)
        chart_controls = QFrame(chart_section)
        _call(chart_controls, "setObjectName", "dashboardFilterRow")
        chart_controls_layout = QHBoxLayout(chart_controls)
        chart_controls_layout.setContentsMargins(SPACING_XL, SPACING_MD, SPACING_XL, SPACING_MD)
        chart_controls_layout.setSpacing(SPACING_LG)

        self._chart_status_badge = StatusBadge("销售额 × 商品分类", tone="info")
        self._trend_combo = self._create_combo_group("趋势指标", self._trend_options, self._active_trend, "dashboardTrendCombo")
        self._category_combo = self._create_combo_group("分类视角", self._category_options, self._active_category, "dashboardCategoryCombo")

        chart_controls_layout.addWidget(self._chart_status_badge)
        chart_controls_layout.addWidget(self._trend_combo)
        chart_controls_layout.addWidget(self._category_combo)
        chart_controls_layout.addStretch(1)
        chart_section.add_widget(chart_controls)

        charts_row = QWidget(chart_section)
        _call(charts_row, "setObjectName", "dashboardChartsRow")
        charts_layout = QHBoxLayout(charts_row)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(SPACING_XL)

        line_panel, self._line_meta_label = self._create_chart_panel("7天趋势", charts_row)
        self._line_chart = ChartWidget(
            chart_type="line",
            title="7天趋势",
            labels=("周一", "周二", "周三", "周四", "周五", "周六", "周日"),
            data=(1.0, 1.2, 1.1, 1.4, 1.5, 1.7, 1.8),
            unit="万",
        )
        self._attach_chart_widget(line_panel, self._line_chart)

        bar_panel, self._bar_meta_label = self._create_chart_panel("分类销售", charts_row)
        self._bar_chart = ChartWidget(
            chart_type="bar",
            title="分类销售",
            labels=("女装", "家居", "美妆", "配饰", "食品"),
            data=(1.0, 0.8, 0.6, 0.5, 0.4),
            unit="万",
        )
        self._attach_chart_widget(bar_panel, self._bar_chart)

        charts_layout.addWidget(line_panel, 3)
        charts_layout.addWidget(bar_panel, 2)
        chart_section.add_widget(charts_row)

        orders_section = ContentSection("最近订单", icon="◎", parent=self._page_container)
        orders_meta = QFrame(orders_section)
        _call(orders_meta, "setObjectName", "dashboardOrderMeta")
        orders_meta_layout = QHBoxLayout(orders_meta)
        orders_meta_layout.setContentsMargins(SPACING_XL, SPACING_MD, SPACING_XL, SPACING_MD)
        orders_meta_layout.setSpacing(SPACING_MD)

        self._table_status_badge = StatusBadge("订单流正常", tone="success")
        self._selection_label = QLabel("点击表格行可查看演示订单焦点信息。", orders_meta)
        self._orders_hint_label = QLabel("支持关键词搜索，表头支持排序。", orders_meta)
        _call(self._selection_label, "setObjectName", "dashboardSelectionLabel")
        _call(self._orders_hint_label, "setObjectName", "dashboardHintLabel")
        _call(self._selection_label, "setWordWrap", True)
        _call(self._orders_hint_label, "setWordWrap", True)

        orders_meta_layout.addWidget(self._table_status_badge)
        orders_meta_layout.addWidget(self._selection_label, 1)
        orders_meta_layout.addWidget(self._orders_hint_label, 1)
        orders_section.add_widget(orders_meta)

        self._orders_table = DataTable(
            headers=["订单号", "商品", "金额", "状态", "时间"],
            rows=[],
            page_size=6,
            empty_text="暂无匹配订单",
        )
        orders_section.add_widget(self._orders_table)

        self._page_container.add_widget(overview_section)
        self._page_container.add_widget(chart_section)
        self._page_container.add_widget(orders_section)
        self.layout.addWidget(self._page_container)

        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#dashboardPage {{
                background-color: {_token('surface.primary')};
            }}
            QWidget#dashboardMetricGrid,
            QWidget#dashboardMetricRow,
            QWidget#dashboardChartsRow,
            QWidget#dashboardSelectionLabel {{
                background: transparent;
            }}
            {qss_panel_rule('QFrame#dashboardActionBar')}
            {qss_panel_rule('QFrame#dashboardChartPanel')}
            {qss_panel_rule('QFrame#dashboardFilterRow', variant='subtle')}
            {qss_panel_rule('QFrame#dashboardOrderMeta', variant='subtle')}
            {qss_panel_rule('QFrame#dashboardInsightStrip', variant='subtle')}
            {qss_label_rule('QLabel#dashboardSummaryLabel', tone='muted', size_token='font.size.sm')}
            {qss_label_rule('QLabel#dashboardPanelMeta', tone='muted', size_token='font.size.sm')}
            {qss_label_rule('QLabel#dashboardHintLabel', tone='muted', size_token='font.size.sm')}
            {qss_label_rule('QLabel#dashboardSelectionLabel', size_token='font.size.sm', weight_token='font.weight.semibold')}
            {qss_label_rule('QLabel#dashboardPanelTitle', size_token='font.size.lg', weight_token='font.weight.bold')}
            QComboBox#dashboardViewCombo,
            QComboBox#dashboardTrendCombo,
            QComboBox#dashboardCategoryCombo {{
                {_input_style(min_height=BUTTON_HEIGHT, padding_vertical=SPACING_MD)}
                padding-right: {SPACING_2XL}px;
                min-width: 140px;
            }}
            """,
        )

        self._wire_events()
        self._refresh_mock_data(cycle_variant=False)

    def on_activated(self) -> None:
        """页面激活时刷新一轮演示数据。"""

        self._refresh_mock_data(cycle_variant=True)

    def _wire_events(self) -> None:
        """连接搜索、筛选与表格交互信号。"""

        if self._search_bar is not None:
            _connect(self._search_bar.search_changed, self._apply_order_filter)
        if self._view_combo is not None:
            _connect(getattr(self._view_combo.combo_box, "currentTextChanged", None), self._on_view_changed)
        if self._trend_combo is not None:
            _connect(getattr(self._trend_combo.combo_box, "currentTextChanged", None), self._on_trend_changed)
        if self._category_combo is not None:
            _connect(getattr(self._category_combo.combo_box, "currentTextChanged", None), self._on_category_changed)
        if self._refresh_button is not None:
            _connect(getattr(self._refresh_button, "clicked", None), self._trigger_manual_refresh)
        if self._orders_table is not None:
            _connect(self._orders_table.row_selected, self._on_order_selected)
            _connect(self._orders_table.row_double_clicked, self._on_order_double_clicked)

    def _on_view_changed(self, text: str) -> None:
        """切换统计视角后更新全部展示。"""

        if text in self._catalog:
            self._active_view = text
            self._refresh_mock_data(cycle_variant=False)

    def _on_trend_changed(self, text: str) -> None:
        """切换趋势图指标后仅刷新折线图。"""

        if text in self._trend_options:
            self._active_trend = text
            self._update_charts(self._active_snapshot())

    def _on_category_changed(self, text: str) -> None:
        """切换分类销售视角后仅刷新柱状图。"""

        if text in self._category_options:
            self._active_category = text
            self._update_charts(self._active_snapshot())

    def _trigger_manual_refresh(self) -> None:
        """手动触发演示数据轮播。"""

        self._refresh_mock_data(cycle_variant=True)

    def _refresh_mock_data(self, *, cycle_variant: bool) -> None:
        """根据当前视角刷新 KPI、图表与订单列表。"""

        if cycle_variant:
            snapshots = self._catalog[self._active_view]
            next_index = (self._variant_cursor[self._active_view] + 1) % len(snapshots)
            self._variant_cursor[self._active_view] = next_index
            self._refresh_round += 1

        snapshot = self._active_snapshot()
        self._update_header_meta(snapshot)
        self._update_metrics(snapshot)
        self._update_charts(snapshot)
        self._current_orders = list(snapshot.orders)
        self._apply_order_filter(self._search_text())

    def _active_snapshot(self) -> DashboardSnapshot:
        """读取当前视角对应的活动快照。"""

        snapshots = self._catalog[self._active_view]
        return snapshots[self._variant_cursor[self._active_view]]

    def _update_header_meta(self, snapshot: DashboardSnapshot) -> None:
        """刷新顶部摘要、标签与刷新状态。"""

        if self._view_chip is not None:
            self._view_chip.set_text(self._active_view)
            self._view_chip.set_tone("info")
        if self._summary_label is not None:
            _call(self._summary_label, "setText", snapshot.summary)
        if self._refresh_badge is not None:
            badge_text = f"第 {self._refresh_round + 1} 轮演示刷新"
            _call(self._refresh_badge, "setText", badge_text)
            self._refresh_badge.set_tone("brand")

    def _update_metrics(self, snapshot: DashboardSnapshot) -> None:
        """将快照中的指标写入 KPI 卡片。"""

        for card, metric in zip(self._metric_cards, snapshot.metrics):
            card.set_title(metric.title)
            card.set_value(metric.value)
            card.set_trend(metric.trend, metric.percentage)
            card.set_sparkline_data(metric.sparkline)
            _call(getattr(card, "_caption_label", None), "setText", metric.caption)

    def _update_charts(self, snapshot: DashboardSnapshot) -> None:
        """刷新趋势图与分类销售图。"""

        trend_dataset = snapshot.trend_series[self._active_trend]
        category_dataset = snapshot.category_series[self._active_category]

        if self._line_chart is not None:
            self._line_chart.set_data(trend_dataset.values, trend_dataset.labels)
            self._line_chart.set_unit(trend_dataset.unit)
        if self._bar_chart is not None:
            self._bar_chart.set_data(category_dataset.values, category_dataset.labels)
            self._bar_chart.set_unit(category_dataset.unit)
        if self._line_meta_label is not None:
            _call(
                self._line_meta_label,
                "setText",
                f"当前查看：{self._active_trend}｜最近 7 天走势与节奏变化（单位：{trend_dataset.unit or '指数'}）",
            )
        if self._bar_meta_label is not None:
            _call(
                self._bar_meta_label,
                "setText",
                f"当前查看：{self._active_category}｜按结构拆分销售贡献（单位：{category_dataset.unit or '指数'}）",
            )
        if self._chart_status_badge is not None:
            _call(self._chart_status_badge, "setText", f"{self._active_trend} × {self._active_category}")
            self._chart_status_badge.set_tone("info")

    def _apply_order_filter(self, keyword: str) -> None:
        """根据搜索关键词筛选最近订单。"""

        normalized = keyword.strip().lower()
        if not normalized:
            self._filtered_orders = list(self._current_orders)
        else:
            self._filtered_orders = [
                order
                for order in self._current_orders
                if normalized in order.order_id.lower()
                or normalized in order.product_name.lower()
                or normalized in order.status.lower()
                or normalized in order.order_time.lower()
            ]

        if self._orders_table is not None:
            self._orders_table.set_rows([order.to_row() for order in self._filtered_orders])

        if self._table_status_badge is not None:
            if self._filtered_orders:
                _call(self._table_status_badge, "setText", f"已匹配 {len(self._filtered_orders)} 笔订单")
                self._table_status_badge.set_tone("success")
            else:
                _call(self._table_status_badge, "setText", "暂无匹配结果")
                self._table_status_badge.set_tone("warning")

        if self._selection_label is not None:
            if self._filtered_orders:
                first_order = self._filtered_orders[0]
                _call(
                    self._selection_label,
                    "setText",
                    f"焦点订单：{first_order.order_id}｜{first_order.product_name}｜{first_order.status}",
                )
            else:
                _call(self._selection_label, "setText", "没有找到符合关键词的订单，请尝试更短的搜索词。")
        if self._orders_hint_label is not None:
            if normalized:
                _call(
                    self._orders_hint_label,
                    "setText",
                    f"当前筛选：{keyword.strip()}｜已联动 {len(self._filtered_orders)} 笔结果，表头支持排序。",
                )
            else:
                _call(self._orders_hint_label, "setText", "支持关键词搜索，表头支持排序。")

    def _on_order_selected(self, row_index: int) -> None:
        """响应表格行选中事件。"""

        if not (0 <= row_index < len(self._filtered_orders)):
            return
        order = self._filtered_orders[row_index]
        if self._selection_label is not None:
            _call(
                self._selection_label,
                "setText",
                f"已选中：{order.order_id}｜{order.product_name}｜金额 {order.amount}｜{order.status}",
            )

    def _on_order_double_clicked(self, row_index: int) -> None:
        """响应表格行双击事件，强化交互反馈。"""

        if not (0 <= row_index < len(self._filtered_orders)):
            return
        order = self._filtered_orders[row_index]
        if self._orders_hint_label is not None:
            _call(
                self._orders_hint_label,
                "setText",
                f"已打开演示详情：{order.order_id} 于 {order.order_time} 产生，状态为“{order.status}”。",
            )
        if self._table_status_badge is not None:
            _call(self._table_status_badge, "setText", "已打开模拟详情")
            self._table_status_badge.set_tone("info")

    def _search_text(self) -> str:
        """安全读取搜索框文本。"""

        return self._search_bar.text() if self._search_bar is not None else ""

    def _create_combo_group(
        self,
        label_text: str,
        items: Sequence[str],
        current_text: str,
        object_name: str,
    ) -> ThemedComboBox:
        """创建统一风格的筛选下拉控件。"""

        combo_group = ThemedComboBox(label=label_text, items=items)
        _call(combo_group.combo_box, "setObjectName", object_name)
        _call(combo_group.combo_box, "setCurrentText", current_text)
        _call(combo_group.combo_box, "setStyleSheet", _input_style(min_height=BUTTON_HEIGHT, padding_vertical=SPACING_MD))
        _call(combo_group.combo_box, "setMinimumWidth", 144)
        return combo_group

    def _create_chart_panel(self, title: str, parent: QWidget) -> tuple[QFrame, QLabel]:
        """创建图表面板容器。"""

        panel = QFrame(parent)
        _call(panel, "setObjectName", "dashboardChartPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_MD)

        title_label = QLabel(title, panel)
        meta_label = QLabel("", panel)
        _call(title_label, "setObjectName", "dashboardPanelTitle")
        _call(meta_label, "setObjectName", "dashboardPanelMeta")
        _call(meta_label, "setWordWrap", True)

        layout.addWidget(title_label)
        layout.addWidget(meta_label)
        setattr(panel, "_panel_layout", layout)
        return panel, meta_label

    @staticmethod
    def _attach_chart_widget(panel: QWidget, chart_widget: ChartWidget) -> None:
        """将图表挂载到图表面板尾部。"""

        panel_layout = getattr(panel, "_panel_layout", None)
        add_widget = getattr(panel_layout, "addWidget", None)
        if callable(add_widget):
            add_widget(chart_widget)

    @staticmethod
    def _default_metric_placeholders() -> tuple[DashboardMetric, ...]:
        """提供初次渲染时的占位指标，避免空白页面。"""

        return (
            DashboardMetric("总销售额", "¥0", "up", "+0.0%", "等待演示数据", (0.8, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5)),
            DashboardMetric("订单数", "0", "up", "+0.0%", "等待演示数据", (1.0, 1.0, 1.1, 1.0, 1.2, 1.1, 1.3)),
            DashboardMetric("访客数", "0", "up", "+0.0%", "等待演示数据", (0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2)),
            DashboardMetric("转化率", "0%", "flat", "+0.0%", "等待演示数据", (0.6, 0.6, 0.7, 0.8, 0.8, 0.9, 0.9)),
            DashboardMetric("GMV", "¥0", "up", "+0.0%", "等待演示数据", (1.2, 1.1, 1.3, 1.4, 1.4, 1.5, 1.7)),
            DashboardMetric("ROAS", "0.00", "flat", "+0.0%", "等待演示数据", (0.9, 0.9, 1.0, 1.0, 1.1, 1.1, 1.2)),
        )

    @staticmethod
    def _build_mock_catalog() -> dict[str, tuple[DashboardSnapshot, ...]]:
        """构造 Dashboard 使用的全部静态演示数据。"""

        weekdays = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
        return {
            "今日概览": (
                DashboardSnapshot(
                    summary="今日短视频转化稳定走高，女装与家居贡献了主要成交，广告投放回本速度快于上午场。",
                    metrics=(
                        DashboardMetric("总销售额", "¥128,640", "up", "+12.8%", "较昨日提升", (8.2, 9.1, 9.6, 10.8, 11.3, 12.1, 12.9)),
                        DashboardMetric("订单数", "426", "up", "+9.4%", "支付订单走高", (50, 52, 56, 60, 61, 65, 69)),
                        DashboardMetric("访客数", "18,920", "up", "+6.1%", "自然流量回暖", (2100, 2250, 2380, 2500, 2650, 2780, 2910)),
                        DashboardMetric("转化率", "4.82%", "up", "+0.7%", "加购承接更顺畅", (4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.82)),
                        DashboardMetric("GMV", "¥156,300", "up", "+11.6%", "客单价继续抬升", (10.5, 11.2, 11.8, 12.6, 13.4, 14.1, 15.2)),
                        DashboardMetric("ROAS", "3.68", "up", "+0.22", "投放回报向好", (2.8, 3.0, 3.1, 3.3, 3.4, 3.5, 3.68)),
                    ),
                    trend_series={
                        "销售额": ChartDataset(weekdays, (12.4, 13.2, 13.0, 15.6, 16.4, 18.2, 19.6), "万"),
                        "订单数": ChartDataset(weekdays, (42, 45, 44, 53, 56, 61, 67), "单"),
                        "访客数": ChartDataset(weekdays, (1.68, 1.74, 1.71, 1.82, 1.88, 1.93, 2.01), "万"),
                        "ROAS": ChartDataset(weekdays, (2.9, 3.0, 3.0, 3.2, 3.4, 3.5, 3.7), "倍"),
                    },
                    category_series={
                        "商品分类": ChartDataset(("女装", "家居", "美妆", "配饰", "食品"), (5.8, 4.2, 3.1, 2.4, 1.8), "万"),
                        "渠道来源": ChartDataset(("短视频", "短视频", "达人", "投流", "自然"), (6.3, 4.6, 3.3, 2.5, 1.7), "万"),
                    },
                    orders=(
                        OrderRecord("TK20260308001", "春季修身短外套", "¥399", "已付款", "今天 09:18"),
                        OrderRecord("TK20260308007", "北欧香薰加湿器", "¥289", "待发货", "今天 09:42"),
                        OrderRecord("TK20260308011", "柔光持妆粉底液", "¥188", "已完成", "今天 10:06"),
                        OrderRecord("TK20260308015", "高腰直筒牛仔裤", "¥259", "退款中", "今天 10:25"),
                        OrderRecord("TK20260308019", "短视频福利组合装", "¥516", "已付款", "今天 10:51"),
                        OrderRecord("TK20260308022", "厨房多功能收纳架", "¥329", "已完成", "今天 11:13"),
                    ),
                ),
                DashboardSnapshot(
                    summary="午后活动流量进一步放大，爆款女装拉高整体销售额，退款率依旧处于可控区间。",
                    metrics=(
                        DashboardMetric("总销售额", "¥136,980", "up", "+15.1%", "活动承接顺畅", (8.8, 9.6, 10.2, 11.4, 12.0, 12.8, 13.7)),
                        DashboardMetric("订单数", "451", "up", "+11.0%", "短视频成交加速", (52, 54, 58, 61, 64, 68, 73)),
                        DashboardMetric("访客数", "19,480", "up", "+7.3%", "短视频导流增强", (2150, 2280, 2420, 2560, 2700, 2840, 2990)),
                        DashboardMetric("转化率", "4.95%", "up", "+0.9%", "加购到支付更稳定", (4.1, 4.2, 4.4, 4.6, 4.7, 4.8, 4.95)),
                        DashboardMetric("GMV", "¥163,540", "up", "+13.0%", "高客单占比提升", (10.8, 11.7, 12.0, 12.8, 13.8, 14.9, 15.9)),
                        DashboardMetric("ROAS", "3.81", "up", "+0.31", "投放效率改善", (2.9, 3.0, 3.2, 3.3, 3.5, 3.6, 3.81)),
                    ),
                    trend_series={
                        "销售额": ChartDataset(weekdays, (13.1, 13.8, 14.2, 16.3, 17.5, 19.1, 20.4), "万"),
                        "订单数": ChartDataset(weekdays, (44, 47, 50, 56, 59, 64, 70), "单"),
                        "访客数": ChartDataset(weekdays, (1.72, 1.77, 1.83, 1.88, 1.94, 2.0, 2.08), "万"),
                        "ROAS": ChartDataset(weekdays, (3.0, 3.1, 3.2, 3.4, 3.5, 3.7, 3.8), "倍"),
                    },
                    category_series={
                        "商品分类": ChartDataset(("女装", "家居", "美妆", "配饰", "食品"), (6.2, 4.4, 3.3, 2.5, 1.9), "万"),
                        "渠道来源": ChartDataset(("短视频", "短视频", "达人", "投流", "自然"), (6.8, 4.8, 3.5, 2.7, 1.9), "万"),
                    },
                    orders=(
                        OrderRecord("TK20260308029", "凉感针织防晒衫", "¥219", "已付款", "今天 11:26"),
                        OrderRecord("TK20260308031", "多功能懒人沙发毯", "¥179", "已完成", "今天 11:39"),
                        OrderRecord("TK20260308035", "玫瑰精华修护套组", "¥469", "待发货", "今天 11:52"),
                        OrderRecord("TK20260308039", "法式收腰连衣裙", "¥329", "已付款", "今天 12:03"),
                        OrderRecord("TK20260308041", "家用便携榨汁杯", "¥149", "已完成", "今天 12:11"),
                        OrderRecord("TK20260308044", "主播同款轻量托特包", "¥369", "退款中", "今天 12:26"),
                    ),
                ),
            ),
            "近7天概览": (
                DashboardSnapshot(
                    summary="近 7 天整体成交结构健康，短视频持续贡献主力 GMV，内容流量带来的新客转化正在走强。",
                    metrics=(
                        DashboardMetric("总销售额", "¥892,400", "up", "+18.6%", "较上周提升", (72, 74, 77, 80, 84, 87, 89)),
                        DashboardMetric("订单数", "3,284", "up", "+14.2%", "订单密度持续提升", (420, 430, 448, 461, 472, 489, 505)),
                        DashboardMetric("访客数", "126,800", "up", "+9.8%", "拉新效率稳定", (15.2, 15.8, 16.1, 16.9, 17.3, 17.8, 18.4)),
                        DashboardMetric("转化率", "5.03%", "up", "+0.4%", "转化稳定抬升", (4.6, 4.7, 4.8, 4.9, 4.95, 5.0, 5.03)),
                        DashboardMetric("GMV", "¥1,086,700", "up", "+16.9%", "高客单新品放量", (88, 91, 95, 99, 103, 106, 109)),
                        DashboardMetric("ROAS", "4.12", "up", "+0.38", "投流回报更优", (3.4, 3.5, 3.6, 3.8, 3.9, 4.0, 4.12)),
                    ),
                    trend_series={
                        "销售额": ChartDataset(weekdays, (11.2, 12.6, 12.3, 13.8, 14.4, 15.6, 16.8), "万"),
                        "订单数": ChartDataset(weekdays, (380, 402, 395, 428, 441, 466, 489), "单"),
                        "访客数": ChartDataset(weekdays, (1.52, 1.58, 1.55, 1.66, 1.72, 1.79, 1.86), "万"),
                        "ROAS": ChartDataset(weekdays, (3.5, 3.6, 3.6, 3.8, 3.9, 4.0, 4.1), "倍"),
                    },
                    category_series={
                        "商品分类": ChartDataset(("女装", "家居", "美妆", "配饰", "食品"), (34.6, 25.2, 19.7, 11.9, 8.8), "万"),
                        "渠道来源": ChartDataset(("短视频", "短视频", "达人", "投流", "自然"), (38.1, 28.6, 18.4, 12.7, 8.4), "万"),
                    },
                    orders=(
                        OrderRecord("TK20260307091", "轻氧感防晒套装", "¥299", "已完成", "03-07 19:24"),
                        OrderRecord("TK20260307108", "新中式垂感半裙", "¥359", "已付款", "03-07 20:06"),
                        OrderRecord("TK20260307124", "厨房抽拉收纳盒", "¥126", "待发货", "03-07 20:18"),
                        OrderRecord("TK20260307131", "奶油风抱枕四件套", "¥208", "已完成", "03-07 21:04"),
                        OrderRecord("TK20260307145", "焕亮修护精华", "¥239", "退款中", "03-07 21:33"),
                        OrderRecord("TK20260307159", "短视频同款阔腿裤", "¥279", "已付款", "03-07 22:12"),
                    ),
                ),
                DashboardSnapshot(
                    summary="近 7 天热点内容持续发酵，短视频与达人内容配合拉升转化，广告回收周期进一步缩短。",
                    metrics=(
                        DashboardMetric("总销售额", "¥928,260", "up", "+21.4%", "内容投放效率上扬", (74, 76, 79, 82, 85, 89, 93)),
                        DashboardMetric("订单数", "3,416", "up", "+17.6%", "订单峰值更高", (424, 438, 452, 468, 481, 497, 516)),
                        DashboardMetric("访客数", "131,200", "up", "+11.5%", "短视频引流更强", (15.4, 15.9, 16.4, 17.1, 17.6, 18.1, 18.9)),
                        DashboardMetric("转化率", "5.18%", "up", "+0.5%", "成交链路更顺", (4.7, 4.8, 4.9, 5.0, 5.05, 5.1, 5.18)),
                        DashboardMetric("GMV", "¥1,131,900", "up", "+19.2%", "高客单组合包走强", (90, 93, 97, 101, 105, 109, 113)),
                        DashboardMetric("ROAS", "4.28", "up", "+0.46", "投流回收更快", (3.6, 3.7, 3.8, 4.0, 4.1, 4.2, 4.28)),
                    ),
                    trend_series={
                        "销售额": ChartDataset(weekdays, (11.6, 12.9, 13.5, 14.1, 15.2, 16.2, 17.4), "万"),
                        "订单数": ChartDataset(weekdays, (392, 410, 426, 437, 458, 479, 502), "单"),
                        "访客数": ChartDataset(weekdays, (1.55, 1.61, 1.68, 1.72, 1.79, 1.84, 1.92), "万"),
                        "ROAS": ChartDataset(weekdays, (3.6, 3.7, 3.8, 4.0, 4.1, 4.2, 4.3), "倍"),
                    },
                    category_series={
                        "商品分类": ChartDataset(("女装", "家居", "美妆", "配饰", "食品"), (36.8, 26.4, 20.6, 12.3, 9.1), "万"),
                        "渠道来源": ChartDataset(("短视频", "短视频", "达人", "投流", "自然"), (39.4, 30.1, 18.9, 13.6, 8.8), "万"),
                    },
                    orders=(
                        OrderRecord("TK20260306182", "城市轻奢腋下包", "¥318", "已付款", "03-06 17:08"),
                        OrderRecord("TK20260306194", "高弹修形牛仔裤", "¥286", "已完成", "03-06 18:19"),
                        OrderRecord("TK20260306217", "卧室氛围小夜灯", "¥96", "待发货", "03-06 18:44"),
                        OrderRecord("TK20260306233", "修护焕肤面膜礼盒", "¥269", "已完成", "03-06 19:02"),
                        OrderRecord("TK20260306248", "防风轻量冲锋衣", "¥459", "退款中", "03-06 19:26"),
                        OrderRecord("TK20260306260", "主播推荐早餐机", "¥228", "已付款", "03-06 20:11"),
                    ),
                ),
            ),
            "近30天概览": (
                DashboardSnapshot(
                    summary="近 30 天整体生意节奏稳中有升，内容矩阵带来的新增访客扩大了品牌搜索与短视频转化的协同效应。",
                    metrics=(
                        DashboardMetric("总销售额", "¥3,684,000", "up", "+26.3%", "较上月明显增长", (252, 266, 279, 288, 301, 316, 329)),
                        DashboardMetric("订单数", "12,940", "up", "+20.7%", "爆款稳定放量", (1540, 1602, 1664, 1711, 1768, 1826, 1889)),
                        DashboardMetric("访客数", "468,300", "up", "+18.2%", "多渠道拉新协同", (52, 54, 56, 59, 61, 63, 65)),
                        DashboardMetric("转化率", "5.31%", "up", "+0.6%", "承接效率更高", (4.8, 4.9, 5.0, 5.1, 5.15, 5.22, 5.31)),
                        DashboardMetric("GMV", "¥4,426,800", "up", "+24.1%", "组合包与高单价商品贡献提升", (302, 316, 330, 344, 359, 372, 388)),
                        DashboardMetric("ROAS", "4.46", "up", "+0.52", "整体投放更稳", (3.7, 3.8, 3.9, 4.1, 4.2, 4.3, 4.46)),
                    ),
                    trend_series={
                        "销售额": ChartDataset(weekdays, (42.4, 43.8, 45.6, 47.2, 48.9, 50.1, 52.4), "万"),
                        "订单数": ChartDataset(weekdays, (1620, 1675, 1710, 1768, 1824, 1879, 1932), "单"),
                        "访客数": ChartDataset(weekdays, (5.8, 6.0, 6.2, 6.4, 6.6, 6.9, 7.1), "万"),
                        "ROAS": ChartDataset(weekdays, (3.8, 3.9, 4.0, 4.1, 4.2, 4.3, 4.5), "倍"),
                    },
                    category_series={
                        "商品分类": ChartDataset(("女装", "家居", "美妆", "配饰", "食品"), (126, 94, 68, 42, 31), "万"),
                        "渠道来源": ChartDataset(("短视频", "短视频", "达人", "投流", "自然"), (134, 101, 72, 47, 33), "万"),
                    },
                    orders=(
                        OrderRecord("TK20260228110", "显瘦小香风外套", "¥429", "已完成", "02-28 18:42"),
                        OrderRecord("TK20260228134", "奶油风桌面收纳柜", "¥238", "已完成", "02-28 19:11"),
                        OrderRecord("TK20260228158", "焕亮精华安瓶", "¥199", "待发货", "02-28 20:05"),
                        OrderRecord("TK20260228177", "轻运动束脚卫裤", "¥269", "已付款", "02-28 21:17"),
                        OrderRecord("TK20260228194", "电热早餐锅二合一", "¥369", "退款中", "02-28 21:49"),
                        OrderRecord("TK20260228208", "达人同款托特包", "¥309", "已完成", "02-28 22:03"),
                    ),
                ),
                DashboardSnapshot(
                    summary="近 30 天品牌词搜索与短视频转化形成正循环，内容爆点持续为高客单新品蓄水，整体 ROI 呈现健康增长。",
                    metrics=(
                        DashboardMetric("总销售额", "¥3,812,700", "up", "+29.1%", "月度节奏进一步上扬", (258, 271, 284, 296, 308, 324, 341)),
                        DashboardMetric("订单数", "13,402", "up", "+23.4%", "订单峰值再抬升", (1582, 1636, 1698, 1754, 1812, 1886, 1964)),
                        DashboardMetric("访客数", "482,100", "up", "+20.1%", "新客与复购同步增长", (53, 55, 57, 60, 62, 64, 67)),
                        DashboardMetric("转化率", "5.44%", "up", "+0.8%", "短视频承接能力增强", (4.9, 5.0, 5.1, 5.2, 5.3, 5.35, 5.44)),
                        DashboardMetric("GMV", "¥4,590,300", "up", "+27.0%", "爆品结构更优", (309, 323, 337, 351, 366, 382, 397)),
                        DashboardMetric("ROAS", "4.63", "up", "+0.65", "投放与自然流量协同更强", (3.9, 4.0, 4.1, 4.2, 4.3, 4.5, 4.63)),
                    ),
                    trend_series={
                        "销售额": ChartDataset(weekdays, (43.7, 45.1, 46.8, 48.4, 50.2, 52.0, 54.1), "万"),
                        "订单数": ChartDataset(weekdays, (1660, 1708, 1769, 1828, 1894, 1960, 2021), "单"),
                        "访客数": ChartDataset(weekdays, (5.9, 6.1, 6.3, 6.5, 6.8, 7.0, 7.3), "万"),
                        "ROAS": ChartDataset(weekdays, (4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6), "倍"),
                    },
                    category_series={
                        "商品分类": ChartDataset(("女装", "家居", "美妆", "配饰", "食品"), (132, 97, 72, 44, 34), "万"),
                        "渠道来源": ChartDataset(("短视频", "短视频", "达人", "投流", "自然"), (139, 106, 74, 49, 35), "万"),
                    },
                    orders=(
                        OrderRecord("TK20260227143", "法式立领衬衫", "¥239", "已完成", "02-27 17:36"),
                        OrderRecord("TK20260227159", "静音香薰冷风扇", "¥458", "已付款", "02-27 18:04"),
                        OrderRecord("TK20260227188", "胶原修护精华乳", "¥219", "待发货", "02-27 19:23"),
                        OrderRecord("TK20260227203", "通勤显瘦阔腿裤", "¥298", "已完成", "02-27 20:01"),
                        OrderRecord("TK20260227220", "主播推荐电煮锅", "¥188", "退款中", "02-27 20:47"),
                        OrderRecord("TK20260227244", "云感轻盈羽绒马甲", "¥499", "已付款", "02-27 21:15"),
                    ),
                ),
            ),
        }
