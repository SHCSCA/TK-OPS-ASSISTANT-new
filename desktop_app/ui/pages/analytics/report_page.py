# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportArgumentType=false, reportCallIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportPrivateUsage=false, reportImplicitOverride=false

from __future__ import annotations

"""数据报告生成器页面。"""

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Sequence

from ....core.types import RouteId
from ...components import (
    ActionCard,
    ChartWidget,
    ContentSection,
    DataTable,
    FormGroup,
    KPICard,
    PageContainer,
    PrimaryButton,
    SecondaryButton,
    SplitPanel,
    ThemedComboBox,
    ThemedLineEdit,
    ThemedScrollArea,
)
from ...components.inputs import (
    BUTTON_HEIGHT,
    RADIUS_LG,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
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
from ..base_page import BasePage

RATIO_METRICS: tuple[str, ...] = ("毛利率", "转化率", "互动率", "退款率")
MULTIPLIER_METRICS: tuple[str, ...] = ("ROI",)
CHART_TYPE_META: tuple[tuple[str, str], ...] = (
    ("表格", "▦"),
    ("折线图", "∿"),
    ("柱状图", "▥"),
    ("饼图", "◔"),
    ("面积图", "▱"),
    ("混合图", "◫"),
    ("热力图", "░"),
)
COMPARE_OPTIONS: tuple[str, ...] = ("不对比", "环比 (MoM)", "同比 (YoY)")


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba 字符串。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _now_label() -> str:
    """返回当前时间标签。"""

    return datetime.now().strftime("%H:%M:%S")


def _is_ratio_metric(metric: str) -> bool:
    """判断指标是否为百分比类。"""

    return metric in RATIO_METRICS


def _is_multiplier_metric(metric: str) -> bool:
    """判断指标是否为倍数类。"""

    return metric in MULTIPLIER_METRICS


def _format_metric_value(metric: str, value: float | int, *, compact: bool = False) -> str:
    """按指标类型格式化文案。"""

    numeric = float(value)
    if _is_ratio_metric(metric):
        return f"{numeric * 100:.1f}%"
    if _is_multiplier_metric(metric):
        return f"{numeric:.2f}x"
    if metric in {"销售额", "利润额"}:
        if compact and abs(numeric) >= 10000:
            return f"¥{numeric / 10000:.1f}万"
        return f"¥{numeric:,.0f}"
    if abs(numeric) >= 10000 and compact:
        return f"{numeric / 10000:.1f}万"
    return f"{numeric:,.0f}"


def _chart_unit(metric: str) -> str:
    """返回图表展示单位。"""

    if _is_ratio_metric(metric):
        return "%"
    if _is_multiplier_metric(metric):
        return "x"
    if metric in {"销售额", "利润额"}:
        return "万"
    return ""


def _chart_value(metric: str, value: float | int) -> float:
    """将原始值转换为图表展示值。"""

    numeric = float(value)
    if _is_ratio_metric(metric):
        return round(numeric * 100, 2)
    if metric in {"销售额", "利润额"}:
        return round(numeric / 10000, 2)
    return round(numeric, 2)


def _resolved_chart_widget_type(chart_type: str) -> str:
    """将设计稿图表类型映射为内置图表类型。"""

    mapping = {
        "表格": "bar",
        "折线图": "line",
        "柱状图": "bar",
        "饼图": "pie",
        "面积图": "line",
        "混合图": "bar",
        "热力图": "bar",
    }
    return mapping.get(chart_type, "line")


def _trend_direction(values: Sequence[float]) -> tuple[str, str]:
    """根据序列估算趋势方向与文案。"""

    if len(values) < 2:
        return ("flat", "0.0%")
    first_value = float(values[0])
    last_value = float(values[-1])
    if abs(first_value) <= 1e-9:
        return ("flat", "0.0%")
    delta_ratio = (last_value - first_value) / abs(first_value)
    if delta_ratio > 0.03:
        return ("up", f"{abs(delta_ratio) * 100:.1f}%")
    if delta_ratio < -0.03:
        return ("down", f"{abs(delta_ratio) * 100:.1f}%")
    return ("flat", f"{abs(delta_ratio) * 100:.1f}%")


def _clear_layout(layout: object) -> None:
    """安全清空布局中的已有部件。"""

    count_method = getattr(layout, "count", None)
    take_at = getattr(layout, "takeAt", None)
    if callable(count_method) and callable(take_at):
        while True:
            count_value = count_method()
            if not isinstance(count_value, int) or count_value <= 0:
                break
            item = take_at(0)
            widget = getattr(item, "widget", lambda: None)() if item is not None else None
            if widget is not None:
                _call(widget, "setParent", None)
                _call(widget, "deleteLater")
        return

    items = getattr(layout, "_items", None)
    if isinstance(items, list):
        for item in list(items):
            widget = item if isinstance(item, QWidget) else getattr(item, "widget", lambda: None)()
            if widget is not None:
                _call(widget, "setParent", None)
                _call(widget, "deleteLater")
        items.clear()


@dataclass(frozen=True)
class ReportTemplateSpec:
    """单个报告模板的数据定义。"""

    template_id: str
    name: str
    icon: str
    summary: str
    default_title: str
    range_options: tuple[str, ...]
    default_range: str
    default_compare: str
    dimensions: tuple[str, ...]
    metrics: tuple[str, ...]
    default_dimensions: tuple[str, ...]
    default_metrics: tuple[str, ...]
    default_chart_type: str
    filter_field: str
    filter_value: str
    preview_note: str
    records: tuple[dict[str, object], ...]


class TemplateActionItem(QFrame):
    """包裹 ActionCard 的模板选择卡。"""

    chosen = Signal(str)

    def __init__(self, spec: ReportTemplateSpec, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._spec = spec
        self._selected = False
        _call(self, "setObjectName", "reportTemplateItem")
        _call(self, "setCursor", getattr(Qt, "PointingHandCursor", 0))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._card = ActionCard(
            title=spec.name,
            description=spec.summary,
            icon=spec.icon,
            button_text="使用模板",
            status_text="可切换",
            status_tone="info",
            parent=self,
        )
        layout.addWidget(self._card)

        _connect(getattr(self._card.primary_button, "clicked", None), self._emit_chosen)
        self.set_selected(False)

    @property
    def template_id(self) -> str:
        """返回模板 ID。"""

        return self._spec.template_id

    def set_selected(self, selected: bool) -> None:
        """刷新选中状态。"""

        self._selected = selected
        if selected:
            self._card.set_status("当前模板", "brand")
            _call(self._card.primary_button, "setText", "已选中")
        else:
            self._card.set_status("可切换", "info")
            _call(self._card.primary_button, "setText", "使用模板")
        self._apply_styles()

    def mousePressEvent(self, event: object) -> None:
        """支持点击卡片壳层切换模板。"""

        del event
        self._emit_chosen()

    def _emit_chosen(self) -> None:
        self.chosen.emit(self._spec.template_id)

    def _apply_styles(self) -> None:
        colors = _palette()
        background = _rgba(_token("brand.primary"), 0.08) if self._selected else "transparent"
        border = _token("brand.primary") if self._selected else colors.border
        _call(
            self,
            "setStyleSheet",
            f"""
            QFrame#reportTemplateItem {{
                background-color: {background};
                border: 1px solid {border};
                border-radius: {RADIUS_LG}px;
            }}
            """,
        )


class ReportGeneratorPage(BasePage):
    """数据报告生成器主页面。"""

    default_route_id: RouteId = RouteId("report_generator")
    default_display_name: str = "数据报告生成器"
    default_icon_name: str = "description"

    def setup_ui(self) -> None:
        """构建报告生成器页面。"""

        self._templates = self._build_templates()
        self._selected_template_id = self._templates[0].template_id
        self._selected_dimensions: set[str] = set(self._templates[0].default_dimensions)
        self._selected_metrics: set[str] = set(self._templates[0].default_metrics)
        self._selected_chart_type = self._templates[0].default_chart_type
        self._syncing_form = False
        self._template_items: dict[str, TemplateActionItem] = {}
        self._dimension_buttons: dict[str, QPushButton] = {}
        self._metric_buttons: dict[str, QPushButton] = {}
        self._chart_type_buttons: dict[str, QPushButton] = {}
        self._preview_table: DataTable | None = None
        self._last_action_text = "等待生成"

        _call(self, "setObjectName", "reportGeneratorPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_styles()

        page_container = PageContainer(
            title=self.display_name,
            description="左侧选模板，中间配字段与筛选，右侧实时查看表格与趋势预览。",
            parent=self,
        )
        self.layout.addWidget(page_container)

        self._header_chip = QLabel("模板：日报", page_container)
        _call(self._header_chip, "setObjectName", "reportHeaderChip")
        self._reset_button = SecondaryButton("重置配置", page_container, icon_text="↺")
        self._apply_button = PrimaryButton("应用更改", page_container, icon_text="✓")
        page_container.add_action(self._header_chip)
        page_container.add_action(self._reset_button)
        page_container.add_action(self._apply_button)

        self._workspace = self._build_workspace()
        self._footer_bar = self._build_footer_bar()
        page_container.add_widget(self._workspace)
        page_container.add_widget(self._footer_bar)

        _connect(getattr(self._reset_button, "clicked", None), self._handle_reset)
        _connect(getattr(self._apply_button, "clicked", None), self._handle_apply)
        self._select_template(self._selected_template_id)

    def _build_workspace(self) -> QWidget:
        """构建三栏工作区。"""

        left_panel = self._build_template_panel()
        center_panel = self._build_config_panel()
        right_panel = self._build_preview_panel()

        content_split = SplitPanel(
            split_ratio=(0.56, 0.44),
            minimum_sizes=(420, 360),
            parent=self,
        )
        content_split.set_widgets(center_panel, right_panel)

        root_split = SplitPanel(
            split_ratio=(0.28, 0.72),
            minimum_sizes=(300, 780),
            parent=self,
        )
        root_split.set_widgets(left_panel, content_split)
        return root_split

    def _build_template_panel(self) -> QWidget:
        """构建左侧模板选择区。"""

        scroll = ThemedScrollArea(self)
        content = QWidget(scroll)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        template_section = ContentSection("模板列表", icon="◎", parent=content)
        self._new_report_button = PrimaryButton("新建报告", template_section, icon_text="+")
        template_section.add_widget(self._new_report_button)

        for spec in self._templates:
            item = TemplateActionItem(spec, template_section)
            self._template_items[spec.template_id] = item
            template_section.add_widget(item)
            _connect(item.chosen, self._select_template)

        tips_section = ContentSection("使用提示", icon="◌", parent=content)
        tips_label = QLabel(
            "优先选择报告模板，再补充时间范围、维度、指标与过滤值；右侧预览会同步刷新。",
            tips_section,
        )
        _call(tips_label, "setObjectName", "reportSubtleText")
        _call(tips_label, "setWordWrap", True)
        tips_section.add_widget(tips_label)

        layout.addWidget(template_section)
        layout.addWidget(tips_section)
        layout.addStretch(1)
        scroll.set_content_widget(content)

        _connect(getattr(self._new_report_button, "clicked", None), self._handle_new_report)
        return scroll

    def _build_config_panel(self) -> QWidget:
        """构建中间配置区。"""

        scroll = ThemedScrollArea(self)
        content = QWidget(scroll)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        self._template_intro = QFrame(content)
        _call(self._template_intro, "setObjectName", "reportTemplateIntro")
        intro_layout = QVBoxLayout(self._template_intro)
        intro_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        intro_layout.setSpacing(SPACING_SM)
        self._template_intro_title = QLabel("日报模板", self._template_intro)
        _call(self._template_intro_title, "setObjectName", "reportPanelTitle")
        self._template_intro_body = QLabel("围绕日期、地区与核心销售指标快速生成执行日报。", self._template_intro)
        _call(self._template_intro_body, "setObjectName", "reportSubtleText")
        _call(self._template_intro_body, "setWordWrap", True)
        intro_layout.addWidget(self._template_intro_title)
        intro_layout.addWidget(self._template_intro_body)

        info_section = ContentSection("1. 报告信息", icon="①", parent=content)
        self._report_title_input = ThemedLineEdit(
            label="报告标题",
            placeholder="输入报告标题",
            helper_text="标题会直接同步到右侧预览封面。",
            parent=info_section,
        )
        self._range_combo = ThemedComboBox(label="时间范围", parent=info_section)
        self._compare_combo = ThemedComboBox(label="数据对比", items=COMPARE_OPTIONS, parent=info_section)
        info_section.add_widget(self._report_title_input)
        info_section.add_widget(self._range_combo)
        info_section.add_widget(self._compare_combo)

        select_section = ContentSection("2. 字段选择", icon="②", parent=content)
        self._dimensions_group = FormGroup(
            "分析维度",
            description="可多选；首个维度用于驱动右侧图表聚合。",
            parent=select_section,
        )
        self._metrics_group = FormGroup(
            "核心指标",
            description="可多选；首个指标用于计算主 KPI 与趋势图。",
            parent=select_section,
        )
        select_section.add_widget(self._dimensions_group)
        select_section.add_widget(self._metrics_group)

        filter_section = ContentSection("3. 筛选条件", icon="③", parent=content)
        self._filter_field_combo = ThemedComboBox(label="筛选字段", parent=filter_section)
        self._filter_value_input = ThemedLineEdit(
            label="筛选值",
            placeholder="例如：华东 / TikTok Shop / 利润款",
            helper_text="仅做方案配置预览，不会发起真实数据查询。",
            parent=filter_section,
        )
        self._filter_summary = QLabel("过滤规则：等待配置", filter_section)
        _call(self._filter_summary, "setObjectName", "reportFilterSummary")
        _call(self._filter_summary, "setWordWrap", True)
        filter_section.add_widget(self._filter_field_combo)
        filter_section.add_widget(self._filter_value_input)
        filter_section.add_widget(self._filter_summary)

        chart_section = ContentSection("4. 图表类型", icon="④", parent=content)
        self._chart_type_group = FormGroup(
            "可视化方案",
            description="切换后会实时影响右侧图表表达方式。",
            parent=chart_section,
        )
        self._chart_type_hint = QLabel("当前预览以“表格 + 趋势图”组合呈现。", chart_section)
        _call(self._chart_type_hint, "setObjectName", "reportSubtleText")
        _call(self._chart_type_hint, "setWordWrap", True)
        self._chart_type_group.set_field_widget(self._build_chart_type_widget())
        chart_section.add_widget(self._chart_type_group)
        chart_section.add_widget(self._chart_type_hint)

        layout.addWidget(self._template_intro)
        layout.addWidget(info_section)
        layout.addWidget(select_section)
        layout.addWidget(filter_section)
        layout.addWidget(chart_section)
        layout.addStretch(1)

        scroll.set_content_widget(content)

        _connect(getattr(self._report_title_input.line_edit, "textChanged", None), self._on_config_changed)
        _connect(getattr(self._range_combo.combo_box, "currentTextChanged", None), self._on_config_changed)
        _connect(getattr(self._compare_combo.combo_box, "currentTextChanged", None), self._on_config_changed)
        _connect(getattr(self._filter_field_combo.combo_box, "currentTextChanged", None), self._on_config_changed)
        _connect(getattr(self._filter_value_input.line_edit, "textChanged", None), self._on_config_changed)
        return scroll

    def _build_preview_panel(self) -> QWidget:
        """构建右侧实时预览区。"""

        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        header = QFrame(panel)
        _call(header, "setObjectName", "reportLiveHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        header_layout.setSpacing(SPACING_SM)

        live_dot = QLabel("", header)
        _call(live_dot, "setObjectName", "reportLiveDot")
        _call(live_dot, "setFixedSize", SPACING_SM + SPACING_XS, SPACING_SM + SPACING_XS)

        title_column = QVBoxLayout()
        title_column.setContentsMargins(0, 0, 0, 0)
        title_column.setSpacing(SPACING_XS)
        preview_title = QLabel("实时预览", header)
        _call(preview_title, "setObjectName", "reportPanelTitle")
        self._preview_subtitle = QLabel("预览会在字段、筛选和图表类型变化后立即刷新。", header)
        _call(self._preview_subtitle, "setObjectName", "reportSubtleText")
        title_column.addWidget(preview_title)
        title_column.addWidget(self._preview_subtitle)

        self._preview_time_label = QLabel("最后更新：--:--:--", header)
        _call(self._preview_time_label, "setObjectName", "reportSubtleText")

        header_layout.addWidget(live_dot)
        header_layout.addLayout(title_column, 1)
        header_layout.addWidget(self._preview_time_label)

        scroll = ThemedScrollArea(panel)
        content = QWidget(scroll)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(SPACING_XL)

        summary_section = ContentSection("报告摘要", icon="◎", parent=content)
        self._preview_doc_title = QLabel("日报 · 区域销售追踪", summary_section)
        _call(self._preview_doc_title, "setObjectName", "reportPreviewDocumentTitle")
        self._preview_note = QLabel("预览摘要等待生成。", summary_section)
        _call(self._preview_note, "setObjectName", "reportSubtleText")
        _call(self._preview_note, "setWordWrap", True)

        preview_metrics_row = QWidget(summary_section)
        metrics_layout = QHBoxLayout(preview_metrics_row)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(SPACING_MD)
        self._primary_metric_card = KPICard("主指标", "—", trend="flat", percentage="0.0%", caption="等待计算", parent=preview_metrics_row)
        self._coverage_card = KPICard("预览范围", "—", trend="flat", percentage="0 组", caption="等待计算", parent=preview_metrics_row)
        metrics_layout.addWidget(self._primary_metric_card, 1)
        metrics_layout.addWidget(self._coverage_card, 1)

        summary_section.add_widget(self._preview_doc_title)
        summary_section.add_widget(self._preview_note)
        summary_section.add_widget(preview_metrics_row)

        table_section = ContentSection("表格预览", icon="▦", parent=content)
        self._preview_table_host = QWidget(table_section)
        self._preview_table_layout = QVBoxLayout(self._preview_table_host)
        self._preview_table_layout.setContentsMargins(0, 0, 0, 0)
        self._preview_table_layout.setSpacing(0)
        table_section.add_widget(self._preview_table_host)

        chart_section = ContentSection("图表预览", icon="∿", parent=content)
        self._preview_chart = ChartWidget(chart_type="bar", title="预览趋势", parent=chart_section)
        self._preview_chart_hint = QLabel("图表说明等待生成。", chart_section)
        _call(self._preview_chart_hint, "setObjectName", "reportSubtleText")
        _call(self._preview_chart_hint, "setWordWrap", True)
        chart_section.add_widget(self._preview_chart)
        chart_section.add_widget(self._preview_chart_hint)

        content_layout.addWidget(summary_section)
        content_layout.addWidget(table_section)
        content_layout.addWidget(chart_section)
        content_layout.addStretch(1)

        scroll.set_content_widget(content)
        layout.addWidget(header)
        layout.addWidget(scroll, 1)
        return panel

    def _build_footer_bar(self) -> QWidget:
        """构建底部操作栏。"""

        footer = QFrame(self)
        _call(footer, "setObjectName", "reportFooterBar")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)

        self._footer_status_label = QLabel("当前状态：等待生成", footer)
        _call(self._footer_status_label, "setObjectName", "reportSubtleText")

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(SPACING_MD)
        self._export_pdf_button = SecondaryButton("导出 PDF", footer, icon_text="↓")
        self._export_excel_button = SecondaryButton("导出 Excel", footer, icon_text="⇲")
        self._generate_button = PrimaryButton("生成报告", footer, icon_text="⚡")
        button_row.addWidget(self._export_pdf_button)
        button_row.addWidget(self._export_excel_button)
        button_row.addWidget(self._generate_button)

        layout.addWidget(self._footer_status_label, 1)
        layout.addLayout(button_row)

        _connect(getattr(self._export_pdf_button, "clicked", None), lambda: self._handle_export("PDF"))
        _connect(getattr(self._export_excel_button, "clicked", None), lambda: self._handle_export("Excel"))
        _connect(getattr(self._generate_button, "clicked", None), self._handle_generate)
        return footer

    def _build_chart_type_widget(self) -> QWidget:
        """构建图表类型选择器。"""

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        self._chart_type_buttons = {}
        row_widget: QWidget | None = None
        row_layout: QHBoxLayout | None = None
        for index, (chart_type, icon) in enumerate(CHART_TYPE_META):
            if index % 3 == 0:
                row_widget = QWidget(container)
                row_layout = QHBoxLayout(row_widget)
                if row_layout is not None:
                    row_layout.setContentsMargins(0, 0, 0, 0)
                    row_layout.setSpacing(SPACING_SM)
                layout.addWidget(row_widget)
            button = QPushButton(f"{icon}\n{chart_type}", row_widget)
            _call(button, "setObjectName", "reportChartTypeButton")
            _call(button, "setMinimumHeight", BUTTON_HEIGHT * 2 + SPACING_SM)
            _connect(getattr(button, "clicked", None), lambda _checked=False, value=chart_type: self._set_chart_type(value))
            self._chart_type_buttons[chart_type] = button
            if row_layout is not None:
                row_layout.addWidget(button, 1)

        return container

    def _build_multi_choice_widget(
        self,
        options: Sequence[str],
        selected_values: Sequence[str],
        callback: Callable[[str], None],
        *,
        target: str,
    ) -> QWidget:
        """构建多选芯片集合。"""

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)
        button_map: dict[str, QPushButton] = {}

        row_widget: QWidget | None = None
        row_layout: QHBoxLayout | None = None
        for index, option in enumerate(options):
            if index % 2 == 0:
                row_widget = QWidget(container)
                row_layout = QHBoxLayout(row_widget)
                if row_layout is not None:
                    row_layout.setContentsMargins(0, 0, 0, 0)
                    row_layout.setSpacing(SPACING_SM)
                layout.addWidget(row_widget)
            button = QPushButton(option, row_widget)
            _call(button, "setObjectName", "reportChoiceChip")
            _call(button, "setMinimumHeight", BUTTON_HEIGHT + SPACING_XS)
            _connect(getattr(button, "clicked", None), lambda _checked=False, value=option: callback(value))
            button_map[option] = button
            if row_layout is not None:
                row_layout.addWidget(button, 1)

        if target == "dimensions":
            self._dimension_buttons = button_map
        else:
            self._metric_buttons = button_map

        for option, button in button_map.items():
            self._apply_choice_button_style(button, option in selected_values)
        return container

    def _apply_choice_button_style(self, button: QPushButton, active: bool) -> None:
        """刷新芯片按钮样式。"""

        colors = _palette()
        background = _rgba(_token("brand.primary"), 0.10) if active else colors.surface
        border = _token("brand.primary") if active else colors.border
        text_color = colors.text if active else colors.text_muted
        _call(
            button,
            "setStyleSheet",
            f"""
            QPushButton#reportChoiceChip {{
                background-color: {background};
                color: {text_color};
                border: 1px solid {border};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_MD}px {SPACING_XL}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
                text-align: left;
            }}
            QPushButton#reportChoiceChip:hover {{
                border-color: {_token('brand.primary')};
                color: {colors.text};
            }}
            """,
        )
        base_text = getattr(button, "text", lambda: "")()
        clean_text = str(base_text).replace("✓ ", "")
        _call(button, "setText", f"✓ {clean_text}" if active else clean_text)

    def _apply_chart_type_button_style(self, button: QPushButton, active: bool) -> None:
        """刷新图表类型按钮样式。"""

        colors = _palette()
        background = _rgba(_token("brand.primary"), 0.12) if active else colors.surface
        border = _token("brand.primary") if active else colors.border
        text_color = colors.text if active else colors.text_muted
        _call(
            button,
            "setStyleSheet",
            f"""
            QPushButton#reportChartTypeButton {{
                background-color: {background};
                color: {text_color};
                border: 1px solid {border};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_SM}px {SPACING_SM}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
                text-align: center;
            }}
            QPushButton#reportChartTypeButton:hover {{
                border-color: {_token('brand.primary')};
                color: {colors.text};
            }}
            """,
        )

    def _set_combo_items(self, combo: ThemedComboBox, items: Sequence[str], current_text: str) -> None:
        """统一写入下拉选项。"""

        combo_box = combo.combo_box
        _call(combo_box, "clear")
        add_items = getattr(combo_box, "addItems", None)
        if callable(add_items):
            add_items(list(items))
        else:
            for item in items:
                _call(combo_box, "addItem", item)
        target = current_text if current_text in items else (items[0] if items else "")
        if target:
            _call(combo_box, "setCurrentText", target)

    def _select_template(self, template_id: str) -> None:
        """切换当前模板并恢复默认配置。"""

        template = self._template_by_id(template_id)
        self._selected_template_id = template.template_id
        self._selected_dimensions = set(template.default_dimensions)
        self._selected_metrics = set(template.default_metrics)
        self._selected_chart_type = template.default_chart_type
        self._syncing_form = True

        self._template_intro_title.setText(template.name)
        self._template_intro_body.setText(template.summary)
        self._report_title_input.setText(template.default_title)
        self._set_combo_items(self._range_combo, template.range_options, template.default_range)
        self._set_combo_items(self._compare_combo, COMPARE_OPTIONS, template.default_compare)
        self._set_combo_items(self._filter_field_combo, template.dimensions, template.filter_field)
        self._filter_value_input.setText(template.filter_value)

        self._dimensions_group.set_field_widget(
            self._build_multi_choice_widget(
                template.dimensions,
                self._ordered_dimension_selection(),
                self._toggle_dimension,
                target="dimensions",
            )
        )
        self._metrics_group.set_field_widget(
            self._build_multi_choice_widget(
                template.metrics,
                self._ordered_metric_selection(),
                self._toggle_metric,
                target="metrics",
            )
        )

        self._syncing_form = False
        self._sync_template_items()
        self._sync_chart_type_buttons()
        self._generate_button.set_label_text("生成报告")
        self._refresh_preview(update_status=False)

    def _sync_template_items(self) -> None:
        """同步左侧模板选中态。"""

        current_template = self._template_by_id(self._selected_template_id)
        self._header_chip.setText(f"模板：{current_template.name}")
        for template_id, item in self._template_items.items():
            item.set_selected(template_id == self._selected_template_id)

    def _sync_chart_type_buttons(self) -> None:
        """同步图表类型按钮状态。"""

        for chart_type, button in self._chart_type_buttons.items():
            self._apply_chart_type_button_style(button, chart_type == self._selected_chart_type)

    def _ordered_dimension_selection(self) -> list[str]:
        """按模板定义顺序返回已选维度。"""

        template = self._template_by_id(self._selected_template_id)
        selected = [dimension for dimension in template.dimensions if dimension in self._selected_dimensions]
        return selected or [template.dimensions[0]]

    def _ordered_metric_selection(self) -> list[str]:
        """按模板定义顺序返回已选指标。"""

        template = self._template_by_id(self._selected_template_id)
        selected = [metric for metric in template.metrics if metric in self._selected_metrics]
        return selected or [template.metrics[0]]

    def _toggle_dimension(self, value: str) -> None:
        """切换维度勾选状态。"""

        if value in self._selected_dimensions and len(self._selected_dimensions) > 1:
            self._selected_dimensions.remove(value)
        else:
            self._selected_dimensions.add(value)
        for option, button in self._dimension_buttons.items():
            self._apply_choice_button_style(button, option in self._selected_dimensions)
        self._generate_button.set_label_text("生成报告")
        self._refresh_preview(update_status=False)

    def _toggle_metric(self, value: str) -> None:
        """切换指标勾选状态。"""

        if value in self._selected_metrics and len(self._selected_metrics) > 1:
            self._selected_metrics.remove(value)
        else:
            self._selected_metrics.add(value)
        for option, button in self._metric_buttons.items():
            self._apply_choice_button_style(button, option in self._selected_metrics)
        self._generate_button.set_label_text("生成报告")
        self._refresh_preview(update_status=False)

    def _set_chart_type(self, value: str) -> None:
        """切换图表类型。"""

        self._selected_chart_type = value
        self._sync_chart_type_buttons()
        self._generate_button.set_label_text("生成报告")
        self._refresh_preview(update_status=False)

    def _on_config_changed(self, *_args: object) -> None:
        """表单变更时刷新实时预览。"""

        if self._syncing_form:
            return
        self._generate_button.set_label_text("生成报告")
        self._refresh_preview(update_status=False)

    def _refresh_preview(self, *, update_status: bool) -> None:
        """根据当前配置刷新右侧预览。"""

        template = self._template_by_id(self._selected_template_id)
        selected_dimensions = self._ordered_dimension_selection()
        selected_metrics = self._ordered_metric_selection()
        primary_dimension = selected_dimensions[0]
        primary_metric = selected_metrics[0]
        records = list(template.records)

        chart_labels, chart_values = self._build_chart_series(records, primary_dimension, primary_metric)
        trend_direction, trend_percentage = _trend_direction(chart_values)
        title_text = self._report_title_input.text().strip() or template.default_title
        range_text = self._range_combo.current_text() or template.default_range
        compare_text = self._compare_combo.current_text() or template.default_compare
        filter_field = self._filter_field_combo.current_text() or template.filter_field
        filter_value = self._filter_value_input.text().strip() or template.filter_value

        self._preview_doc_title.setText(title_text)
        self._preview_subtitle.setText(f"{template.name} · {range_text} · {compare_text}")
        self._preview_time_label.setText(f"最后更新：{_now_label()}")
        self._chart_type_hint.setText(f"当前使用“{self._selected_chart_type}”表达 {primary_dimension} × {primary_metric}。")
        self._filter_summary.setText(f"过滤规则：{filter_field} = “{filter_value}” · 时间范围 {range_text} · 对比方式 {compare_text}")

        self._preview_note.setText(
            f"{template.preview_note} 当前将以“{primary_dimension}”作为横轴，重点观察“{primary_metric}”，筛选值锁定为 {filter_field} = {filter_value}。"
        )
        self._preview_chart_hint.setText(
            f"图表预览：{self._selected_chart_type}（内置渲染映射为 { _resolved_chart_widget_type(self._selected_chart_type) }），共 {len(chart_labels)} 个分组。"
        )

        primary_value = self._aggregate_metric(records, primary_metric)
        self._primary_metric_card.set_title(primary_metric)
        self._primary_metric_card.set_value(_format_metric_value(primary_metric, primary_value, compact=True))
        self._primary_metric_card.set_trend(trend_direction, trend_percentage)
        self._primary_metric_card.set_sparkline_data(chart_values)
        _call(self._primary_metric_card._caption_label, "setText", f"主图基于 {primary_dimension} 聚合")

        self._coverage_card.set_title("预览范围")
        self._coverage_card.set_value(f"{len(records)} 条")
        self._coverage_card.set_trend("flat", f"{len(chart_labels)} 组")
        self._coverage_card.set_sparkline_data([float(len(selected_dimensions)), float(len(selected_metrics)), float(len(chart_labels))])
        _call(self._coverage_card._caption_label, "setText", f"{len(selected_dimensions)} 维度 · {len(selected_metrics)} 指标")

        self._preview_chart.set_chart_type(_resolved_chart_widget_type(self._selected_chart_type))
        self._preview_chart._title = f"{title_text} · {primary_metric}"
        self._preview_chart.set_unit(_chart_unit(primary_metric))
        self._preview_chart.set_data(chart_values, chart_labels)

        headers, rows = self._build_preview_table(records, selected_dimensions, selected_metrics)
        self._replace_preview_table(headers, rows)

        if update_status:
            self._footer_status_label.setText(f"当前状态：{self._last_action_text}")
        else:
            self._footer_status_label.setText(
                f"当前状态：模板 {template.name} · 图表 {self._selected_chart_type} · 维度 {len(selected_dimensions)} · 指标 {len(selected_metrics)}"
            )

    def _build_chart_series(self, records: Sequence[dict[str, object]], dimension: str, metric: str) -> tuple[list[str], list[float]]:
        """按选定维度聚合图表序列。"""

        grouped_labels: list[str] = []
        grouped_values: dict[str, list[float]] = {}
        for record in records:
            label = str(record.get(dimension, "未命名"))
            if label not in grouped_values:
                grouped_labels.append(label)
                grouped_values[label] = []
            grouped_values[label].append(float(record.get(metric, 0.0)))

        values: list[float] = []
        for label in grouped_labels:
            group = grouped_values.get(label, [])
            if not group:
                values.append(0.0)
                continue
            raw_value = sum(group) / len(group) if _is_ratio_metric(metric) or _is_multiplier_metric(metric) else sum(group)
            values.append(_chart_value(metric, raw_value))
        return grouped_labels, values

    def _aggregate_metric(self, records: Sequence[dict[str, object]], metric: str) -> float:
        """汇总主指标。"""

        values = [float(record.get(metric, 0.0)) for record in records]
        if not values:
            return 0.0
        if _is_ratio_metric(metric) or _is_multiplier_metric(metric):
            return sum(values) / len(values)
        return sum(values)

    def _build_preview_table(
        self,
        records: Sequence[dict[str, object]],
        dimensions: Sequence[str],
        metrics: Sequence[str],
    ) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
        """生成右侧表格预览数据。"""

        primary_metric = metrics[0]
        metric_values = [float(record.get(primary_metric, 0.0)) for record in records]
        average_value = sum(metric_values) / len(metric_values) if metric_values else 0.0
        headers = (*dimensions, *metrics, "状态")
        rows: list[tuple[str, ...]] = []

        for record in records[:6]:
            status = self._status_text(float(record.get(primary_metric, 0.0)), average_value)
            row = [str(record.get(dimension, "—")) for dimension in dimensions]
            row.extend(_format_metric_value(metric, float(record.get(metric, 0.0))) for metric in metrics)
            row.append(status)
            rows.append(tuple(row))
        return tuple(headers), tuple(rows)

    @staticmethod
    def _status_text(value: float, average_value: float) -> str:
        """根据指标值生成状态文案。"""

        if average_value <= 0:
            return "稳定"
        if value >= average_value * 1.08:
            return "领先"
        if value <= average_value * 0.92:
            return "观察"
        return "稳定"

    def _replace_preview_table(self, headers: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
        """重建预览表格以支持动态表头。"""

        _clear_layout(self._preview_table_layout)

        self._preview_table = DataTable(headers=headers, rows=rows, page_size=5, empty_text="暂无预览数据", parent=self._preview_table_host)
        self._preview_table_layout.addWidget(self._preview_table)

    def _handle_new_report(self) -> None:
        """重置到默认模板。"""

        self._last_action_text = "已创建新报告草稿"
        self._select_template(self._templates[0].template_id)
        self._footer_status_label.setText(f"当前状态：{self._last_action_text}")

    def _handle_reset(self) -> None:
        """重置当前模板配置。"""

        self._last_action_text = "已重置为模板默认配置"
        self._select_template(self._selected_template_id)
        self._footer_status_label.setText(f"当前状态：{self._last_action_text}")

    def _handle_apply(self) -> None:
        """应用当前配置。"""

        self._last_action_text = f"已应用《{self._report_title_input.text().strip() or self._template_by_id(self._selected_template_id).default_title}》配置"
        self._refresh_preview(update_status=True)

    def _handle_generate(self) -> None:
        """模拟生成报告。"""

        template = self._template_by_id(self._selected_template_id)
        title_text = self._report_title_input.text().strip() or template.default_title
        self._last_action_text = f"已生成报告：{title_text}"
        self._generate_button.set_label_text("已生成")
        self._refresh_preview(update_status=True)

    def _handle_export(self, export_format: str) -> None:
        """模拟导出报告。"""

        template = self._template_by_id(self._selected_template_id)
        title_text = self._report_title_input.text().strip() or template.default_title
        self._last_action_text = f"已导出 {export_format}：{title_text}"
        self._refresh_preview(update_status=True)

    def _template_by_id(self, template_id: str) -> ReportTemplateSpec:
        """根据 ID 返回模板。"""

        return next(template for template in self._templates if template.template_id == template_id)

    def _apply_styles(self) -> None:
        """应用页面级样式。"""

        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#reportGeneratorPage {{
                background-color: {colors.surface_alt};
            }}
            QFrame#reportTemplateIntro,
            QFrame#reportLiveHeader,
            QFrame#reportFooterBar {{
                background-color: {colors.surface};
                border: 1px solid {_rgba(_token('brand.primary'), 0.18)};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#reportHeaderChip {{
                background-color: {_rgba(_token('brand.primary'), 0.10)};
                color: {_token('brand.primary')};
                border: 1px solid {_rgba(_token('brand.primary'), 0.24)};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_SM}px {SPACING_LG}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QLabel#reportPanelTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#reportPreviewDocumentTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#reportSubtleText {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                background: transparent;
            }}
            QLabel#reportFilterSummary {{
                background-color: {_rgba(_token('brand.primary'), 0.08)};
                color: {colors.text};
                border: 1px dashed {_rgba(_token('brand.primary'), 0.24)};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_MD}px {SPACING_LG}px;
                font-size: {_static_token('font.size.sm')};
            }}
            QLabel#reportLiveDot {{
                background-color: {_token('status.success')};
                border-radius: {(SPACING_SM + SPACING_XS) // 2}px;
            }}
            """,
        )

    @staticmethod
    def _build_templates() -> list[ReportTemplateSpec]:
        """构建页面使用的模板数据。"""

        return [
            ReportTemplateSpec(
                template_id="daily_report",
                name="日报",
                icon="☼",
                summary="围绕日期、地区与销售主指标，适合每日站会快速复盘。",
                default_title="日报 · 区域销售追踪",
                range_options=("最近7天", "最近14天", "自定义范围"),
                default_range="最近7天",
                default_compare="环比 (MoM)",
                dimensions=("日期", "地区", "渠道", "品类"),
                metrics=("销售额", "订单量", "毛利率", "转化率"),
                default_dimensions=("日期", "地区"),
                default_metrics=("销售额", "订单量"),
                default_chart_type="表格",
                filter_field="地区",
                filter_value="华东",
                preview_note="适合晨会同步昨日表现与异常波动，兼顾销量与转化表现。",
                records=(
                    {"日期": "03-01", "地区": "华东", "渠道": "短视频", "品类": "家居", "销售额": 124000.0, "订单量": 840.0, "毛利率": 0.284, "转化率": 0.061},
                    {"日期": "03-02", "地区": "华南", "渠道": "短视频", "品类": "美妆", "销售额": 96800.0, "订单量": 690.0, "毛利率": 0.261, "转化率": 0.054},
                    {"日期": "03-03", "地区": "华东", "渠道": "商城", "品类": "3C", "销售额": 138400.0, "订单量": 902.0, "毛利率": 0.307, "转化率": 0.066},
                    {"日期": "03-04", "地区": "华中", "渠道": "短视频", "品类": "母婴", "销售额": 88400.0, "订单量": 614.0, "毛利率": 0.248, "转化率": 0.049},
                    {"日期": "03-05", "地区": "华东", "渠道": "短视频", "品类": "服饰", "销售额": 156200.0, "订单量": 1038.0, "毛利率": 0.322, "转化率": 0.071},
                    {"日期": "03-06", "地区": "西南", "渠道": "短视频", "品类": "家清", "销售额": 79200.0, "订单量": 566.0, "毛利率": 0.239, "转化率": 0.045},
                ),
            ),
            ReportTemplateSpec(
                template_id="weekly_report",
                name="周报",
                icon="☷",
                summary="聚焦周维度趋势与区域结构，便于复盘资源投放节奏。",
                default_title="周报 · 经营趋势复盘",
                range_options=("最近4周", "最近8周", "本季度"),
                default_range="最近4周",
                default_compare="环比 (MoM)",
                dimensions=("周次", "地区", "渠道", "品类"),
                metrics=("销售额", "订单量", "毛利率", "转化率"),
                default_dimensions=("周次", "品类"),
                default_metrics=("销售额", "毛利率"),
                default_chart_type="折线图",
                filter_field="品类",
                filter_value="利润款",
                preview_note="适合在周复盘中观察资源加码后的趋势拐点与结构变化。",
                records=(
                    {"周次": "W08", "地区": "华东", "渠道": "短视频", "品类": "利润款", "销售额": 428000.0, "订单量": 3020.0, "毛利率": 0.301, "转化率": 0.068},
                    {"周次": "W09", "地区": "华南", "渠道": "短视频", "品类": "利润款", "销售额": 462000.0, "订单量": 3186.0, "毛利率": 0.314, "转化率": 0.071},
                    {"周次": "W10", "地区": "华东", "渠道": "商城", "品类": "引流款", "销售额": 389000.0, "订单量": 3510.0, "毛利率": 0.228, "转化率": 0.053},
                    {"周次": "W11", "地区": "华中", "渠道": "短视频", "品类": "利润款", "销售额": 506000.0, "订单量": 3378.0, "毛利率": 0.327, "转化率": 0.074},
                    {"周次": "W12", "地区": "西南", "渠道": "短视频", "品类": "新品", "销售额": 441000.0, "订单量": 2934.0, "毛利率": 0.256, "转化率": 0.057},
                    {"周次": "W13", "地区": "华东", "渠道": "短视频", "品类": "利润款", "销售额": 534000.0, "订单量": 3620.0, "毛利率": 0.336, "转化率": 0.078},
                ),
            ),
            ReportTemplateSpec(
                template_id="monthly_report",
                name="月报",
                icon="◫",
                summary="适用于管理层查看月度经营脉络、结构占比与年度累计走势。",
                default_title="月报 · 销售与渠道总览",
                range_options=("最近3个月", "最近6个月", "年度累计"),
                default_range="最近6个月",
                default_compare="同比 (YoY)",
                dimensions=("月份", "地区", "渠道", "品类"),
                metrics=("销售额", "订单量", "毛利率", "转化率"),
                default_dimensions=("月份", "渠道"),
                default_metrics=("销售额", "订单量"),
                default_chart_type="柱状图",
                filter_field="渠道",
                filter_value="短视频",
                preview_note="适合拉通管理层视角，快速判断渠道结构是否健康。",
                records=(
                    {"月份": "2025-10", "地区": "华东", "渠道": "短视频", "品类": "家居", "销售额": 1860000.0, "订单量": 13240.0, "毛利率": 0.286, "转化率": 0.058},
                    {"月份": "2025-11", "地区": "华南", "渠道": "短视频", "品类": "美妆", "销售额": 2014000.0, "订单量": 14062.0, "毛利率": 0.298, "转化率": 0.061},
                    {"月份": "2025-12", "地区": "华东", "渠道": "商城", "品类": "3C", "销售额": 2148000.0, "订单量": 14908.0, "毛利率": 0.312, "转化率": 0.064},
                    {"月份": "2026-01", "地区": "华中", "渠道": "短视频", "品类": "服饰", "销售额": 1952000.0, "订单量": 13810.0, "毛利率": 0.274, "转化率": 0.056},
                    {"月份": "2026-02", "地区": "西南", "渠道": "短视频", "品类": "母婴", "销售额": 2286000.0, "订单量": 15420.0, "毛利率": 0.325, "转化率": 0.067},
                    {"月份": "2026-03", "地区": "华东", "渠道": "短视频", "品类": "家清", "销售额": 2470000.0, "订单量": 16380.0, "毛利率": 0.338, "转化率": 0.071},
                ),
            ),
            ReportTemplateSpec(
                template_id="competitor_report",
                name="竞品分析",
                icon="⚑",
                summary="观察竞品在不同平台与内容形式下的投放与互动效率。",
                default_title="竞品分析 · 互动与转化监控",
                range_options=("最近7天", "最近30天", "自定义范围"),
                default_range="最近30天",
                default_compare="不对比",
                dimensions=("竞品", "平台", "内容类型", "地区"),
                metrics=("互动率", "投放量", "转化率", "销售额"),
                default_dimensions=("竞品", "平台"),
                default_metrics=("互动率", "转化率"),
                default_chart_type="折线图",
                filter_field="平台",
                filter_value="TikTok Shop",
                preview_note="适合快速判断竞品内容打法是否进入加速期，辅助选题与排期。",
                records=(
                    {"竞品": "NovaHome", "平台": "TikTok Shop", "内容类型": "测评", "地区": "东南亚", "互动率": 0.082, "投放量": 126.0, "转化率": 0.051, "销售额": 382000.0},
                    {"竞品": "LumaTech", "平台": "TikTok Shop", "内容类型": "教程", "地区": "欧美", "互动率": 0.076, "投放量": 118.0, "转化率": 0.048, "销售额": 356000.0},
                    {"竞品": "AsterFit", "平台": "Shopee Live", "内容类型": "开箱", "地区": "东南亚", "互动率": 0.064, "投放量": 92.0, "转化率": 0.039, "销售额": 288000.0},
                    {"竞品": "CloudSkin", "平台": "TikTok Shop", "内容类型": "口播", "地区": "华东", "互动率": 0.089, "投放量": 135.0, "转化率": 0.055, "销售额": 418000.0},
                    {"竞品": "VitaGlow", "平台": "Amazon", "内容类型": "测评", "地区": "欧美", "互动率": 0.058, "投放量": 74.0, "转化率": 0.034, "销售额": 244000.0},
                    {"竞品": "EchoGear", "平台": "TikTok Shop", "内容类型": "剧情", "地区": "华南", "互动率": 0.081, "投放量": 122.0, "转化率": 0.049, "销售额": 368000.0},
                ),
            ),
            ReportTemplateSpec(
                template_id="profit_report",
                name="利润报告",
                icon="¥",
                summary="围绕 SKU、渠道与利润效率，适合经营复盘与资源倾斜判断。",
                default_title="利润报告 · SKU 结构洞察",
                range_options=("最近30天", "本季度", "年度累计"),
                default_range="本季度",
                default_compare="环比 (MoM)",
                dimensions=("SKU", "品类", "渠道", "地区"),
                metrics=("利润额", "毛利率", "退款率", "ROI"),
                default_dimensions=("SKU", "渠道"),
                default_metrics=("利润额", "毛利率"),
                default_chart_type="柱状图",
                filter_field="渠道",
                filter_value="短视频",
                preview_note="适合将利润款与引流款拆开看，快速定位应该追加预算的 SKU。",
                records=(
                    {"SKU": "无线降噪耳机 X1", "品类": "3C数码", "渠道": "短视频", "地区": "华东", "利润额": 84300.0, "毛利率": 0.318, "退款率": 0.027, "ROI": 2.81},
                    {"SKU": "桌面补光灯 Pro", "品类": "数码配件", "渠道": "短视频", "地区": "华南", "利润额": 56800.0, "毛利率": 0.286, "退款率": 0.022, "ROI": 2.36},
                    {"SKU": "AI 翻译录音笔 S2", "品类": "办公数码", "渠道": "商城", "地区": "华东", "利润额": 69300.0, "毛利率": 0.294, "退款率": 0.019, "ROI": 2.48},
                    {"SKU": "智能香薰机 Air", "品类": "家居生活", "渠道": "短视频", "地区": "华中", "利润额": 47200.0, "毛利率": 0.267, "退款率": 0.024, "ROI": 2.11},
                    {"SKU": "4K 家用投影仪", "品类": "家居影音", "渠道": "短视频", "地区": "西南", "利润额": 102600.0, "毛利率": 0.342, "退款率": 0.018, "ROI": 3.04},
                    {"SKU": "磁吸车载支架 Max", "品类": "车载配件", "渠道": "短视频", "地区": "华东", "利润额": 35100.0, "毛利率": 0.231, "退款率": 0.031, "ROI": 1.86},
                ),
            ),
        ]


__all__ = ["ReportGeneratorPage"]
