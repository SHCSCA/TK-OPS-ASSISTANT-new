# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false
from __future__ import annotations

"""系统管理 - AI 供应商配置页面。"""

from dataclasses import dataclass
from datetime import datetime
from typing import Final, Literal, Mapping

from ....core.qt import QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, Signal
from ....core.theme.tokens import STATIC_TOKENS, get_token_value
from ....core.types import RouteId, ThemeMode
from ...components import (
    AIConfigPanel,
    AIStatusIndicator,
    AgentRoleSelector,
    ContentSection,
    FilterDropdown,
    FormGroup,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    SplitPanel,
    StatusBadge,
    TagChip,
    ThemedComboBox,
    ThemedLineEdit,
    ThemedScrollArea,
    ToggleSwitch,
)
from ..base_page import BasePage


ProviderTone = Literal["success", "warning", "error", "info", "brand", "neutral"]
ProviderHealth = Literal["ready", "syncing", "error", "offline"]


@dataclass
class ProviderModelRecord:
    """单个供应商模型演示数据。"""

    model_id: str
    display_name: str
    summary: str
    context_window: str
    best_for: str
    latency_hint: str
    price_hint: str
    enabled: bool = True


@dataclass
class ProviderRolePresetRecord:
    """按供应商推荐的角色预设。"""

    role_name: str
    preferred_model: str
    summary: str
    temperature: float
    top_p: float
    max_tokens: int


@dataclass
class ProviderRecord:
    """供应商卡片与详情侧栏使用的数据。"""

    key: str
    name: str
    brand_icon: str
    subtitle: str
    description: str
    status_label: str
    status_tone: ProviderTone
    health: ProviderHealth
    enabled: bool
    is_default: bool
    base_url: str
    primary_key: str
    backup_key: str
    workspace_hint: str
    selected_models: list[str]
    primary_model: str
    fallback_model: str
    connection_status: str
    validation_text: str
    last_validated: str
    card_meta: str
    sync_note: str
    compliance_note: str
    models: list[ProviderModelRecord]
    role_presets: list[ProviderRolePresetRecord]
    capability_tags: list[str]
    notes: list[str]


STATUS_BADGE_COPY: Final[Mapping[ProviderHealth, tuple[str, ProviderTone]]] = {
    "ready": ("已连接", "success"),
    "syncing": ("同步中", "warning"),
    "error": ("异常", "error"),
    "offline": ("未连通", "neutral"),
}

STATUS_INDICATOR_COPY: Final[Mapping[ProviderHealth, str]] = {
    "ready": "就绪",
    "syncing": "处理中",
    "error": "错误",
    "offline": "离线",
}

FILTER_COPY: Final[tuple[str, ...]] = ("全部", "已启用", "未启用", "默认", "需关注")
DESKTOP_PAGE_MAX_WIDTH: Final[int] = 1760

GLOBAL_NOTICE_LINES: Final[tuple[str, ...]] = (
    "浏览器隔离与 AI 网关切换需要在保存后重新启动部分服务才能完全生效。",
    "本页为演示配置中心，已填充符合 TikTok Shop 运营场景的中文示例数据。",
)

ROLE_PLAYBOOK: Final[Mapping[str, str]] = {
    "通用助手": "覆盖选品问答、基础策略咨询、内部 SOP 检索与多模块串联任务。",
    "文案专家": "适合商品卖点提炼、短视频标题生成、口播脚本润色与广告语改写。",
    "数据分析师": "适合查看店铺趋势、订单异常说明、活动复盘和实验结果归因。",
    "脚本创作者": "适合短视频分镜、短视频话术、转场节奏与素材脚本搭建。",
    "SEO优化师": "适合关键词规划、搜索流量补量、标题结构优化与站内可发现性提升。",
    "客服助手": "适合售前答疑、发货异常解释、售后安抚与标准话术规范输出。",
    "自定义角色": "面向内部专项岗位，可结合模型参数与系统提示进行二次定制。",
}

PROVIDER_DEMOS: Final[list[ProviderRecord]] = [
    ProviderRecord(
        key="openai",
        name="OpenAI",
        brand_icon="◎",
        subtitle="旗舰多模态接入",
        description="适合高质量商品文案、复杂流程编排、多模态素材理解与运营分析总控。",
        status_label="生产环境可用",
        status_tone="success",
        health="ready",
        enabled=True,
        is_default=True,
        base_url="https://api.openai.com/v1",
        primary_key="sk-live-openai-demo-4o-******",
        backup_key="proj_tkops_openai_fallback",
        workspace_hint="品牌主账号 / 华东一区代理",
        selected_models=["gpt-4o", "gpt-4.1-mini"],
        primary_model="gpt-4o",
        fallback_model="gpt-4.1-mini",
        connection_status="连接稳定，近 24 小时成功率 99.3%",
        validation_text="6/6 项关键字段已通过校验",
        last_validated="2 分钟前",
        card_meta="2 个模型已激活 · AES-256 凭证托管",
        sync_note="用于核心商品文案、视频脚本与多代理编排的默认云端供应商。",
        compliance_note="凭证保存在本地安全区，适用于正式投产环境。",
        models=[
            ProviderModelRecord("gpt-4o", "GPT-4o", "多模态旗舰模型，稳定兼顾速度与质量。", "128K", "全链路主模型", "中等延迟", "高质量优先"),
            ProviderModelRecord("gpt-4.1-mini", "GPT-4.1 mini", "适合批量润色、结构化提取与轻量路由。", "128K", "批量内容处理", "低延迟", "成本均衡"),
            ProviderModelRecord("gpt-4o-mini", "GPT-4o mini", "高频交互更经济，适合作为备用或草稿模型。", "128K", "快速问答/分类", "极低延迟", "低成本"),
        ],
        role_presets=[
            ProviderRolePresetRecord("文案专家", "gpt-4o", "输出更稳定，适合营销语气与卖点组合。", 0.8, 0.95, 3200),
            ProviderRolePresetRecord("数据分析师", "gpt-4.1-mini", "结构化说明更紧凑，适合复盘与归因。", 0.3, 0.85, 2200),
            ProviderRolePresetRecord("脚本创作者", "gpt-4o", "更适合镜头拆解、Hook 设计与节奏感文案。", 0.9, 0.95, 3600),
        ],
        capability_tags=["多模态", "高可用", "函数调用", "批量生成"],
        notes=[
            "建议将主 API Key 与项目级备用 Key 同时配置，避免高峰时段单凭证限流。",
            "默认主模型已绑定到文案、脚本与运营建议三条核心链路。",
            "如果需要将成本压低，可把批处理任务切换到 gpt-4.1-mini。",
        ],
    ),
    ProviderRecord(
        key="anthropic",
        name="Anthropic",
        brand_icon="✦",
        subtitle="长文本策略分析",
        description="适合长文档理解、复盘总结、规则制定和复杂策略讨论，中文表现稳定。",
        status_label="建议作为策略副引擎",
        status_tone="brand",
        health="ready",
        enabled=True,
        is_default=False,
        base_url="https://api.anthropic.com/v1",
        primary_key="sk-ant-tkops-claude-******",
        backup_key="workspace_tkops_anthropic_cn",
        workspace_hint="策略分析组 / 周报总结流",
        selected_models=["claude-3-7-sonnet", "claude-3-5-haiku"],
        primary_model="claude-3-7-sonnet",
        fallback_model="claude-3-5-haiku",
        connection_status="长文本链路稳定，摘要与策略规划平均响应 5.1 秒",
        validation_text="5/6 项通过，建议补充团队级备用凭证",
        last_validated="8 分钟前",
        card_meta="2 个模型在线 · 适合长文档规划",
        sync_note="当前被推荐用于竞品分析、活动复盘、策略备忘和 SOP 草案生成。",
        compliance_note="如用于正式分析报告，请保持输出模板固定以便审阅。",
        models=[
            ProviderModelRecord("claude-3-7-sonnet", "Claude 3.7 Sonnet", "长文本推理能力强，适合策略与报告输出。", "200K", "策略规划/总结", "中等延迟", "质量优先"),
            ProviderModelRecord("claude-3-5-haiku", "Claude 3.5 Haiku", "轻量快速，适合摘要、分类与短结果输出。", "200K", "轻量总结", "低延迟", "成本友好"),
            ProviderModelRecord("claude-3-opus", "Claude 3 Opus", "更偏深度推理，适合高价值场景预研。", "200K", "复杂决策草案", "较高延迟", "高成本"),
        ],
        role_presets=[
            ProviderRolePresetRecord("数据分析师", "claude-3-7-sonnet", "适合长表格总结、归因、结论归纳。", 0.2, 0.8, 2800),
            ProviderRolePresetRecord("通用助手", "claude-3-5-haiku", "适合内部问答与 SOP 速查。", 0.5, 0.9, 1800),
            ProviderRolePresetRecord("SEO优化师", "claude-3-7-sonnet", "适合长尾词规划与类目结构输出。", 0.4, 0.9, 2400),
        ],
        capability_tags=["长上下文", "策略规划", "稳定总结", "规则制定"],
        notes=[
            "推荐把长文档分析、会议纪要和运营周报默认交给 Anthropic 处理。",
            "如果以中文内容为主，建议保留固定格式提示词，输出会更稳定。",
            "Haiku 可承担低价值摘要工作，减少旗舰模型调用成本。",
        ],
    ),
    ProviderRecord(
        key="ollama",
        name="Ollama",
        brand_icon="◫",
        subtitle="本地离线推理",
        description="适合敏感素材离线测试、局域网使用与私有数据草稿生成，不依赖外网。",
        status_label="本地服务待预热",
        status_tone="warning",
        health="syncing",
        enabled=True,
        is_default=False,
        base_url="http://127.0.0.1:11434",
        primary_key="本地部署无需云端 API Key",
        backup_key="局域网节点：10.0.8.21 / GPU-01",
        workspace_hint="剪映素材本地站 / 夜间批处理",
        selected_models=["qwen2.5:14b", "llama3.1:8b"],
        primary_model="qwen2.5:14b",
        fallback_model="llama3.1:8b",
        connection_status="本地节点已发现，正在进行模型预热与上下文缓存准备",
        validation_text="4/6 项通过，需要确认 GPU 显存与模型拉取状态",
        last_validated="12 分钟前",
        card_meta="本地双模型路由 · 适合离线创作",
        sync_note="推荐承接敏感商品草稿、离线测试与夜间批量生成任务。",
        compliance_note="局域网部署更适合内部素材与未公开商品数据，不建议直接替代主生产链路。",
        models=[
            ProviderModelRecord("qwen2.5:14b", "Qwen 2.5 14B", "中文综合表现均衡，适合离线文案与问答。", "32K", "本地中文生成", "中等延迟", "本地资源优先"),
            ProviderModelRecord("llama3.1:8b", "Llama 3.1 8B", "轻量部署更友好，适合离线草稿和结构提取。", "32K", "基础助手", "低延迟", "本地低成本"),
            ProviderModelRecord("mistral:7b", "Mistral 7B", "适合快速试验与规则抽取。", "16K", "实验验证", "低延迟", "低成本"),
        ],
        role_presets=[
            ProviderRolePresetRecord("客服助手", "qwen2.5:14b", "本地处理售后话术更安全，便于审核。", 0.4, 0.85, 1800),
            ProviderRolePresetRecord("通用助手", "llama3.1:8b", "适合低成本内部问答。", 0.5, 0.9, 1600),
            ProviderRolePresetRecord("文案专家", "qwen2.5:14b", "适合草稿初版，不建议直接投放上线。", 0.7, 0.92, 2400),
        ],
        capability_tags=["本地部署", "离线推理", "敏感数据", "夜间批跑"],
        notes=[
            "建议对本地模型设置更严格的输出审校流程，避免直接进入上线链路。",
            "若需要更快响应，可在夜间预热常用模型并缓存系统提示。",
            "本地节点适合处理敏感评论、未发售商品和内部培训资料。",
        ],
    ),
    ProviderRecord(
        key="openai-compatible",
        name="OpenAI-compatible",
        brand_icon="⌁",
        subtitle="兼容网关接入",
        description="适合接入第三方兼容网关、区域代理或企业自建转发层，灵活补充产能。",
        status_label="待补充网关白名单",
        status_tone="warning",
        health="offline",
        enabled=False,
        is_default=False,
        base_url="https://gateway.example.ai/v1",
        primary_key="sk-compatible-routing-******",
        backup_key="tenant=tkops-cn / channel=ops-primary",
        workspace_hint="备用云网关 / 华北容灾通道",
        selected_models=["deepseek-chat", "glm-4.5-air"],
        primary_model="deepseek-chat",
        fallback_model="glm-4.5-air",
        connection_status="兼容网关尚未加入白名单，最近一次探测在 TLS 握手阶段超时",
        validation_text="3/6 项通过，需要完成 Key、域名与代理白名单验证",
        last_validated="27 分钟前",
        card_meta="2 个候选模型 · 容灾与弹性补量",
        sync_note="更适合容灾路由、区域代理、弹性加量与成本优化实验。",
        compliance_note="启用前请确认网关日志策略、请求审计与数据落盘规范。",
        models=[
            ProviderModelRecord("deepseek-chat", "DeepSeek Chat", "适合推理和内容生成，性价比较高。", "64K", "弹性补量", "中等延迟", "高性价比"),
            ProviderModelRecord("glm-4.5-air", "GLM 4.5 Air", "速度与成本平衡，适合运营批处理。", "128K", "批量运营任务", "低延迟", "均衡"),
            ProviderModelRecord("qwen-max-compat", "Qwen Max Compat", "适合兼容 OpenAI 协议的替代线路。", "32K", "兼容网关备援", "中等延迟", "区域灵活"),
        ],
        role_presets=[
            ProviderRolePresetRecord("通用助手", "glm-4.5-air", "适合作为弹性补位的轻量默认路由。", 0.6, 0.9, 1800),
            ProviderRolePresetRecord("文案专家", "deepseek-chat", "适合高性价比文案批处理。", 0.8, 0.95, 2600),
            ProviderRolePresetRecord("SEO优化师", "glm-4.5-air", "适合批量标题与关键词实验。", 0.5, 0.88, 2200),
        ],
        capability_tags=["兼容协议", "容灾补位", "区域代理", "成本实验"],
        notes=[
            "建议在沙箱环境验证速率限制、响应字段和错误码兼容性后再启用。",
            "如果用于生产补量，请保留回退到 OpenAI 的自动切换策略。",
            "适合作为特定区域、特定时间段的弹性线路，而非唯一主路由。",
        ],
    ),
]


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用 Qt 风格方法。"""

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
    """将运行时主题值规整为 ThemeMode。"""

    if isinstance(value, ThemeMode):
        return value
    if isinstance(value, str) and value.lower() == ThemeMode.DARK.value:
        return ThemeMode.DARK
    return ThemeMode.LIGHT


def _theme_mode() -> ThemeMode:
    """尽量从应用实例读取当前主题。"""

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
    """读取主题 token。"""

    return get_token_value(name, _theme_mode())


def _px(name: str) -> int:
    """将 px token 转为整数。"""

    return int(STATIC_TOKENS[name].replace("px", ""))


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _set_word_wrap(widget: QLabel) -> None:
    """安全启用自动换行。"""

    _call(widget, "setWordWrap", True)


def _set_visible(widget: QWidget, visible: bool) -> None:
    """安全控制显隐。"""

    _call(widget, "setVisible", visible)


def _as_float(value: object, default: float) -> float:
    """将运行时值安全转成浮点数。"""

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


def _as_int(value: object, default: int) -> int:
    """将运行时值安全转成整数。"""

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


def _clear_layout(layout: object) -> None:
    """清空真实 Qt 布局中的子项。"""

    count_method = getattr(layout, "count", None)
    take_at = getattr(layout, "takeAt", None)
    if not callable(count_method) or not callable(take_at):
        return
    while True:
        count_value = count_method()
        if not isinstance(count_value, int) or count_value <= 0:
            break
        item = take_at(0)
        widget_reader = getattr(item, "widget", None)
        layout_reader = getattr(item, "layout", None)
        widget = widget_reader() if callable(widget_reader) else None
        nested_layout = layout_reader() if callable(layout_reader) else None
        if widget is not None:
            _call(widget, "deleteLater")
        elif nested_layout is not None:
            _clear_layout(nested_layout)


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


class AIProviderPage(BasePage):
    """AI 供应商配置中心页面。"""

    default_route_id = RouteId("ai_provider_settings")
    default_display_name = "AI供应商配置"
    default_icon_name = "settings"

    provider_selected = Signal(str)

    def __init__(self, parent: object | None = None) -> None:
        self._providers: list[ProviderRecord] = [provider for provider in PROVIDER_DEMOS]
        self._provider_lookup: dict[str, ProviderRecord] = {provider.key: provider for provider in self._providers}
        self._selected_provider_key: str = self._default_provider().key
        self._selected_role_name: str = "文案专家"
        self._syncing_panel = False
        self._syncing_model_combos = False

        self._page_container: PageContainer | None = None
        self._provider_rows_host: QWidget | None = None
        self._provider_rows_layout: QVBoxLayout | None = None
        self._provider_card_widgets: dict[str, QWidget] = {}
        self._provider_card_meta_labels: dict[str, QLabel] = {}
        self._provider_card_note_labels: dict[str, QLabel] = {}
        self._provider_card_selected_badges: dict[str, QLabel] = {}
        self._provider_card_status_badges: dict[str, StatusBadge] = {}
        self._provider_card_toggles: dict[str, ToggleSwitch] = {}
        self._provider_card_buttons: dict[str, QPushButton] = {}
        self._provider_row_registry: list[tuple[QWidget, tuple[str, ...]]] = []

        self._search_bar: SearchBar | None = None
        self._filter_dropdown: FilterDropdown | None = None
        self._global_status_indicator: AIStatusIndicator | None = None
        self._provider_count_label: QWidget | None = None
        self._enabled_count_label: QWidget | None = None
        self._default_provider_label: QWidget | None = None
        self._sync_summary_label: QWidget | None = None

        self._detail_icon_label: QLabel | None = None
        self._detail_name_label: QLabel | None = None
        self._detail_subtitle_label: QLabel | None = None
        self._detail_description_label: QLabel | None = None
        self._detail_status_badge: StatusBadge | None = None
        self._detail_route_label: QLabel | None = None
        self._detail_connection_label: QLabel | None = None
        self._detail_compliance_label: QLabel | None = None

        self._primary_key_input: ThemedLineEdit | None = None
        self._backup_key_input: ThemedLineEdit | None = None
        self._base_url_input: ThemedLineEdit | None = None
        self._workspace_input: ThemedLineEdit | None = None
        self._primary_model_combo: ThemedComboBox | None = None
        self._fallback_model_combo: ThemedComboBox | None = None
        self._routing_mode_combo: ThemedComboBox | None = None
        self._default_toggle: ToggleSwitch | None = None
        self._enable_toggle: ToggleSwitch | None = None
        self._set_default_button: SecondaryButton | None = None
        self._test_button: PrimaryButton | None = None
        self._selected_models_host: QWidget | None = None
        self._selected_models_layout: QHBoxLayout | None = None
        self._selected_model_chips: list[TagChip] = []
        self._model_rows_host: QWidget | None = None
        self._model_rows_layout: QVBoxLayout | None = None

        self._ai_config_panel: AIConfigPanel | None = None
        self._agent_selector: AgentRoleSelector | None = None
        self._role_summary_label: QLabel | None = None
        self._role_playbook_label: QLabel | None = None
        self._role_rows_host: QWidget | None = None
        self._role_rows_layout: QVBoxLayout | None = None

        self._validation_connection_value: QLabel | None = None
        self._validation_fields_value: QLabel | None = None
        self._validation_time_value: QLabel | None = None
        self._validation_hint_label: QLabel | None = None

        super().__init__(parent=parent)

    def setup_ui(self) -> None:
        """完整构建页面，不复用 BasePage 默认占位布局。"""

        _call(self, "setObjectName", "aiProviderPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        reset_button = SecondaryButton("恢复默认示例", self, icon_text="↺")
        save_button = PrimaryButton("保存配置变更", self, icon_text="✓")
        _connect(getattr(reset_button, "clicked", None), self._restore_demo_defaults)
        _connect(getattr(save_button, "clicked", None), self._save_changes)

        self._page_container = PageContainer(
            title="系统管理 - AI供应商配置详细版",
            description="统一维护 OpenAI、Anthropic、Ollama 与兼容网关的接入凭证、模型路由、默认供应商与智能体角色预设。",
            actions=[reset_button, save_button],
            max_width=DESKTOP_PAGE_MAX_WIDTH,
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._page_container.add_widget(self._build_notice_banner())
        self._page_container.add_widget(self._build_top_summary_strip())
        self._page_container.add_widget(self._build_toolbar())
        self._page_container.add_widget(self._build_main_content())
        self._page_container.add_widget(self._build_validation_bar())

        self._apply_page_styles()
        self._build_provider_rows()
        self._apply_provider_filters()
        self._refresh_summary_strip()
        self._refresh_provider_cards()
        self._refresh_detail_panel()

    def _default_provider(self) -> ProviderRecord:
        """返回默认供应商。"""

        for provider in self._providers:
            if provider.is_default:
                return provider
        return self._providers[0]

    def _current_provider(self) -> ProviderRecord:
        """返回当前选中的供应商。"""

        return self._provider_lookup[self._selected_provider_key]

    def _build_notice_banner(self) -> QWidget:
        """顶部提醒条。"""

        banner = QFrame(self)
        _call(banner, "setObjectName", "aiProviderNotice")
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_LG)

        icon_label = QLabel("⚠ ⚠", banner)
        _call(icon_label, "setObjectName", "aiProviderNoticeIcon")

        text_host = QWidget(banner)
        text_layout = QVBoxLayout(text_host)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(SPACING_XS)

        title_label = QLabel("部分 AI 网关参数在保存后需要重载服务", text_host)
        body_label = QLabel(" · ".join(GLOBAL_NOTICE_LINES), text_host)
        _set_word_wrap(body_label)
        _call(title_label, "setObjectName", "aiProviderNoticeTitle")
        _call(body_label, "setObjectName", "aiProviderNoticeBody")

        restart_button = PrimaryButton("立即重载相关服务", banner, icon_text="⟳")
        _connect(getattr(restart_button, "clicked", None), self._simulate_restart)

        text_layout.addWidget(title_label)
        text_layout.addWidget(body_label)

        layout.addWidget(icon_label)
        layout.addWidget(text_host, 1)
        layout.addWidget(restart_button)
        return banner

    def _build_top_summary_strip(self) -> QWidget:
        """顶部状态总览。"""

        host = QWidget(self)
        _call(host, "setObjectName", "aiProviderSummaryStrip")
        row = QHBoxLayout(host)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACING_MD)

        self._provider_count_label = self._build_stat_tile(host, "供应商总数", "0", "已接入的 AI 供应商与路由目标")
        self._enabled_count_label = self._build_stat_tile(host, "当前启用", "0", "在系统中允许分发请求的供应商数量")
        self._default_provider_label = self._build_stat_tile(host, "默认主路由", "-", "主页面、文案流和脚本流的默认供应商")
        self._sync_summary_label = self._build_stat_tile(host, "连接校验", "待检查", "最近一次测试结果与字段完整度")

        for widget in (
            self._provider_count_label,
            self._enabled_count_label,
            self._default_provider_label,
            self._sync_summary_label,
        ):
            row.addWidget(widget)
        return host

    def _build_stat_tile(self, parent: QWidget, title: str, value: str, description: str) -> QWidget:
        """构建简单统计卡。"""

        card = QFrame(parent)
        _call(card, "setObjectName", "aiProviderStatTile")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_SM)

        title_label = QLabel(title, card)
        value_label = QLabel(value, card)
        desc_label = QLabel(description, card)
        _set_word_wrap(desc_label)

        _call(title_label, "setObjectName", "aiProviderStatTitle")
        _call(value_label, "setObjectName", "aiProviderStatValue")
        _call(desc_label, "setObjectName", "aiProviderStatDesc")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(desc_label)
        return card

    def _build_toolbar(self) -> QWidget:
        """搜索与筛选工具条。"""

        toolbar = QWidget(self)
        _call(toolbar, "setObjectName", "aiProviderToolbar")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_XL)

        self._search_bar = SearchBar("搜索供应商、模型或说明…")
        self._filter_dropdown = FilterDropdown(label="状态筛选", items=FILTER_COPY, include_all=False)
        self._global_status_indicator = AIStatusIndicator(toolbar)

        help_label = QLabel("默认角色：文案专家 · 当前页面为 AI 配置中心", toolbar)
        _call(help_label, "setObjectName", "aiProviderToolbarHint")

        _connect(getattr(self._search_bar, "search_changed", None), self._on_search_changed)
        _connect(getattr(self._filter_dropdown, "filter_changed", None), self._on_filter_changed)

        layout.addWidget(self._search_bar, 2)
        layout.addWidget(self._filter_dropdown)
        layout.addWidget(self._global_status_indicator)
        layout.addWidget(help_label, 1)
        return toolbar

    def _build_main_content(self) -> QWidget:
        """主内容双栏区域。"""

        host = SplitPanel("horizontal", split_ratio=(0.36, 0.64), minimum_sizes=(360, 760), parent=self)

        left_scroll = ThemedScrollArea(host)
        right_scroll = ThemedScrollArea(host)

        left_scroll.add_widget(self._build_provider_catalog())
        right_scroll.add_widget(self._build_detail_column())

        host.set_widgets(left_scroll, right_scroll)
        return host

    def _build_provider_catalog(self) -> QWidget:
        """左侧供应商列表区。"""

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        intro_section = ContentSection("供应商列表", icon="◫", parent=container)
        intro_label = QLabel(
            "按供应商查看启用状态、默认路由、候选模型与连接概况。选择任一供应商后，可在右侧完成密钥、Base URL、模型与角色预设配置。",
            intro_section,
        )
        _set_word_wrap(intro_label)
        _call(intro_label, "setObjectName", "aiProviderSectionIntro")
        intro_section.add_widget(intro_label)

        self._provider_rows_host = QWidget(intro_section)
        provider_rows_layout = QVBoxLayout(self._provider_rows_host)
        if provider_rows_layout is not None:
            provider_rows_layout.setContentsMargins(0, 0, 0, 0)
            provider_rows_layout.setSpacing(SPACING_LG)
        self._provider_rows_layout = provider_rows_layout
        intro_section.add_widget(self._provider_rows_host)

        strategy_section = ContentSection("接入策略说明", icon="⌘", parent=container)
        for text in (
            "生产主链路优先走默认供应商；未命中时按备用模型与兼容网关回退。",
            "敏感商品或未公开素材建议优先走本地 Ollama 节点，避免外发。",
            "长文档复盘与策略输出建议交由 Anthropic；高频轻量任务可交由轻量模型处理。",
        ):
            note = self._build_bullet_note(strategy_section, text)
            strategy_section.add_widget(note)

        layout.addWidget(intro_section)
        layout.addWidget(strategy_section)
        return container

    def _build_bullet_note(self, parent: QWidget, text: str) -> QWidget:
        """构建项目说明行。"""

        row = QWidget(parent)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        bullet = QLabel("•", row)
        body = QLabel(text, row)
        _set_word_wrap(body)
        _call(body, "setObjectName", "aiProviderBulletBody")
        _call(bullet, "setObjectName", "aiProviderBullet")

        layout.addWidget(bullet)
        layout.addWidget(body, 1)
        return row

    def _build_provider_rows(self) -> None:
        """按两列生成供应商卡片行。"""

        if self._provider_rows_layout is None or self._provider_rows_host is None:
            return
        _clear_layout(self._provider_rows_layout)
        self._provider_row_registry.clear()
        self._provider_card_widgets.clear()
        self._provider_card_meta_labels.clear()
        self._provider_card_note_labels.clear()
        self._provider_card_selected_badges.clear()
        self._provider_card_status_badges.clear()
        self._provider_card_toggles.clear()
        self._provider_card_buttons.clear()

        pair_size = 1
        for index in range(0, len(self._providers), pair_size):
            row_widget = QWidget(self._provider_rows_host)
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(SPACING_LG)
            keys_in_row: list[str] = []

            for provider in self._providers[index : index + pair_size]:
                keys_in_row.append(provider.key)
                card = self._build_provider_card(provider, row_widget)
                row_layout.addWidget(card, 1)

            if len(keys_in_row) < pair_size:
                row_layout.addStretch(1)

            self._provider_rows_layout.addWidget(row_widget)
            self._provider_row_registry.append((row_widget, tuple(keys_in_row)))

    def _build_provider_card(self, provider: ProviderRecord, parent: QWidget) -> QWidget:
        """构建供应商展示卡。"""

        card = QFrame(parent)
        _call(card, "setObjectName", f"providerCard_{provider.key}")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_MD)

        header_row = QWidget(card)
        header_layout = QHBoxLayout(header_row)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_MD)

        icon_label = QLabel(provider.brand_icon, header_row)
        name_host = QWidget(header_row)
        name_layout = QVBoxLayout(name_host)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(SPACING_XS)
        name_label = QLabel(provider.name, name_host)
        subtitle_label = QLabel(provider.subtitle, name_host)
        _call(name_label, "setObjectName", "providerCardName")
        _call(subtitle_label, "setObjectName", "providerCardSubtitle")

        selected_badge = QLabel("当前查看", header_row)
        _call(selected_badge, "setObjectName", "providerCardSelected")

        name_layout.addWidget(name_label)
        name_layout.addWidget(subtitle_label)

        header_layout.addWidget(icon_label)
        header_layout.addWidget(name_host, 1)
        header_layout.addWidget(selected_badge)

        description_label = QLabel(provider.description, card)
        _set_word_wrap(description_label)
        _call(description_label, "setObjectName", "providerCardDescription")

        toggle_row = QWidget(card)
        toggle_layout = QHBoxLayout(toggle_row)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(SPACING_MD)

        toggle = ToggleSwitch(provider.enabled)
        status_badge = StatusBadge(provider.status_label, provider.status_tone)
        toggle_hint = QLabel("已启用" if provider.enabled else "未启用", toggle_row)
        _call(toggle_hint, "setObjectName", "providerCardToggleHint")

        toggle_layout.addWidget(toggle)
        toggle_layout.addWidget(toggle_hint)
        toggle_layout.addStretch(1)
        toggle_layout.addWidget(status_badge)

        meta_label = QLabel(provider.card_meta, card)
        note_label = QLabel(provider.sync_note, card)
        _set_word_wrap(meta_label)
        _set_word_wrap(note_label)
        _call(meta_label, "setObjectName", "providerCardMeta")
        _call(note_label, "setObjectName", "providerCardNote")

        tags_row = QWidget(card)
        tags_layout = QHBoxLayout(tags_row)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(SPACING_SM)
        for tag in provider.capability_tags[:3]:
            chip = TagChip(tag, tone="neutral")
            tags_layout.addWidget(chip)
        tags_layout.addStretch(1)

        button_row = QWidget(card)
        button_layout = QHBoxLayout(button_row)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(SPACING_MD)

        configure_button = SecondaryButton("查看并配置", button_row, icon_text="⚙")
        default_hint = QLabel("系统默认" if provider.is_default else "可设为默认", button_row)
        _call(default_hint, "setObjectName", "providerCardDefaultHint")

        button_layout.addWidget(configure_button)
        button_layout.addStretch(1)
        button_layout.addWidget(default_hint)

        layout.addWidget(header_row)
        layout.addWidget(description_label)
        layout.addWidget(toggle_row)
        layout.addWidget(meta_label)
        layout.addWidget(note_label)
        layout.addWidget(tags_row)
        layout.addWidget(button_row)

        _connect(getattr(toggle, "toggled", None), lambda checked, key=provider.key: self._on_provider_toggled(key, checked))
        _connect(getattr(configure_button, "clicked", None), lambda key=provider.key: self._select_provider(key))

        self._provider_card_widgets[provider.key] = card
        self._provider_card_meta_labels[provider.key] = meta_label
        self._provider_card_note_labels[provider.key] = note_label
        self._provider_card_selected_badges[provider.key] = selected_badge
        self._provider_card_status_badges[provider.key] = status_badge
        self._provider_card_toggles[provider.key] = toggle
        self._provider_card_buttons[provider.key] = configure_button
        return card

    def _build_detail_column(self) -> QWidget:
        """右侧详情列。"""

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        layout.addWidget(self._build_provider_hero())
        layout.addWidget(self._build_credentials_section())
        layout.addWidget(self._build_model_section())
        layout.addWidget(self._build_routing_section())
        layout.addWidget(self._build_quick_config_section())
        layout.addWidget(self._build_role_section())
        return container

    def _build_provider_hero(self) -> QWidget:
        """详情头部卡片。"""

        card = QFrame(self)
        _call(card, "setObjectName", "aiProviderHero")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)

        header_row = QWidget(card)
        header_layout = QHBoxLayout(header_row)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_MD)

        self._detail_icon_label = QLabel("◎", header_row)
        title_host = QWidget(header_row)
        title_layout = QVBoxLayout(title_host)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_XS)

        self._detail_name_label = QLabel("-", title_host)
        self._detail_subtitle_label = QLabel("-", title_host)
        self._detail_status_badge = StatusBadge("待配置", "neutral", header_row)

        title_layout.addWidget(self._detail_name_label)
        title_layout.addWidget(self._detail_subtitle_label)

        header_layout.addWidget(self._detail_icon_label)
        header_layout.addWidget(title_host, 1)
        header_layout.addWidget(self._detail_status_badge)

        self._detail_description_label = QLabel("", card)
        _set_word_wrap(self._detail_description_label)

        self._detail_route_label = QLabel("", card)
        self._detail_connection_label = QLabel("", card)
        self._detail_compliance_label = QLabel("", card)
        _set_word_wrap(self._detail_route_label)
        _set_word_wrap(self._detail_connection_label)
        _set_word_wrap(self._detail_compliance_label)

        layout.addWidget(header_row)
        layout.addWidget(self._detail_description_label)
        layout.addWidget(self._build_divider(card))
        layout.addWidget(self._detail_route_label)
        layout.addWidget(self._detail_connection_label)
        layout.addWidget(self._detail_compliance_label)
        return card

    def _build_credentials_section(self) -> QWidget:
        """凭证与地址区。"""

        section = ContentSection("凭证与接入地址", icon="🔐", parent=self)

        self._primary_key_input = ThemedLineEdit(
            label="主 API Key",
            placeholder="请输入主凭证",
            helper_text="用于生产主链路的鉴权凭证。",
        )
        self._backup_key_input = ThemedLineEdit(
            label="补充凭证 / 组织 ID",
            placeholder="请输入备用凭证或组织标识",
            helper_text="用于项目级回退、团队级路由或组织范围控制。",
        )
        self._base_url_input = ThemedLineEdit(
            label="Base URL / 网关地址",
            placeholder="请输入基础接入地址",
            helper_text="当使用兼容网关或自定义代理时，请填写完整前缀。",
        )
        self._workspace_input = ThemedLineEdit(
            label="工作空间 / 备注",
            placeholder="请输入账号、区域或说明",
            helper_text="建议记录区域、项目、代理池或用途，便于排障。",
        )

        self._apply_secret_echo(self._primary_key_input)
        self._apply_secret_echo(self._backup_key_input)

        for widget in (
            self._primary_key_input,
            self._backup_key_input,
            self._base_url_input,
            self._workspace_input,
        ):
            section.add_widget(widget)

        action_row = QWidget(section)
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(SPACING_MD)

        self._enable_toggle = ToggleSwitch(True)
        enable_label = QLabel("启用该供应商", action_row)
        self._default_toggle = ToggleSwitch(False)
        default_label = QLabel("设为系统默认", action_row)

        self._test_button = PrimaryButton("测试连接", action_row, icon_text="⇄")
        self._set_default_button = SecondaryButton("设为默认供应商", action_row, icon_text="★")

        _connect(getattr(self._enable_toggle, "toggled", None), self._on_enable_toggle_changed)
        _connect(getattr(self._default_toggle, "toggled", None), self._on_default_toggle_changed)
        _connect(getattr(self._test_button, "clicked", None), self._run_connection_test)
        _connect(getattr(self._set_default_button, "clicked", None), self._set_selected_provider_as_default)

        action_layout.addWidget(self._enable_toggle)
        action_layout.addWidget(enable_label)
        action_layout.addSpacing(SPACING_LG)
        action_layout.addWidget(self._default_toggle)
        action_layout.addWidget(default_label)
        action_layout.addStretch(1)
        action_layout.addWidget(self._set_default_button)
        action_layout.addWidget(self._test_button)
        section.add_widget(action_row)
        return section

    def _apply_secret_echo(self, input_widget: ThemedLineEdit | None) -> None:
        """对密钥输入启用掩码。"""

        if input_widget is None:
            return
        echo_namespace = getattr(QLineEdit, "EchoMode", None)
        password_mode = getattr(echo_namespace, "Password", 2)
        _call(input_widget.line_edit, "setEchoMode", password_mode)

    def _build_model_section(self) -> QWidget:
        """模型选择区。"""

        section = ContentSection("模型选择与推荐", icon="⚙", parent=self)

        intro = QLabel("为每个供应商维护主模型、备用模型、已激活模型标签与模型能力说明。", section)
        _set_word_wrap(intro)
        section.add_widget(intro)

        self._selected_models_host = QWidget(section)
        selected_models_layout = QHBoxLayout(self._selected_models_host)
        if selected_models_layout is not None:
            selected_models_layout.setContentsMargins(0, 0, 0, 0)
            selected_models_layout.setSpacing(SPACING_SM)
        self._selected_models_layout = selected_models_layout
        section.add_widget(self._selected_models_host)

        model_form_row = QWidget(section)
        model_form_layout = QHBoxLayout(model_form_row)
        model_form_layout.setContentsMargins(0, 0, 0, 0)
        model_form_layout.setSpacing(SPACING_LG)

        self._primary_model_combo = ThemedComboBox(label="主模型")
        self._fallback_model_combo = ThemedComboBox(label="备用模型")
        model_form_layout.addWidget(self._primary_model_combo, 1)
        model_form_layout.addWidget(self._fallback_model_combo, 1)

        _connect(getattr(self._primary_model_combo.combo_box, "currentTextChanged", None), self._on_primary_model_changed)
        _connect(getattr(self._fallback_model_combo.combo_box, "currentTextChanged", None), self._on_fallback_model_changed)

        section.add_widget(model_form_row)

        comparison_group = FormGroup(
            label="模型能力对比",
            description="以下内容用于帮助运营同学快速判断不同模型适合的场景、上下文和成本倾向。",
            parent=section,
        )
        self._model_rows_host = QWidget(comparison_group)
        model_rows_layout = QVBoxLayout(self._model_rows_host)
        if model_rows_layout is not None:
            model_rows_layout.setContentsMargins(0, 0, 0, 0)
            model_rows_layout.setSpacing(SPACING_MD)
        self._model_rows_layout = model_rows_layout
        comparison_group.set_field_widget(self._model_rows_host)
        section.add_widget(comparison_group)
        return section

    def _build_routing_section(self) -> QWidget:
        """默认路由与回退策略区。"""

        section = ContentSection("默认路由与分发策略", icon="⇆", parent=self)

        intro = QLabel(
            "可在这里设定默认供应商、任务分发模式以及请求失败时的回退方案。页面中所有数据均为演示值，但结构遵循实际系统管理页要求。",
            section,
        )
        _set_word_wrap(intro)
        section.add_widget(intro)

        self._routing_mode_combo = ThemedComboBox(
            label="任务分发模式",
            items=["主模型优先", "按成本优先", "按可用性优先", "手动固定当前供应商"],
        )
        section.add_widget(self._routing_mode_combo)

        bullet_group = FormGroup(
            label="当前策略说明",
            description="会根据当前选中的供应商同步展示实际建议。",
            parent=section,
        )
        bullet_host = QWidget(bullet_group)
        bullet_layout = QVBoxLayout(bullet_host)
        bullet_layout.setContentsMargins(0, 0, 0, 0)
        bullet_layout.setSpacing(SPACING_SM)
        for text in (
            "当主模型连接失败时，优先尝试同供应商备用模型，再按兼容线路回退。",
            "对高价值创作任务保留更高质量模型；批量任务优先轻量模型以控制成本。",
            "本地 Ollama 适用于敏感数据草稿，不建议直接替代线上主生产模型。",
        ):
            bullet_layout.addWidget(self._build_bullet_note(bullet_host, text))
        bullet_group.set_field_widget(bullet_host)
        section.add_widget(bullet_group)
        return section

    def _build_quick_config_section(self) -> QWidget:
        """右侧快速参数面板。"""

        section = ContentSection("采样参数与快速配置", icon="☷", parent=self)
        intro = QLabel("下方配置面板来自已有 AI 组件，可快速设置供应商、模型、角色、温度、Top-p 与最大 Token。", section)
        _set_word_wrap(intro)
        section.add_widget(intro)

        self._ai_config_panel = AIConfigPanel(section)
        _connect(getattr(self._ai_config_panel, "config_changed", None), self._on_ai_config_changed)
        section.add_widget(self._ai_config_panel)
        return section

    def _build_role_section(self) -> QWidget:
        """角色预设区。"""

        section = ContentSection("智能体角色预设", icon="✧", parent=self)
        intro = QLabel("将供应商与角色预设绑定，确保不同岗位调用到合适的模型、温度和输出风格。", section)
        _set_word_wrap(intro)
        section.add_widget(intro)

        self._agent_selector = AgentRoleSelector(section)
        _connect(getattr(self._agent_selector, "role_selected", None), self._on_role_selected)
        section.add_widget(self._agent_selector)

        self._role_summary_label = QLabel("", section)
        self._role_playbook_label = QLabel("", section)
        _set_word_wrap(self._role_summary_label)
        _set_word_wrap(self._role_playbook_label)
        section.add_widget(self._role_summary_label)
        section.add_widget(self._role_playbook_label)

        role_group = FormGroup(
            label="当前供应商推荐预设",
            description="根据所选供应商列出 3 条建议预设，可作为默认模板直接落地。",
            parent=section,
        )
        self._role_rows_host = QWidget(role_group)
        role_rows_layout = QVBoxLayout(self._role_rows_host)
        if role_rows_layout is not None:
            role_rows_layout.setContentsMargins(0, 0, 0, 0)
            role_rows_layout.setSpacing(SPACING_MD)
        self._role_rows_layout = role_rows_layout
        role_group.set_field_widget(self._role_rows_host)
        section.add_widget(role_group)
        return section

    def _build_validation_bar(self) -> QWidget:
        """底部连接状态条。"""

        bar = QFrame(self)
        _call(bar, "setObjectName", "aiProviderValidationBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_XL)

        self._validation_connection_value = QLabel("待校验", bar)
        self._validation_fields_value = QLabel("0/0", bar)
        self._validation_time_value = QLabel("未执行", bar)
        self._validation_hint_label = QLabel("请先选择供应商并进行连接测试。", bar)
        _set_word_wrap(self._validation_hint_label)

        refresh_button = SecondaryButton("刷新校验状态", bar, icon_text="↻")
        _connect(getattr(refresh_button, "clicked", None), self._run_connection_test)

        for title, value in (
            ("连接状态", self._validation_connection_value),
            ("字段校验", self._validation_fields_value),
            ("最近校验", self._validation_time_value),
        ):
            item = self._build_validation_item(bar, title, value)
            layout.addWidget(item)

        layout.addWidget(self._build_vertical_divider(bar))
        layout.addWidget(self._validation_hint_label, 1)
        layout.addWidget(refresh_button)
        return bar

    def _build_validation_item(self, parent: QWidget, title: str, value_label: QLabel) -> QWidget:
        """底部状态条单项。"""

        item = QWidget(parent)
        layout = QVBoxLayout(item)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XS)
        title_label = QLabel(title, item)
        _call(title_label, "setObjectName", "aiProviderValidationTitle")
        _call(value_label, "setObjectName", "aiProviderValidationValue")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return item

    def _build_divider(self, parent: QWidget) -> QWidget:
        """横向分隔线。"""

        line = QFrame(parent)
        _call(line, "setObjectName", "aiProviderDivider")
        _call(line, "setFixedHeight", 1)
        return line

    def _build_vertical_divider(self, parent: QWidget) -> QWidget:
        """纵向分隔线。"""

        line = QFrame(parent)
        _call(line, "setObjectName", "aiProviderVerticalDivider")
        _call(line, "setFixedWidth", 1)
        return line

    def _apply_provider_filters(self) -> None:
        """根据搜索词和筛选项控制左侧卡片显隐。"""

        keyword = self._search_bar.text().strip().lower() if self._search_bar is not None else ""
        filter_value = self._filter_dropdown.current_text() if self._filter_dropdown is not None else "全部"

        for key, card in self._provider_card_widgets.items():
            provider = self._provider_lookup[key]
            haystack = " ".join(
                [
                    provider.name,
                    provider.subtitle,
                    provider.description,
                    provider.card_meta,
                    provider.sync_note,
                    provider.base_url,
                    *provider.selected_models,
                ]
            ).lower()
            matches_keyword = not keyword or keyword in haystack
            matches_filter = self._matches_filter(provider, filter_value)
            _set_visible(card, matches_keyword and matches_filter)

        for row_widget, keys in self._provider_row_registry:
            visible = False
            for key in keys:
                card = self._provider_card_widgets.get(key)
                if card is None:
                    continue
                hidden_reader = getattr(card, "isHidden", None)
                if callable(hidden_reader):
                    if not hidden_reader():
                        visible = True
                        break
                else:
                    visible = True
                    break
            _set_visible(row_widget, visible)

    def _matches_filter(self, provider: ProviderRecord, filter_value: str) -> bool:
        """判断单个供应商是否满足筛选。"""

        if filter_value == "全部":
            return True
        if filter_value == "已启用":
            return provider.enabled
        if filter_value == "未启用":
            return not provider.enabled
        if filter_value == "默认":
            return provider.is_default
        if filter_value == "需关注":
            return provider.health in {"syncing", "error", "offline"}
        return True

    def _refresh_summary_strip(self) -> None:
        """刷新顶部四个概览卡。"""

        enabled_count = sum(1 for provider in self._providers if provider.enabled)
        default_provider = self._default_provider()
        flagged_count = sum(1 for provider in self._providers if provider.health in {"syncing", "error", "offline"})

        self._set_stat_tile_value(self._provider_count_label, str(len(self._providers)))
        self._set_stat_tile_value(self._enabled_count_label, f"{enabled_count} 个")
        self._set_stat_tile_value(self._default_provider_label, default_provider.name)
        self._set_stat_tile_value(self._sync_summary_label, f"{flagged_count} 个待关注")

        if self._global_status_indicator is not None:
            self._global_status_indicator.set_status(STATUS_INDICATOR_COPY[self._current_provider().health])

    def _set_stat_tile_value(self, card: QWidget | None, value: str) -> None:
        """更新统计卡的数值部分。"""

        if card is None:
            return
        children = getattr(card, "findChildren", None)
        if callable(children):
            matches = children(QLabel)
            if isinstance(matches, list) and len(matches) >= 2:
                matches[1].setText(value)

    def _refresh_provider_cards(self) -> None:
        """刷新左侧卡片的选中态与状态文案。"""

        for provider in self._providers:
            card = self._provider_card_widgets.get(provider.key)
            if card is None:
                continue
            is_selected = provider.key == self._selected_provider_key
            border_color = _token("brand.primary") if is_selected else _token("border.default")
            background = _rgba(_token("brand.primary"), 0.08) if is_selected else _token("surface.secondary")
            accent_text = _token("brand.primary") if is_selected else _token("text.primary")

            _call(
                card,
                "setStyleSheet",
                f"""
                QFrame#{card.objectName()} {{
                    background-color: {background};
                    border: 1px solid {border_color};
                    border-radius: {RADIUS_XL}px;
                }}
                QLabel#providerCardName {{
                    color: {accent_text};
                    font-size: {STATIC_TOKENS['font.size.lg']};
                    font-weight: {STATIC_TOKENS['font.weight.bold']};
                    background: transparent;
                }}
                QLabel#providerCardSubtitle {{
                    color: {_token('text.secondary')};
                    font-size: {STATIC_TOKENS['font.size.sm']};
                    background: transparent;
                }}
                QLabel#providerCardDescription,
                QLabel#providerCardMeta,
                QLabel#providerCardNote,
                QLabel#providerCardToggleHint,
                QLabel#providerCardDefaultHint {{
                    color: {_token('text.secondary')};
                    font-size: {STATIC_TOKENS['font.size.sm']};
                    background: transparent;
                }}
                QLabel#providerCardSelected {{
                    color: {_token('text.inverse')};
                    background-color: {_token('brand.primary')};
                    border-radius: {RADIUS_LG}px;
                    padding: {SPACING_XS}px {SPACING_MD}px;
                    font-size: {STATIC_TOKENS['font.size.sm']};
                    font-weight: {STATIC_TOKENS['font.weight.semibold']};
                }}
                """,
            )

            selected_badge = self._provider_card_selected_badges.get(provider.key)
            if selected_badge is not None:
                _set_visible(selected_badge, is_selected)

            status_badge = self._provider_card_status_badges.get(provider.key)
            if status_badge is not None:
                status_badge.setText(provider.status_label)
                status_badge.set_tone(provider.status_tone)

            meta_label = self._provider_card_meta_labels.get(provider.key)
            if meta_label is not None:
                meta_label.setText(provider.card_meta)

            note_label = self._provider_card_note_labels.get(provider.key)
            if note_label is not None:
                note_label.setText(provider.sync_note)

            toggle = self._provider_card_toggles.get(provider.key)
            if toggle is not None and toggle.isChecked() != provider.enabled:
                toggle.setChecked(provider.enabled)

            button = self._provider_card_buttons.get(provider.key)
            if button is not None:
                button.set_label_text("当前供应商" if is_selected else "查看并配置")

    def _refresh_detail_panel(self) -> None:
        """刷新右侧详情内容。"""

        provider = self._current_provider()

        if self._detail_icon_label is not None:
            self._detail_icon_label.setText(provider.brand_icon)
            _call(
                self._detail_icon_label,
                "setStyleSheet",
                f"font-size: {STATIC_TOKENS['font.size.xxl']}; color: {_token('brand.primary')}; background: transparent;",
            )
        if self._detail_name_label is not None:
            self._detail_name_label.setText(provider.name)
            _call(
                self._detail_name_label,
                "setStyleSheet",
                f"font-size: {STATIC_TOKENS['font.size.xxl']}; font-weight: {STATIC_TOKENS['font.weight.bold']}; color: {_token('text.primary')}; background: transparent;",
            )
        if self._detail_subtitle_label is not None:
            self._detail_subtitle_label.setText(provider.subtitle)
            _call(
                self._detail_subtitle_label,
                "setStyleSheet",
                f"font-size: {STATIC_TOKENS['font.size.md']}; color: {_token('text.secondary')}; background: transparent;",
            )
        if self._detail_status_badge is not None:
            self._detail_status_badge.setText(provider.status_label)
            self._detail_status_badge.set_tone(provider.status_tone)
        if self._detail_description_label is not None:
            self._detail_description_label.setText(provider.description)
            _call(
                self._detail_description_label,
                "setStyleSheet",
                f"font-size: {STATIC_TOKENS['font.size.md']}; color: {_token('text.secondary')}; background: transparent;",
            )
        if self._detail_route_label is not None:
            route_label = "当前为系统默认供应商。" if provider.is_default else f"当前默认供应商为 {self._default_provider().name}，可在此切换。"
            self._detail_route_label.setText(f"默认路由：{route_label}")
            _call(self._detail_route_label, "setStyleSheet", f"color: {_token('text.primary')}; background: transparent;")
        if self._detail_connection_label is not None:
            self._detail_connection_label.setText(f"连接状态：{provider.connection_status}")
            _call(self._detail_connection_label, "setStyleSheet", f"color: {_token('text.primary')}; background: transparent;")
        if self._detail_compliance_label is not None:
            self._detail_compliance_label.setText(f"安全与说明：{provider.compliance_note}")
            _call(self._detail_compliance_label, "setStyleSheet", f"color: {_token('text.secondary')}; background: transparent;")

        if self._primary_key_input is not None:
            self._primary_key_input.setText(provider.primary_key)
            self._primary_key_input.set_helper_text(f"{provider.name} 的主鉴权凭证，用于正式请求。")
        if self._backup_key_input is not None:
            self._backup_key_input.setText(provider.backup_key)
            self._backup_key_input.set_helper_text("可填写项目级备用 Key、组织标识或网关路由参数。")
        if self._base_url_input is not None:
            self._base_url_input.setText(provider.base_url)
            self._base_url_input.set_helper_text("支持官方 API 地址、自建代理地址或兼容网关前缀。")
        if self._workspace_input is not None:
            self._workspace_input.setText(provider.workspace_hint)
            self._workspace_input.set_helper_text("建议记录区域、用途、账号归属或运营线，以便排查。")

        if self._enable_toggle is not None and self._enable_toggle.isChecked() != provider.enabled:
            self._enable_toggle.setChecked(provider.enabled)
        if self._default_toggle is not None and self._default_toggle.isChecked() != provider.is_default:
            self._default_toggle.setChecked(provider.is_default)
        if self._set_default_button is not None:
            self._set_default_button.set_label_text("已是默认供应商" if provider.is_default else "设为默认供应商")

        self._populate_model_combos(provider)
        self._refresh_selected_model_chips(provider)
        self._refresh_model_rows(provider)
        self._refresh_role_summary(provider)
        self._refresh_role_rows(provider)
        self._sync_ai_config_panel(provider)
        self._refresh_validation_bar(provider)
        self._refresh_summary_strip()
        self.provider_selected.emit(provider.key)

    def _populate_model_combos(self, provider: ProviderRecord) -> None:
        """将当前供应商的模型写入下拉。"""

        if self._primary_model_combo is None or self._fallback_model_combo is None:
            return
        self._syncing_model_combos = True
        try:
            self._reset_combo_items(self._primary_model_combo, [model.model_id for model in provider.models], provider.primary_model)
            self._reset_combo_items(self._fallback_model_combo, [model.model_id for model in provider.models], provider.fallback_model)
        finally:
            self._syncing_model_combos = False

    def _reset_combo_items(self, combo: ThemedComboBox, items: list[str], current_text: str) -> None:
        """重置下拉选项。"""

        combo_box = combo.combo_box
        _call(combo_box, "clear")
        add_items = getattr(combo_box, "addItems", None)
        if callable(add_items):
            add_items(items)
        else:
            for item in items:
                _call(combo_box, "addItem", item)
        _call(combo_box, "setCurrentText", current_text)

    def _refresh_selected_model_chips(self, provider: ProviderRecord) -> None:
        """刷新已激活模型标签。"""

        if self._selected_models_layout is None or self._selected_models_host is None:
            return
        for chip in list(self._selected_model_chips):
            _call(chip, "deleteLater")
        self._selected_model_chips.clear()
        _clear_layout(self._selected_models_layout)

        label = QLabel("当前激活模型：", self._selected_models_host)
        _call(label, "setObjectName", "aiProviderSelectedModelsTitle")
        self._selected_models_layout.addWidget(label)
        for model_id in provider.selected_models:
            tone: ProviderTone = "brand" if model_id == provider.primary_model else "neutral"
            chip = TagChip(model_id, tone=tone, parent=self._selected_models_host)
            self._selected_model_chips.append(chip)
            self._selected_models_layout.addWidget(chip)
        self._selected_models_layout.addStretch(1)

    def _refresh_model_rows(self, provider: ProviderRecord) -> None:
        """刷新模型能力说明行。"""

        if self._model_rows_layout is None or self._model_rows_host is None:
            return
        _clear_layout(self._model_rows_layout)
        for model in provider.models:
            row = QFrame(self._model_rows_host)
            _call(row, "setObjectName", "aiProviderModelRow")
            layout = QVBoxLayout(row)
            layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
            layout.setSpacing(SPACING_XS)

            title = QLabel(f"{model.display_name}（{model.model_id}）", row)
            meta = QLabel(f"上下文：{model.context_window} · 适用：{model.best_for} · 延迟：{model.latency_hint} · 成本倾向：{model.price_hint}", row)
            desc = QLabel(model.summary, row)
            _set_word_wrap(meta)
            _set_word_wrap(desc)

            _call(title, "setObjectName", "aiProviderModelRowTitle")
            _call(meta, "setObjectName", "aiProviderModelRowMeta")
            _call(desc, "setObjectName", "aiProviderModelRowDesc")

            layout.addWidget(title)
            layout.addWidget(meta)
            layout.addWidget(desc)
            self._model_rows_layout.addWidget(row)

    def _sync_ai_config_panel(self, provider: ProviderRecord) -> None:
        """同步已有 AIConfigPanel 的值。"""

        if self._ai_config_panel is None:
            return
        self._syncing_panel = True
        self._ai_config_panel.set_config(
            {
                "provider": provider.key,
                "model": provider.primary_model,
                "agent_role": self._selected_role_name,
                "temperature": self._recommended_temperature(provider),
                "max_tokens": self._recommended_max_tokens(provider),
                "top_p": self._recommended_top_p(provider),
            }
        )
        self._syncing_panel = False

    def _recommended_temperature(self, provider: ProviderRecord) -> float:
        """按当前角色返回建议温度。"""

        for preset in provider.role_presets:
            if preset.role_name == self._selected_role_name:
                return preset.temperature
        return provider.role_presets[0].temperature if provider.role_presets else 0.7

    def _recommended_top_p(self, provider: ProviderRecord) -> float:
        """按当前角色返回建议 top-p。"""

        for preset in provider.role_presets:
            if preset.role_name == self._selected_role_name:
                return preset.top_p
        return provider.role_presets[0].top_p if provider.role_presets else 0.9

    def _recommended_max_tokens(self, provider: ProviderRecord) -> int:
        """按当前角色返回建议 max_tokens。"""

        for preset in provider.role_presets:
            if preset.role_name == self._selected_role_name:
                return preset.max_tokens
        return provider.role_presets[0].max_tokens if provider.role_presets else 2048

    def _refresh_role_summary(self, provider: ProviderRecord) -> None:
        """刷新角色摘要说明。"""

        if self._role_summary_label is not None:
            self._role_summary_label.setText(f"当前角色：{self._selected_role_name} · 推荐供应商：{provider.name} · 主模型：{provider.primary_model}")
            _call(
                self._role_summary_label,
                "setStyleSheet",
                f"color: {_token('text.primary')}; font-size: {STATIC_TOKENS['font.size.md']}; font-weight: {STATIC_TOKENS['font.weight.semibold']}; background: transparent;",
            )
        if self._role_playbook_label is not None:
            self._role_playbook_label.setText(ROLE_PLAYBOOK.get(self._selected_role_name, ROLE_PLAYBOOK["自定义角色"]))
            _call(self._role_playbook_label, "setStyleSheet", f"color: {_token('text.secondary')}; background: transparent;")

    def _refresh_role_rows(self, provider: ProviderRecord) -> None:
        """刷新供应商推荐角色列表。"""

        if self._role_rows_layout is None or self._role_rows_host is None:
            return
        _clear_layout(self._role_rows_layout)
        for preset in provider.role_presets:
            row = QFrame(self._role_rows_host)
            _call(row, "setObjectName", "aiProviderPresetRow")
            layout = QHBoxLayout(row)
            layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
            layout.setSpacing(SPACING_LG)

            title_host = QWidget(row)
            title_layout = QVBoxLayout(title_host)
            title_layout.setContentsMargins(0, 0, 0, 0)
            title_layout.setSpacing(SPACING_XS)
            title = QLabel(f"{preset.role_name} · 推荐模型 {preset.preferred_model}", title_host)
            desc = QLabel(preset.summary, title_host)
            meta = QLabel(
                f"温度 {preset.temperature:.1f} · Top-p {preset.top_p:.2f} · 最大 Token {preset.max_tokens}",
                title_host,
            )
            _set_word_wrap(desc)
            _set_word_wrap(meta)
            _call(title, "setObjectName", "aiProviderPresetTitle")
            _call(desc, "setObjectName", "aiProviderPresetDesc")
            _call(meta, "setObjectName", "aiProviderPresetMeta")
            title_layout.addWidget(title)
            title_layout.addWidget(desc)
            title_layout.addWidget(meta)

            badge_tone: ProviderTone = "brand" if preset.role_name == self._selected_role_name else "neutral"
            badge = StatusBadge("当前角色" if preset.role_name == self._selected_role_name else "推荐模板", badge_tone)

            layout.addWidget(title_host, 1)
            layout.addWidget(badge)
            self._role_rows_layout.addWidget(row)

    def _refresh_validation_bar(self, provider: ProviderRecord) -> None:
        """刷新底部验证条。"""

        if self._validation_connection_value is not None:
            self._validation_connection_value.setText(provider.connection_status)
        if self._validation_fields_value is not None:
            self._validation_fields_value.setText(provider.validation_text)
        if self._validation_time_value is not None:
            self._validation_time_value.setText(provider.last_validated)
        if self._validation_hint_label is not None:
            self._validation_hint_label.setText(provider.sync_note)

    def _select_provider(self, provider_key: str) -> None:
        """切换当前供应商。"""

        if provider_key not in self._provider_lookup:
            return
        self._selected_provider_key = provider_key
        self._refresh_provider_cards()
        self._refresh_detail_panel()

    def _on_provider_toggled(self, provider_key: str, checked: bool) -> None:
        """处理左侧卡片启用切换。"""

        provider = self._provider_lookup[provider_key]
        provider.enabled = checked
        if checked:
            provider.health = "ready" if provider.health == "offline" else provider.health
            provider.status_label = "生产环境可用" if provider.key == "openai" else "已启用"
            provider.status_tone = "success" if provider.health == "ready" else "warning"
        else:
            provider.health = "offline"
            provider.status_label = "已停用"
            provider.status_tone = "neutral"
        if provider_key == self._selected_provider_key:
            self._refresh_detail_panel()
        self._refresh_provider_cards()
        self._refresh_summary_strip()
        self._apply_provider_filters()

    def _on_enable_toggle_changed(self, checked: bool) -> None:
        """处理右侧启用切换。"""

        provider = self._current_provider()
        provider.enabled = checked
        provider.health = "ready" if checked else "offline"
        provider.status_label = "已启用" if checked else "已停用"
        provider.status_tone = "success" if checked else "neutral"
        toggle = self._provider_card_toggles.get(provider.key)
        if toggle is not None and toggle.isChecked() != checked:
            toggle.setChecked(checked)
        self._refresh_provider_cards()
        self._refresh_detail_panel()
        self._apply_provider_filters()

    def _on_default_toggle_changed(self, checked: bool) -> None:
        """右侧默认开关联动。"""

        if not checked:
            current = self._current_provider()
            if current.is_default and self._default_toggle is not None:
                self._default_toggle.setChecked(True)
            return
        self._set_selected_provider_as_default()

    def _set_selected_provider_as_default(self) -> None:
        """将当前供应商设为默认。"""

        selected = self._current_provider()
        for provider in self._providers:
            provider.is_default = provider.key == selected.key
        selected.sync_note = f"已设为系统默认供应商，优先承接 {self._selected_role_name} 与主生产链路请求。"
        self._refresh_provider_cards()
        self._refresh_detail_panel()

    def _run_connection_test(self) -> None:
        """模拟连接测试。"""

        provider = self._current_provider()
        provider.last_validated = datetime.now().strftime("%H:%M:%S")
        if not provider.enabled:
            provider.health = "offline"
            provider.status_label = "未启用，跳过测试"
            provider.status_tone = "neutral"
            provider.connection_status = "当前供应商已停用，系统未发起真实连接测试。"
            provider.validation_text = "2/6 项通过，需先启用后再测试。"
        elif provider.key == "ollama":
            provider.health = "syncing"
            provider.status_label = "本地节点预热中"
            provider.status_tone = "warning"
            provider.connection_status = "已探测到本地节点，但模型仍在预热；建议稍后再次校验。"
            provider.validation_text = "5/6 项通过，等待模型缓存完成。"
        elif provider.key == "openai-compatible":
            provider.health = "error"
            provider.status_label = "网关需补白名单"
            provider.status_tone = "warning"
            provider.connection_status = "TLS 握手成功，但请求被上游策略拦截；请补充白名单与代理规则。"
            provider.validation_text = "4/6 项通过，域名与 Key 有效，代理策略待修复。"
        else:
            provider.health = "ready"
            provider.status_label = "连接测试通过"
            provider.status_tone = "success"
            provider.connection_status = f"{provider.name} 连接测试成功，主模型 {provider.primary_model} 已完成可用性校验。"
            provider.validation_text = "6/6 项关键字段已通过校验。"
        self._refresh_provider_cards()
        self._refresh_detail_panel()

    def _simulate_restart(self) -> None:
        """模拟重载服务。"""

        provider = self._current_provider()
        provider.sync_note = f"{provider.name} 相关服务已执行模拟重载，建议再次点击“测试连接”确认链路稳定。"
        self._refresh_provider_cards()
        self._refresh_detail_panel()

    def _restore_demo_defaults(self) -> None:
        """恢复示例数据。"""

        for index, source in enumerate(PROVIDER_DEMOS):
            target = self._providers[index]
            target.name = source.name
            target.brand_icon = source.brand_icon
            target.subtitle = source.subtitle
            target.description = source.description
            target.status_label = source.status_label
            target.status_tone = source.status_tone
            target.health = source.health
            target.enabled = source.enabled
            target.is_default = source.is_default
            target.base_url = source.base_url
            target.primary_key = source.primary_key
            target.backup_key = source.backup_key
            target.workspace_hint = source.workspace_hint
            target.selected_models = list(source.selected_models)
            target.primary_model = source.primary_model
            target.fallback_model = source.fallback_model
            target.connection_status = source.connection_status
            target.validation_text = source.validation_text
            target.last_validated = source.last_validated
            target.card_meta = source.card_meta
            target.sync_note = source.sync_note
            target.compliance_note = source.compliance_note
            target.models = list(source.models)
            target.role_presets = list(source.role_presets)
            target.capability_tags = list(source.capability_tags)
            target.notes = list(source.notes)
        self._selected_provider_key = self._default_provider().key
        self._selected_role_name = "文案专家"
        if self._agent_selector is not None:
            self._agent_selector.set_active_role(self._selected_role_name)
        self._apply_provider_filters()
        self._refresh_provider_cards()
        self._refresh_detail_panel()

    def _save_changes(self) -> None:
        """模拟保存。"""

        provider = self._current_provider()
        provider.last_validated = "刚刚保存"
        provider.status_label = "已保存待验证"
        provider.status_tone = "brand"
        provider.connection_status = f"{provider.name} 配置已保存到本地演示状态，请执行连接测试完成最终验证。"
        provider.validation_text = "配置已写入，建议立即执行 1 次连接测试。"
        self._refresh_provider_cards()
        self._refresh_detail_panel()

    def _on_primary_model_changed(self, model_id: str) -> None:
        """切换主模型。"""

        if self._syncing_model_combos:
            return
        if not model_id:
            return
        provider = self._current_provider()
        provider.primary_model = model_id
        if model_id not in provider.selected_models:
            provider.selected_models.insert(0, model_id)
        provider.card_meta = f"{len(provider.selected_models)} 个模型已激活 · 主模型 {provider.primary_model}"
        self._refresh_provider_cards()
        self._refresh_detail_panel()

    def _on_fallback_model_changed(self, model_id: str) -> None:
        """切换备用模型。"""

        if self._syncing_model_combos:
            return
        if not model_id:
            return
        provider = self._current_provider()
        provider.fallback_model = model_id
        if model_id not in provider.selected_models:
            provider.selected_models.append(model_id)
        provider.sync_note = f"主模型为 {provider.primary_model}，备用模型为 {provider.fallback_model}，可用于失败重试与峰值回退。"
        self._refresh_provider_cards()
        self._refresh_detail_panel()

    def _on_ai_config_changed(self, config: Mapping[str, object]) -> None:
        """同步 AIConfigPanel 变更。"""

        if self._syncing_panel:
            return
        provider_key = str(config.get("provider", self._selected_provider_key))
        if provider_key in self._provider_lookup and provider_key != self._selected_provider_key:
            self._selected_provider_key = provider_key

        provider = self._current_provider()
        model_value = str(config.get("model", provider.primary_model))
        role_value = str(config.get("agent_role", self._selected_role_name))
        provider.primary_model = model_value
        if model_value not in provider.selected_models:
            provider.selected_models.insert(0, model_value)
        self._selected_role_name = role_value

        if self._agent_selector is not None and self._agent_selector.current_role() != role_value:
            self._agent_selector.set_active_role(role_value)

        temperature_value = _as_float(config.get("temperature", 0.7), 0.7)
        top_p_value = _as_float(config.get("top_p", 0.9), 0.9)
        max_tokens_value = _as_int(config.get("max_tokens", 2048), 2048)
        provider.sync_note = (
            f"快速配置已同步：角色 {role_value} · 温度 {temperature_value:.1f} · "
            f"Top-p {top_p_value:.2f} · 最大 Token {max_tokens_value}"
        )
        self._refresh_provider_cards()
        self._refresh_detail_panel()

    def _on_role_selected(self, role_name: str) -> None:
        """更新当前角色。"""

        self._selected_role_name = role_name
        self._refresh_detail_panel()

    def _on_search_changed(self, _text: str) -> None:
        """搜索变更。"""

        self._apply_provider_filters()

    def _on_filter_changed(self, _text: str) -> None:
        """筛选变更。"""

        self._apply_provider_filters()

    def _apply_page_styles(self) -> None:
        """应用页面级样式。"""

        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#aiProviderPage {{
                background-color: {_token('surface.primary')};
            }}
            QWidget#aiProviderPage QFrame#contentSection {{
                background-color: {_token('surface.secondary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_XL}px;
            }}
            QFrame#aiProviderNotice {{
                background-color: {_rgba(_token('status.warning'), 0.12)};
                border: 1px solid {_rgba(_token('status.warning'), 0.28)};
                border-radius: {RADIUS_XL}px;
            }}
            QLabel#aiProviderNoticeIcon {{
                color: {_token('status.warning')};
                font-size: {STATIC_TOKENS['font.size.xl']};
                background: transparent;
            }}
            QLabel#aiProviderNoticeTitle {{
                color: {_token('text.primary')};
                font-size: {STATIC_TOKENS['font.size.md']};
                font-weight: {STATIC_TOKENS['font.weight.bold']};
                background: transparent;
            }}
            QLabel#aiProviderNoticeBody {{
                color: {_token('text.secondary')};
                font-size: {STATIC_TOKENS['font.size.sm']};
                background: transparent;
            }}
            QFrame#aiProviderStatTile {{
                background-color: {_token('surface.secondary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_XL}px;
            }}
            QLabel#aiProviderStatTitle {{
                color: {_token('text.secondary')};
                font-size: {STATIC_TOKENS['font.size.sm']};
                background: transparent;
            }}
            QLabel#aiProviderStatValue {{
                color: {_token('text.primary')};
                font-size: {STATIC_TOKENS['font.size.xxl']};
                font-weight: {STATIC_TOKENS['font.weight.bold']};
                background: transparent;
            }}
            QLabel#aiProviderStatDesc {{
                color: {_token('text.secondary')};
                font-size: {STATIC_TOKENS['font.size.sm']};
                background: transparent;
            }}
            QLabel#aiProviderToolbarHint {{
                color: {_token('text.secondary')};
                font-size: {STATIC_TOKENS['font.size.sm']};
                background: transparent;
            }}
            QWidget#aiProviderToolbar,
            QWidget#aiProviderSummaryStrip {{
                background-color: {_token('surface.secondary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_XL}px;
            }}
            QLabel#aiProviderSectionIntro,
            QLabel#aiProviderBulletBody {{
                color: {_token('text.secondary')};
                font-size: {STATIC_TOKENS['font.size.sm']};
                background: transparent;
            }}
            QLabel#aiProviderBullet {{
                color: {_token('brand.primary')};
                font-size: {STATIC_TOKENS['font.size.md']};
                background: transparent;
            }}
            QFrame#aiProviderHero {{
                background-color: {_token('surface.secondary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_XL}px;
            }}
            QFrame#aiProviderValidationBar {{
                background-color: {_token('surface.secondary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_XL}px;
            }}
            QLabel#aiProviderValidationTitle {{
                color: {_token('text.secondary')};
                font-size: {STATIC_TOKENS['font.size.sm']};
                background: transparent;
            }}
            QLabel#aiProviderValidationValue {{
                color: {_token('text.primary')};
                font-size: {STATIC_TOKENS['font.size.md']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
                background: transparent;
            }}
            QFrame#aiProviderDivider,
            QFrame#aiProviderVerticalDivider {{
                background-color: {_token('border.default')};
                border: none;
            }}
            QLabel#aiProviderSelectedModelsTitle {{
                color: {_token('text.primary')};
                font-size: {STATIC_TOKENS['font.size.sm']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
                background: transparent;
            }}
            QFrame#aiProviderModelRow,
            QFrame#aiProviderPresetRow {{
                background-color: {_token('surface.secondary')};
                border: 1px solid {_token('border.default')};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#aiProviderModelRowTitle,
            QLabel#aiProviderPresetTitle {{
                color: {_token('text.primary')};
                font-size: {STATIC_TOKENS['font.size.md']};
                font-weight: {STATIC_TOKENS['font.weight.bold']};
                background: transparent;
            }}
            QLabel#aiProviderModelRowMeta,
            QLabel#aiProviderModelRowDesc,
            QLabel#aiProviderPresetDesc,
            QLabel#aiProviderPresetMeta {{
                color: {_token('text.secondary')};
                font-size: {STATIC_TOKENS['font.size.sm']};
                background: transparent;
            }}
            """,
        )


__all__ = ["AIProviderPage"]
