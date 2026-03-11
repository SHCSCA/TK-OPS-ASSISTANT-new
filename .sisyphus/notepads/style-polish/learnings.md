- MainWindow still hardcodes shell surface colors instead of fully reading theme tokens.
- Shared layout primitives exist, but several key pages still duplicate local frame/title/muted text styling helpers.
- The app already has theme tokens and QSS generation, so style work should prefer centralization over ad hoc page CSS.
- Shell chrome now resolves window/body/text/border colors through dedicated shell theme tokens and a ThemeEngine helper, keeping light/dark propagation unchanged while removing MainWindow hardcoded surfaces.
- Shared label/panel helper rules were centralized in `desktop_app/ui/components/layouts.py` so key page typography and card shells reuse the same QSS primitives.
- `dashboard/page.py`, `ai/script_generation_page.py`, and `system/ai_provider_page.py` now consume those shared helpers instead of repeating page-local label/frame style helpers and duplicated stylesheet fragments.
- Python 3.8 test compatibility may require importing `Callable`/generic aliases from `typing`, and tests can locally patch a module's `Mapping` alias to `typing.Mapping` when production code uses subscripted mapping casts with a `collections.abc.Mapping` import.
- For Python 3.8 pytest collection compatibility, keep test-side `Callable` type aliases based on `typing` generics (`Dict`, `Optional`) instead of builtin generic syntax inside `cast(...)` signatures.
- Title bar polish landed best by framing brand, page title, and right actions as token-driven subpanels instead of a flat utility row, which made the shell read closer to a mature desktop product without changing behavior.
- Reusing existing surface/border/brand tokens plus restrained accent alpha states was enough to upgrade search, utility buttons, and avatar presence while keeping the shell crisp and consistent with the refined sidebar.
- Status bar polish works best when connection, message, and meta zones are framed as low-contrast token-driven subpanels with slightly stronger emphasis on live state and time, preserving behavior while making the shell footer feel intentionally segmented.

## Qt Fallback Implementation Completion

### Task Completed
Completed supplementing `desktop_app/core/qt.py` with missing Qt fallback methods to resolve smoke test failures.

### Changes Made
1. **Added to `QWidget` class:**
   - `_object_name: str` field to track widget names
   - `setObjectName(name: str)` method - stores the widget name
   - `objectName() -> str` method - returns the stored widget name

2. **Added to `_BaseLayout` class:**
   - `count() -> int` method - returns number of items in layout
   - `itemAt(index: int) -> object | None` method - returns layout item at index wrapped in `_FakeLayoutItem`
   - `removeWidget(widget: QWidget) -> None` method - removes widget from layout

3. **Created new `_FakeLayoutItem` class:**
   - Wrapper for layout items with `widget() -> QWidget | None` method
   - Enables proper layout item querying

### Implementation Pattern
Followed existing fallback convention:
- No-op implementations return None or safe defaults
- Methods store state internally in private attributes
- Type annotations match real Qt API signatures

### Test Results
- `test_blue_ocean_page_instantiates` - PASSED (was failing with AttributeError: 'QHBoxLayout' object has no attribute 'count')
- `test_dashboard_page_instantiates` - PASSED
- All related smoke tests functional

### Why This Works
The fallback implementation only needs to satisfy the Python API contract that pages call. Since pages in this environment have PySide6 installed during test runs, the real Qt classes are used. The fallback implementations are only used in non-GUI test environments (like import checks in CI) and in minimal smoke test scenarios where layout queries occur.
