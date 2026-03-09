# pyright: basic, reportMissingImports=false, reportGeneralTypeIssues=false, reportArgumentType=false, reportIncompatibleMethodOverride=false

from __future__ import annotations

"""操作区使用的主题按钮组件。"""

from ...core.theme.tokens import STATIC_TOKENS, get_token_value
from ...core.types import ThemeMode

try:
    from PySide6.QtWidgets import QApplication, QPushButton, QWidget
except ImportError:
    from ...core.qt import QApplication, QPushButton, QWidget


def _call(target: object, method_name: str, *args: object) -> None:
    """安全调用可能不存在的 Qt 方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        method(*args)


def _coerce_mode(value: object) -> ThemeMode:
    """将运行时主题值归一化。"""

    if isinstance(value, ThemeMode):
        return value
    if isinstance(value, str) and value.lower() == ThemeMode.DARK.value:
        return ThemeMode.DARK
    return ThemeMode.LIGHT


def _theme_mode() -> ThemeMode:
    """尽量从应用实例读取当前主题模式。"""

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
    """读取当前主题 token。"""

    return get_token_value(name, _theme_mode())


def _px(name: str) -> int:
    """将 px token 转成整数。"""

    return int(STATIC_TOKENS[name].replace("px", ""))


RADIUS_MD = _px("button.radius")
HEIGHT_SM = _px("button.height.sm")
HEIGHT_MD = _px("button.height.md")
HEIGHT_LG = _px("button.height.lg")
SPACE_MD = _px("spacing.md")
SPACE_LG = _px("spacing.lg")
SPACE_XL = _px("spacing.xl")
SPACE_2XL = _px("spacing.2xl")


class _BaseThemedButton(QPushButton):
    """主题按钮基类。"""

    def __init__(
        self,
        text: str,
        parent: QWidget | None = None,
        *,
        object_name: str,
        icon_text: str | None = None,
        min_height: int = HEIGHT_MD,
        min_width: int | None = None,
    ) -> None:
        self._raw_text = text
        self._icon_text = icon_text or ""
        super().__init__(self._compose_text(), parent)
        _call(self, "setObjectName", object_name)
        _call(self, "setMinimumHeight", min_height)
        if min_width is not None:
            _call(self, "setMinimumWidth", min_width)
        self._apply_theme()

    def set_icon_text(self, icon_text: str | None) -> None:
        """设置前缀图标文本。"""

        self._icon_text = icon_text or ""
        _call(self, "setText", self._compose_text())

    def set_label_text(self, text: str) -> None:
        """设置按钮主文案。"""

        self._raw_text = text
        _call(self, "setText", self._compose_text())

    def _compose_text(self) -> str:
        prefix = f"{self._icon_text} " if self._icon_text else ""
        return f"{prefix}{self._raw_text}".strip()

    def _apply_theme(self) -> None:
        """由子类实现具体主题样式。"""

        return None


class PrimaryButton(_BaseThemedButton):
    """主操作按钮，强调品牌主色与高对比反馈。"""

    def __init__(self, text: str = "主要操作", parent: QWidget | None = None, icon_text: str | None = None) -> None:
        super().__init__(
            text,
            parent,
            object_name="primaryButton",
            icon_text=icon_text,
            min_height=HEIGHT_MD,
        )

    def _apply_theme(self) -> None:
        primary = _token("brand.primary")
        hover = _token("brand.primary_hover")
        pressed = _token("brand.primary_pressed")
        text_color = _token("text.inverse")
        _call(
            self,
            "setStyleSheet",
            f"""
            QPushButton#primaryButton {{
                background-color: {primary};
                color: {text_color};
                border: 1px solid {primary};
                border-radius: {RADIUS_MD}px;
                padding: {SPACE_MD}px {SPACE_2XL}px;
                font-size: {STATIC_TOKENS['font.size.md']};
                font-weight: {STATIC_TOKENS['font.weight.bold']};
                min-height: {HEIGHT_MD}px;
            }}
            QPushButton#primaryButton:hover {{
                background-color: {hover};
                border-color: {hover};
            }}
            QPushButton#primaryButton:pressed {{
                background-color: {pressed};
                border-color: {pressed};
            }}
            QPushButton#primaryButton:disabled {{
                background-color: {_token('surface.tertiary')};
                border-color: {_token('border.default')};
                color: {_token('text.disabled')};
            }}
            """,
        )


class SecondaryButton(_BaseThemedButton):
    """次级操作按钮，采用透明描边样式。"""

    def __init__(self, text: str = "次级操作", parent: QWidget | None = None, icon_text: str | None = None) -> None:
        super().__init__(
            text,
            parent,
            object_name="secondaryButton",
            icon_text=icon_text,
            min_height=HEIGHT_MD,
        )

    def _apply_theme(self) -> None:
        primary = _token("brand.primary")
        _call(
            self,
            "setStyleSheet",
            f"""
            QPushButton#secondaryButton {{
                background-color: transparent;
                color: {primary};
                border: 1px solid {primary};
                border-radius: {RADIUS_MD}px;
                padding: {SPACE_MD}px {SPACE_XL}px;
                font-size: {STATIC_TOKENS['font.size.md']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
                min-height: {HEIGHT_MD}px;
            }}
            QPushButton#secondaryButton:hover {{
                background-color: rgba(0,242,234,0.10);
            }}
            QPushButton#secondaryButton:pressed {{
                background-color: rgba(0,242,234,0.16);
            }}
            QPushButton#secondaryButton:disabled {{
                color: {_token('text.disabled')};
                border-color: {_token('border.default')};
            }}
            """,
        )


class IconButton(_BaseThemedButton):
    """仅展示图标文本的方形按钮，依赖 tooltip 提示语义。"""

    def __init__(self, icon_text: str = "⋯", tooltip: str = "更多操作", parent: QWidget | None = None) -> None:
        super().__init__(
            icon_text,
            parent,
            object_name="iconButton",
            min_height=HEIGHT_MD,
            min_width=HEIGHT_MD,
        )
        _call(self, "setFixedSize", HEIGHT_MD, HEIGHT_MD)
        _call(self, "setToolTip", tooltip)

    def _apply_theme(self) -> None:
        surface = _token("surface.secondary")
        border = _token("border.default")
        hover = _token("surface.tertiary")
        _call(
            self,
            "setStyleSheet",
            f"""
            QPushButton#iconButton {{
                background-color: {surface};
                color: {_token('text.primary')};
                border: 1px solid {border};
                border-radius: {RADIUS_MD}px;
                padding: 0;
                font-size: {STATIC_TOKENS['font.size.lg']};
                font-weight: {STATIC_TOKENS['font.weight.medium']};
                min-width: {HEIGHT_MD}px;
                min-height: {HEIGHT_MD}px;
            }}
            QPushButton#iconButton:hover {{
                background-color: {hover};
                border-color: {_token('brand.primary')};
            }}
            QPushButton#iconButton:pressed {{
                background-color: {_token('surface.sunken')};
            }}
            """,
        )


class DangerButton(_BaseThemedButton):
    """危险操作按钮，用于删除或不可逆行为。"""

    def __init__(self, text: str = "危险操作", parent: QWidget | None = None, icon_text: str | None = None) -> None:
        super().__init__(
            text,
            parent,
            object_name="dangerButton",
            icon_text=icon_text,
            min_height=HEIGHT_MD,
        )

    def _apply_theme(self) -> None:
        danger = _token("status.error")
        _call(
            self,
            "setStyleSheet",
            f"""
            QPushButton#dangerButton {{
                background-color: {danger};
                color: #FFFFFF;
                border: 1px solid {danger};
                border-radius: {RADIUS_MD}px;
                padding: {SPACE_MD}px {SPACE_XL}px;
                font-size: {STATIC_TOKENS['font.size.md']};
                font-weight: {STATIC_TOKENS['font.weight.bold']};
                min-height: {HEIGHT_MD}px;
            }}
            QPushButton#dangerButton:hover {{
                background-color: rgba(239,68,68,0.90);
                border-color: rgba(239,68,68,0.90);
            }}
            QPushButton#dangerButton:pressed {{
                background-color: rgba(239,68,68,0.80);
                border-color: rgba(239,68,68,0.80);
            }}
            """,
        )


class FloatingActionButton(_BaseThemedButton):
    """圆形悬浮主操作按钮，适合放在右下角。"""

    def __init__(self, icon_text: str = "+", tooltip: str = "新增", parent: QWidget | None = None) -> None:
        super().__init__(
            icon_text,
            parent,
            object_name="fabButton",
            min_height=HEIGHT_LG,
            min_width=HEIGHT_LG,
        )
        _call(self, "setFixedSize", HEIGHT_LG, HEIGHT_LG)
        _call(self, "setToolTip", tooltip)

    def _apply_theme(self) -> None:
        primary = _token("brand.primary")
        _call(
            self,
            "setStyleSheet",
            f"""
            QPushButton#fabButton {{
                background-color: {primary};
                color: {_token('text.inverse')};
                border: 1px solid {primary};
                border-radius: {HEIGHT_LG // 2}px;
                padding: 0;
                font-size: {STATIC_TOKENS['font.size.xl']};
                font-weight: {STATIC_TOKENS['font.weight.bold']};
                min-width: {HEIGHT_LG}px;
                min-height: {HEIGHT_LG}px;
            }}
            QPushButton#fabButton:hover {{
                background-color: {_token('brand.primary_hover')};
                border-color: {_token('brand.primary_hover')};
            }}
            QPushButton#fabButton:pressed {{
                background-color: {_token('brand.primary_pressed')};
                border-color: {_token('brand.primary_pressed')};
            }}
            """,
        )


class GhostButton(SecondaryButton):
    """兼容旧命名的次级按钮。"""

    def __init__(self, text: str = "次级操作", parent: QWidget | None = None) -> None:
        super().__init__(text=text, parent=parent)


__all__ = [
    "DangerButton",
    "FloatingActionButton",
    "GhostButton",
    "IconButton",
    "PrimaryButton",
    "SecondaryButton",
]
