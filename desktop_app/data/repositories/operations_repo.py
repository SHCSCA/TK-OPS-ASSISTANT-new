from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false

"""运营领域仓储实现。"""

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..models.operations import CustomerInquiry, InquiryReply, Order

from .base import BaseRepository


class OperationsRepository(BaseRepository[Order]):
    """订单与客服数据仓储。"""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        super().__init__(session_factory, Order)

    def list_orders(self, session: Session, *, skip: int = 0, limit: int = 20) -> list[Order]:
        """分页获取订单列表。"""

        session_any = cast(Any, session)
        deleted_column = cast(Any, getattr(Order, "is_deleted"))
        created_column = cast(Any, getattr(Order, "created_at"))
        statement = cast(Any, select(Order))
        statement = statement.where(deleted_column.is_(False)).order_by(created_column.desc())
        statement = statement.offset(max(skip, 0)).limit(max(limit, 0))
        return list(session_any.scalars(statement).all())

    def count_orders(self, session: Session) -> int:
        """统计有效订单数。"""

        session_any = cast(Any, session)
        deleted_column = cast(Any, getattr(Order, "is_deleted"))
        statement = cast(Any, select(func.count())).select_from(Order).where(deleted_column.is_(False))
        return int(session_any.scalar(statement) or 0)

    def get_order_by_order_id(self, session: Session, order_id: str) -> Order | None:
        """按业务订单号查询订单。"""

        session_any = cast(Any, session)
        order_id_column = cast(Any, getattr(Order, "order_id"))
        deleted_column = cast(Any, getattr(Order, "is_deleted"))
        statement = cast(Any, select(Order)).where(order_id_column == order_id, deleted_column.is_(False))
        return session_any.scalars(statement).first()

    def update_order(self, session: Session, order_id: str, **kwargs: Any) -> Order | None:
        """更新订单状态。"""

        session_any = cast(Any, session)
        order = self.get_order_by_order_id(session, order_id)
        if order is None:
            return None
        for key, value in kwargs.items():
            setattr(order, key, value)
        session_any.add(order)
        session_any.flush()
        session_any.refresh(order)
        return order

    def list_customer_inquiries(self, session: Session, *, skip: int = 0, limit: int = 20) -> list[CustomerInquiry]:
        """分页获取客服咨询队列。"""

        session_any = cast(Any, session)
        deleted_column = cast(Any, getattr(CustomerInquiry, "is_deleted"))
        priority_column = cast(Any, getattr(CustomerInquiry, "priority"))
        created_column = cast(Any, getattr(CustomerInquiry, "created_at"))
        statement = cast(Any, select(CustomerInquiry))
        statement = statement.where(deleted_column.is_(False)).order_by(priority_column.desc(), created_column.desc())
        statement = statement.offset(max(skip, 0)).limit(max(limit, 0))
        return list(session_any.scalars(statement).all())

    def count_customer_inquiries(self, session: Session) -> int:
        """统计客服队列总量。"""

        session_any = cast(Any, session)
        deleted_column = cast(Any, getattr(CustomerInquiry, "is_deleted"))
        statement = cast(Any, select(func.count())).select_from(CustomerInquiry).where(deleted_column.is_(False))
        return int(session_any.scalar(statement) or 0)

    def get_inquiry_by_inquiry_id(self, session: Session, inquiry_id: str) -> CustomerInquiry | None:
        """按业务咨询号查询咨询。"""

        session_any = cast(Any, session)
        inquiry_id_column = cast(Any, getattr(CustomerInquiry, "inquiry_id"))
        deleted_column = cast(Any, getattr(CustomerInquiry, "is_deleted"))
        replies_rel = cast(Any, getattr(CustomerInquiry, "replies"))
        statement = cast(Any, select(CustomerInquiry))
        statement = statement.options(selectinload(replies_rel)).where(inquiry_id_column == inquiry_id, deleted_column.is_(False))
        return session_any.scalars(statement).first()

    def add_inquiry_reply(
        self,
        session: Session,
        inquiry_id: str,
        message: str,
        *,
        replied_by: str = "operations_service",
    ) -> tuple[CustomerInquiry | None, InquiryReply | None]:
        """新增客服回复并更新咨询状态。"""

        session_any = cast(Any, session)
        inquiry = self.get_inquiry_by_inquiry_id(session, inquiry_id)
        if inquiry is None:
            return None, None
        reply = InquiryReply()
        reply.inquiry_id = inquiry.id
        reply.message = message
        reply.replied_by = replied_by
        reply.metadata_json = {"channel": inquiry.channel}
        inquiry.status = "replied"
        inquiry.last_replied_at = datetime.now(timezone.utc)
        session_any.add(reply)
        session_any.add(inquiry)
        session_any.flush()
        session_any.refresh(reply)
        session_any.refresh(inquiry)
        return inquiry, reply


    def get_account_order_metrics(self, session: Session, account_pk: int) -> dict[str, float | int]:
        """按账号聚合订单指标。"""

        session_any = cast(Any, session)
        account_id_column = cast(Any, getattr(Order, "account_id"))
        deleted_column = cast(Any, getattr(Order, "is_deleted"))
        amount_column = cast(Any, getattr(Order, "total_amount"))
        order_statement = cast(Any, select(func.count(Order.id), func.coalesce(func.sum(amount_column), 0.0)))
        order_statement = order_statement.where(account_id_column == account_pk, deleted_column.is_(False))
        order_result = session_any.execute(order_statement).one()
        refund_statement = cast(Any, select(func.count(Order.id))).where(
            account_id_column == account_pk,
            cast(Any, getattr(Order, "refund_status")) == "approved",
            deleted_column.is_(False),
        )
        refund_count = int(session_any.scalar(refund_statement) or 0)
        return {
            "order_count": int(order_result[0] or 0),
            "revenue": float(order_result[1] or 0.0),
            "refund_count": refund_count,
        }

    def count_pending_refunds(self, session: Session) -> int:
        """统计待处理退款单数。"""

        session_any = cast(Any, session)
        refund_column = cast(Any, getattr(Order, "refund_status"))
        deleted_column = cast(Any, getattr(Order, "is_deleted"))
        statement = cast(Any, select(func.count())).select_from(Order)
        statement = statement.where(refund_column == "requested", deleted_column.is_(False))
        return int(session_any.scalar(statement) or 0)

    def count_open_inquiries(self, session: Session) -> int:
        """统计未关闭咨询数。"""

        session_any = cast(Any, session)
        status_column = cast(Any, getattr(CustomerInquiry, "status"))
        deleted_column = cast(Any, getattr(CustomerInquiry, "is_deleted"))
        statement = cast(Any, select(func.count())).select_from(CustomerInquiry)
        statement = statement.where(status_column.in_(["pending", "open"]), deleted_column.is_(False))
        return int(session_any.scalar(statement) or 0)
