from __future__ import annotations

import logging
import os
import sys
import traceback
from pathlib import Path

os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-logging --log-level=3")

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

log = logging.getLogger(__name__)

REFERENCE_ONLY_MESSAGE = (
    "REFERENCE ONLY: desktop_app 旧桌面壳不再是默认运行入口。"
    "请改用 apps/desktop 与 apps/py-runtime 对应的新架构链路。"
)


def _global_excepthook(exc_type, exc_value, exc_tb):
    """Catch unhandled exceptions and log them before the process dies."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    log.critical(
        "Unhandled exception\n%s",
        "".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
    )


def main() -> int:
    sys.excepthook = _global_excepthook
    log.warning(REFERENCE_ONLY_MESSAGE)

    from desktop_app.app import build_application

    app, _window = build_application()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
