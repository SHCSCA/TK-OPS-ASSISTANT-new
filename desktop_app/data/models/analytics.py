from __future__ import annotations

# pyright: basic

"""分析领域持久化模型。"""

from sqlalchemy import Column, DateTime, Float, Index, Integer, JSON, String, Text, UniqueConstraint, func

from .base import Base, SoftDeleteMixin, TimestampMixin


class CompetitorProfile(Base, TimestampMixin, SoftDeleteMixin):
    """存储竞品监控主档与核心基线指标。"""

    __tablename__ = "analytics_competitors"
    __table_args__ = (
        UniqueConstraint("competitor_id", name="uq_analytics_competitors_competitor_id"),
        Index("ix_analytics_competitors_category_status", "category", "status"),
        Index("ix_analytics_competitors_username", "platform_username"),
        Index("ix_analytics_competitors_shop_name", "shop_name"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    competitor_id = Column(String(64), nullable=False, index=True)
    shop_name = Column(String(160), nullable=False)
    display_name = Column(String(160), nullable=False)
    platform_username = Column(String(160), nullable=True, index=True)
    category = Column(String(64), default="general", nullable=False, index=True)
    region = Column(String(32), nullable=True, index=True)
    follower_count = Column(Integer, default=0, nullable=False)
    avg_views = Column(Integer, default=0, nullable=False)
    avg_likes = Column(Integer, default=0, nullable=False)
    avg_price = Column(Float, default=0.0, nullable=False)
    est_monthly_sales = Column(Float, default=0.0, nullable=False)
    engagement_rate = Column(Float, default=0.0, nullable=False)
    ctr = Column(Float, default=0.0, nullable=False)
    cvr = Column(Float, default=0.0, nullable=False)
    roas = Column(Float, default=0.0, nullable=False)
    status = Column(String(32), default="active", nullable=False, index=True)
    metadata_json = Column(JSON, default=dict, nullable=False)

    def __repr__(self) -> str:
        return (
            "CompetitorProfile("
            f"id={self.id!r}, competitor_id={self.competitor_id!r}, shop_name={self.shop_name!r}, category={self.category!r}"
            ")"
        )


class AnalyticsSnapshot(Base, TimestampMixin):
    """存储分析快照与可聚合指标数据。"""

    __tablename__ = "analytics_snapshots"
    __table_args__ = (
        Index("ix_analytics_snapshots_type_date", "snapshot_type", "snapshot_date"),
        Index("ix_analytics_snapshots_entity", "entity_type", "entity_id"),
        Index("ix_analytics_snapshots_source", "source"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_type = Column(String(64), nullable=False, index=True)
    entity_type = Column(String(64), nullable=True, index=True)
    entity_id = Column(String(64), nullable=True, index=True)
    snapshot_date = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False, index=True)
    source = Column(String(64), default="system", nullable=False)
    metrics_json = Column(JSON, default=dict, nullable=False)
    dimensions_json = Column(JSON, default=dict, nullable=False)
    notes = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return (
            "AnalyticsSnapshot("
            f"id={self.id!r}, snapshot_type={self.snapshot_type!r}, entity_type={self.entity_type!r}, entity_id={self.entity_id!r}"
            ")"
        )


class Report(Base, TimestampMixin, SoftDeleteMixin):
    """存储生成后的分析报告与导出元数据。"""

    __tablename__ = "analytics_reports"
    __table_args__ = (
        UniqueConstraint("report_id", name="uq_analytics_reports_report_id"),
        Index("ix_analytics_reports_type_status", "report_type", "status"),
        Index("ix_analytics_reports_generated_at", "generated_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(64), nullable=False, index=True)
    report_type = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    status = Column(String(32), default="generated", nullable=False, index=True)
    parameters_json = Column(JSON, default=dict, nullable=False)
    payload_json = Column(JSON, default=dict, nullable=False)
    export_format = Column(String(16), nullable=True)
    export_path = Column(String(1024), nullable=True)
    generated_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False, index=True)
    summary = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"Report(id={self.id!r}, report_id={self.report_id!r}, report_type={self.report_type!r}, status={self.status!r})"
