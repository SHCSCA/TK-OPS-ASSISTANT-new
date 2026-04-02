"""TK-OPS 旧 PyInstaller 构建辅助脚本。"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "desktop_app" / "assets"
ICO_PATH = ROOT / "tkops.ico"
LEGACY_ICO_PATH = ASSETS / "icon.ico"
SPEC_PATH = ROOT / "tk_ops.spec"
VERSION_FILE = ROOT / "VERSION"
FFMPEG_BINARIES = ("ffmpeg.exe", "ffprobe.exe")
FFMPEG_DLL_GLOB = "*.dll"


@dataclass(frozen=True)
class VersionReplacement:
    pattern: str
    replacement: str
    label: str


def _find_ffmpeg_install_dir() -> Path | None:
    for binary_name in FFMPEG_BINARIES:
        binary_path = shutil.which(binary_name)
        if binary_path:
            return Path(binary_path).resolve().parent
    return None


def ensure_ffmpeg_bundle(root: Path = ROOT) -> Path:
    bundle_dir = root / "tools" / "ffmpeg" / "win64"
    ffmpeg_path = bundle_dir / "ffmpeg.exe"
    ffprobe_path = bundle_dir / "ffprobe.exe"
    if ffmpeg_path.is_file() and ffprobe_path.is_file():
        return bundle_dir

    install_dir = _find_ffmpeg_install_dir()
    if install_dir is None:
        raise RuntimeError(
            "未找到 FFmpeg 安装目录。请先安装 ffmpeg/ffprobe，或手动放入 tools/ffmpeg/win64。"
        )

    bundle_dir.mkdir(parents=True, exist_ok=True)
    for binary_name in FFMPEG_BINARIES:
        source = install_dir / binary_name
        if not source.is_file():
            raise RuntimeError(f"缺少 FFmpeg 组件: {source}")
        shutil.copy2(source, bundle_dir / binary_name)

    for dll_path in install_dir.glob(FFMPEG_DLL_GLOB):
        shutil.copy2(dll_path, bundle_dir / dll_path.name)
    return bundle_dir


def _load_app_version(root: Path = ROOT) -> str:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not version:
        raise RuntimeError("VERSION 文件为空")
    return version


def _replace(pattern: str, replacement: str, text: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"无法更新 {label}")
    return updated


def _version_sync_plan(version: str, root: Path = ROOT) -> dict[Path, tuple[VersionReplacement, ...]]:
    major, minor, patch = version.split(".")
    version_tuple = f"({major}, {minor}, {patch}, 0)"

    return {
        root / "README.md": (
            VersionReplacement(
                r"^当前发布版本：`[0-9]+\.[0-9]+\.[0-9]+`$",
                f"当前发布版本：`{version}`",
                "README 当前版本",
            ),
        ),
        root / "installer.iss": (
            VersionReplacement(
                r'^#define MyAppVersion\s+"[0-9]+\.[0-9]+\.[0-9]+"$',
                f'#define MyAppVersion   "{version}"',
                "安装器版本",
            ),
        ),
        root / "file_version_info.txt": (
            VersionReplacement(
                r"filevers=\([0-9, ]+\)",
                f"filevers={version_tuple}",
                "文件版本元组",
            ),
            VersionReplacement(
                r"prodvers=\([0-9, ]+\)",
                f"prodvers={version_tuple}",
                "产品版本元组",
            ),
            VersionReplacement(
                r'StringStruct\("FileVersion",\s+"[0-9]+\.[0-9]+\.[0-9]+"\)',
                f'StringStruct("FileVersion",      "{version}")',
                "文件版本字符串",
            ),
            VersionReplacement(
                r'StringStruct\("ProductVersion",\s+"[0-9]+\.[0-9]+\.[0-9]+"\)',
                f'StringStruct("ProductVersion",   "{version}")',
                "产品版本字符串",
            ),
        ),
        root / "desktop_app" / "assets" / "js" / "bridge.js": (
            VersionReplacement(
                r"getAppVersion: \(\) => ok\(\{ version: '[0-9]+\.[0-9]+\.[0-9]+' \}\),",
                f"getAppVersion: () => ok({{ version: '{version}' }}),",
                "bridge stub 版本",
            ),
            VersionReplacement(
                r"checkForUpdate: \(\) => ok\(\{ hasUpdate: false, current: '[0-9]+\.[0-9]+\.[0-9]+' \}\),",
                f"checkForUpdate: () => ok({{ hasUpdate: false, current: '{version}' }}),",
                "bridge stub 更新版本",
            ),
        ),
    }


def collect_version_metadata_updates(
    version: str,
    root: Path = ROOT,
) -> dict[Path, str]:
    updates: dict[Path, str] = {}

    for path, replacements in _version_sync_plan(version, root).items():
        current_text = path.read_text(encoding="utf-8")
        updated_text = current_text

        for replacement in replacements:
            updated_text = _replace(
                replacement.pattern,
                replacement.replacement,
                updated_text,
                replacement.label,
            )

        if updated_text != current_text:
            updates[path] = updated_text

    return updates


def sync_version_metadata(version: str, root: Path = ROOT) -> list[Path]:
    updates = collect_version_metadata_updates(version, root)
    for path, updated_text in updates.items():
        path.write_text(updated_text, encoding="utf-8")
    return list(updates)


def ensure_version_metadata_consistent(version: str, root: Path = ROOT) -> None:
    updates = collect_version_metadata_updates(version, root)
    if not updates:
        return

    relative_paths = ", ".join(str(path.relative_to(root)) for path in updates)
    raise RuntimeError(
        "版本受管文件与 VERSION 不一致："
        f"{relative_paths}。"
        "普通构建不会自动改写源码；如需同步，请运行 "
        "`python build.py --sync-version-metadata`。"
    )


def generate_ico() -> None:
    """Merge multi-resolution PNGs into a single .ico file."""
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("未安装 Pillow，请先执行 `pip install Pillow`。") from exc

    sizes = (256, 128, 64, 48, 32, 16)
    images = []
    for size in sizes:
        path = ASSETS / f"icon_{size}.png"
        if not path.exists():
            raise RuntimeError(f"缺少图标源文件: {path}")
        images.append(Image.open(path).convert("RGBA"))

    images[0].save(str(ICO_PATH), format="ICO", append_images=images[1:])
    print(f"[OK] icon.ico generated ({ICO_PATH.stat().st_size:,} bytes)")


def clean() -> None:
    for dirname in ("build", "dist"):
        path = ROOT / dirname
        if path.exists():
            shutil.rmtree(path)
            print(f"[OK] Removed {dirname}/")


def build(extra_args: list[str]) -> None:
    version = _load_app_version()
    ensure_version_metadata_consistent(version)
    ffmpeg_bundle_dir = ensure_ffmpeg_bundle()

    if not ICO_PATH.exists():
        if LEGACY_ICO_PATH.exists():
            print(f"[!] tkops.ico not found, fallback to legacy icon: {LEGACY_ICO_PATH}")
        else:
            generate_ico()

    print(f"[OK] FFmpeg bundle ready: {ffmpeg_bundle_dir}")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(SPEC_PATH),
        *extra_args,
    ]
    print(f"[RUN] {' '.join(cmd)}")
    result = subprocess.call(cmd, cwd=str(ROOT))
    if result != 0:
        raise RuntimeError(f"PyInstaller exited with code {result}")
    print("[OK] Build complete -> dist/TK-OPS/")


def main() -> None:
    parser = argparse.ArgumentParser(description="TK-OPS legacy build helper")
    parser.add_argument("--ico-only", action="store_true", help="仅生成 icon.ico")
    parser.add_argument("--clean", action="store_true", help="构建前清理 build/dist")
    parser.add_argument(
        "--check-version-metadata",
        action="store_true",
        help="只检查版本受管文件是否与 VERSION 一致",
    )
    parser.add_argument(
        "--sync-version-metadata",
        action="store_true",
        help="按 VERSION 显式同步 README、安装器、版本资源和 bridge stub",
    )
    args, extra = parser.parse_known_args()

    try:
        version = _load_app_version()

        if args.sync_version_metadata:
            updated_paths = sync_version_metadata(version)
            if updated_paths:
                print("[OK] Synced version metadata:")
                for path in updated_paths:
                    print(f"  - {path.relative_to(ROOT)}")
            else:
                print("[OK] Version metadata already in sync")

        if args.check_version_metadata:
            ensure_version_metadata_consistent(version)
            print("[OK] Version metadata is consistent")

        if args.sync_version_metadata and not (args.ico_only or args.clean or extra):
            return
        if args.check_version_metadata and not (args.ico_only or args.clean or extra):
            return

        if args.ico_only:
            generate_ico()
            return

        if args.clean:
            clean()
            extra.append("--clean")

        build(extra)
    except RuntimeError as exc:
        print(f"[ERR] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
