from __future__ import annotations

import json
from pathlib import Path
from typing import Any

KNOX_ROOT = Path.home() / ".knox"
KNOX_STATE_DB = KNOX_ROOT / "state.sqlite"
KNOX_REGISTRY_PATH = KNOX_ROOT / "registry.json"
KNOX_AUDIT_PATH = KNOX_ROOT / "audit.log"
DEFAULT_POLICY_PATH = KNOX_ROOT / "policy.json"
KNOX_PAIRING_PATH = KNOX_ROOT / "pairing.json"
KNOX_APPROVAL_CONTROL_PATH = KNOX_ROOT / "approval-control.json"


def ensure_directory(path: Path) -> None:
    """Ensure the Knox directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.chmod(0o700)
    except OSError:
        pass


def load_json_file(path: Path, fallback: dict[str, Any] | list[Any]) -> dict[str, Any] | list[Any]:
    if not path.exists():
        return fallback
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback
    return raw
