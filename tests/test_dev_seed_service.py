from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEV_SEED_SERVICE_PY = ROOT / 'desktop_app' / 'services' / 'dev_seed_service.py'
BRIDGE_PY = ROOT / 'desktop_app' / 'ui' / 'bridge.py'
BRIDGE_JS = ROOT / 'desktop_app' / 'assets' / 'js' / 'bridge.js'


def _run_isolated_script(script: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temp_dir:
        env = os.environ.copy()
        env['TK_OPS_DATA_DIR'] = temp_dir
        output = subprocess.check_output(
            [sys.executable, '-c', script],
            cwd=str(ROOT),
            env=env,
            text=True,
        )
    return json.loads(output.strip().splitlines()[-1])


def test_dev_seed_service_populates_real_tables_and_is_idempotent() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.models import ActivityLog, AnalysisSnapshot, ReportRun, WorkflowDefinition, WorkflowRun, ExperimentView
from desktop_app.database.repository import Repository
from desktop_app.services.dev_seed_service import DevSeedService

repo = Repository()
service = DevSeedService(repo)
first = service.seed_development_data()
second = service.seed_development_data()
print(json.dumps({
    'first_accounts': first['counts']['accounts'],
    'first_tasks': first['counts']['tasks'],
    'first_assets': first['counts']['assets'],
    'second_created': second['created'],
    'providers': second['counts']['providers'],
    'experiments': second['counts']['experiment_projects'],
    'activity_logs': repo.count(ActivityLog),
    'snapshots': repo.count(AnalysisSnapshot),
    'report_runs': repo.count(ReportRun),
    'workflow_definitions': repo.count(WorkflowDefinition),
    'workflow_runs': repo.count(WorkflowRun),
    'experiment_views': repo.count(ExperimentView),
}, ensure_ascii=False))
"""
    )
    assert int(result['first_accounts']) >= 2
    assert int(result['first_tasks']) >= 2
    assert int(result['first_assets']) >= 2
    assert int(result['providers']) >= 1
    assert int(result['experiments']) >= 1
    assert int(result['activity_logs']) >= 3
    assert int(result['snapshots']) >= 3
    assert int(result['report_runs']) >= 2
    assert int(result['workflow_definitions']) >= 2
    assert int(result['workflow_runs']) >= 2
    assert int(result['experiment_views']) >= 2
    assert result['second_created'] == 0


def test_bridge_exposes_manual_dev_seed_entrypoint() -> None:
    assert DEV_SEED_SERVICE_PY.exists(), DEV_SEED_SERVICE_PY

    bridge_text = BRIDGE_PY.read_text(encoding='utf-8')
    assert 'def runDevSeed(' in bridge_text

    bridge_stub_text = BRIDGE_JS.read_text(encoding='utf-8')
    assert 'runDevSeed:' in bridge_stub_text
