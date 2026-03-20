"""Account & Group management service."""
from __future__ import annotations

from typing import Any, Sequence

from desktop_app.database.models import Account, Device, Group
from desktop_app.database.repository import Repository


class AccountService:
    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    def create_account(self, username: str, **kwargs: Any) -> Account:
        return self._repo.add(Account(username=username, **kwargs))

    def list_accounts(self, *, status: str | None = None) -> Sequence[Account]:
        return self._repo.list_accounts(status=status)

    def get_account(self, pk: int) -> Account | None:
        return self._repo.get_by_id(Account, pk)

    def update_account(self, pk: int, **fields: Any) -> Account | None:
        account = self._repo.get_by_id(Account, pk)
        if account is None:
            return None
        return self._repo.update(account, **fields)

    def delete_account(self, pk: int) -> bool:
        account = self._repo.get_by_id(Account, pk)
        if account is None:
            return False
        self._repo.delete(account)
        return True

    def bind_device(self, account_id: int, device_id: int) -> Account | None:
        return self.update_account(account_id, device_id=device_id)

    # ── Groups ──

    def create_group(self, name: str, **kwargs: Any) -> Group:
        return self._repo.add(Group(name=name, **kwargs))

    def list_groups(self) -> Sequence[Group]:
        return self._repo.list_groups()

    def update_group(self, pk: int, **fields: Any) -> Group | None:
        group = self._repo.get_by_id(Group, pk)
        if group is None:
            return None
        return self._repo.update(group, **fields)

    def delete_group(self, pk: int) -> bool:
        group = self._repo.get_by_id(Group, pk)
        if group is None:
            return False
        self._repo.delete(group)
        return True

    def assign_group(self, account_id: int, group_id: int) -> Account | None:
        return self.update_account(account_id, group_id=group_id)

    # ── Devices ──

    def list_devices(self, *, status: str | None = None) -> Sequence[Device]:
        return self._repo.list_devices(status=status)

    def create_device(self, device_code: str, name: str, **kwargs: Any) -> Device:
        return self._repo.add(Device(device_code=device_code, name=name, **kwargs))

    def get_device(self, pk: int) -> Device | None:
        return self._repo.get_by_id(Device, pk)

    def update_device(self, pk: int, **fields: Any) -> Device | None:
        device = self._repo.get_by_id(Device, pk)
        if device is None:
            return None
        return self._repo.update(device, **fields)

    def delete_device(self, pk: int) -> bool:
        device = self._repo.get_by_id(Device, pk)
        if device is None:
            return False
        self._repo.delete(device)
        return True
