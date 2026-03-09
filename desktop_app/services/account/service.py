from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false

"""账号领域服务实现。"""

from collections.abc import Mapping
from dataclasses import dataclass

from sqlalchemy.orm import Session

from ...data.database import Database
from ...data.models.account import TikTokAccount
from ...data.repositories.account_repo import AccountRepository
from ...data.repositories.operations_repo import OperationsRepository


@dataclass
class AccountDTO:
    """账号列表项 DTO。"""

    account_id: str
    name: str
    display_name: str
    status: str
    region: str | None
    category: str | None
    follower_count: int
    product_count: int
    orders_count: int
    total_revenue: float
    conversion_rate: float
    health_score: float


@dataclass
class AccountSummaryDTO:
    """账号摘要 DTO。"""

    account_id: str
    name: str
    status: str
    region: str | None
    category: str | None
    followers: int
    products: int
    orders: int
    revenue: float
    conversion_rate: float
    health_score: float


@dataclass
class AccountMetricsDTO:
    """账号指标 DTO。"""

    account_id: str
    health_score: float
    order_count: int
    refund_count: int
    revenue: float
    average_order_value: float
    conversion_rate: float
    follower_count: int
    product_count: int


class AccountService:
    """账号管理领域服务。"""

    service_name: str = "account"

    def __init__(self, database: Database | None = None) -> None:
        """初始化账号服务。"""

        self._database: Database = database or Database()
        self._account_repo: AccountRepository = AccountRepository(self._database.create_session)
        self._operations_repo: OperationsRepository = OperationsRepository(self._database.create_session)

    def initialize(self) -> None:
        """初始化服务，无需额外动作。"""

        return None

    def shutdown(self) -> None:
        """关闭服务，无需额外动作。"""

        return None

    def healthcheck(self) -> dict[str, object]:
        """返回账号服务健康状态。"""

        with self._database.session_scope() as session:
            active_accounts = self._account_repo.count_active(session)
        return {
            "service": self.service_name,
            "status": "ok",
            "active_accounts": active_accounts,
            "database": "connected",
        }

    def list_accounts(self) -> list[dict[str, object]]:
        """返回账号列表。"""

        with self._database.session_scope() as session:
            accounts = self._account_repo.get_active_accounts(session)
        return [self._dto_to_dict(self._to_account_dto(account)) for account in accounts]

    def get_account_summary(self, account_id: str) -> dict[str, object]:
        """返回单个账号摘要。"""

        with self._database.session_scope() as session:
            account = self._require_account(session, account_id)
            summary = AccountSummaryDTO(
                account_id=account.account_id,
                name=account.shop_name,
                status=account.status,
                region=account.region,
                category=account.category,
                followers=int(account.follower_count or 0),
                products=int(account.product_count or 0),
                orders=int(account.orders_count or 0),
                revenue=float(account.total_revenue or 0.0),
                conversion_rate=float(account.conversion_rate or 0.0),
                health_score=float(account.health_score or 0.0),
            )
        return self._dto_to_dict(summary)

    def create_account(self, data: dict[str, object]) -> dict[str, object]:
        """创建并持久化新账号。"""

        payload = self._build_create_payload(data)
        with self._database.session_scope() as session:
            existing = self._account_repo.get_by_account_id(session, str(payload["account_id"]))
            if existing is not None:
                raise ValueError(f"账号已存在: {payload['account_id']}")
            account = self._account_repo.create_account(session, **payload)
        return self._dto_to_dict(self._to_account_dto(account))

    def update_account(self, account_id: str, data: dict[str, object]) -> dict[str, object]:
        """更新指定账号。"""

        payload = self._build_update_payload(data)
        with self._database.session_scope() as session:
            self._require_account(session, account_id)
            account = self._account_repo.update_account(session, account_id, **payload)
            if account is None:
                raise LookupError(f"账号不存在: {account_id}")
        return self._dto_to_dict(self._to_account_dto(account))

    def delete_account(self, account_id: str) -> bool:
        """软删除指定账号。"""

        with self._database.session_scope() as session:
            deleted = self._account_repo.soft_delete_account(session, account_id)
        return deleted

    def get_account_metrics(self, account_id: str) -> dict[str, object]:
        """返回账号经营指标。"""

        with self._database.session_scope() as session:
            account = self._require_account(session, account_id)
            aggregates = self._operations_repo.get_account_order_metrics(session, int(account.id))
            order_count = int(aggregates["order_count"])
            revenue = float(aggregates["revenue"])
            metrics = AccountMetricsDTO(
                account_id=account.account_id,
                health_score=float(account.health_score or 0.0),
                order_count=order_count,
                refund_count=int(aggregates["refund_count"]),
                revenue=revenue,
                average_order_value=(revenue / order_count) if order_count else 0.0,
                conversion_rate=float(account.conversion_rate or 0.0),
                follower_count=int(account.follower_count or 0),
                product_count=int(account.product_count or 0),
            )
        return self._dto_to_dict(metrics)

    def _require_account(self, session: Session, account_id: str) -> TikTokAccount:
        """确保账号存在。"""

        account = self._account_repo.get_by_account_id(session, account_id)
        if account is None:
            raise LookupError(f"账号不存在: {account_id}")
        return account

    def _to_account_dto(self, account: TikTokAccount) -> AccountDTO:
        """将模型转换为账号 DTO。"""

        return AccountDTO(
            account_id=account.account_id,
            name=account.shop_name,
            display_name=account.display_name,
            status=account.status,
            region=account.region,
            category=account.category,
            follower_count=int(account.follower_count or 0),
            product_count=int(account.product_count or 0),
            orders_count=int(account.orders_count or 0),
            total_revenue=float(account.total_revenue or 0.0),
            conversion_rate=float(account.conversion_rate or 0.0),
            health_score=float(account.health_score or 0.0),
        )

    def _build_create_payload(self, data: dict[str, object]) -> dict[str, object]:
        """标准化创建账号输入。"""

        account_id = str(data.get("account_id") or "").strip()
        shop_name = str(data.get("name") or data.get("shop_name") or "").strip()
        if not account_id:
            raise ValueError("account_id 不能为空")
        if not shop_name:
            raise ValueError("name 不能为空")
        return {
            "account_id": account_id,
            "shop_name": shop_name,
            "display_name": str(data.get("display_name") or shop_name),
            "platform_username": self._optional_str(data.get("platform_username")),
            "status": str(data.get("status") or "active"),
            "region": self._optional_str(data.get("region")),
            "category": self._optional_str(data.get("category")),
            "follower_count": self._coerce_int(data.get("follower_count")),
            "product_count": self._coerce_int(data.get("product_count")),
            "orders_count": self._coerce_int(data.get("orders_count")),
            "total_revenue": self._coerce_float(data.get("total_revenue")),
            "conversion_rate": self._coerce_float(data.get("conversion_rate")),
            "health_score": self._coerce_float(data.get("health_score"), default=100.0),
            "metadata_json": self._coerce_dict(data.get("metadata")),
        }

    def _build_update_payload(self, data: dict[str, object]) -> dict[str, object]:
        """标准化更新账号输入。"""

        payload: dict[str, object] = {}
        mapping = {
            "name": "shop_name",
            "shop_name": "shop_name",
            "display_name": "display_name",
            "platform_username": "platform_username",
            "status": "status",
            "region": "region",
            "category": "category",
            "follower_count": "follower_count",
            "product_count": "product_count",
            "orders_count": "orders_count",
            "total_revenue": "total_revenue",
            "conversion_rate": "conversion_rate",
            "health_score": "health_score",
            "metadata": "metadata_json",
        }
        for source_key, target_key in mapping.items():
            if source_key not in data:
                continue
            raw_value = data[source_key]
            if target_key in {"follower_count", "product_count", "orders_count"}:
                payload[target_key] = self._coerce_int(raw_value)
            elif target_key in {"total_revenue", "conversion_rate", "health_score"}:
                payload[target_key] = self._coerce_float(raw_value)
            elif target_key == "metadata_json":
                payload[target_key] = self._coerce_dict(raw_value)
            else:
                payload[target_key] = self._optional_str(raw_value) if raw_value is not None else None
        if "shop_name" in payload and not payload["shop_name"]:
            raise ValueError("name 不能为空")
        return payload

    @staticmethod
    def _coerce_int(value: object, *, default: int = 0) -> int:
        """将输入转换为整数。"""

        if value is None:
            return default
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            normalized = value.strip()
            return default if not normalized else int(normalized)
        raise ValueError("无法转换为整数")

    @staticmethod
    def _coerce_float(value: object, *, default: float = 0.0) -> float:
        """将输入转换为浮点数。"""

        if value is None:
            return default
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            normalized = value.strip()
            return default if not normalized else float(normalized)
        raise ValueError("无法转换为浮点数")

    @staticmethod
    def _optional_str(value: object) -> str | None:
        """将输入转换为可空字符串。"""

        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @staticmethod
    def _coerce_dict(value: object) -> dict[str, object]:
        """将输入转换为字典。"""

        if isinstance(value, Mapping):
            return {str(key): item for key, item in value.items()}
        return {}

    @staticmethod
    def _dto_to_dict(dto: AccountDTO | AccountSummaryDTO | AccountMetricsDTO) -> dict[str, object]:
        """将 DTO 转换为字典。"""

        return {key: value for key, value in vars(dto).items()}


__all__ = ["AccountDTO", "AccountMetricsDTO", "AccountService", "AccountSummaryDTO"]
