#!/usr/bin/env python3
"""Start optional tray helper and launch the Knox MCP server."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.knox.server import main


def _bootstrap_paths() -> Path:
    return Path(__file__).resolve().parents[1]


def _candidate_tray_paths(root: Path) -> list[Path]:
    return [
        root / "apps" / "KnoxMenuBar" / "build" / "KnoxMenuBar",
        root / "apps" / "KnoxMenuBar" / ".build" / "release" / "KnoxMenuBar",
        root / "apps" / "KnoxMenuBar" / ".build" / "debug" / "KnoxMenuBar",
        Path("/Applications/KnoxMenuBar.app/Contents/MacOS/KnoxMenuBar"),
    ]


def _start_tray(root: Path) -> None:
    if os.getenv("KNOX_SKIP_TRAY", "").strip().lower() in {"1", "true", "on", "yes"}:
        return
    approval_mode = os.getenv("KNOX_APPROVAL_MODE", "").strip().lower()
    if approval_mode not in {"tray", "hybrid"}:
        return

    configured = os.getenv("KNOX_TRAY_BINARY")
    tray_binary = Path(configured) if configured else None
    if tray_binary is None or not tray_binary.exists():
        for candidate in _candidate_tray_paths(root):
            if candidate.exists():
                tray_binary = candidate
                break

    if tray_binary is None or not tray_binary.exists():
        return

    try:
        subprocess.Popen(
            [str(tray_binary)],
            cwd=str(root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        return


def main_entrypoint() -> int:
    root = _bootstrap_paths()
    sys.path.insert(0, str(root))
    _start_tray(root)
    return main()


if __name__ == "__main__":
    raise SystemExit(main_entrypoint())
