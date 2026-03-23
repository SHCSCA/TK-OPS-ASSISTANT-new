from __future__ import annotations

from pathlib import Path

from sqlalchemy import text

from desktop_app.database import SessionLocal
from desktop_app.database.models import Task
from desktop_app.database.repository import Repository


def test_list_tasks_tolerates_legacy_task_type_value() -> None:
    session = SessionLocal()
    repo = Repository(session=session)

    try:
        session.execute(text("DELETE FROM tasks"))
        session.commit()

        session.execute(
            text(
                """
                INSERT INTO tasks (title, task_type, priority, status)
                VALUES (:title, :task_type, :priority, :status)
                """
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

        assert len(tasks) == 1
        assert tasks[0].title == "legacy analytics task"
        assert tasks[0].task_type == "analytics_action"
    finally:
        session.execute(text("DELETE FROM tasks WHERE title = :title"), {"title": "legacy analytics task"})
        session.commit()
        session.close()
