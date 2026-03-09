# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false

from __future__ import annotations

"""CRM 客户关系管理页面。"""

from dataclasses import dataclass, replace
from datetime import datetime
from typing import cast

from ....core.qt import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    ContentSection,
    DataTable,
    FilterDropdown,
    FloatingActionButton,
    InfoCard,
    KPICard,
    PageContainer,
    PrimaryButton,
    ProfileCard,
    SearchBar,
    SecondaryButton,
    SplitPanel,
    StatusBadge,
    TabBar,
    TagChip,
    ThemedLineEdit,
    ThemedScrollArea,
    TimelineWidget,
)
from ...components.inputs import (
    RADIUS_LG,
    RADIUS_MD,
    SPACING_2XL,
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
from ...components.tags import BadgeTone
from ..base_page import BasePage

TABLE_PAGE_SIZE = 6
SEARCH_MIN_WIDTH = SPACING_2XL * 12
FILTER_MIN_WIDTH = SPACING_2XL * 7
TAB_TITLES = ("全部客户", "活跃", "潜在", "流失")
ACTIVE_STATUSES = {"已成交", "活跃跟进"}
POTENTIAL_STATUSES = {"潜在机会"}
LOST_STATUSES = {"流失预警"}
DESKTOP_PAGE_MAX_WIDTH = 1760


@dataclass(frozen=True)
class CRMInteraction:
    """客户互动记录。"""

    timestamp: str
    title: str
    content: str
    event_type: str = "info"


@dataclass(frozen=True)
class CRMCustomer:
    """客户档案。"""

    customer_id: str
    name: str
    company: str
    persona: str
    contact: str
    phone: str
    wechat: str
    owner: str
    status: str
    recent_interaction: str
    customer_value: str
    monthly_revenue: str
    interaction_count: int
    deal_rate: str
    insight: str
    next_step: str
    segment_tags: tuple[str, ...]
    interactions: tuple[CRMInteraction, ...]


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _clear_layout(layout: object) -> None:
    """清空布局中的部件。"""

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


class CRMPage(BasePage):
    """CRM 客户关系管理页。"""

    default_route_id: RouteId = RouteId("crm_customer_management")
    default_display_name: str = "CRM客户关系管理"
    default_icon_name: str = "hub"

    def setup_ui(self) -> None:
        """构建 CRM 页面主体。"""

        self._all_customers = self._build_demo_customers()
        self._visible_customers: list[CRMCustomer] = []
        self._cell_widgets: list[QWidget] = []
        self._active_tab_index = 0
        self._current_customer_id: str | None = self._all_customers[0].customer_id if self._all_customers else None
        self._syncing_selection = False
        self._new_customer_seed = len(self._all_customers) + 1

        _call(self, "setObjectName", "crmPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        self._batch_follow_button = PrimaryButton("批量建联", self, icon_text="✦")
        self._export_button = SecondaryButton("导出名单", self, icon_text="⇪")

        page_container = PageContainer(
            title=self.display_name,
            description="集中完成客户分层、互动复盘、商机跟进与价值提升，让运营与销售协同始终在线。",
            actions=(self._batch_follow_button, self._export_button),
            max_width=DESKTOP_PAGE_MAX_WIDTH,
            parent=self,
        )
        self.layout.addWidget(page_container)

        split_panel = SplitPanel(split_ratio=(0.6, 0.4), minimum_sizes=(720, 400), parent=page_container)
        _call(split_panel, "setObjectName", "crmMainSplit")
        split_panel.set_widgets(self._build_workspace_panel(), self._build_detail_panel())
        page_container.add_widget(split_panel)

        _connect(self._search_bar.search_changed, self._apply_filters)
        _connect(self._status_filter.filter_changed, self._apply_filters)
        _connect(self._value_filter.filter_changed, self._apply_filters)
        _connect(self._customer_table.row_selected, self._handle_table_selection)
        _connect(self._customer_table.row_double_clicked, self._handle_table_selection)
        _connect(self._tab_bar.tab_changed, self._handle_tab_changed)
        _connect(getattr(self._add_customer_fab, "clicked", None), self._handle_add_customer)
        _connect(getattr(self._batch_follow_button, "clicked", None), self._handle_batch_follow_up)
        _connect(getattr(self._export_button, "clicked", None), self._handle_export_customers)
        _connect(getattr(self._follow_up_button, "clicked", None), self._handle_record_follow_up)
        _connect(getattr(self._promote_button, "clicked", None), self._handle_promote_customer)
        _connect(getattr(self._insight_card.action_button, "clicked", None), self._refresh_customer_brief)

        table_model = getattr(self._customer_table, "_model", None)
        if table_model is not None:
            _connect(getattr(table_model, "modelReset", None), self._refresh_cell_widgets)
            _connect(getattr(table_model, "layoutChanged", None), self._refresh_cell_widgets)

        self._apply_filters()

    def _build_workspace_panel(self) -> QWidget:
        panel = QWidget(self)
        _call(panel, "setObjectName", "crmWorkspace")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        kpi_row = QWidget(panel)
        _call(kpi_row, "setObjectName", "crmStatusStrip")
        kpi_layout = QHBoxLayout(kpi_row)
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        kpi_layout.setSpacing(SPACING_LG)
        self._kpi_cards = [
            KPICard(parent=kpi_row),
            KPICard(parent=kpi_row),
            KPICard(parent=kpi_row),
            KPICard(parent=kpi_row),
        ]
        for card in self._kpi_cards:
            kpi_layout.addWidget(card, 1)

        self._toolbar = QWidget(panel)
        _call(self._toolbar, "setObjectName", "crmFilterBar")
        toolbar_layout = QHBoxLayout(self._toolbar)
        toolbar_layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        toolbar_layout.setSpacing(SPACING_XL)

        self._search_bar = SearchBar("搜索客户名称、公司、微信或客户经理")
        _call(self._search_bar, "setMinimumWidth", SEARCH_MIN_WIDTH)
        self._status_filter = FilterDropdown(
            label="客户状态",
            items=("已成交", "活跃跟进", "潜在机会", "流失预警"),
            include_all=True,
        )
        self._value_filter = FilterDropdown(
            label="客户价值",
            items=("战略客户", "高价值", "成长型", "观察"),
            include_all=True,
        )
        _call(self._status_filter, "setMinimumWidth", FILTER_MIN_WIDTH)
        _call(self._value_filter, "setMinimumWidth", FILTER_MIN_WIDTH)

        toolbar_layout.addWidget(self._search_bar, 1)
        toolbar_layout.addWidget(self._status_filter)
        toolbar_layout.addWidget(self._value_filter)

        self._tab_bar = TabBar(panel)
        tab_specs: tuple[tuple[str, str, BadgeTone], ...] = (
            ("全部客户", "覆盖全部客户池，适合做分层巡检与批量回访。", "brand"),
            ("活跃", "近期有成交或在持续沟通的重点客户，优先推进复购。", "success"),
            ("潜在", "有明确需求但尚未锁单，建议强化报价与样品跟进。", "warning"),
            ("流失", "最近互动明显下降，需要重启沟通或挽回计划。", "error"),
        )
        for title, description, tone in tab_specs:
            self._tab_bar.add_tab(title, self._build_tab_hint(description, tone))

        self._table_section = ContentSection("客户列表", icon="◎", parent=panel)
        self._summary_bar = QWidget(self._table_section)
        _call(self._summary_bar, "setObjectName", "crmSummaryBar")
        summary_layout = QHBoxLayout(self._summary_bar)
        summary_layout.setContentsMargins(SPACING_XL, SPACING_MD, SPACING_XL, SPACING_MD)
        summary_layout.setSpacing(SPACING_MD)

        self._result_badge = StatusBadge("筛选结果 0", tone="brand", parent=self._summary_bar)
        self._high_value_badge = StatusBadge("高价值 0", tone="success", parent=self._summary_bar)
        self._selection_badge = StatusBadge("未选中客户", tone="neutral", parent=self._summary_bar)
        self._tab_chip = TagChip("当前分组：全部客户", tone="info", parent=self._summary_bar)

        summary_layout.addWidget(self._result_badge)
        summary_layout.addWidget(self._high_value_badge)
        summary_layout.addWidget(self._selection_badge)
        summary_layout.addStretch(1)
        summary_layout.addWidget(self._tab_chip)

        self._customer_table = DataTable(
            headers=("名称", "公司", "联系方式", "状态", "最近互动", "客户价值"),
            rows=(),
            page_size=TABLE_PAGE_SIZE,
            empty_text="当前筛选条件下暂无客户",
            parent=self._table_section,
        )
        _call(self._customer_table.table_view, "setMinimumHeight", SPACING_2XL * 17)

        self._table_section.add_widget(self._summary_bar)
        self._table_section.add_widget(self._customer_table)

        fab_row = QWidget(panel)
        _call(fab_row, "setObjectName", "crmFabRow")
        fab_layout = QHBoxLayout(fab_row)
        fab_layout.setContentsMargins(0, 0, 0, 0)
        fab_layout.setSpacing(0)
        self._add_customer_fab = FloatingActionButton(icon_text="＋", tooltip="新增客户", parent=fab_row)
        fab_layout.addStretch(1)
        fab_layout.addWidget(self._add_customer_fab)

        layout.addWidget(kpi_row)
        layout.addWidget(self._toolbar)
        layout.addWidget(self._tab_bar)
        layout.addWidget(self._table_section, 1)
        layout.addWidget(fab_row)
        return panel

    def _build_detail_panel(self) -> QWidget:
        panel = QWidget(self)
        _call(panel, "setObjectName", "crmDetailPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll_area = ThemedScrollArea(panel)
        layout.addWidget(scroll_area)

        content = QWidget(panel)
        _call(content, "setObjectName", "crmDetailContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, SPACING_XS, 0)
        content_layout.setSpacing(SPACING_LG)
        scroll_area.set_content_widget(content)

        self._detail_header = QWidget(content)
        _call(self._detail_header, "setObjectName", "crmDetailHeader")
        header_layout = QVBoxLayout(self._detail_header)
        header_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        header_layout.setSpacing(SPACING_SM)

        self._detail_eyebrow = QLabel("当前查看", self._detail_header)
        _call(self._detail_eyebrow, "setObjectName", "crmDetailEyebrow")
        self._detail_name = QLabel("暂无客户", self._detail_header)
        _call(self._detail_name, "setObjectName", "crmDetailName")

        detail_meta_row = QWidget(self._detail_header)
        meta_layout = QHBoxLayout(detail_meta_row)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(SPACING_MD)
        self._detail_id = QLabel("请从左侧表格选择客户", detail_meta_row)
        _call(self._detail_id, "setObjectName", "crmDetailId")
        self._detail_status_badge = StatusBadge("未选择", tone="neutral", parent=detail_meta_row)
        self._detail_value_chip = TagChip("价值待定", tone="neutral", parent=detail_meta_row)
        meta_layout.addWidget(self._detail_id, 1)
        meta_layout.addWidget(self._detail_status_badge)
        meta_layout.addWidget(self._detail_value_chip)

        header_layout.addWidget(self._detail_eyebrow)
        header_layout.addWidget(self._detail_name)
        header_layout.addWidget(detail_meta_row)

        self._profile_host = QWidget(content)
        _call(self._profile_host, "setObjectName", "crmProfileHost")
        self._profile_layout = QVBoxLayout(self._profile_host)
        self._profile_layout.setContentsMargins(0, 0, 0, 0)
        self._profile_layout.setSpacing(0)

        self._insight_card = InfoCard(
            title="跟进建议",
            description="选择客户后可查看该客户的最近需求、价值判断与下一步建议。",
            icon="✦",
            action_text="生成跟进建议",
            parent=content,
        )

        self._tags_section = ContentSection("客户标签", icon="⌘", parent=content)
        self._tag_container = QWidget(self._tags_section)
        _call(self._tag_container, "setObjectName", "crmTagWrap")
        self._tag_layout = QHBoxLayout(self._tag_container)
        self._tag_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        self._tag_layout.setSpacing(SPACING_SM)
        self._tags_section.add_widget(self._tag_container)

        self._contact_section = ContentSection("联系信息", icon="☎", parent=content)
        self._phone_field = self._build_readonly_field("联系电话", "用于电话回访与紧急沟通")
        self._wechat_field = self._build_readonly_field("企业微信", "用于发送报价、素材与群发通知")
        self._owner_field = self._build_readonly_field("客户经理", "当前负责该客户的跟进人")
        self._next_step_field = self._build_readonly_field("下一步动作", "由 CRM 节奏自动提醒")

        row_one = QWidget(self._contact_section)
        row_one_layout = QHBoxLayout(row_one)
        row_one_layout.setContentsMargins(0, 0, 0, 0)
        row_one_layout.setSpacing(SPACING_LG)
        row_one_layout.addWidget(self._phone_field, 1)
        row_one_layout.addWidget(self._wechat_field, 1)

        row_two = QWidget(self._contact_section)
        row_two_layout = QHBoxLayout(row_two)
        row_two_layout.setContentsMargins(0, 0, 0, 0)
        row_two_layout.setSpacing(SPACING_LG)
        row_two_layout.addWidget(self._owner_field, 1)
        row_two_layout.addWidget(self._next_step_field, 1)

        action_row = QWidget(self._contact_section)
        _call(action_row, "setObjectName", "crmActionRow")
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(SPACING_MD)
        self._follow_up_button = PrimaryButton("记录跟进", action_row, icon_text="↗")
        self._promote_button = SecondaryButton("推进成交", action_row, icon_text="◎")
        action_layout.addWidget(self._follow_up_button)
        action_layout.addWidget(self._promote_button)
        action_layout.addStretch(1)

        self._contact_section.add_widget(row_one)
        self._contact_section.add_widget(row_two)
        self._contact_section.add_widget(action_row)

        self._timeline_section = ContentSection("互动时间线", icon="↻", parent=content)
        self._timeline_widget = TimelineWidget()
        self._timeline_section.add_widget(self._timeline_widget)

        content_layout.addWidget(self._detail_header)
        content_layout.addWidget(self._profile_host)
        content_layout.addWidget(self._insight_card)
        content_layout.addWidget(self._tags_section)
        content_layout.addWidget(self._contact_section)
        content_layout.addWidget(self._timeline_section)
        content_layout.addStretch(1)

        for field in (self._phone_field, self._wechat_field, self._owner_field, self._next_step_field):
            _call(field.line_edit, "setReadOnly", True)

        return panel

    def _build_readonly_field(self, label: str, helper_text: str) -> ThemedLineEdit:
        field = ThemedLineEdit(label=label, placeholder="", helper_text=helper_text)
        return field

    def _build_tab_hint(self, description: str, tone: BadgeTone) -> QWidget:
        card = QFrame(self)
        _call(card, "setObjectName", "crmTabHint")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_SM)

        badge = StatusBadge("分群洞察", tone=tone, parent=card)
        title = QLabel(description, card)
        _call(title, "setObjectName", "crmTabHintBody")
        _call(title, "setWordWrap", True)
        layout.addWidget(badge, 0)
        layout.addWidget(title)

        colors = _palette()
        _call(
            card,
            "setStyleSheet",
            f"""
            QFrame#crmTabHint {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#crmTabHintBody {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.md')};
                line-height: 1.6;
            }}
            """,
        )
        return card

    def _handle_tab_changed(self, index: int) -> None:
        self._active_tab_index = index
        self._apply_filters()

    def _handle_table_selection(self, row_index: int) -> None:
        if self._syncing_selection:
            return
        if 0 <= row_index < len(self._visible_customers):
            self._current_customer_id = self._visible_customers[row_index].customer_id
            self._update_summary_bar()
            self._update_detail_panel(self._visible_customers[row_index])

    def _apply_filters(self, *_args: object) -> None:
        query = self._search_bar.text().strip().lower()
        status_filter = self._status_filter.current_text()
        value_filter = self._value_filter.current_text()

        filtered: list[CRMCustomer] = []
        for customer in self._all_customers:
            if not self._matches_tab(customer):
                continue
            haystack = " ".join(
                (
                    customer.customer_id,
                    customer.name,
                    customer.company,
                    customer.contact,
                    customer.wechat,
                    customer.owner,
                )
            ).lower()
            if query and query not in haystack:
                continue
            if status_filter != "全部" and customer.status != status_filter:
                continue
            if value_filter != "全部" and customer.customer_value != value_filter:
                continue
            filtered.append(customer)

        self._visible_customers = filtered
        self._customer_table.set_rows(self._rows_from_customers(filtered))
        self._update_kpi_cards()
        self._update_summary_bar()
        self._sync_selected_customer()

    def _sync_selected_customer(self) -> None:
        if not self._visible_customers:
            self._current_customer_id = None
            self._update_detail_panel(None)
            return

        visible_ids = {customer.customer_id for customer in self._visible_customers}
        if self._current_customer_id not in visible_ids:
            self._current_customer_id = self._visible_customers[0].customer_id

        target_index = next(
            (index for index, customer in enumerate(self._visible_customers) if customer.customer_id == self._current_customer_id),
            0,
        )
        self._syncing_selection = True
        self._customer_table.select_absolute_row(target_index)
        self._syncing_selection = False
        self._update_summary_bar()
        self._update_detail_panel(self._visible_customers[target_index])

    def _update_kpi_cards(self) -> None:
        total_visible = len(self._visible_customers)
        total_all = max(len(self._all_customers), 1)
        active_count = sum(1 for customer in self._visible_customers if customer.status in ACTIVE_STATUSES)
        potential_count = sum(1 for customer in self._visible_customers if customer.status in POTENTIAL_STATUSES)
        high_value_count = sum(1 for customer in self._visible_customers if customer.customer_value in {"战略客户", "高价值"})

        metrics = (
            ("客户总量", total_visible, total_visible / total_all, "当前筛选覆盖", self._sparkline(total_visible)),
            ("活跃客户", active_count, active_count / max(total_visible, 1), "持续推进中", self._sparkline(active_count)),
            ("潜在商机", potential_count, potential_count / max(total_visible, 1), "等待锁单", self._sparkline(potential_count)),
            ("高价值客户", high_value_count, high_value_count / max(total_visible, 1), "可重点加深合作", self._sparkline(high_value_count)),
        )

        for card, (title, value, ratio, caption, sparkline) in zip(self._kpi_cards, metrics):
            trend: str = "flat"
            if ratio >= 0.45:
                trend = "up"
            elif ratio <= 0.15:
                trend = "down"
            card.set_title(title)
            card.set_value(str(value))
            card.set_trend(trend, f"{ratio * 100:.0f}%")
            card.set_sparkline_data(sparkline)
            _call(getattr(card, "_caption_label", None), "setText", caption)

    def _update_summary_bar(self) -> None:
        high_value = sum(1 for customer in self._visible_customers if customer.customer_value in {"战略客户", "高价值"})
        _call(self._result_badge, "setText", f"筛选结果 {len(self._visible_customers)}")
        _call(self._high_value_badge, "setText", f"高价值 {high_value}")
        _call(self._tab_chip, "set_text", f"当前分组：{TAB_TITLES[self._active_tab_index]}")

        selected_customer = self._selected_customer()
        if selected_customer is None:
            _call(self._selection_badge, "setText", "未选中客户")
            self._selection_badge.set_tone("neutral")
            return
        _call(self._selection_badge, "setText", f"当前：{selected_customer.name}")
        self._selection_badge.set_tone(self._status_tone(selected_customer.status))

    def _update_detail_panel(self, customer: CRMCustomer | None) -> None:
        if customer is None:
            _call(self._detail_name, "setText", "暂无客户")
            _call(self._detail_id, "setText", "请调整筛选条件或新增客户")
            _call(self._detail_status_badge, "setText", "未选择")
            self._detail_status_badge.set_tone("neutral")
            _call(self._detail_value_chip, "set_text", "价值待定")
            self._detail_value_chip.set_tone("neutral")
            self._phone_field.setText("")
            self._wechat_field.setText("")
            self._owner_field.setText("")
            self._next_step_field.setText("")
            self._insight_card.set_description("当前没有可展示的客户，请切换筛选条件或创建新的客户档案。")
            self._replace_profile_card(None)
            self._rebuild_tag_chips(())
            self._timeline_widget.set_events([])
            return

        _call(self._detail_name, "setText", customer.name)
        _call(self._detail_id, "setText", f"{customer.customer_id} · {customer.company} · 负责人：{customer.owner}")
        _call(self._detail_status_badge, "setText", customer.status)
        self._detail_status_badge.set_tone(self._status_tone(customer.status))
        _call(self._detail_value_chip, "set_text", customer.customer_value)
        self._detail_value_chip.set_tone(self._value_tone(customer.customer_value))

        self._phone_field.setText(customer.phone)
        self._wechat_field.setText(customer.wechat)
        self._owner_field.setText(customer.owner)
        self._next_step_field.setText(customer.next_step)
        self._insight_card.set_description(customer.insight)
        self._replace_profile_card(customer)
        self._rebuild_tag_chips(customer.segment_tags)
        self._timeline_widget.set_events(
            [
                {
                    "timestamp": item.timestamp,
                    "title": item.title,
                    "content": item.content,
                    "type": item.event_type,
                }
                for item in customer.interactions
            ]
        )
    def _replace_profile_card(self, customer: CRMCustomer | None) -> None:
        _clear_layout(self._profile_layout)
        if customer is None:
            placeholder = InfoCard(
                title="客户详情待选择",
                description="左侧列表支持搜索、分群和状态筛选，选中后即可查看完整互动时间线。",
                icon="◎",
                action_text="等待选择",
                parent=self._profile_host,
            )
            _call(getattr(placeholder, "action_button", None), "setEnabled", False)
            self._profile_layout.addWidget(placeholder)
            return

        profile_card = ProfileCard(
            name=customer.name,
            role=f"{customer.company} · {customer.persona}",
            stats=(
                ("月度成交", customer.monthly_revenue),
                ("互动总数", str(customer.interaction_count)),
                ("成交率", customer.deal_rate),
            ),
            parent=self._profile_host,
        )
        self._profile_layout.addWidget(profile_card)

    def _rebuild_tag_chips(self, tags: tuple[str, ...]) -> None:
        _clear_layout(self._tag_layout)
        if not tags:
            empty_badge = StatusBadge("暂无标签", tone="neutral", parent=self._tag_container)
            self._tag_layout.addWidget(empty_badge)
            self._tag_layout.addStretch(1)
            return

        for text in tags:
            chip = TagChip(text, tone="brand" if "高" in text or "复购" in text else "neutral", parent=self._tag_container)
            self._tag_layout.addWidget(chip)
        self._tag_layout.addStretch(1)

    def _handle_record_follow_up(self) -> None:
        customer = self._selected_customer()
        if customer is None:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_interaction = CRMInteraction(
            timestamp=timestamp,
            title="电话跟进",
            content=f"已与 {customer.name} 确认近期排期与需求优先级，客户希望本周内收到更细的执行方案。",
            event_type="success",
        )
        updated = replace(
            customer,
            recent_interaction="刚刚完成电话跟进",
            interaction_count=customer.interaction_count + 1,
            insight="客户反馈积极，建议尽快发送定制方案与排期说明，缩短从沟通到成交的等待时间。",
            next_step="24 小时内发送报价单与执行排期",
            interactions=(new_interaction, *customer.interactions),
        )
        self._replace_customer(updated)

    def _handle_promote_customer(self) -> None:
        customer = self._selected_customer()
        if customer is None:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_status = "已成交"
        new_value = "战略客户" if customer.customer_value != "战略客户" else customer.customer_value
        updated = replace(
            customer,
            status=new_status,
            customer_value=new_value,
            recent_interaction="刚刚确认合作推进",
            insight="客户已进入合作推进阶段，建议同步售后与内容团队准备首轮交付方案。",
            next_step="安排合同确认与首轮执行排期",
            interactions=(
                CRMInteraction(
                    timestamp=timestamp,
                    title="合作推进",
                    content="客户确认合作意向，进入签约与排期对接阶段。",
                    event_type="success",
                ),
                *customer.interactions,
            ),
        )
        self._replace_customer(updated)
        if self._active_tab_index != 0:
            self._tab_bar.set_current(0)

    def _handle_batch_follow_up(self) -> None:
        touched = 0
        updated_customers: list[CRMCustomer] = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        for customer in self._all_customers:
            if touched >= 3 or customer not in self._visible_customers:
                updated_customers.append(customer)
                continue
            if customer.status in LOST_STATUSES:
                updated_customers.append(customer)
                continue
            updated_customers.append(
                replace(
                    customer,
                    recent_interaction="已创建今日批量跟进任务",
                    next_step="今日 18:00 前完成一轮回访",
                    interactions=(
                        CRMInteraction(
                            timestamp=timestamp,
                            title="批量建联任务",
                            content="系统已为该客户创建今日跟进计划，提醒运营同学在晚间前完成回访。",
                            event_type="info",
                        ),
                        *customer.interactions,
                    ),
                )
            )
            touched += 1
        self._all_customers = updated_customers
        self._insight_card.set_description(f"已为当前视图中的 {touched} 位客户创建今日跟进任务，可直接在时间线中查看回访记录。")
        self._apply_filters()

    def _handle_export_customers(self) -> None:
        selected = self._selected_customer()
        suffix = f"，当前焦点客户为 {selected.name}" if selected is not None else ""
        self._insight_card.set_description(f"已根据当前筛选结果整理出 {len(self._visible_customers)} 位客户的导出名单{suffix}。")

    def _handle_add_customer(self) -> None:
        new_customer = self._make_new_customer(self._new_customer_seed)
        self._new_customer_seed += 1
        self._all_customers.append(new_customer)
        self._current_customer_id = new_customer.customer_id
        self._search_bar.setText("")
        self._status_filter.set_current_text("全部")
        self._value_filter.set_current_text("全部")
        self._tab_bar.set_current(0)

    def _refresh_customer_brief(self) -> None:
        customer = self._selected_customer()
        if customer is None:
            return
        self._insight_card.set_description(
            f"建议围绕“{customer.segment_tags[0] if customer.segment_tags else customer.customer_value}”切入沟通，"
            f"先确认 {customer.next_step}，再补发最近一次互动对应的素材与报价。"
        )

    def _replace_customer(self, updated: CRMCustomer) -> None:
        self._all_customers = [updated if customer.customer_id == updated.customer_id else customer for customer in self._all_customers]
        self._current_customer_id = updated.customer_id
        self._apply_filters()

    def _refresh_cell_widgets(self) -> None:
        self._clear_cell_widgets()
        table_view = self._customer_table.table_view
        set_index_widget = getattr(table_view, "setIndexWidget", None)
        table_model = getattr(self._customer_table, "_model", None)
        if not callable(set_index_widget) or table_model is None:
            return

        row_count = table_model.rowCount()
        for page_row in range(row_count):
            absolute_row = table_model.absolute_row(page_row)
            if not (0 <= absolute_row < len(self._visible_customers)):
                continue
            customer = self._visible_customers[absolute_row]
            status_widget = self._build_status_cell(customer)
            value_widget = self._build_value_cell(customer)
            set_index_widget(table_model.index(page_row, 3), status_widget)
            set_index_widget(table_model.index(page_row, 5), value_widget)
            self._cell_widgets.extend((status_widget, value_widget))

    def _clear_cell_widgets(self) -> None:
        for widget in self._cell_widgets:
            _call(widget, "setParent", None)
            _call(widget, "deleteLater")
        self._cell_widgets.clear()

    def _build_status_cell(self, customer: CRMCustomer) -> QWidget:
        cell = QWidget(self._customer_table)
        layout = QHBoxLayout(cell)
        layout.setContentsMargins(SPACING_XS, SPACING_XS, SPACING_XS, SPACING_XS)
        layout.setSpacing(0)
        badge = StatusBadge(customer.status, tone=self._status_tone(customer.status), parent=cell)
        layout.addStretch(1)
        layout.addWidget(badge)
        layout.addStretch(1)
        return cell

    def _build_value_cell(self, customer: CRMCustomer) -> QWidget:
        cell = QWidget(self._customer_table)
        layout = QHBoxLayout(cell)
        layout.setContentsMargins(SPACING_XS, SPACING_XS, SPACING_XS, SPACING_XS)
        layout.setSpacing(0)
        chip = TagChip(customer.customer_value, tone=self._value_tone(customer.customer_value), parent=cell)
        layout.addStretch(1)
        layout.addWidget(chip)
        layout.addStretch(1)
        return cell

    def _matches_tab(self, customer: CRMCustomer) -> bool:
        title = TAB_TITLES[self._active_tab_index]
        if title == "活跃":
            return customer.status in ACTIVE_STATUSES
        if title == "潜在":
            return customer.status in POTENTIAL_STATUSES
        if title == "流失":
            return customer.status in LOST_STATUSES
        return True

    def _rows_from_customers(self, customers: list[CRMCustomer]) -> list[tuple[object, ...]]:
        return [
            (
                customer.name,
                customer.company,
                customer.contact,
                customer.status,
                customer.recent_interaction,
                customer.customer_value,
            )
            for customer in customers
        ]

    def _selected_customer(self) -> CRMCustomer | None:
        if self._current_customer_id is None:
            return None
        return next((customer for customer in self._all_customers if customer.customer_id == self._current_customer_id), None)

    def _status_tone(self, status: str) -> BadgeTone:
        mapping: dict[str, BadgeTone] = {
            "已成交": "success",
            "活跃跟进": "brand",
            "潜在机会": "warning",
            "流失预警": "error",
        }
        return mapping.get(status, "neutral")

    def _value_tone(self, value: str) -> BadgeTone:
        mapping: dict[str, BadgeTone] = {
            "战略客户": "brand",
            "高价值": "success",
            "成长型": "info",
            "观察": "neutral",
        }
        return mapping.get(value, "neutral")

    def _sparkline(self, value: int) -> list[int]:
        base = max(value, 1)
        return [max(1, base - 2), max(1, base - 1), base, max(1, base + 1), base, max(1, base + 2), max(1, base + 1)]

    def _make_new_customer(self, seed: int) -> CRMCustomer:
        names = ("顾明朗", "温书意", "孟知远", "沈嘉禾")
        companies = ("苏州云岚服饰", "福州海屿家清", "长沙辰木文具", "合肥栖川宠物")
        personas = ("品牌招商主管", "渠道采购经理", "内容增长负责人", "电商运营总监")
        owners = ("梁若溪", "邵以安", "顾念秋", "简修远")
        tags = (
            ("新品切入", "内容加热", "报价待发"),
            ("复购潜力", "品牌联名", "样品已寄"),
            ("内容共创", "短视频投流", "高响应"),
            ("低频唤醒", "老客重启", "需二次建联"),
        )
        index = (seed - 1) % len(names)
        customer_id = f"CRM-{seed:04d}"
        name = names[index]
        company = companies[index]
        owner = owners[index]
        wechat_handle = cast(str, f"tk_{seed:04d}_{index + 1}")
        return CRMCustomer(
            customer_id=customer_id,
            name=name,
            company=company,
            persona=personas[index],
            contact=f"139 66{seed:02d} 28{seed:02d} · 微信 {wechat_handle}",
            phone=f"139 66{seed:02d} 28{seed:02d}",
            wechat=wechat_handle,
            owner=owner,
            status="潜在机会",
            recent_interaction="刚刚创建客户档案",
            customer_value="成长型",
            monthly_revenue="¥0",
            interaction_count=1,
            deal_rate="15%",
            insight="新客户已入池，建议 24 小时内完成首次建联并同步询盘背景。",
            next_step="今天完成首次问候与需求确认",
            segment_tags=tags[index],
            interactions=(
                CRMInteraction(
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    title="创建客户档案",
                    content="已完成基础信息录入，等待运营同学发起首次沟通。",
                    event_type="info",
                ),
            ),
        )

    def _build_demo_customers(self) -> list[CRMCustomer]:
        return [
            CRMCustomer(
                customer_id="CRM-1001",
                name="苏清妍",
                company="杭州织羽品牌管理",
                persona="品牌采购负责人",
                contact="138 1168 2301 · 微信 suqingyan88",
                phone="138 1168 2301",
                wechat="suqingyan88",
                owner="林予安",
                status="已成交",
                recent_interaction="10 分钟前确认续费节奏",
                customer_value="战略客户",
                monthly_revenue="¥128,400",
                interaction_count=36,
                deal_rate="48%",
                insight="客户已连续两个月追加预算，对短视频专场和短视频矩阵的联动方案接受度高，适合继续做年度框架合作。",
                next_step="明天中午前发送 4 月专场排期与预算拆分",
                segment_tags=("年度续费", "短视频专场", "高复购", "决策快"),
                interactions=(
                    CRMInteraction("2026-03-09 10:20", "续费确认", "客户确认继续执行 4 月短视频专场，并追加 20% 达人预算。", "success"),
                    CRMInteraction("2026-03-08 16:40", "微信群沟通", "已在企微群同步最新爆款素材与投放复盘，客户反馈希望继续加码女装类目。", "info"),
                    CRMInteraction("2026-03-07 11:00", "线下会面", "完成季度复盘，客户对达人复投机制表示认可。", "success"),
                ),
            ),
            CRMCustomer(
                customer_id="CRM-1002",
                name="陈泽楷",
                company="广州星桥供应链",
                persona="电商运营总监",
                contact="137 2456 9902 · 微信 czk_xingqiao",
                phone="137 2456 9902",
                wechat="czk_xingqiao",
                owner="沈知序",
                status="活跃跟进",
                recent_interaction="今天 09:30 已发送报价清单",
                customer_value="高价值",
                monthly_revenue="¥86,900",
                interaction_count=24,
                deal_rate="39%",
                insight="客户正在比较两套投流方案，对达人分层与 SKU 组合测试较感兴趣，报价阶段响应较快。",
                next_step="今晚前补发达人分层报价与试投周期建议",
                segment_tags=("报价阶段", "达人投流", "3C 配件"),
                interactions=(
                    CRMInteraction("2026-03-09 09:30", "报价发送", "已发送短视频投流与达人分层报价清单，等待客户确认预算区间。", "info"),
                    CRMInteraction("2026-03-08 18:10", "语音沟通", "客户希望追加试投周期对比数据，重点关注单场 ROI。", "warning"),
                    CRMInteraction("2026-03-07 14:55", "样本复盘", "运营团队已展示近 14 天素材表现曲线，客户认可优化方向。", "success"),
                ),
            ),
            CRMCustomer(
                customer_id="CRM-1003",
                name="林若岚",
                company="深圳禾木家居",
                persona="内容增长负责人",
                contact="136 8031 4418 · 微信 ruolan_home",
                phone="136 8031 4418",
                wechat="ruolan_home",
                owner="许知遥",
                status="潜在机会",
                recent_interaction="昨天 20:15 询问家居类脚本案例",
                customer_value="成长型",
                monthly_revenue="¥24,600",
                interaction_count=11,
                deal_rate="22%",
                insight="客户对家居软装类短视频脚本案例很感兴趣，但仍需看到更贴近自身产品的执行样本。",
                next_step="发送家居类脚本模板与样品拍摄建议",
                segment_tags=("家居软装", "案例沟通", "需要样本"),
                interactions=(
                    CRMInteraction("2026-03-08 20:15", "私信咨询", "客户询问家居类脚本模板，希望本周拿到 3 套可直接修改的版本。", "warning"),
                    CRMInteraction("2026-03-07 17:20", "需求访谈", "确认客户目标是提升新品上架首周转化，重点关注评论区互动。", "info"),
                    CRMInteraction("2026-03-06 13:30", "首次建联", "通过朋友圈内容与客户取得联系，已约定二次沟通时间。", "info"),
                ),
            ),
            CRMCustomer(
                customer_id="CRM-1004",
                name="周铭轩",
                company="宁波海策母婴",
                persona="渠道采购经理",
                contact="135 6620 5516 · 微信 zhoumx_baby",
                phone="135 6620 5516",
                wechat="zhoumx_baby",
                owner="顾星阑",
                status="流失预警",
                recent_interaction="5 天前未回复复盘报告",
                customer_value="观察",
                monthly_revenue="¥11,200",
                interaction_count=7,
                deal_rate="14%",
                insight="客户近两周互动明显下降，且对上次复盘报告未给出反馈，需要以更轻量的切口重新激活。",
                next_step="发送精简版增长建议并预约 10 分钟回访",
                segment_tags=("沉默客户", "母婴用品", "需重新唤醒"),
                interactions=(
                    CRMInteraction("2026-03-04 19:10", "复盘未读", "周报与 ROI 复盘已发送，但客户暂未回复。", "error"),
                    CRMInteraction("2026-03-01 15:40", "活动邀约", "邀请客户参加平台母婴专场活动，客户表示暂缓。", "warning"),
                    CRMInteraction("2026-02-27 10:05", "数据同步", "已同步近 30 天短视频 GMV 走势与评论关键词。", "info"),
                ),
            ),
            CRMCustomer(
                customer_id="CRM-1005",
                name="何嘉怡",
                company="义乌熙岸饰品",
                persona="品牌主理人",
                contact="139 7723 8026 · 微信 hjy_xian",
                phone="139 7723 8026",
                wechat="hjy_xian",
                owner="纪时安",
                status="活跃跟进",
                recent_interaction="今天 11:05 确认达人寄样名单",
                customer_value="高价值",
                monthly_revenue="¥58,300",
                interaction_count=19,
                deal_rate="35%",
                insight="客户在饰品新品节奏上非常积极，对寄样和达人联动动作配合快，适合尽快推进联名主题内容。",
                next_step="确认首批达人寄样地址与短视频发布时间",
                segment_tags=("饰品新品", "达人寄样", "快反"),
                interactions=(
                    CRMInteraction("2026-03-09 11:05", "寄样确认", "客户确认 8 位达人寄样名单，并补充新品主推款式。", "success"),
                    CRMInteraction("2026-03-08 13:15", "选品沟通", "运营团队完成新品选款，客户希望突出高客单礼盒套组。", "info"),
                    CRMInteraction("2026-03-07 09:40", "脚本讨论", "已确认主推内容调性为节日礼赠与穿搭场景。", "info"),
                ),
            ),
            CRMCustomer(
                customer_id="CRM-1006",
                name="唐亦辰",
                company="厦门澜起个护",
                persona="品类负责人",
                contact="138 9044 6607 · 微信 tang_yc_care",
                phone="138 9044 6607",
                wechat="tang_yc_care",
                owner="温晚舟",
                status="已成交",
                recent_interaction="昨天已确认复购套装素材方向",
                customer_value="战略客户",
                monthly_revenue="¥142,000",
                interaction_count=31,
                deal_rate="51%",
                insight="客户对复购套装和高频内容测试有成熟认知，适合建立长期内容工厂机制。",
                next_step="输出本月复购套装短视频矩阵与复盘节奏",
                segment_tags=("个护复购", "内容工厂", "长期合作"),
                interactions=(
                    CRMInteraction("2026-03-08 18:30", "复购方向确认", "客户确认聚焦头皮护理复购套装，并锁定两位核心主播档期。", "success"),
                    CRMInteraction("2026-03-06 16:00", "数据复盘", "近 7 天转化成本下降，客户同意扩大测试预算。", "success"),
                    CRMInteraction("2026-03-05 11:25", "素材筛选", "已完成 A/B 素材挑选，计划下周开始批量投放。", "info"),
                ),
            ),
            CRMCustomer(
                customer_id="CRM-1007",
                name="许安澜",
                company="青岛沐禾户外",
                persona="渠道拓展经理",
                contact="137 8801 7345 · 微信 xuanlan_outdoor",
                phone="137 8801 7345",
                wechat="xuanlan_outdoor",
                owner="白行舟",
                status="潜在机会",
                recent_interaction="2 小时前索取春季露营主题选品单",
                customer_value="成长型",
                monthly_revenue="¥18,500",
                interaction_count=9,
                deal_rate="19%",
                insight="客户对露营与轻户外场景内容需求明确，若能快速给到主题选品与脚本，推进概率较高。",
                next_step="发送春季露营主题选品单与脚本提纲",
                segment_tags=("轻户外", "春季露营", "待发送选品单"),
                interactions=(
                    CRMInteraction("2026-03-09 14:05", "索取选品单", "客户希望今天拿到春季露营主题选品清单，用于内部评估。", "warning"),
                    CRMInteraction("2026-03-08 10:20", "需求确认", "明确客户更关注高转化套组和评论互动设计。", "info"),
                    CRMInteraction("2026-03-06 15:50", "渠道推荐", "通过合作伙伴推荐接入，已完成第一次需求了解。", "info"),
                ),
            ),
            CRMCustomer(
                customer_id="CRM-1008",
                name="宋知夏",
                company="成都未见茶饮",
                persona="品牌增长经理",
                contact="136 5509 8821 · 微信 songzx_tea",
                phone="136 5509 8821",
                wechat="songzx_tea",
                owner="裴景和",
                status="活跃跟进",
                recent_interaction="今天 08:50 回传门店活动排期",
                customer_value="高价值",
                monthly_revenue="¥64,700",
                interaction_count=16,
                deal_rate="33%",
                insight="客户节奏快，门店联动和城市话题结合度高，适合推动同城流量与达人探店并行。",
                next_step="根据门店排期确定同城达人探店档期",
                segment_tags=("同城流量", "探店达人", "活动排期已定"),
                interactions=(
                    CRMInteraction("2026-03-09 08:50", "排期回传", "客户已回传 3 月门店活动档期，适合结合同城达人探店推广。", "success"),
                    CRMInteraction("2026-03-08 12:40", "素材确认", "确认使用春日限定饮品做短视频主推主题。", "info"),
                    CRMInteraction("2026-03-07 20:10", "评论互动复盘", "上周互动关键词以新品口味、门店福利为主，建议继续强化福利导向。", "info"),
                ),
            ),
        ]

    def _apply_page_styles(self) -> None:
        colors = _palette()
        primary_soft = _rgba(_token("brand.primary"), 0.08)
        primary_border = _rgba(_token("brand.primary"), 0.18)
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#crmPage {{
                background-color: {colors.surface_alt};
            }}
            QWidget#crmStatusStrip,
            QWidget#crmFabRow,
            QWidget#crmActionRow {{
                background: transparent;
                border: none;
            }}
            QWidget#crmWorkspace,
            QWidget#crmDetailPanel,
            QWidget#crmDetailContent,
            QWidget#crmProfileHost {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#crmSummaryBar,
            QWidget#crmDetailHeader,
            QWidget#crmTagWrap {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#crmFilterBar {{
                background-color: {colors.surface};
                border: 1px solid {primary_border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#crmDetailHeader {{
                background-color: {primary_soft};
                border-color: {primary_border};
            }}
            QLabel#crmDetailEyebrow {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QLabel#crmDetailName {{
                background: transparent;
                color: {colors.text};
                font-size: {_static_token('font.size.xxl')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#crmDetailId {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QFrame#contentSection {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QSplitter#splitPanelCore::handle {{
                background-color: {primary_soft};
                border-radius: {RADIUS_MD}px;
            }}
            QSplitter#splitPanelCore::handle:hover {{
                background-color: {_token('brand.primary')};
            }}
            """,
        )
