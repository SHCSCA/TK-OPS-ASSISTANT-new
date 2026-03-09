# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportCallIssue=false
from __future__ import annotations

"""日志中心页面。"""

from dataclasses import dataclass
from datetime import datetime

from ....core.qt import QFrame, QHBoxLayout, QLabel, QWidget
from ....core.types import RouteId
from ...components import (
    ContentSection,
    DataTable,
    FilterDropdown,
    InfoCard,
    KPICard,
    LogViewer,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    StatsBadge,
    TagChip,
)
from ...components.inputs import (
    RADIUS_LG,
    SPACING_MD,
    SPACING_LG,
    SPACING_SM,
    SPACING_XL,
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
    """十六进制转 rgba。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


@dataclass(frozen=True)
class LogRecord:
    """日志记录。"""

    timestamp: str
    level: str
    module: str
    message: str
    details: str


@dataclass(frozen=True)
class ModuleStatRecord:
    """模块统计记录。"""

    module_name: str
    total_count: int
    warning_count: int
    owner: str
    trend_text: str


@dataclass(frozen=True)
class ExportRecord:
    """导出历史记录。"""

    exported_at: str
    scope_text: str
    count_text: str
    operator: str
    destination: str


@dataclass(frozen=True)
class AlertRecord:
    """告警观察记录。"""

    priority: str
    module: str
    owner: str
    status: str
    summary: str


@dataclass(frozen=True)
class SavedViewRecord:
    """已保存视图记录。"""

    view_name: str
    filter_text: str
    owner: str
    updated_at: str
    note: str


@dataclass(frozen=True)
class SubscriptionRecord:
    """日志订阅规则。"""

    subscription_name: str
    target: str
    trigger_text: str
    channel: str
    enabled_text: str


LOG_RECORDS: tuple[LogRecord, ...] = (
    LogRecord("2026-03-09 11:18:06", "INFO", "权限管理", "权限矩阵已刷新", "焦点角色切换为运营经理，矩阵高亮完成同步。"),
    LogRecord("2026-03-09 11:16:42", "WARN", "版本升级", "检测到镜像源延迟升高", "主镜像响应 2.6 秒，已切换备用下载节点。"),
    LogRecord("2026-03-09 11:15:25", "ERROR", "系统设置", "代理健康检查失败", "代理返回连接超时，已进入重试队列。"),
    LogRecord("2026-03-09 11:12:03", "INFO", "日志中心", "历史日志导出完成", "已将近 7 天日志导出到 D:/Reports/log-center-20260309.zip。"),
    LogRecord("2026-03-09 11:08:54", "DEBUG", "素材工厂", "缩略图缓存命中", "命中 48 条素材缩略图缓存，避免重复渲染。"),
    LogRecord("2026-03-09 11:07:31", "INFO", "调度中心", "夜间任务批次已创建", "共创建 12 个批处理任务，等待凌晨执行。"),
    LogRecord("2026-03-09 11:04:17", "FATAL", "数据采集", "采集节点进程异常退出", "节点 03 在写入阶段崩溃，已触发高等级告警。"),
    LogRecord("2026-03-09 10:58:49", "WARN", "网络诊断", "检测到 DNS 波动", "东南亚出口线路出现瞬时解析抖动。"),
    LogRecord("2026-03-09 10:52:10", "INFO", "权限管理", "待审批用户已更新", "新增 2 名待审批用户，等待管理员处理。"),
    LogRecord("2026-03-09 10:45:32", "DEBUG", "系统设置", "配置快照写入完成", "本地快照校验通过，耗时 84ms。"),
    LogRecord("2026-03-09 10:42:18", "ERROR", "版本升级", "补丁清单拉取失败", "备用源证书过期，正在尝试回退主源。"),
    LogRecord("2026-03-09 10:37:22", "INFO", "日志中心", "实时流已恢复", "日志轮询器重新连接，自动刷新继续运行。"),
)


MODULE_STATS: tuple[ModuleStatRecord, ...] = (
    ModuleStatRecord("权限管理", 18, 2, "系统平台组", "审批流稳定"),
    ModuleStatRecord("版本升级", 12, 3, "基础设施组", "镜像波动待关注"),
    ModuleStatRecord("系统设置", 15, 1, "系统平台组", "配置写入稳定"),
    ModuleStatRecord("日志中心", 21, 0, "运行时组", "实时流恢复完成"),
    ModuleStatRecord("素材工厂", 8, 0, "内容平台组", "缓存命中良好"),
    ModuleStatRecord("调度中心", 10, 1, "自动化组", "夜间任务正常"),
    ModuleStatRecord("数据采集", 9, 4, "自动化组", "节点崩溃待修复"),
    ModuleStatRecord("网络诊断", 7, 1, "网络支持", "出口抖动轻微"),
)


EXPORT_HISTORY: tuple[ExportRecord, ...] = (
    ExportRecord("今天 11:12", "最近 7 天", "218 条", "陈启航", "D:/Reports/log-center-20260309.zip"),
    ExportRecord("今天 09:48", "ERROR / FATAL", "36 条", "林若溪", "D:/Reports/log-risk-pack.zip"),
    ExportRecord("昨天 18:06", "权限管理", "44 条", "赵明锐", "D:/Reports/permission-audit.zip"),
    ExportRecord("昨天 15:20", "版本升级", "28 条", "顾言舟", "D:/Reports/upgrade-check.zip"),
    ExportRecord("昨天 11:55", "最近 24 小时", "162 条", "宋安可", "D:/Reports/log-center-yesterday.zip"),
    ExportRecord("03-07 17:18", "日志中心", "31 条", "陈启航", "D:/Reports/log-center-module.zip"),
    ExportRecord("03-07 10:12", "系统设置", "26 条", "林若溪", "D:/Reports/settings-trace.zip"),
    ExportRecord("03-06 19:35", "数据采集", "52 条", "顾言舟", "D:/Reports/collector-critical.zip"),
)


ALERT_RECORDS: tuple[AlertRecord, ...] = (
    AlertRecord("P0", "数据采集", "自动化组", "处理中", "采集节点 03 崩溃，需要在下个批次前恢复。"),
    AlertRecord("P1", "版本升级", "基础设施组", "待确认", "备用镜像证书异常，建议检查回退逻辑。"),
    AlertRecord("P1", "系统设置", "系统平台组", "处理中", "代理健康检查失败次数升高。"),
    AlertRecord("P2", "网络诊断", "网络支持", "观察中", "出口 DNS 抖动在阈值附近波动。"),
    AlertRecord("P2", "权限管理", "系统平台组", "处理中", "待审批用户数量连续两小时未下降。"),
    AlertRecord("P3", "日志中心", "运行时组", "已缓解", "轮询器短暂中断后已恢复。"),
    AlertRecord("P3", "调度中心", "自动化组", "观察中", "夜间批次任务量较上周提升 12%。"),
    AlertRecord("P3", "素材工厂", "内容平台组", "正常", "缩略图缓存命中率良好。"),
)


SAVED_VIEWS: tuple[SavedViewRecord, ...] = (
    SavedViewRecord("高风险异常视图", "ERROR/FATAL + 最近 24 小时", "陈启航", "今天 11:05", "用于晨间巡检时快速查看高优先异常。"),
    SavedViewRecord("版本升级专项", "模块=版本升级 + 最近 7 天", "林若溪", "今天 10:30", "用于发布前复核升级链路与镜像源稳定性。"),
    SavedViewRecord("权限治理日常", "模块=权限管理 + INFO/WARN", "赵明锐", "今天 09:58", "追踪审批、角色切换与导出行为。"),
    SavedViewRecord("代理异常快照", "模块=系统设置 + keyword=代理", "网络支持", "今天 09:21", "快速定位代理连接与健康探测问题。"),
    SavedViewRecord("采集节点崩溃", "模块=数据采集 + ERROR/FATAL", "顾言舟", "昨天 18:41", "聚焦采集节点退出与恢复过程。"),
    SavedViewRecord("日志导出观察", "模块=日志中心 + keyword=导出", "运行时组", "昨天 16:28", "关注导出链路与压缩包生成表现。"),
    SavedViewRecord("夜间调度复盘", "模块=调度中心 + 最近 7 天", "自动化组", "昨天 11:50", "为夜间批次复盘准备基础日志视图。"),
    SavedViewRecord("内容缓存稳定性", "模块=素材工厂 + DEBUG", "内容平台组", "03-07 15:12", "观察素材缓存、命中率与索引回填。"),
)


SUBSCRIPTIONS: tuple[SubscriptionRecord, ...] = (
    SubscriptionRecord("高危异常推送", "系统管理员群", "ERROR/FATAL 连续出现", "桌面通知 + 企业群", "已开启"),
    SubscriptionRecord("升级源异常播报", "基础设施组", "模块=版本升级 且包含镜像/证书", "企业群", "已开启"),
    SubscriptionRecord("代理故障提醒", "网络支持", "模块=系统设置 且关键字=代理", "桌面通知", "已开启"),
    SubscriptionRecord("采集崩溃日报", "自动化组", "模块=数据采集 且级别>=ERROR", "邮件摘要", "已开启"),
    SubscriptionRecord("夜间调度回顾", "自动化组", "模块=调度中心 + 最近 24 小时", "邮件摘要", "已关闭"),
    SubscriptionRecord("权限审批日报", "系统平台组", "模块=权限管理 + 待审批", "企业群", "已开启"),
    SubscriptionRecord("日志导出结果", "运行时组", "模块=日志中心 + 关键字=导出", "桌面通知", "已关闭"),
    SubscriptionRecord("网络波动观察", "网络支持", "模块=网络诊断 + 级别=WARN", "邮件摘要", "已开启"),
)

DESKTOP_PAGE_MAX_WIDTH = 1760


class LogCenterPage(BasePage):
    """日志中心页。"""

    default_route_id: RouteId = RouteId("log_center")
    default_display_name: str = "日志中心"
    default_icon_name: str = "receipt_long"

    def __init__(self, parent: object | None = None) -> None:
        self._all_logs: list[LogRecord] = list(LOG_RECORDS)
        self._visible_logs: list[LogRecord] = list(LOG_RECORDS)
        self._module_stats: list[ModuleStatRecord] = list(MODULE_STATS)
        self._export_history: list[ExportRecord] = list(EXPORT_HISTORY)
        self._alert_records: list[AlertRecord] = list(ALERT_RECORDS)
        self._saved_views: list[SavedViewRecord] = list(SAVED_VIEWS)
        self._subscriptions: list[SubscriptionRecord] = list(SUBSCRIPTIONS)
        self._level_filter_value = "全部"
        self._module_filter_value = "全部"
        self._date_filter_value = "最近 24 小时"
        self._keyword = ""
        self._auto_refresh = True
        self._status_text = "实时流已连接，支持按级别、模块和关键字筛选。"

        self._page_container: PageContainer | None = None
        self._summary_cards: dict[str, KPICard] = {}
        self._search_bar: SearchBar | None = None
        self._level_filter: FilterDropdown | None = None
        self._module_filter: FilterDropdown | None = None
        self._date_filter: FilterDropdown | None = None
        self._export_button: SecondaryButton | None = None
        self._clear_button: SecondaryButton | None = None
        self._refresh_button: PrimaryButton | None = None
        self._auto_refresh_switch: ToggleSwitch | None = None
        self._auto_refresh_label: QLabel | None = None
        self._stream_viewer: LogViewer | None = None
        self._history_table: DataTable | None = None
        self._stats_badges: dict[str, StatsBadge] = {}
        self._status_hint_label: QLabel | None = None
        self._stream_note_card: InfoCard | None = None
        self._module_table: DataTable | None = None
        self._export_table: DataTable | None = None
        self._scope_chip: TagChip | None = None
        self._level_chip: TagChip | None = None
        self._alert_table: DataTable | None = None
        self._saved_view_table: DataTable | None = None
        self._subscription_table: DataTable | None = None

        super().__init__(parent=parent)

    def setup_ui(self) -> None:
        """构建日志中心页面。"""

        _call(self, "setObjectName", "logCenterPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self._export_button = SecondaryButton("导出日志", self, icon_text="⇩")
        self._clear_button = SecondaryButton("清空筛选", self, icon_text="⌫")
        self._refresh_button = PrimaryButton("立即刷新", self, icon_text="↻")

        self._page_container = PageContainer(
            title="日志中心",
            description="集中查看系统实时流、历史日志与模块级统计，快速定位错误、告警与性能波动。",
            actions=(self._export_button, self._clear_button, self._refresh_button),
            max_width=DESKTOP_PAGE_MAX_WIDTH,
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._page_container.add_widget(self._build_summary_strip())
        self._page_container.add_widget(self._build_filter_bar())
        self._page_container.add_widget(self._build_stream_section())
        self._page_container.add_widget(self._build_statistics_section())
        self._page_container.add_widget(self._build_alert_section())
        self._page_container.add_widget(self._build_history_section())

        self._apply_page_styles()
        self._bind_interactions()
        self._refresh_all_views()

    def _build_summary_strip(self) -> QWidget:
        """构建顶部统计。"""

        host = QWidget(self)
        row = QHBoxLayout(host)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACING_MD)

        self._summary_cards["total"] = KPICard("日志总量", "0", trend="up", percentage="+12", caption="当前筛选窗口内的记录量", sparkline_data=[8, 9, 10, 11, 11, 12, 12])
        self._summary_cards["errors"] = KPICard("异常日志", "0", trend="flat", percentage="待关注", caption="ERROR 与 FATAL 总和", sparkline_data=[1, 1, 2, 2, 2, 3, 3])
        self._summary_cards["modules"] = KPICard("模块覆盖", "0", trend="flat", percentage="多模块", caption="当前筛选结果涉及的模块数", sparkline_data=[3, 4, 4, 5, 5, 5, 6])
        self._summary_cards["stream"] = KPICard("实时流状态", "在线", trend="up", percentage="自动刷新", caption="当前是否保持实时流更新", sparkline_data=[75, 78, 80, 82, 84, 88, 92])
        for card in self._summary_cards.values():
            row.addWidget(card)
        return host

    def _build_filter_bar(self) -> QWidget:
        """过滤区。"""

        host = QFrame(self)
        _call(host, "setObjectName", "logCenterFilterBar")
        layout = QHBoxLayout(host)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_XL)

        self._search_bar = SearchBar("搜索级别、模块或关键字…")
        self._level_filter = FilterDropdown("日志级别", ("DEBUG", "INFO", "WARN", "ERROR", "FATAL"))
        self._module_filter = FilterDropdown("模块", ("权限管理", "版本升级", "系统设置", "日志中心", "素材工厂", "调度中心", "数据采集", "网络诊断"))
        self._date_filter = FilterDropdown("时间范围", ("最近 1 小时", "最近 24 小时", "最近 7 天", "自定义范围"))

        auto_host = QFrame(host)
        _call(auto_host, "setObjectName", "logCenterAutoHost")
        auto_layout = QHBoxLayout(auto_host)
        auto_layout.setContentsMargins(SPACING_LG, SPACING_SM, SPACING_LG, SPACING_SM)
        auto_layout.setSpacing(SPACING_SM)
        self._auto_refresh_label = QLabel("自动刷新", auto_host)
        _call(self._auto_refresh_label, "setObjectName", "logCenterInlineText")
        self._auto_refresh_switch = ToggleSwitch(True)
        auto_layout.addWidget(self._auto_refresh_label)
        auto_layout.addWidget(self._auto_refresh_switch)

        layout.addWidget(self._search_bar, 1)
        layout.addWidget(self._level_filter)
        layout.addWidget(self._module_filter)
        layout.addWidget(self._date_filter)
        layout.addWidget(auto_host)
        layout.addStretch(1)
        return host

    def _build_stream_section(self) -> QWidget:
        """实时流区。"""

        section = ContentSection("实时日志流", icon="≫", parent=self)
        self._stream_note_card = InfoCard(
            title="实时流说明",
            description="自动刷新开启时，实时流会优先显示最近 10 条匹配记录；关闭后保留当前窗口快照。",
            icon="◉",
            action_text="保持当前状态",
        )
        self._stream_viewer = LogViewer()
        self._status_hint_label = QLabel(self._status_text, section)
        _call(self._status_hint_label, "setObjectName", "logCenterInlineText")
        _call(self._status_hint_label, "setWordWrap", True)
        chip_row = QWidget(section)
        _call(chip_row, "setObjectName", "logCenterScopeBar")
        chip_layout = QHBoxLayout(chip_row)
        chip_layout.setContentsMargins(0, 0, 0, 0)
        chip_layout.setSpacing(SPACING_SM)
        self._scope_chip = TagChip("时间范围：最近 24 小时", tone="brand")
        self._level_chip = TagChip("级别：全部", tone="neutral")
        chip_layout.addWidget(self._scope_chip)
        chip_layout.addWidget(self._level_chip)
        chip_layout.addStretch(1)
        section.add_widget(self._stream_note_card)
        section.add_widget(self._status_hint_label)
        section.add_widget(chip_row)
        section.add_widget(self._stream_viewer)
        return section

    def _build_statistics_section(self) -> QWidget:
        """统计区。"""

        section = ContentSection("日志统计", icon="◔", parent=self)
        badges_host = QWidget(section)
        _call(badges_host, "setObjectName", "logCenterStatsStrip")
        badges_layout = QHBoxLayout(badges_host)
        badges_layout.setContentsMargins(0, 0, 0, 0)
        badges_layout.setSpacing(SPACING_LG)

        badge_specs: tuple[tuple[str, str, str, BadgeTone], ...] = (
            ("DEBUG", "DEBUG 数量", "∙", "neutral"),
            ("INFO", "INFO 数量", "◎", "success"),
            ("WARN", "WARN 数量", "▲", "warning"),
            ("ERROR", "ERROR/FATAL", "!", "error"),
            ("MODULE", "模块分布", "▣", "brand"),
        )
        for key, label, icon, tone in badge_specs:
            badge = StatsBadge(label=label, value="0", icon=icon, tone=tone)
            self._stats_badges[key] = badge
            badges_layout.addWidget(badge)
        section.add_widget(badges_host)

        self._module_table = DataTable(
            headers=("模块", "日志量", "告警量", "负责人", "趋势说明"),
            rows=(),
            page_size=8,
            empty_text="暂无模块统计",
            parent=section,
        )
        section.add_widget(self._module_table)
        return section

    def _build_history_section(self) -> QWidget:
        """历史日志表格。"""

        section = ContentSection("历史日志", icon="▤", parent=self)
        self._history_table = DataTable(
            headers=("时间", "级别", "模块", "消息", "详情"),
            rows=(),
            page_size=10,
            empty_text="当前条件下暂无历史日志",
            parent=section,
        )
        self._export_table = DataTable(
            headers=("导出时间", "范围", "数量", "操作人", "目标位置"),
            rows=(),
            page_size=8,
            empty_text="暂无导出历史",
            parent=section,
        )
        section.add_widget(self._history_table)
        section.add_widget(self._export_table)
        return section

    def _build_alert_section(self) -> QWidget:
        """告警与保存视图区。"""

        section = ContentSection("告警与视图管理", icon="⚠", parent=self)
        self._alert_table = DataTable(
            headers=("优先级", "模块", "负责人", "状态", "摘要"),
            rows=(),
            page_size=8,
            empty_text="暂无告警观察项",
            parent=section,
        )
        self._saved_view_table = DataTable(
            headers=("视图名称", "筛选条件", "维护人", "更新时间", "备注"),
            rows=(),
            page_size=8,
            empty_text="暂无保存视图",
            parent=section,
        )
        self._subscription_table = DataTable(
            headers=("订阅名称", "目标对象", "触发条件", "通道", "状态"),
            rows=(),
            page_size=8,
            empty_text="暂无订阅规则",
            parent=section,
        )
        section.add_widget(self._alert_table)
        section.add_widget(self._saved_view_table)
        section.add_widget(self._subscription_table)
        return section

    def _bind_interactions(self) -> None:
        """绑定交互。"""

        if self._search_bar is not None:
            _connect(self._search_bar.search_changed, self._on_search_changed)
        if self._level_filter is not None:
            _connect(self._level_filter.filter_changed, self._on_level_changed)
        if self._module_filter is not None:
            _connect(self._module_filter.filter_changed, self._on_module_changed)
        if self._date_filter is not None:
            _connect(self._date_filter.filter_changed, self._on_date_changed)
        if self._auto_refresh_switch is not None:
            _connect(getattr(self._auto_refresh_switch, "toggled", None), self._on_auto_refresh_changed)
        if self._export_button is not None:
            _connect(getattr(self._export_button, "clicked", None), self._export_logs)
        if self._clear_button is not None:
            _connect(getattr(self._clear_button, "clicked", None), self._clear_filters)
        if self._refresh_button is not None:
            _connect(getattr(self._refresh_button, "clicked", None), self._simulate_refresh)

    def _on_search_changed(self, text: str) -> None:
        """处理关键字搜索。"""

        self._keyword = text.strip().lower()
        self._apply_filters()

    def _on_level_changed(self, value: str) -> None:
        """处理级别筛选。"""

        self._level_filter_value = value
        self._apply_filters()

    def _on_module_changed(self, value: str) -> None:
        """处理模块筛选。"""

        self._module_filter_value = value
        self._apply_filters()

    def _on_date_changed(self, value: str) -> None:
        """处理日期筛选。"""

        self._date_filter_value = value
        self._apply_filters()

    def _on_auto_refresh_changed(self, checked: bool) -> None:
        """切换自动刷新。"""

        self._auto_refresh = checked
        self._status_text = f"自动刷新已{'开启' if checked else '关闭'}，当前仍保留最近一次筛选结果。"
        self._refresh_all_views()

    def _clear_filters(self) -> None:
        """清空筛选。"""

        self._keyword = ""
        self._level_filter_value = "全部"
        self._module_filter_value = "全部"
        self._date_filter_value = "最近 24 小时"
        if self._search_bar is not None:
            self._search_bar.clear()
        if self._level_filter is not None:
            self._level_filter.set_current_text("全部")
        if self._module_filter is not None:
            self._module_filter.set_current_text("全部")
        if self._date_filter is not None:
            self._date_filter.set_current_text("最近 24 小时")
        self._status_text = "已恢复默认筛选条件。"
        self._apply_filters()

    def _export_logs(self) -> None:
        """模拟导出。"""

        self._export_history.insert(
            0,
            ExportRecord(
                datetime.now().strftime("今天 %H:%M"),
                self._date_filter_value,
                f"{len(self._visible_logs)} 条",
                "当前工作区",
                "D:/Reports/log-center-latest.zip",
            ),
        )
        self._export_history = self._export_history[:10]
        self._status_text = f"已导出 {len(self._visible_logs)} 条日志到本地归档目录。"
        self._refresh_all_views()

    def _simulate_refresh(self) -> None:
        """模拟刷新新日志。"""

        self._all_logs.insert(
            0,
            LogRecord(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "INFO",
                "日志中心",
                "手动刷新完成",
                "新一轮日志筛选已执行，实时流与历史表格已同步。",
            ),
        )
        self._all_logs = self._all_logs[:15]
        self._status_text = "已拉取最新日志并刷新统计结果。"
        self._apply_filters()

    def _apply_filters(self) -> None:
        """应用日志筛选。"""

        self._visible_logs = [
            record
            for record in self._all_logs
            if (self._level_filter_value in {"", "全部"} or record.level == self._level_filter_value)
            and (self._module_filter_value in {"", "全部"} or record.module == self._module_filter_value)
            and (
                not self._keyword
                or self._keyword in f"{record.level} {record.module} {record.message} {record.details}".lower()
            )
        ]
        self._refresh_keyword_summary()
        self._refresh_all_views()

    def _refresh_all_views(self) -> None:
        """刷新全部视图。"""

        self._refresh_summary_cards()
        self._refresh_stream_viewer()
        self._refresh_stats_badges()
        self._refresh_module_table()
        self._refresh_alert_tables()
        self._refresh_history_table()
        self._refresh_export_table()
        self._refresh_status_text()

    def _refresh_summary_cards(self) -> None:
        """刷新 KPI。"""

        total = len(self._visible_logs)
        error_count = sum(1 for item in self._visible_logs if item.level in {"ERROR", "FATAL"})
        module_count = len({item.module for item in self._visible_logs})
        self._summary_cards["total"].set_value(str(total))
        self._summary_cards["total"].set_trend("up" if total >= 8 else "flat", f"{self._date_filter_value}")
        self._summary_cards["errors"].set_value(str(error_count))
        self._summary_cards["errors"].set_trend("flat" if error_count <= 2 else "up", "高优先处理")
        self._summary_cards["modules"].set_value(str(module_count))
        self._summary_cards["modules"].set_trend("flat", "跨模块追踪")
        self._summary_cards["stream"].set_value("在线" if self._auto_refresh else "暂停")
        self._summary_cards["stream"].set_trend("up" if self._auto_refresh else "flat", "自动刷新" if self._auto_refresh else "手动模式")

    def _refresh_stream_viewer(self) -> None:
        """刷新实时流。"""

        if self._stream_viewer is None:
            return
        self._stream_viewer.clear_logs()
        for record in self._visible_logs[:10]:
            level = "WARNING" if record.level == "WARN" else record.level
            self._stream_viewer.append_log(level, f"{record.module} · {record.message} · {record.details}", record.timestamp)

    def _refresh_stats_badges(self) -> None:
        """刷新统计徽标。"""

        counts = {
            "DEBUG": sum(1 for item in self._visible_logs if item.level == "DEBUG"),
            "INFO": sum(1 for item in self._visible_logs if item.level == "INFO"),
            "WARN": sum(1 for item in self._visible_logs if item.level == "WARN"),
            "ERROR": sum(1 for item in self._visible_logs if item.level in {"ERROR", "FATAL"}),
            "MODULE": len({item.module for item in self._visible_logs}),
        }
        for key, badge in self._stats_badges.items():
            badge.set_value(str(counts[key]))

    def _refresh_module_table(self) -> None:
        """刷新模块统计表。"""

        if self._module_table is None:
            return
        rows = [
            (record.module_name, str(record.total_count), str(record.warning_count), record.owner, record.trend_text)
            for record in self._module_stats
            if self._module_filter_value in {"", "全部"} or record.module_name == self._module_filter_value
        ]
        self._module_table.set_rows(rows)

    def _refresh_history_table(self) -> None:
        """刷新历史表格。"""

        if self._history_table is None:
            return
        rows = [
            (record.timestamp, record.level, record.module, record.message, record.details)
            for record in self._visible_logs
        ]
        self._history_table.set_rows(rows)

    def _refresh_alert_tables(self) -> None:
        """刷新告警表和保存视图表。"""

        if self._alert_table is not None:
            alert_rows = [
                (record.priority, record.module, record.owner, record.status, record.summary)
                for record in self._alert_records
                if self._module_filter_value in {"", "全部"} or record.module == self._module_filter_value
            ]
            self._alert_table.set_rows(alert_rows)
        if self._saved_view_table is not None:
            view_rows = [
                (record.view_name, record.filter_text, record.owner, record.updated_at, record.note)
                for record in self._saved_views
            ]
            self._saved_view_table.set_rows(view_rows)
        if self._subscription_table is not None:
            subscription_rows = [
                (record.subscription_name, record.target, record.trigger_text, record.channel, record.enabled_text)
                for record in self._subscriptions
            ]
            self._subscription_table.set_rows(subscription_rows)

    def _refresh_export_table(self) -> None:
        """刷新导出历史。"""

        if self._export_table is None:
            return
        rows = [
            (record.exported_at, record.scope_text, record.count_text, record.operator, record.destination)
            for record in self._export_history
        ]
        self._export_table.set_rows(rows)

    def _refresh_status_text(self) -> None:
        """刷新状态文案。"""

        if self._status_hint_label is not None:
            storyline = self._diagnostic_storylines()[0]
            overview = "；".join((self._status_text, self._alert_backlog_text(), self._saved_view_summary(), self._export_summary(), storyline))
            _call(self._status_hint_label, "setText", overview)
        if self._auto_refresh_label is not None:
            _call(self._auto_refresh_label, "setText", "自动刷新：开启" if self._auto_refresh else "自动刷新：关闭")
        if self._scope_chip is not None:
            self._scope_chip.set_text(f"时间范围：{self._date_filter_value}")
        if self._level_chip is not None:
            self._level_chip.set_text(f"级别：{self._level_filter_value}")
        if self._stream_note_card is not None:
            note_parts = [f"自动刷新{'开启' if self._auto_refresh else '关闭'}", self._subscription_summary()]
            _call(self._stream_note_card, "set_description", "；".join(note_parts))

    def on_activated(self) -> None:
        """页面激活时刷新状态。"""

        if self._auto_refresh:
            self._status_text = "页面已激活，实时流保持自动刷新。"
            self._refresh_all_views()

    def on_deactivated(self) -> None:
        """页面离开时记录状态。"""

        self._status_text = "页面已离开，保留最近一次日志快照。"

    def _module_overview_text(self) -> str:
        """返回模块概览文案。"""

        if self._module_filter_value not in {"", "全部"}:
            return f"当前聚焦模块：{self._module_filter_value}"
        return f"当前覆盖模块：{len({item.module for item in self._visible_logs})} 个"

    def _level_overview_text(self) -> str:
        """返回级别概览文案。"""

        if self._level_filter_value not in {"", "全部"}:
            return f"当前级别：{self._level_filter_value}"
        return "当前级别：全部"

    def _history_summary_text(self) -> str:
        """返回历史表摘要。"""

        error_count = sum(1 for item in self._visible_logs if item.level in {"ERROR", "FATAL"})
        return f"历史表共 {len(self._visible_logs)} 条，其中高优先异常 {error_count} 条"

    def _refresh_keyword_summary(self) -> None:
        """整理关键筛选摘要。"""

        fragments = [self._module_overview_text(), self._level_overview_text(), self._history_summary_text()]
        self._status_text = " · ".join(fragments)

    def _diagnostic_storylines(self) -> tuple[str, ...]:
        """返回诊断提示列表。"""

        return (
            "如果 FATAL 日志开始集中出现在单一模块，建议先锁定该模块的最近部署和配置变化。",
            "当 WARN 数量突然升高但 ERROR 没有同步增加时，通常意味着系统仍在自愈边缘，需要提前介入。",
            "实时流适合看新事件，历史表更适合对比上下文，两个区域建议交替使用。",
            "保存视图后，团队可以用统一的筛选口径做交接和复盘，避免每次手动重构查询条件。",
            "导出日志前建议先缩小时间范围和模块范围，压缩包更小、复盘效率更高。",
            "若关闭自动刷新，请在关键故障观察结束后主动点击“立即刷新”，避免错过恢复信号。",
        )

    def _subscription_summary(self) -> str:
        """返回订阅汇总。"""

        enabled_count = sum(1 for item in self._subscriptions if item.enabled_text == "已开启")
        return f"当前共有 {len(self._subscriptions)} 条订阅规则，其中 {enabled_count} 条已开启。"

    def _module_health_snapshot(self) -> tuple[str, ...]:
        """返回模块健康快照。"""

        return tuple(
            f"{item.module_name}：{item.total_count} 条日志，告警 {item.warning_count} 条，负责人 {item.owner}。"
            for item in self._module_stats[:6]
        )

    def _alert_backlog_text(self) -> str:
        """返回告警积压摘要。"""

        processing_count = sum(1 for item in self._alert_records if item.status in {"处理中", "待确认"})
        return f"当前告警清单 {len(self._alert_records)} 项，其中 {processing_count} 项仍需跟进。"

    def _saved_view_summary(self) -> str:
        """返回视图摘要。"""

        latest = self._saved_views[0]
        return f"最近更新视图：{latest.view_name}（{latest.updated_at}）"

    def _export_summary(self) -> str:
        """返回导出摘要。"""

        latest = self._export_history[0]
        return f"最近导出：{latest.exported_at} · {latest.scope_text} · {latest.count_text}"

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
            QWidget#logCenterPage {{
                background-color: {colors.surface_alt};
            }}
            QFrame#logCenterFilterBar,
            QFrame#logCenterAutoHost {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#logCenterFilterBar {{
                border-color: {primary_border};
            }}
            QWidget#logCenterStatsStrip,
            QWidget#logCenterScopeBar {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#logCenterInlineText {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QWidget#logCenterPage QFrame#contentSection {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#logCenterPage QTableView {{
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#logCenterPage QFrame[variant="card"] {{
                background-color: {colors.surface};
            }}
            QWidget#logCenterPage QFrame#logCenterAutoHost {{
                background-color: {primary_soft};
                border-color: {primary_border};
            }}
            QWidget#logCenterPage QPushButton:hover {{
                border-color: {primary};
            }}
            QWidget#logCenterPage QLabel#pageContainerDescription {{
                color: {colors.text_muted};
            }}
            """,
        )


__all__ = ["LogCenterPage"]
