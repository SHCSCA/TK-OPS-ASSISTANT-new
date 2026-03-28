from __future__ import annotations

import subprocess
from pathlib import Path


def _git_check_ignore(repo_root: Path, path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", path],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def test_temp_artifacts_are_ignored_while_sample_data_db_stays_allowed() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    assert _git_check_ignore(repo_root, ".tmp_runtime/probe.db-wal")
    assert _git_check_ignore(repo_root, "nested/.tmp_candidate.js")
    assert not _git_check_ignore(repo_root, "sample_data/probe.db")
    assert (repo_root / "sample_data" / "tk_ops_test_seed.db").exists()
