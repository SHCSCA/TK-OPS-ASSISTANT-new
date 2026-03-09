from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportCallIssue=false

"""自动化领域仓储实现。"""

from datetime import datetime
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.automation import AutoReplyRule, AutomationTask, CollectionTask
from ..models.log import LogEntry
from ..models.schedule import PublishSchedule


class AutomationRepository:
    """自动化领域数据访问适配器。"""

    def count_auto_reply_rules(self, session: Session) -> int:
        """统计自动回复规则数量。"""

        session_any = cast(Any, session)
        statement = cast(Any, select(AutoReplyRule))
        return len(list(session_any.scalars(statement).all()))

    def count_collection_tasks(self, session: Session) -> int:
        """统计采集任务数量。"""

        session_any = cast(Any, session)
        statement = cast(Any, select(CollectionTask))
        return len(list(session_any.scalars(statement).all()))

    def list_automation_tasks(self, session: Session, category: str | None = None) -> list[AutomationTask]:
        """列出自动化任务。"""

        session_any = cast(Any, session)
        task_updated_at = cast(Any, getattr(AutomationTask, "updated_at"))
        statement = cast(Any, select(AutomationTask))
        if category is not None:
            task_category = cast(Any, getattr(AutomationTask, "task_category"))
            statement = statement.where(task_category == category)
        statement = statement.order_by(task_updated_at.desc())
        return list(session_any.scalars(statement).all())

    def get_automation_task(self, session: Session, task_type: str) -> AutomationTask | None:
        """按任务类型获取自动化任务。"""

        session_any = cast(Any, session)
        task_type_column = cast(Any, getattr(AutomationTask, "task_type"))
        statement = cast(Any, select(AutomationTask)).where(task_type_column == task_type)
        return session_any.scalars(statement).first()

    def save_automation_task(self, session: Session, task: AutomationTask) -> AutomationTask:
        """保存自动化任务。"""

        session_any = cast(Any, session)
        session_any.add(task)
        session_any.flush()
        session_any.refresh(task)
        return task

    def list_auto_reply_rules(self, session: Session) -> list[AutoReplyRule]:
        """按优先级列出自动回复规则。"""

        session_any = cast(Any, session)
        rule_priority = cast(Any, getattr(AutoReplyRule, "priority"))
        rule_updated_at = cast(Any, getattr(AutoReplyRule, "updated_at"))
        statement = cast(Any, select(AutoReplyRule)).order_by(rule_priority.asc(), rule_updated_at.desc())
        return list(session_any.scalars(statement).all())

    def get_auto_reply_rule(self, session: Session, rule_id: int) -> AutoReplyRule | None:
        """获取指定自动回复规则。"""

        session_any = cast(Any, session)
        return cast(AutoReplyRule | None, session_any.get(AutoReplyRule, rule_id))

    def save_auto_reply_rule(self, session: Session, rule: AutoReplyRule) -> AutoReplyRule:
        """保存自动回复规则。"""

        session_any = cast(Any, session)
        session_any.add(rule)
        session_any.flush()
        session_any.refresh(rule)
        return rule

    def delete_auto_reply_rule(self, session: Session, rule: AutoReplyRule) -> None:
        """删除自动回复规则。"""

        session_any = cast(Any, session)
        session_any.delete(rule)

    def list_auto_reply_logs(
        self,
        session: Session,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> list[LogEntry]:
        """查询自动回复日志。"""

        session_any = cast(Any, session)
        log_module = cast(Any, getattr(LogEntry, "module"))
        log_timestamp = cast(Any, getattr(LogEntry, "timestamp"))
        statement = cast(Any, select(LogEntry)).where(log_module == "automation.auto_reply")
        if start_at is not None:
            statement = statement.where(log_timestamp >= start_at)
        if end_at is not None:
            statement = statement.where(log_timestamp <= end_at)
        statement = statement.order_by(log_timestamp.desc())
        return list(session_any.scalars(statement).all())

    def create_log(
        self,
        session: Session,
        module: str,
        message: str,
        details_json: dict[str, object] | None = None,
        level: str = "info",
    ) -> LogEntry:
        """写入结构化日志。"""

        entry = cast(Any, LogEntry)(level=level, module=module, message=message, details_json=details_json or {})
        session_any = cast(Any, session)
        session_any.add(entry)
        session_any.flush()
        session_any.refresh(entry)
        return entry

    def list_scheduled_posts(self, session: Session) -> list[PublishSchedule]:
        """列出已计划发布的内容。"""

        session_any = cast(Any, session)
        schedule_time = cast(Any, getattr(PublishSchedule, "scheduled_time"))
        statement = cast(Any, select(PublishSchedule)).order_by(schedule_time.asc())
        return list(session_any.scalars(statement).all())

    def get_scheduled_post(self, session: Session, post_id: int) -> PublishSchedule | None:
        """获取计划发布记录。"""

        session_any = cast(Any, session)
        return cast(PublishSchedule | None, session_any.get(PublishSchedule, post_id))

    def save_scheduled_post(self, session: Session, post: PublishSchedule) -> PublishSchedule:
        """保存计划发布记录。"""

        session_any = cast(Any, session)
        session_any.add(post)
        session_any.flush()
        session_any.refresh(post)
        return post

    def list_collection_tasks(self, session: Session) -> list[CollectionTask]:
        """列出采集任务。"""

        session_any = cast(Any, session)
        started_at = cast(Any, getattr(CollectionTask, "started_at"))
        updated_at = cast(Any, getattr(CollectionTask, "updated_at"))
        statement = cast(Any, select(CollectionTask)).order_by(started_at.desc(), updated_at.desc())
        return list(session_any.scalars(statement).all())

    def get_collection_task(self, session: Session, task_id: int) -> CollectionTask | None:
        """获取采集任务。"""

        session_any = cast(Any, session)
        return cast(CollectionTask | None, session_any.get(CollectionTask, task_id))

    def save_collection_task(self, session: Session, task: CollectionTask) -> CollectionTask:
        """保存采集任务。"""

        session_any = cast(Any, session)
        session_any.add(task)
        session_any.flush()
        session_any.refresh(task)
        return task
