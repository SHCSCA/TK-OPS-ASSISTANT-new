from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false

"""账号领域仓储实现。"""

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models.account import TikTokAccount

from .base import BaseRepository


class AccountRepository(BaseRepository[TikTokAccount]):
    """账号数据访问仓储。"""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        super().__init__(session_factory, TikTokAccount)

    def get_active_accounts(self, session: Session, skip: int = 0, limit: int = 100) -> list[TikTokAccount]:
        """获取未删除账号列表。"""

        session_any = cast(Any, session)
        deleted_column = cast(Any, getattr(TikTokAccount, "is_deleted"))
        status_column = cast(Any, getattr(TikTokAccount, "status"))
        created_column = cast(Any, getattr(TikTokAccount, "created_at"))
        statement = cast(Any, select(TikTokAccount))
        statement = statement.where(deleted_column.is_(False)).order_by(status_column, created_column.desc())
        statement = statement.offset(max(skip, 0)).limit(max(limit, 0))
        return list(session_any.scalars(statement).all())

    def get_by_account_id(self, session: Session, account_id: str, *, include_deleted: bool = False) -> TikTokAccount | None:
        """按业务账号 ID 查询。"""

        session_any = cast(Any, session)
        account_id_column = cast(Any, getattr(TikTokAccount, "account_id"))
        deleted_column = cast(Any, getattr(TikTokAccount, "is_deleted"))
        statement = cast(Any, select(TikTokAccount)).where(account_id_column == account_id)
        if not include_deleted:
            statement = statement.where(deleted_column.is_(False))
        return session_any.scalars(statement).first()

    def create_account(self, session: Session, **kwargs: Any) -> TikTokAccount:
        """创建账号记录。"""

        session_any = cast(Any, session)
        account = TikTokAccount(**kwargs)
        session_any.add(account)
        session_any.flush()
        session_any.refresh(account)
        return account

    def update_account(self, session: Session, account_id: str, **kwargs: Any) -> TikTokAccount | None:
        """更新账号记录。"""

        session_any = cast(Any, session)
        account = self.get_by_account_id(session, account_id, include_deleted=True)
        if account is None:
            return None
        for key, value in kwargs.items():
            setattr(account, key, value)
        session_any.add(account)
        session_any.flush()
        session_any.refresh(account)
        return account

    def soft_delete_account(self, session: Session, account_id: str) -> bool:
        """软删除账号。"""

        session_any = cast(Any, session)
        account = self.get_by_account_id(session, account_id)
        if account is None:
            return False
        account.is_deleted = True
        account.deleted_at = datetime.now(timezone.utc)
        account.status = "inactive"
        session_any.add(account)
        session_any.flush()
        return True

    def count_active(self, session: Session) -> int:
        """统计有效账号数。"""

        session_any = cast(Any, session)
        deleted_column = cast(Any, getattr(TikTokAccount, "is_deleted"))
        statement = cast(Any, select(func.count())).select_from(TikTokAccount).where(deleted_column.is_(False))
        return int(session_any.scalar(statement) or 0)
