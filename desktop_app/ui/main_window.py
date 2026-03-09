"""Minimal PySide6 UI skeleton for main window (optional usage)."""
try:
    from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
except Exception:  # PySide6 may not be installed in all environments
    QMainWindow = object
    QWidget = object
    QVBoxLayout = object
    QLabel = object


class MainWindow(QMainWindow):  # type: ignore
    def __init__(self):  # type: ignore
        super().__init__()
        self.setWindowTitle("TK-OPS Desktop – MVP UI")
        self.resize(1000, 700)
        central = QWidget()
        layout = QVBoxLayout(central)  # type: ignore
        layout.addWidget(QLabel("TK-OPS Desktop MVP"))  # type: ignore
        self.setCentralWidget(central)  # type: ignore
