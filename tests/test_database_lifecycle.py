from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run_isolated_script(script: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temp_dir:
        env = os.environ.copy()
        env["TK_OPS_DATA_DIR"] = temp_dir
        env["PYTHONIOENCODING"] = "utf-8"
        output = subprocess.check_output(
            [sys.executable, "-c", script],
            cwd=str(ROOT),
            env=env,
            text=True,
            encoding="utf-8",
        )
    return json.loads(output.strip().splitlines()[-1])


def test_database_import_does_not_create_the_database_file() -> None:
    result = _run_isolated_script(
        """
import json
from pathlib import Path
import desktop_app.database as db

print(json.dumps({
    'exists': Path(db.DB_PATH).exists(),
}, ensure_ascii=False))
"""
    )

    assert result["exists"] is False


def test_sessionlocal_initializes_the_database_on_demand() -> None:
    result = _run_isolated_script(
        """
import json
import sqlite3
from pathlib import Path
from sqlalchemy import text
from desktop_app.database import DB_PATH, SessionLocal

session = SessionLocal()
try:
    session.execute(text("SELECT 1"))
finally:
    session.close()

conn = sqlite3.connect(DB_PATH)
try:
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
finally:
    conn.close()

print(json.dumps({
    'exists': Path(DB_PATH).exists(),
    'has_alembic_version': 'alembic_version' in tables,
}, ensure_ascii=False))
"""
    )

    assert result["exists"] is True
    assert result["has_alembic_version"] is True


def test_bridge_resets_repository_session_after_each_slot() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.ui.bridge import Bridge

bridge = Bridge()
first_session_id = id(bridge._repo.session)
bridge.listDevices()
second_session_id = id(bridge._repo.session)
bridge.listAccounts()
third_session_id = id(bridge._repo.session)

print(json.dumps({
    'changed_after_first_call': first_session_id != second_session_id,
    'changed_after_second_call': second_session_id != third_session_id,
}, ensure_ascii=False))
"""
    )

    assert result["changed_after_first_call"] is True
    assert result["changed_after_second_call"] is True
