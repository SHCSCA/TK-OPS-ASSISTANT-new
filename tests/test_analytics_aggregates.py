from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_JS = ROOT / "desktop_app" / "assets" / "js" / "data.js"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
BRIDGE_PY = ROOT / "desktop_app" / "ui" / "bridge.py"


def _run_isolated_script(script: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temp_dir:
        env = os.environ.copy()
        env["TK_OPS_DATA_DIR"] = temp_dir
        output = subprocess.check_output(
            [sys.executable, "-c", script],
            cwd=str(ROOT),
            env=env,
            text=True,
        )
    return json.loads(output.strip().splitlines()[-1])


def test_analytics_service_builds_real_summary_conversion_and_persona_views() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService
from desktop_app.services.ai_service import AIService
from desktop_app.services.analytics_service import AnalyticsService
from desktop_app.services.asset_service import AssetService
from desktop_app.services.task_service import TaskService

repo = Repository()
accounts = AccountService(repo)
providers = AIService(repo)
assets = AssetService(repo)
tasks = TaskService(repo)
analytics = AnalyticsService(repo)

accounts.create_account('alpha_us', region='US', followers=1200, status='active')
accounts.create_account('beta_de', region='DE', followers=3400, status='warming')
providers.create_provider('Primary OpenAI', provider_type='openai', default_model='gpt-4o', is_active=True)
assets.create_asset('hero.png', asset_type='image', file_path='C:/seed/hero.png', file_size=100)
assets.create_asset('hook.mp4', asset_type='video', file_path='C:/seed/hook.mp4', file_size=200)
tasks.create_task('Weekly report', task_type='report', status='completed')
tasks.create_task('Content publish', task_type='publish', status='running')

summary = analytics.get_analytics_summary()
conversion = analytics.get_conversion_analysis()
persona = analytics.get_persona_analysis()

print(json.dumps({
    'accounts_total': summary['accounts']['total'],
    'providers_active': summary['providers']['active'],
    'asset_types': summary['assets']['by_type'],
    'conversion_funnel': [step['key'] for step in conversion['funnel']],
    'conversion_completed': conversion['counts']['completed_tasks'],
    'persona_segments': [segment['key'] for segment in persona['segments']],
    'top_region': persona['regions'][0]['key'],
}, ensure_ascii=False))
"""
    )
    assert result['accounts_total'] == 2
    assert result['providers_active'] == 1
    assert result['asset_types']['image'] == 1
    assert result['asset_types']['video'] == 1
    assert result['conversion_funnel'] == ['accounts', 'active_accounts', 'tasks', 'completed_tasks', 'assets']
    assert result['conversion_completed'] == 1
    assert 'high_value' in result['persona_segments']
    assert result['top_region'] == 'DE'


def test_bridge_and_frontend_expose_real_analytics_aggregate_surface() -> None:
    bridge_text = BRIDGE_PY.read_text(encoding='utf-8')
    assert 'def getAnalyticsSummary(' in bridge_text
    assert 'def getConversionAnalysis(' in bridge_text
    assert 'def getPersonaAnalysis(' in bridge_text

    data_text = DATA_JS.read_text(encoding='utf-8')
    assert 'analytics:' in data_text
    assert "callBackend('getAnalyticsSummary')" in data_text
    assert "callBackend('getConversionAnalysis')" in data_text
    assert "callBackend('getPersonaAnalysis')" in data_text


def test_analytics_pages_consume_backend_aggregate_apis() -> None:
    text = PAGE_LOADERS_JS.read_text(encoding='utf-8')
    required = [
        'api.analytics.summary()',
        'api.analytics.conversion()',
        'api.analytics.persona()',
    ]
    for marker in required:
        assert marker in text, marker
