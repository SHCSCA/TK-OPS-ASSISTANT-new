# Account Management Production Ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在新架构中把账号管理从基础 CRUD 提升到生产预备版第一阶段，补齐双状态、风险状态、批量操作、归档与审计摘要。

**Architecture:** 以后端数据模型与 runtime API 收口为主，前端列表页围绕新契约改造成工作台。人工状态继续使用账号主状态字段，系统状态由登录校验与连通性检测汇总，风险状态与归档语义独立持久化。

**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、Alembic、Vue 3、TypeScript、pytest

---

### Task 1: 账号模型与迁移补齐

**Files:**
- Modify: `desktop_app/database/models.py`
- Create: `desktop_app/database/migrations/versions/2026_account_management_production_ready.py`
- Test: `tests/test_database_lifecycle.py`

- [ ] 为 `Account` 增加风险状态与归档字段，并保证 ORM 默认值明确
- [ ] 新增 Alembic 迁移，把新字段安全加入 `accounts`
- [ ] 更新数据库生命周期测试，确保 head 迁移可用

### Task 2: 账号服务与 runtime API 收口

**Files:**
- Modify: `desktop_app/database/repository.py`
- Modify: `desktop_app/services/account_service.py`
- Modify: `apps/py-runtime/src/legacy_adapter/serializers.py`
- Modify: `apps/py-runtime/src/api/http/accounts/routes.py`
- Test: `tests/test_accounts_vertical_slice.py`
- Test: `tests/test_runtime_api.py`

- [ ] 为账号列表增加筛选能力：关键词、人工状态、系统状态、风险状态、归档
- [ ] 为账号服务增加批量更新、归档、取消归档、账号活动摘要读取
- [ ] 为账号序列化增加双状态、风险状态、归档字段、最近检测信息和最近活动摘要
- [ ] 为 runtime accounts 路由增加新查询参数与批量动作接口
- [ ] 写垂类测试覆盖：创建、筛选、批量改状态、归档、检测回写

### Task 3: 账号页工作台重构

**Files:**
- Modify: `apps/desktop/src/modules/runtime/types.ts`
- Modify: `apps/desktop/src/modules/runtime/runtimeApi.ts`
- Modify: `apps/desktop/src/modules/accounts/useAccountsData.ts`
- Modify: `apps/desktop/src/pages/accounts/AccountsPage.vue`
- Test: `tests/test_accounts_vertical_slice.py`

- [ ] 为前端类型增加风险状态、归档、活动摘要和批量接口类型
- [ ] 在数据层增加筛选状态、勾选状态、批量操作与详情侧板状态
- [ ] 把账号页改造成双状态工作台，加入筛选、批量操作条和详情摘要
- [ ] 保留基础创建/编辑能力，但删除主入口改为归档优先
- [ ] 补前端合约测试，确保页面上存在双状态与批量操作语义

### Task 4: 最终回归

**Files:**
- Test: `tests/test_accounts_vertical_slice.py`
- Test: `tests/test_runtime_api.py`
- Test: `tests/test_database_lifecycle.py`

- [ ] 运行账号相关 pytest
- [ ] 运行全量 pytest
- [ ] 运行 `npm run typecheck`
- [ ] 运行 `npm run build`
- [ ] 运行 `python -m compileall apps/py-runtime/src desktop_app`
