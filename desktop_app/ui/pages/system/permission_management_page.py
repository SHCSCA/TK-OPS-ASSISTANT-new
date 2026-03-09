# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportCallIssue=false
from __future__ import annotations

"""权限管理页面。"""

from dataclasses import dataclass, replace
from datetime import datetime

from ....core.qt import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    ContentSection,
    DataTable,
    FilterDropdown,
    InfoCard,
    KPICard,
    PageContainer,
    PlaceholderDialog,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    StatusBadge,
    TagChip,
)
from ...components.inputs import (
    BUTTON_HEIGHT,
    RADIUS_LG,
    RADIUS_MD,
    SPACING_2XL,
    SPACING_MD,
    SPACING_LG,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    ToggleSwitch,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ...components.tags import BadgeTone
from ..base_page import BasePage


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


@dataclass(frozen=True)
class UserRecord:
    """用户记录。"""

    username: str
    role: str
    department: str
    status: str
    last_login: str
    action_label: str
    is_admin: bool
    active: bool
    pending: bool


@dataclass(frozen=True)
class AuditRecord:
    """审计日志记录。"""

    happened_at: str
    operator: str
    action: str
    target: str
    result: str
    detail: str


@dataclass(frozen=True)
class RoleRecord:
    """角色定义。"""

    name: str
    level_text: str
    member_count: int
    summary: str
    tone: BadgeTone


@dataclass(frozen=True)
class ModulePermissionRecord:
    """权限矩阵中的模块行。"""

    module_name: str
    module_group: str
    description: str
    super_admin: bool
    operations_manager: bool
    content_creator: bool
    analyst: bool
    standard_user: bool


ROLE_ORDER: tuple[str, ...] = (
    "超级管理员",
    "运营经理",
    "内容创作者",
    "数据分析师",
    "普通用户",
)


ROLES: tuple[RoleRecord, ...] = (
    RoleRecord("超级管理员", "L5 全局控制", 2, "拥有系统全部配置、审批和风险动作权限。", "error"),
    RoleRecord("运营经理", "L4 业务管理", 4, "管理账号、任务、发布计划与团队协作规则。", "brand"),
    RoleRecord("内容创作者", "L3 创作执行", 3, "处理素材、脚本、文案与内容投放前准备。", "success"),
    RoleRecord("数据分析师", "L3 分析决策", 2, "可查看报表、日志、复盘与关键经营指标。", "info"),
    RoleRecord("普通用户", "L2 基础访问", 2, "保留基础查看与有限动作权限。", "neutral"),
)


USERS: tuple[UserRecord, ...] = (
    UserRecord("陈启航", "超级管理员", "系统平台组", "正常", "今天 11:20", "编辑", True, True, False),
    UserRecord("林若溪", "超级管理员", "系统平台组", "正常", "今天 10:56", "编辑", True, True, False),
    UserRecord("赵明锐", "运营经理", "华东运营中心", "正常", "今天 10:31", "编辑", True, True, False),
    UserRecord("宋安可", "运营经理", "华南运营中心", "正常", "今天 09:58", "编辑", True, True, False),
    UserRecord("何知夏", "内容创作者", "创意内容组", "正常", "今天 09:40", "编辑", False, True, False),
    UserRecord("唐以沫", "内容创作者", "创意内容组", "停用", "昨天 18:42", "恢复", False, False, False),
    UserRecord("顾言舟", "数据分析师", "经营分析组", "正常", "今天 09:26", "编辑", False, True, False),
    UserRecord("沈知岚", "数据分析师", "经营分析组", "待审批", "从未登录", "审批", False, False, True),
    UserRecord("许念初", "普通用户", "客户成功组", "正常", "今天 08:55", "编辑", False, True, False),
    UserRecord("周景川", "普通用户", "客户成功组", "待审批", "从未登录", "审批", False, False, True),
)


AUDITS: tuple[AuditRecord, ...] = (
    AuditRecord("今天 11:18", "陈启航", "调整权限", "赵明锐", "成功", "新增“版本升级”查看与执行权限。"),
    AuditRecord("今天 10:52", "林若溪", "审批用户", "沈知岚", "待同步", "审批已通过，等待首次登录激活。"),
    AuditRecord("今天 10:15", "赵明锐", "重置角色", "内容创作者组", "成功", "统一恢复为创作标准权限模板。"),
    AuditRecord("今天 09:48", "陈启航", "停用账号", "唐以沫", "成功", "因项目轮岗，暂时停用内容操作权限。"),
    AuditRecord("今天 09:10", "顾言舟", "申请提升权限", "数据分析师", "审批中", "申请开放日志中心导出能力。"),
    AuditRecord("今天 08:56", "林若溪", "批量导出名单", "全部用户", "成功", "导出当前活跃用户与角色分布。"),
    AuditRecord("今天 08:42", "宋安可", "创建用户", "周景川", "成功", "创建客户成功组新成员账号。"),
    AuditRecord("昨天 18:30", "陈启航", "启用审计策略", "权限管理", "成功", "将高风险动作全部纳入二次记录。"),
    AuditRecord("昨天 17:54", "赵明锐", "修改部门", "许念初", "成功", "从运营支持组迁移到客户成功组。"),
    AuditRecord("昨天 17:20", "林若溪", "调整审批流", "待审批用户", "成功", "改为超级管理员与业务负责人双签。"),
)


MODULE_PERMISSIONS: tuple[ModulePermissionRecord, ...] = (
    ModulePermissionRecord("系统设置", "系统", "修改启动、网络、存储与高级配置。", True, True, False, False, False),
    ModulePermissionRecord("权限管理", "系统", "管理角色、审批用户与审计记录。", True, True, False, False, False),
    ModulePermissionRecord("日志中心", "系统", "查看实时日志、导出历史记录。", True, True, False, True, False),
    ModulePermissionRecord("版本升级", "系统", "检查更新、下载升级包与回滚。", True, True, False, False, False),
    ModulePermissionRecord("素材工厂", "内容", "查看素材库、导入和批量整理素材。", True, True, True, False, True),
    ModulePermissionRecord("脚本提取", "内容", "处理脚本生成、标签和导出。", True, True, True, False, True),
    ModulePermissionRecord("经营分析", "分析", "查看趋势报表、实验结果与复盘。", True, True, False, True, True),
    ModulePermissionRecord("自动化任务", "运营", "创建任务、暂停、恢复与批量执行。", True, True, False, False, False),
    ModulePermissionRecord("数据采集", "自动化", "触发采集链路、查看抓取状态。", True, True, False, True, False),
    ModulePermissionRecord("发布调度", "运营", "创建发布计划、审批与排期。", True, True, True, False, False),
)

DESKTOP_PAGE_MAX_WIDTH = 1760


class PermissionManagementPage(BasePage):
    """权限管理页。"""

    default_route_id: RouteId = RouteId("permission_management")
    default_display_name: str = "权限管理"
    default_icon_name: str = "admin_panel_settings"

    def __init__(self, parent: object | None = None) -> None:
        self._all_users: list[UserRecord] = list(USERS)
        self._visible_users: list[UserRecord] = list(USERS)
        self._audit_records: list[AuditRecord] = list(AUDITS)
        self._permission_rows: list[ModulePermissionRecord] = list(MODULE_PERMISSIONS)
        self._selected_user_index = 0
        self._active_role = ROLE_ORDER[0]
        self._search_keyword = ""
        self._role_filter_value = "全部"
        self._department_filter_value = "全部"
        self._status_filter_value = "全部"
        self._status_message = "权限矩阵与用户清单已加载，可进行审批、编辑与角色梳理。"

        self._page_container: PageContainer | None = None
        self._summary_cards: dict[str, KPICard] = {}
        self._focus_badge: StatusBadge | None = None
        self._focus_text: QLabel | None = None
        self._role_overview_card: InfoCard | None = None
        self._result_badge: StatusBadge | None = None
        self._selection_badge: StatusBadge | None = None
        self._permission_hint_label: QLabel | None = None
        self._search_bar: SearchBar | None = None
        self._role_filter: FilterDropdown | None = None
        self._department_filter: FilterDropdown | None = None
        self._status_filter: FilterDropdown | None = None
        self._add_user_button: PrimaryButton | None = None
        self._edit_user_button: SecondaryButton | None = None
        self._approve_button: SecondaryButton | None = None
        self._user_table: DataTable | None = None
        self._audit_table: DataTable | None = None
        self._role_cards: dict[str, QFrame] = {}
        self._role_badges: dict[str, StatusBadge] = {}
        self._role_descriptions: dict[str, QLabel] = {}
        self._matrix_headers: dict[str, QLabel] = {}
        self._matrix_buttons: dict[tuple[str, str], QPushButton] = {}
        self._matrix_row_notes: dict[str, QLabel] = {}
        self._matrix_toggle_switches: dict[str, ToggleSwitch] = {}
        self._dialog_ref: PlaceholderDialog | None = None

        super().__init__(parent=parent)

    def setup_ui(self) -> None:
        """构建权限管理页面。"""

        _call(self, "setObjectName", "permissionManagementPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self._add_user_button = PrimaryButton("新增用户", self, icon_text="＋")
        self._edit_user_button = SecondaryButton("编辑用户", self, icon_text="✎")
        self._approve_button = SecondaryButton("审批用户", self, icon_text="✓")

        self._page_container = PageContainer(
            title="权限管理",
            description="统一管理团队成员、角色层级、模块访问矩阵与操作审计，适合系统管理员做精细化权限治理。",
            actions=(self._add_user_button, self._edit_user_button, self._approve_button),
            max_width=DESKTOP_PAGE_MAX_WIDTH,
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._page_container.add_widget(self._build_summary_strip())
        self._page_container.add_widget(self._build_focus_banner())
        self._page_container.add_widget(self._build_filter_bar())
        self._page_container.add_widget(self._build_user_section())
        self._page_container.add_widget(self._build_role_hierarchy_section())
        self._page_container.add_widget(self._build_permission_matrix_section())
        self._page_container.add_widget(self._build_audit_section())

        self._apply_page_styles()
        self._bind_interactions()
        self._refresh_all_views()

    def _build_summary_strip(self) -> QWidget:
        """构建 KPI 条。"""

        host = QWidget(self)
        row = QHBoxLayout(host)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACING_MD)

        self._summary_cards["total"] = KPICard("总用户", "0", trend="up", percentage="+2", caption="当前工作区全部账号数", sparkline_data=[8, 8, 9, 9, 10, 10, 10])
        self._summary_cards["admins"] = KPICard("管理员", "0", trend="flat", percentage="稳定", caption="超级管理员与运营经理合计", sparkline_data=[5, 5, 5, 5, 6, 6, 6])
        self._summary_cards["active"] = KPICard("活跃用户", "0", trend="up", percentage="+1", caption="最近 24 小时有登录或动作记录", sparkline_data=[5, 6, 6, 7, 7, 8, 8])
        self._summary_cards["pending"] = KPICard("待审批", "0", trend="flat", percentage="待处理", caption="等待审批或首次激活的成员", sparkline_data=[2, 2, 2, 1, 2, 2, 2])

        for card in self._summary_cards.values():
            row.addWidget(card)
        return host

    def _build_focus_banner(self) -> QWidget:
        """顶部状态概览。"""

        host = QFrame(self)
        _call(host, "setObjectName", "permissionBanner")
        layout = QHBoxLayout(host)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_XL)

        self._role_overview_card = InfoCard(
            title="当前治理重点",
            description="建议先处理待审批用户，再复核“系统设置 / 版本升级 / 权限管理”三个高风险模块的开放范围。",
            icon="◎",
            action_text="查看建议",
        )

        status_host = QFrame(host)
        _call(status_host, "setObjectName", "permissionBannerStatus")
        status_layout = QVBoxLayout(status_host)
        status_layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        status_layout.setSpacing(SPACING_SM)

        title = QLabel("实时状态", status_host)
        _call(title, "setObjectName", "permissionBannerTitle")
        self._focus_badge = StatusBadge("审计中", tone="brand")
        self._focus_text = QLabel(self._status_message, status_host)
        _call(self._focus_text, "setObjectName", "permissionBannerText")
        _call(self._focus_text, "setWordWrap", True)

        status_layout.addWidget(title)
        status_layout.addWidget(self._focus_badge)
        status_layout.addWidget(self._focus_text)
        status_layout.addStretch(1)

        layout.addWidget(self._role_overview_card, 2)
        layout.addWidget(status_host, 1)
        return host

    def _build_filter_bar(self) -> QWidget:
        """构建搜索筛选区。"""

        host = QFrame(self)
        _call(host, "setObjectName", "permissionFilterBar")
        layout = QHBoxLayout(host)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_XL)

        self._search_bar = SearchBar("搜索用户名、角色或部门…")
        self._role_filter = FilterDropdown("角色", ROLE_ORDER)
        self._department_filter = FilterDropdown("部门", ("系统平台组", "华东运营中心", "华南运营中心", "创意内容组", "经营分析组", "客户成功组"))
        self._status_filter = FilterDropdown("状态", ("正常", "停用", "待审批"))

        layout.addWidget(self._search_bar, 1)
        layout.addWidget(self._role_filter)
        layout.addWidget(self._department_filter)
        layout.addWidget(self._status_filter)
        layout.addStretch(1)
        return host

    def _build_user_section(self) -> QWidget:
        """用户与角色表格。"""

        section = ContentSection("用户与角色清单", icon="▦", parent=self)

        summary_bar = QWidget(section)
        _call(summary_bar, "setObjectName", "permissionUserSummaryBar")
        summary_layout = QHBoxLayout(summary_bar)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(SPACING_SM)

        self._result_badge = StatusBadge("筛选结果 0/0", tone="brand")
        self._selection_badge = StatusBadge("未选择用户", tone="neutral")
        summary_text = QLabel("支持搜索、角色筛选、审批与编辑动作。", summary_bar)
        _call(summary_text, "setObjectName", "permissionInlineText")

        summary_layout.addWidget(self._result_badge)
        summary_layout.addWidget(self._selection_badge)
        summary_layout.addStretch(1)
        summary_layout.addWidget(summary_text)

        self._user_table = DataTable(
            headers=("用户名", "角色", "部门", "状态", "最近登录", "操作"),
            rows=(),
            page_size=10,
            empty_text="当前筛选条件下暂无用户",
            parent=section,
        )

        section.add_widget(summary_bar)
        section.add_widget(self._user_table)
        return section

    def _build_role_hierarchy_section(self) -> QWidget:
        """角色层级区。"""

        section = ContentSection("角色层级", icon="◈", parent=self)
        host = QWidget(section)
        column = QVBoxLayout(host)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(SPACING_MD)

        for role in ROLES:
            card = QFrame(host)
            _call(card, "setObjectName", "permissionRoleCard")
            layout = QHBoxLayout(card)
            layout.setContentsMargins(SPACING_XL, SPACING_MD, SPACING_XL, SPACING_MD)
            layout.setSpacing(SPACING_MD)

            title_col = QVBoxLayout()
            title_col.setContentsMargins(0, 0, 0, 0)
            title_col.setSpacing(SPACING_XS)
            title = QLabel(role.name, card)
            desc = QLabel(role.summary, card)
            _call(title, "setObjectName", "permissionRoleTitle")
            _call(desc, "setObjectName", "permissionRoleDesc")
            _call(desc, "setWordWrap", True)
            title_col.addWidget(title)
            title_col.addWidget(desc)

            meta_col = QVBoxLayout()
            meta_col.setContentsMargins(0, 0, 0, 0)
            meta_col.setSpacing(SPACING_SM)
            badge = StatusBadge(role.level_text, tone=role.tone)
            member_chip = TagChip(f"成员 {role.member_count} 人", tone=role.tone)
            meta_col.addWidget(badge)
            meta_col.addWidget(member_chip)
            meta_col.addStretch(1)

            select_button = QPushButton("设为焦点角色", card)
            _call(select_button, "setObjectName", "permissionRoleAction")

            layout.addLayout(title_col, 1)
            layout.addLayout(meta_col)
            layout.addWidget(select_button)

            self._role_cards[role.name] = card
            self._role_badges[role.name] = badge
            self._role_descriptions[role.name] = desc
            _connect(getattr(select_button, "clicked", None), lambda _checked=False, role_name=role.name: self._set_active_role(role_name))
            column.addWidget(card)

        section.add_widget(host)
        return section

    def _build_permission_matrix_section(self) -> QWidget:
        """权限矩阵区。"""

        section = ContentSection("权限矩阵", icon="☷", parent=self)

        summary = QWidget(section)
        _call(summary, "setObjectName", "permissionMatrixSummaryBar")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(SPACING_SM)
        self._permission_hint_label = QLabel("点击矩阵中的勾选框可切换角色对模块的访问权限。", summary)
        _call(self._permission_hint_label, "setObjectName", "permissionInlineText")
        summary_layout.addWidget(self._permission_hint_label, 1)
        summary_layout.addWidget(TagChip("高风险模块已高亮", tone="warning"))
        summary_layout.addWidget(TagChip("当前焦点角色可快速预览", tone="brand"))

        matrix_host = QFrame(section)
        _call(matrix_host, "setObjectName", "permissionMatrixHost")
        matrix_column = QVBoxLayout(matrix_host)
        matrix_column.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        matrix_column.setSpacing(SPACING_SM)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(SPACING_SM)
        module_header = QLabel("模块 / 说明", matrix_host)
        _call(module_header, "setObjectName", "permissionMatrixHeader")
        header_row.addWidget(module_header, 3)
        for role_name in ROLE_ORDER:
            label = QLabel(role_name, matrix_host)
            _call(label, "setObjectName", "permissionMatrixHeader")
            self._matrix_headers[role_name] = label
            header_row.addWidget(label, 1)
        matrix_column.addLayout(header_row)

        for row in self._permission_rows:
            row_host = QWidget(matrix_host)
            row_layout = QHBoxLayout(row_host)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(SPACING_SM)

            desc_host = QWidget(row_host)
            desc_layout = QVBoxLayout(desc_host)
            desc_layout.setContentsMargins(0, 0, 0, 0)
            desc_layout.setSpacing(0)
            title = QLabel(f"{row.module_name} · {row.module_group}", desc_host)
            note = QLabel(row.description, desc_host)
            _call(title, "setObjectName", "permissionMatrixTitle")
            _call(note, "setObjectName", "permissionMatrixNote")
            _call(note, "setWordWrap", True)
            self._matrix_row_notes[row.module_name] = note
            desc_layout.addWidget(title)
            desc_layout.addWidget(note)
            row_layout.addWidget(desc_host, 3)

            for role_name, allowed in self._permission_state_for_row(row).items():
                cell = QWidget(row_host)
                cell_layout = QVBoxLayout(cell)
                cell_layout.setContentsMargins(0, 0, 0, 0)
                cell_layout.setSpacing(SPACING_XS)
                button = QPushButton("☑" if allowed else "☐", cell)
                _call(button, "setObjectName", "permissionMatrixToggle")
                hint = QLabel("允许" if allowed else "禁止", cell)
                _call(hint, "setObjectName", "permissionMatrixHint")
                cell_layout.addWidget(button)
                cell_layout.addWidget(hint)
                self._matrix_buttons[(row.module_name, role_name)] = button
                _connect(getattr(button, "clicked", None), lambda _checked=False, module_name=row.module_name, target_role=role_name: self._toggle_permission(module_name, target_role))
                row_layout.addWidget(cell, 1)
            matrix_column.addWidget(row_host)

        footer_row = QWidget(matrix_host)
        footer_layout = QHBoxLayout(footer_row)
        footer_layout.setContentsMargins(0, SPACING_SM, 0, 0)
        footer_layout.setSpacing(SPACING_LG)
        for label_text, checked in (("严格审批模式", True), ("高风险动作二次确认", True), ("同步角色模板", False)):
            switch = ToggleSwitch(checked)
            self._matrix_toggle_switches[label_text] = switch
            group = self._build_strategy_card(label_text, switch)
            footer_layout.addWidget(group, 1)
        matrix_column.addWidget(footer_row)

        section.add_widget(summary)
        section.add_widget(matrix_host)
        return section

    def _build_audit_section(self) -> QWidget:
        """审计日志区。"""

        section = ContentSection("审计日志", icon="⧉", parent=self)
        self._audit_table = DataTable(
            headers=("时间", "操作人", "动作", "对象", "结果", "详情"),
            rows=(),
            page_size=10,
            empty_text="暂无审计记录",
            parent=section,
        )
        section.add_widget(self._audit_table)
        return section

    def _build_strategy_card(self, title: str, toggle: ToggleSwitch) -> QWidget:
        """构建矩阵策略开关卡。"""

        card = QFrame(self)
        _call(card, "setObjectName", "permissionMatrixStrategyCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(SPACING_LG, SPACING_SM, SPACING_LG, SPACING_SM)
        layout.setSpacing(SPACING_SM)
        text = QLabel(title, card)
        _call(text, "setObjectName", "permissionInlineText")
        layout.addWidget(text, 1)
        layout.addWidget(toggle)
        return card

    def _bind_interactions(self) -> None:
        """绑定交互。"""

        if self._search_bar is not None:
            _connect(self._search_bar.search_changed, self._on_search_changed)
        if self._role_filter is not None:
            _connect(self._role_filter.filter_changed, self._on_role_filter_changed)
        if self._department_filter is not None:
            _connect(self._department_filter.filter_changed, self._on_department_filter_changed)
        if self._status_filter is not None:
            _connect(self._status_filter.filter_changed, self._on_status_filter_changed)
        if self._add_user_button is not None:
            _connect(getattr(self._add_user_button, "clicked", None), self._show_add_user_dialog)
        if self._edit_user_button is not None:
            _connect(getattr(self._edit_user_button, "clicked", None), self._show_edit_user_dialog)
        if self._approve_button is not None:
            _connect(getattr(self._approve_button, "clicked", None), self._approve_selected_user)
        if self._user_table is not None:
            _connect(self._user_table.row_selected, self._on_user_selected)
            _connect(self._user_table.row_double_clicked, self._on_user_double_clicked)

        for label_text, switch in self._matrix_toggle_switches.items():
            _connect(getattr(switch, "toggled", None), lambda checked, name=label_text: self._on_strategy_toggled(name, bool(checked)))

    def _permission_state_for_row(self, row: ModulePermissionRecord) -> dict[str, bool]:
        """返回单行权限状态。"""

        return {
            "超级管理员": row.super_admin,
            "运营经理": row.operations_manager,
            "内容创作者": row.content_creator,
            "数据分析师": row.analyst,
            "普通用户": row.standard_user,
        }

    def _replace_permission_row(self, module_name: str, role_name: str, allowed: bool) -> None:
        """更新指定模块权限。"""

        updated_rows: list[ModulePermissionRecord] = []
        for row in self._permission_rows:
            if row.module_name != module_name:
                updated_rows.append(row)
                continue
            field_map = {
                "超级管理员": "super_admin",
                "运营经理": "operations_manager",
                "内容创作者": "content_creator",
                "数据分析师": "analyst",
                "普通用户": "standard_user",
            }
            updated_rows.append(replace(row, **{field_map[role_name]: allowed}))
        self._permission_rows = updated_rows

    def _toggle_permission(self, module_name: str, role_name: str) -> None:
        """切换权限。"""

        current = False
        for row in self._permission_rows:
            if row.module_name == module_name:
                current = self._permission_state_for_row(row)[role_name]
                break
        next_state = not current
        self._replace_permission_row(module_name, role_name, next_state)
        self._status_message = f"已将 {role_name} 对“{module_name}”的权限切换为{'允许' if next_state else '禁止'}。"
        self._audit_records.insert(
            0,
            AuditRecord(
                datetime.now().strftime("今天 %H:%M"),
                "当前工作区",
                "切换权限",
                f"{role_name} / {module_name}",
                "成功",
                f"矩阵权限已更新为{'允许' if next_state else '禁止'}。",
            ),
        )
        self._audit_records = self._audit_records[:12]
        self._refresh_all_views()

    def _on_search_changed(self, text: str) -> None:
        """处理搜索。"""

        self._search_keyword = text.strip().lower()
        self._apply_filters()

    def _on_role_filter_changed(self, value: str) -> None:
        """处理角色筛选。"""

        self._role_filter_value = value
        self._apply_filters()

    def _on_department_filter_changed(self, value: str) -> None:
        """处理部门筛选。"""

        self._department_filter_value = value
        self._apply_filters()

    def _on_status_filter_changed(self, value: str) -> None:
        """处理状态筛选。"""

        self._status_filter_value = value
        self._apply_filters()

    def _apply_filters(self, *_args: object) -> None:
        """应用筛选。"""

        self._visible_users = [
            record
            for record in self._all_users
            if (not self._search_keyword or self._search_keyword in f"{record.username} {record.role} {record.department}".lower())
            and (self._role_filter_value in {"", "全部"} or record.role == self._role_filter_value)
            and (self._department_filter_value in {"", "全部"} or record.department == self._department_filter_value)
            and (self._status_filter_value in {"", "全部"} or record.status == self._status_filter_value)
        ]
        if not self._visible_users:
            self._selected_user_index = -1
        else:
            self._selected_user_index = min(max(self._selected_user_index, 0), len(self._visible_users) - 1)
        self._status_message = f"筛选后保留 {len(self._visible_users)} 名成员，可继续审批或调整矩阵权限。"
        self._refresh_all_views()

    def _selected_user(self) -> UserRecord | None:
        """返回当前选中用户。"""

        if 0 <= self._selected_user_index < len(self._visible_users):
            return self._visible_users[self._selected_user_index]
        return None

    def _on_user_selected(self, absolute_row: int) -> None:
        """响应表格选中。"""

        if 0 <= absolute_row < len(self._visible_users):
            self._selected_user_index = absolute_row
            user = self._visible_users[absolute_row]
            self._status_message = f"已选择 {user.username}，可继续编辑角色、状态和模块权限。"
            self._active_role = user.role
            self._refresh_all_views()

    def _on_user_double_clicked(self, absolute_row: int) -> None:
        """双击即编辑。"""

        self._on_user_selected(absolute_row)
        self._show_edit_user_dialog()

    def _set_active_role(self, role_name: str) -> None:
        """设置焦点角色。"""

        self._active_role = role_name
        self._status_message = f"已切换焦点角色为“{role_name}”，矩阵高亮与层级说明已同步。"
        self._refresh_all_views()

    def _show_add_user_dialog(self) -> None:
        """展示新增用户对话框。"""

        self._dialog_ref = PlaceholderDialog("新增用户")
        _call(self._dialog_ref, "show")
        self._status_message = "已唤起“新增用户”原型对话框，可继续补充字段流程。"
        self._audit_records.insert(
            0,
            AuditRecord(datetime.now().strftime("今天 %H:%M"), "当前工作区", "打开对话框", "新增用户", "成功", "已打开新增用户占位对话框。"),
        )
        self._audit_records = self._audit_records[:12]
        self._refresh_all_views()

    def _show_edit_user_dialog(self) -> None:
        """展示编辑用户对话框。"""

        user = self._selected_user()
        if user is None:
            self._status_message = "当前没有可编辑的用户，请先从列表中选择成员。"
            self._refresh_all_views()
            return
        self._dialog_ref = PlaceholderDialog(f"编辑用户 - {user.username}")
        _call(self._dialog_ref, "show")
        self._status_message = f"已唤起“{user.username}”编辑对话框，可继续补充字段与权限修改流程。"
        self._refresh_all_views()

    def _approve_selected_user(self) -> None:
        """审批当前用户。"""

        user = self._selected_user()
        if user is None:
            self._status_message = "没有待审批的目标用户。"
            self._refresh_all_views()
            return
        if user.status != "待审批":
            self._status_message = f"{user.username} 当前状态为“{user.status}”，无需审批。"
            self._refresh_all_views()
            return

        updated_all: list[UserRecord] = []
        for record in self._all_users:
            if record.username == user.username:
                updated_all.append(replace(record, status="正常", last_login="待首次登录", action_label="编辑", active=True, pending=False))
            else:
                updated_all.append(record)
        self._all_users = updated_all
        self._audit_records.insert(
            0,
            AuditRecord(datetime.now().strftime("今天 %H:%M"), "当前工作区", "审批用户", user.username, "成功", "待审批用户已转为正常状态，等待首次登录。"),
        )
        self._audit_records = self._audit_records[:12]
        self._status_message = f"已通过 {user.username} 的账号审批。"
        self._apply_filters()

    def _on_strategy_toggled(self, name: str, checked: bool) -> None:
        """处理矩阵策略开关。"""

        self._status_message = f"策略“{name}”已切换为{'开启' if checked else '关闭'}。"
        self._audit_records.insert(
            0,
            AuditRecord(datetime.now().strftime("今天 %H:%M"), "当前工作区", "切换策略", name, "成功", f"策略已切换为{'开启' if checked else '关闭'}。"),
        )
        self._audit_records = self._audit_records[:12]
        self._refresh_all_views()

    def _refresh_all_views(self) -> None:
        """刷新全部视图。"""

        self._refresh_summary_cards()
        self._refresh_focus_banner()
        self._refresh_user_table()
        self._refresh_role_hierarchy()
        self._refresh_permission_matrix()
        self._refresh_audit_table()

    def _refresh_summary_cards(self) -> None:
        """刷新 KPI。"""

        total = len(self._all_users)
        admins = sum(1 for user in self._all_users if user.role in {"超级管理员", "运营经理"})
        active = sum(1 for user in self._all_users if user.active)
        pending = sum(1 for user in self._all_users if user.pending)

        self._summary_cards["total"].set_value(str(total))
        self._summary_cards["total"].set_trend("up", f"{len(self._visible_users)} 可见")
        self._summary_cards["admins"].set_value(str(admins))
        self._summary_cards["admins"].set_trend("flat", "高权限成员")
        self._summary_cards["active"].set_value(str(active))
        self._summary_cards["active"].set_trend("up", "近 24 小时在线")
        self._summary_cards["pending"].set_value(str(pending))
        self._summary_cards["pending"].set_trend("flat", "等待审批")

    def _refresh_focus_banner(self) -> None:
        """刷新焦点提示。"""

        if self._focus_badge is not None:
            tone = "warning" if any(user.pending for user in self._all_users) else "success"
            _call(self._focus_badge, "setText", "有待审批用户" if tone == "warning" else "权限状态稳定")
            self._focus_badge.set_tone(tone)
        if self._focus_text is not None:
            _call(self._focus_text, "setText", self._status_message)
        if self._role_overview_card is not None:
            role = next(role_item for role_item in ROLES if role_item.name == self._active_role)
            _call(self._role_overview_card, "set_description", f"当前焦点角色：{role.name}。{role.summary} 当前成员 {role.member_count} 人。")

    def _refresh_user_table(self) -> None:
        """刷新用户表。"""

        if self._user_table is None:
            return
        rows = [
            (record.username, record.role, record.department, record.status, record.last_login, record.action_label)
            for record in self._visible_users
        ]
        self._user_table.set_rows(rows)
        if self._result_badge is not None:
            _call(self._result_badge, "setText", f"筛选结果 {len(self._visible_users)}/{len(self._all_users)}")
        if self._selection_badge is not None:
            selected = self._selected_user()
            if selected is None:
                _call(self._selection_badge, "setText", "未选择用户")
                self._selection_badge.set_tone("neutral")
            else:
                _call(self._selection_badge, "setText", f"当前：{selected.username} · {selected.role}")
                self._selection_badge.set_tone("brand")

    def _refresh_role_hierarchy(self) -> None:
        """刷新层级卡高亮。"""

        colors = _palette()
        primary = _token("brand.primary")
        for role in ROLES:
            card = self._role_cards[role.name]
            badge = self._role_badges[role.name]
            desc = self._role_descriptions[role.name]
            is_active = role.name == self._active_role
            border_color = primary if is_active else colors.border
            background = _rgba(primary, 0.08) if is_active else colors.surface
            _call(
                card,
                "setStyleSheet",
                f"""
                QFrame#permissionRoleCard {{
                    background-color: {background};
                    border: 1px solid {border_color};
                    border-radius: {RADIUS_LG}px;
                }}
                QLabel#permissionRoleTitle {{
                    background: transparent;
                    color: {colors.text};
                    font-size: {_static_token('font.size.lg')};
                    font-weight: {_static_token('font.weight.bold')};
                }}
                QLabel#permissionRoleDesc {{
                    background: transparent;
                    color: {colors.text_muted};
                    font-size: {_static_token('font.size.sm')};
                }}
                QPushButton#permissionRoleAction {{
                    background-color: {_rgba(primary, 0.10)};
                    color: {primary};
                    border: 1px solid {_rgba(primary, 0.20)};
                    border-radius: {RADIUS_MD}px;
                    min-height: {BUTTON_HEIGHT}px;
                    padding: {SPACING_XS}px {SPACING_LG}px;
                }}
                """,
            )
            badge.set_tone(role.tone)
            _call(desc, "setText", f"{role.summary} · 当前成员 {role.member_count} 人。")

    def _refresh_permission_matrix(self) -> None:
        """刷新权限矩阵。"""

        colors = _palette()
        primary = _token("brand.primary")
        warning = _token("status.warning")
        high_risk = {"系统设置", "权限管理", "版本升级"}

        for role_name, label in self._matrix_headers.items():
            is_active = role_name == self._active_role
            _call(
                label,
                "setStyleSheet",
                f"background: transparent; color: {primary if is_active else colors.text_muted}; font-size: {_static_token('font.size.sm')}; font-weight: {_static_token('font.weight.bold')};",
            )

        for row in self._permission_rows:
            row_state = self._permission_state_for_row(row)
            note = self._matrix_row_notes[row.module_name]
            note_color = warning if row.module_name in high_risk else colors.text_muted
            _call(note, "setStyleSheet", f"background: transparent; color: {note_color}; font-size: {_static_token('font.size.sm')};")
            for role_name, allowed in row_state.items():
                button = self._matrix_buttons[(row.module_name, role_name)]
                is_focus = role_name == self._active_role
                background = _rgba(primary if allowed else colors.border, 0.12 if allowed else 0.08)
                border = primary if is_focus else (primary if allowed else colors.border)
                text_color = primary if allowed else colors.text_muted
                _call(button, "setText", "☑" if allowed else "☐")
                _call(
                    button,
                    "setStyleSheet",
                    f"""
                    QPushButton#permissionMatrixToggle {{
                        background-color: {background};
                        color: {text_color};
                        border: 1px solid {border};
                        border-radius: {RADIUS_MD}px;
                        min-height: {BUTTON_HEIGHT}px;
                        padding: {SPACING_XS}px {SPACING_SM}px;
                        font-size: {_static_token('font.size.lg')};
                        font-weight: {_static_token('font.weight.bold')};
                    }}
                    """,
                )
        if self._permission_hint_label is not None:
            _call(self._permission_hint_label, "setText", f"当前焦点角色：{self._active_role}。点击矩阵中的勾选框可继续切换访问权限。")

    def _refresh_audit_table(self) -> None:
        """刷新审计日志。"""

        if self._audit_table is None:
            return
        rows = [
            (record.happened_at, record.operator, record.action, record.target, record.result, record.detail)
            for record in self._audit_records
        ]
        self._audit_table.set_rows(rows)

    def _apply_page_styles(self) -> None:
        """应用页面样式。"""

        colors = _palette()
        primary = _token("brand.primary")
        primary_soft = _rgba(primary, 0.08)
        primary_border = _rgba(primary, 0.18)
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#permissionManagementPage {{
                background-color: {colors.surface_alt};
            }}
            QFrame#permissionFilterBar,
            QFrame#permissionMatrixHost {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#permissionFilterBar {{
                border-color: {primary_border};
            }}
            QFrame#permissionBanner {{
                background-color: {primary_soft};
                border: 1px solid {primary_border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#permissionBannerStatus {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#permissionUserSummaryBar,
            QWidget#permissionMatrixSummaryBar,
            QFrame#permissionMatrixStrategyCard {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#permissionBannerTitle {{
                background: transparent;
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#permissionBannerText,
            QLabel#permissionInlineText,
            QLabel#permissionMatrixNote,
            QLabel#permissionMatrixHint {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QLabel#permissionMatrixHeader {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#permissionMatrixTitle {{
                background: transparent;
                color: {colors.text};
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QWidget#permissionManagementPage QFrame#contentSection {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#permissionManagementPage QTableView {{
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#permissionManagementPage QFrame[variant="card"] {{
                background-color: {colors.surface};
            }}
            QWidget#permissionManagementPage QFrame#permissionRoleCard {{
                min-height: {BUTTON_HEIGHT + SPACING_2XL}px;
            }}
            QWidget#permissionManagementPage QPushButton#permissionRoleAction:hover,
            QWidget#permissionManagementPage QPushButton#permissionMatrixToggle:hover {{
                border-color: {primary};
                background-color: {primary_soft};
            }}
            """,
        )
__all__ = ["PermissionManagementPage"]
