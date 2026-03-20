# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec – TK-OPS Desktop Application.

Usage:
    pyinstaller tk_ops.spec          # 常规构建
    pyinstaller tk_ops.spec --clean  # 清理后构建
"""
from pathlib import Path

ROOT = Path(SPECPATH)
ASSETS = ROOT / "desktop_app" / "assets"
MIGRATIONS = ROOT / "desktop_app" / "database" / "migrations"
PROTOTYPE_ASSETS = ROOT / "prototype" / "assets"
APP_ICO = ROOT / "tkops.ico"

a = Analysis(
    [str(ROOT / "desktop_app" / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # 前端资源（HTML / CSS / JS / 图标）
        (str(ASSETS), "desktop_app/assets"),
        # 历史基础样式（app_shell.html 仍依赖该文件）
        (str(PROTOTYPE_ASSETS), "prototype/assets"),
        # Alembic 迁移
        (str(MIGRATIONS), "desktop_app/database/migrations"),
        # Alembic 配置
        (str(ROOT / "alembic.ini"), "."),
    ],
    hiddenimports=[
        # Qt 子模块（部分平台可能未被自动检测）
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebChannel",
        "PySide6.QtWebEngineCore",
        # SQLAlchemy dialect
        "sqlalchemy.dialects.sqlite",
        # Alembic 需要 mako + logging.config
        "alembic",
        "mako",
        "mako.template",
        "logging.config",
        # Pydantic
        "pydantic",
        # openai / httpx transport
        "openai",
        "httpx",
        "httpx._transports",
        "httpx._transports.default",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 测试框架不打包
        "pytest",
        "pytest_qt",
        # 开发工具
        "IPython",
        "notebook",
        "tkinter",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TK-OPS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                       # GUI 应用，不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[str(APP_ICO)],
    version="file_version_info.txt",     # 可选：Windows 版本信息
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="TK-OPS",
)
