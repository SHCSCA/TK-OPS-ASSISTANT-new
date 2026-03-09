# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportPrivateUsage=false, reportImplicitOverride=false

from __future__ import annotations

"""下载器页面。"""

from dataclasses import dataclass, replace
from importlib import import_module
from typing import Any

from ....core.types import RouteId
from ...components import (
    DangerButton,
    IconButton,
    PageContainer,
    PrimaryButton,
    SecondaryButton,
    StatusBadge,
    ThemedComboBox,
    ThemedLineEdit,
    ThemedScrollArea,
    ToggleSwitch,
)
from ...components.tags import BadgeTone
from ...components.inputs import (
    BUTTON_HEIGHT,
    RADIUS_LG,
    RADIUS_MD,
    RADIUS_SM,
    SPACING_2XL,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    QLabel,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ..base_page import BasePage


class _FallbackProgressBar(QWidget):
    """无 Qt 环境时的最小进度条实现。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._minimum = 0
        self._maximum = 100
        self._value = 0

    def setRange(self, minimum: int, maximum: int) -> None:
        self._minimum = minimum
        self._maximum = maximum

    def setValue(self, value: int) -> None:
        self._value = max(self._minimum, min(value, self._maximum))

    def setTextVisible(self, _visible: bool) -> None:
        return None


def _resolve_optional_widget(name: str, fallback: type[object]) -> type[object]:
    """动态解析可选 Qt Widget。"""

    try:
        module = import_module("PySide6.QtWidgets")
    except Exception:
        return fallback
    resolved = getattr(module, name, None)
    if isinstance(resolved, type):
        return resolved
    return fallback


QProgressBar: Any = _resolve_optional_widget("QProgressBar", _FallbackProgressBar)


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba 字符串。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


CARD_PADDING = SPACING_2XL
CARD_GAP = SPACING_XL
SIDEBAR_WIDTH = SPACING_2XL * 13
DOWNLOAD_LIST_MIN_HEIGHT = SPACING_2XL * 19
THUMBNAIL_SIZE = SPACING_2XL * 3
ACTION_MIN_WIDTH = SPACING_2XL * 3
PROGRESS_HEIGHT = SPACING_SM
PROMO_MIN_HEIGHT = SPACING_2XL * 8
HEADER_ICON_SIZE = SPACING_2XL * 2
DESKTOP_PAGE_MAX_WIDTH = 1760


@dataclass(frozen=True)
class DownloadRecord:
    """下载任务展示数据。"""

    download_id: str
    title: str
    source: str
    status: str
    downloaded_mb: float
    total_mb: float
    speed_mbps: float
    eta_text: str
    quality: str
    format_label: str


class DownloaderPage(BasePage):
    """系统模块下的下载器页面。"""

    default_route_id: RouteId = RouteId("download_manager")
    default_display_name: str = "下载器"
    default_icon_name: str = "download"

    def setup_ui(self) -> None:
        """构建下载器页面，不使用基类默认占位布局。"""

        self._quality_options = ("4K / 2160p", "1080p FHD", "720p HD", "MP3 320kbps")
        self._save_paths = (
            "C:/Downloads/VideoDownloader/",
            "D:/TK-OPS/素材下载/",
            "E:/运营共享盘/短视频缓存/",
        )
        self._demo_links = (
            "https://www.tiktok.com/@ops_lab/video/7365001024001",
            "https://www.youtube.com/watch?v=tkops-demo-2026",
            "https://www.instagram.com/reel/C7TkOpsStudio/",
        )
        self._demo_cursor = 0
        self._save_path_index = 0
        self._selected_quality = self._quality_options[0]
        self._downloads = self._mock_downloads()
        self._next_download_index = len(self._downloads) + 1
        self._quality_buttons: dict[str, QPushButton] = {}

        _call(self, "setObjectName", "downloaderPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        self._page_container = PageContainer(
            title=self.display_name,
            description="围绕 TikTok / YouTube / Instagram 素材解析、批量下载与路径管理构建的高保真下载面板。",
            max_width=DESKTOP_PAGE_MAX_WIDTH,
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._history_button = IconButton("↻", "推进下载队列", self._page_container)
        self._restore_button = IconButton("⚙", "恢复推荐设置", self._page_container)
        self._page_container.add_action(self._history_button)
        self._page_container.add_action(self._restore_button)

        self._page_container.add_widget(self._build_input_card())
        self._page_container.add_widget(self._build_main_content())
        self._page_container.add_widget(self._build_footer_bar())

        _connect(getattr(self._history_button, "clicked", None), self._handle_advance_queue)
        _connect(getattr(self._restore_button, "clicked", None), self._handle_restore_defaults)
        _connect(getattr(self._url_input.line_edit, "returnPressed", None), self._handle_parse_link)
        _connect(getattr(self._parse_button, "clicked", None), self._handle_parse_link)
        _connect(getattr(self._demo_button, "clicked", None), self._handle_fill_demo_link)
        _connect(getattr(self._stop_all_button, "clicked", None), self._handle_stop_all)
        _connect(getattr(self._start_all_button, "clicked", None), self._handle_start_all)
        _connect(getattr(self._clear_completed_button, "clicked", None), self._handle_clear_completed)
        _connect(getattr(self._format_combo.combo_box, "currentTextChanged", None), self._refresh_summary)
        _connect(getattr(self._parallel_combo.combo_box, "currentTextChanged", None), self._refresh_summary)
        _connect(self._watermark_toggle.toggled, self._refresh_summary)
        _connect(self._auto_name_toggle.toggled, self._refresh_summary)
        _connect(self._proxy_toggle.toggled, self._refresh_summary)
        _connect(getattr(self._change_path_button, "clicked", None), self._handle_change_path)
        _connect(getattr(self._upgrade_button, "clicked", None), self._handle_upgrade_click)

        self._refresh_quality_buttons()
        self._render_downloads()
        self._refresh_summary()

    def _build_input_card(self) -> QWidget:
        """顶部粘贴链接与主操作区域。"""

        card = self._create_card("downloaderHeroCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        layout.setSpacing(CARD_GAP)

        title = QLabel("粘贴链接开始下载", card)
        _call(title, "setObjectName", "downloaderSectionTitle")
        layout.addWidget(title)

        input_row = QWidget(card)
        input_layout = QHBoxLayout(input_row)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(SPACING_XL)

        self._url_input = ThemedLineEdit(
            label="视频链接",
            placeholder="粘贴 TikTok, YouTube, Instagram 链接...",
            helper_text="支持 TikTok / YouTube / Instagram 链接，回车或点击按钮即可加入队列。",
            parent=input_row,
        )
        _call(self._url_input.line_edit, "setMinimumHeight", BUTTON_HEIGHT + SPACING_XL)

        button_column = QWidget(input_row)
        button_layout = QVBoxLayout(button_column)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(SPACING_MD)

        self._parse_button = PrimaryButton("开始解析", button_column, icon_text="⚡")
        self._demo_button = SecondaryButton("填入示例", button_column, icon_text="⎘")
        self._stop_all_button = DangerButton("停止全部", button_column, icon_text="■")

        button_layout.addWidget(self._parse_button)
        button_layout.addWidget(self._demo_button)
        button_layout.addWidget(self._stop_all_button)
        button_layout.addStretch(1)

        input_layout.addWidget(self._url_input, 1)
        input_layout.addWidget(button_column)
        layout.addWidget(input_row)

        badge_row = QWidget(card)
        badge_layout = QHBoxLayout(badge_row)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(SPACING_MD)
        self._clipboard_badge = StatusBadge("自动检测剪贴板", tone="info", parent=badge_row)
        self._resolution_badge = StatusBadge("支持 4K 解析", tone="success", parent=badge_row)
        self._quality_badge = StatusBadge("默认画质 · 4K / 2160p", tone="brand", parent=badge_row)
        badge_layout.addWidget(self._clipboard_badge)
        badge_layout.addWidget(self._resolution_badge)
        badge_layout.addWidget(self._quality_badge)
        badge_layout.addStretch(1)
        layout.addWidget(badge_row)
        return card

    def _build_main_content(self) -> QWidget:
        """中部下载列表与设置侧栏。"""

        content = QWidget(self)
        _call(content, "setObjectName", "downloaderMainContent")
        layout = QHBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        left_column = self._build_download_list_card()
        right_column = self._build_settings_sidebar()
        _call(right_column, "setMinimumWidth", SIDEBAR_WIDTH)

        layout.addWidget(left_column, 7)
        layout.addWidget(right_column, 4)
        return content

    def _build_download_list_card(self) -> QWidget:
        """下载任务列表区域。"""

        card = self._create_card("downloaderListCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget(card)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, SPACING_XL)
        header_layout.setSpacing(SPACING_XL)

        header_text = QWidget(header)
        header_text_layout = QVBoxLayout(header_text)
        header_text_layout.setContentsMargins(0, 0, 0, 0)
        header_text_layout.setSpacing(SPACING_XS)
        self._download_count_label = QLabel("下载列表 (0)", header_text)
        _call(self._download_count_label, "setObjectName", "downloaderSectionTitle")
        self._download_meta_label = QLabel("准备就绪", header_text)
        _call(self._download_meta_label, "setObjectName", "downloaderMutedLabel")
        header_text_layout.addWidget(self._download_count_label)
        header_text_layout.addWidget(self._download_meta_label)

        actions = QWidget(header)
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(SPACING_MD)
        self._start_all_button = SecondaryButton("全部开始", actions, icon_text="▶")
        self._clear_completed_button = DangerButton("清除已完成", actions, icon_text="✕")
        actions_layout.addWidget(self._start_all_button)
        actions_layout.addWidget(self._clear_completed_button)

        header_layout.addWidget(header_text, 1)
        header_layout.addWidget(actions)
        layout.addWidget(header)

        divider = QFrame(card)
        _call(divider, "setObjectName", "downloaderDivider")
        _call(divider, "setFixedHeight", 1)
        layout.addWidget(divider)

        self._downloads_scroll = ThemedScrollArea(card)
        _call(self._downloads_scroll, "setMinimumHeight", DOWNLOAD_LIST_MIN_HEIGHT)
        self._downloads_scroll.content_layout.setContentsMargins(CARD_PADDING, SPACING_XL, CARD_PADDING, CARD_PADDING)
        self._downloads_scroll.content_layout.setSpacing(SPACING_LG)
        layout.addWidget(self._downloads_scroll)
        return card

    def _build_settings_sidebar(self) -> QWidget:
        """右侧设置栏。"""

        sidebar = QWidget(self)
        _call(sidebar, "setObjectName", "downloaderSidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        settings_card = self._create_card("downloaderSettingsCard")
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        settings_layout.setSpacing(SPACING_XL)

        settings_header = QWidget(settings_card)
        settings_header_layout = QHBoxLayout(settings_header)
        settings_header_layout.setContentsMargins(0, 0, 0, 0)
        settings_header_layout.setSpacing(SPACING_MD)
        settings_icon = QLabel("✣", settings_header)
        _call(settings_icon, "setObjectName", "downloaderAccentIcon")
        settings_title = QLabel("下载设置", settings_header)
        _call(settings_title, "setObjectName", "downloaderSectionTitle")
        settings_header_layout.addWidget(settings_icon)
        settings_header_layout.addWidget(settings_title)
        settings_header_layout.addStretch(1)
        settings_layout.addWidget(settings_header)

        quality_group = QWidget(settings_card)
        quality_layout = QVBoxLayout(quality_group)
        quality_layout.setContentsMargins(0, 0, 0, 0)
        quality_layout.setSpacing(SPACING_MD)
        quality_label = QLabel("默认画质", quality_group)
        _call(quality_label, "setObjectName", "downloaderMutedLabel")
        quality_layout.addWidget(quality_label)

        for row_options in (self._quality_options[:2], self._quality_options[2:]):
            row = QWidget(quality_group)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(SPACING_MD)
            for option in row_options:
                button = QPushButton(option, row)
                _call(button, "setObjectName", "downloaderQualityButton")
                _call(button, "setMinimumHeight", BUTTON_HEIGHT + SPACING_MD)
                _connect(getattr(button, "clicked", None), lambda checked=False, value=option: self._handle_select_quality(value))
                self._quality_buttons[option] = button
                row_layout.addWidget(button, 1)
            quality_layout.addWidget(row)
        settings_layout.addWidget(quality_group)

        self._watermark_toggle = self._build_toggle_row(
            settings_layout,
            "去除水印",
            "自动移除 TikTok / IG 水印",
            checked=True,
        )
        self._auto_name_toggle = self._build_toggle_row(
            settings_layout,
            "自动命名",
            "使用视频标题作为文件名",
            checked=True,
        )
        self._proxy_toggle = self._build_toggle_row(
            settings_layout,
            "代理下载",
            "提升海外平台下载速度",
            checked=False,
        )

        self._format_combo = ThemedComboBox("默认封装", ("MP4 视频", "MP3 音频", "仅封面图"), settings_card)
        _call(self._format_combo.combo_box, "setCurrentText", "MP4 视频")
        self._parallel_combo = ThemedComboBox("并发任务", ("1 个并发任务", "3 个并发任务", "5 个并发任务"), settings_card)
        _call(self._parallel_combo.combo_box, "setCurrentText", "3 个并发任务")
        settings_layout.addWidget(self._format_combo)
        settings_layout.addWidget(self._parallel_combo)

        path_card = self._create_card("downloaderPathCard")
        path_layout = QVBoxLayout(path_card)
        path_layout.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        path_layout.setSpacing(SPACING_XL)

        path_title = QLabel("保存路径", path_card)
        _call(path_title, "setObjectName", "downloaderSectionTitle")
        path_layout.addWidget(path_title)

        path_row = QFrame(path_card)
        _call(path_row, "setObjectName", "downloaderPathValue")
        path_row_layout = QHBoxLayout(path_row)
        path_row_layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        path_row_layout.setSpacing(SPACING_MD)
        self._save_path_label = QLabel("", path_row)
        _call(self._save_path_label, "setObjectName", "downloaderPathLabel")
        _call(self._save_path_label, "setWordWrap", True)
        self._change_path_button = SecondaryButton("更改", path_row)
        path_row_layout.addWidget(self._save_path_label, 1)
        path_row_layout.addWidget(self._change_path_button)
        path_layout.addWidget(path_row)

        promo_card = self._create_card("downloaderPromoCard")
        _call(promo_card, "setMinimumHeight", PROMO_MIN_HEIGHT)
        promo_layout = QVBoxLayout(promo_card)
        promo_layout.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        promo_layout.setSpacing(SPACING_LG)
        promo_layout.addStretch(1)
        promo_title = QLabel("获取专业版", promo_card)
        _call(promo_title, "setObjectName", "downloaderPromoTitle")
        promo_copy = QLabel("解锁批量下载、智能命名与 8K 画质解析能力。", promo_card)
        _call(promo_copy, "setObjectName", "downloaderPromoCopy")
        _call(promo_copy, "setWordWrap", True)
        self._upgrade_button = QPushButton("立即升级", promo_card)
        _call(self._upgrade_button, "setObjectName", "downloaderPromoButton")
        _call(self._upgrade_button, "setMinimumHeight", BUTTON_HEIGHT + SPACING_MD)
        promo_layout.addWidget(promo_title)
        promo_layout.addWidget(promo_copy)
        promo_layout.addWidget(self._upgrade_button)

        layout.addWidget(settings_card)
        layout.addWidget(path_card)
        layout.addWidget(promo_card)
        return sidebar

    def _build_footer_bar(self) -> QWidget:
        """底部状态栏。"""

        footer = self._create_card("downloaderFooterBar")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(SPACING_XL, SPACING_MD, SPACING_XL, SPACING_MD)
        layout.setSpacing(SPACING_XL)

        left_group = QWidget(footer)
        left_layout = QHBoxLayout(left_group)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(SPACING_XL)
        self._server_badge = StatusBadge("服务器 · 香港-高速", tone="success", parent=left_group)
        self._traffic_label = QLabel("当前流量: 0.0 MB/s", left_group)
        _call(self._traffic_label, "setObjectName", "downloaderFooterMeta")
        left_layout.addWidget(self._server_badge)
        left_layout.addWidget(self._traffic_label)

        right_group = QWidget(footer)
        right_layout = QHBoxLayout(right_group)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(SPACING_XL)
        self._storage_label = QLabel("剩余空间: 124.5 GB", right_group)
        self._version_label = QLabel("V 2.1.0", right_group)
        _call(self._storage_label, "setObjectName", "downloaderFooterMeta")
        _call(self._version_label, "setObjectName", "downloaderVersion")
        right_layout.addWidget(self._storage_label)
        right_layout.addWidget(self._version_label)

        layout.addWidget(left_group)
        layout.addStretch(1)
        layout.addWidget(right_group)
        return footer

    def _build_toggle_row(self, parent_layout: QVBoxLayout, title: str, caption: str, checked: bool) -> ToggleSwitch:
        """构建设置开关行。"""

        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)

        text_column = QWidget(row)
        text_layout = QVBoxLayout(text_column)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(SPACING_XS)
        title_label = QLabel(title, text_column)
        caption_label = QLabel(caption, text_column)
        _call(title_label, "setObjectName", "downloaderToggleTitle")
        _call(caption_label, "setObjectName", "downloaderToggleCaption")
        _call(caption_label, "setWordWrap", True)
        text_layout.addWidget(title_label)
        text_layout.addWidget(caption_label)

        toggle = ToggleSwitch(checked=checked, parent=row)
        layout.addWidget(text_column, 1)
        layout.addWidget(toggle)
        parent_layout.addWidget(row)
        return toggle

    def _create_card(self, object_name: str) -> QFrame:
        """创建统一视觉卡片。"""

        card = QFrame(self)
        _call(card, "setObjectName", object_name)
        return card

    def _render_downloads(self) -> None:
        """根据当前状态重绘下载列表。"""

        self._clear_layout_items(self._downloads_scroll.content_layout)
        if not self._downloads:
            empty_label = QLabel("当前没有下载任务，贴入链接后会出现在这里。", self._downloads_scroll)
            _call(empty_label, "setObjectName", "downloaderEmptyState")
            self._downloads_scroll.add_widget(empty_label)
            self._downloads_scroll.content_layout.addStretch(1)
            return

        for record in self._downloads:
            self._downloads_scroll.add_widget(self._build_download_item(record))
        self._downloads_scroll.content_layout.addStretch(1)

    def _build_download_item(self, record: DownloadRecord) -> QWidget:
        """构建单条下载记录卡片。"""

        card = QFrame(self._downloads_scroll)
        _call(card, "setObjectName", "downloaderItemCard")
        self._apply_download_card_styles(card, record)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        thumbnail = QFrame(card)
        _call(thumbnail, "setObjectName", "downloaderThumbnail")
        _call(thumbnail, "setFixedSize", THUMBNAIL_SIZE, THUMBNAIL_SIZE)
        thumbnail_layout = QVBoxLayout(thumbnail)
        thumbnail_layout.setContentsMargins(0, 0, 0, 0)
        thumbnail_layout.setSpacing(0)
        play_label = QLabel("▶", thumbnail)
        _call(play_label, "setObjectName", "downloaderThumbnailIcon")
        thumbnail_layout.addStretch(1)
        thumbnail_layout.addWidget(play_label)
        thumbnail_layout.addStretch(1)
        layout.addWidget(thumbnail)

        content = QWidget(card)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(SPACING_SM)

        title_row = QWidget(content)
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)
        title_row_layout.setSpacing(SPACING_MD)
        title_label = QLabel(record.title, title_row)
        _call(title_label, "setObjectName", "downloaderItemTitle")
        _call(title_label, "setWordWrap", True)
        status_badge = StatusBadge(self._status_label(record.status), tone=self._status_tone(record.status), parent=title_row)
        speed_label = QLabel(self._speed_label(record), title_row)
        _call(speed_label, "setObjectName", "downloaderSpeedLabel")
        title_row_layout.addWidget(title_label, 1)
        title_row_layout.addWidget(status_badge)
        title_row_layout.addWidget(speed_label)

        meta_label = QLabel(f"{record.source} · {record.format_label} · {record.quality}", content)
        _call(meta_label, "setObjectName", "downloaderMutedLabel")

        progress_bar = QProgressBar(content)
        _call(progress_bar, "setObjectName", "downloaderLinearProgress")
        _call(progress_bar, "setRange", 0, 100)
        _call(progress_bar, "setTextVisible", False)
        _call(progress_bar, "setValue", self._progress_value(record))
        _call(progress_bar, "setMinimumHeight", PROGRESS_HEIGHT)
        _call(progress_bar, "setStyleSheet", self._progress_style(record.status))

        footer_row = QWidget(content)
        footer_row_layout = QHBoxLayout(footer_row)
        footer_row_layout.setContentsMargins(0, 0, 0, 0)
        footer_row_layout.setSpacing(SPACING_MD)
        size_label = QLabel(self._size_progress_label(record), footer_row)
        eta_label = QLabel(record.eta_text, footer_row)
        _call(size_label, "setObjectName", "downloaderMetaLabel")
        _call(eta_label, "setObjectName", "downloaderMetaLabel")
        footer_row_layout.addWidget(size_label)
        footer_row_layout.addStretch(1)
        footer_row_layout.addWidget(eta_label)

        content_layout.addWidget(title_row)
        content_layout.addWidget(meta_label)
        content_layout.addWidget(progress_bar)
        content_layout.addWidget(footer_row)
        layout.addWidget(content, 1)

        actions = QWidget(card)
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(SPACING_SM)
        primary_action = QPushButton(self._primary_action_label(record), actions)
        remove_action = QPushButton("移除", actions)
        _call(primary_action, "setObjectName", "downloaderMiniAction")
        _call(remove_action, "setObjectName", "downloaderMiniDanger")
        _call(primary_action, "setMinimumWidth", ACTION_MIN_WIDTH)
        _call(remove_action, "setMinimumWidth", ACTION_MIN_WIDTH)
        _connect(getattr(primary_action, "clicked", None), lambda checked=False, download_id=record.download_id: self._handle_primary_action(download_id))
        _connect(getattr(remove_action, "clicked", None), lambda checked=False, download_id=record.download_id: self._handle_remove_download(download_id))
        actions_layout.addWidget(primary_action)
        actions_layout.addWidget(remove_action)
        layout.addWidget(actions)
        return card

    def _apply_page_styles(self) -> None:
        """应用页面级样式。"""

        colors = _palette()
        brand = _token("brand.primary")
        brand_soft = _rgba(brand, 0.10)
        brand_line = _rgba(brand, 0.18)
        panel_soft = _rgba(_token("status.info"), 0.08)
        panel_border = _rgba(_token("status.info"), 0.18)
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#downloaderPage {{
                background-color: {colors.surface_alt};
            }}
            QWidget#downloaderPage QLabel,
            QWidget#downloaderPage QPushButton {{
                font-family: {_static_token('font.family.chinese')};
            }}
            QWidget#downloaderMainContent,
            QWidget#downloaderSidebar {{
                background: transparent;
                border: none;
            }}
            QFrame#downloaderListCard,
            QFrame#downloaderSettingsCard,
            QFrame#downloaderPathCard,
            QFrame#downloaderFooterBar {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#downloaderHeroCard {{
                background-color: {brand_soft};
                border: 1px solid {brand_line};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#downloaderPage QFrame#downloaderListCard,
            QWidget#downloaderPage QFrame#downloaderSettingsCard,
            QWidget#downloaderPage QFrame#downloaderPathCard {{
                min-height: {SPACING_2XL * 6}px;
            }}
            QFrame#downloaderFooterBar {{
                background-color: {panel_soft};
                border-color: {panel_border};
            }}
            QFrame#downloaderPromoCard {{
                background-color: {_rgba(brand, 0.16)};
                border: 1px solid {_rgba(brand, 0.24)};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#downloaderSectionTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#downloaderMutedLabel,
            QLabel#downloaderMetaLabel,
            QLabel#downloaderFooterMeta,
            QLabel#downloaderToggleCaption,
            QLabel#downloaderPathLabel,
            QLabel#downloaderPromoCopy,
            QLabel#downloaderEmptyState {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                background: transparent;
            }}
            QLabel#downloaderItemTitle,
            QLabel#downloaderToggleTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.semibold')};
                background: transparent;
            }}
            QLabel#downloaderSpeedLabel,
            QLabel#downloaderVersion,
            QLabel#downloaderAccentIcon {{
                color: {brand};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#downloaderPromoTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.xxl')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QFrame#downloaderPathValue {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_MD}px;
            }}
            QFrame#downloaderDivider {{
                background-color: {colors.border};
                border: none;
            }}
            QFrame#downloaderThumbnail {{
                background-color: {_rgba(brand, 0.12)};
                border: 1px solid {_rgba(brand, 0.12)};
                border-radius: {RADIUS_MD}px;
            }}
            QLabel#downloaderThumbnailIcon {{
                color: {_rgba(colors.text, 0.50)};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QPushButton#downloaderQualityButton {{
                background-color: transparent;
                color: {colors.text};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_MD}px {SPACING_LG}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.medium')};
            }}
            QPushButton#downloaderQualityButton:hover {{
                border-color: {brand};
                background-color: {brand_soft};
            }}
            QPushButton#downloaderMiniAction {{
                background-color: {brand_soft};
                color: {colors.text};
                border: 1px solid {brand_line};
                border-radius: {RADIUS_SM}px;
                padding: {SPACING_SM}px {SPACING_LG}px;
                min-height: {BUTTON_HEIGHT}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QPushButton#downloaderMiniAction:hover {{
                border-color: {brand};
                background-color: {_rgba(brand, 0.16)};
            }}
            QPushButton#downloaderMiniDanger {{
                background-color: {_rgba(_token('status.error'), 0.08)};
                color: {_token('status.error')};
                border: 1px solid {_rgba(_token('status.error'), 0.18)};
                border-radius: {RADIUS_SM}px;
                padding: {SPACING_SM}px {SPACING_LG}px;
                min-height: {BUTTON_HEIGHT}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QPushButton#downloaderMiniDanger:hover {{
                background-color: {_rgba(_token('status.error'), 0.14)};
                border-color: {_token('status.error')};
            }}
            QPushButton#downloaderPromoButton {{
                background-color: {colors.surface_alt};
                color: {brand};
                border: 1px solid {_rgba(colors.text, 0.10)};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_MD}px {SPACING_XL}px;
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QPushButton#downloaderPromoButton:hover {{
                background-color: {colors.text};
                color: {colors.text_inverse};
                border-color: {colors.text};
            }}
            """,
        )

    def _apply_download_card_styles(self, card: QFrame, record: DownloadRecord) -> None:
        """为任务卡片按状态应用视觉样式。"""

        colors = _palette()
        state_colors = {
            "downloading": (_rgba(_token("brand.primary"), 0.05), _rgba(_token("brand.primary"), 0.18)),
            "paused": (colors.surface_alt, colors.border),
            "queued": (_rgba(_token("status.info"), 0.06), _rgba(_token("status.info"), 0.16)),
            "completed": (_rgba(_token("status.success"), 0.06), _rgba(_token("status.success"), 0.16)),
            "failed": (_rgba(_token("status.error"), 0.06), _rgba(_token("status.error"), 0.16)),
        }
        background, border = state_colors.get(record.status, (colors.surface, colors.border))
        opacity = 0.74 if record.status == "paused" else 1.0
        _call(
            card,
            "setStyleSheet",
            f"""
            QFrame#downloaderItemCard {{
                background-color: {background};
                border: 1px solid {border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#downloaderItemCard QLabel {{
                background: transparent;
                color: {colors.text};
            }}
            QFrame#downloaderItemCard {{
                opacity: {opacity:.2f};
            }}
            """,
        )

    def _progress_style(self, status: str) -> str:
        """返回线性进度条样式。"""

        colors = _palette()
        chunk_color = {
            "downloading": _token("brand.primary"),
            "paused": colors.border_strong,
            "queued": _token("status.info"),
            "completed": _token("status.success"),
            "failed": _token("status.error"),
        }.get(status, _token("brand.primary"))
        return f"""
            QProgressBar#downloaderLinearProgress {{
                background-color: {colors.border};
                border: none;
                border-radius: {PROGRESS_HEIGHT // 2}px;
            }}
            QProgressBar#downloaderLinearProgress::chunk {{
                background-color: {chunk_color};
                border-radius: {PROGRESS_HEIGHT // 2}px;
            }}
        """

    def _refresh_quality_buttons(self) -> None:
        """刷新画质按钮的选中态。"""

        colors = _palette()
        for option, button in self._quality_buttons.items():
            selected = option == self._selected_quality
            border_color = _token("brand.primary") if selected else colors.border
            background = _rgba(_token("brand.primary"), 0.10) if selected else "transparent"
            text_color = _token("brand.primary") if selected else colors.text
            weight = _static_token("font.weight.bold") if selected else _static_token("font.weight.medium")
            _call(
                button,
                "setStyleSheet",
                f"""
                QPushButton#downloaderQualityButton {{
                    background-color: {background};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-radius: {RADIUS_MD}px;
                    padding: {SPACING_MD}px {SPACING_LG}px;
                    font-size: {_static_token('font.size.sm')};
                    font-weight: {weight};
                }}
                QPushButton#downloaderQualityButton:hover {{
                    border-color: {_token('brand.primary')};
                    background-color: {_rgba(_token('brand.primary'), 0.14)};
                }}
                """,
            )

    def _refresh_summary(self, *_args: object) -> None:
        """刷新顶部、列表与底部摘要。"""

        active_count = sum(1 for item in self._downloads if item.status == "downloading")
        completed_count = sum(1 for item in self._downloads if item.status == "completed")
        waiting_count = sum(1 for item in self._downloads if item.status in {"queued", "paused", "failed"})
        traffic = sum(item.speed_mbps for item in self._downloads if item.status == "downloading")
        occupied_space = sum(item.downloaded_mb for item in self._downloads) / 1024
        free_space = max(48.0, 124.5 - occupied_space)

        _call(self._download_count_label, "setText", f"下载列表 ({len(self._downloads)})")
        _call(
            self._download_meta_label,
            "setText",
            f"{active_count} 个任务正在传输，{waiting_count} 个待处理，{completed_count} 个已完成。",
        )
        _call(self._quality_badge, "setText", f"默认画质 · {self._selected_quality}")
        _call(self._save_path_label, "setText", self._save_paths[self._save_path_index])
        _call(self._traffic_label, "setText", f"当前流量: {traffic:.1f} MB/s")
        _call(self._storage_label, "setText", f"剩余空间: {free_space:.1f} GB")

        if self._proxy_toggle.isChecked():
            self._server_badge.setText("服务器 · 香港-代理加速")
            self._server_badge.set_tone("brand")
        elif active_count:
            self._server_badge.setText("服务器 · 香港-高速")
            self._server_badge.set_tone("success")
        else:
            self._server_badge.setText("服务器 · 就绪待命")
            self._server_badge.set_tone("info")

    def _handle_select_quality(self, quality: str) -> None:
        """切换默认画质。"""

        self._selected_quality = quality
        self._refresh_quality_buttons()
        self._refresh_summary()

    def _handle_fill_demo_link(self) -> None:
        """填入示例链接。"""

        link = self._demo_links[self._demo_cursor % len(self._demo_links)]
        self._demo_cursor += 1
        self._url_input.clear_error()
        self._url_input.setText(link)
        self._url_input.set_helper_text("已填入演示链接，可直接回车或点击“开始解析”加入队列。")

    def _handle_parse_link(self) -> None:
        """将当前链接转为新的 mock 下载任务。"""

        raw_url = self._url_input.text().strip()
        if not raw_url:
            self._url_input.set_error("请先粘贴要下载的链接。")
            return

        if not raw_url.startswith(("http://", "https://")):
            self._url_input.set_error("链接格式不正确，请输入以 http:// 或 https:// 开头的地址。")
            return

        self._url_input.clear_error()
        title, source = self._resolve_url_meta(raw_url)
        total_mb = (SPACING_2XL * 1.4) + ((self._next_download_index % 5) * SPACING_LG) + 18.0
        new_record = DownloadRecord(
            download_id=f"DL-{self._next_download_index:04d}",
            title=title,
            source=source,
            status="queued",
            downloaded_mb=0.0,
            total_mb=round(total_mb, 1),
            speed_mbps=0.0,
            eta_text="等待解析",
            quality=self._selected_quality,
            format_label=self._format_combo.current_text(),
        )
        self._next_download_index += 1
        self._downloads.insert(0, new_record)
        self._url_input.setText("")
        self._url_input.set_helper_text(f"已加入 {title}，正在准备下载参数。")
        self._replace_download(self._advance_record(new_record, auto_start=True))
        self._render_downloads()
        self._refresh_summary()

    def _handle_stop_all(self) -> None:
        """暂停所有进行中的下载。"""

        self._downloads = [
            replace(item, status="paused", speed_mbps=0.0, eta_text="暂停中") if item.status == "downloading" else item
            for item in self._downloads
        ]
        self._url_input.clear_error()
        self._url_input.set_helper_text("已暂停所有进行中的任务，可随时重新开始。")
        self._render_downloads()
        self._refresh_summary()

    def _handle_start_all(self) -> None:
        """启动所有待处理任务。"""

        self._downloads = [self._advance_record(item, auto_start=True) if item.status in {"queued", "paused", "failed"} else item for item in self._downloads]
        self._render_downloads()
        self._refresh_summary()

    def _handle_clear_completed(self) -> None:
        """清空已完成任务。"""

        self._downloads = [item for item in self._downloads if item.status != "completed"]
        self._render_downloads()
        self._refresh_summary()

    def _handle_primary_action(self, download_id: str) -> None:
        """执行单条任务主操作。"""

        record = self._download_by_id(download_id)
        if record is None:
            return

        if record.status == "downloading":
            updated = replace(record, status="paused", speed_mbps=0.0, eta_text="暂停中")
        elif record.status in {"paused", "queued", "failed"}:
            updated = self._advance_record(record, auto_start=True)
        else:
            updated = record
            self._url_input.clear_error()
            self._url_input.set_helper_text(f"已定位 {record.title} 的保存目录：{self._save_paths[self._save_path_index]}")

        self._replace_download(updated)
        self._render_downloads()
        self._refresh_summary()

    def _handle_remove_download(self, download_id: str) -> None:
        """移除单条下载记录。"""

        self._downloads = [item for item in self._downloads if item.download_id != download_id]
        self._render_downloads()
        self._refresh_summary()

    def _handle_advance_queue(self) -> None:
        """推进当前下载队列进度。"""

        self._downloads = [self._advance_record(item) for item in self._downloads]
        self._render_downloads()
        self._refresh_summary()

    def _handle_restore_defaults(self) -> None:
        """恢复推荐设置。"""

        self._selected_quality = self._quality_options[0]
        self._save_path_index = 0
        self._watermark_toggle.setChecked(True)
        self._auto_name_toggle.setChecked(True)
        self._proxy_toggle.setChecked(False)
        _call(self._format_combo.combo_box, "setCurrentText", "MP4 视频")
        _call(self._parallel_combo.combo_box, "setCurrentText", "3 个并发任务")
        self._refresh_quality_buttons()
        self._refresh_summary()

    def _handle_change_path(self) -> None:
        """轮换演示保存路径。"""

        self._save_path_index = (self._save_path_index + 1) % len(self._save_paths)
        self._refresh_summary()

    def _handle_upgrade_click(self) -> None:
        """模拟升级操作反馈。"""

        self._url_input.clear_error()
        self._url_input.set_helper_text("专业版特性已预热：批量下载、8K 解析与更高并发能力。")

    def _advance_record(self, record: DownloadRecord, auto_start: bool = False) -> DownloadRecord:
        """推进单条记录的演示状态。"""

        if record.status == "completed":
            return record
        if record.status == "paused" and not auto_start:
            return record
        if record.status == "failed" and not auto_start:
            return record

        if record.status in {"queued", "paused", "failed"}:
            base_speed = 1.2 + ((self._record_order(record) % 4) * 0.8)
            next_downloaded = min(record.total_mb, max(record.downloaded_mb, record.total_mb * 0.18))
            remain_mb = max(0.0, record.total_mb - next_downloaded)
            eta = "已完成" if remain_mb <= 0 else f"预计剩余 {max(1, int(remain_mb / max(base_speed, 0.8)))}s"
            status = "completed" if remain_mb <= 0 else "downloading"
            return replace(
                record,
                status=status,
                downloaded_mb=record.total_mb if status == "completed" else round(next_downloaded, 1),
                speed_mbps=0.0 if status == "completed" else round(base_speed, 1),
                eta_text=eta,
            )

        delta = max(record.total_mb * 0.16, 4.0)
        next_downloaded = min(record.total_mb, record.downloaded_mb + delta)
        speed = round(max(1.0, record.speed_mbps + 0.4), 1)
        if next_downloaded >= record.total_mb:
            return replace(record, status="completed", downloaded_mb=record.total_mb, speed_mbps=0.0, eta_text="已完成")
        remain_mb = max(0.0, record.total_mb - next_downloaded)
        eta = f"预计剩余 {max(1, int(remain_mb / max(speed, 0.8)))}s"
        return replace(record, status="downloading", downloaded_mb=round(next_downloaded, 1), speed_mbps=speed, eta_text=eta)

    def _record_order(self, record: DownloadRecord) -> int:
        """返回记录序号，用于生成稳定的 mock 波动。"""

        try:
            return int(record.download_id.split("-")[-1])
        except ValueError:
            return 1

    def _replace_download(self, updated: DownloadRecord) -> None:
        """替换列表中的指定记录。"""

        self._downloads = [updated if item.download_id == updated.download_id else item for item in self._downloads]

    def _download_by_id(self, download_id: str) -> DownloadRecord | None:
        """按 ID 获取下载记录。"""

        return next((item for item in self._downloads if item.download_id == download_id), None)

    def _resolve_url_meta(self, url: str) -> tuple[str, str]:
        """根据链接生成展示标题与来源。"""

        compact = url.replace("https://", "").replace("http://", "").strip("/")
        domain = compact.split("/")[0] if compact else "media"
        tail = compact.split("/")[-1] if compact else "clip"
        title_seed = tail.replace("-", " ").replace("_", " ").strip()
        readable = title_seed if len(title_seed) >= 4 else f"{domain} 热门片段"
        title = f"{readable.title()} 下载任务"
        source = domain.split(".")[1].upper() if "." in domain else domain.upper()
        return title[:54], source[:18]

    def _progress_value(self, record: DownloadRecord) -> int:
        """返回 0-100 的进度值。"""

        if record.total_mb <= 0:
            return 0
        return max(0, min(100, int((record.downloaded_mb / record.total_mb) * 100)))

    def _size_progress_label(self, record: DownloadRecord) -> str:
        """返回已下载/总大小文案。"""

        return f"{record.downloaded_mb:.1f} MB / {record.total_mb:.1f} MB"

    def _speed_label(self, record: DownloadRecord) -> str:
        """返回速度标签。"""

        if record.status == "downloading":
            return f"{record.speed_mbps:.1f} MB/s"
        if record.status == "completed":
            return "已完成"
        if record.status == "paused":
            return "已暂停"
        if record.status == "failed":
            return "待重试"
        return "等待中"

    @staticmethod
    def _status_tone(status: str) -> BadgeTone:
        """映射任务状态到徽标色。"""

        mapping: dict[str, BadgeTone] = {
            "downloading": "brand",
            "paused": "warning",
            "queued": "info",
            "completed": "success",
            "failed": "error",
        }
        return mapping.get(status, "neutral")

    @staticmethod
    def _status_label(status: str) -> str:
        """返回中文状态文案。"""

        return {
            "downloading": "下载中",
            "paused": "已暂停",
            "queued": "等待中",
            "completed": "已完成",
            "failed": "解析失败",
        }.get(status, "待处理")

    @staticmethod
    def _primary_action_label(record: DownloadRecord) -> str:
        """返回卡片主操作按钮文案。"""

        if record.status == "downloading":
            return "暂停"
        if record.status in {"queued", "paused"}:
            return "开始"
        if record.status == "failed":
            return "重试"
        return "打开"

    @staticmethod
    def _clear_layout_items(layout: object) -> None:
        """兼容真实 Qt 与占位布局的清空逻辑。"""

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
            return
        items = getattr(layout, "_items", None)
        if isinstance(items, list):
            items.clear()

    @staticmethod
    def _mock_downloads() -> list[DownloadRecord]:
        """返回页面默认使用的 mock 下载数据。"""

        return [
            DownloadRecord(
                download_id="DL-0001",
                title="Amazing Nature Drone Footage - 4K Ultra HD",
                source="YOUTUBE",
                status="downloading",
                downloaded_mb=42.5,
                total_mb=65.2,
                speed_mbps=1.2,
                eta_text="预计剩余 18s",
                quality="4K / 2160p",
                format_label="MP4 视频",
            ),
            DownloadRecord(
                download_id="DL-0002",
                title="TikTok Dance Trends 2024 Compilation",
                source="TIKTOK",
                status="downloading",
                downloaded_mb=12.1,
                total_mb=14.0,
                speed_mbps=3.8,
                eta_text="预计剩余 2s",
                quality="1080p FHD",
                format_label="MP4 视频",
            ),
            DownloadRecord(
                download_id="DL-0003",
                title="Lofi Hip Hop Mix - Study Beat Session",
                source="YOUTUBE",
                status="paused",
                downloaded_mb=5.2,
                total_mb=15.8,
                speed_mbps=0.0,
                eta_text="暂停中",
                quality="720p HD",
                format_label="MP4 视频",
            ),
            DownloadRecord(
                download_id="DL-0004",
                title="Instagram Travel Reel Collection - Spring Edit",
                source="INSTAGRAM",
                status="queued",
                downloaded_mb=0.0,
                total_mb=28.6,
                speed_mbps=0.0,
                eta_text="等待队列",
                quality="1080p FHD",
                format_label="MP4 视频",
            ),
            DownloadRecord(
                download_id="DL-0005",
                title="Shop Product Soundtrack Pack",
                source="TIKTOK",
                status="completed",
                downloaded_mb=18.4,
                total_mb=18.4,
                speed_mbps=0.0,
                eta_text="已完成",
                quality="MP3 320kbps",
                format_label="MP3 音频",
            ),
            DownloadRecord(
                download_id="DL-0006",
                title="Creator Studio Episode Cut - Behind the Scene",
                source="YOUTUBE",
                status="failed",
                downloaded_mb=17.6,
                total_mb=44.0,
                speed_mbps=0.0,
                eta_text="签名解析异常，等待重试",
                quality="4K / 2160p",
                format_label="MP4 视频",
            ),
        ]


__all__ = ["DownloaderPage"]
