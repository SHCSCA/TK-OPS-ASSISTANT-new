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


def test_list_tasks_tolerates_legacy_task_type_value() -> None:
    result = _run_isolated_script(
        """
import json
from sqlalchemy import text
from desktop_app.database import SessionLocal
from desktop_app.database.models import Task
from desktop_app.database.repository import Repository

session = SessionLocal()
repo = Repository(session=session)

try:
    session.execute(text("DELETE FROM tasks"))
    session.commit()

    session.execute(
        text(
            'INSERT INTO tasks (title, task_type, priority, status) '
            'VALUES (:title, :task_type, :priority, :status)'
        ),
        {
            "title": "legacy analytics task",
            "task_type": "analytics_action",
            "priority": "medium",
            "status": "pending",
        },
    )
    session.commit()

    tasks = repo.list_tasks()

    print(json.dumps({
        'count': len(tasks),
        'title': tasks[0].title if tasks else None,
        'task_type': tasks[0].task_type if tasks else None,
    }, ensure_ascii=False))
finally:
    session.execute(text("DELETE FROM tasks WHERE title = :title"), {"title": "legacy analytics task"})
    session.commit()
    session.close()
"""
    )

    assert result["count"] == 1
    assert result["title"] == "legacy analytics task"
    assert result["task_type"] == "analytics_action"
