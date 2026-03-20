"""TK-OPS build helper — generate assets & invoke PyInstaller.

Usage:
    python build.py              # 完整构建
    python build.py --ico-only   # 仅生成 .ico
    python build.py --clean      # 清理 build/ dist/ 后构建
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "desktop_app" / "assets"
ICO_PATH = ROOT / "tkops.ico"
LEGACY_ICO_PATH = ASSETS / "icon.ico"
SPEC_PATH = ROOT / "tk_ops.spec"


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
