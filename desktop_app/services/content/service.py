from __future__ import annotations

# pyright: basic

"""内容服务，负责素材、脚本与模板的领域逻辑。"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from importlib import import_module
from pathlib import Path
from string import Formatter
from typing import Any, Mapping, cast

from sqlalchemy import select

from ...data.database import Database
from ...data.models.asset import Asset
from ...data.models.schedule import PublishSchedule


def _content_template_model() -> type[Any]:
    """延迟加载内容模板模型，规避静态分析缓存问题。"""

    module = import_module("desktop_app.data.models.content")
    return cast(type[Any], getattr(module, "ContentTemplate"))


def _script_model() -> type[Any]:
    """延迟加载脚本模型，规避静态分析缓存问题。"""

    module = import_module("desktop_app.data.models.content")
    return cast(type[Any], getattr(module, "Script"))


@dataclass
class AssetFilters:
    """素材查询筛选条件。"""

    asset_type: str | None = None
    status: str | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None


@dataclass
class AssetDTO:
    """素材传输对象。"""

    id: int
    name: str
    asset_type: str
    file_path: str
    thumbnail_path: str | None
    size_bytes: int | None
    duration_seconds: int | None
    tags: list[str] = field(default_factory=list)
    status: str = "active"
    metadata: dict[str, object] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


@dataclass
class BatchUpdateResultDTO:
    """批量更新素材后的结果摘要。"""

    requested_count: int
    updated_count: int
    missing_asset_ids: list[int] = field(default_factory=list)


@dataclass
class ScriptDTO:
    """脚本传输对象。"""

    id: int
    title: str
    body: str
    hook_text: str | None
    cta_text: str | None
    status: str
    platform: str
    tone: str | None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)
    scheduled_at: datetime | None = None
    asset_id: int | None = None
    template_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ContentTemplateDTO:
    """内容模板传输对象。"""

    id: int
    name: str
    category: str
    title_template: str
    body_template: str
    description: str | None
    parameter_schema: list[dict[str, object]] = field(default_factory=list)
    default_params: dict[str, object] = field(default_factory=dict)
    status: str = "active"
    metadata: dict[str, object] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ContentCalendarEntryDTO:
    """内容日历条目。"""

    source_type: str
    source_id: int
    title: str
    status: str
    scheduled_at: datetime
    owner: str | None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class ContentCalendarOverviewDTO:
    """内容日历总览。"""

    items: list[ContentCalendarEntryDTO] = field(default_factory=list)
    total_scheduled: int = 0
    upcoming_count: int = 0
    overdue_count: int = 0
    window_start: datetime | None = None
    window_end: datetime | None = None


class _SafeTemplateDict(dict):
    """模板格式化时为缺失参数保留原占位符。"""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


class ContentService:
    """内容域服务，封装素材与脚本的核心业务能力。"""

    service_name: str = "content"
    _DEFAULT_TEMPLATES: tuple[dict[str, object], ...] = (
        {
            "name": "新品预热短视频",
            "category": "promotion",
            "title_template": "{product_name}新品预热脚本",
            "body_template": "开场：{hook}\n卖点：{selling_point}\n福利：{offer}\n行动：{cta}",
            "description": "适用于新品预热短视频内容生成。",
            "parameter_schema_json": [
                {"name": "product_name", "required": True, "description": "商品名称"},
                {"name": "hook", "required": True, "description": "开场钩子"},
                {"name": "selling_point", "required": True, "description": "核心卖点"},
                {"name": "offer", "required": True, "description": "福利信息"},
                {"name": "cta", "required": True, "description": "转化引导"},
            ],
            "default_params_json": {
                "hook": "前三秒先别划走",
                "selling_point": "高颜值、高性价比",
                "offer": "限时福利",
                "cta": "点击预约上新，不错过开抢时间",
            },
            "metadata_json": {"scene": "live_warmup"},
        },
        {
            "name": "商品种草口播",
            "category": "seeding",
            "title_template": "{product_name}种草口播脚本",
            "body_template": "痛点：{pain_point}\n解决方案：{solution}\n证据：{proof}\n收尾：{cta}",
            "description": "适用于商品种草和短视频口播场景。",
            "parameter_schema_json": [
                {"name": "product_name", "required": True, "description": "商品名称"},
                {"name": "pain_point", "required": True, "description": "用户痛点"},
                {"name": "solution", "required": True, "description": "解决方案"},
                {"name": "proof", "required": True, "description": "证明材料"},
                {"name": "cta", "required": True, "description": "转化引导"},
            ],
            "default_params_json": {
                "pain_point": "总觉得同类产品不好用",
                "solution": "这款产品把关键细节都做好了",
                "proof": "评论区和复购数据都很稳",
                "cta": "想看实拍效果，评论区留言我发你",
            },
            "metadata_json": {"scene": "product_seeding"},
        },
    )

    def __init__(self, database: Database | None = None) -> None:
        """初始化内容服务，支持外部注入数据库实例。"""

        self._database: Database = database or Database()
        self._initialized: bool = False

    def initialize(self) -> None:
        """初始化数据库结构并注入默认模板。"""

        self._database.create_all()
        self._seed_default_templates()
        self._initialized = True

    def shutdown(self) -> None:
        """关闭内容服务运行态。"""

        self._initialized = False

    def healthcheck(self) -> dict[str, object]:
        """返回内容服务健康状态与基础统计。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            asset_count = len(list(session_any.scalars(cast(Any, select(Asset))).all()))
            script_count = len(list(session_any.scalars(cast(Any, select(_script_model()))).all()))
            template_count = len(list(session_any.scalars(cast(Any, select(_content_template_model()))).all()))
            return {
                "service": self.service_name,
                "status": "healthy",
                "initialized": self._initialized,
                "assets": asset_count,
                "scripts": script_count,
                "templates": template_count,
            }

    def list_assets(self, filters: AssetFilters | Mapping[str, object] | None = None) -> list[AssetDTO]:
        """按筛选条件列出素材记录。"""

        self._ensure_initialized()
        normalized_filters = self._normalize_asset_filters(filters)

        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            statement = cast(Any, select(Asset))
            if normalized_filters.asset_type:
                statement = statement.where(cast(Any, getattr(Asset, "asset_type")) == normalized_filters.asset_type)

            if normalized_filters.status == "deleted":
                statement = statement.where(cast(Any, getattr(Asset, "is_deleted")).is_(True))
            else:
                statement = statement.where(cast(Any, getattr(Asset, "is_deleted")).is_(False))

            if normalized_filters.created_from is not None:
                statement = statement.where(cast(Any, getattr(Asset, "created_at")) >= normalized_filters.created_from)
            if normalized_filters.created_to is not None:
                statement = statement.where(cast(Any, getattr(Asset, "created_at")) <= normalized_filters.created_to)

            statement = statement.order_by(cast(Any, getattr(Asset, "created_at")).desc())
            assets = list(session_any.scalars(statement).all())

            if normalized_filters.status not in {None, "active", "deleted"}:
                assets = [asset for asset in assets if self._asset_status(asset) == normalized_filters.status]

            return [self._to_asset_dto(asset) for asset in assets]

    def get_asset(self, asset_id: int) -> AssetDTO | None:
        """获取单个素材详情。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            asset = session_any.get(Asset, asset_id)
            if asset is None:
                return None
            return self._to_asset_dto(asset)

    def upload_asset(self, file_path: str, metadata: Mapping[str, object] | None = None) -> AssetDTO:
        """登记新素材记录，文件落盘逻辑暂以占位方式处理。"""

        self._ensure_initialized()
        normalized_metadata = dict(metadata or {})
        path = Path(file_path)
        tags = self._to_string_list(normalized_metadata.get("tags"))
        asset_type = self._normalize_asset_type(normalized_metadata.get("asset_type"), path.suffix)
        name = str(normalized_metadata.get("name") or path.name or "未命名素材")
        thumbnail_path = self._optional_str(normalized_metadata.get("thumbnail_path"))
        duration_seconds = self._optional_int(normalized_metadata.get("duration_seconds"))
        size_bytes = self._resolve_size_bytes(path, normalized_metadata.get("size_bytes"))
        status = str(normalized_metadata.get("status") or "active")
        metadata_payload = self._extract_asset_metadata_payload(normalized_metadata, status=status)

        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            asset = Asset()
            asset.name = name
            asset.asset_type = asset_type
            asset.file_path = str(path)
            asset.thumbnail_path = thumbnail_path
            asset.size_bytes = size_bytes
            asset.duration_seconds = duration_seconds
            asset.tags_json = tags
            asset.metadata_json = metadata_payload
            asset.is_deleted = False
            session_any.add(asset)
            session_any.flush()
            session_any.refresh(asset)
            return self._to_asset_dto(asset)

    def delete_asset(self, asset_id: int) -> bool:
        """软删除素材记录。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            asset = session_any.get(Asset, asset_id)
            if asset is None or bool(asset.is_deleted):
                return False
            asset.is_deleted = True
            asset.deleted_at = datetime.now(timezone.utc)
            metadata_payload = self._copy_dict(asset.metadata_json)
            metadata_payload["status"] = "deleted"
            asset.metadata_json = metadata_payload
            session_any.add(asset)
            session_any.flush()
            return True

    def batch_update_assets(self, asset_ids: list[int], updates: Mapping[str, object]) -> BatchUpdateResultDTO:
        """批量更新素材元数据与基础字段。"""

        self._ensure_initialized()
        requested_ids = [int(asset_id) for asset_id in asset_ids]
        missing_ids: list[int] = []
        updated_count = 0

        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            statement = cast(Any, select(Asset))
            statement = statement.where(cast(Any, getattr(Asset, "id")).in_(requested_ids))
            assets = list(session_any.scalars(statement).all())
            asset_map = {int(asset.id): asset for asset in assets}

            for asset_id in requested_ids:
                asset = asset_map.get(asset_id)
                if asset is None:
                    missing_ids.append(asset_id)
                    continue
                self._apply_asset_updates(asset, updates)
                session_any.add(asset)
                updated_count += 1

            session_any.flush()

        return BatchUpdateResultDTO(
            requested_count=len(requested_ids),
            updated_count=updated_count,
            missing_asset_ids=missing_ids,
        )

    def list_scripts(self) -> list[ScriptDTO]:
        """列出所有未删除脚本。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            script_model = _script_model()
            statement = cast(Any, select(script_model))
            statement = statement.where(cast(Any, getattr(script_model, "is_deleted")).is_(False))
            statement = statement.order_by(cast(Any, getattr(script_model, "created_at")).desc())
            scripts = list(session_any.scalars(statement).all())
            return [self._to_script_dto(script) for script in scripts]

    def create_script(self, data: Mapping[str, object]) -> ScriptDTO:
        """创建新的脚本记录。"""

        self._ensure_initialized()
        payload = dict(data)
        title = str(payload.get("title") or "未命名脚本")
        body = str(payload.get("body") or "")
        if not body.strip():
            raise ValueError("脚本正文不能为空。")

        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            content_template_model = _content_template_model()
            script_model = _script_model()
            asset_id = self._optional_int(payload.get("asset_id"))
            template_id = self._optional_int(payload.get("template_id"))
            if asset_id is not None and session_any.get(Asset, asset_id) is None:
                raise ValueError(f"素材不存在：{asset_id}")
            if template_id is not None and session_any.get(content_template_model, template_id) is None:
                raise ValueError(f"模板不存在：{template_id}")

            script = script_model()
            script.title = title
            script.body = body
            script.hook_text = self._optional_str(payload.get("hook_text"))
            script.cta_text = self._optional_str(payload.get("cta_text"))
            script.status = str(payload.get("status") or "draft")
            script.platform = str(payload.get("platform") or "tiktok")
            script.tone = self._optional_str(payload.get("tone"))
            script.tags_json = self._to_string_list(payload.get("tags"))
            script.metadata_json = self._copy_dict(payload.get("metadata"))
            script.scheduled_at = self._optional_datetime(payload.get("scheduled_at"))
            script.asset_id = asset_id
            script.template_id = template_id
            script.is_deleted = False
            session_any.add(script)
            session_any.flush()
            session_any.refresh(script)
            return self._to_script_dto(script)

    def update_script(self, script_id: int, data: Mapping[str, object]) -> ScriptDTO | None:
        """更新已有脚本。"""

        self._ensure_initialized()
        payload = dict(data)
        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            content_template_model = _content_template_model()
            script_model = _script_model()
            script = session_any.get(script_model, script_id)
            if script is None or bool(script.is_deleted):
                return None

            if "title" in payload:
                script.title = str(payload["title"] or "未命名脚本")
            if "body" in payload:
                body = str(payload["body"] or "")
                if not body.strip():
                    raise ValueError("脚本正文不能为空。")
                script.body = body
            if "hook_text" in payload:
                script.hook_text = self._optional_str(payload.get("hook_text"))
            if "cta_text" in payload:
                script.cta_text = self._optional_str(payload.get("cta_text"))
            if "status" in payload:
                script.status = str(payload["status"] or "draft")
            if "platform" in payload:
                script.platform = str(payload["platform"] or "tiktok")
            if "tone" in payload:
                script.tone = self._optional_str(payload.get("tone"))
            if "tags" in payload:
                script.tags_json = self._to_string_list(payload.get("tags"))
            if "metadata" in payload:
                script.metadata_json = self._copy_dict(payload.get("metadata"))
            if "scheduled_at" in payload:
                script.scheduled_at = self._optional_datetime(payload.get("scheduled_at"))
            if "asset_id" in payload:
                asset_id = self._optional_int(payload.get("asset_id"))
                if asset_id is not None and session_any.get(Asset, asset_id) is None:
                    raise ValueError(f"素材不存在：{asset_id}")
                script.asset_id = asset_id
            if "template_id" in payload:
                template_id = self._optional_int(payload.get("template_id"))
                if template_id is not None and session_any.get(content_template_model, template_id) is None:
                    raise ValueError(f"模板不存在：{template_id}")
                script.template_id = template_id

            session_any.add(script)
            session_any.flush()
            session_any.refresh(script)
            return self._to_script_dto(script)

    def get_content_calendar(self) -> ContentCalendarOverviewDTO:
        """返回脚本排期与发布计划的内容日历总览。"""

        self._ensure_initialized()
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(days=7)
        window_end = now + timedelta(days=30)
        items: list[ContentCalendarEntryDTO] = []

        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            script_model = _script_model()
            script_statement = cast(Any, select(script_model))
            script_statement = script_statement.where(cast(Any, getattr(script_model, "is_deleted")).is_(False))
            script_statement = script_statement.where(cast(Any, getattr(script_model, "scheduled_at")).is_not(None))
            script_statement = script_statement.where(cast(Any, getattr(script_model, "scheduled_at")) >= window_start)
            script_statement = script_statement.where(cast(Any, getattr(script_model, "scheduled_at")) <= window_end)
            script_statement = script_statement.order_by(cast(Any, getattr(script_model, "scheduled_at")).asc())
            scripts = list(session_any.scalars(script_statement).all())

            schedule_statement = cast(Any, select(PublishSchedule))
            schedule_statement = schedule_statement.where(cast(Any, getattr(PublishSchedule, "scheduled_time")) >= window_start)
            schedule_statement = schedule_statement.where(cast(Any, getattr(PublishSchedule, "scheduled_time")) <= window_end)
            schedule_statement = schedule_statement.order_by(cast(Any, getattr(PublishSchedule, "scheduled_time")).asc())
            schedules = list(session_any.scalars(schedule_statement).all())

        for script in scripts:
            if script.scheduled_at is None:
                continue
            items.append(
                ContentCalendarEntryDTO(
                    source_type="script",
                    source_id=int(script.id),
                    title=script.title,
                    status=script.status,
                    scheduled_at=script.scheduled_at,
                    owner=script.platform,
                    metadata=self._copy_dict(script.metadata_json),
                )
            )

        for schedule in schedules:
            items.append(
                ContentCalendarEntryDTO(
                    source_type="publish_schedule",
                    source_id=int(schedule.id),
                    title=schedule.title,
                    status=schedule.status,
                    scheduled_at=schedule.scheduled_time,
                    owner=schedule.account_id,
                    metadata=self._copy_dict(schedule.content_json),
                )
            )

        items.sort(key=lambda item: item.scheduled_at)
        overdue_statuses = {"pending", "draft", "queued"}
        upcoming_count = sum(1 for item in items if item.scheduled_at >= now)
        overdue_count = sum(1 for item in items if item.scheduled_at < now and item.status in overdue_statuses)

        return ContentCalendarOverviewDTO(
            items=items,
            total_scheduled=len(items),
            upcoming_count=upcoming_count,
            overdue_count=overdue_count,
            window_start=window_start,
            window_end=window_end,
        )

    def list_templates(self) -> list[ContentTemplateDTO]:
        """列出可用内容模板。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            content_template_model = _content_template_model()
            statement = cast(Any, select(content_template_model))
            statement = statement.where(cast(Any, getattr(content_template_model, "is_deleted")).is_(False))
            statement = statement.order_by(cast(Any, getattr(content_template_model, "created_at")).desc())
            templates = list(session_any.scalars(statement).all())
            return [self._to_template_dto(template) for template in templates]

    def create_from_template(self, template_id: int, params: Mapping[str, object] | None = None) -> ScriptDTO:
        """基于内容模板生成脚本并持久化。"""

        self._ensure_initialized()
        normalized_params = dict(params or {})

        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            content_template_model = _content_template_model()
            script_model = _script_model()
            template = session_any.get(content_template_model, template_id)
            if template is None or bool(template.is_deleted):
                raise ValueError(f"模板不存在：{template_id}")

            merged_params: dict[str, object] = self._copy_dict(template.default_params_json)
            merged_params.update(normalized_params)
            self._validate_template_params(template, merged_params)
            safe_params = _SafeTemplateDict(merged_params)
            title = template.title_template.format_map(safe_params)
            body = template.body_template.format_map(safe_params)
            hook_text = self._first_available_param(merged_params, ("hook", "pain_point"))
            cta_text = self._optional_str(merged_params.get("cta"))

            metadata_payload = self._copy_dict(template.metadata_json)
            metadata_payload["generated_from_template"] = template.id
            metadata_payload["template_name"] = template.name
            metadata_payload["render_params"] = {key: self._stringify_json_value(value) for key, value in merged_params.items()}

            script = script_model()
            script.title = title
            script.body = body
            script.hook_text = hook_text
            script.cta_text = cta_text
            script.status = "draft"
            script.platform = str(merged_params.get("platform") or "tiktok")
            script.tone = self._optional_str(merged_params.get("tone"))
            script.tags_json = self._to_string_list(merged_params.get("tags"))
            script.metadata_json = metadata_payload
            script.scheduled_at = self._optional_datetime(merged_params.get("scheduled_at"))
            script.asset_id = self._optional_int(merged_params.get("asset_id"))
            script.template_id = int(template.id)
            script.is_deleted = False
            if script.asset_id is not None and session_any.get(Asset, script.asset_id) is None:
                raise ValueError(f"素材不存在：{script.asset_id}")

            session_any.add(script)
            session_any.flush()
            session_any.refresh(script)
            return self._to_script_dto(script)

    def create_content_task(self, payload: Mapping[str, object]) -> str:
        """兼容旧接口，将内容任务创建映射为脚本创建。"""

        script = self.create_script(payload)
        return str(script.id)

    def _ensure_initialized(self) -> None:
        """确保服务已完成初始化。"""

        if not self._initialized:
            self.initialize()

    def _seed_default_templates(self) -> None:
        """在空库中写入默认内容模板。"""

        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            content_template_model = _content_template_model()
            existing_count = len(list(session_any.scalars(cast(Any, select(content_template_model))).all()))
            if existing_count > 0:
                return
            for template_payload in self._DEFAULT_TEMPLATES:
                template = content_template_model()
                template.name = str(template_payload["name"])
                template.category = str(template_payload["category"])
                template.title_template = str(template_payload["title_template"])
                template.body_template = str(template_payload["body_template"])
                template.description = self._optional_str(template_payload.get("description"))
                template.parameter_schema_json = self._to_dict_list(template_payload.get("parameter_schema_json"))
                template.default_params_json = self._copy_dict(template_payload.get("default_params_json"))
                template.status = str(template_payload.get("status") or "active")
                template.metadata_json = self._copy_dict(template_payload.get("metadata_json"))
                template.is_deleted = False
                session_any.add(template)
            session_any.flush()

    def _normalize_asset_filters(self, filters: AssetFilters | Mapping[str, object] | None) -> AssetFilters:
        """标准化素材筛选参数。"""

        if filters is None:
            return AssetFilters()
        if isinstance(filters, AssetFilters):
            return filters
        return AssetFilters(
            asset_type=self._optional_str(filters.get("type") or filters.get("asset_type")),
            status=self._optional_str(filters.get("status")),
            created_from=self._optional_datetime(filters.get("date_from") or filters.get("created_from")),
            created_to=self._optional_datetime(filters.get("date_to") or filters.get("created_to")),
        )

    def _apply_asset_updates(self, asset: Asset, updates: Mapping[str, object]) -> None:
        """将更新字段应用到素材实体。"""

        if "name" in updates:
            asset.name = str(updates["name"] or asset.name)
        if "thumbnail_path" in updates:
            asset.thumbnail_path = self._optional_str(updates.get("thumbnail_path"))
        if "duration_seconds" in updates:
            asset.duration_seconds = self._optional_int(updates.get("duration_seconds"))
        if "size_bytes" in updates:
            asset.size_bytes = self._optional_int(updates.get("size_bytes"))
        if "tags" in updates:
            asset.tags_json = self._to_string_list(updates.get("tags"))
        if "asset_type" in updates:
            asset.asset_type = self._normalize_asset_type(updates.get("asset_type"), Path(asset.file_path).suffix)

        metadata_payload = self._copy_dict(asset.metadata_json)
        if "status" in updates:
            metadata_payload["status"] = str(updates["status"] or metadata_payload.get("status") or "active")
            if metadata_payload["status"] != "deleted":
                asset.is_deleted = False
                asset.deleted_at = None
        if "metadata" in updates:
            metadata_payload.update(self._copy_dict(updates.get("metadata")))
        asset.metadata_json = metadata_payload

    def _validate_template_params(self, template: object, params: Mapping[str, object]) -> None:
        """校验模板必填参数是否齐备。"""

        template_any = cast(Any, template)
        missing_keys: list[str] = []
        for item in self._to_dict_list(template_any.parameter_schema_json):
            name = self._optional_str(item.get("name"))
            required = bool(item.get("required", False))
            if not name or not required:
                continue
            value = params.get(name)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing_keys.append(name)

        formatter = Formatter()
        referenced_keys = {
            field_name
            for _, field_name, _, _ in formatter.parse(str(template_any.title_template) + str(template_any.body_template))
            if field_name
        }
        for field_name in sorted(referenced_keys):
            value = params.get(field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                if field_name not in missing_keys:
                    missing_keys.append(field_name)

        if missing_keys:
            raise ValueError(f"模板参数缺失：{', '.join(missing_keys)}")

    def _to_asset_dto(self, asset: Asset) -> AssetDTO:
        """将素材实体转换为 DTO。"""

        return AssetDTO(
            id=int(asset.id),
            name=str(asset.name),
            asset_type=str(asset.asset_type),
            file_path=str(asset.file_path),
            thumbnail_path=self._optional_str(asset.thumbnail_path),
            size_bytes=self._optional_int(asset.size_bytes),
            duration_seconds=self._optional_int(asset.duration_seconds),
            tags=self._to_string_list(asset.tags_json),
            status=self._asset_status(asset),
            metadata=self._copy_dict(asset.metadata_json),
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            deleted_at=asset.deleted_at,
        )

    def _to_script_dto(self, script: object) -> ScriptDTO:
        """将脚本实体转换为 DTO。"""

        script_any = cast(Any, script)
        return ScriptDTO(
            id=int(script_any.id),
            title=str(script_any.title),
            body=str(script_any.body),
            hook_text=self._optional_str(script_any.hook_text),
            cta_text=self._optional_str(script_any.cta_text),
            status=str(script_any.status),
            platform=str(script_any.platform),
            tone=self._optional_str(script_any.tone),
            tags=self._to_string_list(script_any.tags_json),
            metadata=self._copy_dict(script_any.metadata_json),
            scheduled_at=script_any.scheduled_at,
            asset_id=self._optional_int(script_any.asset_id),
            template_id=self._optional_int(script_any.template_id),
            created_at=script_any.created_at,
            updated_at=script_any.updated_at,
        )

    def _to_template_dto(self, template: object) -> ContentTemplateDTO:
        """将模板实体转换为 DTO。"""

        template_any = cast(Any, template)
        return ContentTemplateDTO(
            id=int(template_any.id),
            name=str(template_any.name),
            category=str(template_any.category),
            title_template=str(template_any.title_template),
            body_template=str(template_any.body_template),
            description=self._optional_str(template_any.description),
            parameter_schema=self._to_dict_list(template_any.parameter_schema_json),
            default_params=self._copy_dict(template_any.default_params_json),
            status=str(template_any.status),
            metadata=self._copy_dict(template_any.metadata_json),
            created_at=template_any.created_at,
            updated_at=template_any.updated_at,
        )

    def _asset_status(self, asset: Asset) -> str:
        """统一解析素材状态。"""

        if bool(asset.is_deleted):
            return "deleted"
        metadata_payload = self._copy_dict(asset.metadata_json)
        return str(metadata_payload.get("status") or "active")

    def _extract_asset_metadata_payload(self, metadata: Mapping[str, object], status: str) -> dict[str, object]:
        """提取可持久化的素材元数据。"""

        excluded_keys = {
            "name",
            "asset_type",
            "thumbnail_path",
            "size_bytes",
            "duration_seconds",
            "tags",
            "status",
        }
        payload = {key: self._stringify_json_value(value) for key, value in metadata.items() if key not in excluded_keys}
        payload["status"] = status
        return payload

    def _normalize_asset_type(self, asset_type: object, suffix: str) -> str:
        """标准化素材类型，确保满足数据库约束。"""

        normalized = str(asset_type or "").strip().lower()
        if normalized in {"image", "video", "audio", "document"}:
            return normalized

        suffix_map = {
            ".jpg": "image",
            ".jpeg": "image",
            ".png": "image",
            ".gif": "image",
            ".webp": "image",
            ".mp4": "video",
            ".mov": "video",
            ".avi": "video",
            ".mkv": "video",
            ".mp3": "audio",
            ".wav": "audio",
            ".aac": "audio",
            ".pdf": "document",
            ".doc": "document",
            ".docx": "document",
            ".txt": "document",
        }
        return suffix_map.get(suffix.lower(), "document")

    def _resolve_size_bytes(self, path: Path, provided_size: object) -> int | None:
        """解析素材大小，优先使用文件大小，其次读取显式参数。"""

        if path.exists() and path.is_file():
            return int(path.stat().st_size)
        return self._optional_int(provided_size)

    def _optional_str(self, value: object) -> str | None:
        """将可空值转为字符串。"""

        if value is None:
            return None
        text = str(value)
        return text if text != "" else None

    def _optional_int(self, value: object) -> int | None:
        """将可空值转为整数。"""

        if value is None or value == "":
            return None
        return int(str(value))

    def _optional_datetime(self, value: object) -> datetime | None:
        """将输入解析为日期时间对象。"""

        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value))

    def _to_string_list(self, value: object) -> list[str]:
        """将任意序列值标准化为字符串列表。"""

        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, (list, tuple, set)):
            return [str(item) for item in value if str(item).strip()]
        return [str(value)]

    def _copy_dict(self, value: object) -> dict[str, object]:
        """复制字典值并确保键为字符串。"""

        if not isinstance(value, Mapping):
            return {}
        return {str(key): self._stringify_json_value(item) for key, item in value.items()}

    def _to_dict_list(self, value: object) -> list[dict[str, object]]:
        """将输入标准化为字典列表。"""

        if not isinstance(value, list):
            return []
        result: list[dict[str, object]] = []
        for item in value:
            if isinstance(item, Mapping):
                result.append({str(key): self._stringify_json_value(inner_value) for key, inner_value in item.items()})
        return result

    def _stringify_json_value(self, value: object) -> object:
        """确保嵌套值适合 JSON 持久化。"""

        if isinstance(value, Mapping):
            return {str(key): self._stringify_json_value(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._stringify_json_value(item) for item in value]
        if isinstance(value, tuple):
            return [self._stringify_json_value(item) for item in value]
        if isinstance(value, set):
            return [self._stringify_json_value(item) for item in value]
        return cast(object, value)

    def _first_available_param(self, params: Mapping[str, object], keys: tuple[str, ...]) -> str | None:
        """按顺序查找第一个存在的模板参数。"""

        for key in keys:
            value = self._optional_str(params.get(key))
            if value is not None:
                return value
        return None


__all__ = [
    "AssetDTO",
    "AssetFilters",
    "BatchUpdateResultDTO",
    "ContentCalendarEntryDTO",
    "ContentCalendarOverviewDTO",
    "ContentService",
    "ContentTemplateDTO",
    "ScriptDTO",
]
