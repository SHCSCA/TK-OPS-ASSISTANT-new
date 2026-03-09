from __future__ import annotations

# pyright: basic

"""Persistent AI provider, model, and agent role records."""

from typing import Any, cast

from sqlalchemy import Boolean, Column, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin

_relationship = cast(Any, relationship)


class AIProvider(Base, TimestampMixin):
    """AI service provider (OpenAI, Anthropic, Ollama, custom)."""

    __tablename__ = "ai_providers"
    __table_args__ = (
        UniqueConstraint("name", name="uq_ai_providers_name"),
        Index("ix_ai_providers_type_enabled", "provider_type", "is_enabled"),
        Index("ix_ai_providers_sort_order", "sort_order"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    provider_type = Column(String(64), nullable=False, index=True)
    base_url = Column(String(512), nullable=True)
    is_enabled = Column(Boolean, default=True, nullable=False, index=True)
    config_json = Column(JSON, default=dict, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)

    models = _relationship(
        "AIModel",
        back_populates="provider",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="AIModel.display_name",
    )
    agent_roles = _relationship("AgentRole", back_populates="provider", passive_deletes=True)

    def __repr__(self) -> str:
        return f"AIProvider(id={self.id!r}, name={self.name!r}, provider_type={self.provider_type!r})"


class AIModel(Base, TimestampMixin):
    """Specific model within a provider."""

    __tablename__ = "ai_models"
    __table_args__ = (
        UniqueConstraint("provider_id", "model_id", name="uq_ai_models_provider_model_id"),
        Index("ix_ai_models_provider_enabled", "provider_id", "is_enabled"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(ForeignKey("ai_providers.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(String(160), nullable=False)
    display_name = Column(String(160), nullable=False, index=True)
    capabilities_json = Column(JSON, default=list, nullable=False)
    max_tokens = Column(Integer, nullable=True)
    is_enabled = Column(Boolean, default=True, nullable=False, index=True)

    provider = _relationship("AIProvider", back_populates="models")
    agent_roles = _relationship("AgentRole", back_populates="model", passive_deletes=True)

    def __repr__(self) -> str:
        return f"AIModel(id={self.id!r}, provider_id={self.provider_id!r}, model_id={self.model_id!r})"


class AgentRole(Base, TimestampMixin):
    """Agent role preset with prompt, model, and parameters."""

    __tablename__ = "agent_roles"
    __table_args__ = (
        UniqueConstraint("name", name="uq_agent_roles_name"),
        Index("ix_agent_roles_system_sort", "is_system_role", "sort_order"),
        Index("ix_agent_roles_provider_model", "provider_id", "model_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=False)
    provider_id = Column(ForeignKey("ai_providers.id", ondelete="SET NULL"), nullable=True)
    model_id = Column(ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    temperature = Column(Float, default=0.7, nullable=False)
    max_tokens = Column(Integer, nullable=True)
    tools_json = Column(JSON, default=list, nullable=False)
    is_system_role = Column(Boolean, default=False, nullable=False, index=True)
    sort_order = Column(Integer, default=0, nullable=False)

    provider = _relationship("AIProvider", back_populates="agent_roles")
    model = _relationship("AIModel", back_populates="agent_roles")

    def __repr__(self) -> str:
        return f"AgentRole(id={self.id!r}, name={self.name!r}, provider_id={self.provider_id!r}, model_id={self.model_id!r})"
