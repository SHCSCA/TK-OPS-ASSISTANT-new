from __future__ import annotations

# pyright: basic, reportMissingImports=false

"""分析领域仓储实现。"""

from collections.abc import Callable
from datetime import datetime
from typing import Any, cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models.analytics import AnalyticsSnapshot, CompetitorProfile, Report

from .base import BaseRepository


class AnalyticsRepository(BaseRepository[CompetitorProfile]):
    """分析数据访问仓储。"""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        super().__init__(session_factory, CompetitorProfile)

    def list_competitors(self, session: Session, *, active_only: bool = True, limit: int = 100) -> list[CompetitorProfile]:
        """获取竞品监控列表。"""

        session_any = cast(Any, session)
        deleted_column = cast(Any, getattr(CompetitorProfile, "is_deleted"))
        status_column = cast(Any, getattr(CompetitorProfile, "status"))
        created_column = cast(Any, getattr(CompetitorProfile, "created_at"))
        statement = cast(Any, select(CompetitorProfile)).where(deleted_column.is_(False))
        if active_only:
            statement = statement.where(status_column == "active")
        statement = statement.order_by(created_column.desc()).limit(max(limit, 0))
        return list(session_any.scalars(statement).all())

    def get_competitor_by_competitor_id(self, session: Session, competitor_id: str) -> CompetitorProfile | None:
        """按业务竞品编号查询竞品。"""

        session_any = cast(Any, session)
        competitor_id_column = cast(Any, getattr(CompetitorProfile, "competitor_id"))
        deleted_column = cast(Any, getattr(CompetitorProfile, "is_deleted"))
        statement = cast(Any, select(CompetitorProfile)).where(
            competitor_id_column == competitor_id,
            deleted_column.is_(False),
        )
        return session_any.scalars(statement).first()

    def create_competitor(self, session: Session, **kwargs: Any) -> CompetitorProfile:
        """创建竞品记录。"""

        session_any = cast(Any, session)
        competitor = CompetitorProfile(**kwargs)
        session_any.add(competitor)
        session_any.flush()
        session_any.refresh(competitor)
        return competitor

    def count_competitors(self, session: Session) -> int:
        """统计竞品数量。"""

        session_any = cast(Any, session)
        deleted_column = cast(Any, getattr(CompetitorProfile, "is_deleted"))
        statement = cast(Any, select(func.count())).select_from(CompetitorProfile).where(deleted_column.is_(False))
        return int(session_any.scalar(statement) or 0)

    def list_snapshots(
        self,
        session: Session,
        *,
        snapshot_type: str | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        limit: int = 500,
    ) -> list[AnalyticsSnapshot]:
        """查询分析快照列表。"""

        session_any = cast(Any, session)
        snapshot_type_column = cast(Any, getattr(AnalyticsSnapshot, "snapshot_type"))
        entity_type_column = cast(Any, getattr(AnalyticsSnapshot, "entity_type"))
        entity_id_column = cast(Any, getattr(AnalyticsSnapshot, "entity_id"))
        snapshot_date_column = cast(Any, getattr(AnalyticsSnapshot, "snapshot_date"))
        statement = cast(Any, select(AnalyticsSnapshot))
        if snapshot_type is not None:
            statement = statement.where(snapshot_type_column == snapshot_type)
        if entity_type is not None:
            statement = statement.where(entity_type_column == entity_type)
        if entity_id is not None:
            statement = statement.where(entity_id_column == entity_id)
        if start_at is not None:
            statement = statement.where(snapshot_date_column >= start_at)
        if end_at is not None:
            statement = statement.where(snapshot_date_column <= end_at)
        statement = statement.order_by(snapshot_date_column.desc()).limit(max(limit, 0))
        return list(session_any.scalars(statement).all())

    def count_snapshots(self, session: Session, snapshot_type: str | None = None) -> int:
        """统计分析快照数量。"""

        session_any = cast(Any, session)
        snapshot_type_column = cast(Any, getattr(AnalyticsSnapshot, "snapshot_type"))
        statement = cast(Any, select(func.count())).select_from(AnalyticsSnapshot)
        if snapshot_type is not None:
            statement = statement.where(snapshot_type_column == snapshot_type)
        return int(session_any.scalar(statement) or 0)

    def create_report(self, session: Session, **kwargs: Any) -> Report:
        """创建分析报告记录。"""

        session_any = cast(Any, session)
        report = Report(**kwargs)
        session_any.add(report)
        session_any.flush()
        session_any.refresh(report)
        return report

    def get_report_by_report_id(self, session: Session, report_id: str) -> Report | None:
        """按业务报告编号查询报告。"""

        session_any = cast(Any, session)
        report_id_column = cast(Any, getattr(Report, "report_id"))
        deleted_column = cast(Any, getattr(Report, "is_deleted"))
        statement = cast(Any, select(Report)).where(report_id_column == report_id, deleted_column.is_(False))
        return session_any.scalars(statement).first()

    def update_report(self, session: Session, report_id: str, **kwargs: Any) -> Report | None:
        """更新报告导出信息或状态。"""

        session_any = cast(Any, session)
        report = self.get_report_by_report_id(session, report_id)
        if report is None:
            return None
        for key, value in kwargs.items():
            setattr(report, key, value)
        session_any.add(report)
        session_any.flush()
        session_any.refresh(report)
        return report

    def count_reports(self, session: Session) -> int:
        """统计分析报告数量。"""

        session_any = cast(Any, session)
        deleted_column = cast(Any, getattr(Report, "is_deleted"))
        statement = cast(Any, select(func.count())).select_from(Report).where(deleted_column.is_(False))
        return int(session_any.scalar(statement) or 0)
