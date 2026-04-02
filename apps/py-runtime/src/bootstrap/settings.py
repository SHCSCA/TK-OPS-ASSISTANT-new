from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from desktop_app.database import DATA_DIR


def _read_env_text(name: str, default: str) -> str:
    value = os.environ.get(name, default).strip()
    return value or default


def _read_env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    return int(value)


def _read_env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_log_level(value: str) -> str:
    normalized = value.strip().upper()
    if normalized not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError(f"不支持的日志级别: {value}")
    return normalized


def _resolve_runtime_data_dir() -> Path:
    # 优先尊重当前进程环境变量，避免模块导入时就把目录冻结死。
    explicit = os.environ.get("TK_OPS_DATA_DIR")
    if explicit:
        return Path(explicit)
    return DATA_DIR


@dataclass(slots=True)
class RuntimeSettings:
    # 统一收口 runtime 运行期全局配置，避免模块各自读取环境变量。
    host: str
    port: int
    session_token: str
    environment: str
    data_dir: Path
    log_dir: Path
    log_file: Path
    log_level: str
    enable_request_logging: bool


def load_settings() -> RuntimeSettings:
    data_dir = _resolve_runtime_data_dir()
    log_dir = data_dir / "logs"
    return RuntimeSettings(
        host=_read_env_text("TKOPS_RUNTIME_HOST", "127.0.0.1"),
        port=_read_env_int("TKOPS_RUNTIME_PORT", 8765),
        session_token=_read_env_text("TKOPS_RUNTIME_TOKEN", "dev-token"),
        environment=_read_env_text("TKOPS_RUNTIME_ENV", "development"),
        data_dir=data_dir,
        log_dir=log_dir,
        log_file=log_dir / "runtime.log",
        log_level=_normalize_log_level(_read_env_text("TKOPS_LOG_LEVEL", "INFO")),
        enable_request_logging=_read_env_bool("TKOPS_RUNTIME_REQUEST_LOGGING", True),
    )