"""Generic CRUD repository for TK-OPS models."""
from __future__ import annotations

from typing import Any, Sequence, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from desktop_app.database import get_session
from desktop_app.database.models import (
    Account,
    AIProvider,
    AppSetting,
    Asset,
    Base,
    Device,
    Group,
    Task,
)

T = TypeVar("T", bound=Base)


class Repository:
    """Thin wrapper around SQLAlchemy Session providing common CRUD ops."""

    def __init__(self, session: Session | None = None) -> None:
        self._session = session or get_session()

    @property
    def session(self) -> Session:
        return self._session

    # ── generic CRUD ──

    def get_by_id(self, model: Type[T], pk: Any) -> T | None:
        return self._session.get(model, pk)

    def list_all(self, model: Type[T], *, limit: int = 500) -> Sequence[T]:
        return self._session.execute(select(model).limit(limit)).scalars().all()

    def count(self, model: Type[T]) -> int:
        return self._session.execute(select(func.count()).select_from(model)).scalar() or 0

    def add(self, instance: T) -> T:
        self._session.add(instance)
        self._session.commit()
        self._session.refresh(instance)
        return instance

    def update(self, instance: T, **fields: Any) -> T:
        for k, v in fields.items():
            setattr(instance, k, v)
        self._session.commit()
        self._session.refresh(instance)
        return instance

    def delete(self, instance: T) -> None:
        self._session.delete(instance)
        self._session.commit()

    # ── specialized queries ──

    def list_accounts(self, *, status: str | None = None) -> Sequence[Account]:
        stmt = select(Account)
        if status:
            stmt = stmt.where(Account.status == status)
        return self._session.execute(stmt.order_by(Account.id)).scalars().all()

    def list_devices(self, *, status: str | None = None) -> Sequence[Device]:
        stmt = select(Device)
        if status:
            stmt = stmt.where(Device.status == status)
        return self._session.execute(stmt.order_by(Device.id)).scalars().all()

    def list_tasks(self, *, status: str | None = None) -> Sequence[Task]:
        stmt = select(Task)
        if status:
            stmt = stmt.where(Task.status == status)
        return self._session.execute(stmt.order_by(Task.created_at.desc())).scalars().all()

    def get_active_provider(self) -> AIProvider | None:
        stmt = select(AIProvider).where(AIProvider.is_active == True).limit(1)  # noqa: E712
        return self._session.execute(stmt).scalars().first()

    def list_assets(self, *, asset_type: str | None = None) -> Sequence[Asset]:
        stmt = select(Asset)
        if asset_type:
            stmt = stmt.where(Asset.asset_type == asset_type)
        return self._session.execute(stmt.order_by(Asset.created_at.desc())).scalars().all()

    def list_groups(self) -> Sequence[Group]:
        return self._session.execute(select(Group).order_by(Group.id)).scalars().all()

    # ── app settings ──

    def get_setting(self, key: str, default: str = "") -> str:
        row = self._session.get(AppSetting, key)
        return row.value if row else default

    def set_setting(self, key: str, value: str) -> None:
        row = self._session.get(AppSetting, key)
        if row:
            row.value = value
        else:
            self._session.add(AppSetting(key=key, value=value))
        self._session.commit()

    def get_all_settings(self) -> dict[str, str]:
        rows = self._session.execute(select(AppSetting)).scalars().all()
        return {r.key: r.value for r in rows}

    # ── aggregate queries (for dashboard) ──

    def count_accounts_by_status(self) -> dict[str, int]:
        rows = self._session.execute(
            select(Account.status, func.count()).group_by(Account.status)
        ).all()
        return {status: cnt for status, cnt in rows}

    def count_tasks_by_status(self) -> dict[str, int]:
        rows = self._session.execute(
            select(Task.status, func.count()).group_by(Task.status)
        ).all()
        return {status: cnt for status, cnt in rows}

    def count_devices_by_status(self) -> dict[str, int]:
        rows = self._session.execute(
            select(Device.status, func.count()).group_by(Device.status)
        ).all()
        return {status: cnt for status, cnt in rows}

    def close(self) -> None:
        self._session.close()
