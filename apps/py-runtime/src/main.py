from __future__ import annotations

import logging
import sys
from pathlib import Path

import uvicorn


def _discover_runtime_root() -> Path:
    entry = Path(__file__).resolve()
    for candidate in (entry.parent, *entry.parents):
        if (candidate / "desktop_app").is_dir():
            return candidate
    return entry.parent


def _ensure_runtime_root_on_path() -> None:
    runtime_root = _discover_runtime_root()
    runtime_root_str = str(runtime_root)
    if runtime_root_str not in sys.path:
        sys.path.insert(0, runtime_root_str)


_ensure_runtime_root_on_path()

from bootstrap.app_factory import build_app
from bootstrap.container import build_container

log = logging.getLogger(__name__)


def main() -> None:
    container = build_container()
    container.observability_initializer(container.runtime_settings)
    log.info(
        "准备启动 TK-OPS Runtime: env=%s host=%s port=%s",
        container.runtime_settings.environment,
        container.runtime_settings.host,
        container.runtime_settings.port,
    )
    app = build_app(container)
    uvicorn.run(
        app,
        host=container.runtime_settings.host,
        port=container.runtime_settings.port,
    )


if __name__ == "__main__":
    main()
