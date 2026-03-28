from __future__ import annotations

import logging
import sys
import threading
from pathlib import Path
from time import perf_counter

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from desktop_app.logging_config import setup_logging

log = logging.getLogger(__name__)

if getattr(sys, "frozen", False):
    _ASSETS = Path(sys._MEIPASS) / "desktop_app" / "assets"
else:
    _ASSETS = Path(__file__).resolve().parent / "assets"


def _warm_up_database() -> None:
    started = perf_counter()
    try:
        from desktop_app.database import init_db

        init_db()
        log.info("Database warm-up finished in %.0f ms", (perf_counter() - started) * 1000)
    except Exception:
        log.critical("Database warm-up failed", exc_info=True)


def build_application():
    boot_started = perf_counter()
    setup_logging()
    log.info("Application starting")

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("TK-OPS 杩愯惀鍔╂墜")
    app.setOrganizationName("TK-OPS")
    app.setQuitOnLastWindowClosed(True)

    splash_path = _ASSETS / "splash.png"
    splash = None
    if splash_path.exists():
        pixmap = QPixmap(str(splash_path))
        splash = QSplashScreen(pixmap, Qt.WindowType.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()
        splash.showMessage(
            "Starting UI...",
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            Qt.GlobalColor.white,
        )
        app.processEvents()

    from desktop_app.ui.web_shell import WebShellWindow

    window = WebShellWindow()
    window.show()

    threading.Thread(target=_warm_up_database, name="tkops-db-warmup", daemon=True).start()

    if splash:
        splash.finish(window)

    log.info("Main window shown in %.0f ms", (perf_counter() - boot_started) * 1000)
    return app, window
