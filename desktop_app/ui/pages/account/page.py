# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false

from __future__ import annotations

"""账号管理页面。"""

from dataclasses import dataclass
from typing import cast

from ....core.types import RouteId
from ...components.buttons import PrimaryButton, SecondaryButton
from ...components.cards import ProfileCard
from ...components.inputs import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    FilterDropdown,
    SearchBar,
    RADIUS_LG,
    RADIUS_MD,
    SPACING_MD,
    SPACING_SM,
    SPACING_LG,
    SPACING_XL,
    SPACING_2XL,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ...components.layouts import ContentSection, PageContainer, SplitPanel, TabBar, ThemedScrollArea
from ...components.tables import DataTable
from ...components.tags import BadgeTone, StatusBadge, TagChip
from ..base_page import BasePage

CARDS_PER_ROW = 2
SEARCH_MIN_WIDTH = 280
FILTER_MIN_WIDTH = 156
LEFT_PANE_MIN_WIDTH = 720
RIGHT_PANE_MIN_WIDTH = 320


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
    """兼容真实 Qt 与占位 Qt 的布局清空。"""

    take_at = getattr(layout, "takeAt", None)
    count_method = getattr(layout, "count", None)
    if callable(take_at) and callable(count_method):
        while True:
            count = count_method()
            if not isinstance(count, int) or count <= 0:
                break
            item = take_at(0)
            widget = item.widget() if hasattr(item, "widget") else None
            child_layout = item.layout() if hasattr(item, "layout") else None
            if child_layout is not None:
                _clear_layout(child_layout)
            if widget is not None:
                _call(widget, "setParent", None)
                _call(widget, "deleteLater")
        return

    items = getattr(layout, "_items", None)
    if isinstance(items, list):
        while items:
            item = items.pop(0)
            if hasattr(item, "_items"):
                _clear_layout(item)
                continue
            widget = item.widget() if hasattr(item, "widget") else item if isinstance(item, QWidget) else None
            if widget is not None:
                _call(widget, "setParent", None)
                _call(widget, "deleteLater")


@dataclass(frozen=True)
class AccountRecord:
    """账号演示数据。"""

    account_id: str
    display_name: str
    handle: str
    account_type: str
    status: str
    status_tone: BadgeTone
    risk_label: str
    risk_tone: BadgeTone
    follower_count: str
    video_count: str
    like_count: str
    region: str
    store_name: str
    owner: str
    proxy_ip: str
    last_login: str
    cookie_status: str
    cookie_status_tone: BadgeTone
    cookie_expiry: str
    cookie_domain_count: str
    user_agent: str
    canvas_id: str
    webgl_vendor: str
    bio: str
    tags: tuple[str, ...]
    history_rows: tuple[tuple[str, str, str], ...]


class AccountPage(BasePage):
    """TikTok 账号矩阵管理页。"""

    default_route_id: RouteId = RouteId("account_management")
    default_display_name: str = "账号管理"
    default_icon_name: str = "manage_accounts"

    def setup_ui(self) -> None:
        """构建账号管理页面。"""

        self._accounts = self._build_demo_accounts()
        self._selected_account_id = self._accounts[0].account_id if self._accounts else None
        self._extra_account_cursor = 0
        self._active_tab_index = 0
        self._detail_tag_chips = []
        self._detail_stat_chips = []
        self._card_refs = {}
        self._tab_pages = {}
        self._tab_definitions = (
            ("all", "全部账号", None),
            ("online", "在线", "在线"),
            ("offline", "离线", "离线"),
            ("warning", "异常", "预警"),
            ("paused", "暂停", "暂停"),
        )

        _call(self, "setObjectName", "accountPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        page_container = PageContainer(
            title="账号管理",
            description="集中管理 TikTok 账号矩阵、代理环境与会话状态，快速定位高风险账号并查看环境详情。",
            parent=self,
        )

        action_bar = QFrame(page_container)
        _call(action_bar, "setObjectName", "accountActionBar")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(SPACING_XL, SPACING_MD, SPACING_XL, SPACING_MD)
        action_layout.setSpacing(SPACING_LG)

        self._search_bar = SearchBar("搜索账号、IP 或 ID")
        _call(self._search_bar, "setMinimumWidth", SEARCH_MIN_WIDTH)

        self._region_filter = FilterDropdown(
            "地区筛选",
            tuple(sorted({account.region for account in self._accounts})),
            include_all=True,
        )
        _call(self._region_filter, "setMinimumWidth", FILTER_MIN_WIDTH)

        self._add_button = PrimaryButton("添加账号", action_bar, icon_text="＋")
        self._import_button = SecondaryButton("导入 CSV", action_bar, icon_text="⇪")

        action_layout.addWidget(self._search_bar)
        action_layout.addWidget(self._region_filter)
        action_layout.addStretch(1)
        action_layout.addWidget(self._add_button)
        action_layout.addWidget(self._import_button)
        page_container.add_action(action_bar)

        self._warning_banner = self._build_warning_banner(page_container)
        page_container.add_widget(self._warning_banner)

        split_panel = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.69, 0.31),
            minimum_sizes=(LEFT_PANE_MIN_WIDTH, RIGHT_PANE_MIN_WIDTH),
            parent=page_container,
        )
        split_panel.set_widgets(self._build_left_pane(split_panel), self._build_right_pane(split_panel))
        page_container.add_widget(split_panel)

        self.layout.addWidget(page_container)

        _connect(self._search_bar.search_changed, self._refresh_account_views)
        _connect(self._region_filter.filter_changed, self._refresh_account_views)
        _connect(getattr(self._add_button, "clicked", None), self._handle_add_account)
        _connect(getattr(self._import_button, "clicked", None), self._handle_import_accounts)
        _connect(self._tab_bar.tab_changed, self._handle_tab_changed)

        self._apply_page_styles()
        self._refresh_account_views()

    def _build_warning_banner(self, parent: QWidget) -> QWidget:
        """顶部高风险提示横幅。"""

        banner = QFrame(parent)
        _call(banner, "setObjectName", "accountWarningBanner")

        layout = QHBoxLayout(banner)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_LG)

        icon_label = QLabel("⚠", banner)
        _call(icon_label, "setObjectName", "accountWarningIcon")

        self._warning_text_label = QLabel("", banner)
        _call(self._warning_text_label, "setObjectName", "accountWarningText")
        _call(self._warning_text_label, "setWordWrap", True)

        action_button = QPushButton("立即开启", banner)
        _call(action_button, "setObjectName", "accountWarningButton")
        _connect(getattr(action_button, "clicked", None), self._focus_high_risk_tab)

        layout.addWidget(icon_label)
        layout.addWidget(self._warning_text_label, 1)
        layout.addWidget(action_button)
        return banner

    def _build_left_pane(self, parent: QWidget) -> QWidget:
        """左侧账号卡片区域。"""

        pane = QWidget(parent)
        _call(pane, "setObjectName", "accountLeftPane")

        layout = QVBoxLayout(pane)
        layout.setContentsMargins(0, 0, SPACING_XL, 0)
        layout.setSpacing(SPACING_XL)

        self._tab_bar = TabBar(pane)

        for tab_key, title, _status in self._tab_definitions:
            tab_page = QWidget(self._tab_bar)
            tab_layout = QVBoxLayout(tab_page)
            tab_layout.setContentsMargins(0, 0, 0, 0)
            tab_layout.setSpacing(SPACING_LG)

            summary_row = QFrame(tab_page)
            _call(summary_row, "setObjectName", "accountTabSummaryRow")
            summary_layout = QHBoxLayout(summary_row)
            summary_layout.setContentsMargins(SPACING_XL, SPACING_MD, SPACING_XL, SPACING_MD)
            summary_layout.setSpacing(SPACING_SM)

            summary_label = QLabel("", summary_row)
            _call(summary_label, "setObjectName", "accountTabSummaryLabel")

            summary_chip = TagChip("0 个账号", tone="brand", parent=summary_row)

            summary_layout.addWidget(summary_label)
            summary_layout.addStretch(1)
            summary_layout.addWidget(summary_chip)

            scroll_area = ThemedScrollArea(tab_page)
            scroll_area.content_layout.setContentsMargins(0, 0, 0, 0)
            scroll_area.content_layout.setSpacing(SPACING_LG)

            empty_label = QLabel("暂无匹配账号", tab_page)
            _call(empty_label, "setObjectName", "accountEmptyStateLabel")
            _call(empty_label, "setWordWrap", True)

            grid_host = QWidget(tab_page)
            grid_layout = QVBoxLayout(grid_host)
            grid_layout.setContentsMargins(0, 0, 0, 0)
            grid_layout.setSpacing(SPACING_LG)

            scroll_area.add_widget(empty_label)
            scroll_area.add_widget(grid_host)
            scroll_area.content_layout.addStretch(1)

            tab_layout.addWidget(summary_row)
            tab_layout.addWidget(scroll_area, 1)

            self._tab_pages[tab_key] = {
                "summary_label": summary_label,
                "summary_chip": summary_chip,
                "empty_label": empty_label,
                "grid_host": grid_host,
                "grid_layout": grid_layout,
            }
            self._tab_bar.add_tab(title, tab_page)

        layout.addWidget(self._tab_bar)
        return pane

    def _build_right_pane(self, parent: QWidget) -> QWidget:
        """右侧账号详情侧栏。"""

        sidebar = QFrame(parent)
        _call(sidebar, "setObjectName", "accountDetailSidebar")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll_area = ThemedScrollArea(sidebar)
        scroll_area.content_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        scroll_area.content_layout.setSpacing(SPACING_XL)

        hero_card = QFrame(sidebar)
        _call(hero_card, "setObjectName", "accountDetailHero")
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        hero_layout.setSpacing(SPACING_LG)

        hero_header = QHBoxLayout()
        hero_header.setSpacing(SPACING_LG)

        self._detail_avatar_label = QLabel("TK", hero_card)
        _call(self._detail_avatar_label, "setObjectName", "accountDetailAvatar")

        title_layout = QVBoxLayout()
        title_layout.setSpacing(SPACING_SM)

        self._detail_title_label = QLabel("请选择账号", hero_card)
        _call(self._detail_title_label, "setObjectName", "accountDetailTitle")
        self._detail_subtitle_label = QLabel("点击左侧卡片查看环境详情", hero_card)
        _call(self._detail_subtitle_label, "setObjectName", "accountDetailSubtitle")
        _call(self._detail_subtitle_label, "setWordWrap", True)

        title_layout.addWidget(self._detail_title_label)
        title_layout.addWidget(self._detail_subtitle_label)

        self._detail_status_badge = StatusBadge("待选择", tone="neutral", parent=hero_card)

        hero_header.addWidget(self._detail_avatar_label)
        hero_header.addLayout(title_layout, 1)
        hero_header.addWidget(self._detail_status_badge)

        tag_host = QWidget(hero_card)
        self._detail_tag_layout = QHBoxLayout(tag_host)
        self._detail_tag_layout.setContentsMargins(0, 0, 0, 0)
        self._detail_tag_layout.setSpacing(SPACING_SM)

        stat_host = QWidget(hero_card)
        self._detail_stat_layout = QHBoxLayout(stat_host)
        self._detail_stat_layout.setContentsMargins(0, 0, 0, 0)
        self._detail_stat_layout.setSpacing(SPACING_SM)

        self._detail_bio_label = QLabel("", hero_card)
        _call(self._detail_bio_label, "setObjectName", "accountDetailBio")
        _call(self._detail_bio_label, "setWordWrap", True)

        hero_layout.addLayout(hero_header)
        hero_layout.addWidget(tag_host)
        hero_layout.addWidget(stat_host)
        hero_layout.addWidget(self._detail_bio_label)

        self._cookie_section = ContentSection("Cookie 状态", icon="◉", parent=sidebar)
        cookie_body = QWidget(self._cookie_section)
        cookie_layout = QVBoxLayout(cookie_body)
        cookie_layout.setContentsMargins(0, 0, 0, 0)
        cookie_layout.setSpacing(SPACING_MD)

        cookie_status_row = QWidget(cookie_body)
        cookie_status_layout = QHBoxLayout(cookie_status_row)
        cookie_status_layout.setContentsMargins(0, 0, 0, 0)
        cookie_status_layout.setSpacing(SPACING_MD)

        cookie_hint = QLabel("当前会话可用性", cookie_body)
        _call(cookie_hint, "setObjectName", "accountDetailMutedLabel")
        self._detail_cookie_badge = StatusBadge("待选择", tone="neutral", parent=cookie_body)

        cookie_status_layout.addWidget(cookie_hint)
        cookie_status_layout.addStretch(1)
        cookie_status_layout.addWidget(self._detail_cookie_badge)

        self._detail_cookie_expiry = self._build_value_block("过期日期", cookie_body)
        self._detail_cookie_domains = self._build_value_block("域名数", cookie_body)
        self._detail_cookie_owner = self._build_value_block("负责人", cookie_body)
        self._cookie_manage_button = SecondaryButton("管理 Cookies", cookie_body, icon_text="◎")

        cookie_layout.addWidget(cookie_status_row)
        cookie_layout.addWidget(self._detail_cookie_expiry[0])
        cookie_layout.addWidget(self._detail_cookie_domains[0])
        cookie_layout.addWidget(self._detail_cookie_owner[0])
        cookie_layout.addWidget(self._cookie_manage_button)
        self._cookie_section.add_widget(cookie_body)

        self._fingerprint_section = ContentSection("浏览器指纹", icon="◈", parent=sidebar)
        fingerprint_body = QWidget(self._fingerprint_section)
        fingerprint_layout = QVBoxLayout(fingerprint_body)
        fingerprint_layout.setContentsMargins(0, 0, 0, 0)
        fingerprint_layout.setSpacing(SPACING_MD)

        self._detail_fp_user_agent = self._build_value_block("User-Agent", fingerprint_body)
        self._detail_fp_canvas = self._build_value_block("Canvas ID", fingerprint_body)
        self._detail_fp_webgl = self._build_value_block("WebGL Vendor", fingerprint_body)

        fingerprint_layout.addWidget(self._detail_fp_user_agent[0])
        fingerprint_layout.addWidget(self._detail_fp_canvas[0])
        fingerprint_layout.addWidget(self._detail_fp_webgl[0])
        self._fingerprint_section.add_widget(fingerprint_body)

        self._history_section = ContentSection("登录历史", icon="◌", parent=sidebar)
        self._history_table = DataTable(
            headers=("时间", "事件", "结果"),
            rows=(),
            page_size=4,
            empty_text="暂无登录记录",
            parent=sidebar,
        )
        self._history_section.add_widget(self._history_table)

        self._detail_action_button = SecondaryButton("环境配置", sidebar, icon_text="⚙")

        scroll_area.add_widget(hero_card)
        scroll_area.add_widget(self._cookie_section)
        scroll_area.add_widget(self._fingerprint_section)
        scroll_area.add_widget(self._history_section)
        scroll_area.add_widget(self._detail_action_button)
        scroll_area.content_layout.addStretch(1)

        layout.addWidget(scroll_area)
        return sidebar

    def _build_value_block(self, title: str, parent: QWidget) -> tuple[QFrame, QLabel]:
        """构建右侧详情信息块。"""

        block = QFrame(parent)
        _call(block, "setObjectName", "accountDetailInfoBlock")

        layout = QVBoxLayout(block)
        layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_MD)
        layout.setSpacing(SPACING_SM)

        title_label = QLabel(title, block)
        _call(title_label, "setObjectName", "accountDetailBlockTitle")
        value_label = QLabel("--", block)
        _call(value_label, "setObjectName", "accountDetailBlockValue")
        _call(value_label, "setWordWrap", True)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return block, value_label

    def _refresh_account_views(self, _value: str | None = None) -> None:
        """刷新 tab、卡片和详情面板。"""

        base_accounts = self._filtered_accounts()
        self._update_banner_text()
        self._update_tab_titles(base_accounts)
        self._rebuild_tab_pages(base_accounts)
        self._sync_selected_account(base_accounts)
        self._update_card_selection_state()
        self._update_detail_panel(self._find_account(self._selected_account_id))

    def _filtered_accounts(self) -> list[AccountRecord]:
        """应用搜索和地区筛选。"""

        keyword = self._search_bar.text().strip().lower()
        region = self._region_filter.current_text().strip()
        results = []

        for account in self._accounts:
            haystack = " ".join(
                (
                    account.account_id,
                    account.display_name,
                    account.handle,
                    account.owner,
                    account.proxy_ip,
                    account.store_name,
                    account.region,
                )
            ).lower()
            matches_keyword = not keyword or keyword in haystack
            matches_region = region in ("", "全部") or account.region == region
            if matches_keyword and matches_region:
                results.append(account)

        return results

    def _accounts_for_tab(self, accounts: list[AccountRecord], status: str | None) -> list[AccountRecord]:
        """按 tab 状态过滤。"""

        if status is None:
            return list(accounts)
        return [account for account in accounts if account.status == status]

    def _update_tab_titles(self, base_accounts: list[AccountRecord]) -> None:
        """同步标签标题与计数。"""

        buttons = getattr(self._tab_bar, "_buttons", [])
        for index, (_tab_key, title, status) in enumerate(self._tab_definitions):
            count = len(self._accounts_for_tab(base_accounts, status))
            button = buttons[index] if index < len(buttons) else None
            if button is not None:
                _call(button, "setText", f"{title} ({count})")

    def _rebuild_tab_pages(self, base_accounts: list[AccountRecord]) -> None:
        """按当前筛选结果重建每个 tab 的卡片网格。"""

        self._card_refs = {}

        for tab_key, _title, status in self._tab_definitions:
            page_refs = self._tab_pages[tab_key]
            accounts = self._accounts_for_tab(base_accounts, status)
            summary_label = page_refs["summary_label"]
            summary_chip = page_refs["summary_chip"]
            empty_label = page_refs["empty_label"]
            grid_host = page_refs["grid_host"]
            grid_layout = page_refs["grid_layout"]

            _clear_layout(grid_layout)
            summary_text = "支持按账号、IP、ID 与地区快速筛选当前账号矩阵。"
            if status == "预警":
                summary_text = "异常账号建议优先检查代理 IP、Cookie 到期与环境指纹。"
            elif status == "暂停":
                summary_text = "暂停账号通常需要人工复核后再恢复环境登录。"
            elif status == "在线":
                summary_text = "在线账号可直接进入环境，适合快速执行日常运营动作。"
            elif status == "离线":
                summary_text = "离线账号建议先测试连接，再进入环境检查登录状态。"

            _call(summary_label, "setText", summary_text)
            summary_chip.set_text(f"{len(accounts)} 个账号")
            summary_chip.set_tone(
                "error"
                if status == "暂停"
                else "warning"
                if status == "预警"
                else "success"
                if status == "在线"
                else "neutral"
                if status == "离线"
                else "brand"
            )

            _call(empty_label, "setVisible", not accounts)
            _call(grid_host, "setVisible", bool(accounts))

            for start in range(0, len(accounts), CARDS_PER_ROW):
                row_layout = QHBoxLayout()
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(SPACING_LG)

                for account in accounts[start : start + CARDS_PER_ROW]:
                    card, primary_button, secondary_button = self._build_account_card(account, tab_key)
                    self._card_refs.setdefault(account.account_id, []).append(
                        {"frame": card, "primary": primary_button, "secondary": secondary_button, "account": account}
                    )
                    row_layout.addWidget(card, 1)

                if len(accounts[start : start + CARDS_PER_ROW]) < CARDS_PER_ROW:
                    row_layout.addStretch(1)

                grid_layout.addLayout(row_layout)

            grid_layout.addStretch(1)

    def _build_account_card(self, account: AccountRecord, tab_key: str) -> tuple[QFrame, PrimaryButton, SecondaryButton]:
        """构建单个账号卡片。"""

        card = QFrame(self)
        _call(card, "setObjectName", f"accountCard_{tab_key}_{account.account_id}")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)

        top_row = QHBoxLayout()
        top_row.setSpacing(SPACING_SM)

        status_badge = StatusBadge(account.status, tone=account.status_tone, parent=card)
        risk_chip = TagChip(account.risk_label, tone=account.risk_tone, parent=card)
        region_chip = TagChip(account.region, tone="neutral", parent=card)

        top_row.addWidget(status_badge)
        top_row.addWidget(risk_chip)
        top_row.addStretch(1)
        top_row.addWidget(region_chip)

        profile_card = ProfileCard(
            name=account.display_name,
            role=account.account_type,
            stats=(("粉丝", account.follower_count), ("视频", account.video_count), ("点赞", account.like_count)),
            parent=card,
        )

        handle_label = QLabel(f"@{account.handle}", card)
        _call(handle_label, "setObjectName", "accountCardHandle")

        store_label = QLabel(account.store_name, card)
        _call(store_label, "setObjectName", "accountCardStore")

        identity_row = QWidget(card)
        _call(identity_row, "setObjectName", "accountCardIdentityRow")
        identity_layout = QHBoxLayout(identity_row)
        identity_layout.setContentsMargins(0, 0, 0, 0)
        identity_layout.setSpacing(SPACING_SM)

        account_id_chip = TagChip(f"ID {account.account_id}", tone="neutral", parent=identity_row)
        cookie_badge = StatusBadge(account.cookie_status, tone=account.cookie_status_tone, parent=identity_row)

        identity_layout.addWidget(account_id_chip)
        identity_layout.addWidget(cookie_badge)
        identity_layout.addStretch(1)

        meta_panel = QFrame(card)
        _call(meta_panel, "setObjectName", "accountCardMetaPanel")
        meta_layout = QVBoxLayout(meta_panel)
        meta_layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_MD)
        meta_layout.setSpacing(SPACING_SM)

        for label_text, value_text in (
            ("代理 IP", account.proxy_ip),
            ("上次登录", account.last_login),
            ("负责人", account.owner),
        ):
            row = QWidget(meta_panel)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(SPACING_MD)

            key_label = QLabel(label_text, row)
            _call(key_label, "setObjectName", "accountCardMetaKey")
            value_label = QLabel(value_text, row)
            _call(value_label, "setObjectName", "accountCardMetaValue")
            _call(value_label, "setWordWrap", True)

            row_layout.addWidget(key_label)
            row_layout.addStretch(1)
            row_layout.addWidget(value_label)
            meta_layout.addWidget(row)

        footer_row = QHBoxLayout()
        footer_row.setSpacing(SPACING_MD)

        primary_text = "处理异常" if account.status == "预警" else "登录环境"
        primary_icon = "⚠" if account.status == "预警" else "↗"
        primary_button = PrimaryButton(primary_text, card, icon_text=primary_icon)
        secondary_button = SecondaryButton("查看详情", card, icon_text="◎")

        _connect(getattr(primary_button, "clicked", None), lambda checked=False, account_id=account.account_id: self._select_account(account_id))
        _connect(getattr(secondary_button, "clicked", None), lambda checked=False, account_id=account.account_id: self._select_account(account_id))

        footer_row.addWidget(primary_button)
        footer_row.addWidget(secondary_button)

        layout.addLayout(top_row)
        layout.addWidget(profile_card)
        layout.addWidget(handle_label)
        layout.addWidget(store_label)
        layout.addWidget(identity_row)
        layout.addWidget(meta_panel)
        layout.addLayout(footer_row)

        self._apply_account_card_style(card, account, account.account_id == self._selected_account_id)
        return card, primary_button, secondary_button

    def _apply_account_card_style(self, card: QFrame, account: AccountRecord, selected: bool) -> None:
        """应用账号卡片选中态和风险态样式。"""

        colors = _palette()
        highlight = _token("brand.primary")
        warning = _token("status.warning")

        border_color = highlight if selected else _rgba(warning, 0.34) if account.risk_tone in ("warning", "error") else colors.border
        background_color = _rgba(highlight, 0.08) if selected else colors.surface

        _call(
            card,
            "setStyleSheet",
            f"""
            QFrame#{getattr(card, 'objectName', lambda: '')()} {{
                background-color: {background_color};
                border: 1px solid {border_color};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#accountCardHandle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#accountCardStore {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                background: transparent;
            }}
            QFrame#accountCardMetaPanel {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_MD}px;
            }}
            QLabel#accountCardMetaKey {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                background: transparent;
            }}
            QLabel#accountCardMetaValue {{
                color: {colors.text};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
                background: transparent;
            }}
            """,
        )

    def _sync_selected_account(self, base_accounts: list[AccountRecord]) -> None:
        """保证当前选中账号仍在当前 tab 可见。"""

        current_status = self._tab_definitions[self._active_tab_index][2]
        visible_accounts = self._accounts_for_tab(base_accounts, current_status)
        visible_ids = {account.account_id for account in visible_accounts}

        if self._selected_account_id not in visible_ids:
            self._selected_account_id = visible_accounts[0].account_id if visible_accounts else None

    def _update_card_selection_state(self) -> None:
        """刷新卡片视觉选中态。"""

        for account_id, refs in self._card_refs.items():
            for ref in refs:
                account = ref["account"]
                card = ref["frame"]
                primary_button = ref["primary"]
                secondary_button = ref["secondary"]
                selected = account_id == self._selected_account_id

                self._apply_account_card_style(card, account, selected)
                secondary_button.set_label_text("当前查看" if selected else "查看详情")
                if account.status == "预警":
                    primary_button.set_label_text("立即处理" if selected else "处理异常")
                else:
                    primary_button.set_label_text("进入环境" if selected else "登录环境")

    def _update_detail_panel(self, account: AccountRecord | None) -> None:
        """刷新右侧详情。"""

        if account is None:
            self._detail_title_label.setText("暂无匹配账号")
            self._detail_subtitle_label.setText("请调整搜索条件或切换标签页")
            self._detail_avatar_label.setText("--")
            self._detail_status_badge.setText("空状态")
            self._detail_status_badge.set_tone("neutral")
            self._detail_bio_label.setText("当前没有可展示的账号详情。")
            self._detail_cookie_badge.setText("无会话")
            self._detail_cookie_badge.set_tone("neutral")
            self._detail_cookie_expiry[1].setText("--")
            self._detail_cookie_domains[1].setText("--")
            self._detail_cookie_owner[1].setText("--")
            self._detail_fp_user_agent[1].setText("--")
            self._detail_fp_canvas[1].setText("--")
            self._detail_fp_webgl[1].setText("--")
            self._history_table.set_rows(())
            self._detail_action_button.set_label_text("环境配置")
            self._cookie_manage_button.set_label_text("管理 Cookies")
            self._rebuild_detail_chips((), self._detail_tag_layout, self._detail_tag_chips)
            self._rebuild_detail_chips((), self._detail_stat_layout, self._detail_stat_chips)
            return

        self._detail_title_label.setText(account.display_name)
        self._detail_subtitle_label.setText(f"ID: {account.account_id} · @{account.handle} · {account.region} · 负责人 {account.owner}")
        self._detail_avatar_label.setText(account.display_name[:2])
        self._detail_status_badge.setText(account.status)
        self._detail_status_badge.set_tone(account.status_tone)
        self._detail_bio_label.setText(account.bio)

        self._detail_cookie_badge.setText(account.cookie_status)
        self._detail_cookie_badge.set_tone(account.cookie_status_tone)
        self._detail_cookie_expiry[1].setText(account.cookie_expiry)
        self._detail_cookie_domains[1].setText(account.cookie_domain_count)
        self._detail_cookie_owner[1].setText(account.owner)
        self._detail_fp_user_agent[1].setText(account.user_agent)
        self._detail_fp_canvas[1].setText(account.canvas_id)
        self._detail_fp_webgl[1].setText(account.webgl_vendor)
        self._history_table.set_rows(account.history_rows)
        self._detail_action_button.set_label_text("处理高风险环境" if account.risk_tone in ("warning", "error") else "环境配置")
        self._cookie_manage_button.set_label_text("更新 Cookies" if account.cookie_status_tone in ("warning", "error") else "管理 Cookies")

        tags = (
            (account.account_type, cast(BadgeTone, "brand")),
            (account.store_name, cast(BadgeTone, "info")),
            (account.region, cast(BadgeTone, "neutral")),
            (account.risk_label, account.risk_tone),
            *((tag, cast(BadgeTone, "neutral")) for tag in account.tags),
        )
        stats = (
            (f"粉丝 {account.follower_count}", cast(BadgeTone, "brand")),
            (f"视频 {account.video_count}", cast(BadgeTone, "info")),
            (f"点赞 {account.like_count}", cast(BadgeTone, "success")),
        )
        self._rebuild_detail_chips(tags, self._detail_tag_layout, self._detail_tag_chips)
        self._rebuild_detail_chips(stats, self._detail_stat_layout, self._detail_stat_chips)

    def _rebuild_detail_chips(
        self,
        chip_specs: tuple[tuple[str, str], ...],
        layout: QHBoxLayout,
        chip_store: list[TagChip],
    ) -> None:
        """重建详情区域芯片行。"""

        for chip in chip_store:
            _call(chip, "setParent", None)
            _call(chip, "deleteLater")
        chip_store.clear()

        _clear_layout(layout)
        for text, tone in chip_specs:
            chip = TagChip(text, tone=cast(BadgeTone, tone), parent=self)
            chip_store.append(chip)
            layout.addWidget(chip)
        layout.addStretch(1)

    def _select_account(self, account_id: str) -> None:
        """选中账号并刷新详情。"""

        self._selected_account_id = account_id
        self._update_card_selection_state()
        self._update_detail_panel(self._find_account(account_id))

    def _handle_tab_changed(self, index: int) -> None:
        """切换标签后同步当前选中账号。"""

        self._active_tab_index = index
        self._refresh_account_views()

    def _focus_high_risk_tab(self) -> None:
        """跳转到异常标签。"""

        self._tab_bar.set_current(3)

    def _handle_add_account(self) -> None:
        """新增一条演示账号。"""

        account = self._build_extra_account(self._extra_account_cursor)
        self._extra_account_cursor += 1
        self._accounts.append(account)
        self._selected_account_id = account.account_id
        self._refresh_account_views()

    def _handle_import_accounts(self) -> None:
        """模拟导入 CSV。"""

        first = self._build_extra_account(self._extra_account_cursor)
        self._extra_account_cursor += 1
        second = self._build_extra_account(self._extra_account_cursor)
        self._extra_account_cursor += 1
        self._accounts.extend((first, second))
        self._selected_account_id = second.account_id
        self._refresh_account_views()

    def _update_banner_text(self) -> None:
        """根据风险账号数量更新顶部横幅。"""

        risky_count = sum(1 for account in self._accounts if account.risk_tone in ("warning", "error"))
        if risky_count <= 0:
            self._warning_text_label.setText("当前账号矩阵风险可控，建议继续保持隔离环境与定期 Cookie 巡检。")
            return
        self._warning_text_label.setText(
            f"⚠️ 多账号隔离未启用 - 当前有 {risky_count} 个账号处于高风险或待复核状态，建议立即开启环境隔离。"
        )

    def _find_account(self, account_id: str | None) -> AccountRecord | None:
        """按 ID 查询账号。"""

        if not account_id:
            return None
        for account in self._accounts:
            if account.account_id == account_id:
                return account
        return None

    def _apply_page_styles(self) -> None:
        """页面局部样式。"""

        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#accountPage {{
                background-color: {_token('surface.primary')};
            }}
            QFrame#accountActionBar,
            QFrame#accountTabSummaryRow {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#accountWarningBanner {{
                background-color: {_rgba(_token('status.error'), 0.08)};
                border: 1px solid {_rgba(_token('status.error'), 0.16)};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#accountWarningIcon {{
                color: {_token('status.error')};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#accountWarningText,
            QLabel#accountTabSummaryLabel,
            QLabel#accountDetailMutedLabel,
            QLabel#accountDetailSubtitle,
            QLabel#accountDetailBio {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                background: transparent;
            }}
            QPushButton#accountWarningButton {{
                background-color: {_token('status.error')};
                color: #FFFFFF;
                border: 1px solid {_token('status.error')};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_MD}px {SPACING_XL}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QFrame#accountDetailSidebar {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#accountDetailHero {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border_strong};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#accountDetailAvatar {{
                min-width: 56px;
                max-width: 56px;
                min-height: 56px;
                max-height: 56px;
                border-radius: 28px;
                background-color: {_rgba(_token('brand.primary'), 0.14)};
                border: 1px solid {_rgba(_token('brand.primary'), 0.26)};
                color: {_token('brand.primary')};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#accountDetailTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QFrame#accountDetailInfoBlock {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_MD}px;
            }}
            QLabel#accountDetailBlockTitle {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.xs')};
                background: transparent;
            }}
            QLabel#accountDetailBlockValue {{
                color: {colors.text};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
                background: transparent;
            }}
            QLabel#accountEmptyStateLabel {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.md')};
                background-color: {colors.surface_alt};
                border: 1px dashed {colors.border};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_2XL}px;
            }}
            """,
        )

    def _build_demo_accounts(self) -> list[AccountRecord]:
        """默认账号数据。"""

        return [
            AccountRecord(
                account_id="992834012",
                display_name="鹿小贝出海",
                handle="tk_luxiaobei_01",
                account_type="矩阵主号",
                status="在线",
                status_tone="success",
                risk_label="低风险",
                risk_tone="success",
                follower_count="12.3万",
                video_count="486",
                like_count="518.6万",
                region="美国",
                store_name="TK 美妆旗舰店",
                owner="林知夏",
                proxy_ip="192.168.1.1（洛杉矶）",
                last_login="10 分钟前",
                cookie_status="有效",
                cookie_status_tone="success",
                cookie_expiry="2026-03-24",
                cookie_domain_count="12 个域名",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/122.0",
                canvas_id="e849c-f921-4d1a-82bc",
                webgl_vendor="Apple Inc. (Apple M1)",
                bio="主打美妆测评与店播引流，近 7 日自然流量稳定提升，适合承接新品首发。",
                tags=("店播引流", "高复购", "美妆个护"),
                history_rows=(
                    ("今天 14:22", "成功登录", "IP 192.168.1.1"),
                    ("今天 14:20", "环境检测通过", "洛杉矶节点"),
                    ("昨天 23:11", "登录失败", "密码错误"),
                    ("昨天 17:05", "Cookie 更新", "已同步"),
                ),
            ),
            AccountRecord(
                account_id="884120776",
                display_name="青禾家居实验室",
                handle="qinghe_home_lab",
                account_type="内容账号",
                status="在线",
                status_tone="success",
                risk_label="观察中",
                risk_tone="info",
                follower_count="8.7万",
                video_count="328",
                like_count="203.2万",
                region="英国",
                store_name="Home Picks UK",
                owner="周砚",
                proxy_ip="154.22.81.44（伦敦）",
                last_login="35 分钟前",
                cookie_status="有效",
                cookie_status_tone="success",
                cookie_expiry="2026-03-19",
                cookie_domain_count="9 个域名",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0",
                canvas_id="uk17-home-f3a1",
                webgl_vendor="Google Inc. (ANGLE)",
                bio="家居垂类种草号，热视频集中在收纳、小家电与卧室改造场景。",
                tags=("家居", "种草短视频", "中高客单"),
                history_rows=(
                    ("今天 09:48", "成功登录", "伦敦代理"),
                    ("今天 09:26", "素材发布", "已完成"),
                    ("昨天 20:10", "达人私信回收", "已同步"),
                    ("昨天 16:45", "环境检测通过", "正常"),
                ),
            ),
            AccountRecord(
                account_id="771024531",
                display_name="拾光穿搭志",
                handle="shiguang_fit_edit",
                account_type="短视频达人",
                status="离线",
                status_tone="neutral",
                risk_label="待激活",
                risk_tone="neutral",
                follower_count="6.1万",
                video_count="214",
                like_count="98.5万",
                region="新加坡",
                store_name="Urban Style SG",
                owner="许今安",
                proxy_ip="10.12.4.9（新加坡）",
                last_login="2 小时前",
                cookie_status="即将到期",
                cookie_status_tone="warning",
                cookie_expiry="2026-03-11",
                cookie_domain_count="6 个域名",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) Chrome/120.0",
                canvas_id="sg77-style-aa19",
                webgl_vendor="Apple Inc. (Metal)",
                bio="穿搭混剪账号，近期用于内容冷启和新品风格测试。",
                tags=("穿搭", "内容冷启", "新品测试"),
                history_rows=(
                    ("今天 11:20", "连接测试", "需重新登录"),
                    ("昨天 23:11", "登录失败", "Cookie 临近过期"),
                    ("昨天 20:40", "脚本更新", "已完成"),
                    ("周五 09:50", "代理切换", "成功"),
                ),
            ),
            AccountRecord(
                account_id="650092481",
                display_name="墨川数码侦察局",
                handle="shop_manager_03",
                account_type="运营负责人",
                status="预警",
                status_tone="warning",
                risk_label="高风险",
                risk_tone="warning",
                follower_count="18.9万",
                video_count="562",
                like_count="649.1万",
                region="美国",
                store_name="3C Trend US",
                owner="沈知遥",
                proxy_ip="异常（IP 已被拉黑）",
                last_login="1 天前",
                cookie_status="异常",
                cookie_status_tone="error",
                cookie_expiry="2026-03-09",
                cookie_domain_count="4 个域名",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0",
                canvas_id="risk-19ff-0a22",
                webgl_vendor="Intel Iris OpenGL Engine",
                bio="数码测评矩阵主账号，当前因代理节点异常触发高风险预警，建议优先处理环境。",
                tags=("数码", "风控优先", "高客单"),
                history_rows=(
                    ("1 天前", "登录失败", "IP 被拒"),
                    ("1 天前", "Cookie 校验", "状态异常"),
                    ("2 天前", "代理切换", "失败"),
                    ("2 天前", "脚本同步", "已完成"),
                ),
            ),
            AccountRecord(
                account_id="538812609",
                display_name="山海厨房研究所",
                handle="kitchen_story_lab",
                account_type="内容账号",
                status="在线",
                status_tone="success",
                risk_label="稳定",
                risk_tone="success",
                follower_count="9.4万",
                video_count="291",
                like_count="174.8万",
                region="马来西亚",
                store_name="Kitchen Daily MY",
                owner="顾南枝",
                proxy_ip="172.31.18.5（吉隆坡）",
                last_login="今天 11:36",
                cookie_status="有效",
                cookie_status_tone="success",
                cookie_expiry="2026-04-02",
                cookie_domain_count="10 个域名",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0",
                canvas_id="my56-ac19-77b0",
                webgl_vendor="Google Inc. (ANGLE D3D11)",
                bio="厨房好物内容号，热视频稳定带来店铺自然成交，适合做节奏型内容发布。",
                tags=("厨房好物", "食谱场景", "自然流量"),
                history_rows=(
                    ("今天 11:36", "成功登录", "吉隆坡节点"),
                    ("今天 08:30", "短视频发布", "已完成"),
                    ("昨天 22:00", "选品同步", "已完成"),
                    ("昨天 14:15", "素材归档", "成功"),
                ),
            ),
            AccountRecord(
                account_id="420661915",
                display_name="昼夜运动补给站",
                handle="daynight_fit_supply",
                account_type="短视频达人",
                status="暂停",
                status_tone="error",
                risk_label="待复核",
                risk_tone="error",
                follower_count="5.8万",
                video_count="176",
                like_count="88.9万",
                region="加拿大",
                store_name="Fitness Fuel CA",
                owner="黎川",
                proxy_ip="34.88.14.201（多伦多）",
                last_login="3 天前",
                cookie_status="失效",
                cookie_status_tone="error",
                cookie_expiry="2026-03-06",
                cookie_domain_count="0 个域名",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) Chrome/118.0",
                canvas_id="ca21-0ab8-reset",
                webgl_vendor="AMD Radeon Pro 5500M",
                bio="运动补剂短视频账号，当前暂停投放并等待人工复核后恢复。",
                tags=("运动健康", "账号暂停", "人工处理"),
                history_rows=(
                    ("3 天前", "Cookie 校验", "已失效"),
                    ("3 天前", "视频发布", "被拦截"),
                    ("4 天前", "环境重建", "处理中"),
                    ("5 天前", "脚本回滚", "已完成"),
                ),
            ),
        ]

    def _build_extra_account(self, index: int) -> AccountRecord:
        """新增/导入时的额外演示账号。"""

        templates = (
            AccountRecord(
                account_id=f"78001{index:03d}",
                display_name="海盐宠物观察室",
                handle="pet_salt_lab",
                account_type="内容账号",
                status="在线",
                status_tone="success",
                risk_label="稳定",
                risk_tone="success",
                follower_count="4.6万",
                video_count="132",
                like_count="64.8万",
                region="澳洲",
                store_name="Pet Daily AU",
                owner="苏晚",
                proxy_ip="10.1.5.18（悉尼）",
                last_login="今天 13:08",
                cookie_status="有效",
                cookie_status_tone="success",
                cookie_expiry="2026-03-24",
                cookie_domain_count="7 个域名",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) Chrome/122.0",
                canvas_id="au19-pet-6f01",
                webgl_vendor="Apple Inc. (Apple GPU)",
                bio="宠物用品内容号，适合承接节日选题和评论种草任务。",
                tags=("宠物用品", "节日选题", "评论种草"),
                history_rows=(
                    ("今天 13:08", "成功登录", "悉尼节点"),
                    ("今天 12:20", "短视频发布", "已完成"),
                    ("昨天 19:00", "选题同步", "已完成"),
                    ("昨天 10:10", "Cookie 更新", "成功"),
                ),
            ),
            AccountRecord(
                account_id=f"78002{index:03d}",
                display_name="星野母婴手记",
                handle="momcare_daily_note",
                account_type="矩阵主号",
                status="在线",
                status_tone="success",
                risk_label="观察中",
                risk_tone="info",
                follower_count="7.2万",
                video_count="168",
                like_count="117.4万",
                region="美国",
                store_name="Mom Care US",
                owner="唐栀",
                proxy_ip="10.1.7.35（西雅图）",
                last_login="今天 15:12",
                cookie_status="有效",
                cookie_status_tone="success",
                cookie_expiry="2026-03-27",
                cookie_domain_count="8 个域名",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/123.0",
                canvas_id="us77-mom-4c82",
                webgl_vendor="NVIDIA Corporation",
                bio="母婴用品垂类账号，适合配合店铺新品做短视频素材投放。",
                tags=("母婴", "短视频素材", "新品拉新"),
                history_rows=(
                    ("今天 15:12", "成功登录", "西雅图节点"),
                    ("今天 09:45", "短视频素材同步", "已完成"),
                    ("昨天 18:10", "素材归档", "已完成"),
                    ("昨天 08:50", "评论巡检", "成功"),
                ),
            ),
        )
        return templates[index % len(templates)]
