# PLN-03 — TDD Strategy for TK-OPS Desktop Application

## 1. Purpose

This document defines a pragmatic testing strategy for the TK-OPS desktop application. It is designed for a Python 3.11+, PySide6, SQLAlchemy, LiteLLM stack using Clean Architecture / MVVM, a plugin shell, config bus, and typed Qt signals.

Goals:

- Keep fast feedback on core logic.
- Make PySide6 UI changes safe without over-investing in brittle end-to-end automation.
- Enable development against fake services before real backends are ready.
- Establish CI quality gates that scale from MVP to production.

The current codebase already shows patterns that this strategy should protect:

- `desktop_app/core/config.py` contains pure configuration loading logic suited for unit tests.
- `desktop_app/db.py` contains SQLAlchemy setup suited for integration tests.
- `desktop_app/pipeline/pipeline.py` contains orchestration logic suited for service unit tests with mocks.
- `desktop_app/main.py` contains theme toggling, navigation, and page construction suited for widget and smoke tests.

---

## 2. Testing Principles

1. **Prefer unit tests first** for deterministic logic.
2. **Test seams, not internals**: public methods, signals, persistence boundaries, and user-visible state.
3. **Widget tests stay local**: test one widget/page behavior at a time with `pytest-qt`.
4. **Smoke tests stay cheap**: page loads, navigation, theme switch, no exceptions.
5. **Fake services are first-class**: usable in tests and during feature development before real APIs exist.
6. **SQLite integration tests are real**: use temporary SQLite databases instead of mocking SQLAlchemy.
7. **No overly complex framework layering**: pytest + pytest-qt + pytest-cov + unittest.mock is enough.

---

## 3. Test Pyramid

Target distribution:

- **Unit tests (70%)**
  - Pure logic
  - Services
  - Models / DTOs
  - Config bus
  - Typed signals helpers
  - Theme engine
- **Integration tests (20%)**
  - DB operations
  - Repository behavior with real SQLite
  - Service-to-service flows
  - Config persistence
- **Widget tests (8%)**
  - Individual widget rendering
  - Signal connections
  - Button clicks / field changes / state transitions
- **Smoke tests (2%)**
  - Page loading
  - Navigation flow
  - Theme switching

### Pyramid intent

| Layer | Purpose | Speed | Main tools |
|---|---|---:|---|
| Unit | Protect business logic and contracts | Fastest | `pytest`, `unittest.mock` |
| Integration | Verify real persistence and wiring | Medium | `pytest`, SQLite, SQLAlchemy |
| Widget | Verify PySide6 UI behavior | Medium | `pytest`, `pytest-qt` |
| Smoke | Catch app-level breakage | Slowest but small | `pytest`, `pytest-qt` |

### Scope guidance

- If a test does **not** need a real database or Qt event loop, it should be a **unit test**.
- If a test needs SQLAlchemy mappings, transactions, or persisted config, it should be an **integration test**.
- If a test needs a widget instance, signal emission, or a simulated click, it should be a **widget test**.
- If a test only answers “does this page/app section load safely?”, it should be a **smoke test**.

---

## 4. Test Directory Structure

```text
tests/
├── conftest.py          # Global fixtures (qapp, fake_config, fake_db, etc.)
├── unit/
│   ├── core/            # Config bus, theme engine, signals
│   ├── services/        # Domain services with mocked repos
│   └── models/          # DTO validation, model constraints
├── integration/
│   ├── db/              # Repository tests with real SQLite
│   └── services/        # Service integration tests
├── widgets/
│   ├── components/      # Individual widget tests
│   └── pages/           # Page-level widget tests
└── smoke/
    ├── test_pages.py    # Every page loads without error
    └── test_navigation.py  # Sidebar nav works
```

### Mapping to planned application structure

Planned production structure:

```text
core/
services/
models/
ui/
```

Test rule:

- `tests/unit/core/` mirrors `core/`
- `tests/unit/services/` mirrors `services/`
- `tests/unit/models/` mirrors `models/`
- `tests/widgets/components/` mirrors reusable UI components
- `tests/widgets/pages/` mirrors full pages/views

Example future mapping:

```text
core/config_bus.py               -> tests/unit/core/test_config_bus.py
core/theme_engine.py             -> tests/unit/core/test_theme_engine.py
services/account/service.py      -> tests/unit/services/test_account_service.py
models/content_dto.py            -> tests/unit/models/test_content_dto.py
ui/pages/account_page.py         -> tests/widgets/pages/test_account_page.py
ui/components/sidebar.py         -> tests/widgets/components/test_sidebar.py
```

---

## 5. PySide6 Testing Patterns

### 5.1 pytest-qt fixtures

Use:

- `qtbot` to create widgets, simulate interaction, and wait for events.
- `qapp` when a `QApplication` instance is needed explicitly.

Typical rules:

- Always register widgets with `qtbot.addWidget(widget)`.
- Prefer `qtbot.mouseClick`, `qtbot.keyClicks`, and `qtbot.waitSignal` over manual event dispatch.
- Assert UI state using public properties (`text()`, `isVisible()`, current index, emitted signal payloads).

### 5.2 Widget test pattern

Pattern:

1. Create widget.
2. Inject fake/mock dependencies.
3. Simulate interaction.
4. Assert state change and/or signal emission.

Copy-paste-ready example aligned to the current `MainWindow` implementation:

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from desktop_app.main import MainWindow


def test_theme_toggle_button_click_updates_state_and_emits_signal(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    theme_button = next(
        button
        for button in window.findChildren(QPushButton)
        if button.text() == "🌓 切换主题"
    )

    with qtbot.waitSignal(window.theme_changed, timeout=1000) as blocker:
        qtbot.mouseClick(theme_button, Qt.LeftButton)

    assert blocker.args == [True]
    assert window.theme.is_dark is True
```

Recommended improvement for future UI code:

- add stable `objectName` values such as `themeToggleButton`
- prefer `findChild(QPushButton, "themeToggleButton")` over matching button text

### 5.3 Page smoke test pattern

Pattern:

1. Load page/window.
2. Show it.
3. Let Qt process events.
4. Assert page rendered and no exception path triggered.

Copy-paste-ready example:

```python
def test_dashboard_page_loads_without_exception(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window._switch_page(0)
    window.show()
    qtbot.waitExposed(window)

    assert window.pages.currentIndex() == 0
    assert window.windowTitle() != ""
```

### 5.4 Service test pattern

Pattern:

1. Mock dependencies.
2. Call service method.
3. Assert return value.
4. Assert side effects and dependency calls.

Copy-paste-ready example based on current pipeline shape:

```python
from unittest.mock import Mock

from desktop_app.models import Product
from desktop_app.pipeline.pipeline import Pipeline


def test_run_copy_generation_builds_prompt_and_returns_draft():
    ai_client = Mock()
    ai_client.complete.return_value = "High-converting copy"

    tiktok_client = Mock()
    service = Pipeline(ai_client=ai_client, tiktok_client=tiktok_client)

    product = Product(
        id=101,
        title="Smart Bottle",
        description="Tracks hydration",
        price=29.9,
    )

    result = service.run_copy_generation(
        product=product,
        prompt_template="Write copy for {title}: {description}",
    )

    ai_client.complete.assert_called_once_with("Write copy for Smart Bottle: Tracks hydration")
    assert result.product_id == 101
    assert result.content == "High-converting copy"
```

### 5.5 Config bus test pattern

Pattern:

1. Set value.
2. Verify signal emitted.
3. Verify new value stored.
4. Verify persistence adapter called when relevant.

Recommended future shape:

```python
def test_set_value_emits_signal_and_persists(qtbot, fake_config_bus, fake_config_store):
    with qtbot.waitSignal(fake_config_bus.value_changed, timeout=1000) as blocker:
        fake_config_bus.set("theme.mode", "dark")

    assert blocker.args == ["theme.mode", "dark"]
    assert fake_config_bus.get("theme.mode") == "dark"
    assert fake_config_store.data["theme.mode"] == "dark"
```

### 5.6 Theme switching regression pattern

Because the current UI already contains `ThemeManager`, `theme_changed`, `_toggle_theme()`, and `_apply_theme()`, theme regression coverage should be explicit.

Copy-paste-ready example:

```python
def test_toggle_theme_flips_dark_mode_and_updates_stylesheet(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    initial_state = window.theme.is_dark
    initial_stylesheet = window.styleSheet()

    window._toggle_theme()

    assert window.theme.is_dark is not initial_state
    assert window.styleSheet() != initial_stylesheet
```

### 5.7 Navigation regression pattern

The current UI keeps sidebar page indexes in button properties and switches pages through `_switch_page(page_idx)`.

Copy-paste-ready example:

```python
def test_switch_page_updates_current_index_and_active_button(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window._switch_page(3)

    assert window.pages.currentIndex() == 3
    assert window.nav_buttons[3].objectName() == "navButtonActive"
    assert window.nav_buttons[0].objectName() == "navButton"
```

---

## 6. Unit Testing Scope by Layer

### 6.1 `core/`

Cover:

- Config bus get/set semantics
- Theme engine palette rules
- Typed signal wrappers
- Plugin shell registration and lifecycle
- Shared types and validation helpers

Examples:

- invalid config key rejected
- default theme resolved correctly
- plugin registration deduplicates IDs
- signal payload type contract preserved

### 6.2 `services/`

Cover:

- Account service orchestration
- Content generation flow
- Analytics transformations
- Automation rule evaluation
- AI service prompt/result handling

Rules:

- Mock repositories, gateways, and API clients
- Assert domain outputs, not SQLAlchemy internals
- Keep one service concern per test

### 6.3 `models/`

Cover:

- DTO validation
- default values
- model constraints
- serialization/deserialization if introduced

Current code alignment:

- `desktop_app/models.py` dataclasses are ideal early unit-test targets.
- Future Pydantic DTOs should validate required fields and reject malformed payloads.

---

## 7. Integration Testing Scope

### 7.1 Database integration tests

Use real SQLite for:

- SQLAlchemy model mappings
- repository CRUD
- uniqueness / nullable / foreign key behavior
- transaction boundaries

Copy-paste-ready example aligned to current `desktop_app/db.py`:

```python
from desktop_app.db import Base, create_session, get_engine, ProductModel


def test_product_model_persists_and_reads_back(tmp_path):
    db_file = tmp_path / "test.db"
    engine = get_engine(f"sqlite:///{db_file}")
    Session = create_session(engine)

    session = Session()
    try:
        product = ProductModel(
            title="Hydration Bottle",
            description="Vacuum insulated",
            price=19.99,
            category="Drinkware",
        )
        session.add(product)
        session.commit()

        saved = session.query(ProductModel).one()

        assert saved.title == "Hydration Bottle"
        assert saved.category == "Drinkware"
    finally:
        session.close()
        Base.metadata.drop_all(engine)
```

### 7.2 Service integration tests

Use for:

- service + repository
- service + config persistence
- service + fake backend combination

Do not use for:

- full app startup
- cross-page GUI flows
- external network calls

### 7.3 Config persistence integration tests

Use for:

- config bus writes to disk/db
- app restart restores values
- theme or workspace preferences survive reload

---

## 8. Widget Tests

Widget tests focus on isolated PySide6 behavior.

### What belongs here

- Widget renders expected labels/controls
- Clicking button emits signal
- Form field edits update local state/view-model
- Disabled/enabled states react correctly
- Page binds fake service data into visible controls

### What does not belong here

- Real DB I/O
- Network calls
- Multi-page full app flows

### Example component cases

- Sidebar button activates correct route
- Theme toggle emits theme change
- Search box updates filter state
- Table widget displays expected rows from fake service output

---

## 9. Smoke Tests

Smoke tests are intentionally thin and stable.

Required smoke coverage:

1. Every page can be instantiated and shown without raising exceptions.
2. Sidebar navigation changes stacked page index.
3. Theme switching runs without regression.
4. Main shell loads with fake services and fake config.

### Example smoke matrix

| Smoke test | Assertion |
|---|---|
| Page load | widget exists, visible, no exception |
| Navigation | target page index changes |
| Theme switch | stylesheet changes, no crash |
| Plugin shell boot | shell loads default plugins without error |

---

## 10. Fake Service Contracts

Fake services are shared development infrastructure, not just test helpers. They should be deterministic, return realistic data shapes, and support UI development before real backends exist.

### 10.1 Rules for fake services

- Match the public interface of the real service.
- Return stable, hardcoded, realistic business data.
- Avoid randomness unless explicitly seeded.
- Expose simple override hooks where a test needs alternate data.
- Never perform network I/O.

### 10.2 Contract: `FakeAccountService`

Responsibilities:

- list accounts
- get account details
- return account status summary

Recommended shape:

```python
class FakeAccountService:
    def list_accounts(self) -> list[dict]:
        return [
            {
                "account_id": "acc_us_001",
                "display_name": "TK_US_Main",
                "region": "US",
                "status": "online",
                "owner": "Amy",
            },
            {
                "account_id": "acc_uk_002",
                "display_name": "TK_UK_Local",
                "region": "UK",
                "status": "warning",
                "owner": "Leo",
            },
        ]

    def get_account(self, account_id: str) -> dict:
        return next(item for item in self.list_accounts() if item["account_id"] == account_id)
```

### 10.3 Contract: `FakeContentService`

Responsibilities:

- list assets
- list scripts/content drafts
- provide page-ready content summaries

Recommended shape:

```python
class FakeContentService:
    def list_assets(self) -> list[dict]:
        return [
            {
                "asset_id": "asset_001",
                "name": "summer_hook.mp4",
                "kind": "video",
                "duration_sec": 18,
                "status": "ready",
            },
            {
                "asset_id": "asset_002",
                "name": "product_closeup.jpg",
                "kind": "image",
                "duration_sec": None,
                "status": "ready",
            },
        ]

    def list_script_drafts(self) -> list[dict]:
        return [
            {
                "draft_id": "draft_001",
                "title": "3-second hook for hydration bottle",
                "language": "en",
                "status": "approved",
            }
        ]
```

### 10.4 Contract: `FakeAnalyticsService`

Responsibilities:

- dashboard KPIs
- traffic trends
- conversion summaries

Recommended shape:

```python
class FakeAnalyticsService:
    def get_dashboard_metrics(self) -> dict:
        return {
            "accounts_total": 24,
            "ai_tasks_today": 452,
            "videos_processed": 1029,
            "roi_percent": 284,
        }

    def get_traffic_series(self) -> list[dict]:
        return [
            {"label": "Mon", "value": 82},
            {"label": "Tue", "value": 108},
            {"label": "Wed", "value": 72},
        ]
```

### 10.5 Contract: `FakeAIService`

Responsibilities:

- generate scripts/copy
- summarize insights
- return deterministic AI-like responses

Recommended shape:

```python
class FakeAIService:
    def generate_copy(self, product_title: str, tone: str = "professional") -> str:
        return (
            f"{product_title}: a {tone} short-form commerce script focusing on value, trust, and urgency."
        )

    def summarize_metrics(self, metrics: dict) -> str:
        return (
            f"ROI is {metrics['roi_percent']}%, videos processed are {metrics['videos_processed']}, "
            "and the system is healthy for the next campaign window."
        )
```

### 10.6 Usage guidance

Use fake services in two places:

- **Tests**: deterministic fixtures and view-model wiring.
- **Development mode**: unblock UI/page work before real service adapters exist.

---

## 11. `conftest.py` Skeleton

Global fixtures should stay small, composable, and cheap.

Copy-paste-ready skeleton:

```python
# tests/conftest.py
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication


class FakeConfigStore:
    def __init__(self):
        self.data = {}

    def load(self) -> dict:
        return dict(self.data)

    def save(self, values: dict) -> None:
        self.data = dict(values)


class FakeAccountService:
    def list_accounts(self) -> list[dict]:
        return [
            {
                "account_id": "acc_us_001",
                "display_name": "TK_US_Main",
                "region": "US",
                "status": "online",
                "owner": "Amy",
            }
        ]


class FakeContentService:
    def list_assets(self) -> list[dict]:
        return [
            {
                "asset_id": "asset_001",
                "name": "summer_hook.mp4",
                "kind": "video",
                "status": "ready",
            }
        ]


class FakeAnalyticsService:
    def get_dashboard_metrics(self) -> dict:
        return {
            "accounts_total": 24,
            "ai_tasks_today": 452,
            "videos_processed": 1029,
            "roi_percent": 284,
        }


class FakeAIService:
    def generate_copy(self, product_title: str, tone: str = "professional") -> str:
        return f"{product_title} - {tone} conversion copy"


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def fake_config_store():
    return FakeConfigStore()


@pytest.fixture
def fake_account_service():
    return FakeAccountService()


@pytest.fixture
def fake_content_service():
    return FakeContentService()


@pytest.fixture
def fake_analytics_service():
    return FakeAnalyticsService()


@pytest.fixture
def fake_ai_service():
    return FakeAIService()


@pytest.fixture
def sqlite_db_url(tmp_path):
    return f"sqlite:///{tmp_path / 'test.db'}"
```

### Fixture guidance

- `qapp`: one `QApplication` per session.
- `fake_*_service`: default fake service instances.
- `sqlite_db_url`: temp SQLite database for integration tests.
- Add `fake_config_bus` once the config bus exists.
- Add `fake_plugin_registry` once plugin shell work starts.

---

## 12. pytest Configuration

The project can use either `pytest.ini` or `pyproject.toml`. Keep configuration simple and explicit.

### Recommended `pytest.ini`

```ini
[pytest]
minversion = 8.0
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts =
    --tb=short
    --strict-markers
    --strict-config
    --cov=core
    --cov=services
    --cov=models
    --cov=ui
    --cov-report=term-missing
    --cov-report=xml
markers =
    unit: fast isolated tests
    integration: tests using sqlite or real wiring
    widget: PySide6 widget tests
    smoke: shell/page regression tests
qt_api = pyside6
```

### Alternative `pyproject.toml` section

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
python_classes = ["Test*"]
addopts = "--tb=short --strict-markers --strict-config --cov=core --cov=services --cov=models --cov=ui --cov-report=term-missing --cov-report=xml"
markers = [
  "unit: fast isolated tests",
  "integration: tests using sqlite or real wiring",
  "widget: PySide6 widget tests",
  "smoke: shell/page regression tests",
]
qt_api = "pyside6"
```

### Dependency note

Current `desktop_app/requirements.txt` does **not** yet include test dependencies. The project should add them later when TST-01 begins:

```text
pytest
pytest-qt
pytest-cov
mypy
```

`unittest.mock` is included with Python and does not need a separate package.

---

## 13. Naming Conventions

### Test files

- `test_{module}.py`

Examples:

- `test_config_bus.py`
- `test_theme_engine.py`
- `test_account_service.py`
- `test_navigation.py`

### Test functions

- `test_{method}_{scenario}_{expected}`

Examples:

- `test_set_theme_when_dark_mode_selected_emits_signal`
- `test_load_accounts_when_service_returns_data_populates_table`
- `test_save_config_when_store_available_persists_values`

### Fixtures

- snake_case only
- descriptive, not abbreviated unless conventional

Examples:

- `fake_account_service`
- `sqlite_db_url`
- `dashboard_page`
- `sample_product_dto`

### Test data

- Use factories or fixtures.
- Never inline unexplained magic values in multiple tests.
- Prefer named sample objects such as `sample_account`, `sample_campaign`, `sample_product`.

Recommended pattern:

```python
@pytest.fixture
def sample_product():
    return Product(
        id=101,
        title="Hydration Bottle",
        description="Vacuum insulated stainless bottle",
        price=19.99,
        category="Drinkware",
    )
```

---

## 14. Quality Gates

The following are pass/fail criteria for local verification and CI.

### Coverage thresholds

- **Minimum coverage: 60% overall**
- **Minimum coverage: 80% for `core/`**
- **Minimum coverage: 40% for `ui/`**

Why:

- `core/` contains deterministic, critical behavior and should be highly covered.
- `ui/` is harder to cover exhaustively in desktop apps; smoke + widget coverage is acceptable early.

### Mandatory green checks

- All unit tests pass with **zero failures**.
- No type errors.
- Widget smoke tests pass.
- Every page renders without regression.
- Theme switching has no regressions.

### Static typing gate

Run **mypy strict** on:

- `core/`
- `services/`

Recommended future command:

```bash
mypy core services --strict
```

### Coverage enforcement examples

Single threshold:

```bash
pytest --cov=. --cov-fail-under=60
```

Per-area threshold can be enforced in CI with a small coverage script or report parser after XML generation.

---

## 15. CI Integration Notes (Future)

Recommended command baseline:

```bash
pytest --tb=short --strict-markers
```

Recommended CI flow:

1. **unit**
2. **integration**
3. **widget**
4. **smoke**

### Stage details

#### Stage 1: Unit

- run `tests/unit/`
- fastest feedback
- block everything else if red

#### Stage 2: Integration

- run `tests/integration/`
- uses SQLite temp DB
- verifies persistence and service wiring

#### Stage 3: Widget

- run `tests/widgets/`
- uses `pytest-qt`
- can run headless in CI with proper Qt platform setup

#### Stage 4: Smoke

- run `tests/smoke/`
- verify page creation, navigation, and theme switching

### Coverage report generation

Generate:

- terminal missing-lines report for developers
- XML coverage report for CI systems and future dashboards

Recommended command:

```bash
pytest --cov=. --cov-report=term-missing --cov-report=xml
```

### CI environment note for PySide6

For headless CI, set an offscreen platform when needed:

```bash
QT_QPA_PLATFORM=offscreen
```

On Windows runners this may not always be necessary, but the strategy should assume a headless-compatible path.

---

## 16. Minimal Test Roadmap After This Document

This document intentionally does **not** create tests yet. Recommended next implementation sequence for TST-01:

1. Add test dependencies.
2. Add `pytest.ini`.
3. Add `tests/conftest.py`.
4. Add first unit tests for `core/config.py`, `models.py`, and pipeline orchestration.
5. Add first widget smoke test for `MainWindow` page load and theme switching.
6. Add SQLite integration test for `db.py`.

---

## 17. Summary

The TK-OPS desktop app should use a desktop-friendly TDD strategy centered on:

- a **70/20/8/2** pyramid,
- **pytest + pytest-qt** for pragmatic PySide6 coverage,
- **fake services** as shared development contracts,
- **SQLite-backed integration tests** for real persistence confidence,
- and **CI quality gates** that enforce coverage, typing, smoke stability, and theme safety.

This keeps the test system fast enough for daily iteration while still protecting the highest-risk areas of a PySide6 desktop application.
