# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false

from __future__ import annotations

"""主题化数据卡片组件。"""

from typing import Iterable, Literal, Sequence

from .charts import MiniSparkline
from .inputs import (
    BUTTON_HEIGHT,
    RADIUS_LG,
    SPACING_2XL,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    _call,
    _palette,
    _static_token,
    _token,
)
from .tags import BadgeTone, StatusBadge, StatsBadge, TagChip

TrendDirection = Literal["up", "down", "flat"]


def _rgba(hex_color: str, alpha: float) -> str:
    """十六进制颜色转 rgba。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _trend_meta(direction: TrendDirection) -> tuple[str, str, str]:
    """返回趋势箭头、主色与中文描述。"""

    mapping = {
        "up": ("↑", _token("status.success"), "增长"),
        "down": ("↓", _token("status.error"), "下降"),
        "flat": ("→", _token("status.info"), "持平"),
    }
    return mapping[direction]


def _role_tone(role: str) -> BadgeTone:
    """根据岗位映射标签色调。"""

    normalized = role.strip().lower()
    if any(token in normalized for token in ("运营", "manager")):
        return "error"
    if any(token in normalized for token in ("分析", "analyst")):
        return "info"
    if any(token in normalized for token in ("自动化", "automation")):
        return "warning"
    return "brand"


def _base_card_style(object_name: str) -> str:
    """统一卡片壳层样式。"""

    colors = _palette()
    return f"""
        QFrame#{object_name} {{
            background-color: {colors.surface};
            border: 1px solid {colors.border};
            border-radius: {RADIUS_LG}px;
        }}
        QLabel#{object_name}Eyebrow {{
            color: {colors.text_muted};
            font-size: {_static_token('font.size.sm')};
            font-weight: {_static_token('font.weight.semibold')};
        }}
        QLabel#{object_name}Title {{
            color: {colors.text};
            font-size: {_static_token('font.size.lg')};
            font-weight: {_static_token('font.weight.bold')};
        }}
        QLabel#{object_name}Body {{
            color: {colors.text_muted};
            font-size: {_static_token('font.size.sm')};
            line-height: 1.5;
        }}
    """


class KPICard(QFrame):
    """数据 KPI 卡片，展示核心指标、趋势和迷你折线。"""

    def __init__(
        self,
        title: str = "ROAS",
        value: str = "3.42",
        *,
        trend: TrendDirection = "up",
        percentage: str = "+12.6%",
        caption: str = "较昨日提升",
        sparkline_data: Sequence[float | int] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "kpiCard")
        _call(self, "setProperty", "variant", "card")

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING_2XL, SPACING_XL, SPACING_2XL, SPACING_XL)
        root.setSpacing(SPACING_MD)

        header = QHBoxLayout()
        header.setSpacing(SPACING_MD)

        self._title_label = QLabel(title, self)
        _call(self._title_label, "setObjectName", "kpiCardEyebrow")

        self._trend_badge = QLabel("", self)
        _call(self._trend_badge, "setObjectName", "kpiCardTrend")

        header.addWidget(self._title_label)
        header.addStretch(1)
        header.addWidget(self._trend_badge)

        self._value_label = QLabel(value, self)
        _call(self._value_label, "setObjectName", "kpiCardValue")

        meta_row = QHBoxLayout()
        meta_row.setSpacing(SPACING_MD)

        self._percentage_label = QLabel(percentage, self)
        _call(self._percentage_label, "setObjectName", "kpiCardPercentage")

        self._caption_label = QLabel(caption, self)
        _call(self._caption_label, "setObjectName", "kpiCardCaption")

        meta_row.addWidget(self._percentage_label)
        meta_row.addWidget(self._caption_label)
        meta_row.addStretch(1)

        self._sparkline = MiniSparkline(sparkline_data or [102, 108, 111, 120, 118, 126, 133], self)

        root.addLayout(header)
        root.addWidget(self._value_label)
        root.addLayout(meta_row)
        root.addWidget(self._sparkline)

        self.set_trend(trend, percentage)
        self._apply_styles()

    def set_value(self, value: str) -> None:
        """更新核心数值。"""

        _call(self._value_label, "setText", value)

    def set_title(self, title: str) -> None:
        """更新标题文案。"""

        _call(self._title_label, "setText", title)

    def set_trend(self, trend: TrendDirection, percentage: str) -> None:
        """更新趋势方向与涨跌幅。"""

        arrow, color, label = _trend_meta(trend)
        _call(self._trend_badge, "setText", f"{arrow} {label}")
        _call(self._percentage_label, "setText", percentage)
        _call(
            self._trend_badge,
            "setStyleSheet",
            f"""
            QLabel#kpiCardTrend {{
                color: {color};
                background-color: {_rgba(color, 0.14)};
                border: 1px solid {_rgba(color, 0.24)};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_XS}px {SPACING_MD}px;
                font-size: {_static_token('font.size.xs')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            """,
        )
        _call(
            self._percentage_label,
            "setStyleSheet",
            f"color: {color}; font-size: {_static_token('font.size.sm')}; font-weight: {_static_token('font.weight.bold')};",
        )

    def set_sparkline_data(self, data: Sequence[float | int]) -> None:
        """更新迷你趋势线数据。"""

        self._sparkline.set_values(data)

    def _apply_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            _base_card_style("kpiCard")
            + f"""
            QLabel#kpiCardValue {{
                color: {colors.text};
                font-size: {_static_token('font.size.display')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#kpiCardCaption {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            """,
        )


class InfoCard(QFrame):
    """信息提示卡片，适合入口说明与轻量行动。"""

    def __init__(
        self,
        title: str = "投放建议",
        description: str = "根据近 7 天 GPM 与 CTR 变化，建议优先加码高转化素材。",
        *,
        icon: str = "◌",
        action_text: str = "查看详情",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "infoCard")
        _call(self, "setProperty", "variant", "card")

        root = QHBoxLayout(self)
        root.setContentsMargins(SPACING_2XL, SPACING_XL, SPACING_2XL, SPACING_XL)
        root.setSpacing(SPACING_XL)

        self._icon_label = QLabel(icon, self)
        _call(self._icon_label, "setObjectName", "infoCardIcon")

        content = QVBoxLayout()
        content.setSpacing(SPACING_SM)

        self._title_label = QLabel(title, self)
        _call(self._title_label, "setObjectName", "infoCardTitle")

        self._body_label = QLabel(description, self)
        _call(self._body_label, "setObjectName", "infoCardBody")
        _call(self._body_label, "setWordWrap", True)

        self._action_button = QPushButton(action_text, self)
        _call(self._action_button, "setObjectName", "infoCardAction")
        _call(self._action_button, "setProperty", "variant", "ghost")

        content.addWidget(self._title_label)
        content.addWidget(self._body_label)
        content.addWidget(self._action_button, 0)
        content.addStretch(1)

        root.addWidget(self._icon_label)
        root.addLayout(content, 1)
        self._apply_styles()

    @property
    def action_button(self) -> QPushButton:
        """暴露操作按钮。"""

        return self._action_button

    def set_description(self, description: str) -> None:
        """更新说明文案。"""

        _call(self._body_label, "setText", description)

    def _apply_styles(self) -> None:
        _call(
            self,
            "setStyleSheet",
            _base_card_style("infoCard")
            + f"""
            QLabel#infoCardIcon {{
                min-width: 44px;
                max-width: 44px;
                min-height: 44px;
                max-height: 44px;
                border-radius: {RADIUS_LG}px;
                background-color: {_rgba(_token('brand.primary'), 0.14)};
                color: {_token('brand.primary')};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QPushButton#infoCardAction {{
                min-height: {BUTTON_HEIGHT}px;
                padding: {SPACING_MD}px {SPACING_XL}px;
                border-radius: {RADIUS_LG}px;
            }}
            QPushButton#infoCardAction:hover {{
                border-color: {_token('brand.primary')};
                color: {_token('brand.primary')};
            }}
            """,
        )


class ProfileCard(QFrame):
    """人物信息卡片，展示头像、角色和业绩统计。"""

    def __init__(
        self,
        name: str = "林知夏",
        role: str = "数据分析师",
        *,
        stats: Iterable[tuple[str, str]] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "profileCard")
        _call(self, "setProperty", "variant", "card")

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING_2XL, SPACING_XL, SPACING_2XL, SPACING_XL)
        root.setSpacing(SPACING_XL)

        header = QHBoxLayout()
        header.setSpacing(SPACING_XL)

        self._avatar = QLabel(self._initials(name), self)
        _call(self._avatar, "setObjectName", "profileCardAvatar")

        title_column = QVBoxLayout()
        title_column.setSpacing(SPACING_SM)

        self._name_label = QLabel(name, self)
        _call(self._name_label, "setObjectName", "profileCardTitle")

        self._role_chip = TagChip(role, tone=_role_tone(role), parent=self)

        title_column.addWidget(self._name_label)
        title_column.addWidget(self._role_chip)

        header.addWidget(self._avatar)
        header.addLayout(title_column, 1)
        header.addStretch(1)

        self._stats_row = QHBoxLayout()
        self._stats_row.setSpacing(SPACING_MD)

        self._stat_badges: list[StatsBadge] = []
        for label, value in stats or (("CTR", "3.8%"), ("CVR", "6.4%"), ("ROAS", "4.1")):
            badge = StatsBadge(label=label, value=value, icon="◔", tone=_role_tone(role), parent=self)
            self._stat_badges.append(badge)
            self._stats_row.addWidget(badge)

        root.addLayout(header)
        root.addLayout(self._stats_row)
        self._apply_styles(role)

    def set_name(self, name: str) -> None:
        """更新姓名与头像首字。"""

        _call(self._name_label, "setText", name)
        _call(self._avatar, "setText", self._initials(name))

    def set_role(self, role: str) -> None:
        """更新角色标签。"""

        self._role_chip.set_text(role)
        self._role_chip.set_tone(_role_tone(role))
        self._apply_styles(role)

    @staticmethod
    def _initials(name: str) -> str:
        """提取头像首字。"""

        compact = "".join(part for part in name.strip().split() if part)
        if not compact:
            return "TK"
        return compact[:2]

    def _apply_styles(self, role: str) -> None:
        colors = _palette()
        tone = _role_tone(role)
        foreground, background, _border = {
            "brand": (_token("brand.primary"), _rgba(_token("brand.primary"), 0.14), colors.border),
            "error": (_token("status.error"), _rgba(_token("status.error"), 0.14), colors.border),
            "warning": (_token("status.warning"), _rgba(_token("status.warning"), 0.14), colors.border),
            "info": (_token("status.info"), _rgba(_token("status.info"), 0.14), colors.border),
            "success": (_token("status.success"), _rgba(_token("status.success"), 0.14), colors.border),
            "neutral": (colors.text_muted, colors.surface_alt, colors.border),
        }[tone]
        _call(
            self,
            "setStyleSheet",
            _base_card_style("profileCard")
            + f"""
            QLabel#profileCardAvatar {{
                min-width: 56px;
                max-width: 56px;
                min-height: 56px;
                max-height: 56px;
                border-radius: 28px;
                background-color: {background};
                border: 1px solid {_rgba(foreground, 0.18)};
                color: {foreground};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            """,
        )


class ActionCard(QFrame):
    """带主行动按钮与状态指示的操作卡片。"""

    def __init__(
        self,
        title: str = "素材批量复盘",
        description: str = "自动汇总 GPM、CTR、CVR 与 ROAS 波动，生成本周优化清单。",
        *,
        icon: str = "✦",
        button_text: str = "立即执行",
        status_text: str = "可执行",
        status_tone: BadgeTone = "success",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "actionCard")
        _call(self, "setProperty", "variant", "card")

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING_2XL, SPACING_XL, SPACING_2XL, SPACING_XL)
        root.setSpacing(SPACING_XL)

        top_row = QHBoxLayout()
        top_row.setSpacing(SPACING_MD)

        self._icon_label = QLabel(icon, self)
        _call(self._icon_label, "setObjectName", "actionCardIcon")

        self._status_badge = StatusBadge(status_text, tone=status_tone, parent=self)

        top_row.addWidget(self._icon_label)
        top_row.addStretch(1)
        top_row.addWidget(self._status_badge)

        self._title_label = QLabel(title, self)
        _call(self._title_label, "setObjectName", "actionCardTitle")

        self._body_label = QLabel(description, self)
        _call(self._body_label, "setObjectName", "actionCardBody")
        _call(self._body_label, "setWordWrap", True)

        self._primary_button = QPushButton(button_text, self)
        _call(self._primary_button, "setObjectName", "actionCardPrimaryButton")
        _call(self._primary_button, "setProperty", "variant", "primary")

        root.addLayout(top_row)
        root.addWidget(self._title_label)
        root.addWidget(self._body_label)
        root.addWidget(self._primary_button, 0)
        root.addStretch(1)
        self._apply_styles()

    @property
    def primary_button(self) -> QPushButton:
        """暴露主操作按钮。"""

        return self._primary_button

    def set_status(self, text: str, tone: BadgeTone) -> None:
        """更新状态指示。"""

        _call(self._status_badge, "setText", text)
        self._status_badge.set_tone(tone)

    def set_description(self, description: str) -> None:
        """更新说明文案。"""

        _call(self._body_label, "setText", description)

    def _apply_styles(self) -> None:
        _call(
            self,
            "setStyleSheet",
            _base_card_style("actionCard")
            + f"""
            QLabel#actionCardIcon {{
                min-width: 42px;
                max-width: 42px;
                min-height: 42px;
                max-height: 42px;
                border-radius: {RADIUS_LG}px;
                background-color: {_rgba(_token('brand.primary'), 0.12)};
                color: {_token('brand.primary')};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QPushButton#actionCardPrimaryButton {{
                min-height: {BUTTON_HEIGHT}px;
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_MD}px {SPACING_XL}px;
            }}
            """,
        )


MetricCard = KPICard


__all__ = ["ActionCard", "InfoCard", "KPICard", "MetricCard", "ProfileCard"]
