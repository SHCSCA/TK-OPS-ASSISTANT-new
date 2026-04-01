from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QByteArray, QSettings, Qt, QUrl
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QSystemTrayIcon

from desktop_app.ui.bridge import Bridge

if getattr(sys, "frozen", False):
    _ASSETS = Path(sys._MEIPASS) / "desktop_app" / "assets"
else:
    _ASSETS = Path(__file__).resolve().parents[1] / "assets"


def _app_icon() -> QIcon:
    icon = QIcon()
    for size in (16, 32, 48, 64, 128, 256):
        path = _ASSETS / f"icon_{size}.png"
        if path.exists():
            icon.addFile(str(path))
    return icon


class WebShellWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TK-OPS 运营助手")
        self.resize(1600, 960)
        self.setWindowIcon(_app_icon())

        # Restore saved window geometry
        self._settings = QSettings("TK-OPS", "Desktop")
        geo = self._settings.value("window/geometry")
        if isinstance(geo, QByteArray) and not geo.isEmpty():
            self.restoreGeometry(geo)
        state = self._settings.value("window/state")
        if isinstance(state, QByteArray) and not state.isEmpty():
            self.restoreState(state)

        self._view = QWebEngineView()
        self._view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        web_settings = self._view.settings()
        web_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        web_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        web_settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)

        # QWebChannel bridge
        self._bridge = Bridge(self)
        self._channel = QWebChannel(self)
        self._channel.registerObject("backend", self._bridge)
        self._view.page().setWebChannel(self._channel)

        self._view.load(QUrl.fromLocalFile(str(_ASSETS / "app_shell.html")))
        self.setCentralWidget(self._view)

        # System tray
        self._tray = QSystemTrayIcon(_app_icon(), self)
        tray_menu = QMenu()
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self._activate_window)
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        self._tray.setContextMenu(tray_menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    # ── helpers ──

    def _activate_window(self) -> None:
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _quit_app(self) -> None:
        self._force_quit = True
        self.close()
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._activate_window()

    @property
    def bridge(self) -> Bridge:
        return self._bridge

    def closeEvent(self, event) -> None:
        self._settings.setValue("window/geometry", self.saveGeometry())
        self._settings.setValue("window/state", self.saveState())
        self._tray.hide()
        super().closeEvent(event)
