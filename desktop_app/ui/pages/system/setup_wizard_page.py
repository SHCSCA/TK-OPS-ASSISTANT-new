# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportArgumentType=false, reportUnknownParameterType=false, reportPrivateUsage=false, reportUntypedBaseClass=false, reportImplicitOverride=false, reportReturnType=false, reportCallIssue=false, reportAssignmentType=false, reportGeneralTypeIssues=false, reportUninitializedInstanceVariable=false, reportUnusedCallResult=false

from __future__ import annotations

"""Interactive setup wizard page for initial system onboarding."""

from dataclasses import dataclass

from ....core.qt import QFrame, QHBoxLayout, QLabel, QStackedWidget, QVBoxLayout, QWidget, QApplication, Signal
from ....core.theme.tokens import STATIC_TOKENS, get_token_value
from ....core.types import RouteId, ThemeMode
from ...components import (
    AIConfigPanel,
    AIStatusIndicator,
    AgentRoleSelector,
    ContentSection,
    FormGroup,
    ModelPicker,
    PageContainer,
    PrimaryButton,
    SecondaryButton,
    ThemedComboBox,
    ThemedLineEdit,
)
from ...components.inputs import BUTTON_HEIGHT, ToggleSwitch
from ..base_page import BasePage


def _call(target: object, method_name: str, *args: object) -> object | None:
    """Safely call a Qt method when it exists."""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _connect(signal_object: object, callback: object) -> None:
    """Safely connect a signal-like object."""

    connect = getattr(signal_object, "connect", None)
    if callable(connect):
        connect(callback)


def _coerce_mode(value: object) -> ThemeMode:
    """Normalize runtime theme values."""

    if isinstance(value, ThemeMode):
        return value
    if isinstance(value, str) and value.lower() == ThemeMode.DARK.value:
        return ThemeMode.DARK
    return ThemeMode.LIGHT


def _theme_mode() -> ThemeMode:
    """Resolve current application theme mode when available."""

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
    """Read a themed token."""

    return get_token_value(name, _theme_mode())


def _static_token(name: str) -> str:
    """Read a static token."""

    return STATIC_TOKENS[name]


@dataclass(frozen=True)
class _Palette:
    """Local palette helper for wizard styling."""

    surface: str
    surface_alt: str
    text: str
    text_muted: str
    text_inverse: str
    border: str
    border_strong: str
    primary: str


def _palette() -> _Palette:
    """Build the local palette from design tokens."""

    return _Palette(
        surface=_token("surface.secondary"),
        surface_alt=_token("surface.sunken"),
        text=_token("text.primary"),
        text_muted=_token("text.secondary"),
        text_inverse=_token("text.inverse"),
        border=_token("border.default"),
        border_strong=_token("border.strong"),
        primary=_token("brand.primary"),
    )


def _px_token(name: str, fallback: int) -> int:
    """Resolve a px static token into an integer."""

    raw_value = STATIC_TOKENS.get(name, f"{fallback}px")
    digits = "".join(character for character in str(raw_value) if character.isdigit())
    return int(digits) if digits else fallback


def _rgba(hex_color: str, alpha: float) -> str:
    """Convert a hex color to rgba while keeping existing rgba values."""

    color = hex_color.strip()
    if color.startswith("rgba"):
        return color
    color = color.lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _as_int(value: object, default: int) -> int:
    """Safely coerce a runtime value to int."""

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
    """Safely coerce a runtime value to float."""

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


SPACING_XS = _px_token("spacing.xs", 4)
SPACING_SM = _px_token("spacing.sm", 6)
SPACING_MD = _px_token("spacing.md", 8)
SPACING_LG = _px_token("spacing.lg", 12)
SPACING_XL = _px_token("spacing.xl", 16)
SPACING_2XL = _px_token("spacing.2xl", 24)
SPACING_3XL = _px_token("spacing.3xl", 32)
SPACING_4XL = _px_token("spacing.4xl", 48)
RADIUS_MD = _px_token("radius.md", 8)
RADIUS_LG = _px_token("radius.lg", 12)
RADIUS_XL = _px_token("radius.xl", 16)
BUTTON_HEIGHT_MD = _px_token("button.height.md", 40)
BUTTON_HEIGHT_LG = _px_token("button.height.lg", 48)
PAGE_MAX_WIDTH = _px_token("layout.sidebar_width.canonical", 280) * 3
STEP_INACTIVE_SIZE = BUTTON_HEIGHT
STEP_COMPLETE_SIZE = BUTTON_HEIGHT_MD
STEP_ACTIVE_SIZE = BUTTON_HEIGHT_LG + SPACING_XS
WIZARD_PANEL_MIN_HEIGHT = SPACING_4XL * 8

PROVIDER_ITEMS: tuple[tuple[str, str], ...] = (
    ("openai", "OpenAI"),
    ("anthropic", "Anthropic"),
    ("ollama", "Ollama"),
    ("openai-compatible", "OpenAI-compatible"),
)
REGION_ITEMS: tuple[str, ...] = ("中国大陆", "Global", "离线实验环境")
RESPONSE_STYLE_ITEMS: tuple[str, ...] = ("平衡稳健", "高转化营销", "结构化分析", "品牌语气")


@dataclass(frozen=True)
class WizardStepMeta:
    """Metadata used by the wizard stepper and content header."""

    title: str
    heading: str
    description: str


class StepIndicatorItem(QWidget):
    """Single visual step item shown inside the wizard stepper."""

    def __init__(self, index: int, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._index = index
        self._title = title
        self._state = "upcoming"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        self._bubble = QLabel(str(index + 1), self)
        self._label = QLabel(title, self)
        _call(self._label, "setWordWrap", True)

        layout.addWidget(self._bubble, 0)
        layout.addWidget(self._label, 0)
        self._apply_state("upcoming")

    def set_state(self, state: str) -> None:
        """Update the visual state for this step."""

        self._apply_state(state)

    def _apply_state(self, state: str) -> None:
        self._state = state
        colors = _palette()
        size = STEP_INACTIVE_SIZE
        text = str(self._index + 1)
        bubble_color = colors.surface_alt
        bubble_text = colors.text_muted
        border_color = colors.border
        border_width = 1
        label_color = colors.text_muted
        label_weight = _static_token("font.weight.medium")

        if state == "completed":
            size = STEP_COMPLETE_SIZE
            text = "✓"
            bubble_color = _token("brand.primary")
            bubble_text = _token("text.inverse")
            border_color = _token("brand.primary")
            border_width = 1
            label_color = colors.text_muted
        elif state == "current":
            size = STEP_ACTIVE_SIZE
            bubble_color = _token("brand.secondary")
            bubble_text = _token("brand.primary")
            border_color = _token("brand.primary")
            border_width = SPACING_XS
            label_color = colors.text
            label_weight = _static_token("font.weight.bold")

        _call(self._bubble, "setText", text)
        _call(self._bubble, "setFixedSize", size, size)
        _call(
            self._bubble,
            "setStyleSheet",
            f"""
            QLabel {{
                background-color: {bubble_color};
                color: {bubble_text};
                border: {border_width}px solid {border_color};
                border-radius: {size // 2}px;
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.bold')};
                padding: 0;
            }}
            """,
        )
        _call(
            self._label,
            "setStyleSheet",
            f"color: {label_color}; font-size: {_static_token('font.size.md')}; font-weight: {label_weight};",
        )


class SetupWizardPage(BasePage):
    """Multi-step onboarding wizard matching the setup mockup."""

    setup_completed = Signal(dict)

    default_route_id: RouteId = RouteId("setup_wizard")
    default_display_name: str = "Setup Wizard"
    default_icon_name: str = "settings_suggest"

    _STEP_META: tuple[WizardStepMeta, ...] = (
        WizardStepMeta(
            title="欢迎",
            heading="欢迎使用 TK-OPS 智能工作台",
            description="只需几个步骤，即可完成 AI 引擎接入、模型选择与 Agent 角色初始化。",
        ),
        WizardStepMeta(
            title="AI供应商配置",
            heading="配置你的 AI 供应商",
            description="接入首选模型服务商，密钥仅存储在本地设备，方便后续生成、分析与自动化流程使用。",
        ),
        WizardStepMeta(
            title="模型选择",
            heading="选择主力模型",
            description="为当前工作区指定默认模型，兼顾速度、成本与内容质量。",
        ),
        WizardStepMeta(
            title="Agent角色",
            heading="定义默认 Agent 角色",
            description="为团队配置最常用的 AI 角色与输出风格，让后续任务执行更贴近运营场景。",
        ),
        WizardStepMeta(
            title="完成",
            heading="全部设置已就绪",
            description="确认当前工作区配置摘要，完成后即可进入日常运营与内容生产流程。",
        ),
    )

    def setup_ui(self) -> None:
        """Build the setup wizard page shell and all step content."""

        self._current_step_index = 0
        self._wizard_finished = False
        self._syncing_controls = False

        self._workspace_name = "TK-OPS 控制台"
        self._region = REGION_ITEMS[0]
        self._provider_key = PROVIDER_ITEMS[0][0]
        self._api_key = ""
        self._organization_id = ""
        self._base_url = ""
        self._advanced_reasoning = True
        self._selected_model = "gpt-4o"
        self._selected_role = "通用助手"
        self._agent_alias = "运营总控 Agent"
        self._response_style = RESPONSE_STYLE_ITEMS[0]
        self._temperature = 0.7
        self._max_tokens = 2048
        self._top_p = 0.9

        _call(self, "setObjectName", "setupWizardPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        self._page_container = PageContainer(max_width=PAGE_MAX_WIDTH, parent=self)
        self.layout.addWidget(self._page_container)

        self._step_items: list[StepIndicatorItem] = []
        self._step_lines: list[QFrame] = []

        self._page_container.add_widget(self._build_stepper())
        self._page_container.add_widget(self._build_wizard_panel())
        self._page_container.add_widget(self._build_navigation())
        self._page_container.add_widget(self._build_tip_panel())
        self._page_container.add_widget(self._build_footer())

        self._sync_controls_from_state()
        self._set_step(0)

    def _build_stepper(self) -> QWidget:
        root = QWidget(self)
        _call(root, "setObjectName", "setupWizardStepper")
        layout = QHBoxLayout(root)
        layout.setContentsMargins(SPACING_XL, SPACING_SM, SPACING_XL, SPACING_SM)
        layout.setSpacing(SPACING_MD)

        for index, step in enumerate(self._STEP_META):
            item = StepIndicatorItem(index, step.title, root)
            self._step_items.append(item)
            layout.addWidget(item, 0)
            if index < len(self._STEP_META) - 1:
                line = QFrame(root)
                _call(line, "setObjectName", "setupWizardStepLine")
                _call(line, "setFixedHeight", SPACING_XS)
                self._step_lines.append(line)
                layout.addWidget(line, 1)

        return root

    def _build_wizard_panel(self) -> QWidget:
        self._wizard_panel = QFrame(self)
        _call(self._wizard_panel, "setObjectName", "setupWizardPanel")
        _call(self._wizard_panel, "setMinimumHeight", WIZARD_PANEL_MIN_HEIGHT)

        layout = QVBoxLayout(self._wizard_panel)
        layout.setContentsMargins(SPACING_3XL, SPACING_3XL, SPACING_3XL, SPACING_3XL)
        layout.setSpacing(SPACING_2XL)

        self._heading_label = QLabel("", self._wizard_panel)
        self._description_label = QLabel("", self._wizard_panel)
        _call(self._heading_label, "setObjectName", "setupWizardHeading")
        _call(self._description_label, "setObjectName", "setupWizardDescription")
        _call(self._description_label, "setWordWrap", True)

        self._stack = QStackedWidget(self._wizard_panel)

        layout.addWidget(self._heading_label)
        layout.addWidget(self._description_label)
        layout.addWidget(self._stack, 1)

        self._stack.addWidget(self._build_welcome_step())
        self._stack.addWidget(self._build_provider_step())
        self._stack.addWidget(self._build_model_step())
        self._stack.addWidget(self._build_role_step())
        self._stack.addWidget(self._build_complete_step())
        return self._wizard_panel

    def _build_navigation(self) -> QWidget:
        root = QWidget(self)
        _call(root, "setObjectName", "setupWizardNavBar")
        layout = QHBoxLayout(root)
        layout.setContentsMargins(SPACING_SM, 0, SPACING_SM, 0)
        layout.setSpacing(SPACING_XL)

        self._back_button = SecondaryButton("返回", root, icon_text="←")
        self._next_button = PrimaryButton("下一步", root, icon_text="→")
        self._finish_button = PrimaryButton("完成设置", root, icon_text="✓")
        self._step_caption = QLabel("", root)
        _call(self._step_caption, "setObjectName", "setupWizardMeta")

        _connect(getattr(self._back_button, "clicked", None), self._go_previous)
        _connect(getattr(self._next_button, "clicked", None), self._go_next)
        _connect(getattr(self._finish_button, "clicked", None), self._finish_wizard)

        layout.addWidget(self._back_button)
        layout.addStretch(1)
        layout.addWidget(self._step_caption)
        layout.addStretch(1)
        layout.addWidget(self._next_button)
        layout.addWidget(self._finish_button)
        return root

    def _build_tip_panel(self) -> QWidget:
        tip_panel = QFrame(self)
        _call(tip_panel, "setObjectName", "setupWizardTipPanel")
        layout = QHBoxLayout(tip_panel)
        layout.setContentsMargins(SPACING_2XL, SPACING_XL, SPACING_2XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        icon_label = QLabel("✦", tip_panel)
        title_label = QLabel("Pro Tip", tip_panel)
        body_label = QLabel(
            "完成后仍可在系统设置中随时切换供应商、模型与默认 Agent，无需重新运行整个向导。",
            tip_panel,
        )
        _call(icon_label, "setObjectName", "setupWizardTipIcon")
        _call(title_label, "setObjectName", "setupWizardTipTitle")
        _call(body_label, "setObjectName", "setupWizardTipBody")
        _call(body_label, "setWordWrap", True)

        text_host = QWidget(tip_panel)
        text_layout = QVBoxLayout(text_host)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(SPACING_XS)
        text_layout.addWidget(title_label)
        text_layout.addWidget(body_label)

        layout.addWidget(icon_label)
        layout.addWidget(text_host, 1)
        return tip_panel

    def _build_footer(self) -> QWidget:
        footer = QWidget(self)
        _call(footer, "setObjectName", "setupWizardFooterBar")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label = QLabel("© 2024 TK-OPS Intelligence System • v1.0.4-beta", footer)
        _call(label, "setObjectName", "setupWizardFooter")

        layout.addStretch(1)
        layout.addWidget(label)
        layout.addStretch(1)
        return footer

    def _build_welcome_step(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        intro_section = ContentSection("启动前确认", icon="◎", parent=page)
        intro_copy = QLabel(
            "TK-OPS 将帮助你建立默认 AI 工作区，用于选品分析、脚本生成、营销文案与自动化执行。",
            intro_section,
        )
        _call(intro_copy, "setObjectName", "setupWizardBodyText")
        _call(intro_copy, "setWordWrap", True)

        self._welcome_status = AIStatusIndicator(intro_section)
        self._welcome_status.set_status("处理中")
        status_group = FormGroup(
            "当前引导状态",
            field_widget=self._welcome_status,
            description="完成供应商与模型设置后，系统将自动切换为就绪状态。",
            parent=intro_section,
        )

        intro_section.add_widget(intro_copy)
        intro_section.add_widget(status_group)

        workspace_section = ContentSection("工作区偏好", icon="✦", parent=page)
        self._workspace_name_field = ThemedLineEdit(
            label="工作区名称",
            placeholder="例如：TK-OPS 运营中台",
            helper_text="名称将显示在默认工作区与系统摘要中。",
            parent=workspace_section,
        )
        self._region_field = ThemedComboBox(label="部署区域", items=REGION_ITEMS, parent=workspace_section)
        workspace_section.add_widget(self._workspace_name_field)
        workspace_section.add_widget(self._region_field)

        preview_card = QFrame(page)
        _call(preview_card, "setObjectName", "setupWizardAccentCard")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        preview_layout.setSpacing(SPACING_SM)

        preview_title = QLabel("本次向导将完成", preview_card)
        preview_body = QLabel("1. 工作区初始化\n2. AI 供应商接入\n3. 主力模型确认\n4. 默认 Agent 角色配置", preview_card)
        _call(preview_title, "setObjectName", "setupWizardAccentTitle")
        _call(preview_body, "setObjectName", "setupWizardBodyText")
        _call(preview_body, "setWordWrap", True)
        preview_layout.addWidget(preview_title)
        preview_layout.addWidget(preview_body)

        _connect(getattr(self._workspace_name_field.line_edit, "textChanged", None), self._handle_workspace_name_changed)
        _connect(getattr(self._region_field.combo_box, "currentTextChanged", None), self._handle_region_changed)

        layout.addWidget(intro_section)
        layout.addWidget(workspace_section)
        layout.addWidget(preview_card)
        layout.addStretch(1)
        return page

    def _build_provider_step(self) -> QWidget:
        page = QWidget(self)
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        form_column = QWidget(page)
        form_layout = QVBoxLayout(form_column)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(SPACING_2XL)

        credentials_section = ContentSection("供应商接入", icon="⚙", parent=form_column)
        self._provider_field = ThemedComboBox(
            label="AI 供应商",
            items=[label for _, label in PROVIDER_ITEMS],
            parent=credentials_section,
        )
        self._api_key_field = ThemedLineEdit(
            label="API Key",
            placeholder="sk-...",
            helper_text="示例：sk-proj-xxxxxxxxxxxxxxxxxxxx",
            parent=credentials_section,
        )
        self._organization_field = ThemedLineEdit(
            label="Organization ID（可选）",
            placeholder="org-xxxxxxxx",
            helper_text="企业账号或团队配额场景下可填写。",
            parent=credentials_section,
        )
        self._base_url_field = ThemedLineEdit(
            label="Base URL（可选）",
            placeholder="https://api.openai.com/v1",
            helper_text="兼容网关、代理或自部署网关可在此填写。",
            parent=credentials_section,
        )

        credentials_section.add_widget(self._provider_field)
        credentials_section.add_widget(self._api_key_field)
        credentials_section.add_widget(self._organization_field)
        credentials_section.add_widget(self._base_url_field)

        advanced_card = QFrame(form_column)
        _call(advanced_card, "setObjectName", "setupWizardAccentCard")
        advanced_layout = QHBoxLayout(advanced_card)
        advanced_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        advanced_layout.setSpacing(SPACING_XL)

        advanced_copy = QWidget(advanced_card)
        advanced_copy_layout = QVBoxLayout(advanced_copy)
        advanced_copy_layout.setContentsMargins(0, 0, 0, 0)
        advanced_copy_layout.setSpacing(SPACING_XS)
        advanced_title = QLabel("启用高级推理", advanced_card)
        advanced_body = QLabel("为复杂分析、长链路任务与策略规划提供更稳定的推理预算。", advanced_card)
        _call(advanced_title, "setObjectName", "setupWizardAccentTitle")
        _call(advanced_body, "setObjectName", "setupWizardBodyText")
        _call(advanced_body, "setWordWrap", True)
        advanced_copy_layout.addWidget(advanced_title)
        advanced_copy_layout.addWidget(advanced_body)

        self._reasoning_toggle = ToggleSwitch(True, advanced_card)
        advanced_layout.addWidget(advanced_copy, 1)
        advanced_layout.addWidget(self._reasoning_toggle)

        form_layout.addWidget(credentials_section)
        form_layout.addWidget(advanced_card)
        form_layout.addStretch(1)

        side_column = QWidget(page)
        side_layout = QVBoxLayout(side_column)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(SPACING_2XL)

        status_section = ContentSection("连接状态", icon="●", parent=side_column)
        self._provider_status = AIStatusIndicator(status_section)
        provider_status_group = FormGroup(
            "引擎状态",
            field_widget=self._provider_status,
            description="根据当前供应商、凭证与配置摘要实时同步。",
            parent=status_section,
        )
        status_section.add_widget(provider_status_group)

        preview_section = ContentSection("实时参数预览", icon="⌁", parent=side_column)
        self._ai_config_panel = AIConfigPanel(preview_section)
        preview_section.add_widget(self._ai_config_panel)

        side_layout.addWidget(status_section)
        side_layout.addWidget(preview_section)
        side_layout.addStretch(1)

        _connect(getattr(self._provider_field.combo_box, "currentTextChanged", None), self._handle_provider_label_changed)
        _connect(getattr(self._api_key_field.line_edit, "textChanged", None), self._handle_api_key_changed)
        _connect(getattr(self._organization_field.line_edit, "textChanged", None), self._handle_org_changed)
        _connect(getattr(self._base_url_field.line_edit, "textChanged", None), self._handle_base_url_changed)
        _connect(getattr(self._reasoning_toggle, "toggled", None), self._handle_reasoning_toggled)
        _connect(getattr(self._ai_config_panel, "config_changed", None), self._handle_ai_config_changed)

        layout.addWidget(form_column, 3)
        layout.addWidget(side_column, 2)
        return page

    def _build_model_step(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        model_section = ContentSection("模型库", icon="◈", parent=page)
        self._model_picker = ModelPicker(model_section)
        model_section.add_widget(self._model_picker)

        summary_card = QFrame(page)
        _call(summary_card, "setObjectName", "setupWizardAccentCard")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        summary_layout.setSpacing(SPACING_SM)

        self._model_summary_title = QLabel("当前主力模型", summary_card)
        self._model_summary_body = QLabel("", summary_card)
        _call(self._model_summary_title, "setObjectName", "setupWizardAccentTitle")
        _call(self._model_summary_body, "setObjectName", "setupWizardBodyText")
        _call(self._model_summary_body, "setWordWrap", True)

        summary_layout.addWidget(self._model_summary_title)
        summary_layout.addWidget(self._model_summary_body)

        _connect(getattr(self._model_picker, "model_selected", None), self._handle_model_selected)

        layout.addWidget(model_section)
        layout.addWidget(summary_card)
        layout.addStretch(1)
        return page

    def _build_role_step(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        role_section = ContentSection("默认 Agent 角色", icon="☍", parent=page)
        self._role_selector = AgentRoleSelector(role_section)
        role_section.add_widget(self._role_selector)

        prefs_section = ContentSection("交互偏好", icon="✎", parent=page)
        self._agent_alias_field = ThemedLineEdit(
            label="Agent 昵称",
            placeholder="例如：短视频运营总控 Agent",
            helper_text="该名称将用于默认对话入口与系统摘要。",
            parent=prefs_section,
        )
        self._response_style_field = ThemedComboBox(
            label="输出风格",
            items=RESPONSE_STYLE_ITEMS,
            parent=prefs_section,
        )
        prefs_section.add_widget(self._agent_alias_field)
        prefs_section.add_widget(self._response_style_field)

        self._role_summary_card = QFrame(page)
        _call(self._role_summary_card, "setObjectName", "setupWizardAccentCard")
        role_summary_layout = QVBoxLayout(self._role_summary_card)
        role_summary_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        role_summary_layout.setSpacing(SPACING_SM)
        role_summary_title = QLabel("角色摘要", self._role_summary_card)
        self._role_summary_body = QLabel("", self._role_summary_card)
        _call(role_summary_title, "setObjectName", "setupWizardAccentTitle")
        _call(self._role_summary_body, "setObjectName", "setupWizardBodyText")
        _call(self._role_summary_body, "setWordWrap", True)
        role_summary_layout.addWidget(role_summary_title)
        role_summary_layout.addWidget(self._role_summary_body)

        _connect(getattr(self._role_selector, "role_selected", None), self._handle_role_selected)
        _connect(getattr(self._agent_alias_field.line_edit, "textChanged", None), self._handle_agent_alias_changed)
        _connect(getattr(self._response_style_field.combo_box, "currentTextChanged", None), self._handle_response_style_changed)

        layout.addWidget(role_section)
        layout.addWidget(prefs_section)
        layout.addWidget(self._role_summary_card)
        layout.addStretch(1)
        return page

    def _build_complete_step(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        readiness_section = ContentSection("准备完成", icon="✓", parent=page)
        self._completion_status = AIStatusIndicator(readiness_section)
        self._completion_status.set_status("就绪")
        readiness_group = FormGroup(
            "系统状态",
            field_widget=self._completion_status,
            description="完成后即可开始使用 AI 选品、文案、脚本与自动化能力。",
            parent=readiness_section,
        )
        readiness_section.add_widget(readiness_group)

        summary_section = ContentSection("当前配置摘要", icon="≡", parent=page)
        self._summary_workspace = QLabel("", summary_section)
        self._summary_provider = QLabel("", summary_section)
        self._summary_model = QLabel("", summary_section)
        self._summary_role = QLabel("", summary_section)
        self._summary_generation = QLabel("", summary_section)

        for label in (
            self._summary_workspace,
            self._summary_provider,
            self._summary_model,
            self._summary_role,
            self._summary_generation,
        ):
            _call(label, "setObjectName", "setupWizardSummaryText")
            _call(label, "setWordWrap", True)
            summary_section.add_widget(label)

        done_card = QFrame(page)
        _call(done_card, "setObjectName", "setupWizardAccentCard")
        done_layout = QVBoxLayout(done_card)
        done_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        done_layout.setSpacing(SPACING_SM)

        self._completion_title = QLabel("完成后你可以立即开始", done_card)
        self._completion_body = QLabel(
            "进入系统后，可直接在 AI 页面生成脚本、在内容页面整理素材，并在系统设置中继续扩展网关与模型配置。",
            done_card,
        )
        _call(self._completion_title, "setObjectName", "setupWizardAccentTitle")
        _call(self._completion_body, "setObjectName", "setupWizardBodyText")
        _call(self._completion_body, "setWordWrap", True)
        done_layout.addWidget(self._completion_title)
        done_layout.addWidget(self._completion_body)

        layout.addWidget(readiness_section)
        layout.addWidget(summary_section)
        layout.addWidget(done_card)
        layout.addStretch(1)
        return page

    def _go_previous(self) -> None:
        if self._current_step_index <= 0:
            return
        self._wizard_finished = False
        self._set_step(self._current_step_index - 1)

    def _go_next(self) -> None:
        if self._current_step_index >= len(self._STEP_META) - 1:
            return
        self._set_step(self._current_step_index + 1)

    def _finish_wizard(self) -> None:
        self._wizard_finished = True
        self._completion_status.set_status("就绪")
        self._completion_title.setText("设置完成，系统已准备就绪")
        self._completion_body.setText("你现在可以开始配置运营工作流，也可以返回任一步继续调整参数。")
        self.setup_completed.emit(self._snapshot())
        self._refresh_navigation()

    def _set_step(self, index: int) -> None:
        bounded_index = max(0, min(index, len(self._STEP_META) - 1))
        self._current_step_index = bounded_index
        _call(self._stack, "setCurrentIndex", bounded_index)
        meta = self._STEP_META[bounded_index]
        self._heading_label.setText(meta.heading)
        self._description_label.setText(meta.description)
        self._update_stepper()
        self._refresh_dynamic_copy()
        self._refresh_navigation()

    def _update_stepper(self) -> None:
        colors = _palette()
        for index, item in enumerate(self._step_items):
            if index < self._current_step_index:
                item.set_state("completed")
            elif index == self._current_step_index:
                item.set_state("current")
            else:
                item.set_state("upcoming")

        for index, line in enumerate(self._step_lines):
            line_color = _token("brand.primary") if index < self._current_step_index else colors.border
            _call(
                line,
                "setStyleSheet",
                f"QFrame#setupWizardStepLine {{ background-color: {line_color}; border: none; border-radius: {SPACING_XS // 2}px; }}",
            )

    def _refresh_navigation(self) -> None:
        _call(self._back_button, "setEnabled", self._current_step_index > 0)
        _call(self._next_button, "setVisible", self._current_step_index < len(self._STEP_META) - 1)
        _call(self._finish_button, "setVisible", self._current_step_index == len(self._STEP_META) - 1)
        finish_enabled = self._current_step_index == len(self._STEP_META) - 1 and not self._wizard_finished
        _call(self._finish_button, "setEnabled", finish_enabled)
        self._step_caption.setText(f"第 {self._current_step_index + 1} / {len(self._STEP_META)} 步")

    def _refresh_dynamic_copy(self) -> None:
        self._welcome_status.set_status("就绪" if self._provider_status_value() == "就绪" else "处理中")
        self._provider_status.set_status(self._provider_status_value())
        self._model_summary_body.setText(
            f"当前已选择 {self._provider_label(self._provider_key)} · {self._selected_model}，适合作为 {self._workspace_name or '当前工作区'} 的默认引擎。"
        )
        self._role_summary_body.setText(
            f"默认角色为“{self._selected_role}”，对外展示昵称为“{self._agent_alias or self._selected_role}”，输出风格偏向“{self._response_style}”。"
        )
        self._summary_workspace.setText(f"工作区：{self._workspace_name or '未命名工作区'} · 区域：{self._region}")
        self._summary_provider.setText(
            f"供应商：{self._provider_label(self._provider_key)} · 高级推理：{'开启' if self._advanced_reasoning else '关闭'}"
        )
        self._summary_model.setText(f"默认模型：{self._selected_model}")
        self._summary_role.setText(f"默认 Agent：{self._selected_role} · 昵称：{self._agent_alias or self._selected_role}")
        self._summary_generation.setText(
            f"生成参数：temperature {self._temperature:.1f} · max tokens {self._max_tokens} · top-p {self._top_p:.2f}"
        )

    def _provider_status_value(self) -> str:
        if self._provider_key == "ollama":
            return "就绪"
        if self._api_key.strip():
            return "就绪"
        return "离线"

    def _provider_label(self, provider_key: str) -> str:
        return dict(PROVIDER_ITEMS).get(provider_key, provider_key)

    def _sync_controls_from_state(self) -> None:
        self._syncing_controls = True
        try:
            self._workspace_name_field.setText(self._workspace_name)
            _call(self._region_field.combo_box, "setCurrentText", self._region)
            _call(self._provider_field.combo_box, "setCurrentText", self._provider_label(self._provider_key))
            self._api_key_field.setText(self._api_key)
            self._organization_field.setText(self._organization_id)
            self._base_url_field.setText(self._base_url)
            self._reasoning_toggle.setChecked(self._advanced_reasoning)
            self._agent_alias_field.setText(self._agent_alias)
            _call(self._response_style_field.combo_box, "setCurrentText", self._response_style)
            self._sync_ai_config_panel()
            self._sync_model_picker()
            self._sync_role_selector()
        finally:
            self._syncing_controls = False
        self._refresh_dynamic_copy()

    def _sync_ai_config_panel(self) -> None:
        self._ai_config_panel.set_config(
            {
                "provider": self._provider_key,
                "model": self._selected_model,
                "agent_role": self._selected_role,
                "temperature": self._temperature,
                "max_tokens": self._max_tokens,
                "top_p": self._top_p,
            }
        )
        config = self._ai_config_panel.config()
        self._provider_key = str(config.get("provider", self._provider_key))
        self._selected_model = str(config.get("model", self._selected_model))
        self._selected_role = str(config.get("agent_role", self._selected_role))
        self._temperature = _as_float(config.get("temperature", self._temperature), self._temperature)
        self._max_tokens = _as_int(config.get("max_tokens", self._max_tokens), self._max_tokens)
        self._top_p = _as_float(config.get("top_p", self._top_p), self._top_p)

    def _sync_model_picker(self) -> None:
        self._model_picker.set_provider(self._provider_key)
        current_provider, current_model = self._model_picker.current_model()
        if current_provider != self._provider_key or current_model != self._selected_model:
            self._model_picker.set_selected_model(self._provider_key, self._selected_model)

    def _sync_role_selector(self) -> None:
        if self._role_selector.current_role() != self._selected_role:
            self._role_selector.set_active_role(self._selected_role)

    def _handle_workspace_name_changed(self, text: str) -> None:
        if self._syncing_controls:
            return
        self._workspace_name = text.strip() or "TK-OPS 控制台"
        self._refresh_dynamic_copy()

    def _handle_region_changed(self, text: str) -> None:
        if self._syncing_controls:
            return
        self._region = text or REGION_ITEMS[0]
        self._refresh_dynamic_copy()

    def _handle_provider_label_changed(self, label: str) -> None:
        if self._syncing_controls:
            return
        reverse_lookup = {provider_label: provider_key for provider_key, provider_label in PROVIDER_ITEMS}
        self._provider_key = reverse_lookup.get(label, self._provider_key)
        self._syncing_controls = True
        try:
            self._sync_ai_config_panel()
            self._sync_model_picker()
            self._sync_role_selector()
        finally:
            self._syncing_controls = False
        self._refresh_dynamic_copy()

    def _handle_api_key_changed(self, text: str) -> None:
        if self._syncing_controls:
            return
        self._api_key = text.strip()
        self._refresh_dynamic_copy()

    def _handle_org_changed(self, text: str) -> None:
        if self._syncing_controls:
            return
        self._organization_id = text.strip()
        self._refresh_dynamic_copy()

    def _handle_base_url_changed(self, text: str) -> None:
        if self._syncing_controls:
            return
        self._base_url = text.strip()
        self._refresh_dynamic_copy()

    def _handle_reasoning_toggled(self, checked: bool) -> None:
        if self._syncing_controls:
            return
        self._advanced_reasoning = checked
        self._refresh_dynamic_copy()

    def _handle_ai_config_changed(self, config: dict[str, object]) -> None:
        if self._syncing_controls:
            return
        self._provider_key = str(config.get("provider", self._provider_key))
        self._selected_model = str(config.get("model", self._selected_model))
        self._selected_role = str(config.get("agent_role", self._selected_role))
        self._temperature = _as_float(config.get("temperature", self._temperature), self._temperature)
        self._max_tokens = _as_int(config.get("max_tokens", self._max_tokens), self._max_tokens)
        self._top_p = _as_float(config.get("top_p", self._top_p), self._top_p)

        self._syncing_controls = True
        try:
            _call(self._provider_field.combo_box, "setCurrentText", self._provider_label(self._provider_key))
            self._sync_model_picker()
            self._sync_role_selector()
        finally:
            self._syncing_controls = False
        self._refresh_dynamic_copy()

    def _handle_model_selected(self, provider_key: str, model_id: str) -> None:
        if self._syncing_controls:
            return
        self._provider_key = provider_key
        self._selected_model = model_id
        self._syncing_controls = True
        try:
            _call(self._provider_field.combo_box, "setCurrentText", self._provider_label(self._provider_key))
            self._sync_ai_config_panel()
        finally:
            self._syncing_controls = False
        self._refresh_dynamic_copy()

    def _handle_role_selected(self, role_name: str) -> None:
        if self._syncing_controls:
            return
        self._selected_role = role_name
        self._syncing_controls = True
        try:
            self._sync_ai_config_panel()
        finally:
            self._syncing_controls = False
        self._refresh_dynamic_copy()

    def _handle_agent_alias_changed(self, text: str) -> None:
        if self._syncing_controls:
            return
        self._agent_alias = text.strip() or "运营总控 Agent"
        self._refresh_dynamic_copy()

    def _handle_response_style_changed(self, text: str) -> None:
        if self._syncing_controls:
            return
        self._response_style = text or RESPONSE_STYLE_ITEMS[0]
        self._refresh_dynamic_copy()

    def _snapshot(self) -> dict[str, object]:
        return {
            "workspace_name": self._workspace_name,
            "region": self._region,
            "provider": self._provider_key,
            "api_key_configured": bool(self._api_key),
            "organization_id": self._organization_id,
            "base_url": self._base_url,
            "advanced_reasoning": self._advanced_reasoning,
            "model": self._selected_model,
            "agent_role": self._selected_role,
            "agent_alias": self._agent_alias,
            "response_style": self._response_style,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "top_p": self._top_p,
        }

    def _apply_page_styles(self) -> None:
        colors = _palette()
        primary_soft = _rgba(_token("brand.primary"), 0.08)
        primary_border = _rgba(_token("brand.primary"), 0.18)
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#setupWizardPage {{
                background-color: {_token('surface.primary')};
            }}
            QWidget#setupWizardPage QLabel {{
                background: transparent;
                color: {colors.text};
                font-family: {_static_token('font.family.chinese')};
            }}
            QWidget#setupWizardStepper,
            QWidget#setupWizardFooterBar {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_XL}px;
            }}
            QWidget#setupWizardNavBar {{
                background-color: {primary_soft};
                border: 1px solid {primary_border};
                border-radius: {RADIUS_XL}px;
            }}
            QWidget#setupWizardPage QFrame#contentSection {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#setupWizardPanel {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_XL}px;
            }}
            QLabel#setupWizardHeading {{
                color: {colors.text};
                font-size: {_static_token('font.size.display')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#setupWizardDescription {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.regular')};
            }}
            QLabel#setupWizardMeta,
            QLabel#setupWizardFooter {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QLabel#setupWizardBodyText,
            QLabel#setupWizardSummaryText {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.md')};
            }}
            QFrame#setupWizardAccentCard {{
                background-color: {primary_soft};
                border: 1px solid {primary_border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#setupWizardAccentTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QFrame#setupWizardTipPanel {{
                background-color: {colors.surface_alt};
                border: 1px dashed {colors.border_strong};
                border-radius: {RADIUS_XL}px;
            }}
            QLabel#setupWizardTipIcon {{
                color: {_token('brand.primary')};
                font-size: {_static_token('font.size.xxl')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#setupWizardTipTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#setupWizardTipBody {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.md')};
            }}
            """,
        )


__all__ = ["SetupWizardPage"]
