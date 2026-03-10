from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUntypedBaseClass=false

"""页面级可复用布局原语组件。"""

from typing import Final, Literal, Sequence, cast

from ...core import qt
from ...core.qt import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QVBoxLayout, QWidget, Signal
from ...core.theme.tokens import STATIC_TOKENS, TOKENS, get_token_value
from ...core.types import ThemeMode


def _px_token(name: str, fallback: int) -> int:
    """将 px token 解析为整数，保证间距与圆角统一。"""

    raw_value = STATIC_TOKENS.get(name, f"{fallback}px")
    digits = "".join(character for character in raw_value if character.isdigit())
    return int(digits) if digits else fallback


def _coerce_mode(value: object) -> ThemeMode:
    """将运行时主题值规整为 ThemeMode。"""

    if isinstance(value, ThemeMode):
        return value
    if isinstance(value, str) and value.lower() == ThemeMode.DARK.value:
        return ThemeMode.DARK
    return ThemeMode.LIGHT


def _theme_mode() -> ThemeMode:
    """尽量从应用实例中读取当前主题模式。"""

    app = QApplication.instance() if hasattr(QApplication, "instance") else None
    if app is not None:
        property_reader = getattr(app, "property", None)
        if callable(property_reader):
            for key in ("theme.mode", "theme_mode", "themeMode"):
                resolved = property_reader(key)
                if resolved is not None:
                    return _coerce_mode(resolved)
    return ThemeMode.LIGHT


def _token(name: str) -> str:
    """解析当前主题下的语义 token。"""

    return get_token_value(name, _theme_mode())


def rgba_color(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba 字符串。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


LabelTone = Literal["default", "muted", "accent", "success", "warning", "error", "info", "inverse"]
PanelVariant = Literal["default", "subtle", "highlight", "warning", "dashed"]


def qss_label_rule(
    selector: str,
    *,
    tone: LabelTone = "default",
    size_token: str = "font.size.md",
    weight_token: str | None = None,
    line_height: str | None = None,
) -> str:
    """生成统一文本规则，减少页面级重复标题/说明样式。"""

    color = {
        "default": _token("text.primary"),
        "muted": _token("text.secondary"),
        "accent": _token("brand.primary"),
        "success": _token("status.success"),
        "warning": _token("status.warning"),
        "error": _token("status.error"),
        "info": _token("status.info"),
        "inverse": _token("text.inverse"),
    }[tone]
    declarations = [
        f"color: {color};",
        f"font-size: {STATIC_TOKENS[size_token]};",
        "background: transparent;",
    ]
    if weight_token is not None:
        declarations.append(f"font-weight: {STATIC_TOKENS[weight_token]};")
    if line_height is not None:
        declarations.append(f"line-height: {line_height};")
    return f"{selector} {{ {' '.join(declarations)} }}"


def label_text_style(
    *,
    tone: LabelTone = "default",
    size_token: str = "font.size.md",
    weight_token: str | None = None,
    line_height: str | None = None,
) -> str:
    """生成可直接应用在 QLabel 上的统一文本样式。"""

    return qss_label_rule(
        "QLabel",
        tone=tone,
        size_token=size_token,
        weight_token=weight_token,
        line_height=line_height,
    )


def qss_panel_rule(
    selector: str,
    *,
    variant: PanelVariant = "default",
    radius_token: str = "radius.lg",
) -> str:
    """生成统一面板壳层规则，集中管理关键页面卡片风格。"""

    background = _token("surface.secondary")
    border_color = _token("border.default")
    border_style = "solid"

    if variant == "subtle":
        background = _token("surface.sunken")
    elif variant == "highlight":
        brand = _token("brand.primary")
        background = rgba_color(brand, 0.08)
        border_color = rgba_color(brand, 0.24)
    elif variant == "warning":
        warning = _token("status.warning")
        background = rgba_color(warning, 0.12)
        border_color = rgba_color(warning, 0.28)
    elif variant == "dashed":
        border_style = "dashed"

    return (
        f"{selector} {{"
        f"background-color: {background};"
        f"border: 1px {border_style} {border_color};"
        f"border-radius: {STATIC_TOKENS[radius_token]};"
        "}"
    )


def panel_frame_style(*, variant: PanelVariant = "default", radius_token: str = "radius.lg") -> str:
    """生成可直接应用在 QFrame 上的统一面板样式。"""

    return qss_panel_rule("QFrame", variant=variant, radius_token=radius_token)


def _call_if_available(target: object, method_name: str, *args: object) -> object | None:
    """仅在目标对象支持对应方法时再调用，兼容精简 Qt 适配层。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _set_object_name(widget: object, name: str) -> None:
    """安全设置 objectName，便于测试定位。"""

    _ = _call_if_available(widget, "setObjectName", name)


def _set_visible(widget: object, visible: bool) -> None:
    """安全切换可见性。"""

    _ = _call_if_available(widget, "setVisible", visible)


def _set_stylesheet(widget: object, stylesheet: str) -> None:
    """安全写入局部样式。"""

    _ = _call_if_available(widget, "setStyleSheet", stylesheet)


def _set_text(widget: object, text: str) -> None:
    """安全更新文本。"""

    _ = _call_if_available(widget, "setText", text)


def _set_word_wrap(widget: object, enabled: bool = True) -> None:
    """安全开启文本换行。"""

    _ = _call_if_available(widget, "setWordWrap", enabled)


def _detach_widget(widget: QWidget | None) -> None:
    """将旧部件从原父级脱离，避免重复挂载。"""

    if widget is None:
        return
    _ = _call_if_available(widget, "setParent", None)


def _label_text(widget: object) -> str:
    """兼容真实 Qt 与占位 QLabel 的文本读取。"""

    text_method = getattr(widget, "text", None)
    if callable(text_method):
        value = text_method()
        if isinstance(value, str):
            return value
    fallback = getattr(widget, "_text", "")
    return fallback if isinstance(fallback, str) else ""


def _layout_has_items(layout: object) -> bool:
    """兼容真实 Qt layout 与占位 layout 的项目数量判断。"""

    count_method = getattr(layout, "count", None)
    if callable(count_method):
        count_value = count_method()
        if isinstance(count_value, int):
            return count_value > 0
    items = getattr(layout, "_items", [])
    return bool(items)


def _normalize_ratio(split_ratio: tuple[float, float]) -> tuple[float, float]:
    """归一化分栏比例，避免异常输入。"""

    first_ratio, second_ratio = split_ratio
    total = first_ratio + second_ratio
    if total <= 0:
        return (0.3, 0.7)
    return (first_ratio / total, second_ratio / total)


def _resolve_orientation(orientation: str) -> object | None:
    """根据字符串解析 Qt 分栏方向。"""

    qt_namespace = getattr(qt, "Qt", None)
    orientation_namespace = getattr(qt_namespace, "Orientation", None)
    if orientation == "vertical":
        return getattr(orientation_namespace, "Vertical", None) or getattr(qt_namespace, "Vertical", None)
    return getattr(orientation_namespace, "Horizontal", None) or getattr(qt_namespace, "Horizontal", None)


def _apply_minimum_size(widget: QWidget, orientation: str, size: int) -> None:
    """按照分栏方向设置最小尺寸。"""

    if orientation == "vertical":
        _ = _call_if_available(widget, "setMinimumHeight", size)
        return
    _ = _call_if_available(widget, "setMinimumWidth", size)


BRAND_PRIMARY: Final[str] = TOKENS["brand.primary"].light
STATUS_ERROR: Final[str] = TOKENS["status.error"].light
SPACING_XS: Final[int] = _px_token("spacing.xs", 4)
SPACING_SM: Final[int] = _px_token("spacing.sm", 6)
SPACING_MD: Final[int] = _px_token("spacing.md", 8)
SPACING_LG: Final[int] = _px_token("spacing.lg", 12)
SPACING_XL: Final[int] = _px_token("spacing.xl", 16)
SPACING_2XL: Final[int] = _px_token("spacing.2xl", 24)
RADIUS_MD: Final[int] = _px_token("radius.md", 8)
RADIUS_LG: Final[int] = _px_token("radius.lg", 12)
PAGE_MAX_WIDTH: Final[int] = 1680
TAB_UNDERLINE_HEIGHT: Final[int] = SPACING_XS
SCROLLBAR_THICKNESS: Final[int] = SPACING_MD
DEFAULT_MIN_LEFT: Final[int] = _px_token("layout.sidebar_width.canonical", 280)
DEFAULT_MIN_RIGHT: Final[int] = 480


class PageContainer(QWidget):
    """页面内容容器，统一标题区、操作区与内容宽度约束。"""

    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        actions: Sequence[QWidget] | None = None,
        max_width: int = PAGE_MAX_WIDTH,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _set_object_name(self, "pageContainer")

        self._max_width: int = max_width

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(SPACING_2XL, SPACING_2XL, SPACING_2XL, SPACING_2XL)
        root_layout.setSpacing(0)

        self._content_shell: QWidget = QWidget(self)
        _set_object_name(self._content_shell, "pageContainerShell")
        _ = _call_if_available(self._content_shell, "setMaximumWidth", self._max_width)
        root_layout.addWidget(self._content_shell)

        shell_layout = QVBoxLayout(self._content_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(SPACING_2XL)

        self._header: QWidget = QWidget(self._content_shell)
        _set_object_name(self._header, "pageContainerHeader")
        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_XL)

        self._header_text: QWidget = QWidget(self._header)
        _set_object_name(self._header_text, "pageContainerHeaderText")
        header_text_layout = QVBoxLayout(self._header_text)
        header_text_layout.setContentsMargins(0, 0, 0, 0)
        header_text_layout.setSpacing(SPACING_SM)

        self._title_label: QLabel = QLabel(title or "", self._header_text)
        _set_object_name(self._title_label, "pageContainerTitle")
        self._description_label: QLabel = QLabel(description or "", self._header_text)
        _set_object_name(self._description_label, "pageContainerDescription")
        _set_word_wrap(self._description_label)

        _set_stylesheet(
            self._title_label,
            (
                f"QLabel#pageContainerTitle {{"
                f"font-size: {STATIC_TOKENS['font.size.xxl']};"
                f"font-weight: {STATIC_TOKENS['font.weight.bold']};"
                "background: transparent;"
                "}"
            ),
        )
        _set_stylesheet(
            self._description_label,
            (
                f"QLabel#pageContainerDescription {{"
                f"font-size: {STATIC_TOKENS['font.size.md']};"
                "color: palette(mid);"
                "background: transparent;"
                "}"
            ),
        )

        header_text_layout.addWidget(self._title_label)
        header_text_layout.addWidget(self._description_label)

        self._actions_host: QWidget = QWidget(self._header)
        _set_object_name(self._actions_host, "pageContainerActions")
        self.actions_layout: QHBoxLayout = QHBoxLayout(self._actions_host)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_layout.setSpacing(SPACING_MD)

        header_layout.addWidget(self._header_text)
        header_layout.addStretch(1)
        header_layout.addWidget(self._actions_host)

        self._content_host: QWidget = QWidget(self._content_shell)
        _set_object_name(self._content_host, "pageContainerBody")
        self.content_layout: QVBoxLayout = QVBoxLayout(self._content_host)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(SPACING_2XL)

        shell_layout.addWidget(self._header)
        shell_layout.addWidget(self._content_host)
        shell_layout.addStretch(1)

        for action in actions or ():
            self.add_action(action)

        self.set_header(title=title, description=description)

    def set_header(self, title: str | None = None, description: str | None = None) -> None:
        """更新页面头部文案，并自动控制头部显隐。"""

        resolved_title = title or ""
        resolved_description = description or ""
        _set_text(self._title_label, resolved_title)
        _set_text(self._description_label, resolved_description)
        _set_visible(self._title_label, bool(resolved_title))
        _set_visible(self._description_label, bool(resolved_description))
        self._update_header_visibility()

    def add_action(self, widget: QWidget) -> None:
        """向头部右侧添加操作控件。"""

        self.actions_layout.addWidget(widget)
        self._update_header_visibility()

    def add_widget(self, widget: QWidget) -> None:
        """向内容区域添加子部件。"""

        self.content_layout.addWidget(widget)

    def _update_header_visibility(self) -> None:
        """当标题、描述、操作均为空时隐藏头部。"""

        title_text = _label_text(self._title_label)
        description_text = _label_text(self._description_label)
        has_actions = _layout_has_items(self.actions_layout)
        _set_visible(self._header, bool(title_text or description_text or has_actions))


class SplitPanel(QWidget):
    """双栏分割布局，内部优先使用 QSplitter。"""

    def __init__(
        self,
        orientation: str = "horizontal",
        split_ratio: tuple[float, float] = (0.3, 0.7),
        minimum_sizes: tuple[int, int] = (DEFAULT_MIN_LEFT, DEFAULT_MIN_RIGHT),
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _set_object_name(self, "splitPanel")

        self._orientation: str = "vertical" if orientation == "vertical" else "horizontal"
        self._split_ratio: tuple[float, float] = _normalize_ratio(split_ratio)
        self._minimum_sizes: tuple[int, int] = minimum_sizes
        self._first_widget: QWidget | None = None
        self._second_widget: QWidget | None = None

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        splitter_class = getattr(qt, "QSplitter", None)
        splitter_instance = splitter_class(self) if callable(splitter_class) else QWidget(self)
        self._splitter: QWidget = cast(QWidget, splitter_instance)
        _set_object_name(self._splitter, "splitPanelCore")
        root_layout.addWidget(self._splitter)

        self.first_pane: QWidget = QWidget(self._splitter)
        _set_object_name(self.first_pane, "splitPanelFirstPane")
        self.first_layout: QVBoxLayout = QVBoxLayout(self.first_pane)
        self.first_layout.setContentsMargins(0, 0, 0, 0)
        self.first_layout.setSpacing(0)

        self.second_pane: QWidget = QWidget(self._splitter)
        _set_object_name(self.second_pane, "splitPanelSecondPane")
        self.second_layout: QVBoxLayout = QVBoxLayout(self.second_pane)
        self.second_layout.setContentsMargins(0, 0, 0, 0)
        self.second_layout.setSpacing(0)

        resolved_orientation = _resolve_orientation(self._orientation)
        if resolved_orientation is not None:
            _ = _call_if_available(self._splitter, "setOrientation", resolved_orientation)

        _ = _call_if_available(self._splitter, "setChildrenCollapsible", False)
        _ = _call_if_available(self._splitter, "setHandleWidth", SPACING_MD)
        _set_stylesheet(
            self._splitter,
            (
                "QSplitter#splitPanelCore::handle {"
                "background-color: palette(midlight);"
                f"border-radius: {RADIUS_MD}px;"
                "}"
                "QSplitter#splitPanelCore::handle:hover {"
                f"background-color: {BRAND_PRIMARY};"
                "}"
            ),
        )

        if _call_if_available(self._splitter, "addWidget", self.first_pane) is None:
            fallback_layout = QVBoxLayout(self._splitter) if self._orientation == "vertical" else QHBoxLayout(self._splitter)
            fallback_layout.setContentsMargins(0, 0, 0, 0)
            fallback_layout.setSpacing(SPACING_MD)
            fallback_layout.addWidget(self.first_pane)
            fallback_layout.addWidget(self.second_pane)
        else:
            _ = _call_if_available(self._splitter, "addWidget", self.second_pane)

        self._apply_minimum_sizes()
        self._apply_split_ratio()

    def set_widgets(self, first_widget: QWidget, second_widget: QWidget) -> None:
        """一次性设置左右/上下两个面板内容。"""

        self.set_first_widget(first_widget)
        self.set_second_widget(second_widget)

    def set_first_widget(self, widget: QWidget) -> None:
        """设置第一面板内容。"""

        _detach_widget(self._first_widget)
        self._first_widget = widget
        _apply_minimum_size(widget, self._orientation, self._minimum_sizes[0])
        self.first_layout.addWidget(widget)

    def set_second_widget(self, widget: QWidget) -> None:
        """设置第二面板内容。"""

        _detach_widget(self._second_widget)
        self._second_widget = widget
        _apply_minimum_size(widget, self._orientation, self._minimum_sizes[1])
        self.second_layout.addWidget(widget)

    def set_split_ratio(self, first_ratio: float, second_ratio: float) -> None:
        """动态更新分栏比例。"""

        self._split_ratio = _normalize_ratio((first_ratio, second_ratio))
        self._apply_split_ratio()

    def _apply_minimum_sizes(self) -> None:
        """将最小尺寸应用到两个分栏容器。"""

        _apply_minimum_size(self.first_pane, self._orientation, self._minimum_sizes[0])
        _apply_minimum_size(self.second_pane, self._orientation, self._minimum_sizes[1])

    def _apply_split_ratio(self) -> None:
        """将比例映射为 splitter size hint。"""

        first_size = max(1, int(self._split_ratio[0] * 1000))
        second_size = max(1, int(self._split_ratio[1] * 1000))
        _ = _call_if_available(self._splitter, "setStretchFactor", 0, first_size)
        _ = _call_if_available(self._splitter, "setStretchFactor", 1, second_size)
        _ = _call_if_available(self._splitter, "setSizes", [first_size, second_size])


class TabBar(QWidget):
    """页内标签切换组件，内置内容堆栈与 TikTok 风格激活态。"""

    tab_changed: Signal = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _set_object_name(self, "tabBar")

        self._buttons: list[QPushButton] = []
        self._current_index: int = -1

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(SPACING_LG)

        self._tab_strip: QWidget = QWidget(self)
        _set_object_name(self._tab_strip, "tabBarStrip")
        self._tab_strip_layout: QHBoxLayout = QHBoxLayout(self._tab_strip)
        self._tab_strip_layout.setContentsMargins(0, 0, 0, 0)
        self._tab_strip_layout.setSpacing(SPACING_SM)

        self._stack: QStackedWidget = QStackedWidget(self)
        _set_object_name(self._stack, "tabBarStack")

        root_layout.addWidget(self._tab_strip)
        root_layout.addWidget(self._stack)

    @property
    def stacked_widget(self) -> QStackedWidget:
        """暴露内部 QStackedWidget，便于复杂场景扩展。"""

        return self._stack

    def add_tab(self, title: str, widget: QWidget) -> int:
        """新增一个标签及其对应页面。"""

        index = len(self._buttons)
        button = QPushButton(title, self._tab_strip)
        _set_object_name(button, f"tabBarItem{index}")
        _ = _call_if_available(button, "setCheckable", True)
        button.clicked.connect(lambda _checked=False, tab_index=index: self.set_current(tab_index))

        self._buttons.append(button)
        self._tab_strip_layout.addWidget(button)
        _ = self._stack.addWidget(widget)
        self._refresh_tab_styles()

        if index == 0:
            self.set_current(0)

        return index

    def set_current(self, index: int) -> None:
        """切换当前标签。"""

        if index < 0 or index >= len(self._buttons):
            return

        changed = index != self._current_index
        self._current_index = index
        self._stack.setCurrentIndex(index)
        self._refresh_tab_styles()

        if changed:
            self.tab_changed.emit(index)

    def _refresh_tab_styles(self) -> None:
        """根据当前索引刷新每个标签的视觉状态。"""

        for index, button in enumerate(self._buttons):
            is_active = index == self._current_index
            _ = _call_if_available(button, "setChecked", is_active)

            font_weight = STATIC_TOKENS["font.weight.bold"] if is_active else STATIC_TOKENS["font.weight.semibold"]
            color = BRAND_PRIMARY if is_active else "palette(mid)"
            underline = BRAND_PRIMARY if is_active else "transparent"
            background = "rgba(0, 242, 234, 0.08)" if is_active else "transparent"

            _set_stylesheet(
                button,
                (
                    "QPushButton {"
                    "background: transparent;"
                    "border: none;"
                    f"border-bottom: {TAB_UNDERLINE_HEIGHT}px solid {underline};"
                    f"border-radius: {RADIUS_MD}px;"
                    f"padding: {SPACING_LG}px {SPACING_XL}px {SPACING_MD}px {SPACING_XL}px;"
                    f"font-size: {STATIC_TOKENS['font.size.md']};"
                    f"font-weight: {font_weight};"
                    f"color: {color};"
                    f"background-color: {background};"
                    "text-align: left;"
                    "}"
                    "QPushButton:hover {"
                    "background-color: rgba(0, 242, 234, 0.10);"
                    "color: palette(windowText);"
                    "}"
                ),
            )


class ThemedScrollArea(QWidget):
    """统一滚动区域外观，封装主题一致的滚动条样式。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _set_object_name(self, "themedScroll")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        scroll_area_class = getattr(qt, "QScrollArea", None)
        scroll_area_instance = scroll_area_class(self) if callable(scroll_area_class) else QWidget(self)
        self._scroll_area: QWidget = cast(QWidget, scroll_area_instance)
        _set_object_name(self._scroll_area, "themedScrollCore")
        root_layout.addWidget(self._scroll_area)

        self._content_widget: QWidget = QWidget(self)
        _set_object_name(self._content_widget, "themedScrollContent")
        self.content_layout: QVBoxLayout = QVBoxLayout(self._content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(SPACING_LG)

        _ = _call_if_available(self._scroll_area, "setWidgetResizable", True)
        frame_shape_namespace: object | None = getattr(QFrame, "Shape", None)
        no_frame: object | None = getattr(frame_shape_namespace, "NoFrame", None)
        if no_frame is not None:
            _ = _call_if_available(self._scroll_area, "setFrameShape", no_frame)

        if _call_if_available(self._scroll_area, "setWidget", self._content_widget) is None:
            fallback_layout = QVBoxLayout(self._scroll_area)
            fallback_layout.setContentsMargins(0, 0, 0, 0)
            fallback_layout.setSpacing(0)
            fallback_layout.addWidget(self._content_widget)

        _set_stylesheet(
            self,
            (
                "QWidget#themedScroll, QWidget#themedScrollContent {"
                "background: transparent;"
                "border: none;"
                "}"
                f"QWidget#themedScroll QScrollBar:vertical {{width: {SCROLLBAR_THICKNESS}px; margin: {SPACING_XS}px 0; background: transparent;}}"
                f"QWidget#themedScroll QScrollBar:horizontal {{height: {SCROLLBAR_THICKNESS}px; margin: 0 {SPACING_XS}px; background: transparent;}}"
                "QWidget#themedScroll QScrollBar::handle:vertical, QWidget#themedScroll QScrollBar::handle:horizontal {"
                f"background-color: {BRAND_PRIMARY};"
                f"border-radius: {RADIUS_MD}px;"
                "min-height: 32px;"
                "min-width: 32px;"
                "}"
                "QWidget#themedScroll QScrollBar::add-line, QWidget#themedScroll QScrollBar::sub-line, QWidget#themedScroll QScrollBar::add-page, QWidget#themedScroll QScrollBar::sub-page {"
                "background: transparent;"
                "border: none;"
                "}"
            ),
        )

    def add_widget(self, widget: QWidget) -> None:
        """向滚动内容区添加子部件。"""

        self.content_layout.addWidget(widget)

    def set_content_widget(self, widget: QWidget) -> None:
        """设置滚动区域的主内容部件。"""

        _detach_widget(widget)
        self.content_layout.addWidget(widget)


class ContentSection(QFrame):
    """带折叠能力的内容分组区块。"""

    def __init__(
        self,
        title: str,
        icon: str | None = None,
        collapsed: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _set_object_name(self, "contentSection")
        _ = _call_if_available(self, "setProperty", "variant", "card")

        self._title: str = title
        self._icon: str | None = icon
        self._collapsed: bool = collapsed

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_LG)
        root_layout.setSpacing(SPACING_LG)

        self._header_button: QPushButton = QPushButton("", self)
        _set_object_name(self._header_button, "contentSectionHeader")
        self._header_button.clicked.connect(self.toggle)
        _set_stylesheet(
            self._header_button,
            (
                "QPushButton#contentSectionHeader {"
                "background: transparent;"
                "border: none;"
                f"padding: {SPACING_XS}px 0;"
                f"font-size: {STATIC_TOKENS['font.size.lg']};"
                f"font-weight: {STATIC_TOKENS['font.weight.semibold']};"
                "color: palette(windowText);"
                "text-align: left;"
                "}"
                "QPushButton#contentSectionHeader:hover {"
                "color: palette(highlight);"
                "}"
            ),
        )

        self._content_host: QWidget = QWidget(self)
        _set_object_name(self._content_host, "contentSectionBody")
        self.content_layout: QVBoxLayout = QVBoxLayout(self._content_host)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(SPACING_LG)

        self._separator: QFrame = QFrame(self)
        _set_object_name(self._separator, "contentSectionSeparator")
        _ = _call_if_available(self._separator, "setFixedHeight", 1)
        _set_stylesheet(self._separator, "QFrame#contentSectionSeparator { background-color: palette(midlight); border: none; }")

        root_layout.addWidget(self._header_button)
        root_layout.addWidget(self._content_host)
        root_layout.addWidget(self._separator)

        self._refresh_header_text()
        self.set_collapsed(collapsed)

    def add_widget(self, widget: QWidget) -> None:
        """向分组内容区添加子部件。"""

        self.content_layout.addWidget(widget)

    def set_collapsed(self, collapsed: bool) -> None:
        """更新折叠状态。"""

        self._collapsed = collapsed
        _set_visible(self._content_host, not collapsed)
        self._refresh_header_text()

    def toggle(self) -> None:
        """切换折叠/展开状态。"""

        self.set_collapsed(not self._collapsed)

    def _refresh_header_text(self) -> None:
        """同步箭头、图标与标题文本。"""

        arrow = "▸" if self._collapsed else "▾"
        icon_prefix = f"{self._icon}  " if self._icon else ""
        _set_text(self._header_button, f"{arrow}  {icon_prefix}{self._title}")


class FormGroup(QWidget):
    """表单字段分组，统一标签、说明与必填标识样式。"""

    def __init__(
        self,
        label: str,
        field_widget: QWidget | None = None,
        description: str | None = None,
        required: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _set_object_name(self, "formGroup")

        self._field_widget: QWidget | None = None
        self._label: str = label
        self._description: str = description or ""
        self._required: bool = required

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(SPACING_SM)

        self._label_widget: QLabel = QLabel("", self)
        _set_object_name(self._label_widget, "formGroupLabel")
        _set_stylesheet(
            self._label_widget,
            (
                f"QLabel#formGroupLabel {{font-size: {STATIC_TOKENS['font.size.sm']};"
                f"font-weight: {STATIC_TOKENS['font.weight.bold']};"
                "color: palette(windowText);"
                "background: transparent;}"
            ),
        )

        self._description_widget: QLabel = QLabel(self._description, self)
        _set_object_name(self._description_widget, "formGroupDescription")
        _set_word_wrap(self._description_widget)
        _set_stylesheet(
            self._description_widget,
            (
                f"QLabel#formGroupDescription {{font-size: {STATIC_TOKENS['font.size.sm']};"
                "color: palette(mid);"
                "background: transparent;}"
            ),
        )

        self._field_host: QWidget = QWidget(self)
        _set_object_name(self._field_host, "formGroupFieldHost")
        self.field_layout: QVBoxLayout = QVBoxLayout(self._field_host)
        self.field_layout.setContentsMargins(0, 0, 0, 0)
        self.field_layout.setSpacing(SPACING_SM)

        root_layout.addWidget(self._label_widget)
        root_layout.addWidget(self._description_widget)
        root_layout.addWidget(self._field_host)

        self._refresh_label()
        _set_visible(self._description_widget, bool(self._description))

        if field_widget is not None:
            self.set_field_widget(field_widget)

    def set_field_widget(self, widget: QWidget) -> None:
        """设置当前表单控件。"""

        _detach_widget(self._field_widget)
        self._field_widget = widget
        self.field_layout.addWidget(widget)

    def set_description(self, description: str | None) -> None:
        """更新说明文案。"""

        self._description = description or ""
        _set_text(self._description_widget, self._description)
        _set_visible(self._description_widget, bool(self._description))

    def set_required(self, required: bool) -> None:
        """更新必填状态。"""

        self._required = required
        self._refresh_label()

    def _refresh_label(self) -> None:
        """更新标签文本与必填星标。"""

        if self._required:
            _set_text(self._label_widget, f'{self._label} <span style="color: {STATUS_ERROR};">*</span>')
            return
        _set_text(self._label_widget, self._label)


__all__ = [
    "ContentSection",
    "FormGroup",
    "PageContainer",
    "SplitPanel",
    "TabBar",
    "ThemedScrollArea",
    "label_text_style",
    "panel_frame_style",
    "qss_label_rule",
    "qss_panel_rule",
    "rgba_color",
]
