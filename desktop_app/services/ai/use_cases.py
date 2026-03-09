from __future__ import annotations

# pyright: basic, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportAttributeAccessIssue=false

"""面向 TK-OPS 功能页面的 AI 用例集成模块。"""

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, field

from .config_service import AIConfigService, ProviderSelection
from .provider_adapter import MessagePayload, ProviderAdapter
from .streaming import StreamingAIRuntime


def _clean_text(value: object, *, default: str = "") -> str:
    """将任意输入标准化为去空白字符串。"""

    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _optional_text(value: object) -> str | None:
    """返回可空字符串。"""

    text = _clean_text(value)
    return text or None


def _string_list(value: object) -> list[str]:
    """将输入规整为字符串列表并去重。"""

    if value is None:
        return []
    if isinstance(value, str):
        items = [item.strip() for item in value.replace("\n", "，").split("，")]
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        items = [str(item).strip() for item in value]
    else:
        items = [str(value).strip()]

    result: list[str] = []
    for item in items:
        if item and item not in result:
            result.append(item)
    return result


def _truncate(value: str, *, limit: int) -> str:
    """按字符上限截断文本。"""

    if len(value) <= limit:
        return value
    return value[: max(0, limit - 1)] + "…"


@dataclass(frozen=True)
class PromptEnvelope:
    """统一封装系统提示词、用户提示词与消息载荷。"""

    system_prompt: str
    user_prompt: str
    messages: list[dict[str, object]]


@dataclass(frozen=True)
class RuntimeSnapshot:
    """记录流式运行时的当前摘要。"""

    service_name: str
    can_stream: bool
    is_streaming: bool
    active_stream_count: int
    current_model: str | None
    usage_totals: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class StreamingPlan:
    """供页面层发起流式调用的计划对象。"""

    enabled: bool
    role_name: str
    provider_name: str
    model_name: str
    temperature: float
    runtime: RuntimeSnapshot
    messages: list[dict[str, object]] = field(default_factory=list)
    dispatch_hint: str = "页面层可直接复用该计划发起流式生成。"


@dataclass(frozen=True)
class UseCaseExecutionMeta:
    """描述一次用例执行的模型选择与上下文。"""

    use_case_name: str
    provider_name: str
    model_name: str
    temperature: float
    input_digest: str
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TitleGenerationInput:
    """爆款标题生成输入。"""

    product_name: str
    product_category: str
    selling_points: list[str] = field(default_factory=list)
    audience: str = "泛兴趣电商人群"
    market: str = "美区"
    usage_scene: str = "短视频电商"
    style_keywords: list[str] = field(default_factory=list)
    banned_words: list[str] = field(default_factory=list)
    variant_count: int = 5
    temperature: float = 0.75
    enable_streaming: bool = True


@dataclass(frozen=True)
class TitleVariant:
    """标题候选项。"""

    title: str
    angle: str
    hook: str
    hashtags: list[str] = field(default_factory=list)
    confidence: float = 0.0
    notes: str = ""


@dataclass(frozen=True)
class TitleGenerationResult:
    """爆款标题生成输出。"""

    meta: UseCaseExecutionMeta
    prompt: PromptEnvelope
    streaming: StreamingPlan
    variants: list[TitleVariant] = field(default_factory=list)
    recommended_title: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CopyWritingInput:
    """营销文案生成输入。"""

    product_name: str
    product_category: str
    audience: str
    tone: str
    selling_points: list[str] = field(default_factory=list)
    price_anchor: str | None = None
    promotion_message: str | None = None
    platform_scene: str = "商品卡短文案"
    variant_count: int = 3
    temperature: float = 0.72
    enable_streaming: bool = True


@dataclass(frozen=True)
class CopyVariant:
    """营销文案候选。"""

    headline: str
    body: str
    cta: str
    angle: str
    keywords: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass(frozen=True)
class CopyWritingResult:
    """营销文案生成输出。"""

    meta: UseCaseExecutionMeta
    prompt: PromptEnvelope
    streaming: StreamingPlan
    variants: list[CopyVariant] = field(default_factory=list)
    recommended_summary: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScriptExtractionInput:
    """脚本提炼输入。"""

    video_title: str
    video_description: str = ""
    hashtags: list[str] = field(default_factory=list)
    spoken_keywords: list[str] = field(default_factory=list)
    comments_summary: str = ""
    product_name: str | None = None
    duration_seconds: int | None = None
    temperature: float = 0.35
    enable_streaming: bool = True


@dataclass(frozen=True)
class ScriptSegment:
    """提炼后的脚本片段。"""

    order: int
    stage: str
    text: str
    objective: str


@dataclass(frozen=True)
class ScriptExtractionResult:
    """脚本提炼结果。"""

    meta: UseCaseExecutionMeta
    prompt: PromptEnvelope
    streaming: StreamingPlan
    title: str
    summary: str
    segments: list[ScriptSegment] = field(default_factory=list)
    reconstructed_script: str = ""
    content_tags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CompetitorRecord:
    """竞品基础信息。"""

    name: str
    price_band: str = ""
    selling_points: list[str] = field(default_factory=list)
    content_style: str = ""
    traffic_signals: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass(frozen=True)
class CompetitorAnalysisInput:
    """竞品分析输入。"""

    product_name: str
    product_category: str
    target_market: str
    competitors: list[CompetitorRecord] = field(default_factory=list)
    brand_strengths: list[str] = field(default_factory=list)
    business_goal: str = "提升转化效率"
    temperature: float = 0.4
    enable_streaming: bool = True


@dataclass(frozen=True)
class CompetitorInsight:
    """单个竞品洞察。"""

    competitor_name: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    threats: list[str] = field(default_factory=list)
    recommended_response: str = ""


@dataclass(frozen=True)
class CompetitorAnalysisResult:
    """竞品分析输出。"""

    meta: UseCaseExecutionMeta
    prompt: PromptEnvelope
    streaming: StreamingPlan
    overview: str
    insights: list[CompetitorInsight] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BlueOceanAnalysisInput:
    """蓝海机会分析输入。"""

    product_category: str
    target_audience: str
    target_market: str
    market_signals: list[str] = field(default_factory=list)
    existing_pain_points: list[str] = field(default_factory=list)
    competitor_patterns: list[str] = field(default_factory=list)
    brand_constraints: list[str] = field(default_factory=list)
    temperature: float = 0.55
    enable_streaming: bool = True


@dataclass(frozen=True)
class BlueOceanOpportunity:
    """蓝海机会点。"""

    niche: str
    unmet_need: str
    content_angle: str
    offer_direction: str
    risk_level: str
    next_action: str


@dataclass(frozen=True)
class BlueOceanAnalysisResult:
    """蓝海机会分析输出。"""

    meta: UseCaseExecutionMeta
    prompt: PromptEnvelope
    streaming: StreamingPlan
    summary: str
    opportunities: list[BlueOceanOpportunity] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AutoReplyInput:
    """智能回复输入。"""

    customer_message: str
    scenario: str
    product_name: str
    brand_tone: str
    order_context: str | None = None
    knowledge_points: list[str] = field(default_factory=list)
    variant_count: int = 3
    temperature: float = 0.3
    enable_streaming: bool = True


@dataclass(frozen=True)
class AutoReplySuggestion:
    """智能回复建议。"""

    reply: str
    intent: str
    style: str
    upsell_tip: str | None = None
    risk_flags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AutoReplyResult:
    """智能回复输出。"""

    meta: UseCaseExecutionMeta
    prompt: PromptEnvelope
    streaming: StreamingPlan
    suggestions: list[AutoReplySuggestion] = field(default_factory=list)
    recommended_reply: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ContentComplianceInput:
    """内容合规检测输入。"""

    content_text: str
    content_type: str
    product_category: str
    target_market: str
    highlighted_claims: list[str] = field(default_factory=list)
    platform_name: str = "TikTok"
    temperature: float = 0.15
    enable_streaming: bool = True


@dataclass(frozen=True)
class ComplianceIssue:
    """合规问题项。"""

    severity: str
    rule: str
    description: str
    suggestion: str


@dataclass(frozen=True)
class ContentComplianceResult:
    """内容合规检测输出。"""

    meta: UseCaseExecutionMeta
    prompt: PromptEnvelope
    streaming: StreamingPlan
    passed: bool
    score: int
    issues: list[ComplianceIssue] = field(default_factory=list)
    safe_version: str = ""
    summary: str = ""


class _BaseAIUseCase:
    """所有 AI 用例共享的基础能力。"""

    use_case_name: str = "base_use_case"

    def __init__(self, config_service: AIConfigService, runtime: StreamingAIRuntime) -> None:
        self._config_service = config_service
        self._runtime = runtime

    def _resolve_provider_context(self) -> tuple[ProviderSelection, ProviderAdapter]:
        """读取当前活动模型与 provider。"""

        selection = self._config_service.get_active_selection()
        adapter = self._config_service.get_provider(selection.provider_name)
        return selection, adapter

    def _supports_streaming(self, selection: ProviderSelection) -> bool:
        """判断当前模型是否支持流式输出。"""

        for descriptor in self._config_service.list_models(selection.provider_name):
            if descriptor.model_name == selection.model_name:
                return bool(descriptor.supports_streaming)
        return True

    def _runtime_snapshot(self, *, can_stream: bool) -> RuntimeSnapshot:
        """采集运行时摘要。"""

        health = self._runtime.healthcheck()
        usage = self._runtime.get_usage_stats()
        active_stream_count_raw = health.get("active_stream_count")
        active_stream_count = 0
        if isinstance(active_stream_count_raw, bool):
            active_stream_count = int(active_stream_count_raw)
        elif isinstance(active_stream_count_raw, int):
            active_stream_count = active_stream_count_raw
        elif isinstance(active_stream_count_raw, float):
            active_stream_count = int(active_stream_count_raw)
        elif isinstance(active_stream_count_raw, str):
            try:
                active_stream_count = int(float(active_stream_count_raw.strip()))
            except ValueError:
                active_stream_count = 0
        return RuntimeSnapshot(
            service_name=self._runtime.service_name,
            can_stream=can_stream,
            is_streaming=bool(self._runtime.is_streaming()),
            active_stream_count=max(0, active_stream_count),
            current_model=_optional_text(health.get("current_model")),
            usage_totals=usage,
        )

    def _build_prompt_envelope(self, *, system_prompt: str, user_prompt: str) -> PromptEnvelope:
        """构造标准消息包。"""

        messages: list[dict[str, object]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return PromptEnvelope(system_prompt=system_prompt, user_prompt=user_prompt, messages=messages)

    def _build_streaming_plan(
        self,
        *,
        role_name: str,
        selection: ProviderSelection,
        temperature: float,
        messages: Sequence[MessagePayload],
        enabled: bool,
    ) -> StreamingPlan:
        """生成交给页面层的流式计划。"""

        can_stream = enabled and self._supports_streaming(selection)
        dispatch_hint = "当前模块仅构造流式参数，实际发起由页面层调用运行时。"
        if enabled and not can_stream:
            dispatch_hint = "当前模型未声明流式能力，页面层应回退到非流式展示。"
        return StreamingPlan(
            enabled=enabled,
            role_name=role_name,
            provider_name=selection.provider_name,
            model_name=selection.model_name,
            temperature=temperature,
            runtime=self._runtime_snapshot(can_stream=can_stream),
            messages=[dict(message) for message in messages],
            dispatch_hint=dispatch_hint,
        )

    def _build_meta(
        self,
        *,
        selection: ProviderSelection,
        temperature: float,
        input_digest: str,
        tags: Sequence[str],
    ) -> UseCaseExecutionMeta:
        """生成统一执行元信息。"""

        return UseCaseExecutionMeta(
            use_case_name=self.use_case_name,
            provider_name=selection.provider_name,
            model_name=selection.model_name,
            temperature=temperature,
            input_digest=_truncate(input_digest, limit=180),
            tags=[item for item in _string_list(list(tags)) if item],
        )

    async def _yield_control(self) -> None:
        """保持异步签名的一致性。"""

        await asyncio.sleep(0)


class TitleGenerationUseCase(_BaseAIUseCase):
    """根据商品信息生成标题候选。"""

    use_case_name = "title_generation"
    _SYSTEM_PROMPT = (
        "你是 TK-OPS 的 TikTok Shop 标题策划助手。"
        "你必须围绕点击率、停留率、商品相关性与平台表达边界来设计标题，"
        "优先使用利益点前置、痛点反差、场景代入、结果承诺与轻度行动引导。"
        "输出要适合跨境电商运营场景，不夸大、不违规、不堆砌。"
    )

    async def execute(self, input_data: TitleGenerationInput) -> TitleGenerationResult:
        await self._yield_control()
        selection, _adapter = self._resolve_provider_context()

        selling_points = input_data.selling_points or ["高转化卖点待补充"]
        styles = input_data.style_keywords or ["强钩子", "结果导向", "场景感"]
        banned_words = input_data.banned_words or []
        angle_templates = [
            ("痛点反差", "先戳痛点，再给解决结果"),
            ("结果承诺", "突出使用前后变化"),
            ("场景种草", "围绕真实使用场景说服"),
            ("性价比优势", "强调值回票价与购买理由"),
            ("人群定向", "直接锁定目标用户"),
        ]

        user_prompt = (
            f"请为商品生成适合 {input_data.market}{input_data.usage_scene} 的标题方案。\n"
            f"商品：{input_data.product_name}\n"
            f"类目：{input_data.product_category}\n"
            f"卖点：{'、'.join(selling_points)}\n"
            f"目标人群：{input_data.audience}\n"
            f"风格关键词：{'、'.join(styles)}\n"
            f"需避开词：{'、'.join(banned_words) if banned_words else '无'}\n"
            f"数量：{max(1, input_data.variant_count)}"
        )
        prompt = self._build_prompt_envelope(system_prompt=self._SYSTEM_PROMPT, user_prompt=user_prompt)

        hashtags = [f"#{_clean_text(input_data.product_category)}", f"#{_clean_text(input_data.market)}电商", "#种草推荐"]
        variants: list[TitleVariant] = []
        for index in range(max(1, input_data.variant_count)):
            angle, notes = angle_templates[index % len(angle_templates)]
            selling_point = selling_points[index % len(selling_points)]
            title = f"{input_data.product_name}别再乱买了，{selling_point}真的更适合{input_data.audience}"
            if angle == "结果承诺":
                title = f"用了{input_data.product_name}才知道，{selling_point}可以这么省心"
            elif angle == "场景种草":
                title = f"{input_data.audience}做{input_data.usage_scene}时，{input_data.product_name}这一点太加分"
            elif angle == "性价比优势":
                title = f"想要{selling_point}又不想踩雷，{input_data.product_name}这波很稳"
            elif angle == "人群定向":
                title = f"如果你是{input_data.audience}，这条{input_data.product_name}建议先收藏"

            for banned_word in banned_words:
                if banned_word and banned_word in title:
                    title = title.replace(banned_word, "")

            variants.append(
                TitleVariant(
                    title=_truncate(title.replace("  ", " ").strip("，。！？ "), limit=36),
                    angle=angle,
                    hook=f"前 3 秒先把“{selling_point}”抛给用户。",
                    hashtags=hashtags,
                    confidence=max(0.55, 0.92 - index * 0.06),
                    notes=notes,
                )
            )

        warnings = ["当前结果为集成占位输出，页面层可继续复用提示词与流式计划接入真实生成。"]
        if banned_words:
            warnings.append("已按输入词表执行基础避词处理，正式投放前仍需人工复核。")

        meta = self._build_meta(
            selection=selection,
            temperature=input_data.temperature,
            input_digest=f"标题生成：{input_data.product_name} / {input_data.product_category} / {input_data.market}",
            tags=["标题", "内容运营", input_data.market, input_data.product_category],
        )
        streaming = self._build_streaming_plan(
            role_name="文案专家",
            selection=selection,
            temperature=input_data.temperature,
            messages=prompt.messages,
            enabled=input_data.enable_streaming,
        )
        recommended_title = variants[0].title if variants else ""
        return TitleGenerationResult(
            meta=meta,
            prompt=prompt,
            streaming=streaming,
            variants=variants,
            recommended_title=recommended_title,
            warnings=warnings,
        )


class CopyWritingUseCase(_BaseAIUseCase):
    """生成商品营销文案。"""

    use_case_name = "copy_writing"
    _SYSTEM_PROMPT = (
        "你是 TK-OPS 的 TikTok Shop 高转化文案助手。"
        "你需要同时兼顾强钩子、利益点、信任感与行动引导，"
        "并根据不同市场的人群语气、促销敏感度和合规边界调整表达。"
        "输出必须自然、可执行、适合运营直接改写上线。"
    )

    async def execute(self, input_data: CopyWritingInput) -> CopyWritingResult:
        await self._yield_control()
        selection, _adapter = self._resolve_provider_context()

        selling_points = input_data.selling_points or ["核心卖点待补充"]
        price_anchor = _optional_text(input_data.price_anchor)
        promo = _optional_text(input_data.promotion_message)
        angles = ["利益点前置", "痛点唤起", "对比转化", "口碑信任"]
        user_prompt = (
            f"请生成适合 {input_data.platform_scene} 的营销文案。\n"
            f"商品：{input_data.product_name}\n"
            f"类目：{input_data.product_category}\n"
            f"目标人群：{input_data.audience}\n"
            f"语气：{input_data.tone}\n"
            f"卖点：{'、'.join(selling_points)}\n"
            f"价格锚点：{price_anchor or '未提供'}\n"
            f"促销信息：{promo or '未提供'}\n"
            f"数量：{max(1, input_data.variant_count)}"
        )
        prompt = self._build_prompt_envelope(system_prompt=self._SYSTEM_PROMPT, user_prompt=user_prompt)

        variants: list[CopyVariant] = []
        for index in range(max(1, input_data.variant_count)):
            angle = angles[index % len(angles)]
            selling_point = selling_points[index % len(selling_points)]
            headline = f"{input_data.product_name}把{selling_point}直接拉满"
            body = (
                f"这不是单纯在卖{input_data.product_category}，而是在帮{input_data.audience}更快获得“{selling_point}”的体验。"
                f"整体表达走{input_data.tone}路线，适合放在{input_data.platform_scene}承接流量。"
            )
            if angle == "痛点唤起":
                headline = f"总觉得{input_data.product_category}不好选？先看这款{input_data.product_name}"
                body = f"如果你也在纠结同类产品踩雷、效果不稳或不够省心，{input_data.product_name}会更容易打中“{selling_point}”这个购买理由。"
            elif angle == "对比转化":
                headline = f"同类里更值得下单的，往往是这类{input_data.product_name}"
                body = f"不是一味压价，而是把{selling_point}、使用体验和转化承接一起做好，更适合{input_data.audience}快速做购买判断。"
            elif angle == "口碑信任":
                headline = f"越是回购高的{input_data.product_category}，越会把细节做到位"
                body = f"{input_data.product_name}更适合通过细节建立信任：突出{selling_point}，再用真实场景和清晰承诺承接成交。"

            if price_anchor:
                body += f" 价格表达可围绕“{price_anchor}”展开。"
            if promo:
                body += f" 当前可叠加“{promo}”作为行动触发。"

            variants.append(
                CopyVariant(
                    headline=_truncate(headline, limit=30),
                    body=_truncate(body, limit=180),
                    cta=f"现在先看详情，确认适合再下单更稳。",
                    angle=angle,
                    keywords=[input_data.product_name, input_data.product_category, selling_point],
                    notes=f"建议在首屏 1 句内交代人群与卖点，减少理解成本。",
                )
            )

        recommended_summary = "优先使用“利益点前置”或“痛点唤起”版本承接短视频流量，转化路径更短。"
        warnings = ["当前结果为集成占位文案，建议在正式上线前结合素材画面再做二次润色。"]
        meta = self._build_meta(
            selection=selection,
            temperature=input_data.temperature,
            input_digest=f"营销文案：{input_data.product_name} / {input_data.audience} / {input_data.platform_scene}",
            tags=["文案", "转化", input_data.product_category, input_data.platform_scene],
        )
        streaming = self._build_streaming_plan(
            role_name="文案专家",
            selection=selection,
            temperature=input_data.temperature,
            messages=prompt.messages,
            enabled=input_data.enable_streaming,
        )
        return CopyWritingResult(
            meta=meta,
            prompt=prompt,
            streaming=streaming,
            variants=variants,
            recommended_summary=recommended_summary,
            warnings=warnings,
        )


class ScriptExtractionUseCase(_BaseAIUseCase):
    """从视频元数据中提炼脚本结构。"""

    use_case_name = "script_extraction"
    _SYSTEM_PROMPT = (
        "你是 TK-OPS 的视频脚本拆解助手。"
        "你要从标题、描述、口播关键词、评论反馈中重建短视频脚本结构，"
        "特别关注前三秒钩子、卖点递进、证据展示与结尾转化。"
        "输出应适合内容团队直接复盘和二创。"
    )

    async def execute(self, input_data: ScriptExtractionInput) -> ScriptExtractionResult:
        await self._yield_control()
        selection, _adapter = self._resolve_provider_context()

        title = _clean_text(input_data.video_title, default="未命名视频")
        hashtags = input_data.hashtags or []
        spoken = input_data.spoken_keywords or []
        product_name = _optional_text(input_data.product_name) or "目标商品"
        comment_signal = _optional_text(input_data.comments_summary) or "评论反馈待补充"
        duration_text = f"约 {input_data.duration_seconds} 秒" if input_data.duration_seconds else "时长未提供"

        user_prompt = (
            f"请从以下视频元数据提炼脚本结构。\n"
            f"标题：{title}\n"
            f"描述：{input_data.video_description or '无'}\n"
            f"标签：{'、'.join(hashtags) if hashtags else '无'}\n"
            f"口播关键词：{'、'.join(spoken) if spoken else '无'}\n"
            f"评论摘要：{comment_signal}\n"
            f"关联商品：{product_name}\n"
            f"视频时长：{duration_text}"
        )
        prompt = self._build_prompt_envelope(system_prompt=self._SYSTEM_PROMPT, user_prompt=user_prompt)

        hook_source = spoken[0] if spoken else title
        selling_source = spoken[1] if len(spoken) > 1 else "核心卖点"
        proof_source = hashtags[0] if hashtags else "真实使用场景"
        segments = [
            ScriptSegment(order=1, stage="开场钩子", text=f"先用“{hook_source}”抓住注意力，快速建立问题感。", objective="拦截滑走"),
            ScriptSegment(order=2, stage="痛点展开", text=f"点出用户在{product_name}相关决策中的犹豫点，并承接“{selling_source}”。", objective="建立共鸣"),
            ScriptSegment(order=3, stage="卖点证明", text=f"通过“{proof_source}”这类证据或场景演示增强信任。", objective="降低怀疑"),
            ScriptSegment(order=4, stage="行动引导", text=f"结合评论区关注点“{comment_signal}”引导用户查看详情或留言。", objective="承接转化"),
        ]
        reconstructed_script = "\n".join(f"{segment.stage}：{segment.text}" for segment in segments)
        warnings = ["当前脚本为元数据重构结果，不等同于逐字转写。"]
        if not spoken:
            warnings.append("未提供口播关键词，开场与卖点段落基于标题和标签推断。")

        meta = self._build_meta(
            selection=selection,
            temperature=input_data.temperature,
            input_digest=f"脚本提炼：{title} / {product_name} / {duration_text}",
            tags=["脚本", "拆解", "二创", product_name],
        )
        streaming = self._build_streaming_plan(
            role_name="脚本创作者",
            selection=selection,
            temperature=input_data.temperature,
            messages=prompt.messages,
            enabled=input_data.enable_streaming,
        )
        return ScriptExtractionResult(
            meta=meta,
            prompt=prompt,
            streaming=streaming,
            title=title,
            summary="该视频采用“钩子—痛点—证明—转化”四段式结构，适合做商品种草与复刻迭代。",
            segments=segments,
            reconstructed_script=reconstructed_script,
            content_tags=[item for item in [product_name, *hashtags[:2], *spoken[:2]] if item],
            warnings=warnings,
        )


class CompetitorAnalysisUseCase(_BaseAIUseCase):
    """输出竞品洞察与应对动作。"""

    use_case_name = "competitor_analysis"
    _SYSTEM_PROMPT = (
        "你是 TK-OPS 的竞品策略分析助手。"
        "你要把竞品卖点、价格、内容风格、流量信号和薄弱点整理成可执行的运营建议，"
        "帮助团队更快找到差异化定位、内容突破口和转化补位动作。"
    )

    async def execute(self, input_data: CompetitorAnalysisInput) -> CompetitorAnalysisResult:
        await self._yield_control()
        selection, _adapter = self._resolve_provider_context()

        competitors = input_data.competitors or [CompetitorRecord(name="样例竞品", selling_points=["卖点待补充"])]
        strengths = input_data.brand_strengths or ["履约稳定", "沟通响应更快"]
        competitor_lines = []
        for item in competitors:
            competitor_lines.append(
                f"竞品：{item.name}；价格带：{item.price_band or '未提供'}；卖点：{'、'.join(item.selling_points) or '无'}；"
                f"风格：{item.content_style or '未提供'}；流量信号：{'、'.join(item.traffic_signals) or '无'}；弱点：{'、'.join(item.weaknesses) or '无'}"
            )
        user_prompt = (
            f"请分析 {input_data.target_market} 市场下 {input_data.product_name} 的竞品格局。\n"
            f"类目：{input_data.product_category}\n"
            f"我方优势：{'、'.join(strengths)}\n"
            f"业务目标：{input_data.business_goal}\n"
            f"竞品信息：\n" + "\n".join(competitor_lines)
        )
        prompt = self._build_prompt_envelope(system_prompt=self._SYSTEM_PROMPT, user_prompt=user_prompt)

        insights: list[CompetitorInsight] = []
        for item in competitors:
            item_strengths = item.selling_points or ["内容表达集中，用户更易理解"]
            item_weaknesses = item.weaknesses or ["缺少更强信任背书", "差异化表达不足"]
            opportunities = [
                f"围绕“{input_data.product_name} + {input_data.target_market} 使用场景”补足场景内容。",
                f"强化我方“{strengths[0]}”作为竞品未明显占据的心智。",
            ]
            threats = [
                f"{item.name} 已经在“{item.content_style or '内容种草'}”方向占据部分注意力。",
                "若我方卖点表达不够集中，容易在首屏比较中失分。",
            ]
            insights.append(
                CompetitorInsight(
                    competitor_name=item.name,
                    strengths=item_strengths,
                    weaknesses=item_weaknesses,
                    opportunities=opportunities,
                    threats=threats,
                    recommended_response=f"建议用更清晰的利益点首屏 + 对比证据，正面切走 {item.name} 的主打心智。",
                )
            )

        recommended_actions = [
            f"先围绕“{strengths[0]}”做一轮差异化短视频测试，验证点击与加购提升。",
            "商品页与视频首屏统一卖点口径，避免内容承诺和落地页脱节。",
            "对竞品高频评论区问题做反向话术储备，提升客服和内容联动效率。",
        ]
        meta = self._build_meta(
            selection=selection,
            temperature=input_data.temperature,
            input_digest=f"竞品分析：{input_data.product_name} / {input_data.product_category} / {input_data.target_market}",
            tags=["竞品", "策略", input_data.target_market, input_data.product_category],
        )
        streaming = self._build_streaming_plan(
            role_name="数据分析师",
            selection=selection,
            temperature=input_data.temperature,
            messages=prompt.messages,
            enabled=input_data.enable_streaming,
        )
        return CompetitorAnalysisResult(
            meta=meta,
            prompt=prompt,
            streaming=streaming,
            overview="竞品竞争重点集中在卖点表达效率和信任感构建，我方更适合从差异化内容切入，而不是单纯打价格。",
            insights=insights,
            recommended_actions=recommended_actions,
            warnings=["当前结果基于输入资料归纳，建议结合真实投流与评论数据进一步校验。"],
        )


class BlueOceanAnalysisUseCase(_BaseAIUseCase):
    """识别可切入的蓝海机会。"""

    use_case_name = "blue_ocean_analysis"
    _SYSTEM_PROMPT = (
        "你是 TK-OPS 的蓝海机会识别助手。"
        "你需要从人群需求、竞品表达空白、内容供给不足和履约约束之间找出可落地的切入口，"
        "避免空泛战略描述，输出适合商品、内容和投流团队协同执行的机会点。"
    )

    async def execute(self, input_data: BlueOceanAnalysisInput) -> BlueOceanAnalysisResult:
        await self._yield_control()
        selection, _adapter = self._resolve_provider_context()

        signals = input_data.market_signals or ["用户对更省心方案的讨论升高"]
        pains = input_data.existing_pain_points or ["同类产品同质化严重"]
        patterns = input_data.competitor_patterns or ["内容高度集中在价格刺激"]
        constraints = input_data.brand_constraints or ["需控制合规风险"]

        user_prompt = (
            f"请为 {input_data.target_market} 的 {input_data.product_category} 寻找蓝海机会。\n"
            f"目标人群：{input_data.target_audience}\n"
            f"市场信号：{'、'.join(signals)}\n"
            f"现有痛点：{'、'.join(pains)}\n"
            f"竞品模式：{'、'.join(patterns)}\n"
            f"品牌约束：{'、'.join(constraints)}"
        )
        prompt = self._build_prompt_envelope(system_prompt=self._SYSTEM_PROMPT, user_prompt=user_prompt)

        opportunities = [
            BlueOceanOpportunity(
                niche=f"{input_data.target_audience}的细分效率场景",
                unmet_need=f"用户希望解决“{pains[0]}”，但不想再被同质化表达打扰。",
                content_angle=f"把{signals[0]}具体化为可视化对比内容，突出真实前后变化。",
                offer_direction="先用低门槛试用利益承接，再引导组合购买。",
                risk_level="低",
                next_action="先做 3 组人群定向内容脚本，小流量验证停留率和点击率。",
            ),
            BlueOceanOpportunity(
                niche=f"{input_data.product_category}的信任补位赛道",
                unmet_need=f"竞品主要在“{patterns[0]}”，信任背书表达仍有空白。",
                content_angle="用测评、对比、评论反馈和售后安心感构建新心智。",
                offer_direction="把服务承诺与商品卖点同步前置，减少犹豫成本。",
                risk_level="中",
                next_action="拉通商品页、短视频和客服话术，统一证据链表达。",
            ),
            BlueOceanOpportunity(
                niche=f"{input_data.target_market}本地化表达切口",
                unmet_need="同类内容多为通用表达，本地语言情境和生活方式贴合度不足。",
                content_angle="围绕地区节奏、消费顾虑和使用情境做本地化二创。",
                offer_direction="以场景适配和购买放心感替代简单促销堆叠。",
                risk_level="中",
                next_action="先从评论区高频问题中筛选 5 个最强本地化表达点。",
            ),
        ]
        recommendations = [
            "机会验证优先看前三秒留存、点击率和评论提问质量，而不是只看曝光。",
            "不要同时打开过多切口，建议每周只验证一个机会方向，确保复盘足够清晰。",
            f"执行时需持续检查“{constraints[0]}”是否被满足。",
        ]
        meta = self._build_meta(
            selection=selection,
            temperature=input_data.temperature,
            input_digest=f"蓝海分析：{input_data.product_category} / {input_data.target_market} / {input_data.target_audience}",
            tags=["蓝海", "选品", "机会", input_data.target_market],
        )
        streaming = self._build_streaming_plan(
            role_name="数据分析师",
            selection=selection,
            temperature=input_data.temperature,
            messages=prompt.messages,
            enabled=input_data.enable_streaming,
        )
        return BlueOceanAnalysisResult(
            meta=meta,
            prompt=prompt,
            streaming=streaming,
            summary="当前蓝海空间主要来自细分场景、人群信任补位和本地化表达三条路径，适合先做内容验证再决定货盘投入。",
            opportunities=opportunities,
            recommendations=recommendations,
            warnings=["当前结果为策略占位推演，落地前建议补充真实竞品视频样本与成交数据。"],
        )


class AutoReplyUseCase(_BaseAIUseCase):
    """生成客服智能回复建议。"""

    use_case_name = "auto_reply"
    _SYSTEM_PROMPT = (
        "你是 TK-OPS 的 TikTok Shop 客服回复助手。"
        "请生成友好、清晰、能解决问题并兼顾转化的回复，"
        "避免生硬、夸大和高风险承诺，必要时提醒人工接管。"
    )

    async def execute(self, input_data: AutoReplyInput) -> AutoReplyResult:
        await self._yield_control()
        selection, _adapter = self._resolve_provider_context()

        knowledge_points = input_data.knowledge_points or ["支持结合商品详情页进行进一步说明"]
        order_context = _optional_text(input_data.order_context) or "暂无订单补充信息"
        user_prompt = (
            f"请为客服场景生成回复建议。\n"
            f"场景：{input_data.scenario}\n"
            f"商品：{input_data.product_name}\n"
            f"用户消息：{input_data.customer_message}\n"
            f"品牌语气：{input_data.brand_tone}\n"
            f"订单上下文：{order_context}\n"
            f"知识点：{'、'.join(knowledge_points)}\n"
            f"数量：{max(1, input_data.variant_count)}"
        )
        prompt = self._build_prompt_envelope(system_prompt=self._SYSTEM_PROMPT, user_prompt=user_prompt)

        suggestions: list[AutoReplySuggestion] = []
        intents = ["解答疑问", "安抚情绪", "推动下单", "引导人工"]
        for index in range(max(1, input_data.variant_count)):
            intent = intents[index % len(intents)]
            reply = (
                f"您好，这边已经看到您关于“{input_data.product_name}”的消息啦。"
                f"针对您提到的情况，我们建议先关注“{knowledge_points[index % len(knowledge_points)]}”。"
                f"如果您愿意，我也可以继续根据您的具体需求帮您更快判断是否适合。"
            )
            upsell_tip: str | None = None
            if intent == "推动下单":
                reply = (
                    f"您好，{input_data.product_name}这边更适合关注实际使用效果和匹配需求。"
                    f"如果您现在正准备下单，我可以帮您把关键区别点快速整理出来，方便您马上做决定。"
                )
                upsell_tip = "可在确认需求后补一句“需要我顺手帮您对比一下哪款更适合吗”。"
            elif intent == "安抚情绪":
                reply = (
                    f"非常理解您的着急心情，我们先帮您把问题尽快处理清楚。"
                    f"关于{input_data.product_name}，当前最关键的是先确认“{knowledge_points[0]}”，这样能更快给您准确答复。"
                )
            elif intent == "引导人工":
                reply = (
                    f"您这边描述的信息比较关键，为了避免误判，建议由人工同事继续跟进会更稳妥。"
                    f"我们已经记录您关于{input_data.product_name}的情况，稍后可按您的重点继续处理。"
                )

            suggestions.append(
                AutoReplySuggestion(
                    reply=_truncate(reply, limit=150),
                    intent=intent,
                    style=input_data.brand_tone,
                    upsell_tip=upsell_tip,
                    risk_flags=[] if intent != "引导人工" else ["建议人工复核订单与售后细节"],
                )
            )

        meta = self._build_meta(
            selection=selection,
            temperature=input_data.temperature,
            input_digest=f"智能回复：{input_data.product_name} / {input_data.scenario}",
            tags=["客服", "回复", input_data.scenario, input_data.product_name],
        )
        streaming = self._build_streaming_plan(
            role_name="客服助手",
            selection=selection,
            temperature=input_data.temperature,
            messages=prompt.messages,
            enabled=input_data.enable_streaming,
        )
        return AutoReplyResult(
            meta=meta,
            prompt=prompt,
            streaming=streaming,
            suggestions=suggestions,
            recommended_reply=suggestions[0].reply if suggestions else "",
            warnings=["涉及退款、补偿、发货异常等高风险场景时，建议人工审核后再发送。"],
        )


class ContentComplianceUseCase(_BaseAIUseCase):
    """执行平台内容合规检查。"""

    use_case_name = "content_compliance"
    _SYSTEM_PROMPT = (
        "你是 TK-OPS 的内容合规审查助手。"
        "你需要从平台表达边界、敏感承诺、绝对化措辞、误导性收益与高风险导购表达中识别风险，"
        "并给出更稳妥的中文改写建议。"
    )

    async def execute(self, input_data: ContentComplianceInput) -> ContentComplianceResult:
        await self._yield_control()
        selection, _adapter = self._resolve_provider_context()

        claims = input_data.highlighted_claims or []
        user_prompt = (
            f"请检查以下内容是否适合 {input_data.platform_name} 平台发布。\n"
            f"内容类型：{input_data.content_type}\n"
            f"商品类目：{input_data.product_category}\n"
            f"目标市场：{input_data.target_market}\n"
            f"重点声明：{'、'.join(claims) if claims else '无'}\n"
            f"正文：{input_data.content_text}"
        )
        prompt = self._build_prompt_envelope(system_prompt=self._SYSTEM_PROMPT, user_prompt=user_prompt)

        text = input_data.content_text
        issues: list[ComplianceIssue] = []
        risky_terms = {
            "绝对化": ["最强", "第一", "百分百", "永久", "立刻见效"],
            "收益承诺": ["稳赚", "暴增", "必出单", "保证赚钱"],
            "夸大功效": ["根治", "治愈", "药到病除", "零风险"],
        }
        for rule, terms in risky_terms.items():
            for term in terms:
                if term in text:
                    issues.append(
                        ComplianceIssue(
                            severity="高" if rule != "绝对化" else "中",
                            rule=rule,
                            description=f"检测到“{term}”相关表述，存在被判定为夸大或误导的风险。",
                            suggestion=f"建议改为更克制的表达，例如“更适合”“表现更稳定”“更值得参考”。",
                        )
                    )

        for claim in claims:
            if claim and claim in text and len(claim) >= 8:
                issues.append(
                    ComplianceIssue(
                        severity="中",
                        rule="重点声明复核",
                        description=f"重点声明“{claim}”字数较长，建议确认是否具备充分证据支持。",
                        suggestion="可补充适用条件、数据来源或改写为经验性描述。",
                    )
                )

        safe_version = text
        replacements = {
            "最强": "更有优势",
            "第一": "更受关注",
            "百分百": "尽量",
            "永久": "更持久",
            "立刻见效": "更快看到变化",
            "稳赚": "更有机会提升",
            "暴增": "明显提升",
            "必出单": "更有机会成交",
            "保证赚钱": "帮助提升经营效率",
            "根治": "帮助改善",
            "治愈": "缓解相关困扰",
            "药到病除": "更快进入改善状态",
            "零风险": "风险更可控",
        }
        for source, target in replacements.items():
            safe_version = safe_version.replace(source, target)

        passed = len(issues) == 0
        score = max(0, 100 - len(issues) * 18)
        if passed:
            summary = "当前文本未命中明显高风险词，可进入下一步人工审校。"
        else:
            summary = "文本存在平台表达风险，建议优先移除绝对化、收益承诺与功效夸大措辞。"

        meta = self._build_meta(
            selection=selection,
            temperature=input_data.temperature,
            input_digest=f"内容合规：{input_data.content_type} / {input_data.product_category} / {input_data.target_market}",
            tags=["合规", "审核", input_data.content_type, input_data.target_market],
        )
        streaming = self._build_streaming_plan(
            role_name="客服助手",
            selection=selection,
            temperature=input_data.temperature,
            messages=prompt.messages,
            enabled=input_data.enable_streaming,
        )
        return ContentComplianceResult(
            meta=meta,
            prompt=prompt,
            streaming=streaming,
            passed=passed,
            score=score,
            issues=issues,
            safe_version=safe_version,
            summary=summary,
        )


__all__ = [
    "AutoReplyInput",
    "AutoReplyResult",
    "AutoReplySuggestion",
    "AutoReplyUseCase",
    "BlueOceanAnalysisInput",
    "BlueOceanAnalysisResult",
    "BlueOceanAnalysisUseCase",
    "BlueOceanOpportunity",
    "CompetitorAnalysisInput",
    "CompetitorAnalysisResult",
    "CompetitorAnalysisUseCase",
    "CompetitorInsight",
    "CompetitorRecord",
    "ComplianceIssue",
    "ContentComplianceInput",
    "ContentComplianceResult",
    "ContentComplianceUseCase",
    "CopyVariant",
    "CopyWritingInput",
    "CopyWritingResult",
    "CopyWritingUseCase",
    "PromptEnvelope",
    "RuntimeSnapshot",
    "ScriptExtractionInput",
    "ScriptExtractionResult",
    "ScriptExtractionUseCase",
    "ScriptSegment",
    "StreamingPlan",
    "TitleGenerationInput",
    "TitleGenerationResult",
    "TitleGenerationUseCase",
    "TitleVariant",
    "UseCaseExecutionMeta",
]
