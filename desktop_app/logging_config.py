"""Structured logging – rotating file + console.

Log directory: %APPDATA%/TK-OPS-ASSISTANT/logs/
Files:         app.log (10 MB × 5 rotations)
"""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from desktop_app.database import DATA_DIR

LOG_DIR = DATA_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5

_FMT = "[%(asctime)s] %(levelname)-8s %(name)s  %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def setup_logging(*, level: int = logging.INFO) -> None:
    """Configure root logger with file + stderr handlers.

    Safe to call multiple times – handlers are only added once.
    """
    root = logging.getLogger()
    if root.handlers:
        return  # already configured

    root.setLevel(level)
    formatter = logging.Formatter(_FMT, datefmt=_DATE_FMT)

    # ── File handler (always INFO+) ──
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    fh = RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
    )
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    root.addHandler(fh)

    # ── Console handler (DEBUG in dev, WARNING in frozen) ──
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.DEBUG if not getattr(sys, "frozen", False) else logging.WARNING)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # Quieten noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
