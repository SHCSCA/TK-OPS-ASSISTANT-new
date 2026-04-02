from __future__ import annotations

import logging
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Callable

from desktop_app.database import DB_PATH, init_db
from desktop_app.version import APP_VERSION

from bootstrap.logging import setup_runtime_logging
from bootstrap.settings import RuntimeSettings, load_settings
from legacy_adapter.facade import LegacyRuntimeFacade

log = logging.getLogger(__name__)


@dataclass(slots=True)
class RuntimeContainer:
    app_version: str
    db_path: Path
    runtime_settings: RuntimeSettings
    legacy_facade: LegacyRuntimeFacade
    initializer: Callable[[], None]
    observability_initializer: Callable[[RuntimeSettings], None] = field(
        default=lambda _settings: None
    )

    def initialize(self) -> None:
        self.observability_initializer(self.runtime_settings)
        self.initializer()
        log.info(
            "Runtime 初始化完成: env=%s db=%s log=%s",
            self.runtime_settings.environment,
            self.db_path,
            self.runtime_settings.log_file,
        )


def build_container() -> RuntimeContainer:
    settings = load_settings()
    return RuntimeContainer(
        app_version=APP_VERSION,
        db_path=DB_PATH,
        runtime_settings=settings,
        legacy_facade=LegacyRuntimeFacade(),
        initializer=init_db,
        observability_initializer=setup_runtime_logging,
    )