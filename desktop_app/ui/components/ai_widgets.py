# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnknownLambdaType=false, reportUntypedBaseClass=false, reportUnusedCallResult=false, reportUnusedImport=false, reportUnusedFunction=false, reportGeneralTypeIssues=false

from __future__ import annotations

"""AI 场景专用的可复用界面组件。"""

from dataclasses import dataclass
from html import escape
from typing import Mapping

from ...core.theme.tokens import STATIC_TOKENS, get_token_value
from ...core.types import ThemeMode
from .inputs import FlowLayout, SearchBar

try:
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QDoubleSpinBox,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSlider,
        QSpinBox,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    from .inputs import QApplication, QComboBox, QHBoxLayout, QLabel, QTextEdit, QVBoxLayout, QWidget
    from ...core.qt import Signal

    class Qt:
        """无 Qt 环境时的最小方向常量。"""

        Horizontal = 1

    class QPushButton(QWidget):
        """无 Qt 环境时的最小按钮。"""

        def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._text = text
            self._checked = False
            self.clicked = Signal()

        def setText(self, text: str) -> None:
            self._text = text

        def text(self) -> str:
            return self._text

        def setCheckable(self, _value: bool) -> None:
            return None

        def setChecked(self, value: bool) -> None:
            self._checked = value

        def isChecked(self) -> bool:
            return self._checked

    class QSlider(QWidget):
        """无 Qt 环境时的最小滑块。"""

        def __init__(self, _orientation: int, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._minimum = 0
            self._maximum = 100
            self._value = 0
            self.valueChanged = Signal(int)

        def setRange(self, minimum: int, maximum: int) -> None:
            self._minimum = minimum
            self._maximum = maximum

        def setValue(self, value: int) -> None:
            self._value = max(self._minimum, min(self._maximum, value))
            self.valueChanged.emit(self._value)

        def value(self) -> int:
            return self._value

    class QSpinBox(QWidget):
        """无 Qt 环境时的最小整数输入框。"""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._minimum = 0
            self._maximum = 999999
            self._value = 0
            self.valueChanged = Signal(int)

        def setRange(self, minimum: int, maximum: int) -> None:
            self._minimum = minimum
            self._maximum = maximum

        def setSingleStep(self, _step: int) -> None:
            return None

        def setValue(self, value: int) -> None:
            self._value = max(self._minimum, min(self._maximum, int(value)))
            self.valueChanged.emit(self._value)

        def value(self) -> int:
            return self._value

    class QDoubleSpinBox(QWidget):
        """无 Qt 环境时的最小浮点输入框。"""

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._minimum = 0.0
            self._maximum = 1.0
            self._value = 0.0
            self.valueChanged = Signal(float)

        def setRange(self, minimum: float, maximum: float) -> None:
            self._minimum = minimum
            self._maximum = maximum

        def setDecimals(self, _decimals: int) -> None:
            return None

        def setSingleStep(self, _step: float) -> None:
            return None

        def setValue(self, value: float) -> None:
            resolved = max(self._minimum, min(self._maximum, float(value)))
            self._value = resolved
            self.valueChanged.emit(self._value)

        def value(self) -> float:
            return self._value


@dataclass(frozen=True)
class AgentRoleMeta:
    """智能体角色元信息。"""

    icon: str
    name: str
    description: str


@dataclass(frozen=True)
class ModelMeta:
    """模型展示元信息。"""

    provider_key: str
    provider_label: str
    model_id: str
    description: str
    context_window: str
    best_for: str


PROVIDER_OPTIONS: tuple[tuple[str, str], ...] = (
    ("openai", "OpenAI"),
    ("anthropic", "Anthropic"),
    ("ollama", "Ollama"),
    ("openai-compatible", "OpenAI-compatible"),
)

ROLE_OPTIONS: tuple[AgentRoleMeta, ...] = (
    AgentRoleMeta("◎", "通用助手", "适合日常问答、流程协助与通用任务编排。"),
    AgentRoleMeta("✦", "文案专家", "擅长营销文案、商品卖点提炼与风格化表达。"),
    AgentRoleMeta("◫", "数据分析师", "聚焦数据洞察、趋势解读与运营复盘。"),
    AgentRoleMeta("▶", "脚本创作者", "面向短视频脚本、口播结构与镜头节奏设计。"),
    AgentRoleMeta("⌕", "SEO优化师", "强化关键词布局、搜索可见性与内容结构。"),
    AgentRoleMeta("☏", "客服助手", "用于客服回复、FAQ 组织与安抚型对话。"),
)

MODEL_OPTIONS: tuple[ModelMeta, ...] = (
    ModelMeta("openai", "OpenAI", "gpt-4o", "多模态旗舰模型，适合综合生成与复杂推理。", "128K 上下文", "高质量内容生成"),
    ModelMeta("openai", "OpenAI", "gpt-4.1-mini", "更轻量的高质量模型，速度与成本更均衡。", "128K 上下文", "批量内容处理"),
    ModelMeta("openai", "OpenAI", "gpt-4o-mini", "响应更快，适合高频交互与工具链调用。", "128K 上下文", "快速聊天与分类"),
    ModelMeta("anthropic", "Anthropic", "claude-3-7-sonnet", "长文本理解稳定，擅长结构化输出。", "200K 上下文", "策略规划与总结"),
    ModelMeta("anthropic", "Anthropic", "claude-3-5-haiku", "轻量快速，适合摘要、润色与问答。", "200K 上下文", "轻量任务与摘要"),
    ModelMeta("ollama", "Ollama", "qwen2.5:14b", "本地部署友好，中文任务表现平衡。", "32K 上下文", "本地中文生成"),
    ModelMeta("ollama", "Ollama", "llama3.1:8b", "适合本地实验、离线推理与基础问答。", "32K 上下文", "离线助手"),
    ModelMeta("openai-compatible", "OpenAI-compatible", "deepseek-chat", "兼容 OpenAI 协议，适合推理与内容生成。", "64K 上下文", "兼容网关接入"),
    ModelMeta("openai-compatible", "OpenAI-compatible", "glm-4.5-air", "成本与速度兼顾，适合运营生产场景。", "128K 上下文", "高性价比调用"),
)

PROMPT_VARIABLES: tuple[str, ...] = (
    "{product_name}",
    "{description}",
    "{audience}",
    "{selling_points}",
    "{tone}",
    "{platform}",
)

PROMPT_PREVIEW_VALUES: Mapping[str, str] = {
    "{product_name}": "TK 爆款随行杯",
    "{description}": "双层保温，适合通勤与露营场景。",
    "{audience}": "18-30 岁注重生活方式的年轻用户",
    "{selling_points}": "高颜值、防漏、长效保温、适合短视频展示",
    "{tone}": "轻快、有记忆点、带购买推动力",
    "{platform}": "TikTok Shop",
}

STATUS_META: Mapping[str, tuple[str, str]] = {
    "就绪": ("status.success", "系统可立即响应请求"),
    "处理中": ("status.warning", "任务正在生成，请稍候"),
    "错误": ("status.error", "任务执行失败，请检查配置"),
    "离线": ("text.disabled", "当前未连接到可用模型服务"),
}


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用可能不存在的 Qt 方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _connect(signal_object: object, callback: object) -> None:
    """安全连接 Qt 风格信号。"""

    connect = getattr(signal_object, "connect", None)
    if callable(connect):
        connect(callback)


def _coerce_mode(value: object) -> ThemeMode:
    """将运行时主题值归一化。"""

    if isinstance(value, ThemeMode):
        return value
    if isinstance(value, str) and value.lower() == ThemeMode.DARK.value:
        return ThemeMode.DARK
    return ThemeMode.LIGHT


def _theme_mode() -> ThemeMode:
    """尽量从应用实例获取当前主题。"""

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
    """将 px token 转为整数。"""

    return int(STATIC_TOKENS[name].replace("px", ""))


def _provider_label(provider_key: str) -> str:
    """返回供应商展示名。"""

    return dict(PROVIDER_OPTIONS).get(provider_key, provider_key)


def _models_for_provider(provider_key: str) -> list[ModelMeta]:
    """筛选指定供应商的模型列表。"""

    return [model for model in MODEL_OPTIONS if model.provider_key == provider_key]


def _role_names() -> list[str]:
    """返回全部角色名。"""

    return [role.name for role in ROLE_OPTIONS]


def _set_rich_text(widget: QTextEdit, text: str) -> None:
    """优先写入富文本，退化到纯文本。"""

    if _call(widget, "setHtml", text) is None:
        plain_text = text.replace("<br/>", "\n").replace("<br>", "\n")
        _call(widget, "setPlainText", plain_text)


def _read_plain_text(widget: QTextEdit) -> str:
    """兼容读取多行文本内容。"""

    reader = getattr(widget, "toPlainText", None)
    return str(reader()) if callable(reader) else ""


SPACING_XS = _px("spacing.xs")
SPACING_SM = _px("spacing.sm")
SPACING_MD = _px("spacing.md")
SPACING_LG = _px("spacing.lg")
SPACING_XL = _px("spacing.xl")
SPACING_2XL = _px("spacing.2xl")
SPACING_4XL = _px("spacing.4xl")
RADIUS_SM = _px("radius.sm")
RADIUS_MD = _px("radius.md")
RADIUS_LG = _px("radius.lg")
RADIUS_XL = _px("radius.xl")
INPUT_HEIGHT = _px("input.height")
BUTTON_HEIGHT_SM = _px("button.height.sm")
BUTTON_HEIGHT_MD = _px("button.height.md")


def _as_int(value: object, default: int) -> int:
    """将运行时值安全转换为整数。"""

    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return default
    return default


def _as_float(value: object, default: float) -> float:
    """将运行时值安全转换为浮点数。"""

    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


class AIStatusIndicator(QWidget):
    """AI 状态指示器，展示当前模型服务可用性。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._status = "就绪"
        self._description = STATUS_META[self._status][1]
        self.setObjectName("aiStatusIndicator")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING_MD, SPACING_SM, SPACING_MD, SPACING_SM)
        layout.setSpacing(SPACING_SM)

        self._dot = QLabel("●", self)
        self._text = QLabel(self._status, self)
        self._text.setToolTip(self._description)

        layout.addWidget(self._dot)
        layout.addWidget(self._text)
        layout.addStretch(1)
        self._apply_styles()

    def set_status(self, status: str) -> None:
        """更新状态文案与颜色。"""

        resolved_status = status if status in STATUS_META else "离线"
        self._status = resolved_status
        self._description = STATUS_META[resolved_status][1]
        self._text.setText(resolved_status)
        self._text.setToolTip(self._description)
        self._apply_styles()

    def status(self) -> str:
        """返回当前状态。"""

        return self._status

    def _apply_styles(self) -> None:
        tone_token = STATUS_META[self._status][0]
        color = _token(tone_token)
        self.setStyleSheet(
            f"""
            QWidget#aiStatusIndicator {{
                background-color: {_token('surface.secondary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#aiStatusIndicator QLabel {{
                background: transparent;
            }}
            QWidget#aiStatusIndicator QLabel:first-child {{
                color: {color};
                font-size: {STATIC_TOKENS['font.size.lg']};
            }}
            QWidget#aiStatusIndicator QLabel:last-child {{
                color: {_token('text.primary')};
                font-size: {STATIC_TOKENS['font.size.sm']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            """
        )


class TokenUsageDisplay(QWidget):
    """展示提示词、补全与总计 token 消耗。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("tokenUsageDisplay")
        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._total_tokens = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        layout.setSpacing(SPACING_SM)

        self._title = QLabel("Token 用量", self)
        self._bar = QWidget(self)
        self._bar.setObjectName("tokenUsageBar")
        self._bar.setFixedHeight(SPACING_2XL)

        self._prompt_label = QLabel("提示词：0", self)
        self._completion_label = QLabel("补全：0", self)
        self._total_label = QLabel("总计：0", self)

        summary_row = QHBoxLayout()
        summary_row.setContentsMargins(0, 0, 0, 0)
        summary_row.setSpacing(SPACING_MD)
        summary_row.addWidget(self._prompt_label)
        summary_row.addWidget(self._completion_label)
        summary_row.addStretch(1)
        summary_row.addWidget(self._total_label)

        layout.addWidget(self._title)
        layout.addWidget(self._bar)
        layout.addLayout(summary_row)
        self._apply_styles()

    def set_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        """设置 token 统计并刷新可视化。"""

        self._prompt_tokens = max(0, int(prompt_tokens))
        self._completion_tokens = max(0, int(completion_tokens))
        self._total_tokens = self._prompt_tokens + self._completion_tokens
        self._prompt_label.setText(f"提示词：{self._prompt_tokens}")
        self._completion_label.setText(f"补全：{self._completion_tokens}")
        self._total_label.setText(f"总计：{self._total_tokens}")
        self._apply_styles()

    def usage(self) -> dict[str, int]:
        """返回当前 token 统计。"""

        return {
            "prompt_tokens": self._prompt_tokens,
            "completion_tokens": self._completion_tokens,
            "total_tokens": self._total_tokens,
        }

    def _apply_styles(self) -> None:
        total = max(self._total_tokens, 1)
        prompt_stop = self._prompt_tokens / total if self._total_tokens else 0.0
        completion_stop = 1.0 if self._total_tokens else 0.0
        prompt_color = _token("brand.primary")
        completion_color = _token("status.info")
        track_color = _token("surface.sunken")
        self.setStyleSheet(
            f"""
            QWidget#tokenUsageDisplay {{
                background-color: {_token('surface.secondary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#tokenUsageDisplay QLabel {{
                background: transparent;
                color: {_token('text.secondary')};
                font-size: {STATIC_TOKENS['font.size.sm']};
            }}
            QWidget#tokenUsageDisplay QLabel:first-child {{
                color: {_token('text.primary')};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            QWidget#tokenUsageBar {{
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_MD}px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {prompt_color},
                    stop: {prompt_stop:.4f} {prompt_color},
                    stop: {prompt_stop:.4f} {completion_color},
                    stop: {completion_stop:.4f} {completion_color},
                    stop: {completion_stop:.4f} {track_color},
                    stop: 1 {track_color}
                );
            }}
            """
        )


class StreamingOutputWidget(QWidget):
    """支持流式追加内容、复制与 token 统计的输出面板。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("streamingOutput")
        self._html_chunks: list[str] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(SPACING_MD)

        self._title = QLabel("流式输出", self)
        self._status = QLabel("思考中...", self)
        self._copy_button = QPushButton("复制内容", self)

        self._output = QTextEdit(self)
        self._output.setObjectName("streamingOutputBody")
        _call(self._output, "setReadOnly", True)
        _call(self._output, "setMinimumHeight", SPACING_4XL if 'spacing.4xl' in STATIC_TOKENS else 160)

        self._token_display = TokenUsageDisplay(self)

        header_row.addWidget(self._title)
        header_row.addStretch(1)
        header_row.addWidget(self._status)
        header_row.addWidget(self._copy_button)

        layout.addLayout(header_row)
        layout.addWidget(self._output)
        layout.addWidget(self._token_display)

        _connect(self._copy_button.clicked, self.copy_content)
        self.set_loading(False)
        self._apply_styles()

    def append_chunk(self, text: str) -> None:
        """向输出区域追加一个流式片段。"""

        escaped_chunk = escape(text).replace("\n", "<br/>")
        self._html_chunks.append(escaped_chunk)
        _set_rich_text(self._output, "".join(self._html_chunks))

    def clear(self) -> None:
        """清空输出内容与 token 显示。"""

        self._html_chunks.clear()
        _call(self._output, "setPlainText", "")
        self._token_display.set_usage(0, 0)
        self.set_loading(False)

    def set_loading(self, loading: bool) -> None:
        """切换思考中状态。"""

        _call(self._status, "setVisible", loading)

    def set_token_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        """同步底部 token 统计。"""

        self._token_display.set_usage(prompt_tokens, completion_tokens)

    def copy_content(self) -> None:
        """复制当前输出内容到剪贴板。"""

        clipboard_reader = getattr(QApplication, "clipboard", None)
        clipboard = clipboard_reader() if callable(clipboard_reader) else None
        if clipboard is not None:
            _call(clipboard, "setText", _read_plain_text(self._output))

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            f"""
            QWidget#streamingOutput {{
                background-color: {_token('surface.secondary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_XL}px;
            }}
            QWidget#streamingOutput QLabel {{
                background: transparent;
            }}
            QWidget#streamingOutput QLabel:first-child {{
                color: {_token('text.primary')};
                font-size: {STATIC_TOKENS['font.size.lg']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            QTextEdit#streamingOutputBody {{
                background-color: {_token('surface.sunken')};
                color: {_token('text.primary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_LG}px;
                font-size: {STATIC_TOKENS['font.size.md']};
                selection-background-color: {_token('brand.primary')};
                selection-color: {_token('text.inverse')};
            }}
            QWidget#streamingOutput QPushButton {{
                min-height: {BUTTON_HEIGHT_SM}px;
                padding: {SPACING_SM}px {SPACING_XL}px;
                border-radius: {RADIUS_MD}px;
                background-color: {_token('surface.tertiary')};
                color: {_token('text.primary')};
                border: 1px solid {_token('border.default')};
                font-weight: {STATIC_TOKENS['font.weight.medium']};
            }}
            QWidget#streamingOutput QPushButton:hover {{
                border-color: {_token('brand.primary')};
                color: {_token('brand.primary')};
            }}
            """
        )
        self._status.setStyleSheet(
            f"color: {_token('status.warning')}; font-size: {STATIC_TOKENS['font.size.sm']}; font-weight: {STATIC_TOKENS['font.weight.semibold']};"
        )


class AgentRoleSelector(QWidget):
    """以卡片网格方式选择 AI 角色。"""

    role_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("agentRoleSelector")
        self._active_role = ROLE_OPTIONS[0].name
        self._cards: dict[str, QWidget] = {}
        self._buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)

        self._title = QLabel("角色选择", self)
        self._grid_host = QWidget(self)
        self._grid_layout = FlowLayout(self._grid_host, h_spacing=SPACING_MD, v_spacing=SPACING_MD)
        self._custom_button = QPushButton("＋ 自定义角色", self)

        layout.addWidget(self._title)
        layout.addWidget(self._grid_host)
        layout.addWidget(self._custom_button)

        for role in ROLE_OPTIONS:
            self._build_role_card(role)

        _connect(self._custom_button.clicked, lambda: self.set_active_role("自定义角色"))
        self._refresh_cards()
        self._apply_styles()

    def set_active_role(self, role_name: str) -> None:
        """设置当前选中的角色。"""

        self._active_role = role_name
        self._refresh_cards()
        self.role_selected.emit(role_name)

    def current_role(self) -> str:
        """返回当前角色名称。"""

        return self._active_role

    def _build_role_card(self, role: AgentRoleMeta) -> None:
        card = QWidget(self._grid_host)
        card.setObjectName(f"roleCard_{role.name}")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        card_layout.setSpacing(SPACING_SM)

        icon_label = QLabel(role.icon, card)
        name_label = QLabel(role.name, card)
        desc_label = QLabel(role.description, card)
        button = QPushButton("选择", card)

        _call(desc_label, "setWordWrap", True)
        _connect(button.clicked, lambda _checked=False, name=role.name: self.set_active_role(name))

        card_layout.addWidget(icon_label)
        card_layout.addWidget(name_label)
        card_layout.addWidget(desc_label)
        card_layout.addStretch(1)
        card_layout.addWidget(button)

        self._cards[role.name] = card
        self._buttons[role.name] = button
        self._grid_layout.addWidget(card)

    def _refresh_cards(self) -> None:
        for role in ROLE_OPTIONS:
            card = self._cards[role.name]
            button = self._buttons[role.name]
            is_active = role.name == self._active_role
            border_color = _token("brand.primary") if is_active else _token("border.default")
            background = "rgba(0,242,234,0.10)" if is_active else _token("surface.secondary")
            title_color = _token("brand.primary") if is_active else _token("text.primary")
            button_background = _token("brand.primary") if is_active else _token("surface.tertiary")
            button_text = _token("text.inverse") if is_active else _token("text.primary")
            card.setStyleSheet(
                f"""
                QWidget#{card.objectName()} {{
                    background-color: {background};
                    border: 1px solid {border_color};
                    border-radius: {RADIUS_LG}px;
                    min-width: 220px;
                    max-width: 220px;
                }}
                QWidget#{card.objectName()} QLabel {{
                    background: transparent;
                    color: {_token('text.secondary')};
                    font-size: {STATIC_TOKENS['font.size.sm']};
                }}
                QWidget#{card.objectName()} QLabel:nth-child(1) {{
                    color: {_token('brand.primary')};
                    font-size: {STATIC_TOKENS['font.size.xxl']};
                    font-weight: {STATIC_TOKENS['font.weight.bold']};
                }}
                QWidget#{card.objectName()} QLabel:nth-child(2) {{
                    color: {title_color};
                    font-size: {STATIC_TOKENS['font.size.lg']};
                    font-weight: {STATIC_TOKENS['font.weight.semibold']};
                }}
                """
            )
            button.setText("已选择" if is_active else "选择")
            button.setStyleSheet(
                f"""
                QPushButton {{
                    min-height: {BUTTON_HEIGHT_SM}px;
                    border-radius: {RADIUS_MD}px;
                    padding: {SPACING_SM}px {SPACING_MD}px;
                    background-color: {button_background};
                    color: {button_text};
                    border: 1px solid {border_color};
                    font-weight: {STATIC_TOKENS['font.weight.medium']};
                }}
                """
            )

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            f"""
            QWidget#agentRoleSelector {{
                background-color: {_token('surface.secondary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_XL}px;
            }}
            QWidget#agentRoleSelector > QLabel {{
                background: transparent;
                color: {_token('text.primary')};
                font-size: {STATIC_TOKENS['font.size.lg']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            QWidget#agentRoleSelector > QPushButton {{
                min-height: {BUTTON_HEIGHT_SM}px;
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_SM}px {SPACING_XL}px;
                background-color: {_token('surface.tertiary')};
                color: {_token('text.primary')};
                border: 1px dashed {_token('border.strong')};
                font-weight: {STATIC_TOKENS['font.weight.medium']};
            }}
            QWidget#agentRoleSelector > QPushButton:hover {{
                border-color: {_token('brand.primary')};
                color: {_token('brand.primary')};
            }}
            """
        )


class ModelPicker(QWidget):
    """供应商标签加模型卡片列表的双层模型选择器。"""

    model_selected = Signal(str, str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("modelPicker")
        self._active_provider = PROVIDER_OPTIONS[0][0]
        self._selected_model = _models_for_provider(self._active_provider)[0].model_id
        self._provider_buttons: dict[str, QPushButton] = {}
        self._model_cards: list[QWidget] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)

        self._title = QLabel("模型选择", self)
        self._search = SearchBar("搜索模型、场景或上下文...", self)

        self._provider_host = QWidget(self)
        provider_layout = QHBoxLayout(self._provider_host)
        provider_layout.setContentsMargins(0, 0, 0, 0)
        provider_layout.setSpacing(SPACING_SM)

        for provider_key, provider_name in PROVIDER_OPTIONS:
            button = QPushButton(provider_name, self._provider_host)
            button.setCheckable(True)
            self._provider_buttons[provider_key] = button
            provider_layout.addWidget(button)
            _connect(button.clicked, lambda _checked=False, key=provider_key: self.set_provider(key))
        provider_layout.addStretch(1)

        self._cards_host = QWidget(self)
        self._cards_layout = FlowLayout(self._cards_host, h_spacing=SPACING_MD, v_spacing=SPACING_MD)

        layout.addWidget(self._title)
        layout.addWidget(self._search)
        layout.addWidget(self._provider_host)
        layout.addWidget(self._cards_host)

        _connect(self._search.search_changed, self._render_cards)
        self._render_cards("")
        self._apply_styles()

    def set_provider(self, provider_key: str) -> None:
        """切换供应商标签并刷新模型列表。"""

        if provider_key not in dict(PROVIDER_OPTIONS):
            return
        self._active_provider = provider_key
        models = _models_for_provider(provider_key)
        if models and self._selected_model not in {model.model_id for model in models}:
            self._selected_model = models[0].model_id
        self._render_cards(self._search.text())

    def set_selected_model(self, provider_key: str, model_id: str) -> None:
        """设置当前模型并发出选择信号。"""

        self._active_provider = provider_key
        self._selected_model = model_id
        self._render_cards(self._search.text())
        self.model_selected.emit(provider_key, model_id)

    def current_model(self) -> tuple[str, str]:
        """返回当前选中的供应商与模型。"""

        return (self._active_provider, self._selected_model)

    def _render_cards(self, keyword: str) -> None:
        search_text = keyword.strip().lower()
        for card in list(self._model_cards):
            self._cards_layout.removeWidget(card)
            _call(card, "deleteLater")
        self._model_cards.clear()

        for provider_key, button in self._provider_buttons.items():
            is_active = provider_key == self._active_provider
            button.setChecked(is_active)
            background = _token("brand.primary") if is_active else _token("surface.tertiary")
            text_color = _token("text.inverse") if is_active else _token("text.primary")
            border = _token("brand.primary") if is_active else _token("border.default")
            button.setStyleSheet(
                f"""
                QPushButton {{
                    min-height: {BUTTON_HEIGHT_SM}px;
                    border-radius: {RADIUS_MD}px;
                    padding: {SPACING_SM}px {SPACING_XL}px;
                    background-color: {background};
                    color: {text_color};
                    border: 1px solid {border};
                    font-weight: {STATIC_TOKENS['font.weight.medium']};
                }}
                """
            )

        visible_models = []
        for model in _models_for_provider(self._active_provider):
            haystack = f"{model.model_id} {model.description} {model.context_window} {model.best_for}".lower()
            if search_text and search_text not in haystack:
                continue
            visible_models.append(model)

        for model in visible_models:
            card = self._create_model_card(model)
            self._model_cards.append(card)
            self._cards_layout.addWidget(card)

    def _create_model_card(self, model: ModelMeta) -> QWidget:
        card = QWidget(self._cards_host)
        card.setObjectName(f"modelCard_{model.model_id.replace(':', '_').replace('.', '_').replace('-', '_')}")
        is_active = model.model_id == self._selected_model and model.provider_key == self._active_provider

        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_SM)

        name_label = QLabel(model.model_id, card)
        details_label = QLabel(f"{model.context_window} · {model.best_for}", card)
        description_label = QLabel(model.description, card)
        select_button = QPushButton("已选择" if is_active else "选择模型", card)

        _call(description_label, "setWordWrap", True)
        _connect(select_button.clicked, lambda _checked=False, provider=model.provider_key, model_id=model.model_id: self.set_selected_model(provider, model_id))

        layout.addWidget(name_label)
        layout.addWidget(details_label)
        layout.addWidget(description_label)
        layout.addStretch(1)
        layout.addWidget(select_button)

        border_color = _token("brand.primary") if is_active else _token("border.default")
        background = "rgba(0,242,234,0.08)" if is_active else _token("surface.secondary")
        button_bg = _token("brand.primary") if is_active else _token("surface.tertiary")
        button_fg = _token("text.inverse") if is_active else _token("text.primary")
        card.setStyleSheet(
            f"""
            QWidget#{card.objectName()} {{
                background-color: {background};
                border: 1px solid {border_color};
                border-radius: {RADIUS_LG}px;
                min-width: 240px;
                max-width: 240px;
            }}
            QWidget#{card.objectName()} QLabel {{
                background: transparent;
                color: {_token('text.secondary')};
                font-size: {STATIC_TOKENS['font.size.sm']};
            }}
            QWidget#{card.objectName()} QLabel:first-child {{
                color: {_token('text.primary')};
                font-size: {STATIC_TOKENS['font.size.lg']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            QWidget#{card.objectName()} QPushButton {{
                min-height: {BUTTON_HEIGHT_SM}px;
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_SM}px {SPACING_XL}px;
                background-color: {button_bg};
                color: {button_fg};
                border: 1px solid {border_color};
                font-weight: {STATIC_TOKENS['font.weight.medium']};
            }}
            """
        )
        return card

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            f"""
            QWidget#modelPicker {{
                background-color: {_token('surface.secondary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_XL}px;
            }}
            QWidget#modelPicker > QLabel {{
                background: transparent;
                color: {_token('text.primary')};
                font-size: {STATIC_TOKENS['font.size.lg']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            """
        )


class PromptEditor(QWidget):
    """支持变量插入、字符统计与预览的提示词编辑器。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("promptEditor")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)

        self._title = QLabel("提示词编辑", self)
        self._editor = QTextEdit(self)
        self._editor.setObjectName("promptEditorField")
        _call(self._editor, "setPlaceholderText", "请输入系统提示词或任务提示词...")
        _call(self._editor, "setMinimumHeight", 160)

        self._variable_host = QWidget(self)
        self._variable_layout = FlowLayout(self._variable_host, h_spacing=SPACING_SM, v_spacing=SPACING_SM)

        self._char_count = QLabel("0 字", self)
        self._preview_title = QLabel("预览", self)
        self._preview = QTextEdit(self)
        self._preview.setObjectName("promptEditorPreview")
        _call(self._preview, "setReadOnly", True)
        _call(self._preview, "setMinimumHeight", 120)

        for variable in PROMPT_VARIABLES:
            button = QPushButton(variable, self._variable_host)
            _connect(button.clicked, lambda _checked=False, value=variable: self.insert_variable(value))
            button.setStyleSheet(
                f"""
                QPushButton {{
                    min-height: {BUTTON_HEIGHT_SM}px;
                    border-radius: {RADIUS_MD}px;
                    padding: {SPACING_SM}px {SPACING_MD}px;
                    background-color: {_token('surface.tertiary')};
                    color: {_token('text.primary')};
                    border: 1px solid {_token('border.default')};
                    font-size: {STATIC_TOKENS['font.size.sm']};
                }}
                QPushButton:hover {{
                    border-color: {_token('brand.primary')};
                    color: {_token('brand.primary')};
                }}
                """
            )
            self._variable_layout.addWidget(button)

        layout.addWidget(self._title)
        layout.addWidget(self._variable_host)
        layout.addWidget(self._editor)
        layout.addWidget(self._char_count)
        layout.addWidget(self._preview_title)
        layout.addWidget(self._preview)

        _connect(self._editor.textChanged, self._sync_state)
        self._sync_state()
        self._apply_styles()

    def text(self) -> str:
        """返回当前提示词文本。"""

        return _read_plain_text(self._editor)

    def set_text(self, text: str) -> None:
        """写入提示词文本。"""

        _call(self._editor, "setPlainText", text)
        self._sync_state()

    def insert_variable(self, variable_name: str) -> None:
        """向编辑器插入变量占位符。"""

        insert_plain = getattr(self._editor, "insertPlainText", None)
        if callable(insert_plain):
            insert_plain(variable_name)
        else:
            self.set_text(f"{self.text()}{variable_name}")
        self._sync_state()

    def preview_text(self) -> str:
        """返回当前预览文本。"""

        return _read_plain_text(self._preview)

    def _sync_state(self) -> None:
        text = self.text()
        self._char_count.setText(f"{len(text)} 字")
        preview_text = text
        for variable, sample_value in PROMPT_PREVIEW_VALUES.items():
            preview_text = preview_text.replace(variable, sample_value)
        _call(self._preview, "setPlainText", preview_text)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            f"""
            QWidget#promptEditor {{
                background-color: {_token('surface.secondary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_XL}px;
            }}
            QWidget#promptEditor > QLabel {{
                background: transparent;
                color: {_token('text.primary')};
                font-size: {STATIC_TOKENS['font.size.lg']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            QTextEdit#promptEditorField,
            QTextEdit#promptEditorPreview {{
                background-color: {_token('surface.sunken')};
                color: {_token('text.primary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_LG}px;
                font-size: {STATIC_TOKENS['font.size.md']};
            }}
            """
        )
        self._char_count.setStyleSheet(f"color: {_token('text.secondary')}; font-size: {STATIC_TOKENS['font.size.sm']};")
        self._preview_title.setStyleSheet(
            f"color: {_token('text.primary')}; font-size: {STATIC_TOKENS['font.size.sm']}; font-weight: {STATIC_TOKENS['font.weight.semibold']};"
        )


class AIConfigPanel(QWidget):
    """提供供应商、模型、角色与采样参数配置的紧凑面板。"""

    config_changed = Signal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("aiConfigPanel")
        self._provider_lookup = dict(PROVIDER_OPTIONS)
        self._provider_lookup_reverse = {label: key for key, label in PROVIDER_OPTIONS}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)

        self._title = QLabel("AI 配置", self)
        layout.addWidget(self._title)

        self._provider_label = QLabel("供应商选择", self)
        self._provider_combo = QComboBox(self)
        self._provider_combo.addItems([label for _, label in PROVIDER_OPTIONS])

        self._model_label = QLabel("模型", self)
        self._model_combo = QComboBox(self)

        self._role_label = QLabel("智能体角色", self)
        self._role_combo = QComboBox(self)
        self._role_combo.addItems(_role_names())

        self._temperature_label = QLabel("温度", self)
        self._temperature_value = QLabel("0.7", self)
        self._temperature_slider = QSlider(Qt.Horizontal, self)
        self._temperature_slider.setRange(0, 20)
        self._temperature_slider.setValue(7)

        self._max_tokens_label = QLabel("最大 Token", self)
        self._max_tokens = QSpinBox(self)
        self._max_tokens.setRange(1, 32000)
        self._max_tokens.setSingleStep(128)
        self._max_tokens.setValue(2048)

        self._top_p_label = QLabel("Top-p", self)
        self._top_p = QDoubleSpinBox(self)
        self._top_p.setRange(0.0, 1.0)
        self._top_p.setDecimals(2)
        self._top_p.setSingleStep(0.05)
        self._top_p.setValue(0.90)

        self._compact_form_rows: list[tuple[QLabel, QWidget]] = [
            (self._provider_label, self._provider_combo),
            (self._model_label, self._model_combo),
            (self._role_label, self._role_combo),
            (self._max_tokens_label, self._max_tokens),
            (self._top_p_label, self._top_p),
        ]

        for label, field in self._compact_form_rows:
            row = QVBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(SPACING_XS)
            row.addWidget(label)
            row.addWidget(field)
            layout.addLayout(row)

        temperature_row = QVBoxLayout()
        temperature_row.setContentsMargins(0, 0, 0, 0)
        temperature_row.setSpacing(SPACING_XS)

        temperature_header = QHBoxLayout()
        temperature_header.setContentsMargins(0, 0, 0, 0)
        temperature_header.setSpacing(SPACING_SM)
        temperature_header.addWidget(self._temperature_label)
        temperature_header.addStretch(1)
        temperature_header.addWidget(self._temperature_value)

        temperature_row.addLayout(temperature_header)
        temperature_row.addWidget(self._temperature_slider)
        layout.addLayout(temperature_row)

        _connect(self._provider_combo.currentTextChanged, self._on_provider_changed)
        _connect(self._model_combo.currentTextChanged, lambda _value: self._emit_config())
        _connect(self._role_combo.currentTextChanged, lambda _value: self._emit_config())
        _connect(self._temperature_slider.valueChanged, self._on_temperature_changed)
        _connect(self._max_tokens.valueChanged, lambda _value: self._emit_config())
        _connect(self._top_p.valueChanged, lambda _value: self._emit_config())

        self._populate_models(PROVIDER_OPTIONS[0][0])
        self._apply_styles()

    def config(self) -> dict[str, object]:
        """返回当前 AI 配置。"""

        provider_label = self._provider_combo.currentText()
        provider_key = self._provider_lookup_reverse.get(provider_label, provider_label)
        return {
            "provider": provider_key,
            "provider_label": provider_label,
            "model": self._model_combo.currentText(),
            "agent_role": self._role_combo.currentText(),
            "temperature": round(self._temperature_slider.value() / 10.0, 1),
            "max_tokens": int(self._max_tokens.value()),
            "top_p": round(float(self._top_p.value()), 2),
        }

    def set_config(self, config: Mapping[str, object]) -> None:
        """批量写入配置。"""

        provider_value = str(config.get("provider", PROVIDER_OPTIONS[0][0]))
        provider_label = self._provider_lookup.get(provider_value, provider_value)
        _call(self._provider_combo, "setCurrentText", provider_label)
        self._populate_models(provider_value)
        _call(self._model_combo, "setCurrentText", str(config.get("model", self._model_combo.currentText())))
        _call(self._role_combo, "setCurrentText", str(config.get("agent_role", ROLE_OPTIONS[0].name)))
        self._temperature_slider.setValue(_as_int(_as_float(config.get("temperature", 0.7), 0.7) * 10, 7))
        self._max_tokens.setValue(_as_int(config.get("max_tokens", 2048), 2048))
        self._top_p.setValue(_as_float(config.get("top_p", 0.90), 0.90))
        self._emit_config()

    def _populate_models(self, provider_key: str) -> None:
        self._model_combo.clear()
        for model in _models_for_provider(provider_key):
            self._model_combo.addItem(model.model_id)

    def _on_provider_changed(self, provider_label: str) -> None:
        provider_key = self._provider_lookup_reverse.get(provider_label, provider_label)
        self._populate_models(provider_key)
        self._emit_config()

    def _on_temperature_changed(self, slider_value: int) -> None:
        resolved_temperature = slider_value / 10.0
        self._temperature_value.setText(f"{resolved_temperature:.1f}")
        self._emit_config()

    def _emit_config(self) -> None:
        self.config_changed.emit(self.config())

    def _apply_styles(self) -> None:
        field_style = f"""
        background-color: {_token('surface.sunken')};
        color: {_token('text.primary')};
        border: 1px solid {_token('border.default')};
        border-radius: {RADIUS_MD}px;
        padding: {SPACING_SM}px {SPACING_XL}px;
        min-height: {INPUT_HEIGHT}px;
        """
        for label, field in self._compact_form_rows:
            label.setStyleSheet(
                f"color: {_token('text.primary')}; font-size: {STATIC_TOKENS['font.size.sm']}; font-weight: {STATIC_TOKENS['font.weight.semibold']};"
            )
            _call(field, "setStyleSheet", field_style)

        self.setStyleSheet(
            f"""
            QWidget#aiConfigPanel {{
                background-color: {_token('surface.secondary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_XL}px;
            }}
            QWidget#aiConfigPanel > QLabel:first-child {{
                color: {_token('text.primary')};
                font-size: {STATIC_TOKENS['font.size.lg']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            QSlider::groove:horizontal {{
                background-color: {_token('surface.sunken')};
                height: {SPACING_SM}px;
                border-radius: {RADIUS_SM}px;
            }}
            QSlider::handle:horizontal {{
                background-color: {_token('brand.primary')};
                width: {SPACING_XL}px;
                height: {SPACING_XL}px;
                margin: -{SPACING_SM}px 0;
                border-radius: {RADIUS_MD}px;
            }}
            """
        )
        self._temperature_label.setStyleSheet(
            f"color: {_token('text.primary')}; font-size: {STATIC_TOKENS['font.size.sm']}; font-weight: {STATIC_TOKENS['font.weight.semibold']};"
        )
        self._temperature_value.setStyleSheet(
            f"color: {_token('brand.primary')}; font-size: {STATIC_TOKENS['font.size.sm']}; font-weight: {STATIC_TOKENS['font.weight.bold']};"
        )


__all__ = [
    "AIConfigPanel",
    "AIStatusIndicator",
    "AgentRoleSelector",
    "ModelPicker",
    "PromptEditor",
    "StreamingOutputWidget",
    "TokenUsageDisplay",
]
