# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportArgumentType=false, reportCallIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportPrivateUsage=false, reportImplicitOverride=false, reportGeneralTypeIssues=false

from __future__ import annotations

"""报表中心页面。"""

from dataclasses import dataclass
from typing import Final

from ....core.qt import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import ChartWidget, ContentSection, DataTable, DistributionChart, FilterDropdown, KPICard, PageContainer, PrimaryButton, SearchBar, SecondaryButton, StatusBadge, TabBar, TagChip
from ...components.inputs import RADIUS_LG, SPACING_LG, SPACING_MD, SPACING_SM, SPACING_XL, SPACING_XS, _call, _connect, _palette, _static_token, _token
from ..base_page import BasePage


def _rgba(hex_color: str, alpha: float) -> str:
    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


@dataclass(frozen=True)
class ReportTemplate:
    name: str
    type_name: str
    summary: str
    metrics: tuple[str, ...]
    format_hint: str


REPORT_HEADERS: Final[tuple[str, ...]] = ("名称", "类型", "日期", "创建人", "定时", "操作")
EXPORT_HEADERS: Final[tuple[str, ...]] = ("导出名称", "格式", "时间", "创建人", "状态")
FORMAT_LABELS: Final[tuple[str, ...]] = ("PDF", "Excel", "CSV")
SCHEDULE_LABELS: Final[tuple[str, ...]] = ("每日", "每周", "每月")
METRIC_LABELS: Final[tuple[str, ...]] = ("GMV", "转化率", "播放量", "新增粉丝", "ROI", "互动率")
TAB_LABELS: Final[tuple[str, ...]] = ("模板中心", "报表管理", "导出记录")

TEMPLATES: Final[tuple[ReportTemplate, ...]] = (
    ReportTemplate("经营日报", "经营分析", "聚焦 GMV、订单与投放效率，适合晨会同步。", ("GMV", "转化率", "ROI"), "PDF / Excel"),
    ReportTemplate("流量周报", "流量分析", "覆盖流量来源、地区、设备与内容分发走势。", ("播放量", "新增粉丝", "互动率"), "PDF / CSV"),
    ReportTemplate("商品转化周报", "电商分析", "针对曝光到支付链路输出漏斗与弃购分析。", ("GMV", "转化率", "ROI"), "PDF / Excel"),
    ReportTemplate("粉丝画像月报", "人群分析", "呈现年龄、兴趣、地区与活跃周期洞察。", ("新增粉丝", "互动率", "播放量"), "PDF / CSV"),
    ReportTemplate("活动复盘", "专项复盘", "适合节点营销，沉淀内容、流量与成交总结。", ("GMV", "播放量", "ROI"), "PDF / Excel"),
    ReportTemplate("竞品追踪", "竞品监测", "追踪对标账号内容表现与热词变动。", ("播放量", "互动率", "新增粉丝"), "CSV / Excel"),
)

SAVED_REPORTS: Final[tuple[tuple[str, str, str, str, str, str], ...]] = (
    ("12 月经营日报", "经营分析", "2026-03-09", "林夏", "每日 09:00", "查看 / 导出"),
    ("流量来源周报", "流量分析", "2026-03-08", "周哲", "每周一", "查看 / 分享"),
    ("商品转化复盘", "电商分析", "2026-03-07", "陈柚", "手动生成", "查看 / 导出"),
    ("粉丝增长月报", "人群分析", "2026-03-05", "安然", "每月 1 日", "查看 / 分享"),
    ("活动大促复盘", "专项复盘", "2026-03-03", "顾鸣", "手动生成", "查看 / 导出"),
    ("站点对比跟踪", "经营分析", "2026-03-02", "许澈", "每周三", "查看 / 复制"),
    ("高客单商品周报", "电商分析", "2026-03-01", "何苗", "每周五", "查看 / 导出"),
    ("高互动内容榜", "流量分析", "2026-02-28", "唐奕", "每日 18:00", "查看 / 分享"),
    ("品牌词搜索追踪", "流量分析", "2026-02-27", "李青", "每周二", "查看 / 复制"),
    ("重点人群分层报告", "人群分析", "2026-02-26", "周哲", "每月 15 日", "查看 / 导出"),
)

RECENT_EXPORTS: Final[tuple[tuple[str, str, str, str, str], ...]] = (
    ("经营日报_0309", "PDF", "09:06", "林夏", "完成"),
    ("流量周报_0308", "Excel", "18:22", "周哲", "完成"),
    ("商品转化复盘_0307", "CSV", "16:40", "陈柚", "完成"),
    ("粉丝画像月报_0305", "PDF", "10:12", "安然", "完成"),
    ("活动大促复盘_0303", "Excel", "21:34", "顾鸣", "进行中"),
    ("高互动内容榜_0228", "CSV", "18:03", "唐奕", "完成"),
)

FORMAT_BREAKDOWN: Final[tuple[int, int, int]] = (42, 33, 25)
METRIC_PLAYBOOKS: Final[tuple[tuple[str, str, str], ...]] = (
    ("GMV", "经营核心", "适合日报、周报与活动复盘，建议与 ROI 联动展示。"),
    ("转化率", "效率核心", "适合商品复盘与投放回看，建议搭配漏斗阶段展示。"),
    ("播放量", "流量核心", "适合流量周报与内容复盘，建议按来源拆分。"),
    ("新增粉丝", "增长核心", "适合人群月报与账号阶段总结。"),
    ("ROI", "投放核心", "适合经营日报与专项复盘，建议强化成本解释。"),
    ("互动率", "内容核心", "适合内容周报与选题复盘，建议和热词同时展示。"),
)
SHARE_CHANNELS: Final[tuple[tuple[str, str, tuple[int, ...]], ...]] = (
    ("团队共享目录", "适合常规日报与周报自动分发。", (18, 20, 22, 24, 26, 28, 31)),
    ("负责人邮箱", "适合管理层晨会与异常提醒。", (12, 14, 17, 19, 21, 24, 27)),
    ("项目空间链接", "适合专项复盘和跨团队协作。", (9, 11, 13, 16, 18, 21, 23)),
)
EXPORT_SCENARIOS: Final[tuple[tuple[str, str, tuple[int, ...]], ...]] = (
    ("晨会简报", "推荐 PDF，适合管理层快速浏览。", (14, 16, 18, 19, 21, 23, 25)),
    ("运营明细", "推荐 Excel，适合二次分析与筛选。", (11, 13, 15, 18, 20, 22, 24)),
    ("跨系统同步", "推荐 CSV，适合接入自动化或外部 BI。", (8, 10, 12, 14, 16, 18, 20)),
)
DELIVERY_CHECKLIST: Final[tuple[tuple[str, str], ...]] = (
    ("模板标题清晰", "确保共享后团队能快速判断用途与范围。"),
    ("日期范围明确", "避免周报与月报口径混用。"),
    ("指标说明齐全", "对 ROI、转化率等指标补充计算说明。"),
    ("导出格式匹配", "管理层默认 PDF，运营明细优先 Excel。"),
)
GOVERNANCE_RULES: Final[tuple[tuple[str, str, tuple[int, ...]], ...]] = (
    ("命名规范", "统一采用 主题_周期_日期 格式，便于检索。", (14, 16, 18, 20, 23, 25, 27)),
    ("口径审阅", "所有转化类报表在共享前需通过指标口径复核。", (12, 14, 17, 19, 21, 24, 26)),
    ("共享授权", "对外共享仅保留 PDF，内部分析优先 Excel。", (10, 12, 15, 18, 20, 23, 25)),
    ("归档策略", "专项复盘按月归档，避免目录噪音累积。", (9, 11, 13, 16, 18, 20, 22)),
)
ARCHIVE_STRATEGIES: Final[tuple[tuple[str, str, tuple[int, ...]], ...]] = (
    ("日报归档", "保留近 90 天在线访问，之后迁移归档目录。", (10, 12, 14, 16, 19, 22, 24)),
    ("周报归档", "保留全年可检索，优先按业务域整理。", (8, 10, 12, 15, 17, 19, 22)),
    ("专项复盘归档", "绑定活动编号与负责人，便于复盘复用。", (7, 9, 11, 13, 16, 18, 21)),
)
NOTIFY_PATHS: Final[tuple[tuple[str, str, tuple[int, ...]], ...]] = (
    ("晨会提醒", "每日 08:55 推送到负责人邮箱与项目群。", (15, 17, 19, 22, 24, 27, 30)),
    ("异常播报", "当指标低于阈值时立即补发摘要。", (9, 11, 14, 17, 19, 22, 24)),
    ("周报汇总", "周一早间统一推送上周经营与流量周报。", (12, 14, 16, 19, 21, 24, 26)),
)
HANDOFF_MODULES: Final[tuple[tuple[str, str, tuple[int, ...]], ...]] = (
    ("经营负责人", "默认接收经营日报、周报与异常提醒。", (16, 18, 20, 23, 25, 28, 31)),
    ("内容团队", "重点接收流量与互动相关模板。", (12, 14, 16, 19, 22, 25, 27)),
    ("投放团队", "重点接收 ROI 与转化相关周报。", (11, 13, 15, 18, 20, 23, 26)),
)
QA_RULES: Final[tuple[tuple[str, str], ...]] = (
    ("样式检查", "确认标题、指标、图表与导出格式文案一致。"),
    ("口径检查", "确认 ROI、转化率、播放量等指标口径统一。"),
    ("时间检查", "确认报表日期范围与定时任务频率一致。"),
    ("共享检查", "确认共享目录、邮箱与项目空间权限正确。"),
)


class ReportCenterPage(BasePage):
    """报表中心页面。"""

    default_route_id: RouteId = RouteId("report_center")
    default_display_name: str = "报表中心"
    default_icon_name: str = "summarize"

    def setup_ui(self) -> None:
        self._search_keyword = ""
        self._selected_type = "全部"
        self._selected_schedule = SCHEDULE_LABELS[1]
        self._selected_format = FORMAT_LABELS[0]
        self._selected_tab = TAB_LABELS[0]

        self._search_bar: SearchBar | None = None
        self._type_filter: FilterDropdown | None = None
        self._schedule_filter: FilterDropdown | None = None
        self._format_filter: FilterDropdown | None = None
        self._tab_bar: TabBar | None = None
        self._saved_table: DataTable | None = None
        self._export_table: DataTable | None = None
        self._format_chart: DistributionChart | None = None
        self._template_cards: list[QFrame] = []
        self._builder_metrics: dict[str, StatusBadge] = {}
        self._builder_summary_label: QLabel | None = None
        self._schedule_summary_label: QLabel | None = None
        self._preview_chart: ChartWidget | None = None
        self._metric_playbook_labels: list[QLabel] = []
        self._share_channel_charts: list[ChartWidget] = []
        self._share_channel_value_labels: list[QLabel] = []
        self._scenario_charts: list[ChartWidget] = []
        self._governance_charts: list[ChartWidget] = []
        self._archive_charts: list[ChartWidget] = []
        self._notify_charts: list[ChartWidget] = []
        self._handoff_charts: list[ChartWidget] = []
        self._qa_labels: list[QLabel] = []
        self._kpi_cards: dict[str, KPICard] = {}

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        _call(self, "setObjectName", "reportCenterPage")

        self._page_container = PageContainer(
            title="报表中心",
            description="管理模板、已保存报表、导出记录与定时任务，快速生成适合运营团队分发的分析报告。",
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
        self._page_container.add_action(TagChip("定时报表开启", tone="success", parent=self))
        self._page_container.add_action(TagChip("共享模板 6 个", tone="brand", parent=self))
        self._page_container.add_action(StatusBadge("本月导出 28 次", tone="info", parent=self))
        self._page_container.add_action(SecondaryButton("刷新目录", parent=self))
        self._page_container.add_action(PrimaryButton("新建报表", parent=self))

    def _build_toolbar(self) -> QWidget:
        panel = QFrame(self)
        _call(panel, "setObjectName", "reportCenterToolbar")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)

        title_row = QWidget(panel)
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_MD)
        title_column = QWidget(title_row)
        title_column_layout = QVBoxLayout(title_column)
        title_column_layout.setContentsMargins(0, 0, 0, 0)
        title_column_layout.setSpacing(SPACING_XS)
        title_label = QLabel("报表筛选", title_column)
        _call(title_label, "setObjectName", "reportCenterPanelTitle")
        helper_label = QLabel("按类型、频率与格式切片模板目录，联动已保存报表、导出记录与分发模块。", title_column)
        _call(helper_label, "setObjectName", "reportSubtleText")
        _call(helper_label, "setWordWrap", True)
        title_column_layout.addWidget(title_label)
        title_column_layout.addWidget(helper_label)
        title_layout.addWidget(title_column, 1)
        title_layout.addWidget(StatusBadge("定时任务稳定运行", tone="success", parent=title_row))

        row = QWidget(panel)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACING_LG)
        self._search_bar = SearchBar("搜索模板、报表名称、创建人或导出记录...", row)
        self._type_filter = FilterDropdown("报表类型", ("经营分析", "流量分析", "电商分析", "人群分析", "专项复盘"), parent=row)
        self._schedule_filter = FilterDropdown("定时频率", SCHEDULE_LABELS, include_all=False, parent=row)
        self._format_filter = FilterDropdown("导出格式", FORMAT_LABELS, include_all=False, parent=row)
        row_layout.addWidget(self._search_bar, 3)
        row_layout.addWidget(self._type_filter, 1)
        row_layout.addWidget(self._schedule_filter, 1)
        row_layout.addWidget(self._format_filter, 1)
        tags = QWidget(panel)
        tags_layout = QHBoxLayout(tags)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(SPACING_MD)
        tags_layout.addWidget(TagChip("日报模板使用率最高", tone="warning", parent=tags))
        tags_layout.addWidget(TagChip("PDF 导出占比 42%", tone="brand", parent=tags))
        tags_layout.addWidget(TagChip("周报共享需求上升", tone="info", parent=tags))
        tags_layout.addStretch(1)
        tags_layout.addWidget(SecondaryButton("重置条件", parent=tags))
        tags_layout.addWidget(PrimaryButton("批量导出", parent=tags))
        layout.addWidget(title_row)
        layout.addWidget(row)
        layout.addWidget(tags)
        return panel

    def _build_kpis(self) -> QWidget:
        wrapper = QWidget(self)
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        for title in ("总报表", "本月生成", "定时报表", "共享报表"):
            card = KPICard(title=title, value="-", trend="up", percentage="+0.0%", caption="近 30 天", sparkline_data=(0, 0, 0, 0, 0, 0, 0), parent=wrapper)
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
        layout.addWidget(self._build_saved_section())
        layout.addWidget(self._build_export_section())
        layout.addWidget(self._build_share_section())
        return column

    def _build_right_column(self) -> QWidget:
        column = QWidget(self)
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        layout.addWidget(self._build_builder_section())
        layout.addWidget(self._build_schedule_section())
        layout.addWidget(self._build_format_section())
        layout.addWidget(self._build_metric_playbook_section())
        layout.addWidget(self._build_scenario_section())
        layout.addWidget(self._build_delivery_checklist_section())
        layout.addWidget(self._build_governance_section())
        layout.addWidget(self._build_archive_section())
        layout.addWidget(self._build_notify_section())
        layout.addWidget(self._build_handoff_section())
        layout.addWidget(self._build_qa_section())
        return column

    def _build_tabs(self) -> QWidget:
        section = ContentSection("模板与目录", icon="◎", parent=self)
        self._tab_bar = TabBar(section)
        self._tab_bar.add_tab(TAB_LABELS[0], self._build_template_tab())
        self._tab_bar.add_tab(TAB_LABELS[1], self._build_management_tab())
        self._tab_bar.add_tab(TAB_LABELS[2], self._build_export_tab())
        section.add_widget(self._tab_bar)
        return section

    def _build_template_tab(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        row1 = QWidget(page)
        row1_layout = QHBoxLayout(row1)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(SPACING_LG)
        for template in TEMPLATES[:3]:
            row1_layout.addWidget(self._build_template_card(template, row1), 1)
        row2 = QWidget(page)
        row2_layout = QHBoxLayout(row2)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(SPACING_LG)
        for template in TEMPLATES[3:]:
            row2_layout.addWidget(self._build_template_card(template, row2), 1)
        layout.addWidget(row1)
        layout.addWidget(row2)
        return page

    def _build_template_card(self, template: ReportTemplate, parent: QWidget) -> QWidget:
        card = QFrame(parent)
        self._template_cards.append(card)
        _call(card, "setObjectName", "reportTemplateCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_SM)
        title = QLabel(template.name, card)
        subtitle = QLabel(template.type_name, card)
        summary = QLabel(template.summary, card)
        footer = QLabel(f"指标：{' / '.join(template.metrics)} · 格式：{template.format_hint}", card)
        _call(title, "setObjectName", "reportTemplateTitle")
        _call(subtitle, "setObjectName", "reportSubtleText")
        _call(summary, "setObjectName", "reportSubtleText")
        _call(summary, "setWordWrap", True)
        _call(footer, "setObjectName", "reportAccentText")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(summary)
        layout.addStretch(1)
        layout.addWidget(footer)
        layout.addWidget(PrimaryButton("使用模板", parent=card))
        return card

    def _build_management_tab(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        chart = ChartWidget(chart_type="bar", title="近 7 日报表生成量", labels=("周一", "周二", "周三", "周四", "周五", "周六", "周日"), data=(18, 20, 23, 24, 28, 17, 15), unit="份", parent=page)
        layout.addWidget(chart)
        return page

    def _build_export_tab(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        self._preview_chart = ChartWidget(chart_type="pie", title="导出格式占比", labels=FORMAT_LABELS, data=FORMAT_BREAKDOWN, unit="%", parent=page)
        layout.addWidget(self._preview_chart)
        return page

    def _build_saved_section(self) -> QWidget:
        section = ContentSection("已保存报表", icon="▤", parent=self)
        self._saved_table = DataTable(headers=REPORT_HEADERS, rows=(), page_size=8, empty_text="暂无已保存报表", parent=section)
        section.add_widget(self._saved_table)
        return section

    def _build_export_section(self) -> QWidget:
        section = ContentSection("最近导出", icon="◫", parent=self)
        self._export_table = DataTable(headers=EXPORT_HEADERS, rows=(), page_size=6, empty_text="暂无导出记录", parent=section)
        section.add_widget(self._export_table)
        return section

    def _build_share_section(self) -> QWidget:
        section = ContentSection("共享与分发", icon="↗", parent=self)
        for title, summary, values in SHARE_CHANNELS:
            card = QFrame(section)
            _call(card, "setObjectName", "reportShareCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            title_label = QLabel(title, card)
            summary_label = QLabel(summary, card)
            value_label = QLabel(f"预计覆盖 {_format_share_value(max(values))}", card)
            chart = ChartWidget(chart_type="line", title="7 日触达曲线", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="次", parent=card)
            _call(title_label, "setObjectName", "reportTemplateTitle")
            _call(summary_label, "setObjectName", "reportSubtleText")
            _call(summary_label, "setWordWrap", True)
            _call(value_label, "setObjectName", "reportAccentText")
            self._share_channel_charts.append(chart)
            self._share_channel_value_labels.append(value_label)
            layout.addWidget(title_label)
            layout.addWidget(summary_label)
            layout.addWidget(chart)
            layout.addWidget(value_label)
            section.add_widget(card)
        return section

    def _build_builder_section(self) -> QWidget:
        section = ContentSection("快速报表构建器", icon="✦", parent=self)
        card = QFrame(section)
        _call(card, "setObjectName", "reportBuilderCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)
        layout.addWidget(QLabel("已选指标", card))
        chips = QWidget(card)
        chips_layout = QHBoxLayout(chips)
        chips_layout.setContentsMargins(0, 0, 0, 0)
        chips_layout.setSpacing(SPACING_SM)
        for metric in METRIC_LABELS:
            badge = StatusBadge(metric, tone="brand" if metric in {"GMV", "ROI"} else "info", parent=chips)
            self._builder_metrics[metric] = badge
            chips_layout.addWidget(badge)
        chips_layout.addStretch(1)
        layout.addWidget(chips)
        self._builder_summary_label = QLabel("当前将生成经营日报模板，日期范围为近 7 天，输出格式为 PDF。", card)
        _call(self._builder_summary_label, "setObjectName", "reportSubtleText")
        _call(self._builder_summary_label, "setWordWrap", True)
        layout.addWidget(self._builder_summary_label)
        layout.addWidget(PrimaryButton("立即生成报表", parent=card))
        section.add_widget(card)
        return section

    def _build_schedule_section(self) -> QWidget:
        section = ContentSection("定时配置", icon="⏱", parent=self)
        card = QFrame(section)
        _call(card, "setObjectName", "reportScheduleCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)
        self._schedule_summary_label = QLabel("当前频率：每周一 09:00 自动生成经营日报，并同步到共享目录。", card)
        _call(self._schedule_summary_label, "setObjectName", "reportSubtleText")
        _call(self._schedule_summary_label, "setWordWrap", True)
        layout.addWidget(self._schedule_summary_label)
        for label in SCHEDULE_LABELS:
            row = QFrame(card)
            _call(row, "setObjectName", "reportScheduleItem")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            row_layout.setSpacing(SPACING_SM)
            row_layout.addWidget(QLabel(label, row))
            row_layout.addStretch(1)
            row_layout.addWidget(StatusBadge("启用" if label == self._selected_schedule else "待用", tone="success" if label == self._selected_schedule else "neutral", parent=row))
            layout.addWidget(row)
        section.add_widget(card)
        return section

    def _build_format_section(self) -> QWidget:
        section = ContentSection("导出格式", icon="◔", parent=self)
        self._format_chart = DistributionChart(section, tuple(zip(FORMAT_LABELS, FORMAT_BREAKDOWN)))
        section.add_widget(self._format_chart)
        return section

    def _build_metric_playbook_section(self) -> QWidget:
        section = ContentSection("指标配置建议", icon="◌", parent=self)
        for metric, flag, summary in METRIC_PLAYBOOKS:
            card = QFrame(section)
            _call(card, "setObjectName", "reportMetricPlaybookCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_XS)
            head = QWidget(card)
            head_layout = QHBoxLayout(head)
            head_layout.setContentsMargins(0, 0, 0, 0)
            head_layout.setSpacing(SPACING_SM)
            title_label = QLabel(metric, head)
            badge = StatusBadge(flag, tone="brand" if "核心" in flag else "info", parent=head)
            _call(title_label, "setObjectName", "reportTemplateTitle")
            head_layout.addWidget(title_label)
            head_layout.addStretch(1)
            head_layout.addWidget(badge)
            body = QLabel(summary, card)
            _call(body, "setObjectName", "reportSubtleText")
            _call(body, "setWordWrap", True)
            self._metric_playbook_labels.append(body)
            layout.addWidget(head)
            layout.addWidget(body)
            section.add_widget(card)
        return section

    def _build_scenario_section(self) -> QWidget:
        section = ContentSection("导出场景建议", icon="◎", parent=self)
        for title, summary, values in EXPORT_SCENARIOS:
            card = QFrame(section)
            _call(card, "setObjectName", "reportScenarioCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            title_label = QLabel(title, card)
            body_label = QLabel(summary, card)
            chart = ChartWidget(chart_type="line", title="近 7 日使用热度", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="次", parent=card)
            _call(title_label, "setObjectName", "reportTemplateTitle")
            _call(body_label, "setObjectName", "reportSubtleText")
            _call(body_label, "setWordWrap", True)
            self._scenario_charts.append(chart)
            layout.addWidget(title_label)
            layout.addWidget(body_label)
            layout.addWidget(chart)
            section.add_widget(card)
        return section

    def _build_delivery_checklist_section(self) -> QWidget:
        section = ContentSection("交付检查项", icon="✓", parent=self)
        for title, summary in DELIVERY_CHECKLIST:
            row = QFrame(section)
            _call(row, "setObjectName", "reportChecklistCard")
            layout = QHBoxLayout(row)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            layout.addWidget(StatusBadge("已校验", tone="success", parent=row))
            title_label = QLabel(title, row)
            body_label = QLabel(summary, row)
            _call(title_label, "setObjectName", "reportTemplateTitle")
            _call(body_label, "setObjectName", "reportSubtleText")
            layout.addWidget(title_label)
            layout.addStretch(1)
            layout.addWidget(body_label)
            section.add_widget(row)
        return section

    def _build_governance_section(self) -> QWidget:
        section = ContentSection("治理规则", icon="◫", parent=self)
        for title, summary, values in GOVERNANCE_RULES:
            card = QFrame(section)
            _call(card, "setObjectName", "reportGovernanceCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            title_label = QLabel(title, card)
            body_label = QLabel(summary, card)
            chart = ChartWidget(chart_type="line", title="执行覆盖趋势", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="次", parent=card)
            _call(title_label, "setObjectName", "reportTemplateTitle")
            _call(body_label, "setObjectName", "reportSubtleText")
            _call(body_label, "setWordWrap", True)
            self._governance_charts.append(chart)
            layout.addWidget(title_label)
            layout.addWidget(body_label)
            layout.addWidget(chart)
            section.add_widget(card)
        return section

    def _build_archive_section(self) -> QWidget:
        section = ContentSection("归档策略", icon="◔", parent=self)
        for title, summary, values in ARCHIVE_STRATEGIES:
            card = QFrame(section)
            _call(card, "setObjectName", "reportArchiveCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            title_label = QLabel(title, card)
            body_label = QLabel(summary, card)
            chart = ChartWidget(chart_type="line", title="归档执行率", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="%", parent=card)
            _call(title_label, "setObjectName", "reportTemplateTitle")
            _call(body_label, "setObjectName", "reportSubtleText")
            _call(body_label, "setWordWrap", True)
            self._archive_charts.append(chart)
            layout.addWidget(title_label)
            layout.addWidget(body_label)
            layout.addWidget(chart)
            section.add_widget(card)
        return section

    def _build_notify_section(self) -> QWidget:
        section = ContentSection("通知路径", icon="↗", parent=self)
        for title, summary, values in NOTIFY_PATHS:
            card = QFrame(section)
            _call(card, "setObjectName", "reportNotifyCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            title_label = QLabel(title, card)
            body_label = QLabel(summary, card)
            chart = ChartWidget(chart_type="line", title="触达次数", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="次", parent=card)
            _call(title_label, "setObjectName", "reportTemplateTitle")
            _call(body_label, "setObjectName", "reportSubtleText")
            _call(body_label, "setWordWrap", True)
            self._notify_charts.append(chart)
            layout.addWidget(title_label)
            layout.addWidget(body_label)
            layout.addWidget(chart)
            section.add_widget(card)
        return section

    def _build_handoff_section(self) -> QWidget:
        section = ContentSection("交付对象", icon="◎", parent=self)
        for title, summary, values in HANDOFF_MODULES:
            card = QFrame(section)
            _call(card, "setObjectName", "reportHandoffCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            title_label = QLabel(title, card)
            body_label = QLabel(summary, card)
            chart = ChartWidget(chart_type="line", title="分发频率", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="次", parent=card)
            _call(title_label, "setObjectName", "reportTemplateTitle")
            _call(body_label, "setObjectName", "reportSubtleText")
            _call(body_label, "setWordWrap", True)
            self._handoff_charts.append(chart)
            layout.addWidget(title_label)
            layout.addWidget(body_label)
            layout.addWidget(chart)
            section.add_widget(card)
        return section

    def _build_qa_section(self) -> QWidget:
        section = ContentSection("质检清单", icon="✓", parent=self)
        for title, summary in QA_RULES:
            row = QFrame(section)
            _call(row, "setObjectName", "reportQACard")
            layout = QHBoxLayout(row)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            layout.addWidget(StatusBadge("通过", tone="success", parent=row))
            title_label = QLabel(title, row)
            body_label = QLabel(summary, row)
            _call(title_label, "setObjectName", "reportTemplateTitle")
            _call(body_label, "setObjectName", "reportSubtleText")
            self._qa_labels.append(body_label)
            layout.addWidget(title_label)
            layout.addStretch(1)
            layout.addWidget(body_label)
            section.add_widget(row)
        return section

    def _bind_interactions(self) -> None:
        if self._search_bar is not None:
            _connect(self._search_bar.search_changed, self._handle_search)
        if self._type_filter is not None:
            _connect(self._type_filter.filter_changed, self._handle_type)
        if self._schedule_filter is not None:
            _connect(self._schedule_filter.filter_changed, self._handle_schedule)
        if self._format_filter is not None:
            _connect(self._format_filter.filter_changed, self._handle_format)
        if self._tab_bar is not None:
            _connect(self._tab_bar.tab_changed, self._handle_tab)

    def _handle_search(self, text: str) -> None:
        self._search_keyword = text.strip()
        self._refresh_all_views()

    def _handle_type(self, text: str) -> None:
        self._selected_type = text
        self._refresh_all_views()

    def _handle_schedule(self, text: str) -> None:
        self._selected_schedule = text
        self._refresh_all_views()

    def _handle_format(self, text: str) -> None:
        self._selected_format = text
        self._refresh_all_views()

    def _handle_tab(self, index: int) -> None:
        if 0 <= index < len(TAB_LABELS):
            self._selected_tab = TAB_LABELS[index]
            self._refresh_all_views()

    def _filter_rows(self, rows: tuple[tuple[str, ...], ...]) -> list[list[object]]:
        result: list[list[object]] = []
        for row in rows:
            combined = " ".join(row)
            if self._search_keyword and self._search_keyword.lower() not in combined.lower():
                continue
            if self._selected_type not in {"", "全部"} and self._selected_type not in row[1]:
                continue
            result.append(list(row))
        return result

    def _refresh_share_cards(self) -> None:
        multiplier = 1.0 if self._selected_format == "PDF" else 0.92 if self._selected_format == "Excel" else 0.86
        for index, (_title, _summary, values) in enumerate(SHARE_CHANNELS):
            adjusted = tuple(int(value * multiplier) for value in values)
            if index < len(self._share_channel_charts):
                self._share_channel_charts[index].set_data(adjusted, ("1", "2", "3", "4", "5", "6", "7"))
                self._share_channel_charts[index].set_unit("次")
            if index < len(self._share_channel_value_labels):
                _call(self._share_channel_value_labels[index], "setText", f"预计覆盖 {_format_share_value(max(adjusted))}")

    def _refresh_metric_playbooks(self) -> None:
        active_type = self._selected_type if self._selected_type not in {"", "全部"} else "经营分析"
        for index, label in enumerate(self._metric_playbook_labels):
            if index >= len(METRIC_PLAYBOOKS):
                continue
            metric, flag, summary = METRIC_PLAYBOOKS[index]
            _call(label, "setText", f"{summary} 当前类型为 {active_type}，建议优先保留 {metric} 作为 {flag} 指标。")

    def _refresh_scenarios(self) -> None:
        multiplier = 1.0 if self._selected_format == "PDF" else 1.08 if self._selected_format == "Excel" else 0.94
        for index, (_title, _summary, values) in enumerate(EXPORT_SCENARIOS):
            adjusted = tuple(int(value * multiplier) for value in values)
            if index < len(self._scenario_charts):
                self._scenario_charts[index].set_data(adjusted, ("1", "2", "3", "4", "5", "6", "7"))
                self._scenario_charts[index].set_unit("次")

    def _refresh_governance(self) -> None:
        multiplier = 1.0 if self._selected_schedule == "每周" else 0.92 if self._selected_schedule == "每日" else 1.08
        for index, (_title, _summary, values) in enumerate(GOVERNANCE_RULES):
            adjusted = tuple(int(value * multiplier) for value in values)
            if index < len(self._governance_charts):
                self._governance_charts[index].set_data(adjusted, ("1", "2", "3", "4", "5", "6", "7"))
                self._governance_charts[index].set_unit("次")

    def _refresh_archive(self) -> None:
        multiplier = 1.0 if self._selected_tab == "模板中心" else 1.06 if self._selected_tab == "报表管理" else 0.96
        for index, (_title, _summary, values) in enumerate(ARCHIVE_STRATEGIES):
            adjusted = tuple(int(value * multiplier) for value in values)
            if index < len(self._archive_charts):
                self._archive_charts[index].set_data(adjusted, ("1", "2", "3", "4", "5", "6", "7"))
                self._archive_charts[index].set_unit("%")

    def _refresh_notify(self) -> None:
        multiplier = 1.0 if self._selected_schedule == "每日" else 0.92 if self._selected_schedule == "每周" else 0.84
        for index, (_title, _summary, values) in enumerate(NOTIFY_PATHS):
            adjusted = tuple(int(value * multiplier) for value in values)
            if index < len(self._notify_charts):
                self._notify_charts[index].set_data(adjusted, ("1", "2", "3", "4", "5", "6", "7"))
                self._notify_charts[index].set_unit("次")

    def _refresh_handoff(self) -> None:
        multiplier = 1.0 if self._selected_type in {"", "全部", "经营分析"} else 0.94
        for index, (_title, _summary, values) in enumerate(HANDOFF_MODULES):
            adjusted = tuple(int(value * multiplier) for value in values)
            if index < len(self._handoff_charts):
                self._handoff_charts[index].set_data(adjusted, ("1", "2", "3", "4", "5", "6", "7"))
                self._handoff_charts[index].set_unit("次")

    def _refresh_qa(self) -> None:
        for index, label in enumerate(self._qa_labels):
            if index >= len(QA_RULES):
                continue
            rule_title, summary = QA_RULES[index]
            _call(label, "setText", f"{rule_title}：{summary} 当前格式为 {self._selected_format}，频率为 {self._selected_schedule}。")

    def _refresh_all_views(self) -> None:
        payload = {
            "总报表": (str(len(SAVED_REPORTS) + len(TEMPLATES)), 0.082, (12, 13, 14, 16, 18, 19, 22)),
            "本月生成": ("28", 0.116, (8, 10, 12, 15, 18, 22, 28)),
            "定时报表": ("9", 0.071, (4, 5, 6, 7, 7, 8, 9)),
            "共享报表": ("14", 0.094, (6, 7, 8, 10, 11, 13, 14)),
        }
        for title, card in self._kpi_cards.items():
            value, delta, spark = payload[title]
            card.set_value(value)
            card.set_trend("up" if delta >= 0 else "down", f"{delta * 100:+.1f}%")
            card.set_sparkline_data(spark)
        if self._saved_table is not None:
            self._saved_table.set_rows(self._filter_rows(SAVED_REPORTS))
        if self._export_table is not None:
            self._export_table.set_rows(self._filter_rows(RECENT_EXPORTS))
        if self._format_chart is not None:
            self._format_chart.set_items(tuple(zip(FORMAT_LABELS, FORMAT_BREAKDOWN)))
        if self._preview_chart is not None:
            self._preview_chart.set_data(FORMAT_BREAKDOWN, FORMAT_LABELS)
        self._refresh_share_cards()
        self._refresh_metric_playbooks()
        self._refresh_scenarios()
        self._refresh_governance()
        self._refresh_archive()
        self._refresh_notify()
        self._refresh_handoff()
        self._refresh_qa()
        if self._builder_summary_label is not None:
            _call(self._builder_summary_label, "setText", f"当前将生成 {self._selected_type if self._selected_type not in {'', '全部'} else '经营分析'} 类报表，定时频率为 {self._selected_schedule}，输出格式为 {self._selected_format}。")
        if self._schedule_summary_label is not None:
            _call(self._schedule_summary_label, "setText", f"当前频率：{self._selected_schedule} 自动生成，默认导出 {self._selected_format}，可同步到共享目录。")
        tones = {
            "PDF": "brand",
            "Excel": "success",
            "CSV": "info",
        }
        for metric, badge in self._builder_metrics.items():
            badge.set_tone("brand" if metric in {"GMV", "ROI"} else tones.get(self._selected_format, "info"))

    def _apply_page_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#reportCenterPage {{ background-color: {colors.surface_alt}; }}
            QFrame#reportCenterToolbar,
            QFrame#reportTemplateCard,
            QFrame#reportBuilderCard,
            QFrame#reportScheduleCard,
            QFrame#reportScheduleItem,
            QFrame#reportShareCard,
            QFrame#reportMetricPlaybookCard,
            QFrame#reportScenarioCard,
            QFrame#reportChecklistCard,
            QFrame#reportGovernanceCard,
            QFrame#reportArchiveCard,
            QFrame#reportNotifyCard,
            QFrame#reportHandoffCard,
            QFrame#reportQACard {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#reportCenterToolbar {{
                border-color: {_rgba(_token('brand.primary'), 0.18)};
            }}
            QLabel#reportCenterPanelTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#reportTemplateTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#reportSubtleText {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                background: transparent;
            }}
            QLabel#reportAccentText {{
                color: {_token('brand.primary')};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
                background: transparent;
            }}
            """,
        )

    def on_activated(self) -> None:
        self._refresh_all_views()


def _format_share_value(value: int | float) -> str:
    amount = float(value)
    if amount >= 1000:
        return f"{amount / 1000:.1f}千次"
    return f"{amount:.0f}次"
