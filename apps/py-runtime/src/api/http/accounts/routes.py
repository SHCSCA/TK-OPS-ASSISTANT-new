from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api.http.common.envelope import err, ok
from bootstrap.container import RuntimeContainer
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService
from legacy_adapter.serializers import serialize_account


class AccountUpsertPayload(BaseModel):
    username: str = Field(min_length=1, max_length=120)
    platform: str = Field(default="tiktok", max_length=40)
    region: str = Field(default="US", max_length=10)
    status: str = Field(default="active", max_length=20)
    followers: int = Field(default=0, ge=0)
    group_id: int | None = Field(default=None, alias="groupId")
    device_id: int | None = Field(default=None, alias="deviceId")
    cookie_status: str = Field(default="unknown", alias="cookieStatus", max_length=20)
    cookie_content: str | None = Field(default=None, alias="cookieContent")
    isolation_enabled: bool = Field(default=False, alias="isolationEnabled")
    last_connection_status: str = Field(default="unknown", alias="lastConnectionStatus", max_length=20)
    last_connection_message: str | None = Field(default=None, alias="lastConnectionMessage")
    risk_status: str = Field(default="normal", alias="riskStatus", max_length=20)
    notes: str | None = Field(default=None)
    tags: str | None = Field(default=None)

    model_config = {"populate_by_name": True}


class AccountBulkPayload(BaseModel):
    action: str = Field(min_length=1, max_length=40)
    account_ids: list[int] = Field(default_factory=list, alias="accountIds")
    manual_status: str | None = Field(default=None, alias="manualStatus")
    risk_status: str | None = Field(default=None, alias="riskStatus")
    group_id: int | None = Field(default=None, alias="groupId")
    archive_reason: str | None = Field(default=None, alias="archiveReason")

    model_config = {"populate_by_name": True}


class AccountArchivePayload(BaseModel):
    reason: str | None = Field(default=None)


def _not_found(message: str) -> JSONResponse:
    return JSONResponse(status_code=404, content=err("resource.not_found", message))


def _bad_request(message: str) -> JSONResponse:
    return JSONResponse(status_code=400, content=err("validation.invalid_input", message))


def _account_summary(items: list[dict[str, object]]) -> dict[str, int]:
    active = 0
    archived = 0
    risky = 0
    for item in items:
        if str(item.get("manualStatus") or item.get("status") or "") in {"active", "warming"}:
            active += 1
        if item.get("archivedAt"):
            archived += 1
        if str(item.get("riskStatus") or "normal") in {"watch", "high_risk", "frozen"}:
            risky += 1
    return {"total": len(items), "active": active, "archived": archived, "risky": risky}


def build_accounts_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/accounts", tags=["accounts"])

    @router.get("")
    def list_accounts(
        query: str | None = None,
        manual_status: str | None = None,
        system_status: str | None = None,
        risk_status: str | None = None,
        include_archived: bool = False,
    ) -> dict[str, object]:
        items = container.legacy_facade.list_accounts(
            query=query,
            manual_status=manual_status,
            system_status=system_status,
            risk_status=risk_status,
            include_archived=include_archived,
        )
        return ok({"items": items, "total": len(items), "summary": _account_summary(items)})

    @router.get("/{account_id}", response_model=None)
    def get_account_detail(account_id: int):
        repo = Repository()
        try:
            service = AccountService(repo)
            detail = service.get_account_detail(account_id)
            if detail is None:
                return _not_found("账号不存在，无法查看详情")
            if "account" in detail:
                account_payload = serialize_account(detail["account"])
                account_payload["activitySummary"] = detail["activitySummary"]
                account_payload["recentError"] = detail["lastError"]
            else:
                account_payload = dict(detail)
            return ok(account_payload)
        finally:
            repo.reset_session()

    @router.post("", response_model=None)
    def create_account(payload: AccountUpsertPayload):
        payload_data = payload.model_dump(by_alias=False)
        username = str(payload_data.pop("username", "")).strip()
        if not username:
            return _bad_request("用户名不能为空")

        repo = Repository()
        try:
            service = AccountService(repo)
            account = service.create_account(username, **payload_data)
            return ok(serialize_account(account))
        finally:
            repo.reset_session()

    @router.put("/{account_id}", response_model=None)
    def update_account(account_id: int, payload: AccountUpsertPayload):
        payload_data = payload.model_dump(exclude_unset=True, by_alias=False)
        username = str(payload_data.pop("username", "")).strip()
        if not username:
            return _bad_request("用户名不能为空")

        repo = Repository()
        try:
            service = AccountService(repo)
            account = service.update_account(account_id, username=username, **payload_data)
            if account is None:
                return _not_found("账号不存在，无法更新。")
            return ok(serialize_account(account))
        finally:
            repo.reset_session()

    @router.post("/bulk", response_model=None)
    def bulk_update_accounts(payload: AccountBulkPayload):
        if not payload.account_ids:
            return _bad_request("请至少选择一个账号")

        repo = Repository()
        try:
            service = AccountService(repo)
            try:
                result = service.bulk_update_accounts(
                    payload.account_ids,
                    action=payload.action,
                    manual_status=payload.manual_status,
                    risk_status=payload.risk_status,
                    group_id=payload.group_id,
                    archive_reason=payload.archive_reason,
                )
            except ValueError as exc:
                return _bad_request(str(exc))
            return ok(result)
        finally:
            repo.reset_session()

    @router.post("/{account_id}/archive", response_model=None)
    def archive_account(account_id: int, payload: AccountArchivePayload):
        repo = Repository()
        try:
            service = AccountService(repo)
            result = service.archive_account(account_id, reason=payload.reason)
            if result is None:
                return _not_found("账号不存在，无法归档")
            return ok(result)
        finally:
            repo.reset_session()

    @router.post("/{account_id}/unarchive", response_model=None)
    def unarchive_account(account_id: int):
        repo = Repository()
        try:
            service = AccountService(repo)
            result = service.unarchive_account(account_id)
            if result is None:
                return _not_found("账号不存在，无法取消归档")
            return ok(result)
        finally:
            repo.reset_session()

    @router.delete("/{account_id}", response_model=None)
    def delete_account(account_id: int):
        repo = Repository()
        try:
            service = AccountService(repo)
            deleted = service.delete_account(account_id)
            if not deleted:
                return _not_found("账号不存在，无法删除")
            return ok({"deleted": True, "accountId": account_id})
        finally:
            repo.reset_session()

    @router.post("/{account_id}/test", response_model=None)
    def test_account_connection(account_id: int):
        repo = Repository()
        try:
            service = AccountService(repo)
            try:
                result = service.test_account_connection(account_id)
            except ValueError:
                return _not_found("账号不存在，无法测试连接")
            if not bool(result.get("ok")):
                message = str(result.get("error") or "账号连接测试失败")
                return JSONResponse(
                    status_code=400 if result.get("error") else 500,
                    content=err("account.test_failed", message, details=result),
                )
            return ok(result)
        finally:
            repo.reset_session()

    return router
