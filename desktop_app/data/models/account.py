from __future__ import annotations

# pyright: basic

"""账号领域持久化模型。"""

from typing import Any, cast

from sqlalchemy import Column, DateTime, Float, Index, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base, SoftDeleteMixin, TimestampMixin

_relationship = cast(Any, relationship)


class TikTokAccount(Base, TimestampMixin, SoftDeleteMixin):
    """存储 TikTok 店铺账号主数据。"""

    __tablename__ = "tiktok_accounts"
    __table_args__ = (
        UniqueConstraint("account_id", name="uq_tiktok_accounts_account_id"),
        Index("ix_tiktok_accounts_status_deleted", "status", "is_deleted"),
        Index("ix_tiktok_accounts_region_status", "region", "status"),
        Index("ix_tiktok_accounts_shop_name", "shop_name"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(64), nullable=False, index=True)
    shop_name = Column(String(160), nullable=False)
    display_name = Column(String(160), nullable=False)
    platform_username = Column(String(160), nullable=True, index=True)
    status = Column(String(32), default="active", nullable=False, index=True)
    region = Column(String(32), nullable=True, index=True)
    category = Column(String(64), nullable=True)
    follower_count = Column(Integer, default=0, nullable=False)
    product_count = Column(Integer, default=0, nullable=False)
    orders_count = Column(Integer, default=0, nullable=False)
    total_revenue = Column(Float, default=0.0, nullable=False)
    conversion_rate = Column(Float, default=0.0, nullable=False)
    health_score = Column(Float, default=100.0, nullable=False)
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)

    orders = _relationship("Order", back_populates="account", passive_deletes=True)
    inquiries = _relationship("CustomerInquiry", back_populates="account", passive_deletes=True)

    def __repr__(self) -> str:
        return (
            "TikTokAccount("
            f"id={self.id!r}, account_id={self.account_id!r}, shop_name={self.shop_name!r}, status={self.status!r}"
            ")"
        )
