# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportCallIssue=false
from __future__ import annotations

"""系统设置页面。"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ....core.qt import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    ContentSection,
    DataTable,
    FormGroup,
    InfoCard,
    KPICard,
    PageContainer,
    PrimaryButton,
    SecondaryButton,
    StatusBadge,
    TabBar,
    TagChip,
    ThemedComboBox,
    ThemedLineEdit,
    ToggleSwitch,
)
from ...components.inputs import (
    BUTTON_HEIGHT,
    RADIUS_LG,
    SPACING_MD,
    SPACING_LG,
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
    """将十六进制颜色转换为 rgba。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


@dataclass(frozen=True)
class CategoryMeta:
    """分类说明。"""

    key: str
    title: str
    subtitle: str
    tip: str


@dataclass(frozen=True)
class ShortcutRecord:
    """快捷键示例记录。"""

    action_name: str
    keybinding: str
    area: str
    status: str
    note: str


@dataclass(frozen=True)
class SettingChangeRecord:
    """设置变更记录。"""

    changed_at: str
    category: str
    field_name: str
    changed_to: str
    operator: str


CATEGORY_METAS: tuple[CategoryMeta, ...] = (
    CategoryMeta("general", "通用", "系统级基础体验与启动行为", "适合先完成语言、开机启动与托盘行为配置。"),
    CategoryMeta("appearance", "外观", "主题、字号与布局宽度", "决定整个桌面工作台的视觉节奏与阅读舒适度。"),
    CategoryMeta("storage", "存储", "缓存、下载路径与数据库位置", "建议定期整理缓存并将下载目录放在高速磁盘。"),
    CategoryMeta("network", "网络", "代理、超时、重试与并发连接", "高峰投放期间建议为网络链路保留更高并发余量。"),
    CategoryMeta("notification", "通知", "桌面提醒、提示音与免打扰", "适合控制自动化任务与系统告警的打扰级别。"),
    CategoryMeta("shortcut", "快捷键", "常用动作的快捷触发入口", "把高频动作压缩成肌肉记忆，减少跨模块切换成本。"),
    CategoryMeta("advanced", "高级", "实验特性与风险控制开关", "仅建议给系统管理员或技术支持角色开放。"),
)


DEFAULT_SETTINGS_STATE: dict[str, object] = {
    "language": "简体中文",
    "auto_start": True,
    "minimize_to_tray": True,
    "check_updates_on_start": True,
    "theme_mode": "跟随系统",
    "font_size": "标准（14px）",
    "accent_color": "薄荷青 #00F2EA",
    "sidebar_width": "标准 264px",
    "download_path": str(Path.home() / "Downloads" / "TK-OPS"),
    "cache_size": "2.5 GB",
    "auto_cleanup": True,
    "database_location": str(Path.home() / "AppData" / "Local" / "TK-OPS" / "database.sqlite"),
    "proxy_address": "http://127.0.0.1:7890",
    "network_timeout": "18 秒",
    "retry_count": "3 次",
    "concurrent_connections": "12 路",
    "desktop_notification": True,
    "notification_sound": True,
    "dnd_schedule": "23:00 - 08:00",
    "quick_open_dashboard": "Ctrl + Shift + D",
    "quick_search_command": "Ctrl + K",
    "quick_new_task": "Ctrl + Alt + N",
    "quick_toggle_theme": "Ctrl + Shift + T",
    "quick_open_log_center": "Ctrl + Shift + L",
    "quick_screen_capture": "Ctrl + Alt + S",
    "quick_publish_panel": "Ctrl + Shift + P",
    "quick_sync_data": "Ctrl + Alt + Y",
    "advanced_debug_log": False,
    "advanced_safe_mode": True,
    "advanced_experimental": False,
    "advanced_keep_backup_days": "14 天",
    "advanced_gpu_strategy": "自动识别",
    "advanced_profile": "稳态运营配置",
}


SHORTCUT_RECORDS: tuple[ShortcutRecord, ...] = (
    ShortcutRecord("打开总览看板", "Ctrl + Shift + D", "导航", "已启用", "用于快速返回经营总览。"),
    ShortcutRecord("唤起全局命令面板", "Ctrl + K", "全局", "已启用", "支持搜索页面、命令与最近动作。"),
    ShortcutRecord("新建自动化任务", "Ctrl + Alt + N", "自动化", "已启用", "在任意页面唤起任务创建流程。"),
    ShortcutRecord("切换主题模式", "Ctrl + Shift + T", "外观", "已启用", "在亮色、暗色与自动之间轮换。"),
    ShortcutRecord("打开日志中心", "Ctrl + Shift + L", "系统", "已启用", "快速查看最近的运行异常与告警。"),
    ShortcutRecord("截取当前工作区", "Ctrl + Alt + S", "内容", "已启用", "保存到最近一次素材导出路径。"),
    ShortcutRecord("打开发布面板", "Ctrl + Shift + P", "运营", "已启用", "用于检查待发布计划与草稿内容。"),
    ShortcutRecord("触发本地数据同步", "Ctrl + Alt + Y", "数据", "已启用", "同步账号、素材与缓存索引。"),
)


INITIAL_CHANGE_RECORDS: tuple[SettingChangeRecord, ...] = (
    SettingChangeRecord("今天 08:05", "通用", "启动时检查更新", "已开启", "系统管理员"),
    SettingChangeRecord("今天 08:16", "外观", "主题模式", "跟随系统", "运营经理-华东组"),
    SettingChangeRecord("今天 08:28", "存储", "缓存大小上限", "2.5 GB", "系统管理员"),
    SettingChangeRecord("今天 08:40", "网络", "代理地址", "http://127.0.0.1:7890", "网络支持"),
    SettingChangeRecord("今天 09:05", "通知", "免打扰时段", "23:00 - 08:00", "运营经理-华南组"),
    SettingChangeRecord("今天 09:20", "快捷键", "打开日志中心", "Ctrl + Shift + L", "系统管理员"),
    SettingChangeRecord("今天 09:46", "高级", "安全模式", "已开启", "系统管理员"),
    SettingChangeRecord("今天 10:12", "外观", "侧边栏宽度", "标准 264px", "内容创作组"),
    SettingChangeRecord("今天 10:35", "网络", "并发连接数", "12 路", "网络支持"),
    SettingChangeRecord("今天 11:00", "高级", "配置档案", "稳态运营配置", "系统管理员"),
)

DESKTOP_PAGE_MAX_WIDTH = 1760


class SystemSettingsPage(BasePage):
    """系统设置主面板。"""

    default_route_id: RouteId = RouteId("system_settings")
    default_display_name: str = "系统设置"
    default_icon_name: str = "settings"

    def __init__(self, parent: object | None = None) -> None:
        self._saved_state: dict[str, object] = dict(DEFAULT_SETTINGS_STATE)
        self._draft_state: dict[str, object] = dict(DEFAULT_SETTINGS_STATE)
        self._recent_changes: list[SettingChangeRecord] = list(INITIAL_CHANGE_RECORDS)
        self._shortcut_records: list[ShortcutRecord] = list(SHORTCUT_RECORDS)
        self._current_category_index = 0
        self._is_syncing_widgets = False
        self._status_text = "尚未保存新的设置变更"

        self._page_container: PageContainer | None = None
        self._summary_cards: dict[str, KPICard] = {}
        self._tips_card: InfoCard | None = None
        self._status_badge: StatusBadge | None = None
        self._save_hint_label: QLabel | None = None
        self._active_profile_chip: TagChip | None = None
        self._category_tabs: TabBar | None = None
        self._current_category_label: QLabel | None = None
        self._current_tip_label: QLabel | None = None
        self._preview_lines: dict[str, QLabel] = {}
        self._footer_summary_label: QLabel | None = None
        self._save_button: PrimaryButton | None = None
        self._reset_button: SecondaryButton | None = None
        self._preset_button: SecondaryButton | None = None
        self._change_table: DataTable | None = None
        self._shortcut_table: DataTable | None = None

        self._language_combo: ThemedComboBox | None = None
        self._auto_start_toggle: ToggleSwitch | None = None
        self._tray_toggle: ToggleSwitch | None = None
        self._update_toggle: ToggleSwitch | None = None

        self._theme_combo: ThemedComboBox | None = None
        self._font_combo: ThemedComboBox | None = None
        self._accent_line: ThemedLineEdit | None = None
        self._sidebar_combo: ThemedComboBox | None = None

        self._download_path_line: ThemedLineEdit | None = None
        self._cache_size_line: ThemedLineEdit | None = None
        self._cleanup_toggle: ToggleSwitch | None = None
        self._database_line: ThemedLineEdit | None = None

        self._proxy_line: ThemedLineEdit | None = None
        self._timeout_combo: ThemedComboBox | None = None
        self._retry_combo: ThemedComboBox | None = None
        self._concurrency_combo: ThemedComboBox | None = None

        self._desktop_notification_toggle: ToggleSwitch | None = None
        self._sound_toggle: ToggleSwitch | None = None
        self._dnd_line: ThemedLineEdit | None = None

        self._shortcut_editors: dict[str, ThemedLineEdit] = {}

        self._debug_toggle: ToggleSwitch | None = None
        self._safe_mode_toggle: ToggleSwitch | None = None
        self._experimental_toggle: ToggleSwitch | None = None
        self._backup_combo: ThemedComboBox | None = None
        self._gpu_combo: ThemedComboBox | None = None
        self._profile_combo: ThemedComboBox | None = None

        super().__init__(parent=parent)

    def setup_ui(self) -> None:
        """构建页面。"""

        _call(self, "setObjectName", "systemSettingsPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self._preset_button = SecondaryButton("恢复推荐配置", self, icon_text="↺")
        self._page_container = PageContainer(
            title="系统设置",
            description="统一管理系统通用参数、外观偏好、网络链路、通知策略与高级运行配置，适合系统管理员与运营负责人做集中调优。",
            actions=(self._preset_button,),
            max_width=DESKTOP_PAGE_MAX_WIDTH,
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._page_container.add_widget(self._build_summary_strip())
        self._page_container.add_widget(self._build_focus_banner())
        self._page_container.add_widget(self._build_category_header())
        self._page_container.add_widget(self._build_settings_tabs())
        self._page_container.add_widget(self._build_change_section())
        self._page_container.add_widget(self._build_footer_bar())

        self._apply_page_styles()
        self._bind_interactions()
        self._sync_widgets_from_state()
        self._refresh_all_views()

    def _build_summary_strip(self) -> QWidget:
        """顶部 KPI 概览。"""

        host = QWidget(self)
        row = QHBoxLayout(host)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACING_MD)

        self._summary_cards["enabled"] = KPICard(
            title="已启用开关",
            value="0 / 0",
            trend="up",
            percentage="+0",
            caption="当前草稿中的启用项数量",
            sparkline_data=[7, 8, 8, 9, 10, 10, 11],
            parent=host,
        )
        self._summary_cards["appearance"] = KPICard(
            title="界面配置热度",
            value="标准",
            trend="flat",
            percentage="本周稳定",
            caption="主题、字号与布局配置状态",
            sparkline_data=[52, 53, 53, 54, 54, 54, 55],
            parent=host,
        )
        self._summary_cards["network"] = KPICard(
            title="网络策略评分",
            value="92 分",
            trend="up",
            percentage="+6 分",
            caption="综合超时、重试和并发给出的建议评分",
            sparkline_data=[78, 81, 85, 86, 89, 91, 92],
            parent=host,
        )
        self._summary_cards["safety"] = KPICard(
            title="安全稳态等级",
            value="高",
            trend="up",
            percentage="已加固",
            caption="由安全模式、备份保留与实验开关推导",
            sparkline_data=[64, 65, 67, 70, 73, 76, 81],
            parent=host,
        )

        for card in self._summary_cards.values():
            row.addWidget(card)
        return host

    def _build_focus_banner(self) -> QWidget:
        """状态提示横幅。"""

        banner = QFrame(self)
        _call(banner, "setObjectName", "systemSettingsBanner")
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_LG)

        self._tips_card = InfoCard(
            title="推荐动作",
            description="建议先检查外观与网络两组设置，再保存到当前工作区，避免在高峰任务执行时引入大范围行为变化。",
            icon="◎",
            action_text="查看建议",
            parent=banner,
        )

        status_host = QFrame(banner)
        _call(status_host, "setObjectName", "systemSettingsStatusHost")
        status_layout = QVBoxLayout(status_host)
        status_layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        status_layout.setSpacing(SPACING_SM)

        title_label = QLabel("当前配置档案", status_host)
        _call(title_label, "setObjectName", "systemSettingsBannerTitle")
        self._active_profile_chip = TagChip("稳态运营配置", tone="brand", parent=status_host)
        self._status_badge = StatusBadge("草稿未保存", tone="warning", parent=status_host)
        self._save_hint_label = QLabel("保存后将同步到当前工作区的本地配置快照。", status_host)
        _call(self._save_hint_label, "setObjectName", "systemSettingsBannerText")
        _call(self._save_hint_label, "setWordWrap", True)

        status_layout.addWidget(title_label)
        status_layout.addWidget(self._active_profile_chip)
        status_layout.addWidget(self._status_badge)
        status_layout.addWidget(self._save_hint_label)
        status_layout.addStretch(1)

        layout.addWidget(self._tips_card, 2)
        layout.addWidget(status_host, 1)
        return banner

    def _build_category_header(self) -> QWidget:
        """当前分类摘要。"""

        host = QFrame(self)
        _call(host, "setObjectName", "systemSettingsCategoryHeader")
        layout = QHBoxLayout(host)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_LG)

        text_host = QWidget(host)
        text_layout = QVBoxLayout(text_host)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(SPACING_XS)

        self._current_category_label = QLabel("通用", text_host)
        self._current_tip_label = QLabel("适合先完成语言、开机启动与托盘行为配置。", text_host)
        _call(self._current_category_label, "setObjectName", "systemSettingsCategoryTitle")
        _call(self._current_tip_label, "setObjectName", "systemSettingsCategoryDesc")
        _call(self._current_tip_label, "setWordWrap", True)

        text_layout.addWidget(self._current_category_label)
        text_layout.addWidget(self._current_tip_label)

        preview_host = QWidget(host)
        preview_layout = QVBoxLayout(preview_host)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(SPACING_XS)

        for key, label_text in (
            ("theme", "主题预览：-"),
            ("network", "网络策略：-"),
            ("notify", "通知策略：-"),
        ):
            label = QLabel(label_text, preview_host)
            _call(label, "setObjectName", "systemSettingsPreviewLine")
            self._preview_lines[key] = label
            preview_layout.addWidget(label)

        layout.addWidget(text_host, 2)
        layout.addWidget(preview_host, 1)
        return host

    def _build_settings_tabs(self) -> QWidget:
        """分类标签区。"""

        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)

        self._category_tabs = TabBar(host)
        self._category_tabs.add_tab("通用", self._create_general_tab())
        self._category_tabs.add_tab("外观", self._create_appearance_tab())
        self._category_tabs.add_tab("存储", self._create_storage_tab())
        self._category_tabs.add_tab("网络", self._create_network_tab())
        self._category_tabs.add_tab("通知", self._create_notification_tab())
        self._category_tabs.add_tab("快捷键", self._create_shortcut_tab())
        self._category_tabs.add_tab("高级", self._create_advanced_tab())
        layout.addWidget(self._category_tabs)
        return host

    def _create_general_tab(self) -> QWidget:
        """通用设置页。"""

        tab = QWidget(self)
        root = QVBoxLayout(tab)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(SPACING_LG)

        basic_section = ContentSection("基础行为", icon="◉", parent=tab)
        basic_row = QHBoxLayout()
        basic_row.setContentsMargins(0, 0, 0, 0)
        basic_row.setSpacing(SPACING_XL)

        self._language_combo = ThemedComboBox("界面语言", ("简体中文", "繁體中文", "英文"))
        self._auto_start_toggle = ToggleSwitch(True)
        auto_start_group = FormGroup("开机自动启动", self._auto_start_toggle, "启动系统后自动拉起桌面应用。")

        basic_row.addWidget(self._language_combo, 1)
        basic_row.addWidget(auto_start_group, 1)
        basic_section.content_layout.addLayout(basic_row)

        misc_row = QHBoxLayout()
        misc_row.setContentsMargins(0, 0, 0, 0)
        misc_row.setSpacing(SPACING_XL)
        self._tray_toggle = ToggleSwitch(True)
        self._update_toggle = ToggleSwitch(True)
        misc_row.addWidget(FormGroup("最小化到托盘", self._tray_toggle, "关闭窗口时保留后台任务入口。"), 1)
        misc_row.addWidget(FormGroup("启动时检查更新", self._update_toggle, "在应用启动后自动执行版本检测。"), 1)
        basic_section.content_layout.addLayout(misc_row)

        suggestion_section = ContentSection("建议说明", icon="✦", parent=tab)
        suggestion_card = InfoCard(
            title="通用设置建议",
            description="如果你的工作台会执行夜间任务，建议同时开启开机启动与托盘驻留，并保留启动时检查更新。",
            icon="△",
            action_text="采用推荐值",
            parent=suggestion_section,
        )
        suggestion_section.add_widget(suggestion_card)

        root.addWidget(basic_section)
        root.addWidget(suggestion_section)
        root.addStretch(1)
        return tab

    def _create_appearance_tab(self) -> QWidget:
        """外观设置页。"""

        tab = QWidget(self)
        root = QVBoxLayout(tab)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(SPACING_LG)

        appearance_section = ContentSection("界面风格", icon="◌", parent=tab)
        row_one = QHBoxLayout()
        row_one.setContentsMargins(0, 0, 0, 0)
        row_one.setSpacing(SPACING_XL)
        self._theme_combo = ThemedComboBox("主题模式", ("浅色模式", "深色模式", "跟随系统"))
        self._font_combo = ThemedComboBox("字体大小", ("紧凑（13px）", "标准（14px）", "舒适（16px）", "演示（18px）"))
        row_one.addWidget(self._theme_combo, 1)
        row_one.addWidget(self._font_combo, 1)
        appearance_section.content_layout.addLayout(row_one)

        row_two = QHBoxLayout()
        row_two.setContentsMargins(0, 0, 0, 0)
        row_two.setSpacing(SPACING_XL)
        self._accent_line = ThemedLineEdit("强调色", "例如：薄荷青 #00F2EA", "支持手动输入色值和命名说明。")
        self._sidebar_combo = ThemedComboBox("侧边栏宽度", ("紧凑 232px", "标准 264px", "舒展 296px", "演示 328px"))
        row_two.addWidget(self._accent_line, 1)
        row_two.addWidget(self._sidebar_combo, 1)
        appearance_section.content_layout.addLayout(row_two)

        mood_section = ContentSection("视觉提示", icon="✧", parent=tab)
        mood_label = QLabel("推荐在深色模式下搭配标准字号与薄荷青强调色，以获得更稳定的夜间巡检体验。", mood_section)
        _call(mood_label, "setObjectName", "systemSettingsPlainText")
        _call(mood_label, "setWordWrap", True)
        mood_section.add_widget(mood_label)

        root.addWidget(appearance_section)
        root.addWidget(mood_section)
        root.addStretch(1)
        return tab

    def _create_storage_tab(self) -> QWidget:
        """存储设置页。"""

        tab = QWidget(self)
        root = QVBoxLayout(tab)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(SPACING_LG)

        storage_section = ContentSection("本地存储策略", icon="▣", parent=tab)
        self._download_path_line = ThemedLineEdit("下载路径", "请输入下载路径", "建议放在读写速度更高的磁盘目录。")
        self._cache_size_line = ThemedLineEdit("缓存大小上限", "例如：2.5 GB", "达到阈值后将结合自动清理策略释放空间。")
        self._database_line = ThemedLineEdit("数据库位置", "请输入数据库文件位置", "修改后建议在空闲时段迁移数据。")
        self._cleanup_toggle = ToggleSwitch(True)
        cleanup_group = FormGroup("自动清理缓存", self._cleanup_toggle, "每天凌晨自动清理陈旧缓存与临时索引。")

        storage_section.add_widget(self._download_path_line)
        storage_section.add_widget(self._cache_size_line)
        storage_section.add_widget(cleanup_group)
        storage_section.add_widget(self._database_line)

        storage_notice = ContentSection("存储提醒", icon="⚑", parent=tab)
        storage_notice_card = InfoCard(
            title="空间占用提醒",
            description="当素材下载量较高时，缓存与缩略图索引会快速增长，建议保留自动清理并定期归档数据库。",
            icon="◈",
            action_text="查看清理建议",
            parent=storage_notice,
        )
        storage_notice.add_widget(storage_notice_card)

        root.addWidget(storage_section)
        root.addWidget(storage_notice)
        root.addStretch(1)
        return tab

    def _create_network_tab(self) -> QWidget:
        """网络设置页。"""

        tab = QWidget(self)
        root = QVBoxLayout(tab)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(SPACING_LG)

        network_section = ContentSection("网络链路", icon="⇄", parent=tab)
        self._proxy_line = ThemedLineEdit("代理设置", "例如：http://127.0.0.1:7890", "支持 http、https 与 socks5 样式地址。")

        row_one = QHBoxLayout()
        row_one.setContentsMargins(0, 0, 0, 0)
        row_one.setSpacing(SPACING_XL)
        self._timeout_combo = ThemedComboBox("超时设置", ("10 秒", "18 秒", "24 秒", "30 秒"))
        self._retry_combo = ThemedComboBox("失败重试", ("1 次", "2 次", "3 次", "5 次"))
        row_one.addWidget(self._timeout_combo, 1)
        row_one.addWidget(self._retry_combo, 1)

        row_two = QHBoxLayout()
        row_two.setContentsMargins(0, 0, 0, 0)
        row_two.setSpacing(SPACING_XL)
        self._concurrency_combo = ThemedComboBox("并发连接数", ("6 路", "8 路", "12 路", "16 路", "24 路"))
        network_tip = QLabel("建议在多账号巡检场景中使用 12 路并发；若网络波动明显，可下调并发并提高超时。", network_section)
        _call(network_tip, "setObjectName", "systemSettingsPlainText")
        _call(network_tip, "setWordWrap", True)
        row_two.addWidget(self._concurrency_combo, 1)
        row_two.addWidget(network_tip, 1)

        network_section.add_widget(self._proxy_line)
        network_section.content_layout.addLayout(row_one)
        network_section.content_layout.addLayout(row_two)

        root.addWidget(network_section)
        root.addStretch(1)
        return tab

    def _create_notification_tab(self) -> QWidget:
        """通知设置页。"""

        tab = QWidget(self)
        root = QVBoxLayout(tab)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(SPACING_LG)

        notification_section = ContentSection("告警与提醒", icon="♪", parent=tab)
        self._desktop_notification_toggle = ToggleSwitch(True)
        self._sound_toggle = ToggleSwitch(True)
        self._dnd_line = ThemedLineEdit("免打扰时段", "例如：23:00 - 08:00", "在此时间范围内仅保留严重错误提醒。")

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACING_XL)
        row.addWidget(FormGroup("桌面通知", self._desktop_notification_toggle, "任务完成、失败与系统提示会在桌面弹出。"), 1)
        row.addWidget(FormGroup("提示音", self._sound_toggle, "严重错误和关键成功节点使用不同提示音。"), 1)

        notification_section.content_layout.addLayout(row)
        notification_section.add_widget(self._dnd_line)

        quiet_section = ContentSection("提醒建议", icon="☾", parent=tab)
        quiet_label = QLabel("对于全天候巡检团队，推荐保留桌面通知并把提示音限制在工作时段，减少夜间打扰。", quiet_section)
        _call(quiet_label, "setObjectName", "systemSettingsPlainText")
        _call(quiet_label, "setWordWrap", True)
        quiet_section.add_widget(quiet_label)

        root.addWidget(notification_section)
        root.addWidget(quiet_section)
        root.addStretch(1)
        return tab

    def _create_shortcut_tab(self) -> QWidget:
        """快捷键设置页。"""

        tab = QWidget(self)
        root = QVBoxLayout(tab)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(SPACING_LG)

        shortcut_section = ContentSection("快捷键映射", icon="⌘", parent=tab)
        for field_key, label, helper in (
            ("quick_open_dashboard", "打开总览看板", "用于快速回到全局经营看板。"),
            ("quick_search_command", "唤起全局命令面板", "建议保留单手可触达组合。"),
            ("quick_new_task", "新建自动化任务", "用于快速发起采集或发布任务。"),
            ("quick_toggle_theme", "切换主题模式", "适合在投影与夜间办公场景快速切换。"),
            ("quick_open_log_center", "打开日志中心", "遇到异常时可直接跳转系统日志页。"),
            ("quick_screen_capture", "截取当前工作区", "生成素材讨论图与巡检快照。"),
            ("quick_publish_panel", "打开发布面板", "快速定位待发布与已预约内容。"),
            ("quick_sync_data", "触发本地数据同步", "用于刷新本地缓存和工作区索引。"),
        ):
            editor = ThemedLineEdit(label, "请输入组合键", helper)
            self._shortcut_editors[field_key] = editor
            shortcut_section.add_widget(editor)

        overview_section = ContentSection("快捷键清单", icon="☰", parent=tab)
        self._shortcut_table = DataTable(
            headers=("动作", "快捷键", "区域", "状态", "说明"),
            rows=(),
            page_size=8,
            empty_text="暂无快捷键记录",
            parent=overview_section,
        )
        overview_section.add_widget(self._shortcut_table)

        root.addWidget(shortcut_section)
        root.addWidget(overview_section)
        root.addStretch(1)
        return tab

    def _create_advanced_tab(self) -> QWidget:
        """高级设置页。"""

        tab = QWidget(self)
        root = QVBoxLayout(tab)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(SPACING_LG)

        advanced_section = ContentSection("高级策略", icon="⚙", parent=tab)
        toggle_row = QHBoxLayout()
        toggle_row.setContentsMargins(0, 0, 0, 0)
        toggle_row.setSpacing(SPACING_XL)

        self._debug_toggle = ToggleSwitch(False)
        self._safe_mode_toggle = ToggleSwitch(True)
        self._experimental_toggle = ToggleSwitch(False)

        toggle_row.addWidget(FormGroup("调试日志", self._debug_toggle, "开启后将记录更细粒度的系统运行信息。"), 1)
        toggle_row.addWidget(FormGroup("安全模式", self._safe_mode_toggle, "限制高风险实验动作，优先保证稳定性。"), 1)
        toggle_row.addWidget(FormGroup("实验特性", self._experimental_toggle, "用于试用新能力与灰度功能。"), 1)
        advanced_section.content_layout.addLayout(toggle_row)

        option_row = QHBoxLayout()
        option_row.setContentsMargins(0, 0, 0, 0)
        option_row.setSpacing(SPACING_XL)
        self._backup_combo = ThemedComboBox("备份保留期", ("7 天", "14 天", "30 天", "90 天"))
        self._gpu_combo = ThemedComboBox("GPU 策略", ("自动识别", "优先独显", "节能模式", "仅 CPU"))
        self._profile_combo = ThemedComboBox("配置档案", ("稳态运营配置", "高性能拉满", "低干扰巡检", "夜间批处理"))
        option_row.addWidget(self._backup_combo, 1)
        option_row.addWidget(self._gpu_combo, 1)
        option_row.addWidget(self._profile_combo, 1)
        advanced_section.content_layout.addLayout(option_row)

        risk_section = ContentSection("风险提示", icon="!", parent=tab)
        risk_label = QLabel("启用实验特性时，建议同时开启安全模式并保留 14 天以上的配置备份，以便回退。", risk_section)
        _call(risk_label, "setObjectName", "systemSettingsPlainText")
        _call(risk_label, "setWordWrap", True)
        risk_section.add_widget(risk_label)

        root.addWidget(advanced_section)
        root.addWidget(risk_section)
        root.addStretch(1)
        return tab

    def _build_change_section(self) -> QWidget:
        """变更记录区。"""

        section = ContentSection("最近设置变更", icon="≡", parent=self)
        self._change_table = DataTable(
            headers=("时间", "分类", "字段", "变更结果", "操作人"),
            rows=(),
            page_size=10,
            empty_text="暂无变更记录",
            parent=section,
        )
        section.add_widget(self._change_table)
        return section

    def _build_footer_bar(self) -> QWidget:
        """底部保存栏。"""

        footer = QFrame(self)
        _call(footer, "setObjectName", "systemSettingsFooter")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_LG)

        text_host = QWidget(footer)
        text_layout = QVBoxLayout(text_host)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(SPACING_XS)
        footer_title = QLabel("保存前确认", text_host)
        _call(footer_title, "setObjectName", "systemSettingsFooterTitle")
        self._footer_summary_label = QLabel("当前草稿与已保存配置一致。", text_host)
        _call(self._footer_summary_label, "setObjectName", "systemSettingsFooterText")
        _call(self._footer_summary_label, "setWordWrap", True)
        text_layout.addWidget(footer_title)
        text_layout.addWidget(self._footer_summary_label)

        self._reset_button = SecondaryButton("重置", footer, icon_text="↻")
        self._save_button = PrimaryButton("保存设置", footer, icon_text="✓")

        layout.addWidget(text_host, 1)
        layout.addWidget(self._reset_button)
        layout.addWidget(self._save_button)
        return footer

    def _bind_interactions(self) -> None:
        """绑定交互。"""

        if self._preset_button is not None:
            _connect(getattr(self._preset_button, "clicked", None), self._apply_recommended_profile)
        if self._save_button is not None:
            _connect(getattr(self._save_button, "clicked", None), self._save_settings)
        if self._reset_button is not None:
            _connect(getattr(self._reset_button, "clicked", None), self._reset_settings)
        if self._category_tabs is not None:
            _connect(getattr(self._category_tabs, "tab_changed", None), self._on_category_changed)

        self._bind_combo(self._language_combo, "language")
        self._bind_toggle(self._auto_start_toggle, "auto_start")
        self._bind_toggle(self._tray_toggle, "minimize_to_tray")
        self._bind_toggle(self._update_toggle, "check_updates_on_start")

        self._bind_combo(self._theme_combo, "theme_mode")
        self._bind_combo(self._font_combo, "font_size")
        self._bind_line(self._accent_line, "accent_color")
        self._bind_combo(self._sidebar_combo, "sidebar_width")

        self._bind_line(self._download_path_line, "download_path")
        self._bind_line(self._cache_size_line, "cache_size")
        self._bind_toggle(self._cleanup_toggle, "auto_cleanup")
        self._bind_line(self._database_line, "database_location")

        self._bind_line(self._proxy_line, "proxy_address")
        self._bind_combo(self._timeout_combo, "network_timeout")
        self._bind_combo(self._retry_combo, "retry_count")
        self._bind_combo(self._concurrency_combo, "concurrent_connections")

        self._bind_toggle(self._desktop_notification_toggle, "desktop_notification")
        self._bind_toggle(self._sound_toggle, "notification_sound")
        self._bind_line(self._dnd_line, "dnd_schedule")

        for field_name, editor in self._shortcut_editors.items():
            self._bind_line(editor, field_name)

        self._bind_toggle(self._debug_toggle, "advanced_debug_log")
        self._bind_toggle(self._safe_mode_toggle, "advanced_safe_mode")
        self._bind_toggle(self._experimental_toggle, "advanced_experimental")
        self._bind_combo(self._backup_combo, "advanced_keep_backup_days")
        self._bind_combo(self._gpu_combo, "advanced_gpu_strategy")
        self._bind_combo(self._profile_combo, "advanced_profile")

    def _bind_line(self, widget: ThemedLineEdit | None, field_name: str) -> None:
        """绑定文本输入。"""

        if widget is None:
            return
        _connect(getattr(widget.line_edit, "textChanged", None), lambda text, key=field_name: self._update_draft_value(key, str(text)))

    def _bind_combo(self, widget: ThemedComboBox | None, field_name: str) -> None:
        """绑定下拉选择。"""

        if widget is None:
            return
        _connect(getattr(widget.combo_box, "currentTextChanged", None), lambda text, key=field_name: self._update_draft_value(key, str(text)))

    def _bind_toggle(self, widget: ToggleSwitch | None, field_name: str) -> None:
        """绑定开关。"""

        if widget is None:
            return
        _connect(getattr(widget, "toggled", None), lambda checked, key=field_name: self._update_draft_value(key, bool(checked)))

    def _sync_widgets_from_state(self) -> None:
        """将草稿状态同步到控件。"""

        self._is_syncing_widgets = True
        try:
            self._set_combo_text(self._language_combo, str(self._draft_state["language"]))
            self._set_toggle_state(self._auto_start_toggle, bool(self._draft_state["auto_start"]))
            self._set_toggle_state(self._tray_toggle, bool(self._draft_state["minimize_to_tray"]))
            self._set_toggle_state(self._update_toggle, bool(self._draft_state["check_updates_on_start"]))

            self._set_combo_text(self._theme_combo, str(self._draft_state["theme_mode"]))
            self._set_combo_text(self._font_combo, str(self._draft_state["font_size"]))
            self._set_line_text(self._accent_line, str(self._draft_state["accent_color"]))
            self._set_combo_text(self._sidebar_combo, str(self._draft_state["sidebar_width"]))

            self._set_line_text(self._download_path_line, str(self._draft_state["download_path"]))
            self._set_line_text(self._cache_size_line, str(self._draft_state["cache_size"]))
            self._set_toggle_state(self._cleanup_toggle, bool(self._draft_state["auto_cleanup"]))
            self._set_line_text(self._database_line, str(self._draft_state["database_location"]))

            self._set_line_text(self._proxy_line, str(self._draft_state["proxy_address"]))
            self._set_combo_text(self._timeout_combo, str(self._draft_state["network_timeout"]))
            self._set_combo_text(self._retry_combo, str(self._draft_state["retry_count"]))
            self._set_combo_text(self._concurrency_combo, str(self._draft_state["concurrent_connections"]))

            self._set_toggle_state(self._desktop_notification_toggle, bool(self._draft_state["desktop_notification"]))
            self._set_toggle_state(self._sound_toggle, bool(self._draft_state["notification_sound"]))
            self._set_line_text(self._dnd_line, str(self._draft_state["dnd_schedule"]))

            for field_name, editor in self._shortcut_editors.items():
                self._set_line_text(editor, str(self._draft_state[field_name]))

            self._set_toggle_state(self._debug_toggle, bool(self._draft_state["advanced_debug_log"]))
            self._set_toggle_state(self._safe_mode_toggle, bool(self._draft_state["advanced_safe_mode"]))
            self._set_toggle_state(self._experimental_toggle, bool(self._draft_state["advanced_experimental"]))
            self._set_combo_text(self._backup_combo, str(self._draft_state["advanced_keep_backup_days"]))
            self._set_combo_text(self._gpu_combo, str(self._draft_state["advanced_gpu_strategy"]))
            self._set_combo_text(self._profile_combo, str(self._draft_state["advanced_profile"]))
        finally:
            self._is_syncing_widgets = False

    def _set_line_text(self, widget: ThemedLineEdit | None, value: str) -> None:
        """设置输入框文本。"""

        if widget is not None:
            widget.setText(value)

    def _set_combo_text(self, widget: ThemedComboBox | None, value: str) -> None:
        """设置下拉值。"""

        if widget is not None:
            _call(widget.combo_box, "setCurrentText", value)

    def _set_toggle_state(self, widget: ToggleSwitch | None, value: bool) -> None:
        """设置开关状态。"""

        if widget is not None:
            widget.setChecked(value)

    def _update_draft_value(self, field_name: str, value: object) -> None:
        """更新草稿状态。"""

        if self._is_syncing_widgets:
            return
        previous = self._draft_state.get(field_name)
        if previous == value:
            return
        self._draft_state[field_name] = value
        self._status_text = f"已修改 {self._field_label(field_name)}，等待保存"
        self._refresh_all_views()

    def _field_label(self, field_name: str) -> str:
        """返回字段显示名。"""

        mapping = {
            "language": "界面语言",
            "auto_start": "开机自动启动",
            "minimize_to_tray": "最小化到托盘",
            "check_updates_on_start": "启动时检查更新",
            "theme_mode": "主题模式",
            "font_size": "字体大小",
            "accent_color": "强调色",
            "sidebar_width": "侧边栏宽度",
            "download_path": "下载路径",
            "cache_size": "缓存大小上限",
            "auto_cleanup": "自动清理缓存",
            "database_location": "数据库位置",
            "proxy_address": "代理设置",
            "network_timeout": "超时设置",
            "retry_count": "失败重试",
            "concurrent_connections": "并发连接数",
            "desktop_notification": "桌面通知",
            "notification_sound": "提示音",
            "dnd_schedule": "免打扰时段",
            "advanced_debug_log": "调试日志",
            "advanced_safe_mode": "安全模式",
            "advanced_experimental": "实验特性",
            "advanced_keep_backup_days": "备份保留期",
            "advanced_gpu_strategy": "GPU 策略",
            "advanced_profile": "配置档案",
        }
        if field_name in mapping:
            return mapping[field_name]
        for record in self._shortcut_records:
            if self._shortcut_field_name(record) == field_name:
                return record.action_name
        return field_name

    def _shortcut_field_name(self, record: ShortcutRecord) -> str:
        """从快捷键记录推导字段名。"""

        lookup = {
            "打开总览看板": "quick_open_dashboard",
            "唤起全局命令面板": "quick_search_command",
            "新建自动化任务": "quick_new_task",
            "切换主题模式": "quick_toggle_theme",
            "打开日志中心": "quick_open_log_center",
            "截取当前工作区": "quick_screen_capture",
            "打开发布面板": "quick_publish_panel",
            "触发本地数据同步": "quick_sync_data",
        }
        return lookup.get(record.action_name, record.action_name)

    def _on_category_changed(self, index: int) -> None:
        """响应分类切换。"""

        self._current_category_index = index
        self._refresh_all_views()

    def _save_settings(self) -> None:
        """保存设置。"""

        changed_fields = [key for key, value in self._draft_state.items() if self._saved_state.get(key) != value]
        if not changed_fields:
            self._status_text = "没有新的变化需要保存"
            self._refresh_all_views()
            return

        self._saved_state = dict(self._draft_state)
        changed_labels = []
        for field_name in changed_fields[:5]:
            changed_labels.append(self._field_label(field_name))
            self._recent_changes.insert(
                0,
                SettingChangeRecord(
                    changed_at=datetime.now().strftime("今天 %H:%M"),
                    category=self._category_for_field(field_name),
                    field_name=self._field_label(field_name),
                    changed_to=self._format_state_value(self._draft_state[field_name]),
                    operator="当前工作区",
                ),
            )
        self._recent_changes = self._recent_changes[:12]
        self._status_text = f"已保存 {len(changed_fields)} 项变更：{'、'.join(changed_labels)}"
        self._refresh_all_views()

    def _reset_settings(self) -> None:
        """重置为最近保存状态。"""

        self._draft_state = dict(self._saved_state)
        self._sync_widgets_from_state()
        self._status_text = "已恢复到最近一次保存的配置"
        self._refresh_all_views()

    def _apply_recommended_profile(self) -> None:
        """应用推荐配置。"""

        self._draft_state.update(
            {
                "theme_mode": "深色模式",
                "font_size": "标准（14px）",
                "accent_color": "薄荷青 #00F2EA",
                "sidebar_width": "标准 264px",
                "network_timeout": "24 秒",
                "retry_count": "3 次",
                "concurrent_connections": "12 路",
                "desktop_notification": True,
                "notification_sound": False,
                "advanced_profile": "低干扰巡检",
                "advanced_safe_mode": True,
                "advanced_experimental": False,
            }
        )
        self._sync_widgets_from_state()
        self._status_text = "已应用推荐配置，请确认后保存"
        self._refresh_all_views()

    def _category_for_field(self, field_name: str) -> str:
        """返回字段所属分类。"""

        if field_name in {"language", "auto_start", "minimize_to_tray", "check_updates_on_start"}:
            return "通用"
        if field_name in {"theme_mode", "font_size", "accent_color", "sidebar_width"}:
            return "外观"
        if field_name in {"download_path", "cache_size", "auto_cleanup", "database_location"}:
            return "存储"
        if field_name in {"proxy_address", "network_timeout", "retry_count", "concurrent_connections"}:
            return "网络"
        if field_name in {"desktop_notification", "notification_sound", "dnd_schedule"}:
            return "通知"
        if field_name.startswith("quick_"):
            return "快捷键"
        return "高级"

    def _format_state_value(self, value: object) -> str:
        """格式化状态值。"""

        if isinstance(value, bool):
            return "已开启" if value else "已关闭"
        return str(value)

    def _refresh_all_views(self) -> None:
        """刷新全部视图。"""

        self._refresh_category_header()
        self._refresh_summary_cards()
        self._refresh_status_banner()
        self._refresh_preview_lines()
        self._refresh_change_table()
        self._refresh_shortcut_table()
        self._refresh_footer_summary()

    def _refresh_category_header(self) -> None:
        """刷新分类标题。"""

        meta = CATEGORY_METAS[self._current_category_index]
        if self._current_category_label is not None:
            _call(self._current_category_label, "setText", f"{meta.title} · {meta.subtitle}")
        if self._current_tip_label is not None:
            _call(self._current_tip_label, "setText", meta.tip)

    def _refresh_summary_cards(self) -> None:
        """刷新 KPI。"""

        enabled_count = sum(1 for value in self._draft_state.values() if isinstance(value, bool) and value)
        bool_count = sum(1 for value in self._draft_state.values() if isinstance(value, bool))
        self._summary_cards["enabled"].set_value(f"{enabled_count} / {bool_count}")
        self._summary_cards["enabled"].set_trend("up" if enabled_count >= 6 else "flat", f"{enabled_count} 项开启")

        appearance_label = "舒适" if "舒适" in str(self._draft_state["font_size"]) else "标准"
        self._summary_cards["appearance"].set_value(appearance_label)
        self._summary_cards["appearance"].set_trend("flat", str(self._draft_state["theme_mode"]))

        network_score = 70
        if str(self._draft_state["network_timeout"]) in {"18 秒", "24 秒", "30 秒"}:
            network_score += 8
        if str(self._draft_state["retry_count"]) in {"3 次", "5 次"}:
            network_score += 8
        if str(self._draft_state["concurrent_connections"]) in {"12 路", "16 路", "24 路"}:
            network_score += 6
        self._summary_cards["network"].set_value(f"{network_score} 分")
        self._summary_cards["network"].set_trend("up" if network_score >= 90 else "flat", f"{self._draft_state['concurrent_connections']}")

        safety_score = 58
        if bool(self._draft_state["advanced_safe_mode"]):
            safety_score += 18
        if not bool(self._draft_state["advanced_experimental"]):
            safety_score += 12
        if str(self._draft_state["advanced_keep_backup_days"]) in {"14 天", "30 天", "90 天"}:
            safety_score += 10
        safety_label = "高" if safety_score >= 90 else "中"
        self._summary_cards["safety"].set_value(safety_label)
        self._summary_cards["safety"].set_trend("up" if safety_score >= 90 else "flat", f"{safety_score} 分")

    def _refresh_status_banner(self) -> None:
        """刷新横幅状态。"""

        has_changes = self._draft_state != self._saved_state
        if self._status_badge is not None:
            _call(self._status_badge, "setText", "草稿待保存" if has_changes else "配置已同步")
            self._status_badge.set_tone("warning" if has_changes else "success")
        if self._save_hint_label is not None:
            _call(self._save_hint_label, "setText", self._status_text)
        if self._active_profile_chip is not None:
            self._active_profile_chip.set_text(str(self._draft_state["advanced_profile"]))
        if self._tips_card is not None:
            category = CATEGORY_METAS[self._current_category_index]
            _call(self._tips_card, "set_title", f"当前焦点：{category.title}")
            _call(self._tips_card, "set_description", category.tip)

    def _refresh_preview_lines(self) -> None:
        """刷新右侧预览文案。"""

        preview_values = {
            "theme": f"主题预览：{self._draft_state['theme_mode']} · {self._draft_state['font_size']}",
            "network": f"网络策略：{self._draft_state['network_timeout']} / {self._draft_state['retry_count']} / {self._draft_state['concurrent_connections']}",
            "notify": f"通知策略：{'桌面提醒' if self._draft_state['desktop_notification'] else '静默'} · {'声音开' if self._draft_state['notification_sound'] else '声音关'}",
        }
        for key, text in preview_values.items():
            label = self._preview_lines.get(key)
            if label is not None:
                _call(label, "setText", text)

    def _refresh_change_table(self) -> None:
        """刷新变更表格。"""

        if self._change_table is None:
            return
        rows = [
            (record.changed_at, record.category, record.field_name, record.changed_to, record.operator)
            for record in self._recent_changes
        ]
        self._change_table.set_rows(rows)

    def _refresh_shortcut_table(self) -> None:
        """刷新快捷键表格。"""

        if self._shortcut_table is None:
            return
        rows: list[tuple[str, str, str, str, str]] = []
        for record in self._shortcut_records:
            field_name = self._shortcut_field_name(record)
            rows.append((record.action_name, str(self._draft_state[field_name]), record.area, record.status, record.note))
        self._shortcut_table.set_rows(rows)

    def _refresh_footer_summary(self) -> None:
        """刷新底部提示。"""

        changed_fields = [self._field_label(key) for key, value in self._draft_state.items() if self._saved_state.get(key) != value]
        if self._footer_summary_label is None:
            return
        if not changed_fields:
            _call(self._footer_summary_label, "setText", "当前草稿与已保存配置一致。")
            return
        preview = "、".join(changed_fields[:4])
        if len(changed_fields) > 4:
            preview += f" 等 {len(changed_fields)} 项"
        _call(self._footer_summary_label, "setText", f"待保存变更：{preview}。保存后将写入当前工作区配置快照。")

    def _apply_page_styles(self) -> None:
        """应用页面样式。"""

        colors = _palette()
        primary = _token("brand.primary")
        primary_soft = _rgba(primary, 0.10)
        primary_border = _rgba(primary, 0.20)
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#systemSettingsPage {{
                background-color: {colors.surface_alt};
            }}
            QFrame#systemSettingsCategoryHeader,
            QFrame#systemSettingsFooter,
            QFrame#systemSettingsStatusHost {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#systemSettingsBanner {{
                background-color: {primary_soft};
                border: 1px solid {primary_border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#systemSettingsBanner QLabel,
            QFrame#systemSettingsCategoryHeader QLabel,
            QFrame#systemSettingsFooter QLabel {{
                background: transparent;
            }}
            QLabel#systemSettingsBannerTitle,
            QLabel#systemSettingsCategoryTitle,
            QLabel#systemSettingsFooterTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#systemSettingsBannerText,
            QLabel#systemSettingsCategoryDesc,
            QLabel#systemSettingsFooterText,
            QLabel#systemSettingsPreviewLine,
            QLabel#systemSettingsPlainText {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                line-height: 1.5;
            }}
            QWidget#systemSettingsPage QPushButton {{
                font-family: {_static_token('font.family.chinese')};
            }}
            QWidget#systemSettingsPage QFrame[variant="card"] {{
                background-color: {colors.surface};
            }}
            QWidget#systemSettingsPage QTableView {{
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#systemSettingsPage QFrame#contentSection {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#systemSettingsPage QLineEdit,
            QWidget#systemSettingsPage QComboBox {{
                selection-background-color: {primary};
            }}
            QWidget#systemSettingsPage QWidget#tabBarStrip {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_SM}px {SPACING_SM}px 0 {SPACING_SM}px;
            }}
            QWidget#systemSettingsPage QWidget#tabBarStack {{
                background: transparent;
                border: none;
            }}
            QWidget#systemSettingsPage QPushButton:hover {{
                border-color: {primary_border};
            }}
            QWidget#systemSettingsPage QLabel#pageContainerDescription {{
                color: {colors.text_muted};
            }}
            QWidget#systemSettingsPage QLabel#statusBadge {{
                min-height: {BUTTON_HEIGHT - SPACING_SM}px;
            }}
            QWidget#systemSettingsPage QFrame#systemSettingsFooter {{
                background-color: {primary_soft};
                border-color: {primary_border};
            }}
            """,
        )


__all__ = ["SystemSettingsPage"]
