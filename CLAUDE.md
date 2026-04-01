# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TK-OPS is a Windows desktop application for TikTok Shop operations teams. It uses a Python backend with PySide6/QtWebEngine for the desktop shell, SQLite for persistence, and a web-based frontend that communicates with Python via QWebChannel bridge.

Current version: 1.2.3

## Architecture

### Three-Layer Design

1. **Python Backend** (`desktop_app/`)
   - Services layer: Business logic (account, task, AI, asset, analytics, etc.)
   - Repository layer: Database access via SQLAlchemy ORM
   - Bridge layer: QWebChannel slots exposing services to frontend

2. **QWebChannel Bridge** (`desktop_app/ui/bridge.py`)
   - All slots return JSON envelopes: `{ok: bool, data: any, error: string}`
   - `@_safe` decorator catches exceptions and returns error envelopes
   - `dataChanged` signal pushes mutations to frontend for reactive updates
   - Never crashes - all errors are caught and returned as JSON

3. **Web Frontend** (`desktop_app/assets/`)
   - HTML/CSS/JS pages loaded in QtWebEngine
   - `data.js`: Bridge API wrapper with caching and error handling
   - `routes.js`: Route metadata and page factories
   - `page-loaders.js`: Data loading and behavior binding per page
   - `bindings.js`: Shared interaction handlers

### Key Communication Pattern

```
Frontend (JS) → data.js → QWebChannel → bridge.py → Service → Repository → SQLite
                                    ↓
Frontend (JS) ← dataChanged signal ← bridge.py (reactive updates)
```

## Development Commands

### Setup
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run Application
```powershell
venv\Scripts\python.exe desktop_app\main.py
```

### Run Tests
```powershell
# All tests
venv\Scripts\python.exe -m pytest tests/ -v

# Specific test file
venv\Scripts\python.exe -m pytest tests/test_bridge_runtime_contract.py -v

# Key integration tests
venv\Scripts\python.exe -m pytest tests/test_notification_runtime_truthfulness.py tests/test_analyst_page_backend_driven.py tests/test_dev_seed_service.py -v
```

### Database Migrations
```powershell
# Create new migration
venv\Scripts\python.exe -m alembic revision --autogenerate -m "description"

# Apply migrations (auto-runs on app startup)
venv\Scripts\python.exe -m alembic upgrade head
```

### Build Executable
```powershell
.\build_exe.bat --clean
```
Output: `dist\TK-OPS\TK-OPS.exe`

## Database

- **Location**: `%APPDATA%/TK-OPS-ASSISTANT/tk_ops.db` (production)
- **Override**: Set `TK_OPS_DATA_DIR` environment variable for custom location
- **Migrations**: Alembic auto-runs on startup via `desktop_app/app.py`
- **ORM**: SQLAlchemy 2.x with typed `Mapped` columns
- **Sample DB**: `sample_data/tk_ops_test_seed.db` (test data for UI verification)

### Core Models
- `Account`: TikTok accounts with status, cookies, device/group associations
- `Group`: Account grouping with color coding
- `Device`: Proxy devices with fingerprint tracking
- `Task`: Async operations (publish, scrape, analytics, etc.)
- `AIProvider`: AI service configurations
- `Asset`: Media library (images, videos, scripts, templates)
- `VideoSequence`, `VideoClip`, `VideoSubtitle`: Video editor data models
- `AnalysisSnapshot`, `ReportRun`, `WorkflowDefinition`, `ExperimentProject`: Analytics/workflow persistence

## Frontend Architecture

### Page Loading Flow
1. User navigates → `routes.js` matches route → calls page factory
2. Factory creates DOM structure → `page-loaders.js` loads data via `data.js`
3. Data fetched from bridge → page rendered → bindings attached via `bindings.js`
4. Runtime updates via `runtimeSummaryHandlers` (dynamic sidebar content)

### Key Frontend Files
- `app_shell.html`: Main desktop shell with sidebar navigation
- `routes.js`: Route definitions and page factory functions
- `page-loaders.js`: Per-page data loading and initialization
- `bindings.js`: Shared button handlers and interactions
- `data.js`: Bridge API wrapper with caching (`window.api.*`)
- `state.js`: Client-side state management
- `ui-notifications.js`: Real-time notification rendering

### Frontend Conventions
- Pages load real data from backend, not hardcoded examples
- Use `api.*` methods from `data.js` for all backend calls
- Runtime summaries populated via `runtimeSummaryHandlers[pageKey]`
- Task-backed actions create `Task` records and show progress
- Empty states show when no data exists (no fake data)

## Testing Strategy

### Test Categories
1. **Bridge Contract** (`test_bridge_runtime_contract.py`): Verify all bridge slots return valid JSON envelopes
2. **CRUD Interaction** (`test_crud_interaction_matrix.py`): Test create/read/update/delete flows
3. **Page Audits** (`test_page_interaction_audit.py`): Verify pages load without hardcoded data
4. **Backend-Driven** (`test_analyst_page_backend_driven.py`): Ensure analyst pages use real aggregates
5. **Notification Truthfulness** (`test_notification_runtime_truthfulness.py`): Verify notifications come from real data
6. **Task-Backed Actions** (`test_task_backed_actions.py`): Test async operations create Task records
7. **Dev Seed** (`test_dev_seed_service.py`): Verify development data seeding

### Testing Patterns
- Use `Repository()` with in-memory SQLite for isolated tests
- Mock external HTTP calls with `httpx` responses
- Test both service layer and bridge layer
- Verify JSON envelope structure: `{ok, data, error}`

## Development Workflow

### Adding New Features
1. Define models in `desktop_app/database/models.py`
2. Create migration: `alembic revision --autogenerate -m "add_feature"`
3. Implement service in `desktop_app/services/`
4. Add bridge slots in `desktop_app/ui/bridge.py` with `@_safe` decorator
5. Create frontend API in `data.js` (e.g., `api.feature.*`)
6. Add page factory in `routes.js` and loader in `page-loaders.js`
7. Write tests covering bridge contract, CRUD, and page behavior

### Bridge Slot Pattern
```python
@Slot(result=str)
@_safe
def methodName(self, arg1: str, arg2: int) -> str:
    """Docstring."""
    result = self._service.do_something(arg1, arg2)
    return _ok(result)  # Returns {"ok": true, "data": result}
```

### Frontend API Pattern
```javascript
// In data.js
api.feature = {
    doSomething: function(arg1, arg2) {
        return callBackend('methodName', arg1, arg2);
    }
};
```

## Important Constraints

### What NOT to Do
- Don't hardcode business data in frontend factories (accounts, tasks, metrics)
- Don't fake metrics that can't be calculated from real data
- Don't create "silent no-op" buttons (if no backend support, show disabled state)
- Don't skip bridge contract tests for new slots
- Don't bypass `@_safe` decorator on bridge slots
- Don't commit without running tests: `pytest tests/ -v`

### What IS Supported
- Account/group/device/task management with real CRUD
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
- Application logs: Check console output or `desktop_app/logging_config.py` for log file location
- Bridge errors: All exceptions caught by `@_safe` and logged
- Frontend errors: Check browser DevTools console (F12 in QtWebEngine)

### Common Issues
- **Bridge method not found**: Check slot is registered in `bridge.py` and exposed via QWebChannel
- **JSON parse error**: Verify slot returns `_ok(data)` or `_err(msg)`, not raw values
- **Database locked**: Ensure `repo.reset_session()` called after operations
- **Migration conflicts**: Check `alembic_version` table and resolve with `alembic stamp head`

## Superpowers Plugin

This repo includes the `superpowers` plugin in `plugins/superpowers/` with skills for:

- `systematic-debugging`: Root cause analysis before fixes
- `subagent-driven-development`: Execute plans with isolated subagents
- `requesting-code-review`: Dispatch code review subagents
- `test-driven-development`: TDD workflow guidance

These skills are available via the Skill tool and should be used proactively when applicable.

For this repository, non-trivial engineering tasks should follow a gated superpowers workflow: create a plan in `docs/superpowers/plans/`, wait for approval, then create the matching design spec in `docs/superpowers/specs/`, and only then begin phased implementation.
