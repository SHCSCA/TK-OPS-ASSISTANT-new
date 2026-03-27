"""TK-OPS build helper — generate assets & invoke PyInstaller.

Usage:
    python build.py              # 完整构建
    python build.py --ico-only   # 仅生成 .ico
    python build.py --clean      # 清理 build/ dist/ 后构建
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "desktop_app" / "assets"
ICO_PATH = ROOT / "tkops.ico"
LEGACY_ICO_PATH = ASSETS / "icon.ico"
SPEC_PATH = ROOT / "tk_ops.spec"
VERSION_FILE = ROOT / "VERSION"
README_PATH = ROOT / "README.md"
INSTALLER_PATH = ROOT / "installer.iss"
FILE_VERSION_INFO_PATH = ROOT / "file_version_info.txt"
BRIDGE_JS_PATH = ROOT / "desktop_app" / "assets" / "js" / "bridge.js"


def _load_app_version() -> str:
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not version:
        print("[ERR] VERSION file is empty")
        sys.exit(1)
    return version


def _replace(pattern: str, replacement: str, text: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        print(f"[ERR] Failed to update {label}")
        sys.exit(1)
    return updated


def _sync_version_metadata(version: str) -> None:
    major, minor, patch = version.split(".")
    version_tuple = f"({major}, {minor}, {patch}, 0)"

    readme_text = README_PATH.read_text(encoding="utf-8")
    readme_text = _replace(
        r"^当前发布版本：`[0-9]+\.[0-9]+\.[0-9]+`$",
        f"当前发布版本：`{version}`",
        readme_text,
        "README current version",
    )
    README_PATH.write_text(readme_text, encoding="utf-8")

    installer_text = INSTALLER_PATH.read_text(encoding="utf-8")
    installer_text = _replace(
        r'^#define MyAppVersion\s+"[0-9]+\.[0-9]+\.[0-9]+"$',
        f'#define MyAppVersion   "{version}"',
        installer_text,
        "installer version",
    )
    INSTALLER_PATH.write_text(installer_text, encoding="utf-8")

    version_info_text = FILE_VERSION_INFO_PATH.read_text(encoding="utf-8")
    version_info_text = _replace(
        r"filevers=\([0-9, ]+\)",
        f"filevers={version_tuple}",
        version_info_text,
        "file version tuple",
    )
    version_info_text = _replace(
        r"prodvers=\([0-9, ]+\)",
        f"prodvers={version_tuple}",
        version_info_text,
        "product version tuple",
    )
    version_info_text = _replace(
        r'StringStruct\("FileVersion",\s+"[0-9]+\.[0-9]+\.[0-9]+"\)',
        f'StringStruct("FileVersion",      "{version}")',
        version_info_text,
        "file version string",
    )
    version_info_text = _replace(
        r'StringStruct\("ProductVersion",\s+"[0-9]+\.[0-9]+\.[0-9]+"\)',
        f'StringStruct("ProductVersion",   "{version}")',
        version_info_text,
        "product version string",
    )
    FILE_VERSION_INFO_PATH.write_text(version_info_text, encoding="utf-8")

    bridge_text = BRIDGE_JS_PATH.read_text(encoding="utf-8")
    bridge_text = _replace(
        r"getAppVersion: \(\) => ok\(\{ version: '[0-9]+\.[0-9]+\.[0-9]+' \}\),",
        f"getAppVersion: () => ok({{ version: '{version}' }}),",
        bridge_text,
        "bridge stub version",
    )
    bridge_text = _replace(
        r"checkForUpdate: \(\) => ok\(\{ hasUpdate: false, current: '[0-9]+\.[0-9]+\.[0-9]+' \}\),",
        f"checkForUpdate: () => ok({{ hasUpdate: false, current: '{version}' }}),",
        bridge_text,
        "bridge stub update version",
        )
    BRIDGE_JS_PATH.write_text(bridge_text, encoding="utf-8")


def generate_ico() -> None:
    """Merge multi-resolution PNGs into a single .ico file."""
    try:
        from PIL import Image
    except ImportError:
        print("[!] Pillow not installed - run: pip install Pillow")
        sys.exit(1)

    sizes = (256, 128, 64, 48, 32, 16)
    imgs = []
    for s in sizes:
        p = ASSETS / f"icon_{s}.png"
        if not p.exists():
            print(f"[!] Missing {p}")
            sys.exit(1)
        imgs.append(Image.open(p).convert("RGBA"))

    imgs[0].save(str(ICO_PATH), format="ICO", append_images=imgs[1:])
    print(f"[OK] icon.ico generated ({ICO_PATH.stat().st_size:,} bytes)")


def clean() -> None:
    for d in ("build", "dist"):
        p = ROOT / d
        if p.exists():
            shutil.rmtree(p)
            print(f"[OK] Removed {d}/")


def build(extra_args: list[str]) -> None:
    version = _load_app_version()
    _sync_version_metadata(version)

    if not ICO_PATH.exists():
        # Fallback for old icon pipeline.
        if LEGACY_ICO_PATH.exists():
            print(f"[!] tkops.ico not found, fallback to legacy icon: {LEGACY_ICO_PATH}")
        else:
            generate_ico()

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        str(SPEC_PATH),
        *extra_args,
    ]
    print(f"[RUN] {' '.join(cmd)}")
    ret = subprocess.call(cmd, cwd=str(ROOT))
    if ret != 0:
        print(f"[ERR] PyInstaller exited with code {ret}")
        sys.exit(ret)
    print("[OK] Build complete -> dist/TK-OPS/")


def main() -> None:
    ap = argparse.ArgumentParser(description="TK-OPS build helper")
    ap.add_argument("--ico-only", action="store_true", help="仅生成 icon.ico")
    ap.add_argument("--clean", action="store_true", help="构建前清理 build/dist")
    args, extra = ap.parse_known_args()

    if args.ico_only:
        generate_ico()
        return

    if args.clean:
        clean()
        extra.append("--clean")

    build(extra)


if __name__ == "__main__":
    main()
