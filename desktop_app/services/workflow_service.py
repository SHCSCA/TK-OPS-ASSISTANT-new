"""Workflow definition and run persistence service."""
from __future__ import annotations

from typing import Any, Sequence

from desktop_app.database.models import WorkflowDefinition, WorkflowRun
from desktop_app.database.repository import Repository


class WorkflowService:
    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    def create_workflow_definition(self, name: str, **kwargs: Any) -> WorkflowDefinition:
        return self._repo.add(WorkflowDefinition(name=name, **kwargs))

    def list_workflow_definitions(self) -> Sequence[WorkflowDefinition]:
        return self._repo.list_workflow_definitions()

    def create_workflow_run(self, workflow_definition_id: int, **kwargs: Any) -> WorkflowRun:
        return self._repo.add(
            WorkflowRun(workflow_definition_id=workflow_definition_id, **kwargs)
        )

    def list_workflow_runs(
        self, workflow_definition_id: int | None = None
    ) -> Sequence[WorkflowRun]:
        return self._repo.list_workflow_runs(workflow_definition_id=workflow_definition_id)
