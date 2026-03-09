from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportMissingTypeStubs=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false

"""AI 内容治理、合规检查、用量追踪与限流服务。"""

import re
import threading
from collections import Counter, defaultdict, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import monotonic
from typing import Final, Literal, cast

from .agent_service import AgentRoleService
from .config_service import AIConfigService
from .provider_adapter import MessagePayload, ProviderAdapter, ResponsePayload

Severity = Literal["低", "中", "高", "严重"]

_SEVERITY_WEIGHT: Final[dict[Severity, int]] = {
    "低": 8,
    "中": 18,
    "高": 35,
    "严重": 55,
}


@dataclass(frozen=True)
class PolicyViolation:
    """描述单条合规违规项。"""

    rule_code: str
    category: str
    severity: Severity
    description: str
    evidence: tuple[str, ...] = ()
    suggestion: str | None = None

    def to_dict(self) -> dict[str, object]:
        """转换为可序列化字典。"""

        return {
            "rule_code": self.rule_code,
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "evidence": list(self.evidence),
            "suggestion": self.suggestion,
        }


@dataclass(frozen=True)
class ContentPolicy:
    """平台内容政策定义，默认内置 TikTok Shop 场景规则。"""

    platform_name: str
    policy_name: str
    policy_version: str = "2026.03"
    prohibited_categories: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    disclosure_keywords: tuple[str, ...] = field(default_factory=tuple)
    age_restricted_keywords: tuple[str, ...] = field(default_factory=tuple)
    copyright_keywords: tuple[str, ...] = field(default_factory=tuple)
    trademark_keywords: tuple[str, ...] = field(default_factory=tuple)
    restricted_keywords: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    risky_claim_keywords: tuple[str, ...] = field(default_factory=tuple)
    minor_markers: tuple[str, ...] = field(default_factory=tuple)
    remediation_hints: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def tiktok_shop_default(cls) -> ContentPolicy:
        """返回 TikTok Shop 默认治理策略。"""

        return cls(
            platform_name="TikTok Shop",
            policy_name="TikTok 平台 AI 内容治理策略",
            prohibited_categories={
                "违法危险": (
                    "枪支",
                    "手枪",
                    "步枪",
                    "弹药",
                    "炸药",
                    "爆炸物",
                    "管制刀具",
                    "毒品",
                    "冰毒",
                    "海洛因",
                    "大麻售卖",
                    "违禁药",
                    "代开发票",
                    "伪造证件",
                    "翻墙服务",
                    "黑产",
                    "破解教程",
                ),
                "仇恨暴力": (
                    "种族清洗",
                    "极端组织",
                    "恐袭",
                    "校园霸凌教程",
                    "自残挑战",
                    "鼓动自杀",
                    "血腥报复",
                    "暴力处决",
                ),
                "成人色情": (
                    "成人视频",
                    "裸聊",
                    "约炮",
                    "援交",
                    "情色直播",
                    "成人视频资源",
                    "成人用品试用演示",
                    "露点",
                    "性玩具实操",
                ),
                "诈骗误导": (
                    "保证赚钱",
                    "零成本暴富",
                    "内幕开户链接",
                    "博彩返水",
                    "刷单返利",
                    "代办贷款包过",
                    "假一赔十稳赚",
                    "官方内部渠道",
                ),
            },
            disclosure_keywords=(
                "广告",
                "推广",
                "赞助",
                "合作",
                "品牌合作",
                "含推广",
                "商业合作",
                "达人合作",
                "广告合作",
            ),
            age_restricted_keywords=(
                "酒精",
                "白酒",
                "啤酒",
                "红酒",
                "电子烟",
                "香烟",
                "烟草",
                "医美",
                "针剂",
                "处方药",
                "减肥药",
                "壮阳",
                "情趣用品",
                "夜店",
                "纹身",
                "穿孔",
            ),
            copyright_keywords=(
                "搬运",
                "盗版",
                "未授权",
                "未经许可",
                "转载他人",
                "盗图",
                "盗视频",
                "扒素材",
                "剪辑他人视频",
                "影视片段直搬",
            ),
            trademark_keywords=(
                "高仿",
                "复刻",
                "原单",
                "一比一",
                "大牌同款",
                "擦边商标",
                "仿牌",
                "山寨",
                "假货",
                "贴牌冒充",
                "伪授权",
            ),
            restricted_keywords={
                "绝对化用语": (
                    "最强",
                    "第一",
                    "顶级",
                    "国家级",
                    "全网第一",
                    "永久有效",
                    "百分百",
                    "绝对",
                    "无敌",
                    "唯一",
                ),
                "医疗功效": (
                    "根治",
                    "治愈",
                    "药到病除",
                    "消炎止痛",
                    "替代药物",
                    "医生都推荐",
                    "临床验证包治",
                    "快速瘦十斤",
                ),
                "金融收益": (
                    "稳赚不赔",
                    "保本高收益",
                    "稳定翻倍",
                    "躺赚",
                    "日入过万",
                    "一夜暴富",
                    "返现无门槛",
                ),
                "导流私下交易": (
                    "加微",
                    "加v",
                    "私聊下单",
                    "站外交易",
                    "脱离平台",
                    "转账购买",
                    "联系客服改价到别处付",
                ),
                "平台敏感承诺": (
                    "绕过审核",
                    "规避平台",
                    "无限起号",
                    "刷量",
                    "刷评",
                    "控评",
                    "黑科技",
                    "秒过风控",
                ),
            },
            risky_claim_keywords=(
                "保证",
                "承诺",
                "包过",
                "包赚",
                "立刻见效",
                "当天见效",
                "马上变白",
                "立即瘦身",
                "百分之百有效",
            ),
            minor_markers=(
                "未成年",
                "儿童",
                "小学生",
                "初中生",
                "高中生",
                "宝宝",
                "青少年",
                "学生党",
                "幼儿",
            ),
            remediation_hints={
                "违法危险": "删除违法、危险、黑灰产导向内容，改为合法、安全、合规的商品价值描述。",
                "仇恨暴力": "删除仇恨、伤害、自残、极端暴力表达，改为理性、中性、非攻击性叙述。",
                "成人色情": "删除露骨成人、性暗示和低俗引流表达，改用正常生活方式或产品功能描述。",
                "诈骗误导": "去除暴富、保赚、内幕、包过等误导性承诺，保留真实条件与限制说明。",
                "广告披露": "若属于推广或商业合作，请显式加入“广告/推广/合作”等披露语。",
                "年龄适配": "涉及年龄敏感品类时，增加成年人限制说明，避免对未成年人进行诱导。",
                "知识产权": "删除未授权搬运、盗版、仿牌、商标蹭热度内容，改写为原创或正规授权表述。",
                "绝对化用语": "删除“最强、第一、百分百”等绝对化措辞，改为可验证的客观描述。",
                "医疗功效": "删除治疗、根治、药效替代等医疗宣称，改为一般体验或辅助性说明。",
                "金融收益": "删除保本、稳赚、暴富等收益承诺，只保留风险提示和事实数据。",
                "导流私下交易": "删除站外联系与私下交易引导，统一引导在平台内完成咨询与购买。",
                "平台敏感承诺": "删除刷量、绕审、风控规避等违规运营表述。",
            },
        )


@dataclass(frozen=True)
class ComplianceResult:
    """内容合规检查结果。"""

    passed: bool
    severity: Severity
    violations: tuple[PolicyViolation, ...] = ()
    suggestions: tuple[str, ...] = ()
    review_required: bool = False
    matched_rules: tuple[str, ...] = ()
    score: float = 100.0
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, object]:
        """转换为可序列化字典。"""

        return {
            "passed": self.passed,
            "severity": self.severity,
            "violations": [item.to_dict() for item in self.violations],
            "suggestions": list(self.suggestions),
            "review_required": self.review_required,
            "matched_rules": list(self.matched_rules),
            "score": self.score,
            "checked_at": self.checked_at.isoformat(),
        }


@dataclass
class UsageRecord:
    """AI 调用用量记录。"""

    provider_name: str
    model_name: str
    operation: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    latency_ms: float = 0.0
    success: bool = True
    request_id: str | None = None
    user_id: str | None = None
    role_id: int | None = None
    scene: str | None = None
    rate_limited: bool = False
    blocked_by_compliance: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """补齐聚合字段。"""

        if self.total_tokens <= 0:
            self.total_tokens = max(0, self.prompt_tokens) + max(0, self.completion_tokens)
        self.prompt_tokens = max(0, self.prompt_tokens)
        self.completion_tokens = max(0, self.completion_tokens)
        self.total_tokens = max(0, self.total_tokens)
        self.estimated_cost = max(0.0, float(self.estimated_cost))
        self.latency_ms = max(0.0, float(self.latency_ms))

    def to_dict(self) -> dict[str, object]:
        """转换为可序列化字典。"""

        return {
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "operation": self.operation,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.estimated_cost,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "role_id": self.role_id,
            "scene": self.scene,
            "rate_limited": self.rate_limited,
            "blocked_by_compliance": self.blocked_by_compliance,
            "created_at": self.created_at.isoformat(),
            "metadata": dict(self.metadata),
        }


class ContentComplianceChecker:
    """基于规则的内容合规检查器。"""

    def __init__(self, policy: ContentPolicy | None = None) -> None:
        """初始化合规检查器。"""

        self._policy = policy or ContentPolicy.tiktok_shop_default()

    @property
    def policy(self) -> ContentPolicy:
        """返回当前策略。"""

        return self._policy

    def check_content(
        self,
        content: str,
        *,
        require_disclosure: bool = False,
        content_type: str = "通用",
        metadata: Mapping[str, object] | None = None,
    ) -> ComplianceResult:
        """检查单段文本内容是否符合平台政策。"""

        normalized = self._normalize_text(content)
        if not normalized:
            return ComplianceResult(
                passed=True,
                severity="低",
                suggestions=("内容为空，建议补充清晰、客观、可验证的商品与场景描述。",),
                review_required=False,
            )

        violations: list[PolicyViolation] = []
        violations.extend(self._check_prohibited_categories(normalized))
        violations.extend(self._check_disclosure(normalized, require_disclosure=require_disclosure, content_type=content_type, metadata=metadata))
        violations.extend(self._check_age_appropriateness(normalized, metadata=metadata))
        violations.extend(self._check_intellectual_property(normalized))
        violations.extend(self._check_restricted_keywords(normalized))
        violations.extend(self._check_risky_claims(normalized))
        return self._build_result(violations)

    def check_messages(
        self,
        messages: Sequence[MessagePayload],
        *,
        require_disclosure: bool = False,
        include_system: bool = False,
        metadata: Mapping[str, object] | None = None,
    ) -> ComplianceResult:
        """检查消息列表中的文本内容。"""

        segments: list[str] = []
        for message in messages:
            role_name = str(message.get("role", "")).strip().lower()
            if role_name == "system" and not include_system:
                continue
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                segments.append(content.strip())
            elif isinstance(content, Sequence) and not isinstance(content, (str, bytes, bytearray)):
                for item in content:
                    if isinstance(item, Mapping):
                        text = item.get("text")
                        if isinstance(text, str) and text.strip():
                            segments.append(text.strip())
        return self.check_content(
            "\n".join(segments),
            require_disclosure=require_disclosure,
            content_type="消息",
            metadata=metadata,
        )

    def check_response(
        self,
        response: ResponsePayload,
        *,
        require_disclosure: bool = False,
        metadata: Mapping[str, object] | None = None,
    ) -> ComplianceResult:
        """检查模型响应文本。"""

        return self.check_content(
            self.extract_response_text(response),
            require_disclosure=require_disclosure,
            content_type="生成结果",
            metadata=metadata,
        )

    def explain_policy(self) -> dict[str, object]:
        """返回当前策略摘要。"""

        return {
            "platform_name": self._policy.platform_name,
            "policy_name": self._policy.policy_name,
            "policy_version": self._policy.policy_version,
            "prohibited_categories": {key: list(value) for key, value in self._policy.prohibited_categories.items()},
            "disclosure_keywords": list(self._policy.disclosure_keywords),
            "age_restricted_keywords": list(self._policy.age_restricted_keywords),
            "copyright_keywords": list(self._policy.copyright_keywords),
            "trademark_keywords": list(self._policy.trademark_keywords),
            "restricted_keywords": {key: list(value) for key, value in self._policy.restricted_keywords.items()},
            "risky_claim_keywords": list(self._policy.risky_claim_keywords),
        }

    def extract_response_text(self, response: ResponsePayload) -> str:
        """从多种响应结构中尽量提取文本。"""

        direct_text = response.get("text")
        if isinstance(direct_text, str):
            return direct_text

        message = response.get("message")
        if isinstance(message, Mapping):
            content = message.get("content")
            if isinstance(content, str):
                return content

        choices = response.get("choices")
        if isinstance(choices, Sequence) and not isinstance(choices, (str, bytes, bytearray)):
            parts: list[str] = []
            for choice in choices:
                if not isinstance(choice, Mapping):
                    continue
                choice_message = choice.get("message")
                if isinstance(choice_message, Mapping):
                    content = choice_message.get("content")
                    if isinstance(content, str) and content.strip():
                        parts.append(content.strip())
                delta = choice.get("delta")
                if isinstance(delta, Mapping):
                    content = delta.get("content")
                    if isinstance(content, str) and content.strip():
                        parts.append(content.strip())
                text = choice.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
            return "\n".join(parts)

        return ""

    def _normalize_text(self, text: str) -> str:
        """标准化文本。"""

        return re.sub(r"\s+", " ", text).strip().lower()

    def _check_prohibited_categories(self, text: str) -> list[PolicyViolation]:
        """检查禁止内容。"""

        violations: list[PolicyViolation] = []
        for category, keywords in self._policy.prohibited_categories.items():
            matched = self._find_keywords(text, keywords)
            if not matched:
                continue
            severity: Severity = "严重" if category in {"违法危险", "仇恨暴力", "成人色情"} else "高"
            violations.append(
                PolicyViolation(
                    rule_code=f"prohibited:{category}",
                    category=category,
                    severity=severity,
                    description=f"内容命中“{category}”禁止类目，不适合在平台生成或发布。",
                    evidence=matched,
                    suggestion=self._policy.remediation_hints.get(category),
                )
            )
        return violations

    def _check_disclosure(
        self,
        text: str,
        *,
        require_disclosure: bool,
        content_type: str,
        metadata: Mapping[str, object] | None,
    ) -> list[PolicyViolation]:
        """检查商业推广披露。"""

        demand_disclosure = require_disclosure or self._infer_advertising_context(text, content_type=content_type, metadata=metadata)
        if not demand_disclosure:
            return []
        if self._find_keywords(text, self._policy.disclosure_keywords):
            return []
        return [
            PolicyViolation(
                rule_code="disclosure:required",
                category="广告披露",
                severity="中",
                description="内容具备推广或电商属性，但未发现明确的广告披露语。",
                suggestion=self._policy.remediation_hints.get("广告披露"),
            )
        ]

    def _check_age_appropriateness(self, text: str, *, metadata: Mapping[str, object] | None) -> list[PolicyViolation]:
        """检查年龄适配与未成年人风险。"""

        violations: list[PolicyViolation] = []
        age_hits = self._find_keywords(text, self._policy.age_restricted_keywords)
        minor_hits = self._find_keywords(text, self._policy.minor_markers)
        target_age = self._coerce_optional_int(metadata.get("target_age") if metadata is not None else None)

        if age_hits and minor_hits:
            violations.append(
                PolicyViolation(
                    rule_code="age:minor-sensitive",
                    category="年龄适配",
                    severity="高",
                    description="内容同时涉及未成年人指向与年龄敏感品类，存在明显平台风险。",
                    evidence=tuple(dict.fromkeys((*minor_hits, *age_hits))),
                    suggestion=self._policy.remediation_hints.get("年龄适配"),
                )
            )
        elif age_hits and (target_age is None or target_age < 18) and "仅限成年人" not in text and "未成年人请勿" not in text:
            violations.append(
                PolicyViolation(
                    rule_code="age:adult-only-missing",
                    category="年龄适配",
                    severity="中",
                    description="内容涉及年龄敏感品类，但缺少明确的成年人限制说明。",
                    evidence=age_hits,
                    suggestion=self._policy.remediation_hints.get("年龄适配"),
                )
            )
        return violations

    def _check_intellectual_property(self, text: str) -> list[PolicyViolation]:
        """检查版权与商标风险。"""

        violations: list[PolicyViolation] = []
        copyright_hits = self._find_keywords(text, self._policy.copyright_keywords)
        trademark_hits = self._find_keywords(text, self._policy.trademark_keywords)
        if copyright_hits:
            violations.append(
                PolicyViolation(
                    rule_code="ip:copyright",
                    category="知识产权",
                    severity="高",
                    description="内容包含未授权搬运、盗版或侵权素材暗示。",
                    evidence=copyright_hits,
                    suggestion=self._policy.remediation_hints.get("知识产权"),
                )
            )
        if trademark_hits:
            violations.append(
                PolicyViolation(
                    rule_code="ip:trademark",
                    category="知识产权",
                    severity="高",
                    description="内容包含仿牌、擦边商标或冒充授权等高风险表达。",
                    evidence=trademark_hits,
                    suggestion=self._policy.remediation_hints.get("知识产权"),
                )
            )
        return violations

    def _check_restricted_keywords(self, text: str) -> list[PolicyViolation]:
        """检查受限关键词。"""

        violations: list[PolicyViolation] = []
        for category, keywords in self._policy.restricted_keywords.items():
            matched = self._find_keywords(text, keywords)
            if not matched:
                continue
            severity: Severity = "中"
            if category in {"医疗功效", "金融收益", "导流私下交易", "平台敏感承诺"}:
                severity = "高"
            violations.append(
                PolicyViolation(
                    rule_code=f"restricted:{category}",
                    category=category,
                    severity=severity,
                    description=f"内容出现“{category}”相关限制表达，建议降级为客观、可验证、平台内合规说法。",
                    evidence=matched,
                    suggestion=self._policy.remediation_hints.get(category),
                )
            )
        return violations

    def _check_risky_claims(self, text: str) -> list[PolicyViolation]:
        """检查高风险承诺式表达。"""

        matched = self._find_keywords(text, self._policy.risky_claim_keywords)
        if not matched:
            return []
        return [
            PolicyViolation(
                rule_code="claim:risky",
                category="误导承诺",
                severity="中",
                description="内容包含保证式、速效式或结果承诺式表达，容易构成误导。",
                evidence=matched,
                suggestion="删除保证、包过、立刻见效等承诺措辞，补充条件、限制与真实适用场景。",
            )
        ]

    def _build_result(self, violations: Sequence[PolicyViolation]) -> ComplianceResult:
        """将违规列表汇总为最终结果。"""

        if not violations:
            return ComplianceResult(
                passed=True,
                severity="低",
                suggestions=("内容未发现明显风险，仍建议在发布前结合具体商品资质做人工复核。",),
                review_required=False,
                matched_rules=(),
                score=100.0,
            )

        max_severity = self._max_severity(violations)
        review_required = max_severity in {"中", "高", "严重"}
        score = max(0.0, 100.0 - float(sum(_SEVERITY_WEIGHT[item.severity] for item in violations)))
        suggestions: list[str] = []
        for violation in violations:
            if violation.suggestion and violation.suggestion not in suggestions:
                suggestions.append(violation.suggestion)
        if not suggestions:
            suggestions.append("请删除风险词、补充平台内披露说明，并将描述改为真实、客观、可验证的表达。")
        matched_rules = tuple(item.rule_code for item in violations)
        return ComplianceResult(
            passed=False,
            severity=max_severity,
            violations=tuple(violations),
            suggestions=tuple(suggestions),
            review_required=review_required,
            matched_rules=matched_rules,
            score=score,
        )

    def _find_keywords(self, text: str, keywords: Iterable[str]) -> tuple[str, ...]:
        """查找已命中的关键词。"""

        matched: list[str] = []
        for keyword in keywords:
            token = keyword.strip().lower()
            if token and token in text and token not in matched:
                matched.append(token)
        return tuple(matched)

    def _infer_advertising_context(
        self,
        text: str,
        *,
        content_type: str,
        metadata: Mapping[str, object] | None,
    ) -> bool:
        """根据上下文推断是否需要广告披露。"""

        if metadata is not None:
            if bool(metadata.get("is_advertisement", False)):
                return True
            if bool(metadata.get("commercial", False)):
                return True
        if content_type in {"广告", "电商", "短视频", "商品卡", "生成结果"}:
            return True
        signals = (
            "立即下单",
            "短视频",
            "购买链接",
            "优惠券",
            "折扣码",
            "店铺",
            "橱窗",
            "领券",
            "限时优惠",
            "入手",
        )
        return bool(self._find_keywords(text, signals))

    def _coerce_optional_int(self, value: object) -> int | None:
        """把任意输入转换为可空整数。"""

        if value in (None, ""):
            return None
        try:
            return int(str(value).strip())
        except ValueError:
            return None

    def _max_severity(self, violations: Sequence[PolicyViolation]) -> Severity:
        """返回最高等级。"""

        if any(item.severity == "严重" for item in violations):
            return "严重"
        if any(item.severity == "高" for item in violations):
            return "高"
        if any(item.severity == "中" for item in violations):
            return "中"
        return "低"


class AIUsageTracker:
    """线程安全的 AI 用量追踪器。"""

    _DEFAULT_PRICING: Final[dict[str, tuple[float, float]]] = {
        "openai:gpt-4o": (0.005, 0.015),
        "openai:gpt-4.1": (0.002, 0.008),
        "anthropic:claude-3-5-sonnet": (0.003, 0.015),
    }

    def __init__(self, *, max_records: int = 5000) -> None:
        """初始化记录容器。"""

        self._max_records = max(100, max_records)
        self._records: deque[UsageRecord] = deque(maxlen=self._max_records)
        self._lock = threading.Lock()

    def record(self, usage: UsageRecord) -> UsageRecord:
        """写入一条调用记录。"""

        with self._lock:
            self._records.append(usage)
        return usage

    def create_record(
        self,
        *,
        provider_name: str,
        model_name: str,
        operation: str,
        response: Mapping[str, object] | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        latency_ms: float = 0.0,
        success: bool = True,
        request_id: str | None = None,
        user_id: str | None = None,
        role_id: int | None = None,
        scene: str | None = None,
        rate_limited: bool = False,
        blocked_by_compliance: bool = False,
        metadata: Mapping[str, object] | None = None,
    ) -> UsageRecord:
        """基于响应载荷构建一条记录。"""

        response_data = dict(response or {})
        usage_payload = response_data.get("usage")
        usage_map = cast(Mapping[str, object], usage_payload) if isinstance(usage_payload, Mapping) else {}
        normalized_prompt_tokens = prompt_tokens if prompt_tokens is not None else self._coerce_token_value(usage_map.get("prompt_tokens"))
        normalized_completion_tokens = (
            completion_tokens if completion_tokens is not None else self._coerce_token_value(usage_map.get("completion_tokens"))
        )
        total_tokens = self._coerce_token_value(usage_map.get("total_tokens"))
        estimated_cost = self.estimate_cost(
            provider_name=provider_name,
            model_name=model_name,
            prompt_tokens=normalized_prompt_tokens,
            completion_tokens=normalized_completion_tokens,
        )
        return UsageRecord(
            provider_name=provider_name,
            model_name=model_name,
            operation=operation,
            prompt_tokens=normalized_prompt_tokens,
            completion_tokens=normalized_completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            latency_ms=latency_ms,
            success=success,
            request_id=request_id,
            user_id=user_id,
            role_id=role_id,
            scene=scene,
            rate_limited=rate_limited,
            blocked_by_compliance=blocked_by_compliance,
            metadata=dict(metadata or {}),
        )

    def estimate_cost(
        self,
        *,
        provider_name: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """按照内置费率估算成本。"""

        price_key = f"{provider_name.strip().lower()}:{model_name.strip().lower()}"
        pricing = self._DEFAULT_PRICING.get(price_key)
        if pricing is None:
            return 0.0
        prompt_price, completion_price = pricing
        return round((prompt_tokens / 1000.0) * prompt_price + (completion_tokens / 1000.0) * completion_price, 6)

    def list_records(self, *, limit: int | None = None) -> list[UsageRecord]:
        """返回最近的用量记录。"""

        with self._lock:
            records = list(self._records)
        if limit is None or limit <= 0:
            return records
        return records[-limit:]

    def summarize(self, *, provider_name: str | None = None, model_name: str | None = None) -> dict[str, object]:
        """汇总当前用量。"""

        with self._lock:
            records = list(self._records)
        if provider_name is not None:
            target_provider = provider_name.strip().lower()
            records = [item for item in records if item.provider_name.strip().lower() == target_provider]
        if model_name is not None:
            target_model = model_name.strip().lower()
            records = [item for item in records if item.model_name.strip().lower() == target_model]

        total_requests = len(records)
        success_count = sum(1 for item in records if item.success)
        failed_count = total_requests - success_count
        total_tokens = sum(item.total_tokens for item in records)
        prompt_tokens = sum(item.prompt_tokens for item in records)
        completion_tokens = sum(item.completion_tokens for item in records)
        total_cost = round(sum(item.estimated_cost for item in records), 6)
        avg_latency = round(sum(item.latency_ms for item in records) / total_requests, 2) if total_requests else 0.0
        blocked = sum(1 for item in records if item.blocked_by_compliance)
        rate_limited = sum(1 for item in records if item.rate_limited)
        by_provider = Counter(item.provider_name for item in records)
        by_model = Counter(f"{item.provider_name}:{item.model_name}" for item in records)

        return {
            "total_requests": total_requests,
            "success_count": success_count,
            "failed_count": failed_count,
            "blocked_by_compliance": blocked,
            "rate_limited": rate_limited,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "avg_latency_ms": avg_latency,
            "by_provider": dict(by_provider),
            "by_model": dict(by_model),
        }

    def summarize_by_user(self) -> dict[str, dict[str, object]]:
        """按用户汇总使用情况。"""

        groups: dict[str, list[UsageRecord]] = defaultdict(list)
        with self._lock:
            for item in self._records:
                groups[item.user_id or "匿名用户"].append(item)
        result: dict[str, dict[str, object]] = {}
        for user_id, items in groups.items():
            result[user_id] = {
                "request_count": len(items),
                "total_tokens": sum(item.total_tokens for item in items),
                "total_cost": round(sum(item.estimated_cost for item in items), 6),
                "success_count": sum(1 for item in items if item.success),
            }
        return result

    def clear(self) -> None:
        """清空记录。"""

        with self._lock:
            self._records.clear()

    def _coerce_token_value(self, value: object) -> int:
        """把响应中的 token 数值规范化。"""

        if value in (None, ""):
            return 0
        try:
            return max(0, int(float(str(value).strip())))
        except ValueError:
            return 0


class RateLimiter:
    """基于令牌桶的请求限流器。"""

    def __init__(self, *, capacity: float, refill_rate: float, initial_tokens: float | None = None) -> None:
        """初始化令牌桶。"""

        self._capacity = max(1.0, float(capacity))
        self._refill_rate = max(0.0001, float(refill_rate))
        self._tokens = min(self._capacity, float(initial_tokens) if initial_tokens is not None else self._capacity)
        self._updated_at = monotonic()
        self._lock = threading.Lock()

    def allow(self, tokens: float = 1.0) -> bool:
        """尝试消费令牌。"""

        requested = max(0.0, float(tokens))
        if requested == 0.0:
            return True
        with self._lock:
            self._refill_locked()
            if self._tokens < requested:
                return False
            self._tokens -= requested
            return True

    def wait_time(self, tokens: float = 1.0) -> float:
        """返回满足请求所需的预计等待秒数。"""

        requested = max(0.0, float(tokens))
        with self._lock:
            self._refill_locked()
            if self._tokens >= requested:
                return 0.0
            deficit = requested - self._tokens
            return round(deficit / self._refill_rate, 3)

    def snapshot(self) -> dict[str, float]:
        """返回当前桶状态。"""

        with self._lock:
            self._refill_locked()
            return {
                "capacity": round(self._capacity, 3),
                "tokens": round(self._tokens, 3),
                "refill_rate": round(self._refill_rate, 3),
            }

    def reset(self) -> None:
        """重置令牌桶。"""

        with self._lock:
            self._tokens = self._capacity
            self._updated_at = monotonic()

    def _refill_locked(self) -> None:
        """在持锁状态下回填令牌。"""

        now = monotonic()
        elapsed = max(0.0, now - self._updated_at)
        self._updated_at = now
        self._tokens = min(self._capacity, self._tokens + elapsed * self._refill_rate)


class AIGovernanceService:
    """编排 AI 合规检查、用量追踪与限流控制。"""

    service_name: str = "ai_governance"

    def __init__(
        self,
        *,
        config_service: AIConfigService | None = None,
        agent_role_service: AgentRoleService | None = None,
        compliance_checker: ContentComplianceChecker | None = None,
        usage_tracker: AIUsageTracker | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        """初始化治理服务。"""

        self._config_service = config_service
        self._agent_role_service = agent_role_service
        self._compliance_checker = compliance_checker or ContentComplianceChecker()
        self._usage_tracker = usage_tracker or AIUsageTracker()
        self._global_rate_limiter = rate_limiter or RateLimiter(capacity=60.0, refill_rate=1.0)
        self._scoped_limiters: dict[str, RateLimiter] = {}
        self._lock = threading.Lock()

    @property
    def compliance_checker(self) -> ContentComplianceChecker:
        """暴露内部检查器。"""

        return self._compliance_checker

    @property
    def usage_tracker(self) -> AIUsageTracker:
        """暴露内部用量追踪器。"""

        return self._usage_tracker

    def healthcheck(self) -> dict[str, object]:
        """返回服务健康状态。"""

        return {
            "service": self.service_name,
            "status": "ok",
            "policy": self._compliance_checker.policy.policy_name,
            "policy_version": self._compliance_checker.policy.policy_version,
            "global_rate_limiter": self._global_rate_limiter.snapshot(),
            "usage_summary": self._usage_tracker.summarize(),
        }

    def register_limiter(self, scope: str, *, capacity: float, refill_rate: float) -> RateLimiter:
        """注册指定作用域的限流器。"""

        normalized_scope = scope.strip().lower()
        if not normalized_scope:
            raise ValueError("scope 不能为空")
        limiter = RateLimiter(capacity=capacity, refill_rate=refill_rate)
        with self._lock:
            self._scoped_limiters[normalized_scope] = limiter
        return limiter

    def get_limiter(self, scope: str) -> RateLimiter | None:
        """获取已注册的限流器。"""

        normalized_scope = scope.strip().lower()
        with self._lock:
            return self._scoped_limiters.get(normalized_scope)

    def check_content(
        self,
        content: str,
        *,
        require_disclosure: bool = False,
        content_type: str = "通用",
        metadata: Mapping[str, object] | None = None,
    ) -> ComplianceResult:
        """对外提供内容检查入口。"""

        return self._compliance_checker.check_content(
            content,
            require_disclosure=require_disclosure,
            content_type=content_type,
            metadata=metadata,
        )

    def enforce_rate_limit(self, *, scope: str | None = None, tokens: float = 1.0) -> tuple[bool, float]:
        """执行全局与作用域双层限流。"""

        if not self._global_rate_limiter.allow(tokens):
            return False, self._global_rate_limiter.wait_time(tokens)
        if scope is None:
            return True, 0.0
        limiter = self.get_limiter(scope)
        if limiter is None:
            return True, 0.0
        if limiter.allow(tokens):
            return True, 0.0
        return False, limiter.wait_time(tokens)

    def governed_generate(
        self,
        adapter: ProviderAdapter,
        *,
        model: str,
        messages: Sequence[MessagePayload],
        temperature: float = 0.0,
        user_id: str | None = None,
        role_id: int | None = None,
        scene: str | None = None,
        request_id: str | None = None,
        require_disclosure: bool = False,
        content_metadata: Mapping[str, object] | None = None,
        rate_limit_scope: str | None = None,
        request_tokens: float = 1.0,
    ) -> dict[str, object]:
        """执行带治理能力的模型调用。"""

        prompt_result = self._compliance_checker.check_messages(
            messages,
            require_disclosure=require_disclosure,
            metadata=content_metadata,
        )
        estimated_prompt_tokens = self._estimate_tokens_from_messages(messages)

        if not prompt_result.passed:
            record = self._usage_tracker.create_record(
                provider_name=adapter.provider_name,
                model_name=model,
                operation="generate",
                prompt_tokens=estimated_prompt_tokens,
                completion_tokens=0,
                latency_ms=0.0,
                success=False,
                request_id=request_id,
                user_id=user_id,
                role_id=role_id,
                scene=scene,
                blocked_by_compliance=True,
                metadata={"stage": "prompt", "compliance": prompt_result.to_dict()},
            )
            self._usage_tracker.record(record)
            return {
                "ok": False,
                "error": {"message": "输入内容触发平台合规限制，已阻止生成。"},
                "compliance": prompt_result.to_dict(),
                "usage": record.to_dict(),
            }

        allowed, retry_after = self.enforce_rate_limit(scope=rate_limit_scope or self._build_scope(adapter.provider_name, model), tokens=request_tokens)
        if not allowed:
            record = self._usage_tracker.create_record(
                provider_name=adapter.provider_name,
                model_name=model,
                operation="generate",
                prompt_tokens=estimated_prompt_tokens,
                completion_tokens=0,
                latency_ms=0.0,
                success=False,
                request_id=request_id,
                user_id=user_id,
                role_id=role_id,
                scene=scene,
                rate_limited=True,
                metadata={"retry_after_seconds": retry_after},
            )
            self._usage_tracker.record(record)
            return {
                "ok": False,
                "error": {"message": f"请求过于频繁，请在 {retry_after:.3f} 秒后重试。"},
                "rate_limit": {"retry_after_seconds": retry_after},
                "usage": record.to_dict(),
            }

        started_at = monotonic()
        response = dict(adapter.generate(model=model, messages=messages, temperature=temperature))
        latency_ms = round((monotonic() - started_at) * 1000.0, 3)
        output_result = self._compliance_checker.check_response(
            cast(ResponsePayload, response),
            require_disclosure=require_disclosure,
            metadata=content_metadata,
        )
        success = bool(response.get("ok", True)) and output_result.passed
        record = self._usage_tracker.create_record(
            provider_name=adapter.provider_name,
            model_name=model,
            operation="generate",
            response=response,
            prompt_tokens=estimated_prompt_tokens,
            latency_ms=latency_ms,
            success=success,
            request_id=request_id,
            user_id=user_id,
            role_id=role_id,
            scene=scene,
            blocked_by_compliance=not output_result.passed,
            metadata={"stage": "response", "compliance": output_result.to_dict()},
        )
        self._usage_tracker.record(record)
        response["governance"] = {
            "compliance": output_result.to_dict(),
            "usage": record.to_dict(),
        }
        if not output_result.passed:
            response["ok"] = False
            response["error"] = {"message": "生成结果触发平台合规限制，已标记为不可直接发布。"}
        return response

    def build_runtime_context(self, *, role_id: int | None = None) -> dict[str, object]:
        """聚合当前运行时上下文。"""

        context: dict[str, object] = {}
        if self._config_service is not None:
            try:
                selection = self._config_service.get_active_selection()
                context["active_provider"] = selection.provider_name
                context["active_model"] = selection.model_name
            except Exception:
                context["active_provider"] = None
                context["active_model"] = None
        if self._agent_role_service is not None:
            try:
                target_role = self._agent_role_service.get_role(role_id) if role_id is not None else self._agent_role_service.get_default_role()
                context["role_id"] = None if target_role is None else target_role.id
                context["role_name"] = None if target_role is None else target_role.name
            except Exception:
                context["role_id"] = None
                context["role_name"] = None
        return context

    def _estimate_tokens_from_messages(self, messages: Sequence[MessagePayload]) -> int:
        """粗略估算消息 token 用量。"""

        text_parts: list[str] = []
        for message in messages:
            content = message.get("content")
            if isinstance(content, str):
                text_parts.append(content)
        joined = "\n".join(text_parts)
        if not joined.strip():
            return 0
        return max(1, len(joined) // 4)

    def _build_scope(self, provider_name: str, model_name: str) -> str:
        """构造默认限流作用域。"""

        return f"{provider_name.strip().lower()}:{model_name.strip().lower()}"


__all__ = [
    "AIGovernanceService",
    "AIUsageTracker",
    "ComplianceResult",
    "ContentComplianceChecker",
    "ContentPolicy",
    "PolicyViolation",
    "RateLimiter",
    "UsageRecord",
]
