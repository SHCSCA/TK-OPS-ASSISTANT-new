# AGENTS.md — TK-OPS Desktop Application

Guidelines for AI coding agents working in this repository.

## Project Overview

TK-OPS is a Windows desktop application for TikTok Shop operations teams.
Architecture: Python backend + PySide6/QtWebEngine shell + HTML/CSS/JS frontend,
bridged via QWebChannel.

- **Language**: Python 3.11+ (see README)
- **Desktop shell**: PySide6 6.10 with QWebEngineView
- **Frontend**: vanilla HTML / CSS / JavaScript (no bundler, no framework)
- **Database**: SQLite via SQLAlchemy 2.x + Alembic migrations
- **AI integration**: openai SDK
- **HTTP client**: httpx

## Commands

### Run the app

```powershell
# Always use the venv interpreter
venv\Scripts\python.exe desktop_app\main.py
```

### Install dependencies

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run tests

```powershell
venv\Scripts\python.exe -m pytest tests/ -v
```

No pytest.ini or pyproject.toml exists. Test files live in `tests/`.
There are no linter or formatter configurations in this repo.

### Database migrations (Alembic)

```powershell
# Auto-generate a migration after model changes
venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe change"

# Apply all pending migrations
venv\Scripts\python.exe -m alembic upgrade head
```

Note: The app runs Alembic migrations automatically on startup via
`desktop_app/database/__init__.py`. Manual migration is only needed during
development when changing models.

### Build EXE

```powershell
# Full build (PyInstaller)
python build.py --clean

# Or use the batch wrapper with progress bar
.\build_exe.bat --clean

# Icon generation only
python build.py --ico-only
```

Output: `dist\TK-OPS\TK-OPS.exe`

## Directory Structure

```
desktop_app/
  main.py              # CLI entry point, sets excepthook, calls app.build_application()
  app.py               # Composition root: QApplication, splash, init_db, WebShellWindow
  logging_config.py    # Rotating file + console logging setup
  ui/
    web_shell.py       # QWebEngineView main window + system tray
    bridge.py          # QWebChannel bridge: exposes Python services to JS frontend
  database/
    __init__.py        # Engine, session factory, auto-migration runner
    models.py          # SQLAlchemy 2.x ORM models (Account, Group, Device, Task, etc.)
    repository.py      # Generic CRUD repository
    migrations/        # Alembic migration scripts
  services/
    account_service.py # Account + Group CRUD
    ai_service.py      # AI provider management
    chat_service.py    # AI chat with presets
    task_service.py    # Task queue management
    license_service.py # License validation
    asset_service.py   # Asset management
    updater_service.py # Update checking
    usage_tracker.py   # Usage statistics
    fingerprint.py     # Hardware fingerprinting
    license_codec.py   # License encoding/decoding
  assets/
    app_shell.html     # Main shell page loaded by QWebEngineView
    app_shell.js       # Shell initialization script
    css/               # Stylesheets (variables.css, shell.css, components.css, pages-*.css)
    js/                # Frontend JS modules (routes, bindings, state, UI components)
    routes/            # HTML page fragments loaded by the router
tests/
  test_phase8_ai.py   # AI integration tests (unittest style)
```

## Code Style Conventions

### Python

- **Always** start files with `from __future__ import annotations`
- **Imports** are ordered: stdlib, third-party, local (absolute: `from desktop_app.x import y`)
- **Type annotations**: PEP 604 style (`str | None`, `list[int]`). These are safe
  at runtime because of `from __future__ import annotations`.
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes,
  `UPPER_SNAKE_CASE` for module-level constants, `_prefix` for private members
- **Logging**: `log = logging.getLogger(__name__)` at module top
- **Error handling in bridge.py**: The `@_safe` decorator wraps bridge methods,
  catching all exceptions and returning a JSON error envelope `{ok, data, error}`
- **Database sessions**: Use `session_scope()` context manager for transactions
- **ORM models**: SQLAlchemy 2.x declarative with `Mapped[]` type hints and `mapped_column()`
- **No linter or formatter is configured**. Keep style consistent with existing code.

### JavaScript / CSS

- Vanilla JS, no framework or build tooling
- Module-level IIFE or top-level functions
- CSS custom properties defined in `variables.css`, referenced throughout
- Page-specific styles in `pages-*.css` files
- No minification or bundling step

## Architecture Notes

### Python-to-JS Bridge

`bridge.py` exposes Python service methods to the JS frontend via QWebChannel.
All bridge methods return JSON envelopes: `{"ok": true, "data": ...}` on success,
`{"ok": false, "error": "..."}` on failure. The `@_safe` decorator handles this
automatically.

JS calls Python via `window.bridge.methodName(args...)` after QWebChannel init.

### Database Lifecycle

1. `app.py` calls `init_db()` on startup
2. `init_db()` creates the SQLite file (WAL mode) in `%APPDATA%/TK-OPS-ASSISTANT/`
3. Alembic `upgrade("head")` runs automatically
4. Services use `session_scope()` for all DB operations

### Startup Chain

`main.py` -> `build_application()` in `app.py` -> splash screen ->
`init_db()` -> `WebShellWindow` (loads `app_shell.html`) -> QWebChannel bridge ready

## Warnings

- No pyproject.toml exists. Build config is in `tk_ops.spec` (PyInstaller).
- The `desktop_app/core/` and old `desktop_app/ui/pages/` directories are empty
  artifacts from a previous architecture. Do not create files there.
- PySide6 6.10 requires Python 3.9+. The README says 3.11+. Do not use 3.8.
- Test infrastructure is minimal. Only one test file exists in `tests/`.
