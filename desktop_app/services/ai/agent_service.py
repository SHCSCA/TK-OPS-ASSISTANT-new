from __future__ import annotations

# pyright: basic

"""智能体角色服务，负责角色预设的完整管理。"""

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...data.database import Database
from ...data.models.ai_provider import AgentRole
from ...data.repositories.settings_repo import SettingsRepository


@dataclass(frozen=True)
class AgentRoleDTO:
    """智能体角色传输对象。"""

    id: int
    name: str
    description: str | None
    system_prompt: str
    provider_id: int | None
    model_id: int | None
    temperature: float
    max_tokens: int | None
    tools: list[str] = field(default_factory=list)
    is_system_role: bool = False
    sort_order: int = 0
    is_default: bool = False


@dataclass(frozen=True)
class AgentRolePreset:
    """兼容旧接口的角色预设视图。"""

    role_id: str
    display_name: str
    system_prompt: str
    default_model: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)


class AgentRoleService:
    """智能体角色服务，提供初始化、CRUD、默认角色与消息构建能力。"""

    service_name: str = "ai_roles"
    _DEFAULT_ROLE_SETTING_KEY: str = "ai.default_agent_role_id"
    _DEFAULT_ROLE_SETTING_CATEGORY: str = "ai"
    _BUILTIN_ROLE_DEFINITIONS: tuple[dict[str, object], ...] = (
        {
            "name": "通用助手",
            "description": "覆盖 TikTok Shop 日常运营问答、策略拆解与执行建议。",
            "system_prompt": "你是 TK-OPS 的通用 TikTok Shop 运营助手，服务对象是跨境电商团队。回答时必须围绕真实业务目标输出可执行建议，熟悉黄金3秒法则、完播率优化、互动率提升、标签策略、商品卡点击率、GPM、ROAS、转化率、客单价与复购分析。你需要同时考虑美区、东南亚、欧洲市场在内容偏好、价格敏感度、物流时效、节日节点与合规表达上的差异，能够把复杂问题拆解成选品、内容、投流、短视频、客服、复盘五个环节，并明确优先级、风险点和落地步骤。",
            "temperature": 0.4,
            "max_tokens": 1200,
            "tools_json": ["analysis", "planning"],
            "sort_order": 10,
        },
        {
            "name": "文案专家",
            "description": "聚焦爆款标题、商品卖点提炼与高转化文案生成。",
            "system_prompt": "你是专注 TikTok Shop 的文案专家，擅长生成爆款标题、短视频口播稿、商品描述、短视频口播与评论区引导文案。输出必须符合 TikTok 内容节奏，重点强化黄金3秒法则、强钩子开场、利益点前置、情绪驱动、完播率优化与强 CTA 设计，同时结合标签策略提高内容被系统识别与推荐的概率。你熟悉美区强调直接利益和信任背书、东南亚偏好高性价比与促销氛围、欧洲更关注合规措辞与品质体验，也要兼顾 GPM、ROAS、点击率与转化率目标，让文案既能吸引流量又能推动下单。",
            "temperature": 0.75,
            "max_tokens": 1400,
            "tools_json": ["copywriting", "ideation"],
            "sort_order": 20,
        },
        {
            "name": "数据分析师",
            "description": "聚焦经营指标解读、问题定位与优化建议输出。",
            "system_prompt": "你是 TikTok Shop 运营数据分析师，负责解读流量、内容、投流与成交数据，并把结果转化为运营动作。分析时请重点关注曝光、播放率、黄金3秒留存、完播率、互动率、点击率、加购率、GPM、ROAS、退款率与客服响应质量之间的关联，明确区分问题发生在内容、商品、流量还是履约环节。你熟悉美区重视利润效率和广告归因、东南亚更看重促销爆发和价格弹性、欧洲更敏感于合规和履约稳定，输出时需给出诊断结论、可能原因、优先级排序和下一步 A/B 测试方案。",
            "temperature": 0.3,
            "max_tokens": 1300,
            "tools_json": ["analysis", "reporting"],
            "sort_order": 30,
        },
        {
            "name": "脚本创作者",
            "description": "擅长短视频脚本、营销脚本和销售转化脚本创作。",
            "system_prompt": "你是 TikTok 短视频脚本创作者，目标是帮助商家提升停留、互动与成交。编写脚本时要严格体现黄金3秒法则，先用反差、痛点、结果或利益承诺抓住用户，再通过节奏推进、场景切换、证据展示和口播设计优化完播率与信任感，同时自然融入标签策略、热词和适配平台算法的结构。你需要根据美区偏好直给型价值表达、东南亚偏好热闹促销与社交认同、欧洲偏好清晰信息与品质叙事来调整脚本风格，并兼顾短视频转粉、商品点击、GPM 与 ROAS 等经营目标。",
            "temperature": 0.8,
            "max_tokens": 1600,
            "tools_json": ["script", "storytelling"],
            "sort_order": 40,
        },
        {
            "name": "SEO优化师",
            "description": "聚焦商品标题、关键词布局与平台搜索曝光优化。",
            "system_prompt": "你是 TikTok Shop SEO 优化师，负责提升商品标题、详情页与内容标签的搜索曝光和转化表现。你需要综合考虑关键词覆盖、标题可读性、标签策略、搜索意图匹配、类目词与卖点词搭配，以及内容与商品页之间的一致性，避免堆砌关键词。输出建议时请结合黄金3秒法则与完播率优化，确保搜索流量进入内容后仍能被有效承接，并关注关键词策略如何影响点击率、停留时长、GPM 与 ROAS。你熟悉美区搜索词更强调问题解决和品牌背书、东南亚更偏向促销词和价格词、欧洲更注重材质规格和规范表达。",
            "temperature": 0.45,
            "max_tokens": 1200,
            "tools_json": ["seo", "keyword"],
            "sort_order": 50,
        },
        {
            "name": "客服助手",
            "description": "聚焦售前售后沟通、异议处理与满意度提升。",
            "system_prompt": "你是 TikTok Shop 客服助手，负责生成专业、友好且高转化的售前售后回复。回答时既要解决用户疑问，也要兼顾转化和品牌体验，能处理发货、尺码、材质、售后、物流延迟、退款、优惠和催付等场景，并适度引导加购或下单。你需要理解 TikTok 平台运营逻辑，知道客服话术如何与内容承诺、商品卖点、标签策略、短视频节奏及完播率承接保持一致，也能从 GPM、ROAS、退款率和差评风险角度优化表达。针对美区、东南亚、欧洲用户，要分别调整语气、促销敏感点和合规边界，保证沟通自然、清晰、可信。",
            "temperature": 0.35,
            "max_tokens": 1000,
            "tools_json": ["support", "conversion"],
            "sort_order": 60,
        },
    )

    def __init__(self, database: Database | None = None) -> None:
        """初始化角色服务。"""

        self._database: Database = database or Database()
        self._settings_repo: SettingsRepository = SettingsRepository(self._database.create_session)
        self._initialized: bool = False

    def initialize(self) -> None:
        """初始化数据库结构，并在空表时写入内置角色。"""

        self._database.create_all()
        self._seed_builtin_roles()
        self._initialized = True
        self._ensure_default_role_setting()

    def shutdown(self) -> None:
        """关闭角色服务运行态。"""

        self._initialized = False

    def healthcheck(self) -> dict[str, object]:
        """返回角色服务健康状态。"""

        self._ensure_initialized()
        default_role = self.get_default_role()
        return {
            "service": self.service_name,
            "status": "ok",
            "database": "connected",
            "role_count": self._count_roles(),
            "default_role_id": default_role.id if default_role is not None else None,
            "default_role_name": default_role.name if default_role is not None else None,
        }

    def list_roles(self) -> list[AgentRoleDTO]:
        """返回全部角色列表。"""

        self._ensure_initialized()
        default_role_id = self._get_default_role_id()
        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            role_system = cast(Any, getattr(AgentRole, "is_system_role"))
            role_sort = cast(Any, getattr(AgentRole, "sort_order"))
            role_name = cast(Any, getattr(AgentRole, "name"))
            statement = cast(Any, select(AgentRole)).order_by(role_system.desc(), role_sort, role_name)
            roles = list(session_any.scalars(statement).all())
        return [self._to_dto(role, default_role_id=default_role_id) for role in roles]

    def get_role(self, role_id: int) -> AgentRoleDTO:
        """按 ID 获取角色。"""

        self._ensure_initialized()
        role = self._get_role_model(self._coerce_int(role_id, default=0))
        if role is None:
            raise LookupError(f"角色不存在: {role_id}")
        return self._to_dto(role, default_role_id=self._get_default_role_id())

    def create_role(self, data: Mapping[str, object]) -> AgentRoleDTO:
        """创建角色。"""

        self._ensure_initialized()
        payload = self._build_role_payload(data, is_create=True)
        with self._database.session_scope() as session:
            self._ensure_unique_name(session, str(payload["name"]))
            role = self._create_role_model(payload)
            session.add(role)
            session.flush()
            session.refresh(role)
            created_id = int(role.id)
        if self.get_default_role() is None:
            self.set_default_role(created_id)
        return self.get_role(created_id)

    def update_role(self, role_id: int, data: Mapping[str, object]) -> AgentRoleDTO:
        """更新角色。"""

        self._ensure_initialized()
        normalized_role_id = self._coerce_int(role_id, default=0)
        payload = self._build_role_payload(data, is_create=False)
        with self._database.session_scope() as session:
            role = self._require_role(session, normalized_role_id)
            new_name = self._optional_str(payload.get("name"))
            if new_name is not None and new_name != role.name:
                self._ensure_unique_name(session, new_name, exclude_role_id=normalized_role_id)
            for key, value in payload.items():
                setattr(role, key, value)
            session.add(role)
            session.flush()
            session.refresh(role)
        return self.get_role(normalized_role_id)

    def delete_role(self, role_id: int) -> bool:
        """删除角色，系统角色禁止删除。"""

        self._ensure_initialized()
        normalized_role_id = self._coerce_int(role_id, default=0)
        default_role_id = self._get_default_role_id()
        with self._database.session_scope() as session:
            role = self._require_role(session, normalized_role_id)
            if bool(role.is_system_role):
                raise ValueError(f"系统角色不允许删除: {role.name}")
            session.delete(role)
        if default_role_id == normalized_role_id:
            fallback = self._first_available_role()
            if fallback is None:
                self._clear_default_role_setting()
            else:
                self.set_default_role(int(fallback.id))
        return True

    def duplicate_role(self, role_id: int, new_name: str) -> AgentRoleDTO:
        """复制角色并生成新的自定义角色。"""

        self._ensure_initialized()
        normalized_role_id = self._coerce_int(role_id, default=0)
        target_name = new_name.strip()
        if not target_name:
            raise ValueError("new_name 不能为空")
        with self._database.session_scope() as session:
            source = self._require_role(session, normalized_role_id)
            self._ensure_unique_name(session, target_name)
            duplicate = self._create_role_model(
                {
                    "name": target_name,
                    "description": source.description,
                    "system_prompt": source.system_prompt,
                    "provider_id": source.provider_id,
                    "model_id": source.model_id,
                    "temperature": float(source.temperature or 0.7),
                    "max_tokens": source.max_tokens,
                    "tools_json": self._normalize_tools(source.tools_json),
                    "is_system_role": False,
                    "sort_order": self._next_sort_order(session),
                }
            )
            session.add(duplicate)
            session.flush()
            session.refresh(duplicate)
            duplicate_id = int(duplicate.id)
        return self.get_role(duplicate_id)

    def get_default_role(self) -> AgentRoleDTO | None:
        """返回当前默认角色。"""

        self._ensure_initialized()
        default_role_id = self._get_default_role_id()
        if default_role_id is not None:
            role = self._get_role_model(default_role_id)
            if role is not None:
                return self._to_dto(role, default_role_id=default_role_id)
        fallback = self._first_available_role()
        if fallback is None:
            return None
        self.set_default_role(int(fallback.id))
        return self.get_role(int(fallback.id))

    def set_default_role(self, role_id: int) -> AgentRoleDTO:
        """设置默认角色。"""

        self._ensure_initialized()
        normalized_role_id = self._coerce_int(role_id, default=0)
        if self._get_role_model(normalized_role_id) is None:
            raise LookupError(f"角色不存在: {role_id}")
        self._settings_repo.set_value(
            self._DEFAULT_ROLE_SETTING_KEY,
            str(normalized_role_id),
            category=self._DEFAULT_ROLE_SETTING_CATEGORY,
        )
        return self.get_role(normalized_role_id)

    def build_messages(self, role_id: int, user_message: str) -> list[dict[str, str]]:
        """根据角色预设构建模型消息列表。"""

        self._ensure_initialized()
        content = user_message.strip()
        if not content:
            raise ValueError("user_message 不能为空")
        role = self.get_role(role_id)
        return [
            {"role": "system", "content": role.system_prompt},
            {"role": "user", "content": content},
        ]

    def save_role(self, preset: AgentRolePreset) -> None:
        """兼容旧骨架接口，将预设写入角色表。"""

        self.create_role(
            {
                "name": preset.display_name,
                "description": f"由兼容接口导入的角色：{preset.role_id}",
                "system_prompt": preset.system_prompt,
                "tools": list(preset.tags),
            }
        )

    def list_role_dicts(self) -> list[dict[str, object]]:
        """返回角色字典列表。"""

        return [asdict(role) for role in self.list_roles()]

    def _seed_builtin_roles(self) -> None:
        """仅在角色表为空时写入内置角色。"""

        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            role_id_column = cast(Any, getattr(AgentRole, "id"))
            statement = cast(Any, select(func.count(role_id_column)))
            existing_count = int(session_any.scalar(statement) or 0)
            if existing_count > 0:
                return
            for definition in self._BUILTIN_ROLE_DEFINITIONS:
                session.add(
                    self._create_role_model(
                        {
                            "name": str(definition["name"]),
                            "description": self._optional_str(definition.get("description")),
                            "system_prompt": str(definition["system_prompt"]),
                            "provider_id": self._coerce_optional_int(definition.get("provider_id")),
                            "model_id": self._coerce_optional_int(definition.get("model_id")),
                            "temperature": self._coerce_temperature(definition.get("temperature"), default=0.7),
                            "max_tokens": self._coerce_optional_int(definition.get("max_tokens")),
                            "tools_json": self._normalize_tools(definition.get("tools_json")),
                            "is_system_role": True,
                            "sort_order": self._coerce_int(definition.get("sort_order"), default=0),
                        }
                    )
                )

    def _ensure_default_role_setting(self) -> None:
        """确保默认角色配置有效。"""

        if self._get_default_role_id() is not None:
            return
        fallback = self._first_available_role()
        if fallback is not None:
            self._settings_repo.set_value(
                self._DEFAULT_ROLE_SETTING_KEY,
                str(int(fallback.id)),
                category=self._DEFAULT_ROLE_SETTING_CATEGORY,
            )

    def _clear_default_role_setting(self) -> None:
        """清空默认角色配置。"""

        self._settings_repo.set_value(
            self._DEFAULT_ROLE_SETTING_KEY,
            None,
            category=self._DEFAULT_ROLE_SETTING_CATEGORY,
        )

    def _count_roles(self) -> int:
        """统计角色数量。"""

        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            role_id_column = cast(Any, getattr(AgentRole, "id"))
            statement = cast(Any, select(func.count(role_id_column)))
            return int(session_any.scalar(statement) or 0)

    def _get_default_role_id(self) -> int | None:
        """读取当前默认角色 ID。"""

        setting = self._settings_repo.get_by_key(self._DEFAULT_ROLE_SETTING_KEY)
        if setting is None or setting.value is None:
            return None
        try:
            role_id = self._coerce_int(setting.value, default=0)
        except ValueError:
            return None
        return role_id if self._get_role_model(role_id) is not None else None

    def _get_role_model(self, role_id: int) -> AgentRole | None:
        """通过仓储读取角色模型。"""

        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            role_id_column = cast(Any, getattr(AgentRole, "id"))
            statement = cast(Any, select(AgentRole)).where(role_id_column == role_id)
            return cast(AgentRole | None, session_any.scalars(statement).first())

    def _first_available_role(self) -> AgentRole | None:
        """获取排序后的首个可用角色。"""

        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            role_system = cast(Any, getattr(AgentRole, "is_system_role"))
            role_sort = cast(Any, getattr(AgentRole, "sort_order"))
            role_name = cast(Any, getattr(AgentRole, "name"))
            statement = cast(Any, select(AgentRole)).order_by(role_system.desc(), role_sort, role_name)
            return session_any.scalars(statement).first()

    def _require_role(self, session: Session, role_id: int) -> AgentRole:
        """确保角色存在。"""

        session_any = cast(Any, session)
        role = session_any.get(AgentRole, role_id)
        if role is None:
            raise LookupError(f"角色不存在: {role_id}")
        return role

    def _ensure_unique_name(self, session: Session, name: str, exclude_role_id: int | None = None) -> None:
        """确保角色名称唯一。"""

        role_name = cast(Any, getattr(AgentRole, "name"))
        statement = cast(Any, select(AgentRole)).where(role_name == name)
        existing = cast(Any, session).scalars(statement).first()
        if existing is None:
            return
        if exclude_role_id is not None and int(existing.id) == exclude_role_id:
            return
        raise ValueError(f"角色名称已存在: {name}")

    def _next_sort_order(self, session: Session) -> int:
        """计算下一个排序值。"""

        session_any = cast(Any, session)
        role_sort = cast(Any, getattr(AgentRole, "sort_order"))
        statement = cast(Any, select(func.max(role_sort)))
        max_sort = session_any.scalar(statement)
        return int(max_sort or 0) + 10

    def _to_dto(self, role: AgentRole, *, default_role_id: int | None) -> AgentRoleDTO:
        """将模型转换为 DTO。"""

        return AgentRoleDTO(
            id=int(role.id),
            name=str(role.name),
            description=role.description,
            system_prompt=str(role.system_prompt),
            provider_id=cast(int | None, role.provider_id),
            model_id=cast(int | None, role.model_id),
            temperature=float(role.temperature or 0.7),
            max_tokens=cast(int | None, role.max_tokens),
            tools=self._normalize_tools(role.tools_json),
            is_system_role=bool(role.is_system_role),
            sort_order=int(role.sort_order or 0),
            is_default=default_role_id == int(role.id),
        )

    def _build_role_payload(self, data: Mapping[str, object], *, is_create: bool) -> dict[str, object]:
        """标准化角色输入载荷。"""

        payload: dict[str, object] = {}
        name = self._optional_str(data.get("name"))
        system_prompt = self._optional_str(data.get("system_prompt"))

        if is_create:
            if not name:
                raise ValueError("name 不能为空")
            if not system_prompt:
                raise ValueError("system_prompt 不能为空")
            payload["name"] = name
            payload["system_prompt"] = system_prompt
        else:
            if "name" in data:
                if not name:
                    raise ValueError("name 不能为空")
                payload["name"] = name
            if "system_prompt" in data:
                if not system_prompt:
                    raise ValueError("system_prompt 不能为空")
                payload["system_prompt"] = system_prompt

        if "description" in data:
            payload["description"] = self._optional_str(data.get("description"))
        if "provider_id" in data:
            payload["provider_id"] = self._coerce_optional_int(data.get("provider_id"))
        if "model_id" in data:
            payload["model_id"] = self._coerce_optional_int(data.get("model_id"))
        if "temperature" in data:
            payload["temperature"] = self._coerce_temperature(data.get("temperature"), default=0.7)
        elif is_create:
            payload["temperature"] = 0.7
        if "max_tokens" in data:
            payload["max_tokens"] = self._coerce_optional_int(data.get("max_tokens"))
        if "tools" in data:
            payload["tools_json"] = self._normalize_tools(data.get("tools"))
        elif "tools_json" in data:
            payload["tools_json"] = self._normalize_tools(data.get("tools_json"))
        elif is_create:
            payload["tools_json"] = []
        if "is_system_role" in data:
            payload["is_system_role"] = bool(data.get("is_system_role"))
        elif is_create:
            payload["is_system_role"] = False
        if "sort_order" in data:
            payload["sort_order"] = self._coerce_int(data.get("sort_order"), default=0)
        elif is_create:
            payload["sort_order"] = self._next_sort_order_in_new_session()
        return payload

    def _create_role_model(self, payload: Mapping[str, object]) -> AgentRole:
        """根据载荷创建角色模型实例。"""

        role = AgentRole()
        for key, value in payload.items():
            setattr(role, key, value)
        return role

    def _next_sort_order_in_new_session(self) -> int:
        """在独立会话中计算排序值。"""

        with self._database.session_scope() as session:
            return self._next_sort_order(session)

    def _normalize_tools(self, tools_value: object) -> list[str]:
        """规范化工具列表。"""

        if tools_value is None:
            return []
        if isinstance(tools_value, str):
            text = tools_value.strip()
            return [text] if text else []
        if isinstance(tools_value, (list, tuple, set)):
            result: list[str] = []
            for item in tools_value:
                text = str(item).strip()
                if text and text not in result:
                    result.append(text)
            return result
        raise ValueError("tools 必须是字符串或字符串列表")

    def _coerce_optional_int(self, value: object) -> int | None:
        """将输入转换为可空整数。"""

        if value in (None, ""):
            return None
        return int(str(value).strip())

    def _coerce_int(self, value: object, *, default: int) -> int:
        """将输入转换为整数。"""

        if value in (None, ""):
            return default
        return int(str(value).strip())

    def _coerce_temperature(self, value: object, *, default: float) -> float:
        """规范化温度并校验范围。"""

        if value in (None, ""):
            return default
        temperature = float(str(value).strip())
        if temperature < 0 or temperature > 2:
            raise ValueError("temperature 必须在 0 到 2 之间")
        return temperature

    def _optional_str(self, value: object) -> str | None:
        """将输入转换为去空白后的可空字符串。"""

        if value is None:
            return None
        text = str(value).strip()
        return text if text else None

    def _ensure_initialized(self) -> None:
        """确保服务已经初始化。"""

        if not self._initialized:
            raise RuntimeError("AgentRoleService 尚未初始化")
