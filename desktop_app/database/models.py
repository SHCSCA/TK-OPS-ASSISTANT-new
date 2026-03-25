"""SQLAlchemy ORM models for TK-OPS."""
from __future__ import annotations

import datetime as _dt

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ── Account ──────────────────────────────────────────────

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(40), default="tiktok")
    region: Mapped[str] = mapped_column(String(10), default="US")
    status: Mapped[str] = mapped_column(
        Enum("active", "suspended", "warming", "idle", name="account_status"),
        default="active",
    )
    followers: Mapped[int] = mapped_column(Integer, default=0)
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("devices.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    group: Mapped[Group | None] = relationship("Group", back_populates="accounts")
    device: Mapped[Device | None] = relationship("Device", back_populates="accounts")


# ── Group ────────────────────────────────────────────────

class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(20), default="#6366f1")
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())

    accounts: Mapped[list[Account]] = relationship("Account", back_populates="group")


# ── Device ───────────────────────────────────────────────

class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    proxy_ip: Mapped[str | None] = mapped_column(String(80), nullable=True)
    fingerprint_status: Mapped[str] = mapped_column(
        Enum("normal", "drifted", "missing", name="fp_status"), default="normal"
    )
    proxy_status: Mapped[str] = mapped_column(
        Enum("online", "lost", "offline", name="proxy_status"), default="online"
    )
    status: Mapped[str] = mapped_column(
        Enum("healthy", "warning", "error", "idle", name="device_status"),
        default="healthy",
    )
    region: Mapped[str] = mapped_column(String(10), default="US")
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    accounts: Mapped[list[Account]] = relationship("Account", back_populates="device")


# ── Task ─────────────────────────────────────────────────

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    task_type: Mapped[str] = mapped_column(
        Enum(
            "publish",
            "interact",
            "scrape",
            "report",
            "maintenance",
            "onboarding_finalize",
            "onboarding_followup",
            "permission_role",
            "analytics_action",
            name="task_type",
        ),
        default="publish",
    )
    priority: Mapped[str] = mapped_column(
        Enum("urgent", "high", "medium", "low", name="task_priority"), default="medium"
    )
    status: Mapped[str] = mapped_column(
        Enum("pending", "running", "paused", "completed", "failed", name="task_status"),
        default="pending",
    )
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    scheduled_at: Mapped[_dt.datetime | None] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[_dt.datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[_dt.datetime | None] = mapped_column(DateTime, nullable=True)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())

    account: Mapped[Account | None] = relationship("Account")


# ── AI Provider ──────────────────────────────────────────

class AIProvider(Base):
    __tablename__ = "ai_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    provider_type: Mapped[str] = mapped_column(
        Enum("openai", "anthropic", "local", "custom", name="provider_type"),
        default="openai",
    )
    api_base: Mapped[str] = mapped_column(String(255), default="https://api.openai.com/v1")
    api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_model: Mapped[str] = mapped_column(String(80), default="gpt-4o-mini")
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2048)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())


# ── Asset ────────────────────────────────────────────────

class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(
        Enum("image", "video", "audio", "text", "template", name="asset_type"),
        default="image",
    )
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())

    account: Mapped[Account | None] = relationship("Account")


# ── Analysis Snapshot ─────────────────────────────────────

class AnalysisSnapshot(Base):
    __tablename__ = "analysis_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    page_key: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    filters_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


# ── Report Run ────────────────────────────────────────────

class ReportRun(Base):
    __tablename__ = "report_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    report_type: Mapped[str] = mapped_column(String(80), default="general")
    status: Mapped[str] = mapped_column(String(40), default="pending")
    filters_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    task: Mapped[Task | None] = relationship("Task")


# ── Workflow Definition / Run ─────────────────────────────

class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    config_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    runs: Mapped[list[WorkflowRun]] = relationship(
        "WorkflowRun", back_populates="workflow_definition"
    )


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_definition_id: Mapped[int] = mapped_column(
        ForeignKey("workflow_definitions.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(40), default="pending")
    input_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[_dt.datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[_dt.datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())

    workflow_definition: Mapped[WorkflowDefinition] = relationship(
        "WorkflowDefinition", back_populates="runs"
    )


# ── Experiment Project / View ─────────────────────────────

class ExperimentProject(Base):
    __tablename__ = "experiment_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft")
    config_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    views: Mapped[list[ExperimentView]] = relationship(
        "ExperimentView", back_populates="project"
    )


class ExperimentView(Base):
    __tablename__ = "experiment_views"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_project_id: Mapped[int] = mapped_column(
        ForeignKey("experiment_projects.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    layout_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    project: Mapped[ExperimentProject] = relationship(
        "ExperimentProject", back_populates="views"
    )


# ── Activity Log ──────────────────────────────────────────

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_entity_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    related_entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime, server_default=func.now())


# ── App Setting (key-value config) ───────────────

class AppSetting(Base):
    """Flat key-value store for app configuration.

    Examples: theme=dark, window_width=1600, license_key=xxx,
              last_version=1.0.0, update_channel=stable
    """
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[_dt.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
