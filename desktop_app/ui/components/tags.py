# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false, reportAssignmentType=false

from __future__ import annotations

"""主题化标签与徽标组件。"""

from typing import Literal

from .inputs import (
    BUTTON_HEIGHT,
    RADIUS_LG,
    RADIUS_MD,
    RADIUS_SM,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    Qt,
    Signal,
    QVBoxLayout,
    QWidget,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)

BadgeTone = Literal["success", "warning", "error", "info", "brand", "neutral"]


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba 字符串。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _tone_colors(tone: BadgeTone) -> tuple[str, str, str]:
    """返回 tone 对应的前景、背景与边框颜色。"""

    colors = _palette()
    mapping: dict[BadgeTone, tuple[str, str, str]] = {
        "success": (_token("status.success"), _rgba(_token("status.success"), 0.14), _rgba(_token("status.success"), 0.26)),
        "warning": (_token("status.warning"), _rgba(_token("status.warning"), 0.16), _rgba(_token("status.warning"), 0.26)),
        "error": (_token("status.error"), _rgba(_token("status.error"), 0.14), _rgba(_token("status.error"), 0.28)),
        "info": (_token("status.info"), _rgba(_token("status.info"), 0.14), _rgba(_token("status.info"), 0.24)),
        "brand": (_token("brand.primary"), _rgba(_token("brand.primary"), 0.12), _rgba(_token("brand.primary"), 0.22)),
        "neutral": (colors.text_muted, colors.tag_background, colors.border),
    }
    return mapping[tone]


class StatusBadge(QLabel):
    """状态徽标，适用于成功、预警、异常等语义状态。"""

    def __init__(self, text: str = "运行正常", tone: BadgeTone = "success", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self._tone: BadgeTone = tone
        _call(self, "setObjectName", "statusBadge")
        _call(self, "setAlignment", getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignCenter", 0))
        self._apply_styles()

    def set_tone(self, tone: BadgeTone) -> None:
        """更新徽标色调。"""

        self._tone = tone
        self._apply_styles()

    def tone(self) -> BadgeTone:
        """返回当前色调。"""

        return self._tone

    def _apply_styles(self) -> None:
        foreground, background, border = _tone_colors(self._tone)
        _call(
            self,
            "setStyleSheet",
            f"""
            QLabel#statusBadge {{
                color: {foreground};
                background-color: {background};
                border: 1px solid {border};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_XS}px {SPACING_LG}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
                min-height: {BUTTON_HEIGHT - SPACING_SM}px;
            }}
            """,
        )


class TagChip(QFrame):
    """圆角标签芯片，支持可选关闭动作。"""

    close_requested = Signal(str)

    def __init__(
        self,
        text: str = "TikTok Shop",
        *,
        tone: BadgeTone = "neutral",
        closable: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._text = text
        self._tone: BadgeTone = tone
        self._closable = closable
        _call(self, "setObjectName", "tagChip")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_XS, SPACING_SM if closable else SPACING_LG, SPACING_XS)
        layout.setSpacing(SPACING_XS)

        self._label = QLabel(text, self)
        _call(self._label, "setObjectName", "tagChipLabel")

        self._close_button = QPushButton("×", self)
        _call(self._close_button, "setObjectName", "tagChipClose")
        _call(self._close_button, "setToolTip", "移除标签")
        _call(self._close_button, "setVisible", closable)
        _call(self._close_button, "setFixedSize", 18, 18)
        _connect(getattr(self._close_button, "clicked", None), lambda: self.close_requested.emit(self._text))

        layout.addWidget(self._label)
        layout.addWidget(self._close_button)
        self._apply_styles()

    def text(self) -> str:
        """返回芯片文本。"""

        return self._text

    def set_text(self, text: str) -> None:
        """更新芯片文本。"""

        self._text = text
        _call(self._label, "setText", text)

    def set_tone(self, tone: BadgeTone) -> None:
        """更新芯片色调。"""

        self._tone = tone
        self._apply_styles()

    def _apply_styles(self) -> None:
        foreground, background, border = _tone_colors(self._tone)
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QFrame#tagChip {{
                background-color: {background};
                border: 1px solid {border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#tagChipLabel {{
                background: transparent;
                color: {foreground};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.medium')};
            }}
            QPushButton#tagChipClose {{
                background: transparent;
                border: none;
                color: {colors.text_muted};
                border-radius: {RADIUS_SM}px;
                padding: 0;
                min-width: 18px;
                min-height: 18px;
                font-size: {_static_token('font.size.sm')};
            }}
            QPushButton#tagChipClose:hover {{
                background-color: {colors.surface};
                color: {colors.text};
            }}
            """,
        )


class StatsBadge(QFrame):
    """紧凑型数据徽标，展示图标、数值与标签。"""

    def __init__(
        self,
        label: str = "CTR",
        value: str = "3.8%",
        icon: str = "◎",
        tone: BadgeTone = "brand",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tone: BadgeTone = tone
        _call(self, "setObjectName", "statsBadge")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING_MD, SPACING_SM, SPACING_MD, SPACING_SM)
        layout.setSpacing(SPACING_SM)

        self._icon_label = QLabel(icon, self)
        _call(self._icon_label, "setObjectName", "statsBadgeIcon")

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(0)

        self._value_label = QLabel(value, self)
        _call(self._value_label, "setObjectName", "statsBadgeValue")

        self._text_label = QLabel(label, self)
        _call(self._text_label, "setObjectName", "statsBadgeText")

        text_column.addWidget(self._value_label)
        text_column.addWidget(self._text_label)

        layout.addWidget(self._icon_label)
        layout.addLayout(text_column)
        self._apply_styles()

    def set_value(self, value: str) -> None:
        """更新数值文案。"""

        _call(self._value_label, "setText", value)

    def set_label(self, label: str) -> None:
        """更新标签文案。"""

        _call(self._text_label, "setText", label)

    def _apply_styles(self) -> None:
        foreground, background, border = _tone_colors(self._tone)
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QFrame#statsBadge {{
                background-color: {background};
                border: 1px solid {border};
                border-radius: {RADIUS_MD}px;
            }}
            QLabel#statsBadgeIcon {{
                min-width: {SPACING_XL + SPACING_LG}px;
                max-width: {SPACING_XL + SPACING_LG}px;
                min-height: {SPACING_XL + SPACING_LG}px;
                max-height: {SPACING_XL + SPACING_LG}px;
                border-radius: {RADIUS_MD}px;
                background-color: {colors.surface};
                color: {foreground};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#statsBadgeValue {{
                color: {colors.text};
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#statsBadgeText {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.xs')};
            }}
            """,
        )


class CountBadge(QLabel):
    """红色圆形数量徽标，常用于提醒与未处理数量。"""

    def __init__(self, count: int = 3, parent: QWidget | None = None) -> None:
        self._count = max(0, count)
        super().__init__(self._display_text(self._count), parent)
        _call(self, "setObjectName", "countBadge")
        _call(self, "setAlignment", getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignCenter", 0))
        _call(self, "setMinimumSize", 22, 22)
        self._apply_styles()

    @staticmethod
    def _display_text(count: int) -> str:
        """格式化数量显示。"""

        return "99+" if count > 99 else str(count)

    def set_count(self, count: int) -> None:
        """更新数量。"""

        self._count = max(0, count)
        _call(self, "setText", self._display_text(self._count))

    def count(self) -> int:
        """返回当前数量。"""

        return self._count

    def _apply_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QLabel#countBadge {{
                background-color: {_token('status.error')};
                color: {colors.surface};
                border: 1px solid {_rgba(_token('status.error'), 0.34)};
                border-radius: {SPACING_XL + SPACING_XS}px;
                padding: 0 {SPACING_SM}px;
                font-size: {_static_token('font.size.xs')};
                font-weight: {_static_token('font.weight.bold')};
                min-width: 22px;
                min-height: 22px;
            }}
            """,
        )


StatusTag = StatusBadge


__all__ = [
    "CountBadge",
    "StatsBadge",
    "StatusBadge",
    "StatusTag",
    "TagChip",
]
