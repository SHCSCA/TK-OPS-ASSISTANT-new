from __future__ import annotations

# pyright: basic

"""Repository implementation for customer and CRM records."""

from collections.abc import Callable
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models.crm import Customer, CustomerInteraction

from .base import BaseRepository


class CRMRepository(BaseRepository[Customer]):
    """Persistence adapter for CRM records."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        super().__init__(session_factory, Customer)

    def get_active_customers(self) -> list[Customer]:
        with self._read_session() as session:
            session_any = cast(Any, session)
            customer_deleted = cast(Any, getattr(Customer, "is_deleted"))
            customer_status = cast(Any, getattr(Customer, "status"))
            customer_last_contact = cast(Any, getattr(Customer, "last_contact_at"))
            customer_created = cast(Any, getattr(Customer, "created_at"))
            statement = cast(Any, select(Customer))
            statement = statement.where(customer_deleted.is_(False))
            statement = statement.where(customer_status == "active")
            statement = statement.order_by(customer_last_contact.desc(), customer_created.desc())
            return list(session_any.scalars(statement).all())

    def get_by_platform_identity(self, platform_type: str, platform_id: str) -> Customer | None:
        with self._read_session() as session:
            session_any = cast(Any, session)
            customer_platform_type = cast(Any, getattr(Customer, "platform_type"))
            customer_platform_id = cast(Any, getattr(Customer, "platform_id"))
            statement = cast(Any, select(Customer))
            statement = statement.where(customer_platform_type == platform_type, customer_platform_id == platform_id)
            return session_any.scalars(statement).first()

    def get_customer_with_interactions(self, customer_id: int) -> Customer | None:
        with self._read_session() as session:
            session_any = cast(Any, session)
            customer_interactions = cast(Any, getattr(Customer, "interactions"))
            customer_id_column = cast(Any, getattr(Customer, "id"))
            statement = cast(Any, select(Customer))
            statement = statement.options(selectinload(customer_interactions)).where(customer_id_column == customer_id)
            return session_any.scalars(statement).first()

    def get_interactions(self, customer_id: int) -> list[CustomerInteraction]:
        with self._read_session() as session:
            session_any = cast(Any, session)
            interaction_customer_id = cast(Any, getattr(CustomerInteraction, "customer_id"))
            interaction_created = cast(Any, getattr(CustomerInteraction, "created_at"))
            statement = cast(Any, select(CustomerInteraction))
            statement = statement.where(interaction_customer_id == customer_id).order_by(interaction_created.desc())
            return list(session_any.scalars(statement).all())
