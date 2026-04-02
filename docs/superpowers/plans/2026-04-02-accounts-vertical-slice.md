# Accounts Vertical Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 `accounts` 页面真正支持新建、编辑、删除、测试连接，并且所有失败路径都有用户可见的中文错误反馈。

**Architecture:** 后端只扩展 `apps/py-runtime` 的 `/accounts` HTTP 路由，直接复用 `AccountService` 的真实能力，不碰共享 legacy facade。前端保持 `Vue + Composition API`，在 `useAccountsData.ts` 内部自带一个最小请求封装，页面只负责表单、列表和反馈展示，不再把业务规则散落到模板里。

**Tech Stack:** FastAPI、Python pytest、Vue 3 `<script setup>`、原生 `fetch`、现有 runtime envelope（`{ ok, data, error }`）模式。

---

### Task 1: 先补后端 accounts HTTP 契约失败测试

**Files:**
- Modify: `tests/test_runtime_api.py`

- [ ] **Step 1: 写失败测试，覆盖 `/accounts` 的 CRUD + 测试连接**

```python
def test_runtime_accounts_support_create_update_delete_and_connection_test() -> None:
    client = _build_client()

    create = client.post(
        "/accounts",
        json={
            "username": "demo-new",
            "platform": "tiktok",
            "region": "US",
            "status": "active",
            "followers": 123,
            "cookieStatus": "valid",
        },
    )
    assert create.status_code == 200
    created = create.json()["data"]
    account_id = created["id"]

    update = client.put(
        f"/accounts/{account_id}",
        json={
            "username": "demo-renamed",
            "region": "DE",
            "status": "warming",
        },
    )
    assert update.status_code == 200
    assert update.json()["data"]["username"] == "demo-renamed"

    test_result = client.post(f"/accounts/{account_id}/test")
    assert test_result.status_code == 200
    assert "ok" in test_result.json()["data"]

    delete = client.delete(f"/accounts/{account_id}")
    assert delete.status_code == 200
    assert delete.json()["data"]["deleted"] is True
```

- [ ] **Step 2: 再补一个失败测试，验证缺失字段时返回可见错误**

```python
def test_runtime_accounts_reject_empty_username_with_chinese_error() -> None:
    client = _build_client()
    response = client.post("/accounts", json={"username": "   "})
    assert response.status_code == 400
    assert response.json()["ok"] is False
    assert "用户名不能为空" in response.json()["error"]["message"]
```

- [ ] **Step 3: 运行这两个定向测试，确认它们先失败**

Run:
`venv\Scripts\python.exe -m pytest tests/test_runtime_api.py -k "runtime_accounts_support_create_update_delete_and_connection_test or runtime_accounts_reject_empty_username_with_chinese_error" -v`

Expected: fail because `apps/py-runtime/src/api/http/accounts/routes.py` only exposes list.

### Task 2: 实现 py-runtime accounts 路由

**Files:**
- Modify: `apps/py-runtime/src/api/http/accounts/routes.py`
- Test: `tests/test_runtime_api.py`

- [ ] **Step 1: 给路由补齐 `POST /accounts`、`PUT /accounts/{id}`、`DELETE /accounts/{id}`、`POST /accounts/{id}/test`**

```python
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from api.http.common.envelope import ok
from bootstrap.container import RuntimeContainer


def build_accounts_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/accounts", tags=["accounts"])

    @router.get("")
    def list_accounts(status: str | None = None) -> dict[str, object]:
        accounts = container.legacy_facade.list_accounts(status=status)
        return ok({"items": accounts, "total": len(accounts)})

    @router.post("")
    async def create_account(request: Request) -> dict[str, object]:
        data = await request.json()
        username = str(data.get("username", "")).strip()
        if not username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名不能为空")
        account = container.legacy_facade.create_account(**_normalize_account_payload(data))
        return ok(account)

    @router.put("/{account_id}")
    async def update_account(account_id: int, request: Request) -> dict[str, object]:
        data = await request.json()
        account = container.legacy_facade.update_account(account_id, **_normalize_account_payload(data))
        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="账号不存在")
        return ok(account)

    @router.delete("/{account_id}")
    def delete_account(account_id: int) -> dict[str, object]:
        deleted = container.legacy_facade.delete_account(account_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="账号不存在")
        return ok({"deleted": True, "accountId": account_id})

    @router.post("/{account_id}/test")
    def test_account_connection(account_id: int) -> dict[str, object]:
        result = container.legacy_facade.test_account_connection(account_id)
        return ok(result)
```

- [ ] **Step 2: 如果后端还缺 payload 规范，先在路由里做最小字段归一化，不碰 legacy facade**

```python
def _normalize_account_payload(data: dict[str, Any]) -> dict[str, Any]:
    fields = dict(data or {})
    for key in ("username", "platform", "region", "status", "cookieStatus", "cookie_status"):
        if key in fields and fields[key] is not None:
            fields[key] = str(fields[key]).strip()
    if "cookieStatus" in fields and "cookie_status" not in fields:
        fields["cookie_status"] = fields.pop("cookieStatus")
    return fields
```

- [ ] **Step 3: 运行这两个定向测试，确认路由契约通过**

Run:
`venv\Scripts\python.exe -m pytest tests/test_runtime_api.py -k "runtime_accounts_support_create_update_delete_and_connection_test or runtime_accounts_reject_empty_username_with_chinese_error" -v`

Expected: pass.

### Task 3: 补 accounts 前端数据层失败测试

**Files:**
- Modify: `tests/test_accounts_vertical_slice.py`

- [ ] **Step 1: 新增文件，先写读文件契约测试，锁定页面必须出现的动作与反馈文案**

```python
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACCOUNTS_PAGE = ROOT / "apps" / "desktop" / "src" / "pages" / "accounts" / "AccountsPage.vue"
ACCOUNTS_DATA = ROOT / "apps" / "desktop" / "src" / "modules" / "accounts" / "useAccountsData.ts"


def test_accounts_page_exposes_create_edit_delete_test_and_error_feedback() -> None:
    text = ACCOUNTS_PAGE.read_text(encoding="utf-8") + "\n" + ACCOUNTS_DATA.read_text(encoding="utf-8")
    for snippet in [
        "新建账号",
        "编辑账号",
        "删除",
        "测试连接",
        "actionError",
        "actionMessage",
        "保存失败",
        "删除账号失败",
        "测试连接失败",
    ]:
        assert snippet in text, snippet
```

- [ ] **Step 2: 再补一个失败测试，锁定数据层必须提供表单态和动作方法**

```python
def test_accounts_data_layer_defines_local_request_helpers_and_mutations() -> None:
    text = ACCOUNTS_DATA.read_text(encoding="utf-8")
    for snippet in [
        "requestAccounts",
        "prepareCreate",
        "beginEdit",
        "saveAccount",
        "deleteAccount",
        "testAccountConnection",
        "actionError",
        "actionMessage",
    ]:
        assert snippet in text, snippet
```

- [ ] **Step 3: 先跑这组测试，确认它们失败**

Run:
`venv\Scripts\python.exe -m pytest tests/test_accounts_vertical_slice.py -v`

Expected: fail because `useAccountsData.ts` 和 `AccountsPage.vue` 还只有只读列表。

### Task 4: 实现 accounts 数据层

**Files:**
- Modify: `apps/desktop/src/modules/accounts/useAccountsData.ts`
- Test: `tests/test_accounts_vertical_slice.py`

- [ ] **Step 1: 在模块内部加一个最小 `fetch` 请求封装，直接对接 runtime `/accounts`**

```ts
async function requestAccounts<T>(path: string, method: 'POST' | 'PUT' | 'DELETE', body?: unknown): Promise<T> {
  const response = await fetch(`${getRuntimeBaseUrl()}${path}`, {
    method,
    headers: {
      'X-TKOPS-Token': getRuntimeToken(),
      ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const payload = await response.json().catch(() => null);
  if (!response.ok || !payload?.ok) {
    throw new Error(extractRuntimeErrorMessage(payload, 'Runtime 请求失败'));
  }
  return payload.data as T;
}
```

- [ ] **Step 2: 增加可编辑草稿、创建/编辑模式、错误消息、提交态、删除态、测试连接态**

```ts
const draft = ref(createDefaultDraft());
const actionError = ref('');
const actionMessage = ref('');
const saving = ref(false);
const deletingAccountId = ref<number | null>(null);
const testingAccountId = ref<number | null>(null);
const editingAccountId = ref<number | null>(null);
```

- [ ] **Step 3: 最小实现 `prepareCreate / beginEdit / saveAccount / deleteAccount / testAccountConnection`**

```ts
async function saveAccount() {
  const payload = buildPayload();
  if (!payload.username) {
    actionError.value = '用户名不能为空';
    return;
  }

  saving.value = true;
  try {
    const saved = editingAccountId.value
      ? await requestAccounts<AccountItem>(`/accounts/${editingAccountId.value}`, 'PUT', payload)
      : await requestAccounts<AccountItem>('/accounts', 'POST', payload);
    await resource.load();
    actionMessage.value = editingAccountId.value ? `已更新账号：${saved.username}` : `已创建账号：${saved.username}`;
  } catch (cause) {
    actionError.value = cause instanceof Error ? cause.message : '保存账号失败';
  } finally {
    saving.value = false;
  }
}
```

- [ ] **Step 4: 运行 `tests/test_accounts_vertical_slice.py`，确保数据层断言通过**

Run:
`venv\Scripts\python.exe -m pytest tests/test_accounts_vertical_slice.py -v`

Expected: pass after data layer methods exist.

### Task 5: 实现 accounts 页面交互与错误反馈

**Files:**
- Modify: `apps/desktop/src/pages/accounts/AccountsPage.vue`
- Test: `tests/test_accounts_vertical_slice.py`

- [ ] **Step 1: 把页面从纯列表改成“上方表单 + 下方列表 + 状态反馈”**

```vue
<form class="copywriter-form" @submit.prevent="saveAccount">
  <input v-model="draft.username" type="text" placeholder="请输入账号名称" />
  <button type="submit">{{ isEditing ? '保存修改' : '新建账号' }}</button>
  <button type="button" @click="prepareCreate">重置为新建</button>
</form>
```

- [ ] **Step 2: 在每条账号卡片上补齐编辑、删除、测试连接按钮，并显示 loading 状态**

```vue
<button type="button" @click="beginEdit(account)">编辑账号</button>
<button type="button" :disabled="testingAccountId === account.id" @click="testAccountConnection(account)">
  {{ testingAccountId === account.id ? '测试中...' : '测试连接' }}
</button>
<button type="button" :disabled="deletingAccountId === account.id" @click="deleteAccount(account)">
  {{ deletingAccountId === account.id ? '删除中...' : '删除' }}
</button>
```

- [ ] **Step 3: 在页面顶部显式渲染 `actionError` / `actionMessage`，确保用户能看到失败原因**

```vue
<p v-if="actionError" class="dashboard-banner dashboard-banner-error">{{ actionError }}</p>
<p v-if="actionMessage" class="dashboard-banner">{{ actionMessage }}</p>
```

- [ ] **Step 4: 运行页面契约测试，确保文案与交互标记都出现**

Run:
`venv\Scripts\python.exe -m pytest tests/test_accounts_vertical_slice.py -v`

Expected: pass.

### Task 6: 只跑 accounts 相关的最小验证

**Files:**
- Test: `tests/test_runtime_api.py`
- Test: `tests/test_accounts_vertical_slice.py`

- [ ] **Step 1: 运行后端 route 测试**

Run:
`venv\Scripts\python.exe -m pytest tests/test_runtime_api.py -k "runtime_accounts_support_create_update_delete_and_connection_test or runtime_accounts_reject_empty_username_with_chinese_error" -v`

- [ ] **Step 2: 运行 accounts 页面/数据层契约测试**

Run:
`venv\Scripts\python.exe -m pytest tests/test_accounts_vertical_slice.py -v`

- [ ] **Step 3: 如有失败，只修这条切片，不扩到全量测试**

Expected: all selected tests pass; do not run full `tests/` suite.

### Shared API contracts to hand off if needed

- `POST /accounts` with JSON body for create
- `PUT /accounts/{account_id}` with JSON body for edit
- `DELETE /accounts/{account_id}` for delete
- `POST /accounts/{account_id}/test` for connection test
- `useAccountsData.ts` local runtime helper can stay private unless you want to promote it into shared `runtimeApi.ts`
