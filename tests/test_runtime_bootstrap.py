from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_SRC = ROOT / "apps" / "py-runtime" / "src"

if str(RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(RUNTIME_SRC))

from bootstrap.logging import setup_runtime_logging
from bootstrap.settings import load_settings


def test_load_settings_supports_global_runtime_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("TK_OPS_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("TKOPS_RUNTIME_HOST", "0.0.0.0")
    monkeypatch.setenv("TKOPS_RUNTIME_PORT", "9001")
    monkeypatch.setenv("TKOPS_RUNTIME_TOKEN", "token-x")
    monkeypatch.setenv("TKOPS_RUNTIME_ENV", "staging")
    monkeypatch.setenv("TKOPS_LOG_LEVEL", "debug")
    monkeypatch.setenv("TKOPS_RUNTIME_REQUEST_LOGGING", "false")

    settings = load_settings()

    assert settings.host == "0.0.0.0"
    assert settings.port == 9001
    assert settings.session_token == "token-x"
    assert settings.environment == "staging"
    assert settings.data_dir == tmp_path
    assert settings.log_dir == tmp_path / "logs"
    assert settings.log_file == tmp_path / "logs" / "runtime.log"
    assert settings.log_level == "DEBUG"
    assert settings.enable_request_logging is False


def test_setup_runtime_logging_creates_runtime_log_file(tmp_path: Path) -> None:
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    for handler in list(root.handlers):
        root.removeHandler(handler)

    try:
        settings = load_settings()
        settings.log_dir = tmp_path / "logs"
        settings.log_file = settings.log_dir / "runtime.log"
        settings.environment = "test"
        settings.log_level = "INFO"

        setup_runtime_logging(settings)
        logging.getLogger("tests.runtime").info("runtime logging smoke test")

        assert settings.log_file.exists()
        assert "runtime logging smoke test" in settings.log_file.read_text(encoding="utf-8")
    finally:
        for handler in list(root.handlers):
            handler.close()
            root.removeHandler(handler)
        root.setLevel(original_level)
        for handler in original_handlers:
            root.addHandler(handler)