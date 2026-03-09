# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportCallIssue=false
from __future__ import annotations

"""版本升级页面。"""

from dataclasses import dataclass
from datetime import datetime

from ....core.qt import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    ContentSection,
    DataTable,
    InfoCard,
    KPICard,
    PageContainer,
    PrimaryButton,
    SecondaryButton,
    StatusBadge,
    TagChip,
    TaskProgressBar,
    TimelineWidget,
)
from ...components.inputs import (
    RADIUS_LG,
    SPACING_2XL,
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
class VersionRecord:
    """版本变更记录。"""

    version: str
    date_text: str
    title: str
    summary: str
    event_type: str


@dataclass(frozen=True)
class EnvironmentCheckRecord:
    """环境检查记录。"""

    check_name: str
    result: str
    status_text: str
    note: str


@dataclass(frozen=True)
class MirrorRecord:
    """镜像源记录。"""

    mirror_name: str
    region: str
    latency_text: str
    status_text: str
    recommendation: str


@dataclass(frozen=True)
class UpgradePlanRecord:
    """升级计划记录。"""

    stage_name: str
    owner: str
    status: str
    action_window: str
    note: str


@dataclass(frozen=True)
class ReleaseAssetRecord:
    """发布资源记录。"""

    asset_name: str
    size_text: str
    checksum_text: str
    channel_text: str
    note: str


@dataclass(frozen=True)
class RollbackCheckpointRecord:
    """回滚检查点记录。"""

    checkpoint_name: str
    created_at: str
    scope_text: str
    availability: str
    note: str


VERSION_HISTORY: tuple[VersionRecord, ...] = (
    VersionRecord("v2.8.4", "2026-03-09 09:30", "稳定补丁发布", "修复日志中心导出异常，优化权限矩阵加载性能。", "success"),
    VersionRecord("v2.8.3", "2026-03-05 18:20", "系统治理增强", "新增权限审计策略与角色模板同步逻辑。", "info"),
    VersionRecord("v2.8.2", "2026-03-01 16:10", "升级链路修复", "补充镜像回退与升级状态指示器。", "warning"),
    VersionRecord("v2.8.1", "2026-02-25 11:05", "巡检体验优化", "系统设置与日志中心支持更多实时反馈。", "info"),
    VersionRecord("v2.8.0", "2026-02-18 14:42", "系统域大版本", "系统域原型进入统一治理与升级准备阶段。", "success"),
)


ENVIRONMENT_CHECKS: tuple[EnvironmentCheckRecord, ...] = (
    EnvironmentCheckRecord("操作系统兼容性", "通过", "正常", "Windows 11 Pro 23H2 满足目标升级要求。"),
    EnvironmentCheckRecord("Python 运行时", "通过", "正常", "3.11.8 与当前升级包兼容。"),
    EnvironmentCheckRecord("系统盘剩余空间", "通过", "正常", "可用 128 GB，高于建议阈值 20 GB。"),
    EnvironmentCheckRecord("数据库快照", "待执行", "需处理", "建议升级前先执行一次本地快照备份。"),
    EnvironmentCheckRecord("镜像源稳定性", "观察中", "关注", "主镜像延迟上升，但备用节点可用。"),
    EnvironmentCheckRecord("内存占用", "通过", "正常", "当前占用 54%，适合执行后台升级下载。"),
    EnvironmentCheckRecord("重启窗口占用", "待确认", "需确认", "建议安排在 21:30 后执行。"),
    EnvironmentCheckRecord("回滚包准备", "通过", "正常", "已保留 v2.8.3 回滚包与数据库回退点。"),
)


MIRROR_SOURCES: tuple[MirrorRecord, ...] = (
    MirrorRecord("主镜像源", "华东节点", "2.6 秒", "观察中", "延迟略高，建议保留备用源。"),
    MirrorRecord("备用镜像源 A", "华北节点", "1.4 秒", "正常", "推荐作为当前下载优先节点。"),
    MirrorRecord("备用镜像源 B", "华南节点", "1.9 秒", "正常", "适合夜间批量下载窗口使用。"),
    MirrorRecord("海外镜像源", "新加坡节点", "3.8 秒", "关注", "仅在跨区域环境下使用。"),
    MirrorRecord("灾备镜像源", "离线包仓库", "本地可读", "正常", "适用于紧急回滚和离线补丁恢复。"),
    MirrorRecord("历史版本源", "归档仓库", "按需读取", "正常", "可提供 v2.7.x 至 v2.8.x 回滚包。"),
    MirrorRecord("证书校验源", "安全校验节点", "0.8 秒", "正常", "用于升级包摘要和签名校验。"),
    MirrorRecord("内部测试源", "灰度节点", "2.2 秒", "停用", "当前仅供实验特性验证，不建议生产使用。"),
)


UPGRADE_PLANS: tuple[UpgradePlanRecord, ...] = (
    UpgradePlanRecord("环境预检查", "系统管理员", "已完成", "今天 18:30", "已完成空间、内存、运行时与镜像可用性复核。"),
    UpgradePlanRecord("数据库快照", "系统管理员", "待执行", "今天 21:10", "升级前先生成一次完整本地快照。"),
    UpgradePlanRecord("升级包下载", "基础设施组", "进行中", "今天 21:15", "使用华北备用镜像源继续下载。"),
    UpgradePlanRecord("业务冻结提醒", "运营经理", "待执行", "今天 21:20", "通知团队暂停高风险配置变更。"),
    UpgradePlanRecord("应用重启升级", "系统管理员", "待执行", "今天 21:30", "升级完成后执行一次受控重启。"),
    UpgradePlanRecord("升级后验收", "系统平台组", "待执行", "今天 21:40", "重点验证日志中心、权限管理与系统设置。"),
    UpgradePlanRecord("回滚检查", "基础设施组", "已准备", "今天 21:45", "若升级失败，15 分钟内回退到 v2.8.3。"),
    UpgradePlanRecord("团队广播", "运营经理", "待执行", "今天 21:50", "完成升级后向工作群广播结果与风险提示。"),
)


RELEASE_ASSETS: tuple[ReleaseAssetRecord, ...] = (
    ReleaseAssetRecord("tkops-desktop-v2.8.4-full.zip", "842 MB", "sha256:d12a8c…", "稳定版", "完整升级包，适合生产环境直接升级。"),
    ReleaseAssetRecord("tkops-desktop-v2.8.4-patch.zip", "128 MB", "sha256:8f84d1…", "补丁包", "适合从 v2.8.3 快速升级到 v2.8.4。"),
    ReleaseAssetRecord("tkops-desktop-v2.8.4-symbols.zip", "96 MB", "sha256:1bb32e…", "调试包", "用于升级后异常排查和符号还原。"),
    ReleaseAssetRecord("tkops-desktop-v2.8.4-offline.pkg", "870 MB", "sha256:fe77a0…", "离线安装", "适合隔离网络环境或灾备演练。"),
    ReleaseAssetRecord("tkops-desktop-v2.8.4-release-notes.pdf", "3.2 MB", "sha256:0ad88f…", "说明文档", "供团队内训与升级说明使用。"),
    ReleaseAssetRecord("tkops-desktop-v2.8.4-db-migration.sql", "1.1 MB", "sha256:44a1c7…", "数据库脚本", "用于升级前审查数据库结构变更。"),
    ReleaseAssetRecord("tkops-desktop-v2.8.4-signature.sig", "12 KB", "sha256:11bca9…", "签名文件", "校验升级包签名完整性。"),
    ReleaseAssetRecord("tkops-desktop-v2.8.4-rollback.pkg", "836 MB", "sha256:cb7d82…", "回滚包", "升级失败时直接回退到上一稳定版本。"),
)


ROLLBACK_CHECKPOINTS: tuple[RollbackCheckpointRecord, ...] = (
    RollbackCheckpointRecord("数据库快照 A", "今天 20:50", "主数据库 / 权限配置 / 日志索引", "可用", "升级前建议再追加一次增量快照。"),
    RollbackCheckpointRecord("配置快照 B", "今天 20:45", "系统设置 / 主题 / 网络策略", "可用", "与当前工作区草稿保持一致。"),
    RollbackCheckpointRecord("版本包 C", "今天 19:30", "v2.8.3 完整安装包", "可用", "保留上一稳定版本的完整安装文件。"),
    RollbackCheckpointRecord("迁移脚本校验", "今天 19:10", "数据库迁移脚本", "可用", "SQL 回退脚本已通过静态校验。"),
    RollbackCheckpointRecord("运行时依赖锁定", "今天 18:58", "Python 运行时 / 插件依赖", "可用", "确保回滚后环境可重复。"),
    RollbackCheckpointRecord("镜像源切换点", "今天 18:42", "备用镜像源 A / 灾备仓库", "可用", "主镜像不稳定时可快速切换。"),
    RollbackCheckpointRecord("夜间广播模板", "今天 18:30", "升级失败通知模板", "可用", "出现回滚时用于快速同步团队。"),
    RollbackCheckpointRecord("日志快照归档", "今天 18:12", "升级前最后 24 小时日志", "可用", "便于升级后对比异常差异。"),
)

DESKTOP_PAGE_MAX_WIDTH = 1760


class VersionUpgradePage(BasePage):
    """版本升级页。"""

    default_route_id: RouteId = RouteId("version_upgrade")
    default_display_name: str = "版本升级"
    default_icon_name: str = "system_update"

    def __init__(self, parent: object | None = None) -> None:
        self._current_version = "v2.8.3"
        self._current_build_date = "2026-03-05 18:20"
        self._current_commit_hash = "9f4c2ab"
        self._latest_version = "v2.8.4"
        self._download_progress = 18
        self._auto_update = True
        self._status_text = "已检测到可用更新，建议在空闲窗口完成下载与重启。"
        self._environment_checks: list[EnvironmentCheckRecord] = list(ENVIRONMENT_CHECKS)
        self._mirror_sources: list[MirrorRecord] = list(MIRROR_SOURCES)
        self._upgrade_plans: list[UpgradePlanRecord] = list(UPGRADE_PLANS)
        self._release_assets: list[ReleaseAssetRecord] = list(RELEASE_ASSETS)
        self._rollback_points: list[RollbackCheckpointRecord] = list(ROLLBACK_CHECKPOINTS)

        self._page_container: PageContainer | None = None
        self._summary_cards: dict[str, KPICard] = {}
        self._status_badge: StatusBadge | None = None
        self._release_chip: TagChip | None = None
        self._check_button: PrimaryButton | None = None
        self._download_button: SecondaryButton | None = None
        self._rollback_button: SecondaryButton | None = None
        self._progress_bar: TaskProgressBar | None = None
        self._release_notes_label: QLabel | None = None
        self._progress_label: QLabel | None = None
        self._timeline: TimelineWidget | None = None
        self._summary_note_card: InfoCard | None = None
        self._auto_update_switch: ToggleSwitch | None = None
        self._auto_update_label: QLabel | None = None
        self._system_info_lines: dict[str, QLabel] = {}
        self._check_table: DataTable | None = None
        self._mirror_table: DataTable | None = None
        self._plan_table: DataTable | None = None
        self._asset_table: DataTable | None = None
        self._rollback_table: DataTable | None = None

        super().__init__(parent=parent)

    def setup_ui(self) -> None:
        """构建版本升级页面。"""

        _call(self, "setObjectName", "versionUpgradePage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self._check_button = PrimaryButton("检查更新", self, icon_text="↻")
        self._download_button = SecondaryButton("下载升级包", self, icon_text="⇩")
        self._rollback_button = SecondaryButton("查看回滚方案", self, icon_text="⟲")

        self._page_container = PageContainer(
            title="版本升级",
            description="查看当前版本信息、检测可用更新、管理下载进度与系统环境，适合系统管理员做升级准备与回滚评估。",
            actions=(self._check_button, self._download_button, self._rollback_button),
            max_width=DESKTOP_PAGE_MAX_WIDTH,
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._page_container.add_widget(self._build_summary_strip())
        self._page_container.add_widget(self._build_version_overview_section())
        self._page_container.add_widget(self._build_progress_section())
        self._page_container.add_widget(self._build_timeline_section())
        self._page_container.add_widget(self._build_checks_section())
        self._page_container.add_widget(self._build_mirror_section())
        self._page_container.add_widget(self._build_settings_section())
        self._page_container.add_widget(self._build_plan_section())
        self._page_container.add_widget(self._build_asset_section())
        self._page_container.add_widget(self._build_rollback_section())
        self._page_container.add_widget(self._build_system_info_section())

        self._apply_page_styles()
        self._bind_interactions()
        self._refresh_all_views()

    def _build_summary_strip(self) -> QWidget:
        """构建顶部 KPI。"""

        host = QWidget(self)
        row = QHBoxLayout(host)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACING_MD)

        self._summary_cards["version"] = KPICard("当前版本", self._current_version, trend="flat", percentage="稳定", caption="当前工作区运行中的版本号", sparkline_data=[280, 281, 282, 283, 283, 283, 284])
        self._summary_cards["latest"] = KPICard("最新可用", self._latest_version, trend="up", percentage="有更新", caption="远端升级源返回的最新稳定版本", sparkline_data=[281, 281, 282, 282, 283, 284, 284])
        self._summary_cards["progress"] = KPICard("下载进度", f"{self._download_progress}%", trend="up", percentage="进行中", caption="升级包拉取进度", sparkline_data=[0, 4, 8, 12, 15, 18, 18])
        self._summary_cards["readiness"] = KPICard("升级准备度", "高", trend="up", percentage="环境正常", caption="根据磁盘空间、内存和系统版本评估", sparkline_data=[65, 68, 72, 76, 81, 86, 91])
        for card in self._summary_cards.values():
            row.addWidget(card)
        return host

    def _build_version_overview_section(self) -> QWidget:
        """当前版本信息。"""

        section = ContentSection("当前版本信息", icon="◎", parent=self)
        card = QFrame(section)
        _call(card, "setObjectName", "versionUpgradeCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_LG)

        text_host = QWidget(card)
        text_layout = QVBoxLayout(text_host)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(SPACING_SM)
        title = QLabel(f"当前版本：{self._current_version}", text_host)
        subtitle = QLabel(f"构建日期：{self._current_build_date} · Commit：{self._current_commit_hash}", text_host)
        _call(title, "setObjectName", "versionUpgradeTitle")
        _call(subtitle, "setObjectName", "versionUpgradeText")
        self._status_badge = StatusBadge("待升级", tone="warning")
        self._release_chip = TagChip(f"最新稳定版 {self._latest_version}", tone="brand")
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        text_layout.addWidget(self._status_badge)
        text_layout.addWidget(self._release_chip)

        layout.addWidget(text_host, 1)
        section.add_widget(card)
        return section

    def _build_progress_section(self) -> QWidget:
        """下载进度区。"""

        section = ContentSection("升级进度与发布说明", icon="▤", parent=self)
        self._summary_note_card = InfoCard(
            title="升级建议",
            description="建议先完成环境预检查与数据库快照，再继续下载与受控重启。",
            icon="◈",
            action_text="采用建议",
        )
        self._progress_bar = TaskProgressBar(self._download_progress)
        self._progress_label = QLabel("升级包下载中，当前处于处理中阶段。", section)
        self._release_notes_label = QLabel(
            "• 新增系统域四个交互原型页面\n• 优化权限矩阵加载体验\n• 修复日志中心的历史记录导出提示\n• 增强升级镜像回退与状态展示",
            section,
        )
        _call(self._progress_label, "setObjectName", "versionUpgradeText")
        _call(self._release_notes_label, "setObjectName", "versionUpgradeNotes")
        _call(self._release_notes_label, "setWordWrap", True)
        section.add_widget(self._summary_note_card)
        section.add_widget(self._progress_bar)
        section.add_widget(self._progress_label)
        section.add_widget(self._release_notes_label)
        return section

    def _build_timeline_section(self) -> QWidget:
        """变更时间线。"""

        section = ContentSection("版本历史", icon="⧖", parent=self)
        self._timeline = TimelineWidget()
        section.add_widget(self._timeline)
        return section

    def _build_settings_section(self) -> QWidget:
        """自动更新设置。"""

        section = ContentSection("自动更新设置", icon="⚙", parent=self)
        host = QFrame(section)
        _call(host, "setObjectName", "versionUpgradeAutoCard")
        layout = QHBoxLayout(host)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_LG)
        self._auto_update_label = QLabel("自动更新：开启", host)
        _call(self._auto_update_label, "setObjectName", "versionUpgradeText")
        self._auto_update_switch = ToggleSwitch(True)
        note = QLabel("开启后将自动下载稳定补丁，并在重启前提醒你确认升级窗口。", host)
        _call(note, "setObjectName", "versionUpgradeText")
        _call(note, "setWordWrap", True)
        layout.addWidget(self._auto_update_label)
        layout.addWidget(self._auto_update_switch)
        layout.addWidget(note, 1)
        section.add_widget(host)
        return section

    def _build_checks_section(self) -> QWidget:
        """环境检查区。"""

        section = ContentSection("环境检查", icon="✓", parent=self)
        self._check_table = DataTable(
            headers=("检查项", "结果", "状态", "说明"),
            rows=(),
            page_size=8,
            empty_text="暂无环境检查记录",
            parent=section,
        )
        section.add_widget(self._check_table)
        return section

    def _build_mirror_section(self) -> QWidget:
        """镜像源区。"""

        section = ContentSection("镜像源状态", icon="☍", parent=self)
        self._mirror_table = DataTable(
            headers=("镜像名称", "区域", "延迟", "状态", "建议"),
            rows=(),
            page_size=8,
            empty_text="暂无镜像源信息",
            parent=section,
        )
        section.add_widget(self._mirror_table)
        return section

    def _build_plan_section(self) -> QWidget:
        """升级计划区。"""

        section = ContentSection("升级计划", icon="☷", parent=self)
        self._plan_table = DataTable(
            headers=("阶段", "负责人", "状态", "时间窗口", "备注"),
            rows=(),
            page_size=8,
            empty_text="暂无升级计划",
            parent=section,
        )
        section.add_widget(self._plan_table)
        return section

    def _build_asset_section(self) -> QWidget:
        """发布资源区。"""

        section = ContentSection("发布资源", icon="⬒", parent=self)
        self._asset_table = DataTable(
            headers=("资源名称", "大小", "摘要", "通道", "说明"),
            rows=(),
            page_size=8,
            empty_text="暂无发布资源",
            parent=section,
        )
        section.add_widget(self._asset_table)
        return section

    def _build_rollback_section(self) -> QWidget:
        """回滚准备区。"""

        section = ContentSection("回滚检查点", icon="⟲", parent=self)
        self._rollback_table = DataTable(
            headers=("检查点", "创建时间", "范围", "可用性", "说明"),
            rows=(),
            page_size=8,
            empty_text="暂无回滚检查点",
            parent=section,
        )
        section.add_widget(self._rollback_table)
        return section

    def _build_system_info_section(self) -> QWidget:
        """系统环境信息。"""

        section = ContentSection("系统信息", icon="⌂", parent=self)
        host = QFrame(section)
        _call(host, "setObjectName", "versionUpgradeSystemCard")
        layout = QVBoxLayout(host)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_SM)
        for key, text in (
            ("os", "操作系统：Windows 11 Pro 23H2"),
            ("python", "Python：3.11.8"),
            ("disk", "磁盘空间：系统盘可用 128 GB"),
            ("memory", "内存：32 GB / 当前占用 54%"),
        ):
            label = QLabel(text, host)
            _call(label, "setObjectName", "versionUpgradeText")
            self._system_info_lines[key] = label
            layout.addWidget(label)
        section.add_widget(host)
        return section

    def _bind_interactions(self) -> None:
        """绑定交互。"""

        if self._check_button is not None:
            _connect(getattr(self._check_button, "clicked", None), self._check_updates)
        if self._download_button is not None:
            _connect(getattr(self._download_button, "clicked", None), self._advance_download)
        if self._rollback_button is not None:
            _connect(getattr(self._rollback_button, "clicked", None), self._show_rollback_plan)
        if self._auto_update_switch is not None:
            _connect(getattr(self._auto_update_switch, "toggled", None), self._toggle_auto_update)

    def _check_updates(self) -> None:
        """模拟检查更新。"""

        self._latest_version = "v2.8.4"
        self._status_text = f"检查完成：发现最新稳定版 {self._latest_version}，可继续下载升级包。"
        self._refresh_all_views()

    def _advance_download(self) -> None:
        """推进下载进度。"""

        self._download_progress = min(100, self._download_progress + 28)
        if self._download_progress >= 100:
            self._current_version = self._latest_version
            self._current_build_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            self._current_commit_hash = "a84df19"
            self._status_text = "升级包下载完成，已准备重启并应用更新。"
        else:
            self._status_text = f"升级包下载已推进到 {self._download_progress}% 。"
        self._refresh_all_views()

    def _show_rollback_plan(self) -> None:
        """展示回滚方案。"""

        self._status_text = "已生成回滚预案：保留当前数据库快照，并在升级失败时回退到 v2.8.3。"
        self._refresh_all_views()

    def _toggle_auto_update(self, checked: bool) -> None:
        """切换自动更新。"""

        self._auto_update = checked
        self._status_text = f"自动更新已{'开启' if checked else '关闭'}。"
        self._refresh_all_views()

    def _refresh_all_views(self) -> None:
        """刷新全部视图。"""

        self._refresh_summary_cards()
        self._refresh_version_overview()
        self._refresh_progress_section()
        self._refresh_timeline()
        self._refresh_check_table()
        self._refresh_mirror_table()
        self._refresh_settings_section()
        self._refresh_plan_table()
        self._refresh_asset_table()
        self._refresh_rollback_table()
        self._refresh_system_info()

    def _refresh_summary_cards(self) -> None:
        """刷新 KPI。"""

        self._summary_cards["version"].set_value(self._current_version)
        self._summary_cards["version"].set_trend("flat", self._current_build_date)
        self._summary_cards["latest"].set_value(self._latest_version)
        self._summary_cards["latest"].set_trend("up", "稳定版")
        self._summary_cards["progress"].set_value(f"{self._download_progress}%")
        self._summary_cards["progress"].set_trend("up" if self._download_progress > 0 else "flat", "下载中" if self._download_progress < 100 else "已完成")
        readiness = "高" if self._download_progress < 100 else "已就绪"
        self._summary_cards["readiness"].set_value(readiness)
        self._summary_cards["readiness"].set_trend("up", "环境正常")

    def _refresh_version_overview(self) -> None:
        """刷新版本卡。"""

        if self._status_badge is not None:
            tone = "success" if self._download_progress >= 100 else "warning"
            _call(self._status_badge, "setText", "可重启应用" if tone == "success" else "待升级")
            self._status_badge.set_tone(tone)
        if self._release_chip is not None:
            self._release_chip.set_text(f"最新稳定版 {self._latest_version}")

    def _refresh_progress_section(self) -> None:
        """刷新进度区。"""

        if self._progress_bar is not None:
            self._progress_bar.set_progress(self._download_progress)
        if self._progress_label is not None:
            stage = "处理中" if self._download_progress < 100 else "完成"
            _call(self._progress_label, "setText", f"当前升级状态：{stage} · {self._status_text}")
        if self._release_notes_label is not None:
            _call(
                self._release_notes_label,
                "setText",
                "\n".join(f"• {line}" for line in self._release_summary_lines()),
            )
        if self._summary_note_card is not None:
            storyline = self._upgrade_storylines()[0]
            _call(
                self._summary_note_card,
                "set_description",
                "；".join((self._environment_summary_text(), self._mirror_summary_text(), self._rollback_summary_text(), self._plan_status_summary(), self._asset_summary_text(), self._release_channel_summary(), storyline, self._critical_action_summary())),
            )

    def _refresh_timeline(self) -> None:
        """刷新时间线。"""

        if self._timeline is None:
            return
        self._timeline.set_events(
            [
                {
                    "timestamp": record.date_text,
                    "title": f"{record.version} · {record.title}",
                    "content": record.summary,
                    "type": record.event_type,
                }
                for record in VERSION_HISTORY
            ]
        )

    def _refresh_check_table(self) -> None:
        """刷新环境检查表。"""

        if self._check_table is None:
            return
        rows = [
            (record.check_name, record.result, record.status_text, record.note)
            for record in self._environment_checks
        ]
        self._check_table.set_rows(rows)

    def _refresh_mirror_table(self) -> None:
        """刷新镜像源表。"""

        if self._mirror_table is None:
            return
        rows = [
            (record.mirror_name, record.region, record.latency_text, record.status_text, record.recommendation)
            for record in self._mirror_sources
        ]
        self._mirror_table.set_rows(rows)

    def _refresh_settings_section(self) -> None:
        """刷新自动更新设置。"""

        if self._auto_update_label is not None:
            _call(self._auto_update_label, "setText", "自动更新：开启" if self._auto_update else "自动更新：关闭")
        if self._auto_update_switch is not None and self._auto_update_switch.isChecked() != self._auto_update:
            self._auto_update_switch.setChecked(self._auto_update)

    def _refresh_plan_table(self) -> None:
        """刷新升级计划表。"""

        if self._plan_table is None:
            return
        rows = [
            (record.stage_name, record.owner, record.status, record.action_window, record.note)
            for record in self._upgrade_plans
        ]
        self._plan_table.set_rows(rows)

    def _refresh_asset_table(self) -> None:
        """刷新发布资源表。"""

        if self._asset_table is None:
            return
        rows = [
            (record.asset_name, record.size_text, record.checksum_text, record.channel_text, record.note)
            for record in self._release_assets
        ]
        self._asset_table.set_rows(rows)

    def _refresh_rollback_table(self) -> None:
        """刷新回滚检查点。"""

        if self._rollback_table is None:
            return
        rows = [
            (record.checkpoint_name, record.created_at, record.scope_text, record.availability, record.note)
            for record in self._rollback_points
        ]
        self._rollback_table.set_rows(rows)

    def _release_summary_lines(self) -> tuple[str, ...]:
        """返回发布说明摘要。"""

        return (
            f"当前版本 {self._current_version}，最新稳定版 {self._latest_version}。",
            f"升级包下载进度 {self._download_progress}% ，自动更新{'开启' if self._auto_update else '关闭'}。",
            "建议先执行数据库快照，再进行受控重启与业务验收。",
            "若升级失败，可使用准备好的 v2.8.3 回滚包与数据库快照在 15 分钟内恢复。",
            "镜像源推荐优先使用华北备用节点，以降低当前主镜像的延迟波动影响。",
            "升级后应重点检查权限管理、日志中心、系统设置和版本升级页的关键动作。",
        )

    def _environment_summary_text(self) -> str:
        """返回环境检查摘要。"""

        normal_count = sum(1 for item in self._environment_checks if item.status_text == "正常")
        attention_count = len(self._environment_checks) - normal_count
        return f"环境检查共 {len(self._environment_checks)} 项，正常 {normal_count} 项，待关注 {attention_count} 项。"

    def _mirror_summary_text(self) -> str:
        """返回镜像源摘要。"""

        healthy_count = sum(1 for item in self._mirror_sources if item.status_text == "正常")
        return f"镜像源共 {len(self._mirror_sources)} 个，其中 {healthy_count} 个可作为首选下载源。"

    def _rollback_summary_text(self) -> str:
        """返回回滚摘要。"""

        available_count = sum(1 for item in self._rollback_points if item.availability == "可用")
        return f"回滚检查点已准备 {available_count}/{len(self._rollback_points)} 项。"

    def _plan_status_summary(self) -> str:
        """返回计划摘要。"""

        finished_count = sum(1 for item in self._upgrade_plans if item.status in {"已完成", "已准备"})
        return f"升级计划共 {len(self._upgrade_plans)} 个阶段，其中 {finished_count} 个已就绪。"

    def _asset_summary_text(self) -> str:
        """返回资源摘要。"""

        return f"本次发布共准备 {len(self._release_assets)} 份资源，覆盖完整包、补丁包、离线包和回滚包。"

    def on_activated(self) -> None:
        """页面激活回调。"""

        self._status_text = "版本升级页已激活，可继续执行检查、下载和回滚评估。"
        self._refresh_all_views()

    def on_deactivated(self) -> None:
        """页面离开回调。"""

        self._status_text = "版本升级页已离开，保留当前下载进度与计划快照。"

    def _upgrade_storylines(self) -> tuple[str, ...]:
        """返回升级观察要点。"""

        return (
            "升级前的关键动作不是下载，而是确认快照、镜像源和回滚路径都处于可用状态。",
            "下载进度超过 80% 后，可以开始提前广播重启窗口，避免业务侧突然中断。",
            "若镜像源延迟持续升高，优先切换节点，不要在不稳定链路上继续重试。",
            "回滚检查点越完整，升级窗口就越短，团队协作的容错也越高。",
            "发布资源中的补丁包适合快速迭代，而完整包更适合作为稳定回退基线。",
            "升级后验收应从高风险系统页开始，再覆盖内容、分析和自动化主链路。",
        )

    def _critical_action_summary(self) -> str:
        """返回关键动作摘要。"""

        return f"关键动作：检查更新、下载升级包、数据库快照、受控重启、升级后验收。当前状态：{self._status_text}"

    def _operator_guidance_lines(self) -> tuple[str, ...]:
        """返回操作指导清单。"""

        return (
            "操作指引 1：先检查环境，再下载，不要跳过快照准备。",
            "操作指引 2：优先使用状态为“正常”的镜像源，避免在高延迟节点上反复重试。",
            "操作指引 3：升级完成后先验证系统域核心页，再继续业务域巡检。",
            "操作指引 4：若发现关键异常，直接使用回滚检查点，缩短恢复时间。",
        )

    def _release_channel_summary(self) -> str:
        """返回发布通道摘要。"""

        channel_counts: dict[str, int] = {}
        for asset in self._release_assets:
            channel_counts[asset.channel_text] = channel_counts.get(asset.channel_text, 0) + 1
        parts = [f"{channel} {count} 份" for channel, count in channel_counts.items()]
        return "发布通道分布：" + "、".join(parts)

    def _refresh_system_info(self) -> None:
        """刷新环境信息。"""

        mapping = {
            "os": f"操作系统：Windows 11 Pro 23H2 · {self._plan_status_summary()} · {self._operator_guidance_lines()[0]}",
            "python": f"Python：3.11.8 · {self._asset_summary_text()} · {self._operator_guidance_lines()[1]}",
            "disk": f"磁盘空间：系统盘可用 128 GB · {self._mirror_summary_text()} · {self._operator_guidance_lines()[2]}",
            "memory": f"内存：32 GB / 当前占用 54% · {self._rollback_summary_text()} · {self._operator_guidance_lines()[3]}",
        }
        for key, text in mapping.items():
            label = self._system_info_lines.get(key)
            if label is not None:
                _call(label, "setText", text)

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
            QWidget#versionUpgradePage {{
                background-color: {colors.surface_alt};
            }}
            QFrame#versionUpgradeAutoCard,
            QFrame#versionUpgradeSystemCard {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#versionUpgradeCard {{
                background-color: {primary_soft};
                border: 1px solid {primary_border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#versionUpgradePage QFrame#contentSection QFrame#versionUpgradeCard {{
                min-height: {SPACING_2XL * 7}px;
            }}
            QLabel#versionUpgradeTitle {{
                background: transparent;
                color: {colors.text};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#versionUpgradeText,
            QLabel#versionUpgradeNotes {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                line-height: 1.5;
            }}
            QWidget#versionUpgradePage QFrame#contentSection {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#versionUpgradePage QTableView {{
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#versionUpgradePage QFrame[variant="card"] {{
                background-color: {colors.surface};
            }}
            QWidget#versionUpgradePage QFrame#versionUpgradeAutoCard {{
                background-color: {primary_soft};
                border-color: {primary_border};
            }}
            QWidget#versionUpgradePage QPushButton:hover {{
                border-color: {primary};
            }}
            """,
        )


__all__ = ["VersionUpgradePage"]
