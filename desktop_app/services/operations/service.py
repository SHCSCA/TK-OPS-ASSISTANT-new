from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false

"""运营领域服务实现。"""

from dataclasses import dataclass
from datetime import datetime, timezone

from ...data.database import Database
from ...data.models.operations import CustomerInquiry, InquiryReply, Order
from ...data.repositories.operations_repo import OperationsRepository


@dataclass
class OrderDTO:
    """订单 DTO。"""

    order_id: str
    account_id: int | None
    customer_name: str
    status: str
    payment_status: str
    fulfillment_status: str
    refund_status: str
    total_amount: float
    currency: str
    items_count: int
    notes: str | None


@dataclass
class InquiryReplyDTO:
    """客服回复 DTO。"""

    reply_id: int
    message: str
    replied_by: str
    created_at: str | None


@dataclass
class InquiryDTO:
    """客服咨询 DTO。"""

    inquiry_id: str
    account_id: int | None
    customer_name: str
    channel: str
    subject: str | None
    message: str
    status: str
    priority: str
    assigned_to: str | None
    last_replied_at: str | None
    replies: list[InquiryReplyDTO]



class OperationsService:
    """运营中心领域服务。"""

    service_name: str = "operations"

    def __init__(self, database: Database | None = None) -> None:
        """初始化运营服务。"""

        self._database: Database = database or Database()
        self._operations_repo: OperationsRepository = OperationsRepository(self._database.create_session)

    def initialize(self) -> None:
        """初始化服务，无需额外动作。"""

        return None

    def shutdown(self) -> None:
        """关闭服务，无需额外动作。"""

        return None

    def healthcheck(self) -> dict[str, object]:
        """返回运营服务健康状态。"""

        with self._database.session_scope() as session:
            order_count = self._operations_repo.count_orders(session)
            pending_refunds = self._operations_repo.count_pending_refunds(session)
            open_inquiries = self._operations_repo.count_open_inquiries(session)
        return {
            "service": self.service_name,
            "status": "ok",
            "orders": order_count,
            "pending_refunds": pending_refunds,
            "open_inquiries": open_inquiries,
            "database": "connected",
        }

    def list_orders(self, page: int = 1, page_size: int = 20) -> dict[str, object]:
        """分页返回订单列表。"""

        normalized_page = max(page, 1)
        normalized_page_size = max(page_size, 1)
        offset = (normalized_page - 1) * normalized_page_size
        with self._database.session_scope() as session:
            total = self._operations_repo.count_orders(session)
            orders = self._operations_repo.list_orders(session, skip=offset, limit=normalized_page_size)
        return {
            "items": [self._dto_to_dict(self._to_order_dto(order)) for order in orders],
            "pagination": {
                "page": normalized_page,
                "page_size": normalized_page_size,
                "total": total,
            },
        }

    def get_order_detail(self, order_id: str) -> dict[str, object]:
        """返回单个订单详情。"""

        with self._database.session_scope() as session:
            order = self._operations_repo.get_order_by_order_id(session, order_id)
            if order is None:
                raise LookupError(f"订单不存在: {order_id}")
        detail = self._dto_to_dict(self._to_order_dto(order))
        detail.update(
            {
                "shipping_address": order.shipping_address,
                "metadata": dict(order.metadata_json or {}),
                "created_at": self._to_iso(order.created_at),
                "updated_at": self._to_iso(order.updated_at),
                "refunded_at": self._to_iso(order.refunded_at),
            }
        )
        return detail

    def process_refund(self, order_id: str, reason: str) -> dict[str, object]:
        """处理订单退款流程。"""

        normalized_reason = reason.strip()
        if not normalized_reason:
            raise ValueError("退款原因不能为空")
        with self._database.session_scope() as session:
            order = self._operations_repo.get_order_by_order_id(session, order_id)
            if order is None:
                raise LookupError(f"订单不存在: {order_id}")
            metadata = dict(order.metadata_json or {})
            metadata["refund_reason"] = normalized_reason
            metadata["refund_processed_at"] = self._to_iso(datetime.now(timezone.utc))
            updated = self._operations_repo.update_order(
                session,
                order_id,
                status="refunded",
                refund_status="approved",
                refunded_at=datetime.now(timezone.utc),
                notes=normalized_reason,
                metadata_json=metadata,
            )
            if updated is None:
                raise LookupError(f"订单不存在: {order_id}")
        return {
            "order_id": updated.order_id,
            "status": updated.status,
            "refund_status": updated.refund_status,
            "reason": normalized_reason,
        }

    def list_customer_inquiries(self, page: int = 1, page_size: int = 20) -> dict[str, object]:
        """分页返回客服咨询队列。"""

        normalized_page = max(page, 1)
        normalized_page_size = max(page_size, 1)
        offset = (normalized_page - 1) * normalized_page_size
        with self._database.session_scope() as session:
            total = self._operations_repo.count_customer_inquiries(session)
            inquiries = self._operations_repo.list_customer_inquiries(session, skip=offset, limit=normalized_page_size)
        return {
            "items": [self._dto_to_dict(self._to_inquiry_dto(inquiry)) for inquiry in inquiries],
            "pagination": {
                "page": normalized_page,
                "page_size": normalized_page_size,
                "total": total,
            },
        }

    def reply_to_inquiry(self, inquiry_id: str, message: str) -> dict[str, object]:
        """回复指定客服咨询。"""

        normalized_message = message.strip()
        if not normalized_message:
            raise ValueError("回复内容不能为空")
        with self._database.session_scope() as session:
            inquiry, reply = self._operations_repo.add_inquiry_reply(session, inquiry_id, normalized_message)
            if inquiry is None or reply is None:
                raise LookupError(f"咨询不存在: {inquiry_id}")
        return {
            "inquiry_id": inquiry.inquiry_id,
            "status": inquiry.status,
            "reply": self._dto_to_dict(self._to_reply_dto(reply)),
        }


    def list_work_items(self) -> list[dict[str, object]]:
        """兼容旧接口，返回待处理咨询列表。"""

        payload = self.list_customer_inquiries(page=1, page_size=20)
        items = payload.get("items")
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
        return []

    def update_work_item_status(self, work_item_id: str, status: str) -> None:
        """兼容旧接口，直接更新咨询状态。"""

        with self._database.session_scope() as session:
            inquiry = self._operations_repo.get_inquiry_by_inquiry_id(session, work_item_id)
            if inquiry is None:
                raise LookupError(f"咨询不存在: {work_item_id}")
            inquiry.status = status
            session.add(inquiry)

    def _to_order_dto(self, order: Order) -> OrderDTO:
        """将订单模型转换为 DTO。"""

        return OrderDTO(
            order_id=order.order_id,
            account_id=order.account_id,
            customer_name=order.customer_name,
            status=order.status,
            payment_status=order.payment_status,
            fulfillment_status=order.fulfillment_status,
            refund_status=order.refund_status,
            total_amount=float(order.total_amount or 0.0),
            currency=order.currency,
            items_count=int(order.items_count or 0),
            notes=order.notes,
        )

    def _to_reply_dto(self, reply: InquiryReply) -> InquiryReplyDTO:
        """将回复模型转换为 DTO。"""

        return InquiryReplyDTO(
            reply_id=int(reply.id),
            message=reply.message,
            replied_by=reply.replied_by,
            created_at=self._to_iso(reply.created_at),
        )

    def _to_inquiry_dto(self, inquiry: CustomerInquiry) -> InquiryDTO:
        """将咨询模型转换为 DTO。"""

        replies = list(getattr(inquiry, "replies", []) or [])
        return InquiryDTO(
            inquiry_id=inquiry.inquiry_id,
            account_id=inquiry.account_id,
            customer_name=inquiry.customer_name,
            channel=inquiry.channel,
            subject=inquiry.subject,
            message=inquiry.message,
            status=inquiry.status,
            priority=inquiry.priority,
            assigned_to=inquiry.assigned_to,
            last_replied_at=self._to_iso(inquiry.last_replied_at),
            replies=[self._to_reply_dto(reply) for reply in replies],
        )


    @staticmethod
    def _to_iso(value: datetime | None) -> str | None:
        """转换时间为 ISO 字符串。"""

        if value is None:
            return None
        return value.isoformat()

    @staticmethod
    def _dto_to_dict(
        dto: OrderDTO | InquiryReplyDTO | InquiryDTO,
    ) -> dict[str, object]:
        """将 DTO 转换为字典。"""

        return {key: value for key, value in vars(dto).items()}


__all__ = ["InquiryDTO", "InquiryReplyDTO", "OperationsService", "OrderDTO"]
