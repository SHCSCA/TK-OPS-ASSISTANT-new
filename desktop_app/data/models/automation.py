from __future__ import annotations

# pyright: basic

"""自动化领域持久化模型。"""

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, JSON, String, Text

from .base import Base, TimestampMixin


class AutoReplyRule(Base, TimestampMixin):
    """自动回复规则定义。"""

    __tablename__ = "auto_reply_rules"
    __table_args__ = (
        Index("ix_auto_reply_rules_active_priority", "is_active", "priority"),
        Index("ix_auto_reply_rules_trigger", "trigger_type", "is_active"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(255), nullable=False, index=True)
    trigger_type = Column(String(64), nullable=False, index=True)
    trigger_value = Column(Text, nullable=False)
    match_mode = Column(String(32), default="contains", nullable=False)
    reply_text = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    priority = Column(Integer, default=100, nullable=False, index=True)
    channels_json = Column(JSON, default=list, nullable=False)
    conditions_json = Column(JSON, default=dict, nullable=False)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    trigger_count = Column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"AutoReplyRule(id={self.id!r}, rule_name={self.rule_name!r}, is_active={self.is_active!r})"


class AutomationTask(Base, TimestampMixin):
    """自动互动任务与配置状态。"""

    __tablename__ = "automation_tasks"
    __table_args__ = (
        Index("ix_automation_tasks_category_status", "task_category", "status"),
        Index("ix_automation_tasks_enabled_status", "is_enabled", "status"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(64), nullable=False, unique=True, index=True)
    task_category = Column(String(64), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    status = Column(String(32), default="idle", nullable=False, index=True)
    is_enabled = Column(Boolean, default=True, nullable=False, index=True)
    config_json = Column(JSON, default=dict, nullable=False)
    runtime_json = Column(JSON, default=dict, nullable=False)
    last_started_at = Column(DateTime(timezone=True), nullable=True)
    last_stopped_at = Column(DateTime(timezone=True), nullable=True)
    last_healthcheck_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"AutomationTask(id={self.id!r}, task_type={self.task_type!r}, status={self.status!r})"


class CollectionTask(Base, TimestampMixin):
    """数据采集任务记录。"""

    __tablename__ = "collection_tasks"
    __table_args__ = (
        Index("ix_collection_tasks_status_source", "status", "source_type"),
        Index("ix_collection_tasks_started_at", "started_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(255), nullable=False)
    source_type = Column(String(64), nullable=False, index=True)
    status = Column(String(32), default="pending", nullable=False, index=True)
    keywords_json = Column(JSON, default=list, nullable=False)
    config_json = Column(JSON, default=dict, nullable=False)
    result_json = Column(JSON, default=dict, nullable=False)
    items_collected = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    stopped_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"CollectionTask(id={self.id!r}, task_name={self.task_name!r}, status={self.status!r})"
