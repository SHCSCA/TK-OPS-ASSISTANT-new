"""Report persistence service."""
from __future__ import annotations

from typing import Any, Sequence

from desktop_app.database.models import ReportRun
from desktop_app.database.repository import Repository


class ReportService:
    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    def create_report_run(self, title: str, **kwargs: Any) -> ReportRun:
        return self._repo.add(ReportRun(title=title, **kwargs))

    def list_report_runs(self) -> Sequence[ReportRun]:
        return self._repo.list_report_runs()
