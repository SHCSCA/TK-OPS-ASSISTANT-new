from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler

from bootstrap.settings import RuntimeSettings

MAX_BYTES = 10 * 1024 * 1024
BACKUP_COUNT = 5
_FMT = "[%(asctime)s] %(levelname)-8s %(name)s %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"
_FILE_HANDLER_NAME = "tkops-runtime-file"
_CONSOLE_HANDLER_NAME = "tkops-runtime-console"


def setup_runtime_logging(settings: RuntimeSettings) -> None:
    """初始化 runtime 全局日志。

    该方法要求可重复调用，避免启动链路和测试链路重复注入 handler。
    """
    root = logging.getLogger()
    root.setLevel(getattr(logging, settings.log_level))

    existing_handler_names = {handler.get_name() for handler in root.handlers}
    formatter = logging.Formatter(_FMT, datefmt=_DATE_FMT)

    if _FILE_HANDLER_NAME not in existing_handler_names:
        settings.log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            settings.log_file,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.set_name(_FILE_HANDLER_NAME)
        file_handler.setLevel(getattr(logging, settings.log_level))
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    if _CONSOLE_HANDLER_NAME not in existing_handler_names:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.set_name(_CONSOLE_HANDLER_NAME)
        console_handler.setLevel(
            logging.DEBUG if settings.environment == "development" else getattr(logging, settings.log_level)
        )
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)

    # 控制第三方日志噪音，确保关键业务日志可读。
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
