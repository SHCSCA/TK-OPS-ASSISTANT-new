# Full Backend Wiring And Interaction Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace hardcoded frontend data and fake interactions across the TK-OPS desktop app with real backend/database-driven flows, while ensuring every visible interaction has a complete, testable logic path.

**Architecture:** The work proceeds from the runtime chain outward: first harden the frontend bridge contract and shared interaction infrastructure, then wire existing CRUD pages fully to current models, then add aggregate services and new persistence for analytics/workflow/experiment pages, and finally complete page-by-page interaction audits. Each page must be backed by either direct table mutations, real aggregate queries, or real task-queue actions.

**Tech Stack:** Python 3.11+, SQLAlchemy 2.x, Alembic migrations, PySide6 QWebChannel bridge, vanilla HTML/CSS/JavaScript, pytest.

---

## File Map

- `desktop_app/database/models.py`
  - Existing ORM entities; will expand for analytics snapshots, report runs, workflow definitions/runs, experiment projects/views, and activity log entities as needed.
- `desktop_app/database/repository.py`
  - Existing CRUD and aggregate queries; will gain typed list/query helpers, cross-entity aggregates, and retrieval for new entities.
- `desktop_app/database/migrations/versions/*.py`
  - Alembic migrations for every schema change.
- `desktop_app/ui/bridge.py`
  - Single frontend contract; must expose every page’s real list/query/mutation/task action with JSON envelopes.
- `desktop_app/services/account_service.py`
  - Existing account/group/device business logic.
- `desktop_app/services/task_service.py`
  - Existing task queue logic; will expand for async action dispatch.
- `desktop_app/services/ai_service.py`
  - Existing AI provider logic.
- `desktop_app/services/asset_service.py`
  - Existing asset logic.
- `desktop_app/services/chat_service.py`
  - Existing AI chat fallback behavior; fix failing tests before large execution.
- `desktop_app/services/*.py`
  - New aggregate services for dashboard, analytics, experiments, reports, workflows, activity feeds.
- `desktop_app/assets/js/bridge.js`
  - Frontend bridge wrapper and browser stub; must stay aligned with new bridge slots.
- `desktop_app/assets/js/main.js`
  - Shared shell bootstrap, status panel, global refresh hooks.
- `desktop_app/assets/js/bindings.js`
  - Shared interaction binding; must stop fake bindings and only route to real actions.
- `desktop_app/assets/js/page-loaders.js`
  - Real data loaders; large part of page-by-page rewiring.
- `desktop_app/assets/js/routes.js`
  - Route metadata, summaries, status bars; static copy must be reduced and replaced with dynamic summaries where appropriate.
- `desktop_app/assets/js/factories/*.js`
  - Current static route templates; must be audited page-by-page and converted away from hardcoded primary data.
- `desktop_app/assets/app_shell.html`
  - Runtime shell templates; some primary templates still contain hardcoded rows and cards.
- `tests/test_frontend_style_baseline.py`
  - Frontend selector and shell regressions.
- `tests/test_phase8_ai.py`
  - Existing AI tests; currently failing fallback expectations must be restored.
- `tests/`
  - Add backend, bridge, aggregate, and interaction audit tests.

## Task 1: Stabilize The Backend Contract Before New Wiring

**Files:**
- Modify: `tests/test_phase8_ai.py`
- Modify: `desktop_app/services/chat_service.py`
- Modify: `desktop_app/assets/js/bridge.js`
- Modify: `desktop_app/ui/bridge.py`
- Test: `tests/test_phase8_ai.py`

- [ ] **Step 1: Write failing tests for the current backend contract gaps**

Extend `tests/test_phase8_ai.py` with explicit tests for:

```python
def test_chat_service_no_provider_fallback_uses_unconfigured_message():
    ...

def test_bridge_stub_includes_existing_management_methods():
    ...
```

Also add assertions for any already-exposed management slots that the frontend depends on but the stub currently omits.

- [ ] **Step 2: Run the focused backend contract tests to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_phase8_ai.py -v`
Expected: FAIL on the chat fallback message mismatch and any missing stub/bridge coverage you added.

- [ ] **Step 3: Fix the chat fallback behavior to match the intended no-provider contract**

In `desktop_app/services/chat_service.py`, ensure the no-provider path remains distinct from the all-providers-failed path. Keep behavior like:

```python
if not providers:
    return ChatResult(
        content="未配置 AI 供应商，请先在「AI 供应商配置」页面添加。",
        model="",
        provider_name="",
        finished=True,
    )
```

If existing test DB state can contain stale providers, make `_get_providers()` deterministic and safe for tests rather than returning spurious fallback failures.

- [ ] **Step 4: Align `bridge.js` stub with the real bridge surface**

Update `desktop_app/assets/js/bridge.js` so the stub contains all currently relied-upon CRUD/settings/theme/license/update methods and any new slots introduced later in this plan. Keep stub data minimal and obviously empty, not fake business data.

- [ ] **Step 5: Run the focused backend contract tests to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_phase8_ai.py -v`
Expected: PASS.

## Task 2: Create A Page And Interaction Audit Harness

**Files:**
- Create: `tests/test_bridge_runtime_contract.py`
- Create: `tests/test_page_interaction_audit.py`
- Modify: `desktop_app/assets/app_shell.html`
- Modify: `desktop_app/assets/js/routes.js`
- Modify: `desktop_app/assets/js/page-loaders.js`

- [ ] **Step 1: Write failing tests for page interaction coverage markers**

Create `tests/test_page_interaction_audit.py` with checks that every runtime page template contains audit markers or a discoverable interaction manifest, for example:

```python
def test_primary_templates_define_interaction_audit_scope():
    html = ...
    assert 'data-page-audit=' in html
```

Create `tests/test_bridge_runtime_contract.py` with a first pass over bridge method names the runtime pages need.

- [ ] **Step 2: Run the new audit tests to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_bridge_runtime_contract.py tests/test_page_interaction_audit.py -v`
Expected: FAIL because the templates and runtime bridge coverage are not instrumented yet.

- [ ] **Step 3: Add lightweight audit metadata to runtime templates and routes**

In `desktop_app/assets/app_shell.html` and/or `desktop_app/assets/js/routes.js`, add per-page metadata such as:

```html
<template id="route-account-main" data-page-audit="account">
```

and route-level metadata listing the expected interaction families for that page.

- [ ] **Step 4: Expose an interaction registry in page loaders**

In `desktop_app/assets/js/page-loaders.js`, add a small page audit registry that records for each route:

```javascript
pageAudits['account'] = {
    dataSources: ['listAccounts'],
    interactions: ['create', 'edit', 'delete', 'filter', 'detail', 'batch'],
};
```

This is not a user feature; it exists to keep page-by-page completion honest.

- [ ] **Step 5: Run the audit tests to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_bridge_runtime_contract.py tests/test_page_interaction_audit.py -v`
Expected: PASS.

## Task 3: Add Missing Persistence For Analytics, Reports, Workflows, And Experiments

**Files:**
- Modify: `desktop_app/database/models.py`
- Modify: `desktop_app/database/repository.py`
- Create: `desktop_app/services/analytics_service.py`
- Create: `desktop_app/services/report_service.py`
- Create: `desktop_app/services/workflow_service.py`
- Create: `desktop_app/services/activity_service.py`
- Create: `desktop_app/database/migrations/versions/<new_revision>.py`
- Test: `tests/test_backend_entities.py`

- [ ] **Step 1: Write failing backend entity tests**

Create `tests/test_backend_entities.py` with minimal persistence tests for the new entities you introduce, for example:

```python
def test_can_create_experiment_project_and_view():
    ...

def test_can_store_workflow_definition_and_run():
    ...

def test_can_store_report_run_and_activity_log():
    ...
```

- [ ] **Step 2: Run the entity tests to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_backend_entities.py -v`
Expected: FAIL because the models/services do not exist yet.

- [ ] **Step 3: Add the new ORM entities minimally**

In `desktop_app/database/models.py`, add focused entities for:

```python
class AnalysisSnapshot(Base): ...
class ReportRun(Base): ...
class WorkflowDefinition(Base): ...
class WorkflowRun(Base): ...
class ExperimentProject(Base): ...
class ExperimentView(Base): ...
class ActivityLog(Base): ...
```

Keep fields minimal and purposeful: names, status, payload/config JSON text, related ids, created/updated timestamps, summary/result fields.

- [ ] **Step 4: Add repository helpers and thin services**

Add list/create/update/query helpers in `desktop_app/database/repository.py` and thin services in the new service modules. Follow the existing service style: repository-backed, small methods, no framework complexity.

- [ ] **Step 5: Create and apply the migration**

Run: `venv\Scripts\python.exe -m alembic revision --autogenerate -m "add analytics workflow experiment persistence"`
Expected: a new migration file under `desktop_app/database/migrations/versions/`

Then run: `venv\Scripts\python.exe -m alembic upgrade head`
Expected: migration applies successfully.

- [ ] **Step 6: Run the entity tests to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_backend_entities.py -v`
Expected: PASS.

## Task 4: Expand The Bridge To Cover Real Aggregate And Workflow APIs

**Files:**
- Modify: `desktop_app/ui/bridge.py`
- Modify: `desktop_app/assets/js/bridge.js`
- Modify: `tests/test_bridge_runtime_contract.py`
- Test: `tests/test_bridge_runtime_contract.py`

- [ ] **Step 1: Write failing bridge contract tests for new page families**

Extend `tests/test_bridge_runtime_contract.py` to assert bridge methods for:

```python
expected = [
    'getDashboardStats',
    'getAccountOverview',
    'getAnalyticsSummary',
    'getConversionAnalysis',
    'getPersonaAnalysis',
    'listReportRuns',
    'createReportRun',
    'listWorkflowDefinitions',
    'createWorkflowDefinition',
    'startWorkflowRun',
    'listExperimentProjects',
    'createExperimentProject',
    'listActivityLogs',
]
```

Adjust names to the exact methods you introduce, but lock them in tests.

- [ ] **Step 2: Run bridge contract tests to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_bridge_runtime_contract.py -v`
Expected: FAIL because the new bridge slots do not exist yet.

- [ ] **Step 3: Add the new bridge slots with JSON envelopes**

In `desktop_app/ui/bridge.py`, instantiate the new services and add `_safe` slots for aggregate queries and mutations. Keep the bridge consistent with existing CRUD patterns.

- [ ] **Step 4: Mirror the new bridge surface in `bridge.js` stub**

Return empty-but-valid envelope shapes, not fake business records.

- [ ] **Step 5: Run bridge contract tests to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_bridge_runtime_contract.py -v`
Expected: PASS.

## Task 5: Replace Static Dashboard And CRUD Summaries With Real Data

**Files:**
- Modify: `desktop_app/assets/js/page-loaders.js`
- Modify: `desktop_app/assets/js/routes.js`
- Modify: `desktop_app/assets/js/main.js`
- Modify: `desktop_app/assets/app_shell.html`
- Test: `tests/test_page_runtime_data.py`

- [ ] **Step 1: Write failing runtime data tests for dashboard and CRUD pages**

Create `tests/test_page_runtime_data.py` with assertions that the page loaders no longer rely on static summary strings for the primary metrics of:

```python
['dashboard', 'account', 'group-management', 'device-management', 'ai-provider', 'task-queue', 'asset-center']
```

The tests can inspect route metadata / loader registration / absence of obvious hardcoded KPI rows in runtime templates.

- [ ] **Step 2: Run runtime data tests to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
Expected: FAIL because runtime templates and route summaries still contain hardcoded core data.

- [ ] **Step 3: Rewire dashboard and CRUD summaries to real aggregate data**

In `desktop_app/assets/js/page-loaders.js`, load dashboard and CRUD counters from bridge queries. In `desktop_app/assets/js/routes.js`, reduce static summary copy to semantic labels; actual counts/statuses should be filled at runtime.

- [ ] **Step 4: Replace fake page-empty placeholders with real empty-state logic**

When lists are empty, show explicit empty state driven by returned data length instead of template scaffolding pretending data exists.

- [ ] **Step 5: Run runtime data tests to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
Expected: PASS.

## Task 6: Complete CRUD Page Interactions End-To-End

**Files:**
- Modify: `desktop_app/assets/js/page-loaders.js`
- Modify: `desktop_app/assets/js/bindings.js`
- Modify: `desktop_app/assets/js/ui-crud-forms.js`
- Modify: `desktop_app/assets/js/main.js`
- Test: `tests/test_crud_interaction_matrix.py`

- [ ] **Step 1: Write failing CRUD interaction matrix tests**

Create `tests/test_crud_interaction_matrix.py` to assert that each CRUD page registers the full interaction set it promises. Example:

```python
def test_account_page_declares_create_edit_delete_filter_detail_batch():
    ...
```

- [ ] **Step 2: Run CRUD interaction tests to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_crud_interaction_matrix.py -v`
Expected: FAIL because multiple pages still have visible actions with fake or partial behavior.

- [ ] **Step 3: Rewire every visible CRUD action to real backend behavior**

For each first-layer page, ensure buttons and interactions map to real logic:

1. Create / edit / delete -> CRUD forms + bridge mutation.
2. Activate / enable / bind -> mutation or task creation.
3. Detail cards / rows -> real selected object in `detailHost`.
4. Filter / sort / pagination -> real client-side operations over fetched data.
5. Batch actions -> real multi-item operations or queued tasks.

- [ ] **Step 4: Run CRUD interaction tests to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_crud_interaction_matrix.py -v`
Expected: PASS.

## Task 7: Introduce Real Task-Backed Async Actions For Buttons That Are Currently Fake

**Files:**
- Modify: `desktop_app/services/task_service.py`
- Modify: `desktop_app/ui/bridge.py`
- Modify: `desktop_app/assets/js/bindings.js`
- Modify: `desktop_app/assets/js/page-loaders.js`
- Test: `tests/test_task_backed_actions.py`

- [ ] **Step 1: Write failing task-backed action tests**

Create `tests/test_task_backed_actions.py` for actions like:

```python
def test_test_connection_creates_task():
    ...

def test_batch_environment_check_creates_task():
    ...
```

- [ ] **Step 2: Run the task-backed action tests to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_task_backed_actions.py -v`
Expected: FAIL because these actions still use placeholder feedback.

- [ ] **Step 3: Add explicit task-creation pathways for async UI actions**

In `desktop_app/services/task_service.py` and `desktop_app/ui/bridge.py`, add helper methods for named async actions. In frontend bindings/loaders, replace placeholder toasts with real task creation and task list refresh.

- [ ] **Step 4: Run the task-backed action tests to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_task_backed_actions.py -v`
Expected: PASS.

## Task 8: Build Real Analytics Aggregates From Existing Data First

**Files:**
- Modify: `desktop_app/services/analytics_service.py`
- Modify: `desktop_app/ui/bridge.py`
- Modify: `desktop_app/assets/js/page-loaders.js`
- Modify: `desktop_app/assets/js/factories/analytics.js`
- Modify: `desktop_app/assets/js/charts-analytics.js`
- Test: `tests/test_analytics_aggregates.py`

- [ ] **Step 1: Write failing analytics aggregate tests**

Create `tests/test_analytics_aggregates.py` for real aggregate outputs using current entities. Example:

```python
def test_conversion_analysis_uses_tasks_accounts_and_assets():
    ...

def test_persona_analysis_returns_real_buckets_from_account_data():
    ...
```

- [ ] **Step 2: Run analytics aggregate tests to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_analytics_aggregates.py -v`
Expected: FAIL because no aggregate service exists yet.

- [ ] **Step 3: Implement first-pass real aggregates using existing tables**

In `desktop_app/services/analytics_service.py`, derive real aggregates from `Account`, `Task`, `Asset`, and `AppSetting`. Keep the first pass honest: if a metric cannot be supported, return structured “unsupported / no data” metadata rather than inventing values.

- [ ] **Step 4: Rewire analytics pages to consume those aggregates**

Update `desktop_app/ui/bridge.py`, `desktop_app/assets/js/page-loaders.js`, `desktop_app/assets/js/factories/analytics.js`, and `desktop_app/assets/js/charts-analytics.js` so pages render real data, real empty states, and real side-detail updates.

- [ ] **Step 5: Run analytics aggregate tests to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_analytics_aggregates.py -v`
Expected: PASS.

## Task 9: Redefine Unsupported Business Metrics Or Add New Persistence Where Required

**Files:**
- Modify: `desktop_app/services/analytics_service.py`
- Modify: `desktop_app/services/report_service.py`
- Modify: `desktop_app/database/models.py`
- Modify: `desktop_app/database/repository.py`
- Modify: `desktop_app/database/migrations/versions/<new_or_updated_revision>.py`
- Modify: `desktop_app/assets/js/factories/analytics.js`
- Test: `tests/test_analytics_metric_truthfulness.py`

- [ ] **Step 1: Write failing metric-truthfulness tests**

Create `tests/test_analytics_metric_truthfulness.py` with assertions like:

```python
def test_profit_metrics_are_real_or_marked_unsupported():
    ...

def test_roi_metrics_are_not_fabricated_without_source_model():
    ...
```

- [ ] **Step 2: Run truthfulness tests to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_analytics_metric_truthfulness.py -v`
Expected: FAIL because some pages still imply fake business metrics.

- [ ] **Step 3: Choose per-page resolution and implement it**

For each unsupported metric family, do one of two things:

1. Add new persistence and real data flow if the page requires it.
2. Rename/reframe the page to honest operational metrics if true business data does not exist yet.

Do not leave misleading static labels like “利润”“ROI”“订单额” if the backing model does not exist.

- [ ] **Step 4: Run truthfulness tests to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_analytics_metric_truthfulness.py -v`
Expected: PASS.

## Task 10: Persist Experiments, Reports, And Workflow State End-To-End

**Files:**
- Modify: `desktop_app/services/report_service.py`
- Modify: `desktop_app/services/workflow_service.py`
- Modify: `desktop_app/ui/bridge.py`
- Modify: `desktop_app/assets/js/page-loaders.js`
- Modify: `desktop_app/assets/js/factories/content.js`
- Modify: `desktop_app/assets/js/factories/generation.js`
- Modify: `desktop_app/assets/js/factories/toolconsole.js`
- Test: `tests/test_experiment_workflow_persistence.py`

- [ ] **Step 1: Write failing persistence tests for experiment/report/workflow pages**

Create `tests/test_experiment_workflow_persistence.py` for save/load/run/history behavior.

- [ ] **Step 2: Run the persistence tests to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_experiment_workflow_persistence.py -v`
Expected: FAIL because these pages still operate as prototypes.

- [ ] **Step 3: Implement the minimal real persistence loops**

Ensure experiment projects/views, report runs, workflow definitions/runs can be created, listed, loaded, updated, and launched through the bridge. Frontend factories and loaders must read those records instead of embedding prototype cards.

- [ ] **Step 4: Run the persistence tests to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_experiment_workflow_persistence.py -v`
Expected: PASS.

## Task 11: Seed Honest Development Data For Empty Environments

**Files:**
- Create: `desktop_app/services/dev_seed_service.py`
- Modify: `desktop_app/ui/bridge.py`
- Modify: `tests/test_dev_seed_service.py`

- [ ] **Step 1: Write failing seed-service tests**

Create `tests/test_dev_seed_service.py` with assertions that development seed data populates the real tables without frontend hardcoding.

- [ ] **Step 2: Run seed tests to verify failure**

Run: `venv\Scripts\python.exe -m pytest tests/test_dev_seed_service.py -v`
Expected: FAIL because no seed service exists yet.

- [ ] **Step 3: Implement a development-only seed path**

Add a small service that creates coherent sample accounts, groups, devices, tasks, assets, provider records, and any new aggregate entities needed for page verification. Expose it only for development/testing, not as a silent runtime side effect.

- [ ] **Step 4: Run seed tests to verify pass**

Run: `venv\Scripts\python.exe -m pytest tests/test_dev_seed_service.py -v`
Expected: PASS.

## Task 12: Verify Every Page Family And Interaction Matrix

**Files:**
- Modify: any files above if verification reveals gaps
- Test: `tests/test_bridge_runtime_contract.py`
- Test: `tests/test_page_interaction_audit.py`
- Test: `tests/test_page_runtime_data.py`
- Test: `tests/test_crud_interaction_matrix.py`
- Test: `tests/test_task_backed_actions.py`
- Test: `tests/test_analytics_aggregates.py`
- Test: `tests/test_analytics_metric_truthfulness.py`
- Test: `tests/test_experiment_workflow_persistence.py`
- Test: `tests/test_backend_entities.py`
- Test: `tests/test_phase8_ai.py`
- Test: `tests/`

- [ ] **Step 1: Run all targeted new tests**

Run:

```bash
venv\Scripts\python.exe -m pytest tests/test_phase8_ai.py tests/test_bridge_runtime_contract.py tests/test_page_interaction_audit.py tests/test_page_runtime_data.py tests/test_crud_interaction_matrix.py tests/test_task_backed_actions.py tests/test_analytics_aggregates.py tests/test_analytics_metric_truthfulness.py tests/test_experiment_workflow_persistence.py tests/test_backend_entities.py -v
```

Expected: PASS.

- [ ] **Step 2: Run the full suite**

Run: `venv\Scripts\python.exe -m pytest tests/ -v`
Expected: PASS.

- [ ] **Step 3: Run the desktop app and perform page-by-page manual verification**

Run: `venv\Scripts\python.exe desktop_app\main.py`

Verify page families in order:

1. Shared shell interactions
2. Dashboard and CRUD pages
3. Analytics pages
4. Experiment/workflow/content pages

For each page, verify: open, load, primary action, secondary actions, row/card click, filters, selects, pagination, detail update, create/edit/delete if applicable, and empty/error paths.

- [ ] **Step 4: Document any remaining intentionally unsupported paths**

Only if a path is truly out of current business scope and explicitly disabled. No silent no-op buttons are allowed.
