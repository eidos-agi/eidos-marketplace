"""kai usage telemetry — JSONL line per invocation.

Every kai invocation appends one JSON line to $KAI_USAGE_LOG (default
~/.kai/usage.log). Makes "which domains earn their keep" a data question
instead of a vibes question.

Best-effort: failures here never crash the CLI. Telemetry is decoration,
not load-bearing.

NOT in v0:
  - Rotation / retention. Append-only, never truncated.
  - Privacy filtering. Local-only by design; never shipped off-machine.
  - Per-pilot dimensions. Add when there's a second pilot using kai.
"""
from __future__ import annotations

import json
import os
import platform
from datetime import datetime, timezone
from pathlib import Path

from kai import __version__

USAGE_ENV = "KAI_USAGE_LOG"
DEFAULT_USAGE_LOG = Path.home() / ".kai" / "usage.log"


def _usage_log() -> Path:
    override = os.environ.get(USAGE_ENV)
    if override:
        return Path(override).expanduser()
    return DEFAULT_USAGE_LOG


def log_invocation(cmd: str) -> None:
    """Append one JSON line for this invocation. Best effort; never crashes."""
    try:
        path = _usage_log()
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "cmd": cmd,
            "cwd": str(Path.cwd()),
            "kai": __version__,
            "py": platform.python_version(),
        }
        with path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass
