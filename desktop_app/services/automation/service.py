from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportCallIssue=false

"""自动化领域服务实现。"""

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, cast

from ...data.database import Database
from ...data.models.automation import AutoReplyRule, AutomationTask, CollectionTask
from ...data.models.log import LogEntry
from ...data.models.schedule import PublishSchedule
from ...data.repositories.automation_repo import AutomationRepository


@dataclass
class DateRangeDTO:
    """时间范围 DTO。"""

    start_at: datetime | None = None
    end_at: datetime | None = None


@dataclass
class AutomationConfigDTO:
    """自动互动配置 DTO。"""

    task_type: str
    display_name: str
    enabled: bool = True
    account_ids: list[str] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    exclude_keywords: list[str] = field(default_factory=list)
    active_hours: list[str] = field(default_factory=list)
    daily_limit: int = 0
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class AutomationTaskDTO:
    """自动任务 DTO。"""

    task_id: int
    task_type: str
    task_category: str
    display_name: str
    status: str
    enabled: bool
    config: dict[str, object]
    runtime: dict[str, object]
    last_started_at: str | None
    last_stopped_at: str | None
    last_healthcheck_at: str | None
    last_error: str | None


@dataclass
class AutomationStatusDTO:
    """自动化状态总览 DTO。"""

    initialized: bool
    running_count: int
    enabled_count: int
    auto_engagement: list[AutomationTaskDTO] = field(default_factory=list)


@dataclass
class AutoReplyRuleDTO:
    """自动回复规则 DTO。"""

    rule_id: int
    rule_name: str
    trigger_type: str
    trigger_value: str
    match_mode: str
    reply_text: str
    is_active: bool
    priority: int
    channels: list[str] = field(default_factory=list)
    conditions: dict[str, object] = field(default_factory=dict)
    last_triggered_at: str | None = None
    trigger_count: int = 0
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class AutoReplyLogDTO:
    """自动回复日志 DTO。"""

    log_id: int
    timestamp: str | None
    level: str
    message: str
    details: dict[str, object] = field(default_factory=dict)


@dataclass
class ScheduledPostDTO:
    """计划发布 DTO。"""

    post_id: int
    title: str
    account_id: str
    content_type: str
    content: dict[str, object]
    scheduled_time: str | None
    timezone: str
    status: str
    recurrence_rule: str | None
    created_at: str | None
    updated_at: str | None


@dataclass
class CollectionTaskDTO:
    """采集任务 DTO。"""

    task_id: int
    task_name: str
    source_type: str
    status: str
    keywords: list[str] = field(default_factory=list)
    config: dict[str, object] = field(default_factory=dict)
    result: dict[str, object] = field(default_factory=dict)
    items_collected: int = 0
    started_at: str | None = None
    completed_at: str | None = None
    stopped_at: str | None = None
    error_message: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class AutomationService:
    """自动化中心领域服务。"""

    service_name: str = "automation"
    _TASK_LABELS: dict[str, str] = {
        "auto_like": "自动点赞",
        "auto_comment": "自动评论",
        "auto_dm": "自动私信",
    }

    def __init__(self, database: Database | None = None) -> None:
        """初始化自动化服务。"""

        self._database: Database = database or Database()
        self._automation_repo: AutomationRepository = AutomationRepository()
        self._initialized: bool = False

    def initialize(self) -> None:
        """初始化数据库结构并补齐默认自动任务。"""

        self._database.create_all()
        with self._database.session_scope() as session:
            for task_type, display_name in self._TASK_LABELS.items():
                task = self._automation_repo.get_automation_task(session, task_type)
                if task is None:
                    self._automation_repo.save_automation_task(
                        session,
                        cast(Any, AutomationTask)(
                            task_type=task_type,
                            task_category="auto_engagement",
                            display_name=display_name,
                            status="idle",
                            is_enabled=True,
                            config_json=self._default_config(task_type, display_name),
                            runtime_json={"runs": 0, "last_action": "initialized"},
                        ),
                    )
        self._initialized = True

    def shutdown(self) -> None:
        """关闭运行态。"""

        self._initialized = False

    def healthcheck(self) -> dict[str, object]:
        """返回自动化服务健康状态。"""

        with self._database.session_scope() as session:
            tasks = self._automation_repo.list_automation_tasks(session, category="auto_engagement")
            rule_count = self._automation_repo.count_auto_reply_rules(session)
            collection_count = self._automation_repo.count_collection_tasks(session)
        running_count = len([task for task in tasks if task.status == "running"])
        return {
            "service": self.service_name,
            "status": "ok",
            "initialized": self._initialized,
            "database": "connected",
            "auto_engagement_tasks": len(tasks),
            "running_tasks": running_count,
            "auto_reply_rules": rule_count,
            "collection_tasks": collection_count,
        }

    def configure_auto_like(self, config: AutomationConfigDTO | Mapping[str, object]) -> dict[str, object]:
        """配置自动点赞。"""

        return self._configure_auto_engagement("auto_like", config)

    def configure_auto_comment(self, config: AutomationConfigDTO | Mapping[str, object]) -> dict[str, object]:
        """配置自动评论。"""

        return self._configure_auto_engagement("auto_comment", config)

    def configure_auto_dm(self, config: AutomationConfigDTO | Mapping[str, object]) -> dict[str, object]:
        """配置自动私信。"""

        return self._configure_auto_engagement("auto_dm", config)

    def get_automation_status(self) -> dict[str, object]:
        """返回自动互动状态总览。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            tasks = self._automation_repo.list_automation_tasks(session, category="auto_engagement")
            now = datetime.now(timezone.utc)
            task_dtos: list[AutomationTaskDTO] = []
            for task in tasks:
                task.last_healthcheck_at = now
                session.add(task)
                task_dtos.append(self._to_automation_task_dto(task))
        status = AutomationStatusDTO(
            initialized=self._initialized,
            running_count=len([item for item in task_dtos if item.status == "running"]),
            enabled_count=len([item for item in task_dtos if item.enabled]),
            auto_engagement=task_dtos,
        )
        return self._dto_to_dict(status)

    def start_automation(self, task_type: str) -> dict[str, object]:
        """启动指定自动互动任务。"""

        normalized_task_type = self._normalize_task_type(task_type)
        self._ensure_initialized()
        now = datetime.now(timezone.utc)
        with self._database.session_scope() as session:
            task = self._require_automation_task(session, normalized_task_type)
            if not task.is_enabled:
                raise ValueError(f"任务未启用: {normalized_task_type}")
            runtime = dict(task.runtime_json or {})
            runtime["runs"] = int(runtime.get("runs", 0)) + 1
            runtime["last_action"] = "started"
            runtime["last_action_at"] = self._to_iso(now)
            task.status = "running"
            task.last_started_at = now
            task.last_error = None
            task.runtime_json = runtime
            self._automation_repo.save_automation_task(session, task)
            self._automation_repo.create_log(
                session,
                module="automation.runtime",
                message=f"已启动自动任务: {normalized_task_type}",
                details_json={"task_type": normalized_task_type, "action": "start"},
            )
            dto = self._to_automation_task_dto(task)
        return self._dto_to_dict(dto)

    def stop_automation(self, task_type: str) -> dict[str, object]:
        """停止指定自动互动任务。"""

        normalized_task_type = self._normalize_task_type(task_type)
        self._ensure_initialized()
        now = datetime.now(timezone.utc)
        with self._database.session_scope() as session:
            task = self._require_automation_task(session, normalized_task_type)
            runtime = dict(task.runtime_json or {})
            runtime["last_action"] = "stopped"
            runtime["last_action_at"] = self._to_iso(now)
            task.status = "idle" if task.is_enabled else "disabled"
            task.last_stopped_at = now
            task.runtime_json = runtime
            self._automation_repo.save_automation_task(session, task)
            self._automation_repo.create_log(
                session,
                module="automation.runtime",
                message=f"已停止自动任务: {normalized_task_type}",
                details_json={"task_type": normalized_task_type, "action": "stop"},
            )
            dto = self._to_automation_task_dto(task)
        return self._dto_to_dict(dto)

    def list_auto_reply_rules(self) -> list[dict[str, object]]:
        """列出自动回复规则。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            rules = self._automation_repo.list_auto_reply_rules(session)
        return [self._dto_to_dict(self._to_auto_reply_rule_dto(rule)) for rule in rules]

    def create_auto_reply_rule(self, rule_data: Mapping[str, object]) -> dict[str, object]:
        """创建自动回复规则。"""

        self._ensure_initialized()
        payload = self._normalize_auto_reply_rule_payload(rule_data)
        with self._database.session_scope() as session:
            rule = cast(Any, AutoReplyRule)(**payload)
            self._automation_repo.save_auto_reply_rule(session, rule)
            self._automation_repo.create_log(
                session,
                module="automation.auto_reply",
                message=f"已创建自动回复规则: {rule.rule_name}",
                details_json={"rule_id": int(rule.id), "trigger_type": rule.trigger_type},
            )
            dto = self._to_auto_reply_rule_dto(rule)
        return self._dto_to_dict(dto)

    def update_auto_reply_rule(self, rule_id: int, data: Mapping[str, object]) -> dict[str, object]:
        """更新自动回复规则。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            rule = self._automation_repo.get_auto_reply_rule(session, int(rule_id))
            if rule is None:
                raise LookupError(f"自动回复规则不存在: {rule_id}")
            payload = self._normalize_auto_reply_rule_payload(data, existing=rule)
            for key, value in payload.items():
                setattr(rule, key, value)
            self._automation_repo.save_auto_reply_rule(session, rule)
            self._automation_repo.create_log(
                session,
                module="automation.auto_reply",
                message=f"已更新自动回复规则: {rule.rule_name}",
                details_json={"rule_id": int(rule.id), "trigger_type": rule.trigger_type},
            )
            dto = self._to_auto_reply_rule_dto(rule)
        return self._dto_to_dict(dto)

    def delete_auto_reply_rule(self, rule_id: int) -> bool:
        """删除自动回复规则。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            rule = self._automation_repo.get_auto_reply_rule(session, int(rule_id))
            if rule is None:
                return False
            self._automation_repo.create_log(
                session,
                module="automation.auto_reply",
                message=f"已删除自动回复规则: {rule.rule_name}",
                details_json={"rule_id": int(rule.id)},
            )
            self._automation_repo.delete_auto_reply_rule(session, rule)
        return True

    def get_auto_reply_logs(self, date_range: DateRangeDTO | Mapping[str, object] | None = None) -> list[dict[str, object]]:
        """查询自动回复日志。"""

        self._ensure_initialized()
        normalized_range = self._normalize_date_range(date_range)
        with self._database.session_scope() as session:
            logs = self._automation_repo.list_auto_reply_logs(session, normalized_range.start_at, normalized_range.end_at)
        return [self._dto_to_dict(self._to_auto_reply_log_dto(entry)) for entry in logs]

    def list_scheduled_posts(self) -> list[dict[str, object]]:
        """列出计划发布任务。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            posts = self._automation_repo.list_scheduled_posts(session)
        return [self._dto_to_dict(self._to_scheduled_post_dto(post)) for post in posts]

    def schedule_post(self, post_data: Mapping[str, object]) -> dict[str, object]:
        """创建新的计划发布记录。"""

        self._ensure_initialized()
        payload = self._normalize_schedule_payload(post_data)
        with self._database.session_scope() as session:
            post = cast(Any, PublishSchedule)(**payload)
            self._automation_repo.save_scheduled_post(session, post)
            self._automation_repo.create_log(
                session,
                module="automation.schedule",
                message=f"已创建计划发布: {post.title}",
                details_json={"post_id": int(post.id), "status": post.status},
            )
            dto = self._to_scheduled_post_dto(post)
        return self._dto_to_dict(dto)

    def cancel_scheduled_post(self, post_id: int) -> dict[str, object]:
        """取消指定计划发布。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            post = self._automation_repo.get_scheduled_post(session, int(post_id))
            if post is None:
                raise LookupError(f"计划发布不存在: {post_id}")
            post.status = "cancelled"
            self._automation_repo.save_scheduled_post(session, post)
            self._automation_repo.create_log(
                session,
                module="automation.schedule",
                message=f"已取消计划发布: {post.title}",
                details_json={"post_id": int(post.id), "status": post.status},
            )
            dto = self._to_scheduled_post_dto(post)
        return self._dto_to_dict(dto)

    def reschedule_post(self, post_id: int, new_datetime: datetime | str) -> dict[str, object]:
        """调整计划发布时间。"""

        self._ensure_initialized()
        normalized_time = self._coerce_datetime(new_datetime)
        if normalized_time <= datetime.now(timezone.utc):
            raise ValueError("新的发布时间必须晚于当前时间")
        with self._database.session_scope() as session:
            post = self._automation_repo.get_scheduled_post(session, int(post_id))
            if post is None:
                raise LookupError(f"计划发布不存在: {post_id}")
            post.scheduled_time = normalized_time
            post.status = "pending"
            self._automation_repo.save_scheduled_post(session, post)
            self._automation_repo.create_log(
                session,
                module="automation.schedule",
                message=f"已重新排期发布: {post.title}",
                details_json={"post_id": int(post.id), "scheduled_time": self._to_iso(post.scheduled_time)},
            )
            dto = self._to_scheduled_post_dto(post)
        return self._dto_to_dict(dto)

    def create_collection_task(self, task_config: Mapping[str, object]) -> dict[str, object]:
        """创建数据采集任务。"""

        self._ensure_initialized()
        payload = self._normalize_collection_payload(task_config)
        now = datetime.now(timezone.utc)
        result = self._build_collection_result(payload, now)
        with self._database.session_scope() as session:
            task = cast(Any, CollectionTask)(
                task_name=str(payload["task_name"]),
                source_type=str(payload["source_type"]),
                status="running",
                keywords_json=cast(list[str], payload["keywords_json"]),
                config_json=cast(dict[str, object], payload["config_json"]),
                result_json=result,
                items_collected=self._to_int(result.get("items_collected"), default=0),
                started_at=now,
            )
            self._automation_repo.save_collection_task(session, task)
            self._automation_repo.create_log(
                session,
                module="automation.collection",
                message=f"已创建采集任务: {task.task_name}",
                details_json={"task_id": int(task.id), "source_type": task.source_type},
            )
            dto = self._to_collection_task_dto(task)
        return self._dto_to_dict(dto)

    def list_collection_tasks(self) -> list[dict[str, object]]:
        """列出数据采集任务。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            tasks = self._automation_repo.list_collection_tasks(session)
        return [self._dto_to_dict(self._to_collection_task_dto(task)) for task in tasks]

    def get_collection_results(self, task_id: int) -> dict[str, object]:
        """返回指定采集任务结果。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            task = self._automation_repo.get_collection_task(session, int(task_id))
            if task is None:
                raise LookupError(f"采集任务不存在: {task_id}")
            dto = self._to_collection_task_dto(task)
        return self._dto_to_dict(dto)

    def stop_collection_task(self, task_id: int) -> dict[str, object]:
        """停止采集任务并保留已采集结果。"""

        self._ensure_initialized()
        now = datetime.now(timezone.utc)
        with self._database.session_scope() as session:
            task = self._automation_repo.get_collection_task(session, int(task_id))
            if task is None:
                raise LookupError(f"采集任务不存在: {task_id}")
            result = dict(task.result_json or {})
            result["stopped_at"] = self._to_iso(now)
            result["status_note"] = "任务已手动停止，返回当前采集结果"
            task.result_json = result
            task.status = "stopped"
            task.stopped_at = now
            task.completed_at = now
            self._automation_repo.save_collection_task(session, task)
            self._automation_repo.create_log(
                session,
                module="automation.collection",
                message=f"已停止采集任务: {task.task_name}",
                details_json={"task_id": int(task.id), "items_collected": int(task.items_collected or 0)},
            )
            dto = self._to_collection_task_dto(task)
        return self._dto_to_dict(dto)

    def schedule_job(self, payload: dict[str, object]) -> str:
        """兼容旧接口，调度计划发布任务。"""

        post = self.schedule_post(payload)
        return str(post["post_id"])

    def cancel_job(self, job_id: str) -> None:
        """兼容旧接口，取消计划发布任务。"""

        self.cancel_scheduled_post(int(job_id))

    def _configure_auto_engagement(self, task_type: str, config: AutomationConfigDTO | Mapping[str, object]) -> dict[str, object]:
        """保存自动互动配置。"""

        normalized_task_type = self._normalize_task_type(task_type)
        self._ensure_initialized()
        config_dto = self._normalize_automation_config(normalized_task_type, config)
        now = datetime.now(timezone.utc)
        with self._database.session_scope() as session:
            task = self._automation_repo.get_automation_task(session, normalized_task_type)
            if task is None:
                task = cast(Any, AutomationTask)(
                    task_type=normalized_task_type,
                    task_category="auto_engagement",
                    display_name=config_dto.display_name,
                    status="idle",
                    is_enabled=config_dto.enabled,
                    config_json={},
                    runtime_json={"runs": 0},
                )
            task.display_name = config_dto.display_name
            task.is_enabled = config_dto.enabled
            task.status = task.status if task.status == "running" and config_dto.enabled else ("idle" if config_dto.enabled else "disabled")
            task.config_json = self._dto_to_dict(config_dto)
            runtime = dict(task.runtime_json or {})
            runtime["last_action"] = "configured"
            runtime["last_action_at"] = self._to_iso(now)
            task.runtime_json = runtime
            self._automation_repo.save_automation_task(session, task)
            self._automation_repo.create_log(
                session,
                module="automation.runtime",
                message=f"已更新自动任务配置: {normalized_task_type}",
                details_json={"task_type": normalized_task_type, "enabled": config_dto.enabled},
            )
            dto = self._to_automation_task_dto(task)
        return self._dto_to_dict(dto)

    def _normalize_automation_config(
        self,
        task_type: str,
        config: AutomationConfigDTO | Mapping[str, object],
    ) -> AutomationConfigDTO:
        """标准化自动互动配置。"""

        if isinstance(config, AutomationConfigDTO):
            normalized = config
        else:
            data = dict(config)
            normalized = AutomationConfigDTO(
                task_type=task_type,
                display_name=str(data.get("display_name") or self._TASK_LABELS.get(task_type, task_type)),
                enabled=bool(data.get("enabled", True)),
                account_ids=self._to_str_list(data.get("account_ids")),
                triggers=self._to_str_list(data.get("triggers")),
                keywords=self._to_str_list(data.get("keywords")),
                exclude_keywords=self._to_str_list(data.get("exclude_keywords")),
                active_hours=self._to_str_list(data.get("active_hours")),
                daily_limit=max(self._to_int(data.get("daily_limit"), default=0), 0),
                metadata=self._to_dict(data.get("metadata")),
            )
        if normalized.task_type != task_type:
            normalized.task_type = task_type
        if not normalized.display_name.strip():
            raise ValueError("display_name 不能为空")
        return normalized

    def _normalize_auto_reply_rule_payload(
        self,
        data: Mapping[str, object],
        existing: AutoReplyRule | None = None,
    ) -> dict[str, object]:
        """标准化自动回复规则输入。"""

        payload = dict(data)
        rule_name = str(payload.get("rule_name") or getattr(existing, "rule_name", "")).strip()
        trigger_type = str(payload.get("trigger_type") or getattr(existing, "trigger_type", "keyword")).strip()
        trigger_value = str(payload.get("trigger_value") or getattr(existing, "trigger_value", "")).strip()
        match_mode = str(payload.get("match_mode") or getattr(existing, "match_mode", "contains")).strip()
        reply_text = str(payload.get("reply_text") or getattr(existing, "reply_text", "")).strip()
        if not rule_name:
            raise ValueError("rule_name 不能为空")
        if not trigger_value:
            raise ValueError("trigger_value 不能为空")
        if not reply_text:
            raise ValueError("reply_text 不能为空")
        return {
            "rule_name": rule_name,
            "trigger_type": trigger_type or "keyword",
            "trigger_value": trigger_value,
            "match_mode": match_mode or "contains",
            "reply_text": reply_text,
            "is_active": bool(payload.get("is_active", getattr(existing, "is_active", True))),
            "priority": max(self._to_int(payload.get("priority", getattr(existing, "priority", 100)), default=100), 0),
            "channels_json": self._to_str_list(payload.get("channels") or getattr(existing, "channels_json", [])),
            "conditions_json": self._to_dict(payload.get("conditions") or getattr(existing, "conditions_json", {})),
        }

    def _normalize_schedule_payload(self, data: Mapping[str, object]) -> dict[str, object]:
        """标准化计划发布输入。"""

        title = str(data.get("title") or "").strip()
        account_id = str(data.get("account_id") or "").strip()
        content_type = str(data.get("content_type") or "video").strip()
        scheduled_time = self._coerce_datetime(data.get("scheduled_time"))
        if not title:
            raise ValueError("title 不能为空")
        if not account_id:
            raise ValueError("account_id 不能为空")
        if scheduled_time <= datetime.now(timezone.utc):
            raise ValueError("scheduled_time 必须晚于当前时间")
        return {
            "title": title,
            "account_id": account_id,
            "content_type": content_type or "video",
            "content_json": self._to_dict(data.get("content") or data.get("content_json")),
            "scheduled_time": scheduled_time,
            "timezone": str(data.get("timezone") or "UTC"),
            "status": str(data.get("status") or "pending"),
            "recurrence_rule": self._optional_str(data.get("recurrence_rule")),
        }

    def _normalize_collection_payload(self, data: Mapping[str, object]) -> dict[str, object]:
        """标准化采集任务输入。"""

        task_name = str(data.get("task_name") or data.get("name") or "").strip()
        source_type = str(data.get("source_type") or "keyword_search").strip()
        keywords = self._to_str_list(data.get("keywords"))
        if not task_name:
            raise ValueError("task_name 不能为空")
        if not keywords:
            raise ValueError("keywords 不能为空")
        config = self._to_dict(data)
        config.setdefault("limit", max(self._to_int(config.get("limit"), default=20), 1))
        return {
            "task_name": task_name,
            "source_type": source_type or "keyword_search",
            "keywords_json": keywords,
            "config_json": config,
        }

    def _normalize_date_range(self, value: DateRangeDTO | Mapping[str, object] | None) -> DateRangeDTO:
        """标准化时间范围输入。"""

        if value is None:
            return DateRangeDTO()
        if isinstance(value, DateRangeDTO):
            return value
        data = dict(value)
        start_at_raw = data.get("start_at") or data.get("start")
        end_at_raw = data.get("end_at") or data.get("end")
        return DateRangeDTO(
            start_at=self._coerce_datetime(start_at_raw) if start_at_raw else None,
            end_at=self._coerce_datetime(end_at_raw) if end_at_raw else None,
        )

    def _require_automation_task(self, session: Any, task_type: str) -> AutomationTask:
        """确保自动任务存在。"""

        task = self._automation_repo.get_automation_task(session, task_type)
        if task is None:
            raise LookupError(f"自动任务不存在: {task_type}")
        return task

    def _to_automation_task_dto(self, task: AutomationTask) -> AutomationTaskDTO:
        """转换自动任务 DTO。"""

        return AutomationTaskDTO(
            task_id=int(task.id),
            task_type=task.task_type,
            task_category=task.task_category,
            display_name=task.display_name,
            status=task.status,
            enabled=bool(task.is_enabled),
            config=self._to_dict(task.config_json),
            runtime=self._to_dict(task.runtime_json),
            last_started_at=self._to_iso(task.last_started_at),
            last_stopped_at=self._to_iso(task.last_stopped_at),
            last_healthcheck_at=self._to_iso(task.last_healthcheck_at),
            last_error=task.last_error,
        )

    def _to_auto_reply_rule_dto(self, rule: AutoReplyRule) -> AutoReplyRuleDTO:
        """转换自动回复规则 DTO。"""

        return AutoReplyRuleDTO(
            rule_id=int(rule.id),
            rule_name=rule.rule_name,
            trigger_type=rule.trigger_type,
            trigger_value=rule.trigger_value,
            match_mode=rule.match_mode,
            reply_text=rule.reply_text,
            is_active=bool(rule.is_active),
            priority=int(rule.priority or 0),
            channels=self._to_str_list(rule.channels_json),
            conditions=self._to_dict(rule.conditions_json),
            last_triggered_at=self._to_iso(rule.last_triggered_at),
            trigger_count=int(rule.trigger_count or 0),
            created_at=self._to_iso(rule.created_at),
            updated_at=self._to_iso(rule.updated_at),
        )

    def _to_auto_reply_log_dto(self, entry: LogEntry) -> AutoReplyLogDTO:
        """转换自动回复日志 DTO。"""

        return AutoReplyLogDTO(
            log_id=int(entry.id),
            timestamp=self._to_iso(entry.timestamp),
            level=entry.level,
            message=entry.message,
            details=self._to_dict(entry.details_json),
        )

    def _to_scheduled_post_dto(self, post: PublishSchedule) -> ScheduledPostDTO:
        """转换计划发布 DTO。"""

        return ScheduledPostDTO(
            post_id=int(post.id),
            title=post.title,
            account_id=post.account_id,
            content_type=post.content_type,
            content=self._to_dict(post.content_json),
            scheduled_time=self._to_iso(post.scheduled_time),
            timezone=post.timezone,
            status=post.status,
            recurrence_rule=post.recurrence_rule,
            created_at=self._to_iso(post.created_at),
            updated_at=self._to_iso(post.updated_at),
        )

    def _to_collection_task_dto(self, task: CollectionTask) -> CollectionTaskDTO:
        """转换采集任务 DTO。"""

        return CollectionTaskDTO(
            task_id=int(task.id),
            task_name=task.task_name,
            source_type=task.source_type,
            status=task.status,
            keywords=self._to_str_list(task.keywords_json),
            config=self._to_dict(task.config_json),
            result=self._to_dict(task.result_json),
            items_collected=int(task.items_collected or 0),
            started_at=self._to_iso(task.started_at),
            completed_at=self._to_iso(task.completed_at),
            stopped_at=self._to_iso(task.stopped_at),
            error_message=task.error_message,
            created_at=self._to_iso(task.created_at),
            updated_at=self._to_iso(task.updated_at),
        )

    def _build_collection_result(self, payload: dict[str, object], now: datetime) -> dict[str, object]:
        """生成采集任务的初始结果快照。"""

        keywords = cast(list[str], payload["keywords_json"])
        config = cast(dict[str, object], payload["config_json"])
        limit = max(self._to_int(config.get("limit"), default=20), 1)
        sample_count = min(len(keywords) * 3, limit)
        items = [
            {
                "rank": index + 1,
                "keyword": keywords[index % len(keywords)],
                "title": f"{keywords[index % len(keywords)]} 相关内容样本 {index + 1}",
                "engagement_score": round(0.62 + (index * 0.03), 2),
                "captured_at": self._to_iso(now),
            }
            for index in range(sample_count)
        ]
        return {
            "summary": {
                "keywords": keywords,
                "requested_limit": limit,
                "status": "running",
            },
            "items": items,
            "items_collected": len(items),
            "generated_at": self._to_iso(now),
        }

    def _ensure_initialized(self) -> None:
        """确保服务已初始化。"""

        if not self._initialized:
            self.initialize()

    def _normalize_task_type(self, task_type: str) -> str:
        """标准化任务类型。"""

        normalized = task_type.strip().lower()
        if normalized not in self._TASK_LABELS:
            raise ValueError(f"不支持的 task_type: {task_type}")
        return normalized

    def _default_config(self, task_type: str, display_name: str) -> dict[str, object]:
        """返回默认任务配置。"""

        return self._dto_to_dict(
            AutomationConfigDTO(
                task_type=task_type,
                display_name=display_name,
                enabled=True,
                account_ids=[],
                triggers=[],
                keywords=[],
                exclude_keywords=[],
                active_hours=["09:00-12:00", "14:00-18:00"],
                daily_limit=50,
                metadata={"source": "system_default"},
            )
        )

    @staticmethod
    def _dto_to_dict(value: Any) -> dict[str, object]:
        """将 DTO 或映射对象转为字典。"""

        if isinstance(value, Mapping):
            return dict(value)
        return cast(dict[str, object], asdict(value))

    @staticmethod
    def _to_iso(value: datetime | None) -> str | None:
        """转换为 ISO 时间字符串。"""

        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()

    @staticmethod
    def _coerce_datetime(value: object) -> datetime:
        """将输入转换为带时区时间。"""

        if isinstance(value, datetime):
            result = value
        elif isinstance(value, str) and value.strip():
            normalized = value.strip().replace("Z", "+00:00")
            result = datetime.fromisoformat(normalized)
        else:
            raise ValueError("时间参数无效")
        if result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)
        return result.astimezone(timezone.utc)

    @staticmethod
    def _to_dict(value: object) -> dict[str, object]:
        """将输入安全转换为字典。"""

        if isinstance(value, Mapping):
            return {str(key): cast(object, item) for key, item in value.items()}
        return {}

    @staticmethod
    def _to_str_list(value: object) -> list[str]:
        """将输入安全转换为字符串列表。"""

        if isinstance(value, (list, tuple, set)):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [item.strip() for item in value.split(",") if item.strip()]
        return []

    @staticmethod
    def _optional_str(value: object) -> str | None:
        """将输入安全转换为可选字符串。"""

        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @staticmethod
    def _to_int(value: object, default: int = 0) -> int:
        """将输入安全转换为整数。"""

        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return default
            try:
                return int(float(normalized))
            except ValueError:
                return default
        return default
