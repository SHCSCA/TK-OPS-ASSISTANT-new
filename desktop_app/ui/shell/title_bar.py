# pyright: basic, reportAttributeAccessIssue=false, reportMissingImports=false

from __future__ import annotations

"""TK-OPS 应用标题栏组件。"""

from ...core.qt import QApplication, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, Qt, Signal
from ...core.theme.tokens import STATIC_TOKENS, get_token_value
from ...core.types import ThemeMode


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用兼容层方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _set_object_name(widget: object, name: str) -> None:
    """安全设置对象名。"""

    _call(widget, "setObjectName", name)


def _set_text(widget: object, text: str) -> None:
    """安全更新文本。"""

    _call(widget, "setText", text)


def _set_stylesheet(widget: object, stylesheet: str) -> None:
    """安全应用样式。"""

    _call(widget, "setStyleSheet", stylesheet)


def _set_cursor(widget: object, cursor: object) -> None:
    """安全设置鼠标样式。"""

    _call(widget, "setCursor", cursor)


def _set_fixed_height(widget: object, height: int) -> None:
    """安全设置固定高度。"""

    _call(widget, "setFixedHeight", height)
    _call(widget, "setMinimumHeight", height)


def _theme_mode() -> ThemeMode:
    """尽量从应用实例解析当前主题模式。"""

    app = QApplication.instance() if hasattr(QApplication, "instance") else None
    if app is None:
        return ThemeMode.LIGHT

    property_reader = getattr(app, "property", None)
    if not callable(property_reader):
        return ThemeMode.LIGHT

    for key in ("theme.mode", "theme_mode", "themeMode"):
        resolved = property_reader(key)
        if isinstance(resolved, ThemeMode):
            return resolved
        if isinstance(resolved, str) and resolved.lower() == ThemeMode.DARK.value:
            return ThemeMode.DARK
    return ThemeMode.LIGHT


def _token(name: str) -> str:
    """读取当前主题下的语义 token。"""

    return get_token_value(name, _theme_mode())


def _px_token(name: str, fallback: int) -> int:
    """将像素 token 转为整数。"""

    raw = STATIC_TOKENS.get(name, f"{fallback}px")
    digits = "".join(character for character in raw if character.isdigit())
    return int(digits) if digits else fallback


def _color_with_alpha(color: str, alpha: float, fallback: str) -> str:
    """将十六进制或 rgb 颜色转换为 rgba。"""

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
RADIUS_MD = _px_token("radius.md", 8)
RADIUS_LG = _px_token("radius.lg", 12)
RADIUS_XL = _px_token("radius.xl", 16)
TITLE_BAR_HEIGHT = 48
ACTION_SIZE = TITLE_BAR_HEIGHT - (SPACING_MD * 2)
TITLE_LABEL_MIN_WIDTH = SPACING_XL * 10
SEARCH_BUTTON_MIN_WIDTH = ACTION_SIZE * 4
ALIGN_LEFT = getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignLeft", 0)
ALIGN_CENTER = getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignCenter", 0)
POINTING_CURSOR = getattr(Qt, "PointingHandCursor", getattr(getattr(Qt, "CursorShape", Qt), "PointingHandCursor", 0))


class TitleBar(QWidget):
    """自定义标题栏，承载品牌、页面标题与全局动作。"""

    theme_toggle_requested = Signal()
    search_requested = Signal()
    notifications_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._page_title = "系统就绪"

        _set_object_name(self, "titleBar")
        _set_fixed_height(self, TITLE_BAR_HEIGHT)

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(SPACING_XL, SPACING_MD, SPACING_XL, SPACING_MD)
        root_layout.setSpacing(SPACING_LG)

        self._brand_host = QWidget(self)
        _set_object_name(self._brand_host, "titleBarBrandHost")
        brand_layout = QVBoxLayout(self._brand_host)
        brand_layout.setContentsMargins(SPACING_MD, 0, SPACING_LG, 0)
        brand_layout.setSpacing(0)
        _call(self._brand_host, "setMinimumHeight", ACTION_SIZE)

        self._brand_label = QLabel("TK-OPS", self._brand_host)
        _set_object_name(self._brand_label, "titleBarBrand")
        self._brand_hint = QLabel("运营控制台", self._brand_host)
        _set_object_name(self._brand_hint, "titleBarBrandHint")

        brand_layout.addWidget(self._brand_label)
        brand_layout.addWidget(self._brand_hint)

        self._page_label = QLabel(self._page_title, self)
        _set_object_name(self._page_label, "titleBarPageTitle")
        _call(self._page_label, "setAlignment", ALIGN_LEFT)
        _call(self._page_label, "setMinimumHeight", ACTION_SIZE)
        _call(self._page_label, "setMinimumWidth", TITLE_LABEL_MIN_WIDTH)

        self._actions_host = QWidget(self)
        _set_object_name(self._actions_host, "titleBarActions")
        actions_layout = QHBoxLayout(self._actions_host)
        actions_layout.setContentsMargins(SPACING_XS, 0, SPACING_XS, 0)
        actions_layout.setSpacing(SPACING_XS)
        _call(self._actions_host, "setMinimumHeight", ACTION_SIZE)

        self._search_button = QPushButton("⌕  全局搜索", self._actions_host)
        _set_object_name(self._search_button, "titleBarSearchButton")
        _set_cursor(self._search_button, POINTING_CURSOR)
        _call(self._search_button, "setMinimumWidth", SEARCH_BUTTON_MIN_WIDTH)
        self._search_button.clicked.connect(self.search_requested.emit)

        self._theme_button = QPushButton("🌓", self._actions_host)
        _set_object_name(self._theme_button, "titleBarActionButton")
        _set_cursor(self._theme_button, POINTING_CURSOR)
        self._theme_button.clicked.connect(self.theme_toggle_requested.emit)
        _call(self._theme_button, "setToolTip", "切换主题")

        self._notifications_button = QPushButton("🔔", self._actions_host)
        _set_object_name(self._notifications_button, "titleBarActionButton")
        _set_cursor(self._notifications_button, POINTING_CURSOR)
        self._notifications_button.clicked.connect(self.notifications_requested.emit)
        _call(self._notifications_button, "setToolTip", "打开通知中心")

        self._avatar = QLabel("运营", self._actions_host)
        _set_object_name(self._avatar, "titleBarAvatar")
        _call(self._avatar, "setAlignment", ALIGN_CENTER)

        actions_layout.addWidget(self._search_button)
        actions_layout.addWidget(self._theme_button)
        actions_layout.addWidget(self._notifications_button)
        actions_layout.addWidget(self._avatar)

        root_layout.addWidget(self._brand_host)
        root_layout.addStretch(1)
        root_layout.addWidget(self._page_label)
        root_layout.addStretch(1)
        root_layout.addWidget(self._actions_host)

        self._apply_styles()

    def set_page_title(self, title: str) -> None:
        """更新中间区域的页面标题。"""

        self._page_title = title or "系统就绪"
        _set_text(self._page_label, self._page_title)

    def _apply_styles(self) -> None:
        surface = _token("surface.secondary")
        border = _token("border.default")
        text_primary = _token("text.primary")
        text_secondary = _token("text.secondary")
        accent = _token("brand.primary")
        surface_sunken = _token("surface.sunken")
        surface_hover = _token("surface.tertiary")
        text_inverse = _token("text.inverse")
        accent_panel = _color_with_alpha(accent, 0.10, surface_hover)
        accent_panel_hover = _color_with_alpha(accent, 0.16, surface_hover)
        accent_border = _color_with_alpha(accent, 0.28, border)
        panel_border = _color_with_alpha(text_secondary, 0.18, border)
        action_hover = _color_with_alpha(accent, 0.12, surface_hover)
        action_pressed = _color_with_alpha(accent, 0.18, surface_hover)

        _set_stylesheet(
            self,
            (
                "QWidget#titleBar {"
                f"background-color: {surface};"
                f"border-bottom: 1px solid {border};"
                "}"
                "QWidget#titleBarBrandHost {"
                f"background-color: {accent_panel};"
                f"border: 1px solid {accent_border};"
                f"border-radius: {RADIUS_XL}px;"
                f"min-height: {ACTION_SIZE}px;"
                "}"
                "QLabel#titleBarBrand {"
                f"color: {accent};"
                f"font-size: {STATIC_TOKENS['font.size.lg']};"
                f"font-weight: {STATIC_TOKENS['font.weight.bold']};"
                f"font-family: {STATIC_TOKENS['font.family.primary']};"
                "background: transparent;"
                "}"
                "QLabel#titleBarBrandHint {"
                f"color: {text_secondary};"
                f"font-size: {STATIC_TOKENS['font.size.xs']};"
                f"font-family: {STATIC_TOKENS['font.family.chinese']};"
                f"font-weight: {STATIC_TOKENS['font.weight.medium']};"
                "background: transparent;"
                "}"
                "QLabel#titleBarPageTitle {"
                f"background-color: {surface_sunken};"
                f"color: {text_primary};"
                f"font-size: {STATIC_TOKENS['font.size.xl']};"
                f"font-weight: {STATIC_TOKENS['font.weight.semibold']};"
                f"font-family: {STATIC_TOKENS['font.family.chinese']};"
                f"border: 1px solid {panel_border};"
                f"border-left: 3px solid {accent};"
                f"border-radius: {RADIUS_LG}px;"
                f"padding: 0 {SPACING_LG}px 0 {SPACING_XL}px;"
                f"min-height: {ACTION_SIZE}px;"
                f"min-width: {TITLE_LABEL_MIN_WIDTH}px;"
                "}"
                "QWidget#titleBarActions {"
                f"background-color: {surface_sunken};"
                f"border: 1px solid {panel_border};"
                f"border-radius: {RADIUS_XL}px;"
                f"min-height: {ACTION_SIZE}px;"
                "}"
                "QPushButton#titleBarSearchButton {"
                f"background-color: {accent_panel};"
                f"color: {text_primary};"
                f"border: 1px solid {accent_border};"
                f"border-radius: {RADIUS_LG}px;"
                f"padding: 0 {SPACING_XL}px;"
                f"font-size: {STATIC_TOKENS['font.size.sm']};"
                f"font-weight: {STATIC_TOKENS['font.weight.medium']};"
                f"font-family: {STATIC_TOKENS['font.family.chinese']};"
                "text-align: left;"
                f"min-width: {SEARCH_BUTTON_MIN_WIDTH}px;"
                f"min-height: {ACTION_SIZE}px;"
                "}"
                "QPushButton#titleBarSearchButton:hover {"
                f"border-color: {accent};"
                f"color: {text_primary};"
                f"background-color: {accent_panel_hover};"
                "}"
                "QPushButton#titleBarSearchButton:pressed {"
                f"background-color: {action_pressed};"
                "}"
                "QPushButton#titleBarActionButton {"
                "background-color: transparent;"
                f"color: {text_secondary};"
                "border: 1px solid transparent;"
                f"border-radius: {RADIUS_MD}px;"
                f"padding: 0 {SPACING_SM}px;"
                f"min-width: {ACTION_SIZE}px;"
                f"min-height: {ACTION_SIZE}px;"
                f"font-size: {STATIC_TOKENS['font.size.md']};"
                f"font-weight: {STATIC_TOKENS['font.weight.medium']};"
                "}"
                "QPushButton#titleBarActionButton:hover {"
                f"border-color: {accent};"
                f"color: {accent};"
                f"background-color: {action_hover};"
                "}"
                "QPushButton#titleBarActionButton:pressed {"
                f"background-color: {action_pressed};"
                "}"
                "QLabel#titleBarAvatar {"
                f"background-color: {accent};"
                f"color: {text_inverse};"
                f"border: 1px solid {accent_border};"
                f"border-radius: {RADIUS_LG}px;"
                f"padding: 0 {SPACING_LG}px;"
                f"font-size: {STATIC_TOKENS['font.size.sm']};"
                f"font-weight: {STATIC_TOKENS['font.weight.bold']};"
                f"font-family: {STATIC_TOKENS['font.family.chinese']};"
                f"min-width: {ACTION_SIZE + SPACING_LG}px;"
                f"min-height: {ACTION_SIZE}px;"
                "}"
            ),
        )


__all__ = ["TitleBar"]
