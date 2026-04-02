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
_ = bridge._repo.session
bridge.listDevices()
session_cleared_after_first_call = bridge._repo._session is None
_ = bridge._repo.session
bridge.listAccounts()
session_cleared_after_second_call = bridge._repo._session is None

print(json.dumps({
    'session_cleared_after_first_call': session_cleared_after_first_call,
    'session_cleared_after_second_call': session_cleared_after_second_call,
}, ensure_ascii=False))
"""
    )

    assert result["session_cleared_after_first_call"] is True
    assert result["session_cleared_after_second_call"] is True


def test_repository_init_stays_lazy_until_a_session_is_needed() -> None:
    result = _run_isolated_script(
        """
import json
from pathlib import Path
from desktop_app.database import DB_PATH
from desktop_app.database.repository import Repository
from sqlalchemy import text

repo = Repository()
exists_after_init = Path(DB_PATH).exists()
_ = repo.session.execute(text("SELECT 1")).scalar()
exists_after_first_query = Path(DB_PATH).exists()
repo.close()

print(json.dumps({
    'exists_after_init': exists_after_init,
    'exists_after_first_query': exists_after_first_query,
}, ensure_ascii=False))
"""
    )

    assert result["exists_after_init"] is False
    assert result["exists_after_first_query"] is True


def test_init_db_recovers_from_precreated_video_tables_before_head_revision() -> None:
    result = _run_isolated_script(
        """
import json
import sqlite3
from desktop_app.database import DB_PATH, init_db

conn = sqlite3.connect(DB_PATH)
try:
    conn.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
    conn.execute("INSERT INTO alembic_version(version_num) VALUES ('91c9d4b7e2aa')")
    conn.execute("CREATE TABLE assets (id INTEGER PRIMARY KEY AUTOINCREMENT)")
    conn.execute("CREATE TABLE video_projects (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(160) NOT NULL)")
    conn.commit()
finally:
    conn.close()

init_db()

conn = sqlite3.connect(DB_PATH)
try:
    revision = conn.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
finally:
    conn.close()

print(json.dumps({
    'revision': revision,
    'has_video_projects': 'video_projects' in tables,
    'has_video_sequences': 'video_sequences' in tables,
    'has_video_exports': 'video_exports' in tables,
}, ensure_ascii=False))
"""
    )

    assert result["revision"] == "c8f4a7b2d901"
    assert result["has_video_projects"] is True
    assert result["has_video_sequences"] is True
    assert result["has_video_exports"] is True
