# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TK-OPS is a Windows desktop application for TikTok Shop operations teams. It has migrated from the original PySide6/QtWebEngine architecture to a new single-shell architecture:

- **Tauri Desktop Host** (`apps/desktop/`): Modern desktop shell using Tauri 2 + Vue 3 + TypeScript
- **Python Sidecar Runtime** (`apps/py-runtime/`): Business logic runtime using Python + FastAPI
- **Legacy Reference** (`desktop_app/`): Preserved for migration reference and selective runtime code reuse, but forbidden from re-entering default run, integration, packaging, canary, or release paths

Current version: 1.3.2

## Non-Negotiable Constraints

1. **No giant files**: Do not reintroduce single files with thousands of lines. Split by page, data/composable, helpers, types, styles, and tests.
2. **No dual-shell runtime**: PySide6 and Tauri must not run as parallel product shells in any environment. `desktop_app/` is reference-only for migration and selective reuse.
3. **Global consistency first**: All new work must follow the unified architecture, directory boundaries, runtime contract, and migration workflow.
4. **Chinese comments only**: Any newly added comments must be in Chinese and should stay brief, explaining intent, boundaries, or non-obvious logic only.
5. **Global error handling and logging**: Exceptions must be caught, logged, and surfaced through a consistent error contract. Do not leave silent failures.
6. **Unified configuration bus**: New configuration must go through a single configuration entry/bus. Do not scatter config ownership across pages, services, and scripts.

## Current Architecture

### Three-Component Design

1. **Tauri Desktop Host** (`apps/desktop/`)
   - Built with Tauri 2 for secure, high-performance desktop shell
   - Frontend: Vue 3 + TypeScript + Vite + Pinia + Vue Router
   - Communicates with Python runtime via HTTP/WebSocket
   - Provides native window management, system tray, auto-updates

2. **Python Sidecar Runtime** (`apps/py-runtime/`)
   - FastAPI-based HTTP/WebSocket server (default: `127.0.0.1:8765`)
   - Business logic services (account, task, AI, asset, analytics, etc.)
   - Repository layer: Database access via SQLAlchemy ORM (same as legacy)
  - Legacy facade adapter for gradual migration from `desktop_app/`, but not for restoring the old shell as a supported runtime path
   - All endpoints return JSON envelopes: `{ok: bool, data: any, error: string}`

3. **Legacy Desktop App** (`desktop_app/`)
  - Preserved for migration reference and selective shared logic reuse
  - Not allowed as a default development, integration, packaging, or release entry point
   - Contains database models, migrations, and some service logic

### Key Communication Pattern

```
Frontend (Vue) → runtimeApi.ts → HTTP/WebSocket → FastAPI → Services → Repository → SQLite
                                    ↓
Frontend (Vue) ← WebSocket events ← FastAPI (real-time updates)
```

## Development Commands

### Environment Setup
```powershell
# Create and activate Python virtual environment
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Install frontend dependencies
cd apps\desktop
npm install
cd ..\..
```

### Run Application
```powershell
# Default development (starts both desktop and runtime)
scripts\dev.ps1

# Runtime only
scripts\dev.ps1 -RuntimeOnly

# Desktop only (connects to existing runtime)
scripts\dev.ps1 -DesktopOnly
```

### Build Commands
```powershell
# Build Python runtime only
scripts\build-runtime.ps1

# Build desktop frontend with runtime smoke test
scripts\build-desktop.ps1 -SmokeRuntime

# Generate Alpha release artifacts
scripts\release.ps1
```

### Testing
```powershell
# Python tests (including new runtime tests)
venv\Scripts\python.exe -m pytest tests -q

# Python compilation check
venv\Scripts\python.exe -m compileall apps\py-runtime\src desktop_app

# Frontend type checking and build
cd apps\desktop
npm run typecheck
npm run build

# Tauri managed runtime smoke test
scripts\smoke-tauri-runtime.ps1 -SkipBuild
```

### Pre-flight Gates (Release Quality)
```powershell
# Quick check for daily development
scripts\preflight-gate.ps1 -Quick

# Full check before release
scripts\preflight-gate.ps1 -Full
```

### Database Migrations
```powershell
# Create new migration (still uses desktop_app models)
venv\Scripts\python.exe -m alembic revision --autogenerate -m "description"

# Apply migrations (auto-runs on runtime startup)
venv\Scripts\python.exe -m alembic upgrade head
```

### Build Executable
```powershell
# Build Alpha release (output: dist-alpha\TK-OPS-Alpha\)
scripts\release.ps1

# Create Inno Setup installer (requires Inno Setup)
iscc installer.iss
```

## Database

- **Location**: `%APPDATA%/TK-OPS-ASSISTANT/tk_ops.db` (production)
- **Override**: Set `TK_OPS_DATA_DIR` environment variable for custom location
- **Migrations**: Alembic auto-runs on runtime startup
- **ORM**: SQLAlchemy 2.x with typed `Mapped` columns
- **Sample DB**: `sample_data/tk_ops_test_seed.db` (test data for UI verification)

### Core Models (Same as Legacy)
- `Account`: TikTok accounts with dual status (manual + system), risk status, device/group associations
- `Group`: Account grouping with color coding
- `Device`: Proxy devices with fingerprint tracking
- `Task`: Async operations (publish, scrape, analytics, etc.)
- `AIProvider`: AI service configurations
- `Asset`: Media library (images, videos, scripts, templates)
- `VideoSequence`, `VideoClip`, `VideoSubtitle`: Video editor data models
- `AnalysisSnapshot`, `ReportRun`, `WorkflowDefinition`, `ExperimentProject`: Analytics/workflow persistence

## Frontend Architecture (New)

### Technology Stack
- **Framework**: Vue 3 + TypeScript
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router
- **UI Components**: Custom CSS with Tailwind-like utilities
- **Communication**: HTTP client + WebSocket for real-time updates

### Key Frontend Files
- `apps/desktop/src/main.ts`: Application entry point
- `apps/desktop/src/App.vue`: Root component
- `apps/desktop/src/layouts/`: Layout components (AppShell, Sidebar, TitleBar, etc.)
- `apps/desktop/src/pages/`: Page components (Dashboard, Accounts, etc.)
- `apps/desktop/src/modules/`: Feature modules with composables and API clients
- `apps/desktop/src/modules/runtime/`: Runtime communication (httpClient.ts, runtimeApi.ts, runtimeSocket.ts)
- `apps/desktop/src/app/router/`: Routing configuration and route manifest

### Frontend Conventions
- Use `runtimeApi` from `modules/runtime/runtimeApi.ts` for all backend calls
- Use composables (e.g., `useAccountsData.ts`) for reactive data fetching
- Keep files small and responsibility-scoped; prefer page + composable + helpers + types + styles over monolithic components
- Pages load real data from runtime, not hardcoded examples
- Empty states shown when no data exists (no fake data)
- Task-backed actions create `Task` records and show progress
- Real-time updates via WebSocket connections
- New comments should be in Chinese and only added where they clarify intent or boundaries

## Testing Strategy

### Test Categories
1. **Runtime API Tests** (`test_runtime_api.py`): Verify FastAPI endpoints return valid JSON envelopes
2. **Bridge Contract** (`test_bridge_runtime_contract.py`): Legacy bridge compatibility tests
3. **CRUD Interaction** (`test_crud_interaction_matrix.py`): Test create/read/update/delete flows
4. **Page Audits** (`test_page_interaction_audit.py`): Verify pages load without hardcoded data
5. **Backend-Driven** (`test_analyst_page_backend_driven.py`): Ensure analyst pages use real aggregates
6. **Notification Truthfulness** (`test_notification_runtime_truthfulness.py`): Verify notifications come from real data
7. **Task-Backed Actions** (`test_task_backed_actions.py`): Test async operations create Task records
8. **Dev Seed** (`test_dev_seed_service.py`): Verify development data seeding

### Testing Patterns
- Use `Repository()` with in-memory SQLite for isolated tests
- Mock external HTTP calls with `httpx` responses
- Test both service layer and API layer
- Verify JSON envelope structure: `{ok, data, error}`

## Development Workflow

### Adding New Features (New Architecture)
1. **Define/Update models** in `desktop_app/database/models.py` (shared with legacy)
2. **Create migration**: `alembic revision --autogenerate -m "add_feature"`
3. **Implement service** in `apps/py-runtime/src/` (new) or `desktop_app/services/` (reuse)
4. **Add FastAPI endpoints** in `apps/py-runtime/src/api/http/{feature}/routes.py`
5. **Create frontend API** in `apps/desktop/src/modules/{feature}/` with composable
6. **Add to runtimeApi.ts** if needed for shared API client
7. **Create page component** in `apps/desktop/src/pages/{feature}/`
8. **Add route** in `apps/desktop/src/app/router/routes.ts` and `routeManifest.ts`
9. **Write tests** covering API contract, CRUD, and page behavior

### FastAPI Endpoint Pattern
```python
@router.get("/endpoint")
async def get_data() -> dict[str, Any]:
    """Docstring."""
    try:
        result = service.get_data()
        return {"ok": True, "data": result}
    except Exception as e:
        logger.exception("Failed to get data")
        return {"ok": False, "error": str(e)}
```

### Frontend API Pattern
```typescript
// In apps/desktop/src/modules/feature/useFeatureData.ts
export function useFeatureData() {
  const fetchData = async () => {
    return await runtimeApi.getFeatureData();
  };
  
  return { fetchData };
}
```

## Current Migration Status & Roadmap

### Current Progress (as of 2026-04-06)
- **New single-shell architecture**: Tauri host + Python sidecar runtime is production-ready
- **Development tooling**: Complete (dev, build, smoke test, release scripts)
- **Migrated pages**: 9 of 44 pages fully migrated to new architecture:
  - Dashboard
  - Account Management (production-ready phase 1)
  - AI Provider Management
  - Task Queue
  - Task Scheduler
  - AI Copywriter
  - Setup Wizard
  - System Settings
- **Menu baseline**: All 44 pages have placeholder routes to prevent missing pages
- **Account management phase 1**: Dual status model, risk states, archiving, bulk operations, activity summaries

### Next Phase Priorities
1. **Global framework consolidation**: Unify menu, routing, title, detail panel, and placeholder pages
2. **Page-by-page migration**: Start from `device-management`, migrate entire menu in order
3. **Runtime stability**: Enhance sidecar lifecycle, failure recovery, user-friendly error reporting
4. **Release quality**: Installation regression, upgrade coverage, data directory compatibility

### Migration Constraints
- New features MUST target `apps/desktop` and `apps/py-runtime`
- `desktop_app/` is for reference only—no new desktop shell features and no return to dual-shell runtime
- "Page opens" is NOT completion criteria—must have real data flows and error feedback
- Follow the gated superpowers workflow for non-trivial tasks
- Future page migration must be 1:1 deep migration and code conversion from the legacy implementation, not a loose reinterpretation

## Important Constraints

### What NOT to Do
- Don't hardcode business data in frontend (accounts, tasks, metrics)
- Don't fake metrics that can't be calculated from real data
- Don't create "silent no-op" buttons (show disabled state if no backend support)
- Don't skip API contract tests for new endpoints
- Don't bypass error handling in FastAPI endpoints
- Don't let exceptions disappear without structured logging and user-visible feedback where applicable
- Don't commit without running tests: `pytest tests -q`
- Don't add features to `desktop_app/` desktop shell
- Don't add new scattered configuration sources outside the shared configuration entry/bus

### What IS Supported
- Account/group/device/task management with real CRUD
- Dual status model (manual + system) with risk states
- Asset library with video poster generation
- AI provider configuration and chat
- Analytics aggregates from real activity data
- Task queue with async operations
- Workflow and experiment tracking
- Activity logs and notifications

### What is NOT Supported (Out of Scope)
- Real TikTok Shop orders, GMV, fulfillment data
- Actual ad spend and ROI calculations
- Live TikTok API integration for posting/scraping

## Debugging

### Logs
- **Runtime logs**: Check console output or `logs/runtime.log` (configurable via settings)
- **Frontend logs**: Browser DevTools in Tauri (right-click → Inspect Element)
- **Tauri logs**: Check console output during `npm run tauri dev`

### Common Issues
- **Runtime not starting**: Check port 8765 availability, Python venv activation
- **HTTP 401 errors**: Verify `X-TKOPS-Token` header matches runtime token
- **WebSocket connection failed**: Check runtime is running, token parameter in URL
- **Database locked**: Ensure `repo.reset_session()` called after operations
- **Migration conflicts**: Check `alembic_version` table, resolve with `alembic stamp head`

## Superpowers Plugin

This repo includes the `superpowers` plugin in `plugins/superpowers/` with skills for:

- `systematic-debugging`: Root cause analysis before fixes
- `subagent-driven-development`: Execute plans with isolated subagents
- `requesting-code-review`: Dispatch code review subagents
- `test-driven-development`: TDD workflow guidance

These skills are available via the Skill tool and should be used proactively when applicable.

For this repository, non-trivial engineering tasks should follow a gated superpowers workflow: create a plan in `docs/superpowers/plans/`, wait for approval, then create the matching design spec in `docs/superpowers/specs/`, and only then begin phased implementation.