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


SPACING_SM = _px_token("spacing.sm", 6)
SPACING_MD = _px_token("spacing.md", 8)
SPACING_LG = _px_token("spacing.lg", 12)
SPACING_XL = _px_token("spacing.xl", 16)
RADIUS_MD = _px_token("radius.md", 8)
RADIUS_LG = _px_token("radius.lg", 12)
TITLE_BAR_HEIGHT = 48
ALIGN_LEFT = getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignLeft", 0)
ALIGN_CENTER = getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignCenter", 0)


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
        root_layout.setContentsMargins(SPACING_XL, SPACING_SM, SPACING_XL, SPACING_SM)
        root_layout.setSpacing(SPACING_XL)

        self._brand_host = QWidget(self)
        _set_object_name(self._brand_host, "titleBarBrandHost")
        brand_layout = QVBoxLayout(self._brand_host)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(0)

        self._brand_label = QLabel("TK-OPS", self._brand_host)
        _set_object_name(self._brand_label, "titleBarBrand")
        self._brand_hint = QLabel("运营控制台", self._brand_host)
        _set_object_name(self._brand_hint, "titleBarBrandHint")

        brand_layout.addWidget(self._brand_label)
        brand_layout.addWidget(self._brand_hint)

        self._page_label = QLabel(self._page_title, self)
        _set_object_name(self._page_label, "titleBarPageTitle")
        _call(self._page_label, "setAlignment", ALIGN_LEFT)

        self._actions_host = QWidget(self)
        _set_object_name(self._actions_host, "titleBarActions")
        actions_layout = QHBoxLayout(self._actions_host)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(SPACING_SM)

        self._search_button = QPushButton("⌕  全局搜索", self._actions_host)
        _set_object_name(self._search_button, "titleBarSearchButton")
        self._search_button.clicked.connect(self.search_requested.emit)

        self._theme_button = QPushButton("🌓", self._actions_host)
        _set_object_name(self._theme_button, "titleBarActionButton")
        self._theme_button.clicked.connect(self.theme_toggle_requested.emit)
        _call(self._theme_button, "setToolTip", "切换主题")

        self._notifications_button = QPushButton("🔔", self._actions_host)
        _set_object_name(self._notifications_button, "titleBarActionButton")
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

        _set_stylesheet(
            self,
            (
                "QWidget#titleBar {"
                f"background-color: {surface};"
                f"border-bottom: 1px solid {border};"
                "}"
                "QLabel#titleBarBrand {"
                f"color: {accent};"
                f"font-size: {STATIC_TOKENS['font.size.lg']};"
                f"font-weight: {STATIC_TOKENS['font.weight.bold']};"
                "background: transparent;"
                "}"
                "QLabel#titleBarBrandHint {"
                f"color: {text_secondary};"
                f"font-size: {STATIC_TOKENS['font.size.xs']};"
                "background: transparent;"
                "}"
                "QLabel#titleBarPageTitle {"
                f"color: {text_primary};"
                f"font-size: {STATIC_TOKENS['font.size.xl']};"
                f"font-weight: {STATIC_TOKENS['font.weight.semibold']};"
                "background: transparent;"
                "padding: 0 12px;"
                "}"
                "QPushButton#titleBarSearchButton {"
                f"background-color: {surface_sunken};"
                f"color: {text_secondary};"
                f"border: 1px solid {border};"
                f"border-radius: {RADIUS_LG}px;"
                f"padding: {SPACING_SM}px {SPACING_XL}px;"
                f"font-size: {STATIC_TOKENS['font.size.sm']};"
                f"font-weight: {STATIC_TOKENS['font.weight.medium']};"
                "text-align: left;"
                "min-width: 96px;"
                "}"
                "QPushButton#titleBarSearchButton:hover {"
                f"border-color: {accent};"
                f"color: {text_primary};"
                f"background-color: {surface_hover};"
                "}"
                "QPushButton#titleBarActionButton {"
                f"background-color: {surface_sunken};"
                f"color: {text_secondary};"
                f"border: 1px solid {border};"
                f"border-radius: {RADIUS_MD}px;"
                "padding: 0 10px;"
                "min-width: 36px;"
                "min-height: 32px;"
                f"font-size: {STATIC_TOKENS['font.size.md']};"
                "}"
                "QPushButton#titleBarActionButton:hover {"
                f"border-color: {accent};"
                f"color: {accent};"
                f"background-color: {surface_hover};"
                "}"
                "QLabel#titleBarAvatar {"
                f"background-color: {accent};"
                f"color: {text_inverse};"
                f"border-radius: {RADIUS_LG}px;"
                f"padding: {SPACING_SM}px {SPACING_LG}px;"
                f"font-size: {STATIC_TOKENS['font.size.sm']};"
                f"font-weight: {STATIC_TOKENS['font.weight.bold']};"
                "min-width: 44px;"
                "}"
            ),
        )


__all__ = ["TitleBar"]
