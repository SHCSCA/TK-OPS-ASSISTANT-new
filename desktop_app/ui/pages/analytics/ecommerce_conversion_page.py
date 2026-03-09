# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportArgumentType=false, reportCallIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportPrivateUsage=false, reportImplicitOverride=false, reportGeneralTypeIssues=false

from __future__ import annotations

"""电商转化页面。"""

from dataclasses import dataclass
from typing import Final, Sequence

from ....core.qt import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    ChartWidget,
    ContentSection,
    DataTable,
    DistributionChart,
    FilterDropdown,
    FunnelChart,
    KPICard,
    MiniSparkline,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    SentimentGauge,
    StatusBadge,
    TabBar,
    TagChip,
    TrendComparison,
)
from ...components.inputs import (
    RADIUS_LG,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ..base_page import BasePage


def _rgba(hex_color: str, alpha: float) -> str:
    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _format_compact(value: int | float, currency: bool = False) -> str:
    amount = float(value)
    prefix = "¥" if currency else ""
    if abs(amount) >= 100000000:
        return f"{prefix}{amount / 100000000:.2f}亿"
    if abs(amount) >= 10000:
        return f"{prefix}{amount / 10000:.1f}万"
    return f"{prefix}{amount:,.0f}"


def _format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _trend(value: float) -> str:
    if value > 0.008:
        return "up"
    if value < -0.008:
        return "down"
    return "flat"


@dataclass(frozen=True)
class ProductConversionRecord:
    name: str
    category: str
    source: str
    clicks: int
    orders: int
    revenue: int
    add_to_cart: int
    views: int
    refunds: int
    region: str
    cvr_points: tuple[float, ...]
    roi_points: tuple[float, ...]

    @property
    def cvr(self) -> float:
        return _safe_ratio(self.orders, self.clicks)

    @property
    def aov(self) -> float:
        return _safe_ratio(self.revenue, self.orders)

    @property
    def roi(self) -> float:
        ad_cost = self.revenue * 0.31
        return _safe_ratio(self.revenue, ad_cost)

    @property
    def abandon_rate(self) -> float:
        return 1.0 - _safe_ratio(self.orders, self.add_to_cart)


PRODUCT_HEADERS: Final[tuple[str, ...]] = ("商品", "曝光", "点击", "下单", "销售额", "CVR", "ROI")
ABANDON_HEADERS: Final[tuple[str, ...]] = ("商品", "加购", "未下单", "流失率", "原因")
CREW_HEADERS: Final[tuple[str, ...]] = ("类型", "指标", "本周", "上周", "变化")
RANGE_OPTIONS: Final[tuple[str, ...]] = ("本周", "近 14 天", "近 30 天")
CATEGORY_LABELS: Final[tuple[str, ...]] = ("服饰", "家居", "美妆", "数码", "运动", "配饰")
SOURCE_LABELS: Final[tuple[str, ...]] = ("推荐页", "搜索", "主页", "达人合作")
TREND_LABELS: Final[tuple[str, ...]] = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
TAB_LABELS: Final[tuple[str, ...]] = ("转化总览", "商品诊断", "流失分析")

PRODUCTS: Final[tuple[ProductConversionRecord, ...]] = (
    ProductConversionRecord("保暖摇粒绒外套", "服饰", "推荐页", 58200, 6420, 2164000, 8440, 842000, 220, "美国", (0.084, 0.088, 0.091, 0.095, 0.101, 0.106, 0.110), (2.8, 2.9, 3.0, 3.2, 3.3, 3.5, 3.6)),
    ProductConversionRecord("香氛蜡烛礼盒", "家居", "搜索", 49800, 5610, 1823000, 7340, 721000, 180, "英国", (0.079, 0.082, 0.085, 0.088, 0.092, 0.096, 0.101), (2.4, 2.5, 2.6, 2.8, 2.9, 3.0, 3.1)),
    ProductConversionRecord("轻薄羽绒背心", "服饰", "推荐页", 45100, 4980, 1761000, 6420, 684000, 162, "加拿大", (0.075, 0.079, 0.082, 0.086, 0.090, 0.094, 0.098), (2.5, 2.6, 2.8, 2.9, 3.0, 3.1, 3.2)),
    ProductConversionRecord("桌面收纳转盘", "家居", "主页", 43600, 4560, 1498000, 5980, 636000, 141, "德国", (0.071, 0.074, 0.078, 0.082, 0.085, 0.089, 0.092), (2.2, 2.3, 2.4, 2.5, 2.7, 2.8, 2.9)),
    ProductConversionRecord("丝绒唇釉套装", "美妆", "达人合作", 41200, 4790, 1689000, 6380, 592000, 173, "法国", (0.082, 0.085, 0.089, 0.094, 0.098, 0.103, 0.108), (2.6, 2.7, 2.9, 3.0, 3.1, 3.3, 3.4)),
    ProductConversionRecord("运动护膝双支装", "运动", "搜索", 38900, 4210, 1216000, 5590, 548000, 131, "美国", (0.073, 0.076, 0.079, 0.083, 0.087, 0.091, 0.095), (2.1, 2.2, 2.3, 2.5, 2.6, 2.7, 2.8)),
    ProductConversionRecord("蓝牙降噪耳机", "数码", "推荐页", 36600, 3820, 1974000, 5010, 530000, 109, "日本", (0.069, 0.072, 0.076, 0.081, 0.084, 0.088, 0.092), (2.9, 3.0, 3.1, 3.2, 3.4, 3.5, 3.6)),
    ProductConversionRecord("珍珠通勤项链", "配饰", "主页", 34100, 3610, 1085000, 4620, 486000, 98, "西班牙", (0.067, 0.071, 0.075, 0.078, 0.082, 0.086, 0.090), (2.0, 2.1, 2.2, 2.3, 2.5, 2.6, 2.7)),
    ProductConversionRecord("瑜伽弹力长裤", "运动", "推荐页", 32600, 3340, 1028000, 4490, 461000, 87, "澳大利亚", (0.064, 0.068, 0.071, 0.075, 0.079, 0.082, 0.086), (1.9, 2.0, 2.1, 2.2, 2.3, 2.5, 2.6)),
    ProductConversionRecord("复古咖啡杯套组", "家居", "搜索", 31200, 3180, 926000, 4180, 432000, 77, "韩国", (0.063, 0.066, 0.069, 0.073, 0.076, 0.080, 0.084), (1.8, 1.9, 2.0, 2.1, 2.2, 2.4, 2.5)),
    ProductConversionRecord("冬日绒面拖鞋", "服饰", "达人合作", 29600, 2870, 764000, 3920, 404000, 72, "美国", (0.059, 0.063, 0.066, 0.070, 0.074, 0.078, 0.081), (1.7, 1.8, 1.9, 2.0, 2.1, 2.3, 2.4)),
    ProductConversionRecord("便携补光自拍灯", "数码", "推荐页", 28400, 2760, 882000, 3740, 381000, 68, "新加坡", (0.058, 0.061, 0.065, 0.069, 0.073, 0.076, 0.080), (1.8, 1.9, 2.0, 2.1, 2.2, 2.4, 2.5)),
)

FUNNEL_BY_RANGE: Final[dict[str, tuple[int, int, int, int, int]]] = {
    "本周": (10800000, 682000, 184000, 86200, 73400),
    "近 14 天": (20600000, 1282000, 338000, 152000, 130400),
    "近 30 天": (43200000, 2714000, 718000, 326000, 279500),
}

LAST_WEEK_FUNNEL: Final[dict[str, tuple[int, int, int, int, int]]] = {
    "本周": (9840000, 614000, 161000, 74800, 64200),
    "近 14 天": (18820000, 1171000, 299000, 136400, 116900),
    "近 30 天": (40800000, 2526000, 671000, 302000, 258700),
}

GMV_SERIES: Final[dict[str, tuple[int, ...]]] = {
    "本周": (182000, 208000, 236000, 248000, 272000, 318000, 341000),
    "近 14 天": (164000, 172000, 185000, 194000, 202000, 218000, 229000),
    "近 30 天": (148000, 154000, 162000, 171000, 176000, 183000, 195000),
}

GMV_COMPARE_SERIES: Final[dict[str, tuple[int, ...]]] = {
    "本周": (156000, 172000, 196000, 214000, 231000, 259000, 276000),
    "近 14 天": (151000, 159000, 167000, 175000, 183000, 191000, 204000),
    "近 30 天": (136000, 142000, 149000, 156000, 162000, 168000, 174000),
}

CATEGORY_VALUES: Final[dict[str, tuple[int, int, int, int, int, int]]] = {
    "本周": (32, 19, 16, 13, 11, 9),
    "近 14 天": (30, 20, 17, 14, 11, 8),
    "近 30 天": (28, 21, 18, 14, 11, 8),
}

ABANDON_REASONS: Final[tuple[str, ...]] = (
    "运费门槛感知偏高",
    "结算页优惠信息不明确",
    "库存焦虑不足，催单触发偏弱",
    "尺码/规格选择步骤偏多",
    "支付页加载时长偏长",
)
RECOVERY_PLAYBOOKS: Final[tuple[tuple[str, str, tuple[int, ...]], ...]] = (
    ("运费说明前置", "在加购弹层提前展示包邮门槛，缓解价格敏感。", (18, 21, 24, 28, 31, 36, 42)),
    ("优惠券临门一脚", "对高客单商品在结算前触发 10 分钟限时券。", (15, 18, 22, 25, 29, 33, 39)),
    ("规格选择瘦身", "将尺码与颜色优先级前置，减少反复切换。", (12, 14, 17, 20, 24, 27, 31)),
    ("支付页性能优化", "移动端支付页首屏加载压缩到 1.5 秒以内。", (10, 12, 15, 18, 22, 25, 29)),
)
SOURCE_INSIGHTS: Final[tuple[tuple[str, str, str], ...]] = (
    ("推荐页", "高 GMV", "适合承接爆款短视频，建议保持高频迭代封面素材。"),
    ("搜索", "高转化", "功能型标题对点击后转化帮助明显，适合稳定收割。"),
    ("主页", "高复购", "老客回访多，适合上新合集与组合包。"),
    ("达人合作", "高客单", "需要更强的优惠承接，适合联动专属券。"),
)
EXECUTION_RHYTHMS: Final[tuple[tuple[str, str, str, tuple[int, ...]], ...]] = (
    ("周一补货提醒", "服饰与家居主推", "建议以搜索词扩量为主，承接工作周需求。", (18, 20, 23, 27, 29, 31, 34)),
    ("周三内容加推", "美妆与数码主推", "适合在晚高峰追加二次分发与限时券。", (22, 25, 29, 33, 36, 40, 44)),
    ("周末套组冲量", "组合包与礼盒主推", "建议放大高客单套组，强化包邮门槛说明。", (26, 30, 34, 37, 41, 46, 52)),
)
CHECKOUT_CHECKLIST: Final[tuple[tuple[str, str], ...]] = (
    ("运费说明前置", "加购弹层与结算页同时展示包邮门槛。"),
    ("优惠券显性化", "在支付按钮上方露出可用优惠券数量。"),
    ("库存提醒增强", "对热门 SKU 追加实时库存文案。"),
    ("支付方式收敛", "移动端优先显示 2 个高频支付方式。"),
)
RETARGETING_MODULES: Final[tuple[tuple[str, str, tuple[int, ...]], ...]] = (
    ("加购未下单再营销", "针对高意向用户二次触发限时优惠。", (14, 17, 20, 24, 27, 31, 35)),
    ("搜索高意向回捞", "对搜索点击但未加购人群投放对比型素材。", (11, 14, 17, 20, 24, 28, 32)),
    ("主页回访催单", "对回访用户突出库存与组合包优势。", (10, 12, 15, 18, 21, 25, 29)),
)


class EcommerceConversionPage(BasePage):
    """电商转化页面。"""

    default_route_id: RouteId = RouteId("ecommerce_conversion")
    default_display_name: str = "电商转化"
    default_icon_name: str = "shopping_bag"

    def setup_ui(self) -> None:
        self._selected_range = RANGE_OPTIONS[0]
        self._selected_category = "全部"
        self._selected_source = "全部"
        self._search_keyword = ""
        self._selected_index = 0

        self._range_filter: FilterDropdown | None = None
        self._category_filter: FilterDropdown | None = None
        self._source_filter: FilterDropdown | None = None
        self._search_bar: SearchBar | None = None
        self._tab_bar: TabBar | None = None
        self._funnel_chart: FunnelChart | None = None
        self._product_table: DataTable | None = None
        self._abandon_table: DataTable | None = None
        self._crew_table: DataTable | None = None
        self._category_chart: DistributionChart | None = None
        self._trend_comparison: TrendComparison | None = None
        self._gmv_chart: ChartWidget | None = None
        self._roi_gauge: SentimentGauge | None = None
        self._selected_name_label: QLabel | None = None
        self._selected_meta_label: QLabel | None = None
        self._selected_summary_label: QLabel | None = None
        self._selected_badges: list[StatusBadge] = []
        self._selected_metric_labels: dict[str, QLabel] = {}
        self._recovery_value_labels: list[QLabel] = []
        self._recovery_sparklines: list[MiniSparkline] = []
        self._source_insight_labels: list[QLabel] = []
        self._kpi_cards: dict[str, KPICard] = {}

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        _call(self, "setObjectName", "ecommerceConversionPage")

        self._page_container = PageContainer(
            title="电商转化",
            description="围绕曝光、点击、加购、下单与支付，快速诊断 TikTok Shop 商品漏斗效率与流失根因。",
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._build_header_actions()
        self._page_container.add_widget(self._build_toolbar())
        self._page_container.add_widget(self._build_kpis())
        self._page_container.add_widget(self._build_workspace())
        self._apply_page_styles()
        self._bind_interactions()
        self._refresh_all_views()

    def _build_header_actions(self) -> None:
        self._page_container.add_action(TagChip("本周 vs 上周", tone="brand", parent=self))
        self._page_container.add_action(TagChip("支付转化跟踪", tone="info", parent=self))
        self._page_container.add_action(StatusBadge("支付成功率高于均值", tone="success", parent=self))
        self._page_container.add_action(SecondaryButton("刷新归因", parent=self))
        self._page_container.add_action(PrimaryButton("导出转化诊断", parent=self))

    def _build_toolbar(self) -> QWidget:
        panel = QFrame(self)
        _call(panel, "setObjectName", "conversionToolbar")
        root = QVBoxLayout(panel)
        root.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        root.setSpacing(SPACING_LG)

        title_row = QWidget(panel)
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_MD)

        title_column = QWidget(title_row)
        title_column_layout = QVBoxLayout(title_column)
        title_column_layout.setContentsMargins(0, 0, 0, 0)
        title_column_layout.setSpacing(SPACING_XS)
        title_label = QLabel("转化筛选", title_column)
        _call(title_label, "setObjectName", "conversionPanelTitle")
        helper_label = QLabel("按时间、类目与流量入口切片漏斗效率，同步联动商品诊断与流失分析。", title_column)
        _call(helper_label, "setObjectName", "conversionSubtleText")
        _call(helper_label, "setWordWrap", True)
        title_column_layout.addWidget(title_label)
        title_column_layout.addWidget(helper_label)

        title_layout.addWidget(title_column, 1)
        title_layout.addWidget(StatusBadge("漏斗联动已开启", tone="success", parent=title_row))

        row = QWidget(panel)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACING_LG)

        self._search_bar = SearchBar("搜索商品、类目、地区或素材入口...", row)
        self._range_filter = FilterDropdown("时间范围", RANGE_OPTIONS, include_all=False, parent=row)
        self._category_filter = FilterDropdown("类目", CATEGORY_LABELS, parent=row)
        self._source_filter = FilterDropdown("流量入口", SOURCE_LABELS, parent=row)
        row_layout.addWidget(self._search_bar, 3)
        row_layout.addWidget(self._range_filter, 1)
        row_layout.addWidget(self._category_filter, 1)
        row_layout.addWidget(self._source_filter, 1)

        tip_row = QWidget(panel)
        tip_layout = QHBoxLayout(tip_row)
        tip_layout.setContentsMargins(0, 0, 0, 0)
        tip_layout.setSpacing(SPACING_MD)
        tip_layout.addWidget(TagChip("推荐页 GMV 占比 42%", tone="success", parent=tip_row))
        tip_layout.addWidget(TagChip("加购流失集中在运费敏感商品", tone="warning", parent=tip_row))
        tip_layout.addWidget(TagChip("服饰类 ROI 回升", tone="info", parent=tip_row))
        tip_layout.addStretch(1)
        tip_layout.addWidget(SecondaryButton("重置筛选", parent=tip_row))
        tip_layout.addWidget(PrimaryButton("同步投放策略", parent=tip_row))

        root.addWidget(title_row)
        root.addWidget(row)
        root.addWidget(tip_row)
        return panel

    def _build_kpis(self) -> QWidget:
        wrapper = QWidget(self)
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        for title in ("总GMV", "转化率", "客单价", "ROI"):
            card = KPICard(title=title, value="-", trend="up", percentage="+0.0%", caption="本周对比上周", sparkline_data=(0, 0, 0, 0, 0, 0, 0), parent=wrapper)
            self._kpi_cards[title] = card
            layout.addWidget(card, 1)
        return wrapper

    def _build_workspace(self) -> QWidget:
        shell = QWidget(self)
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        layout.addWidget(self._build_left_column(), 3)
        layout.addWidget(self._build_right_column(), 2)
        return shell

    def _build_left_column(self) -> QWidget:
        column = QWidget(self)
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        layout.addWidget(self._build_tabs())
        layout.addWidget(self._build_products_section())
        layout.addWidget(self._build_abandon_section())
        layout.addWidget(self._build_recovery_section())
        layout.addWidget(self._build_execution_rhythm_section())
        layout.addWidget(self._build_checkout_checklist_section())
        layout.addWidget(self._build_retargeting_section())
        return column

    def _build_right_column(self) -> QWidget:
        column = QWidget(self)
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        layout.addWidget(self._build_selection_section())
        layout.addWidget(self._build_category_section())
        layout.addWidget(self._build_compare_section())
        layout.addWidget(self._build_source_insights_section())
        return column

    def _build_tabs(self) -> QWidget:
        section = ContentSection("漏斗视图", icon="◬", parent=self)
        self._tab_bar = TabBar(section)
        self._tab_bar.add_tab(TAB_LABELS[0], self._build_overview_tab())
        self._tab_bar.add_tab(TAB_LABELS[1], self._build_diagnosis_tab())
        self._tab_bar.add_tab(TAB_LABELS[2], self._build_loss_tab())
        section.add_widget(self._tab_bar)
        return section

    def _build_overview_tab(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        self._funnel_chart = FunnelChart(page, tuple(float(value) for value in FUNNEL_BY_RANGE[self._selected_range]))
        layout.addWidget(self._funnel_chart)
        self._gmv_chart = ChartWidget(chart_type="bar", title="本周日 GMV 走势", labels=TREND_LABELS, data=GMV_SERIES[self._selected_range], unit="万", parent=page)
        layout.addWidget(self._gmv_chart)
        return page

    def _build_diagnosis_tab(self) -> QWidget:
        page = QWidget(self)
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        trend_section = ContentSection("关键指标对比", icon="≈", parent=page)
        self._trend_comparison = TrendComparison(
            trend_section,
            labels=TREND_LABELS,
            current_values=tuple(float(value) for value in GMV_SERIES[self._selected_range]),
            compare_values=tuple(float(value) for value in GMV_COMPARE_SERIES[self._selected_range]),
            current_name="本周",
            compare_name="上周",
        )
        trend_section.add_widget(self._trend_comparison)
        layout.addWidget(trend_section, 2)

        gauge_section = ContentSection("转化情绪", icon="◠", parent=page)
        hint = QLabel("综合 ROI、CVR 与支付率给出当前转化温度。", gauge_section)
        _call(hint, "setObjectName", "conversionSubtleText")
        self._roi_gauge = SentimentGauge(gauge_section, 0.36)
        gauge_section.add_widget(hint)
        gauge_section.add_widget(self._roi_gauge)
        layout.addWidget(gauge_section, 1)
        return page

    def _build_loss_tab(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        for name, values in (("结算页优惠刺激", (24, 28, 31, 36, 39, 44, 48)), ("运费解释强化", (18, 22, 24, 29, 33, 37, 41)), ("支付按钮样式优化", (16, 19, 21, 25, 30, 34, 38))):
            item = QFrame(page)
            _call(item, "setObjectName", "conversionMiniCard")
            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            item_layout.setSpacing(SPACING_SM)
            label = QLabel(name, item)
            value = QLabel(f"预计减少流失 {_format_percent(max(values) / 100.0)}", item)
            _call(label, "setObjectName", "conversionMetricTitle")
            _call(value, "setObjectName", "conversionMetricValue")
            item_layout.addWidget(label)
            item_layout.addWidget(MiniSparkline(values, item))
            item_layout.addWidget(value)
            layout.addWidget(item)
        return page

    def _build_products_section(self) -> QWidget:
        section = ContentSection("商品转化表现", icon="▤", parent=self)
        self._product_table = DataTable(headers=PRODUCT_HEADERS, rows=(), page_size=8, empty_text="暂无商品数据", parent=section)
        section.add_widget(self._product_table)
        return section

    def _build_abandon_section(self) -> QWidget:
        section = ContentSection("弃购分析", icon="⚠", parent=self)
        self._abandon_table = DataTable(headers=ABANDON_HEADERS, rows=(), page_size=6, empty_text="暂无弃购数据", parent=section)
        section.add_widget(self._abandon_table)
        return section

    def _build_recovery_section(self) -> QWidget:
        section = ContentSection("弃购挽回策略", icon="↺", parent=self)
        for title, summary, values in RECOVERY_PLAYBOOKS:
            card = QFrame(section)
            _call(card, "setObjectName", "conversionRecoveryCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            label = QLabel(title, card)
            summary_label = QLabel(summary, card)
            value_label = QLabel(f"预计挽回 {_format_percent(max(values) / 100.0)}", card)
            _call(label, "setObjectName", "conversionMetricTitle")
            _call(summary_label, "setObjectName", "conversionSubtleText")
            _call(summary_label, "setWordWrap", True)
            _call(value_label, "setObjectName", "conversionMetricValue")
            sparkline = MiniSparkline(values, card)
            self._recovery_sparklines.append(sparkline)
            self._recovery_value_labels.append(value_label)
            layout.addWidget(label)
            layout.addWidget(summary_label)
            layout.addWidget(sparkline)
            layout.addWidget(value_label)
            section.add_widget(card)
        return section

    def _build_execution_rhythm_section(self) -> QWidget:
        section = ContentSection("执行节奏建议", icon="◎", parent=self)
        for title, focus, summary, values in EXECUTION_RHYTHMS:
            card = QFrame(section)
            _call(card, "setObjectName", "conversionRhythmCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            title_label = QLabel(title, card)
            focus_label = QLabel(focus, card)
            summary_label = QLabel(summary, card)
            chart = ChartWidget(chart_type="line", title="预估带动下单量", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="单", parent=card)
            _call(title_label, "setObjectName", "conversionMetricTitle")
            _call(focus_label, "setObjectName", "conversionMetricValue")
            _call(summary_label, "setObjectName", "conversionSubtleText")
            _call(summary_label, "setWordWrap", True)
            layout.addWidget(title_label)
            layout.addWidget(focus_label)
            layout.addWidget(summary_label)
            layout.addWidget(chart)
            section.add_widget(card)
        return section

    def _build_checkout_checklist_section(self) -> QWidget:
        section = ContentSection("支付页优化清单", icon="✓", parent=self)
        for title, summary in CHECKOUT_CHECKLIST:
            row = QFrame(section)
            _call(row, "setObjectName", "conversionChecklistCard")
            layout = QHBoxLayout(row)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            layout.addWidget(StatusBadge("待执行", tone="warning", parent=row))
            title_label = QLabel(title, row)
            body_label = QLabel(summary, row)
            _call(title_label, "setObjectName", "conversionMetricTitle")
            _call(body_label, "setObjectName", "conversionSubtleText")
            layout.addWidget(title_label)
            layout.addStretch(1)
            layout.addWidget(body_label)
            section.add_widget(row)
        return section

    def _build_retargeting_section(self) -> QWidget:
        section = ContentSection("再营销模块", icon="◔", parent=self)
        for title, summary, values in RETARGETING_MODULES:
            card = QFrame(section)
            _call(card, "setObjectName", "conversionRetargetingCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            title_label = QLabel(title, card)
            body_label = QLabel(summary, card)
            chart = ChartWidget(chart_type="line", title="预计回收订单", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="单", parent=card)
            _call(title_label, "setObjectName", "conversionMetricTitle")
            _call(body_label, "setObjectName", "conversionSubtleText")
            _call(body_label, "setWordWrap", True)
            layout.addWidget(title_label)
            layout.addWidget(body_label)
            layout.addWidget(chart)
            section.add_widget(card)
        return section

    def _build_selection_section(self) -> QWidget:
        section = ContentSection("商品诊断卡", icon="✦", parent=self)
        card = QFrame(section)
        _call(card, "setObjectName", "conversionDetailCard")
        root = QVBoxLayout(card)
        root.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        root.setSpacing(SPACING_LG)
        self._selected_name_label = QLabel("等待选择商品", card)
        self._selected_meta_label = QLabel("", card)
        self._selected_summary_label = QLabel("选择表格中的商品后，此处会展示转化与流失重点。", card)
        _call(self._selected_name_label, "setObjectName", "conversionSelectionTitle")
        _call(self._selected_meta_label, "setObjectName", "conversionSubtleText")
        _call(self._selected_summary_label, "setObjectName", "conversionSubtleText")
        _call(self._selected_summary_label, "setWordWrap", True)
        root.addWidget(self._selected_name_label)
        root.addWidget(self._selected_meta_label)
        root.addWidget(self._selected_summary_label)

        badge_row = QWidget(card)
        badge_layout = QHBoxLayout(badge_row)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(SPACING_SM)
        for text, tone in (("推荐页", "success"), ("服饰", "brand"), ("美国", "info")):
            badge = StatusBadge(text, tone=tone, parent=badge_row)
            self._selected_badges.append(badge)
            badge_layout.addWidget(badge)
        badge_layout.addStretch(1)
        root.addWidget(badge_row)

        for metric in ("CVR", "ROI", "客单价", "弃购率"):
            block = QFrame(card)
            _call(block, "setObjectName", "conversionMetricCard")
            block_layout = QHBoxLayout(block)
            block_layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            block_layout.setSpacing(SPACING_SM)
            label = QLabel(metric, block)
            value = QLabel("-", block)
            _call(label, "setObjectName", "conversionMetricTitle")
            _call(value, "setObjectName", "conversionMetricValue")
            block_layout.addWidget(label)
            block_layout.addStretch(1)
            block_layout.addWidget(value)
            self._selected_metric_labels[metric] = value
            root.addWidget(block)

        section.add_widget(card)
        return section

    def _build_category_section(self) -> QWidget:
        section = ContentSection("类目拆分", icon="▥", parent=self)
        self._category_chart = DistributionChart(section, tuple(zip(CATEGORY_LABELS, CATEGORY_VALUES[self._selected_range])))
        section.add_widget(self._category_chart)
        return section

    def _build_compare_section(self) -> QWidget:
        section = ContentSection("本周 vs 上周速览", icon="◎", parent=self)
        self._crew_table = DataTable(headers=CREW_HEADERS, rows=(), page_size=6, empty_text="暂无对比数据", parent=section)
        section.add_widget(self._crew_table)
        return section

    def _build_source_insights_section(self) -> QWidget:
        section = ContentSection("流量入口洞察", icon="◌", parent=self)
        for source, flag, summary in SOURCE_INSIGHTS:
            card = QFrame(section)
            _call(card, "setObjectName", "conversionSourceInsightCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_XS)
            title_row = QWidget(card)
            title_layout = QHBoxLayout(title_row)
            title_layout.setContentsMargins(0, 0, 0, 0)
            title_layout.setSpacing(SPACING_SM)
            title = QLabel(source, title_row)
            badge = StatusBadge(flag, tone="success" if "高" in flag else "info", parent=title_row)
            _call(title, "setObjectName", "conversionMetricTitle")
            title_layout.addWidget(title)
            title_layout.addStretch(1)
            title_layout.addWidget(badge)
            body = QLabel(summary, card)
            _call(body, "setObjectName", "conversionSubtleText")
            _call(body, "setWordWrap", True)
            self._source_insight_labels.append(body)
            layout.addWidget(title_row)
            layout.addWidget(body)
            section.add_widget(card)
        return section

    def _bind_interactions(self) -> None:
        if self._search_bar is not None:
            _connect(self._search_bar.search_changed, self._handle_search_changed)
        if self._range_filter is not None:
            _connect(self._range_filter.filter_changed, self._handle_range_changed)
        if self._category_filter is not None:
            _connect(self._category_filter.filter_changed, self._handle_category_changed)
        if self._source_filter is not None:
            _connect(self._source_filter.filter_changed, self._handle_source_changed)
        if self._product_table is not None:
            _connect(self._product_table.row_selected, self._handle_row_selected)
            _connect(self._product_table.row_double_clicked, self._handle_row_selected)

    def _handle_search_changed(self, text: str) -> None:
        self._search_keyword = text.strip()
        self._selected_index = 0
        self._refresh_all_views()

    def _handle_range_changed(self, text: str) -> None:
        if text in RANGE_OPTIONS:
            self._selected_range = text
            self._refresh_all_views()

    def _handle_category_changed(self, text: str) -> None:
        self._selected_category = text
        self._selected_index = 0
        self._refresh_all_views()

    def _handle_source_changed(self, text: str) -> None:
        self._selected_source = text
        self._selected_index = 0
        self._refresh_all_views()

    def _handle_row_selected(self, index: int) -> None:
        self._selected_index = index
        self._refresh_selection()

    def _filtered_products(self) -> list[ProductConversionRecord]:
        records: list[ProductConversionRecord] = []
        for record in PRODUCTS:
            searchable = " ".join((record.name, record.category, record.source, record.region))
            if self._search_keyword and self._search_keyword.lower() not in searchable.lower():
                continue
            if self._selected_category not in {"", "全部"} and record.category != self._selected_category:
                continue
            if self._selected_source not in {"", "全部"} and record.source != self._selected_source:
                continue
            records.append(record)
        return records

    def _kpi_payload(self, records: Sequence[ProductConversionRecord]) -> dict[str, tuple[str, float, Sequence[float | int]]]:
        total_gmv = sum(record.revenue for record in records)
        total_orders = sum(record.orders for record in records)
        total_aov = _safe_ratio(total_gmv, total_orders)
        total_roi = _safe_ratio(total_gmv, total_gmv * 0.31)
        current = FUNNEL_BY_RANGE[self._selected_range]
        compare = LAST_WEEK_FUNNEL[self._selected_range]
        cvr = _safe_ratio(current[-1], current[1])
        prev_cvr = _safe_ratio(compare[-1], compare[1])
        return {
            "总GMV": (_format_compact(total_gmv, True), _safe_ratio(current[-1] - compare[-1], compare[-1]), tuple(value / 10000 for value in GMV_SERIES[self._selected_range])),
            "转化率": (_format_percent(cvr), cvr - prev_cvr, tuple(record.cvr * 100 for record in records[:7] or [ProductConversionRecord("", "", "", 1, 0, 0, 1, 1, 0, "", (0.0,), (0.0,))])),
            "客单价": (_format_compact(total_aov, True), _safe_ratio(total_aov - 286.0, 286.0), tuple(record.aov for record in records[:7] or [ProductConversionRecord("", "", "", 1, 1, 1, 1, 1, 0, "", (0.0,), (0.0,))])),
            "ROI": (f"{total_roi:.2f}x", _safe_ratio(total_roi - 2.84, 2.84), tuple(record.roi for record in records[:7] or [ProductConversionRecord("", "", "", 1, 1, 1, 1, 1, 0, "", (0.0,), (0.0,))])),
        }

    def _product_rows(self, records: Sequence[ProductConversionRecord]) -> list[list[object]]:
        return [[record.name, _format_compact(record.views), _format_compact(record.clicks), _format_compact(record.orders), _format_compact(record.revenue, True), _format_percent(record.cvr), f"{record.roi:.2f}x"] for record in records]

    def _abandon_rows(self, records: Sequence[ProductConversionRecord]) -> list[list[object]]:
        rows: list[list[object]] = []
        for index, record in enumerate(records[:8]):
            lost = max(record.add_to_cart - record.orders, 0)
            rows.append([record.name, _format_compact(record.add_to_cart), _format_compact(lost), _format_percent(record.abandon_rate), ABANDON_REASONS[index % len(ABANDON_REASONS)]])
        return rows

    def _crew_rows(self, records: Sequence[ProductConversionRecord]) -> list[list[object]]:
        gmv = sum(record.revenue for record in records)
        orders = sum(record.orders for record in records)
        current = FUNNEL_BY_RANGE[self._selected_range]
        last = LAST_WEEK_FUNNEL[self._selected_range]
        compare_items = (
            ("GMV", "销售额", gmv, sum(last) * 0.05),
            ("效率", "支付转化率", _safe_ratio(current[-1], current[1]), _safe_ratio(last[-1], last[1])),
            ("效率", "点击率", _safe_ratio(current[1], current[0]), _safe_ratio(last[1], last[0])),
            ("效率", "加购率", _safe_ratio(current[2], current[1]), _safe_ratio(last[2], last[1])),
            ("成本", "ROI", _safe_ratio(gmv, gmv * 0.31), 2.84),
            ("订单", "总下单", orders, last[3]),
        )
        rows: list[list[object]] = []
        for group, metric, current_value, last_value in compare_items:
            if metric == "销售额":
                current_text = _format_compact(current_value, True)
                last_text = _format_compact(last_value, True)
            elif metric == "总下单":
                current_text = _format_compact(current_value)
                last_text = _format_compact(last_value)
            elif metric == "ROI":
                current_text = f"{float(current_value):.2f}x"
                last_text = f"{float(last_value):.2f}x"
            else:
                current_text = _format_percent(float(current_value))
                last_text = _format_percent(float(last_value))
            delta = _safe_ratio(float(current_value) - float(last_value), float(last_value) if float(last_value) != 0 else 1.0)
            rows.append([group, metric, current_text, last_text, f"{delta * 100:+.1f}%"])
        return rows

    def _selected_record(self) -> ProductConversionRecord | None:
        records = self._filtered_products()
        if not records:
            return None
        self._selected_index = max(0, min(self._selected_index, len(records) - 1))
        return records[self._selected_index]

    def _refresh_all_views(self) -> None:
        records = self._filtered_products()
        payload = self._kpi_payload(records)
        for title, card in self._kpi_cards.items():
            value, delta, spark = payload[title]
            card.set_value(value)
            card.set_trend(_trend(delta), f"{delta * 100:+.1f}%")
            card.set_sparkline_data(spark)
        if self._funnel_chart is not None:
            self._funnel_chart.set_stages(tuple(float(value) for value in FUNNEL_BY_RANGE[self._selected_range]))
        if self._gmv_chart is not None:
            self._gmv_chart.set_data(GMV_SERIES[self._selected_range], TREND_LABELS)
            self._gmv_chart.set_unit("万")
        if self._category_chart is not None:
            self._category_chart.set_items(tuple(zip(CATEGORY_LABELS, CATEGORY_VALUES[self._selected_range])))
        if self._trend_comparison is not None:
            self._trend_comparison.set_series(TREND_LABELS, tuple(float(v) for v in GMV_SERIES[self._selected_range]), tuple(float(v) for v in GMV_COMPARE_SERIES[self._selected_range]), current_name="本周", compare_name="上周")
        if self._product_table is not None:
            self._product_table.set_rows(self._product_rows(records))
            if records:
                self._product_table.select_absolute_row(self._selected_index)
        if self._abandon_table is not None:
            self._abandon_table.set_rows(self._abandon_rows(records))
        if self._crew_table is not None:
            self._crew_table.set_rows(self._crew_rows(records))
        if self._roi_gauge is not None:
            self._roi_gauge.set_sentiment(min(max((payload["ROI"][1]) * 2.1, -1.0), 1.0))
        self._refresh_recovery_cards(records)
        self._refresh_source_insights(records)
        self._refresh_selection()

    def _refresh_recovery_cards(self, records: Sequence[ProductConversionRecord]) -> None:
        base_multiplier = 1.0 + min(len(records), 12) * 0.01
        for index, (title, _summary, values) in enumerate(RECOVERY_PLAYBOOKS):
            adjusted = tuple(int(value * base_multiplier) for value in values)
            if index < len(self._recovery_sparklines):
                self._recovery_sparklines[index].set_values(adjusted)
            if index < len(self._recovery_value_labels):
                _call(self._recovery_value_labels[index], "setText", f"{title} · 预计挽回 {_format_percent(max(adjusted) / 100.0)}")

    def _refresh_source_insights(self, records: Sequence[ProductConversionRecord]) -> None:
        source_counts = {source: 0 for source in SOURCE_LABELS}
        for record in records:
            source_counts[record.source] = source_counts.get(record.source, 0) + record.revenue
        ranked = sorted(source_counts.items(), key=lambda item: item[1], reverse=True)
        for index, label in enumerate(self._source_insight_labels):
            if index >= len(ranked):
                continue
            source, value = ranked[index]
            _call(label, "setText", f"当前 {source} 累计贡献 {_format_compact(value, True)}，建议保持与该入口匹配的落地页与优惠链路。")

    def _refresh_selection(self) -> None:
        record = self._selected_record()
        if record is None:
            return
        if self._selected_name_label is not None:
            _call(self._selected_name_label, "setText", record.name)
        if self._selected_meta_label is not None:
            _call(self._selected_meta_label, "setText", f"{record.category} · {record.source} · {record.region}")
        if self._selected_summary_label is not None:
            _call(self._selected_summary_label, "setText", f"该商品点击至下单链路表现稳定，建议优先优化加购到支付阶段；当前弃购率为 {_format_percent(record.abandon_rate)}。")
        badge_values = ((record.source, "success" if record.source == "推荐页" else "info"), (record.category, "brand"), (record.region, "warning"))
        for badge, (text, tone) in zip(self._selected_badges, badge_values):
            _call(badge, "setText", text)
            badge.set_tone(tone)
        metric_texts = {
            "CVR": _format_percent(record.cvr),
            "ROI": f"{record.roi:.2f}x",
            "客单价": _format_compact(record.aov, True),
            "弃购率": _format_percent(record.abandon_rate),
        }
        for metric, label in self._selected_metric_labels.items():
            _call(label, "setText", metric_texts[metric])

    def _apply_page_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#ecommerceConversionPage {{ background-color: {colors.surface_alt}; }}
            QFrame#conversionToolbar,
            QFrame#conversionDetailCard,
            QFrame#conversionMetricCard,
            QFrame#conversionMiniCard,
            QFrame#conversionRecoveryCard,
            QFrame#conversionSourceInsightCard,
            QFrame#conversionRhythmCard,
            QFrame#conversionChecklistCard,
            QFrame#conversionRetargetingCard {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#conversionToolbar {{
                border-color: {_rgba(_token('brand.primary'), 0.18)};
            }}
            QLabel#conversionPanelTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#conversionSelectionTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#conversionSubtleText,
            QLabel#conversionMetricTitle {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.medium')};
                background: transparent;
            }}
            QLabel#conversionMetricValue {{
                color: {_token('brand.primary')};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            """,
        )

    def on_activated(self) -> None:
        self._refresh_all_views()
