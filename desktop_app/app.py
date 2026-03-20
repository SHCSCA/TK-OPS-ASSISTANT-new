from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from desktop_app.logging_config import setup_logging

log = logging.getLogger(__name__)

if getattr(sys, "frozen", False):
    _ASSETS = Path(sys._MEIPASS) / "desktop_app" / "assets"
else:
    _ASSETS = Path(__file__).resolve().parent / "assets"


def build_application():
    setup_logging()
    log.info("Application starting")

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("TK-OPS Desktop Prototype")
    app.setOrganizationName("TK-OPS")
    app.setQuitOnLastWindowClosed(True)

    # ── Splash screen ──
    splash_path = _ASSETS / "splash.png"
    splash = None
    if splash_path.exists():
        pixmap = QPixmap(str(splash_path))
        splash = QSplashScreen(pixmap, Qt.WindowType.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()
        splash.showMessage(
            "正在初始化数据库…",
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            Qt.GlobalColor.white,
        )
        app.processEvents()

    from desktop_app.database import init_db
    init_db()
    log.info("Database initialised")

    if splash:
        splash.showMessage(
            "正在加载界面…",
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            Qt.GlobalColor.white,
        )
        app.processEvents()

    from desktop_app.ui.web_shell import WebShellWindow
    window = WebShellWindow()
    window.show()

    if splash:
        splash.finish(window)
    log.info("Main window shown")
    return app, window
