# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false

from __future__ import annotations

"""TK-OPS 主题侧边栏组件。"""

from ...core.qt import QFrame, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget, Qt, Signal
from ...core.shell.navigation import NavGroup, NavItem, NavigationModel
from ...core.theme.tokens import STATIC_TOKENS, TOKENS


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用兼容层可能缺失的方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _set_object_name(widget: object, name: str) -> None:
    """安全设置对象名。"""

    _call(widget, "setObjectName", name)


def _set_visible(widget: object, visible: bool) -> None:
    """安全切换显隐。"""

    _call(widget, "setVisible", visible)


def _set_text(widget: object, text: str) -> None:
    """安全更新文本。"""

    _call(widget, "setText", text)


def _set_stylesheet(widget: object, stylesheet: str) -> None:
    """安全写入样式。"""

    _call(widget, "setStyleSheet", stylesheet)


def _set_tooltip(widget: object, text: str) -> None:
    """安全设置提示文案。"""

    _call(widget, "setToolTip", text)


def _set_fixed_width(widget: object, width: int) -> None:
    """安全设置固定宽度。"""

    _call(widget, "setMinimumWidth", width)
    _call(widget, "setMaximumWidth", width)


def _set_fixed_height(widget: object, height: int) -> None:
    """安全设置固定高度。"""

    _call(widget, "setFixedHeight", height)
    _call(widget, "setMinimumHeight", height)


def _set_property(widget: object, name: str, value: object) -> None:
    """安全设置动态属性。"""

    _call(widget, "setProperty", name, value)


def _set_alignment(widget: object, alignment: int) -> None:
    """安全设置对齐方式。"""

    _call(widget, "setAlignment", alignment)


def _clear_layout(layout: object) -> None:
    """清空布局中的所有子项。"""

    count_method = getattr(layout, "count", None)
    take_at = getattr(layout, "takeAt", None)
    if callable(count_method) and callable(take_at):
        while True:
            count_value = count_method()
            if not isinstance(count_value, int) or count_value <= 0:
                break
            item = take_at(0)
            widget_getter = getattr(item, "widget", None)
            widget = widget_getter() if callable(widget_getter) else None
            if widget is not None:
                _call(widget, "setParent", None)
        return

    items = getattr(layout, "_items", None)
    if isinstance(items, list):
        items.clear()


def _px_token(name: str, fallback: int) -> int:
    """将像素 token 转为整数。"""

    raw = STATIC_TOKENS.get(name, f"{fallback}px")
    digits = "".join(character for character in raw if character.isdigit())
    return int(digits) if digits else fallback


def _sidebar_icon(icon_name: str) -> str:
    """将路由图标名映射为内置 Unicode 图形。"""

    icon_map = {
        "dashboard": "◫",
        "manage_accounts": "◉",
        "group_work": "◌",
        "devices": "⌘",
        "admin_panel_settings": "⚑",
        "live_tv": "◈",
        "receipt_long": "▤",
        "undo": "↺",
        "support_agent": "☏",
        "movie_edit": "▷",
        "factory": "▥",
        "content_cut": "✂",
        "description": "✎",
        "auto_awesome": "✦",
        "edit_note": "✐",
        "auto_fix_high": "☆",
        "rocket_launch": "⇡",
        "assignment": "☰",
        "bar_chart": "▮",
        "query_stats": "◳",
        "monitoring": "◍",
        "explore": "◎",
        "shopping_bag": "▣",
        "analytics": "◴",
        "face": "☺",
        "pie_chart": "◔",
        "thumb_up": "▲",
        "comment": "✉",
        "mail": "✉",
        "schedule": "◷",
        "robot_2": "⟡",
        "settings": "⚙",
        "lock_person": "◍",
        "history": "◷",
        "account_tree": "⋔",
        "terminal": "⌁",
        "upgrade": "⬆",
        "leak_add": "⇄",
        "download": "↓",
        "bolt": "⚡",
        "hub": "◉",
    }
    return icon_map.get(icon_name, "•")


def _color_with_alpha(color: str, alpha: float, fallback: str) -> str:
    """将十六进制或 rgb 颜色转为带透明度的 rgba。"""

    normalized = color.strip()
    if normalized.startswith("#"):
        hex_color = normalized[1:]
        if len(hex_color) == 3:
            hex_color = "".join(channel * 2 for channel in hex_color)
        if len(hex_color) == 6:
            red = int(hex_color[0:2], 16)
            green = int(hex_color[2:4], 16)
            blue = int(hex_color[4:6], 16)
            return f"rgba({red},{green},{blue},{alpha:.2f})"

    if normalized.startswith("rgb(") and normalized.endswith(")"):
        values = normalized[4:-1].strip()
        return f"rgba({values},{alpha:.2f})"

    return fallback


SPACING_XS = _px_token("spacing.xs", 4)
SPACING_SM = _px_token("spacing.sm", 6)
SPACING_MD = _px_token("spacing.md", 8)
SPACING_LG = _px_token("spacing.lg", 12)
SPACING_XL = _px_token("spacing.xl", 16)
SPACING_2XL = _px_token("spacing.2xl", 24)
RADIUS_MD = _px_token("radius.md", 8)
RADIUS_LG = _px_token("radius.lg", 12)
RADIUS_XL = _px_token("radius.xl", 16)
BUTTON_HEIGHT_SM = _px_token("button.height.sm", 36)
FONT_SIZE_SM = STATIC_TOKENS["font.size.sm"]
FONT_SIZE_MD = STATIC_TOKENS["font.size.md"]
FONT_WEIGHT_MEDIUM = STATIC_TOKENS["font.weight.medium"]
FONT_WEIGHT_SEMIBOLD = STATIC_TOKENS["font.weight.semibold"]
FONT_WEIGHT_BOLD = STATIC_TOKENS["font.weight.bold"]
SIDEBAR_WIDTH_EXPANDED = 216
SIDEBAR_WIDTH_COLLAPSED = 56
SIDEBAR_BACKGROUND = TOKENS["brand.secondary"].light
SIDEBAR_PANEL_SOFT = "rgba(255,255,255,0.03)"
SIDEBAR_PANEL = "rgba(255,255,255,0.05)"
SIDEBAR_PANEL_ELEVATED = "rgba(255,255,255,0.08)"
SIDEBAR_BORDER = "rgba(255,255,255,0.08)"
SIDEBAR_BORDER_STRONG = "rgba(255,255,255,0.14)"
SIDEBAR_TEXT = TOKENS["text.primary"].dark
SIDEBAR_MUTED = TOKENS["text.secondary"].dark
SIDEBAR_DIM = TOKENS["text.tertiary"].dark
SIDEBAR_ACCENT = TOKENS["brand.primary"].light
SIDEBAR_HOVER = "rgba(0,242,234,0.12)"
SIDEBAR_ACTIVE = "rgba(0,242,234,0.18)"
SIDEBAR_ACTIVE_STRONG = "rgba(0,242,234,0.24)"
SIDEBAR_CONTEXT = "rgba(255,255,255,0.06)"
SIDEBAR_CONTEXT_STRONG = "rgba(255,255,255,0.09)"
SIDEBAR_DIVIDER = "rgba(255,255,255,0.05)"
SIDEBAR_GLOW = "rgba(0,242,234,0.22)"
DEFAULT_GROUP_COLOR = TOKENS["brand.accent"].light
POINTING_CURSOR = getattr(Qt, "PointingHandCursor", getattr(getattr(Qt, "CursorShape", Qt), "PointingHandCursor", 0))
ALIGN_LEFT = getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignLeft", 0)
ALIGN_CENTER = getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignCenter", 0)


class _RouteMeta:
    """记录单个路由按钮的层级关系。"""

    def __init__(self, button: QPushButton, depth: int, parent_route_id: str | None) -> None:
        self.button = button
        self.depth = depth
        self.parent_route_id = parent_route_id


class _SidebarSection(QWidget):
    """承载单个导航分组及其可折叠内容。"""

    def __init__(self, group: NavGroup, route_requested: Signal, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.group = group
        self._route_requested = route_requested
        self._sidebar_collapsed = False
        self._current_route_id = ""
        self._routes: dict[str, _RouteMeta] = {}
        self._group_color = self._resolve_group_color(group)

        _set_object_name(self, "sidebarSection")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, SPACING_SM)
        root_layout.setSpacing(SPACING_SM)

        self._compact_marker = QFrame(self)
        _set_object_name(self._compact_marker, "sidebarCompactMarker")
        _set_fixed_height(self._compact_marker, 2)

        self._header_button = QPushButton("", self)
        _set_object_name(self._header_button, "sidebarGroupHeader")
        _call(self._header_button, "setCheckable", False)
        self._header_button.clicked.connect(self.toggle_expanded)

        self._body = QWidget(self)
        _set_object_name(self._body, "sidebarSectionBody")
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(SPACING_XS)

        root_layout.addWidget(self._compact_marker)
        root_layout.addWidget(self._header_button)
        root_layout.addWidget(self._body)

        for item in group.items:
            self._add_item(item, depth=0, parent_route_id=None)

        self._refresh_header_text()
        self._apply_header_style()
        self._apply_compact_marker_style()
        self._apply_collapsed_state()

    def contains_route(self, route_id: str) -> bool:
        """判断当前分组是否包含指定路由。"""

        return route_id in self._routes

    def route_buttons(self) -> dict[str, _RouteMeta]:
        """返回当前分组下的全部按钮映射。"""

        return dict(self._routes)

    def expand_for_route(self, route_id: str) -> None:
        """当子路由激活时自动展开所属分组。"""

        if route_id in self._routes:
            self.group.is_expanded = True
            self._refresh_header_text()
            self._apply_collapsed_state()

    def set_sidebar_collapsed(self, collapsed: bool) -> None:
        """同步全局侧边栏折叠态。"""

        self._sidebar_collapsed = collapsed
        self._apply_collapsed_state()
        self._refresh_route_styles()

    def set_active_route(self, route_id: str) -> None:
        """刷新当前分组内所有按钮的激活态。"""

        self._current_route_id = route_id
        self._refresh_route_styles()

    def toggle_expanded(self) -> None:
        """切换当前分组折叠状态。"""

        self.group.is_expanded = not self.group.is_expanded
        self._refresh_header_text()
        self._apply_collapsed_state()

    def _add_item(self, item: NavItem, depth: int, parent_route_id: str | None) -> None:
        route_id = str(item.route_id)
        button = QPushButton("", self._body)
        _set_object_name(button, "sidebarNavButton")
        _call(button, "setCheckable", True)
        _call(button, "setCursor", POINTING_CURSOR)
        _set_tooltip(button, item.label)
        button.clicked.connect(lambda _checked=False, resolved_route=route_id: self._route_requested.emit(resolved_route))

        self._routes[route_id] = _RouteMeta(button=button, depth=depth, parent_route_id=parent_route_id)
        self._body_layout.addWidget(button)
        self._update_button_text(button, item=item, depth=depth)

        for child in item.children:
            self._add_item(child, depth=depth + 1, parent_route_id=route_id)

    def _refresh_header_text(self) -> None:
        arrow = "▾" if self.group.is_expanded else "▸"
        _set_text(self._header_button, f"{arrow}  {self.group.title}")

    def _apply_collapsed_state(self) -> None:
        _set_visible(self._header_button, not self._sidebar_collapsed)
        _set_visible(self._compact_marker, self._sidebar_collapsed)
        _set_visible(self._body, self._sidebar_collapsed or self.group.is_expanded)

        for route_id, meta in self._routes.items():
            item_visible = meta.depth == 0 if self._sidebar_collapsed else self.group.is_expanded
            _set_visible(meta.button, item_visible)
            self._update_button_text(meta.button, item=None, depth=meta.depth, route_id=route_id)

    def _refresh_route_styles(self) -> None:
        active_parent = self._active_parent_route()
        for route_id, meta in self._routes.items():
            is_active = route_id == self._current_route_id
            is_parent_active = active_parent == route_id and not is_active
            self._apply_nav_button_style(meta.button, meta.depth, is_active, is_parent_active)

    def _active_parent_route(self) -> str | None:
        current = self._routes.get(self._current_route_id)
        return current.parent_route_id if current is not None else None

    def _update_button_text(
        self,
        button: QPushButton,
        *,
        item: NavItem | None,
        depth: int,
        route_id: str | None = None,
    ) -> None:
        resolved_item = item
        if resolved_item is None and route_id is not None:
            for candidate_route in self._routes:
                if candidate_route != route_id:
                    continue
                resolved_item = self._nav_item_from_route(candidate_route)
                break

        if resolved_item is None:
            return

        icon = _sidebar_icon(resolved_item.icon)
        badge = f"  · {resolved_item.badge_text}" if resolved_item.badge_text and not self._sidebar_collapsed else ""
        if self._sidebar_collapsed:
            text = icon
        elif depth > 0:
            text = f"↳  {resolved_item.label}{badge}"
        else:
            text = f"{icon}  {resolved_item.label}{badge}"
        _set_text(button, text)
        _set_tooltip(button, resolved_item.label)

    def _nav_item_from_route(self, route_id: str) -> NavItem | None:
        def visit(items: list[NavItem]) -> NavItem | None:
            for item in items:
                if str(item.route_id) == route_id:
                    return item
                resolved = visit(item.children)
                if resolved is not None:
                    return resolved
            return None

        return visit(self.group.items)

    def _apply_header_style(self) -> None:
        header_background = _color_with_alpha(self._group_color, 0.10, SIDEBAR_PANEL)
        header_hover_background = _color_with_alpha(self._group_color, 0.16, SIDEBAR_PANEL_ELEVATED)
        header_border = _color_with_alpha(self._group_color, 0.28, SIDEBAR_BORDER_STRONG)
        _set_stylesheet(
            self._header_button,
            (
                "QPushButton#sidebarGroupHeader {"
                f"background-color: {header_background};"
                f"border: 1px solid {header_border};"
                f"border-left: 3px solid {self._group_color};"
                f"padding: {SPACING_SM}px {SPACING_LG}px {SPACING_SM}px {SPACING_XL}px;"
                f"border-radius: {RADIUS_LG}px;"
                f"color: {self._group_color};"
                f"font-size: {FONT_SIZE_SM};"
                f"font-weight: {FONT_WEIGHT_SEMIBOLD};"
                "text-align: left;"
                "}"
                "QPushButton#sidebarGroupHeader:hover {"
                f"background-color: {header_hover_background};"
                f"border-color: {self._group_color};"
                "}"
                "QPushButton#sidebarGroupHeader:pressed {"
                f"background-color: {SIDEBAR_CONTEXT_STRONG};"
                "}"
            ),
        )

    def _apply_compact_marker_style(self) -> None:
        marker_color = _color_with_alpha(self._group_color, 0.92, self._group_color)
        _set_stylesheet(
            self._compact_marker,
            f"QFrame#sidebarCompactMarker {{ background-color: {marker_color}; border-radius: 1px; }}",
        )

    def _apply_nav_button_style(self, button: QPushButton, depth: int, is_active: bool, is_parent_active: bool) -> None:
        left_padding = SPACING_LG if self._sidebar_collapsed else SPACING_XL + (depth * SPACING_MD)
        right_padding = SPACING_MD if self._sidebar_collapsed else SPACING_LG
        parent_background = _color_with_alpha(self._group_color, 0.10, SIDEBAR_CONTEXT)
        parent_border = _color_with_alpha(self._group_color, 0.24, SIDEBAR_BORDER)
        inactive_background = SIDEBAR_PANEL_SOFT if depth == 0 and not self._sidebar_collapsed else "transparent"
        hover_background = SIDEBAR_HOVER if depth == 0 else _color_with_alpha(self._group_color, 0.12, SIDEBAR_CONTEXT_STRONG)
        background = SIDEBAR_ACTIVE if is_active else parent_background if is_parent_active else inactive_background
        text_color = SIDEBAR_ACCENT if is_active else SIDEBAR_TEXT if depth == 0 or is_parent_active else SIDEBAR_MUTED
        border_color = SIDEBAR_ACCENT if is_active else parent_border if is_parent_active else SIDEBAR_DIVIDER if depth == 0 and not self._sidebar_collapsed else "transparent"
        font_weight = FONT_WEIGHT_BOLD if is_active else FONT_WEIGHT_SEMIBOLD if depth == 0 or is_parent_active else FONT_WEIGHT_MEDIUM
        hover_text = SIDEBAR_ACCENT if is_active else SIDEBAR_TEXT
        min_height = 40 if depth == 0 else 30
        font_size = FONT_SIZE_MD if depth == 0 or self._sidebar_collapsed else FONT_SIZE_SM

        _set_stylesheet(
            button,
            (
                "QPushButton#sidebarNavButton {"
                f"background-color: {background};"
                f"color: {text_color};"
                f"border: 1px solid {SIDEBAR_BORDER};"
                f"border-left: 3px solid {border_color};"
                f"border-radius: {RADIUS_LG}px;"
                f"padding: {SPACING_SM}px {right_padding}px {SPACING_SM}px {left_padding}px;"
                f"font-size: {font_size};"
                f"font-weight: {font_weight};"
                f"min-height: {min_height}px;"
                f"text-align: {'center' if self._sidebar_collapsed else 'left'};"
                "}"
                "QPushButton#sidebarNavButton:hover {"
                f"background-color: {hover_background};"
                f"color: {hover_text};"
                f"border-color: {SIDEBAR_ACCENT};"
                "}"
                "QPushButton#sidebarNavButton:pressed {"
                f"background-color: {SIDEBAR_ACTIVE_STRONG};"
                "}"
            ),
        )
        _call(button, "setChecked", is_active)

    @staticmethod
    def _resolve_group_color(group: NavGroup) -> str:
        if group.color and group.color != "default":
            return group.color
        return DEFAULT_GROUP_COLOR


class Sidebar(QWidget):
    """分组导航侧边栏，支持分组折叠与全局收起。"""

    route_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._navigation_model: NavigationModel | None = None
        self._current_route_id = ""
        self._collapsed = False
        self._sections: list[_SidebarSection] = []
        self._route_buttons: dict[str, _RouteMeta] = {}

        _set_object_name(self, "sidebar")
        _set_property(self, "variant", "sidebar")
        _set_fixed_width(self, SIDEBAR_WIDTH_EXPANDED)

        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(SPACING_LG, SPACING_XL, SPACING_LG, SPACING_LG)
        self._root_layout.setSpacing(SPACING_LG)

        self._brand = QWidget(self)
        _set_object_name(self._brand, "sidebarBrand")
        self._brand_layout = QVBoxLayout(self._brand)
        self._brand_layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_SM)
        self._brand_layout.setSpacing(SPACING_XS)

        self._brand_title = QLabel("TK-OPS", self._brand)
        _set_object_name(self._brand_title, "sidebarBrandTitle")
        self._brand_subtitle = QLabel("全域运营中枢", self._brand)
        _set_object_name(self._brand_subtitle, "sidebarBrandSubtitle")

        self._brand_layout.addWidget(self._brand_title)
        self._brand_layout.addWidget(self._brand_subtitle)

        self._scroll = QScrollArea(self)
        _set_object_name(self._scroll, "sidebarScroll")
        _call(self._scroll, "setWidgetResizable", True)

        self._scroll_content = QWidget(self)
        _set_object_name(self._scroll_content, "sidebarScrollContent")
        self._content_layout = QVBoxLayout(self._scroll_content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(SPACING_MD)
        self._content_layout.addStretch(1)
        _call(self._scroll, "setWidget", self._scroll_content)

        self._footer = QWidget(self)
        _set_object_name(self._footer, "sidebarFooter")
        self._footer_layout = QVBoxLayout(self._footer)
        self._footer_layout.setContentsMargins(0, SPACING_SM, 0, 0)
        self._footer_layout.setSpacing(SPACING_SM)

        self._settings_button = QPushButton("⚙  设置", self._footer)
        _set_object_name(self._settings_button, "sidebarUtilityButton")
        self._settings_button.clicked.connect(lambda _checked=False: self.route_requested.emit("system_settings"))

        self._collapse_button = QPushButton("«  收起导航", self._footer)
        _set_object_name(self._collapse_button, "sidebarCollapseButton")
        self._collapse_button.clicked.connect(self.toggle_collapsed)

        self._footer_layout.addWidget(self._settings_button)
        self._footer_layout.addWidget(self._collapse_button)

        self._root_layout.addWidget(self._brand)
        self._root_layout.addWidget(self._scroll, 1)
        self._root_layout.addWidget(self._footer)

        self._apply_shell_style()
        self._apply_footer_styles()
        self._apply_collapsed_state()

    def populate(self, navigation_model: NavigationModel) -> None:
        """根据导航模型渲染分组与路由按钮。"""

        self._navigation_model = navigation_model
        self._sections.clear()
        self._route_buttons.clear()
        _clear_layout(self._content_layout)

        for group in navigation_model.groups:
            section = _SidebarSection(group, self.route_requested, self._scroll_content)
            section.set_sidebar_collapsed(self._collapsed)
            self._sections.append(section)
            self._route_buttons.update(section.route_buttons())
            self._content_layout.addWidget(section)

        self._content_layout.addStretch(1)
        if self._current_route_id:
            self.set_active_route(self._current_route_id)

    def set_active_route(self, route_id: str) -> None:
        """同步当前激活路由的视觉状态。"""

        self._current_route_id = route_id
        for section in self._sections:
            if section.contains_route(route_id):
                section.expand_for_route(route_id)
            section.set_active_route(route_id)
        self._apply_footer_styles()

    def set_collapsed(self, collapsed: bool) -> None:
        """显式设置侧边栏展开或收起状态。"""

        self._collapsed = collapsed
        self._apply_collapsed_state()

    def toggle_collapsed(self) -> None:
        """切换侧边栏宽度。"""

        self.set_collapsed(not self._collapsed)

    def _apply_shell_style(self) -> None:
        _set_stylesheet(
            self,
            (
                "QWidget#sidebar {"
                f"background-color: {SIDEBAR_BACKGROUND};"
                f"border-right: 1px solid {SIDEBAR_BORDER_STRONG};"
                "}"
                "QWidget#sidebarBrand {"
                f"background-color: {SIDEBAR_PANEL_ELEVATED};"
                f"border: 1px solid {SIDEBAR_BORDER_STRONG};"
                f"border-top: 1px solid {SIDEBAR_GLOW};"
                f"border-radius: {RADIUS_XL}px;"
                "}"
                "QLabel#sidebarBrandTitle {"
                f"color: {SIDEBAR_ACCENT};"
                f"font-size: {STATIC_TOKENS['font.size.xl']};"
                f"font-weight: {FONT_WEIGHT_BOLD};"
                "background: transparent;"
                "}"
                "QLabel#sidebarBrandSubtitle {"
                f"color: {SIDEBAR_DIM};"
                f"font-size: {FONT_SIZE_SM};"
                "background: transparent;"
                "}"
                "QWidget#sidebarSection, QWidget#sidebarSectionBody, QScrollArea#sidebarScroll, QWidget#sidebarScrollContent {"
                "background: transparent;"
                "border: none;"
                "}"
                "QWidget#sidebarFooter {"
                "background: transparent;"
                f"border-top: 1px solid {SIDEBAR_DIVIDER};"
                "}"
            ),
        )

    def _apply_footer_styles(self) -> None:
        settings_active = self._current_route_id == "system_settings"
        self._apply_footer_button_style(
            self._settings_button,
            object_name="sidebarUtilityButton",
            active=settings_active,
            accent=DEFAULT_GROUP_COLOR,
        )
        self._apply_footer_button_style(
            self._collapse_button,
            object_name="sidebarCollapseButton",
            active=self._collapsed,
            accent=SIDEBAR_ACCENT,
        )

    def _apply_footer_button_style(self, button: QPushButton, *, object_name: str, active: bool, accent: str) -> None:
        background = SIDEBAR_ACTIVE if active else SIDEBAR_PANEL_ELEVATED
        hover_background = SIDEBAR_ACTIVE_STRONG if active else SIDEBAR_CONTEXT_STRONG
        text = SIDEBAR_ACCENT if active else SIDEBAR_TEXT
        border = accent if active else SIDEBAR_BORDER
        _set_stylesheet(
            button,
            (
                f"QPushButton#{object_name} {{"
                f"background-color: {background};"
                f"color: {text};"
                f"border: 1px solid {border};"
                f"border-radius: {RADIUS_XL}px;"
                f"padding: {SPACING_MD}px {SPACING_LG}px;"
                f"font-size: {FONT_SIZE_MD};"
                f"font-weight: {FONT_WEIGHT_SEMIBOLD};"
                f"min-height: {BUTTON_HEIGHT_SM}px;"
                f"text-align: {'center' if self._collapsed else 'left'};"
                "}"
                f"QPushButton#{object_name}:hover {{"
                f"background-color: {hover_background};"
                f"border-color: {accent};"
                "}"
                f"QPushButton#{object_name}:pressed {{"
                f"background-color: {SIDEBAR_ACTIVE_STRONG};"
                "}"
            ),
        )

    def _apply_collapsed_state(self) -> None:
        width = SIDEBAR_WIDTH_COLLAPSED if self._collapsed else SIDEBAR_WIDTH_EXPANDED
        _set_fixed_width(self, width)

        _set_visible(self._brand_subtitle, not self._collapsed)
        _set_text(self._brand_title, "TK" if self._collapsed else "TK-OPS")
        _set_text(self._settings_button, "⚙" if self._collapsed else "⚙  设置")
        _set_text(self._collapse_button, "»" if self._collapsed else "«  收起导航")
        _set_tooltip(self._collapse_button, "展开导航" if self._collapsed else "收起导航")
        _set_alignment(self._brand_title, ALIGN_CENTER if self._collapsed else ALIGN_LEFT)
        _set_alignment(self._brand_subtitle, ALIGN_CENTER if self._collapsed else ALIGN_LEFT)

        if self._collapsed:
            self._brand_layout.setContentsMargins(SPACING_XS, SPACING_LG, SPACING_XS, SPACING_LG)
            self._brand_layout.setSpacing(0)
        else:
            self._brand_layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_SM)
            self._brand_layout.setSpacing(SPACING_XS)

        for section in self._sections:
            section.set_sidebar_collapsed(self._collapsed)

        self._apply_footer_styles()


__all__ = ["Sidebar"]
