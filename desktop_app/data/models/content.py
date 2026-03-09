from __future__ import annotations

# pyright: basic

"""内容域持久化模型，涵盖脚本与模板管理。"""

from typing import Any, cast

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base, SoftDeleteMixin, TimestampMixin

_relationship = cast(Any, relationship)


class Script(Base, TimestampMixin, SoftDeleteMixin):
    """存储视频脚本及其排期信息。"""

    __tablename__ = "scripts"
    __table_args__ = (
        Index("ix_scripts_status_scheduled", "status", "scheduled_at"),
        Index("ix_scripts_platform_deleted", "platform", "is_deleted"),
        Index("ix_scripts_asset_deleted", "asset_id", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    hook_text = Column(String(255), nullable=True)
    body = Column(Text, nullable=False)
    cta_text = Column(String(255), nullable=True)
    status = Column(String(32), default="draft", nullable=False, index=True)
    platform = Column(String(64), default="tiktok", nullable=False, index=True)
    tone = Column(String(64), nullable=True)
    tags_json = Column(JSON, default=list, nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    asset_id = Column(ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    template_id = Column(ForeignKey("content_templates.id", ondelete="SET NULL"), nullable=True)

    template = _relationship("ContentTemplate", back_populates="scripts")

    def __repr__(self) -> str:
        return f"Script(id={self.id!r}, title={self.title!r}, status={self.status!r}, platform={self.platform!r})"


class ContentTemplate(Base, TimestampMixin, SoftDeleteMixin):
    """存储内容模板及其默认参数。"""

    __tablename__ = "content_templates"
    __table_args__ = (
        UniqueConstraint("name", name="uq_content_templates_name"),
        Index("ix_content_templates_category_deleted", "category", "is_deleted"),
        Index("ix_content_templates_status_deleted", "status", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(160), nullable=False)
    category = Column(String(64), default="general", nullable=False, index=True)
    title_template = Column(String(255), nullable=False)
    body_template = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    parameter_schema_json = Column(JSON, default=list, nullable=False)
    default_params_json = Column(JSON, default=dict, nullable=False)
    status = Column(String(32), default="active", nullable=False, index=True)
    metadata_json = Column(JSON, default=dict, nullable=False)

    scripts = _relationship(
        "Script",
        back_populates="template",
        order_by="Script.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"ContentTemplate(id={self.id!r}, name={self.name!r}, category={self.category!r}, status={self.status!r})"
