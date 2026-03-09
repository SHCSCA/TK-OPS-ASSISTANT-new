from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


TEST_FILE = Path(__file__).resolve()
DESKTOP_APP_ROOT = TEST_FILE.parents[2]
PROJECT_ROOT = TEST_FILE.parents[3]
REQUIREMENTS_FILE = DESKTOP_APP_ROOT / "requirements.txt"
REQUIRED_DOCUMENTATION_FILES = (
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "docs" / "PRD.md",
    PROJECT_ROOT / "docs" / "UI-DESIGN-PRD.md",
    PROJECT_ROOT / "docs" / "planning" / "PLN-01-page-inventory.md",
    PROJECT_ROOT / "docs" / "planning" / "PLN-02-information-architecture.md",
    PROJECT_ROOT / "docs" / "planning" / "PLN-03-tdd-strategy.md",
    PROJECT_ROOT / "docs" / "planning" / "PLN-04-design-tokens.md",
)
DOCUMENTATION_LINE_THRESHOLDS = {
    PROJECT_ROOT / "README.md": 500,
    PROJECT_ROOT / "docs" / "PRD.md": 1000,
    PROJECT_ROOT / "docs" / "UI-DESIGN-PRD.md": 1500,
}

# Directories to always exclude from file scanning
_EXCLUDED_DIR_NAMES = {"__pycache__", "venv", ".venv"}


def _iter_python_files(root: Path) -> list[Path]:
    """Recursively find all .py files, excluding cache and venv dirs."""
    return sorted(
        path
        for path in root.rglob("*.py")
        if not _EXCLUDED_DIR_NAMES.intersection(path.parts)
    )


def _top_level_modules() -> list[str]:
    """Discover all importable top-level desktop_app modules."""
    module_names: list[str] = []

    for file_path in sorted(DESKTOP_APP_ROOT.glob("*.py")):
        if file_path.name == "__init__.py":
            continue
        module_names.append(f"desktop_app.{file_path.stem}")

    for child_path in sorted(DESKTOP_APP_ROOT.iterdir()):
        if not child_path.is_dir() or child_path.name in _EXCLUDED_DIR_NAMES:
            continue
        if child_path.name.startswith((".", "_")):
            continue
        if any(path.suffix == ".py" for path in child_path.rglob("*.py")):
            module_names.append(f"desktop_app.{child_path.name}")

    return list(dict.fromkeys(module_names))


def _page_modules() -> list[str]:
    """Discover all page module dotted names under desktop_app/ui/pages/."""
    pages_root = DESKTOP_APP_ROOT / "ui" / "pages"
    module_names: list[str] = []

    for file_path in sorted(pages_root.rglob("*.py")):
        if file_path.name in {"__init__.py", "base_page.py"}:
            continue
        module_name = (
            file_path.relative_to(PROJECT_ROOT)
            .with_suffix("")
            .as_posix()
            .replace("/", ".")
        )
        module_names.append(module_name)

    return module_names


def _line_count(file_path: Path) -> int:
    with file_path.open("r", encoding="utf-8") as handle:
        return sum(1 for _ in handle)


def _run_python(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def _assert_subprocess_ok(result: subprocess.CompletedProcess[str], context: str) -> None:
    message = "\n".join(
        (
            f"{context} failed with exit code {result.returncode}.",
            "STDOUT:",
            result.stdout or "<empty>",
            "STDERR:",
            result.stderr or "<empty>",
        )
    )

    if result.returncode != 0:
        pytest.fail(message)


# ---------------------------------------------------------------------------
# Test: All Python files compile without syntax errors
# ---------------------------------------------------------------------------


def test_all_python_files_compile() -> None:
    """Run py_compile on every .py file under desktop_app/."""
    python_files = _iter_python_files(DESKTOP_APP_ROOT)

    assert python_files, "No Python files were found under desktop_app/."

    code = """
import py_compile
from pathlib import Path

files = __FILES__
failures = []

for raw_path in files:
    path = Path(raw_path)
    try:
        py_compile.compile(str(path), doraise=True)
        print(f"OK::{path}")
    except Exception as exc:
        failures.append((str(path), str(exc)))
        print(f"FAIL::{path}::{exc}")

print(f"TOTAL::{len(files)}")
print(f"FAILURES::{len(failures)}")
raise SystemExit(1 if failures else 0)
""".replace("__FILES__", repr([str(path) for path in python_files]))

    result = _run_python(code)
    _assert_subprocess_ok(result, "Full py_compile sweep")


# ---------------------------------------------------------------------------
# Test: No circular imports at the top-level package boundary
# ---------------------------------------------------------------------------


def test_no_circular_imports() -> None:
    """Import every top-level desktop_app sub-package; no ImportError allowed."""
    modules = _top_level_modules()

    assert modules, "No top-level desktop_app modules were discovered."

    code = """
import importlib
import sys
from pathlib import Path

project_root = Path(__PROJECT_ROOT__)
sys.path.insert(0, str(project_root))
modules = __MODULES__
failures = []

for module_name in modules:
    try:
        importlib.import_module(module_name)
        print(f"OK::{module_name}")
    except BaseException as exc:
        failures.append((module_name, type(exc).__name__, str(exc)))
        print(f"FAIL::{module_name}::{type(exc).__name__}::{exc}")

print(f"TOTAL::{len(modules)}")
print(f"FAILURES::{len(failures)}")
raise SystemExit(1 if failures else 0)
""".replace("__PROJECT_ROOT__", repr(str(PROJECT_ROOT))).replace(
        "__MODULES__", repr(modules)
    )

    result = _run_python(code)
    _assert_subprocess_ok(result, "Top-level import validation")


# ---------------------------------------------------------------------------
# Test: Every page module under ui/pages/ is individually importable
# ---------------------------------------------------------------------------


def test_all_page_modules_importable() -> None:
    """Import each page module individually to validate import chains."""
    modules = _page_modules()

    assert modules, "No page modules were discovered under desktop_app/ui/pages/."

    code = """
import importlib
import sys
from pathlib import Path

project_root = Path(__PROJECT_ROOT__)
sys.path.insert(0, str(project_root))
modules = __MODULES__
failures = []

for module_name in modules:
    try:
        importlib.import_module(module_name)
        print(f"OK::{module_name}")
    except BaseException as exc:
        failures.append((module_name, type(exc).__name__, str(exc)))
        print(f"FAIL::{module_name}::{type(exc).__name__}::{exc}")

print(f"TOTAL::{len(modules)}")
print(f"FAILURES::{len(failures)}")
raise SystemExit(1 if failures else 0)
""".replace("__PROJECT_ROOT__", repr(str(PROJECT_ROOT))).replace(
        "__MODULES__", repr(modules)
    )

    result = _run_python(code)
    _assert_subprocess_ok(result, "Page module import validation")


# ---------------------------------------------------------------------------
# Test: All required documentation files exist
# ---------------------------------------------------------------------------


def test_documentation_files_exist() -> None:
    """Verify every required documentation file is present on disk."""
    missing_files = [str(path) for path in REQUIRED_DOCUMENTATION_FILES if not path.exists()]
    assert not missing_files, f"Missing documentation files: {missing_files}"


# ---------------------------------------------------------------------------
# Test: Documentation files meet minimum line-count thresholds
# ---------------------------------------------------------------------------


def test_documentation_line_counts_meet_thresholds() -> None:
    """Ensure key docs are substantive, not just stubs."""
    failures: list[str] = []

    for file_path, minimum_lines in DOCUMENTATION_LINE_THRESHOLDS.items():
        if not file_path.exists():
            failures.append(f"{file_path} does not exist.")
            continue
        actual_lines = _line_count(file_path)
        if actual_lines <= minimum_lines:
            failures.append(f"{file_path} has {actual_lines} lines; expected > {minimum_lines}.")

    assert not failures, "\n".join(failures)


# ---------------------------------------------------------------------------
# Test: Requirements file exists
# ---------------------------------------------------------------------------


def test_requirements_file_exists() -> None:
    """Confirm desktop_app/requirements.txt is present."""
    assert REQUIREMENTS_FILE.exists(), f"Requirements file is missing: {REQUIREMENTS_FILE}"


# ---------------------------------------------------------------------------
# Test: Minimum expected file count to catch accidental mass deletions
# ---------------------------------------------------------------------------


def test_minimum_python_file_count() -> None:
    """Guard against accidental mass deletions by asserting a floor on .py count."""
    python_files = _iter_python_files(DESKTOP_APP_ROOT)
    assert len(python_files) >= 100, (
        f"Expected at least 100 .py files under desktop_app/, found {len(python_files)}. "
        "This may indicate accidental file deletion."
    )
