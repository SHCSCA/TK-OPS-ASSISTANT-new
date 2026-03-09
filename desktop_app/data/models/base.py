from __future__ import annotations

# pyright: basic

"""Declarative SQLAlchemy base and shared mixins."""

from sqlalchemy import Boolean, Column, DateTime, MetaData, func
from sqlalchemy.ext.declarative import declarative_base


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


Base = declarative_base(metadata=MetaData(naming_convention=NAMING_CONVENTION))


class TimestampMixin:
    """Created and updated timestamps for mutable records."""

    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Soft-delete flags for recoverable records."""

    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
