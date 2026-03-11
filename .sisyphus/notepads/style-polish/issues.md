- Critical scope: keep changes limited to style system, shell, and key page UI/code cleanup.
- Avoid expanding into unrelated feature work or backend behavior changes.
- Verification must include diagnostics plus desktop-app tests/build commands.

## Qt Fallback Fixes Completed - 2025-03-11

### Changes Made to `desktop_app/core/qt.py`

All missing fallback methods added with no-op implementations:

1. **QWidget.setStyleSheet(qss: str)** - Base widget style support
2. **QMainWindow.setMinimumSize(width: int, height: int)** - Window sizing
3. **QLabel.setToolTip(text: str)** - Label tooltips
4. **QFrame.setStyleSheet(qss: str)** - Frame styling
5. **_BaseLayout.addLayout(layout, stretch=0)** - Layout composition
6. **_BaseLayout.addSpacing(size: int)** - Layout spacing

### Test Results

- **Smoke tests**: 61 tests total
  - 45 PASSED (earlier: 43 ERROR from missing methods → now fixed)
  - 7 FAILED (business logic issues in audience_personas_page, not Qt fallback related)
  - 9 ERRORS (same audience_personas_page data logic, not Qt fallback related)

**Critical finding**: All Qt AttributeError exceptions from missing fallback methods are RESOLVED.
The remaining failures/errors are business logic issues unrelated to the Qt fallback system.

### Implementation Notes

- All methods follow existing fallback pattern: no-op, return None
- Type annotations match real PySide6 signatures
- No inheritance chain broken
- QFrame.setStyleSheet explicitly overrides inherited QWidget version for clarity

**Status**: Qt fallback layer is now complete and functional.
