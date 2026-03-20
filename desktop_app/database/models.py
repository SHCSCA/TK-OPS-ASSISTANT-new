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
        Enum("publish", "interact", "scrape", "report", "maintenance", name="task_type"),
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
