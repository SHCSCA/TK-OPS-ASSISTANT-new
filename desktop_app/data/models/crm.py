from __future__ import annotations

# pyright: basic

"""CRM persistence records for customer management workflows."""

from typing import Any, cast

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base, SoftDeleteMixin, TimestampMixin

_relationship = cast(Any, relationship)


class Customer(Base, TimestampMixin, SoftDeleteMixin):
    """Stores customer profile metadata."""

    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("platform_type", "platform_id", name="uq_customers_platform_identity"),
        Index("ix_customers_status_deleted", "status", "is_deleted"),
        Index("ix_customers_name", "name"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(160), nullable=False)
    platform_id = Column(String(160), nullable=True)
    platform_type = Column(String(64), nullable=True, index=True)
    tags_json = Column(JSON, default=list, nullable=False)
    notes = Column(Text, nullable=True)
    last_contact_at = Column(DateTime(timezone=True), nullable=True)
    lifetime_value = Column(Float, default=0.0, nullable=False)
    status = Column(String(32), default="active", nullable=False, index=True)

    interactions = _relationship(
        "CustomerInteraction",
        back_populates="customer",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="CustomerInteraction.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"Customer(id={self.id!r}, name={self.name!r}, platform_type={self.platform_type!r}, status={self.status!r})"


class CustomerInteraction(Base, TimestampMixin):
    """Stores interaction history for a customer."""

    __tablename__ = "customer_interactions"
    __table_args__ = (
        Index("ix_customer_interactions_customer_created", "customer_id", "created_at"),
        Index("ix_customer_interactions_type", "interaction_type"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    interaction_type = Column(String(64), nullable=False, index=True)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=False)

    customer = _relationship("Customer", back_populates="interactions")

    def __repr__(self) -> str:
        return f"CustomerInteraction(id={self.id!r}, customer_id={self.customer_id!r}, interaction_type={self.interaction_type!r})"
