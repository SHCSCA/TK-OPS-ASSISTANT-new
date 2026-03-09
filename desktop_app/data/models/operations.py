from __future__ import annotations

# pyright: basic

"""运营领域持久化模型。"""

from typing import Any, cast

from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base, SoftDeleteMixin, TimestampMixin

_relationship = cast(Any, relationship)


class Order(Base, TimestampMixin, SoftDeleteMixin):
    """存储订单与售后状态。"""

    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("order_id", name="uq_orders_order_id"),
        CheckConstraint(
            "status IN ('pending', 'paid', 'processing', 'shipped', 'completed', 'cancelled', 'refunded')",
            name="order_status_valid",
        ),
        Index("ix_orders_status_deleted", "status", "is_deleted"),
        Index("ix_orders_refund_status", "refund_status"),
        Index("ix_orders_account_status", "account_id", "status"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(64), nullable=False, index=True)
    account_id = Column(ForeignKey("tiktok_accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    customer_name = Column(String(160), nullable=False)
    status = Column(String(32), default="pending", nullable=False, index=True)
    payment_status = Column(String(32), default="unpaid", nullable=False)
    fulfillment_status = Column(String(32), default="pending", nullable=False)
    refund_status = Column(String(32), default="none", nullable=False, index=True)
    total_amount = Column(Float, default=0.0, nullable=False)
    currency = Column(String(16), default="USD", nullable=False)
    items_count = Column(Integer, default=0, nullable=False)
    shipping_address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)

    account = _relationship("TikTokAccount", back_populates="orders")

    def __repr__(self) -> str:
        return f"Order(id={self.id!r}, order_id={self.order_id!r}, status={self.status!r}, refund_status={self.refund_status!r})"


class CustomerInquiry(Base, TimestampMixin, SoftDeleteMixin):
    """存储客服咨询主记录。"""

    __tablename__ = "customer_inquiries"
    __table_args__ = (
        UniqueConstraint("inquiry_id", name="uq_customer_inquiries_inquiry_id"),
        CheckConstraint("status IN ('pending', 'open', 'replied', 'closed')", name="inquiry_status_valid"),
        Index("ix_customer_inquiries_status_priority", "status", "priority"),
        Index("ix_customer_inquiries_account_status", "account_id", "status"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    inquiry_id = Column(String(64), nullable=False, index=True)
    account_id = Column(ForeignKey("tiktok_accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    customer_name = Column(String(160), nullable=False)
    channel = Column(String(64), default="tiktok_chat", nullable=False)
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String(32), default="pending", nullable=False, index=True)
    priority = Column(String(32), default="normal", nullable=False, index=True)
    assigned_to = Column(String(160), nullable=True)
    last_replied_at = Column(DateTime(timezone=True), nullable=True)
    sentiment_score = Column(Float, default=0.0, nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=False)

    account = _relationship("TikTokAccount", back_populates="inquiries")
    replies = _relationship(
        "InquiryReply",
        back_populates="inquiry",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="InquiryReply.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"CustomerInquiry(id={self.id!r}, inquiry_id={self.inquiry_id!r}, status={self.status!r}, priority={self.priority!r})"


class InquiryReply(Base, TimestampMixin):
    """存储客服回复记录。"""

    __tablename__ = "inquiry_replies"
    __table_args__ = (Index("ix_inquiry_replies_inquiry_created", "inquiry_id", "created_at"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    inquiry_id = Column(ForeignKey("customer_inquiries.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    replied_by = Column(String(160), default="operations_service", nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=False)

    inquiry = _relationship("CustomerInquiry", back_populates="replies")

    def __repr__(self) -> str:
        return f"InquiryReply(id={self.id!r}, inquiry_id={self.inquiry_id!r}, replied_by={self.replied_by!r})"
