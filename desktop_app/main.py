#!/usr/bin/env python3
from __future__ import annotations

# pyright: basic, reportMissingImports=false

"""TK-OPS 桌面应用正式启动入口。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from .app import main as app_main
except ImportError:
    from desktop_app.app import main as app_main


def main() -> int:
    return app_main(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
