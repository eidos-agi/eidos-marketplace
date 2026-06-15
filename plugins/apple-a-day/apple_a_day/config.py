"""apple-a-day user configuration."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".config" / "eidos" / "apple-a-day"
CONFIG_PATH = CONFIG_DIR / "config.json"


def default_config() -> dict[str, Any]:
    """Return the default config shape."""
    return {
        "storage": {
            "remote_folder": None,
            "provider": "mounted-folder",
            "rclone_remote": None,
            "min_boot_free_gb": 50,
            "notes": (
                "Remote folder is an external drive or mounted share for cold archives. "
                "CloudMounter or rclone-backed drives work when mounted under /Volumes."
            ),
        }
    }


def load_config() -> dict[str, Any]:
    """Load config, returning defaults when no config exists."""
    config = default_config()
    if not CONFIG_PATH.exists():
        return config
    try:
        loaded = json.loads(CONFIG_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return config
    if isinstance(loaded, dict):
        _deep_update(config, loaded)
    return config


def save_config(config: dict[str, Any]) -> Path:
    """Persist config to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    return CONFIG_PATH


def set_remote_folder(
    path: str | Path,
    create: bool = False,
    provider: str | None = None,
    rclone_remote: str | None = None,
) -> dict[str, Any]:
    """Set the remote storage folder, optionally creating it."""
    expanded = Path(path).expanduser()
    if create:
        expanded.mkdir(parents=True, exist_ok=True)
    config = load_config()
    storage = config.setdefault("storage", {})
    storage["remote_folder"] = str(expanded)
    if provider:
        storage["provider"] = provider
    if rclone_remote is not None:
        storage["rclone_remote"] = rclone_remote
    save_config(config)
    return config


def remote_storage_status(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return status for configured remote storage."""
    config = config or load_config()
    storage = config.get("storage", {}) if isinstance(config, dict) else {}
    raw_path = storage.get("remote_folder")
    if not raw_path:
        return {"configured": False}

    path = Path(str(raw_path)).expanduser()
    status: dict[str, Any] = {
        "configured": True,
        "path": str(path),
        "provider": storage.get("provider", "mounted-folder"),
        "exists": path.exists(),
        "is_dir": path.is_dir(),
    }
    rclone_remote = storage.get("rclone_remote")
    if rclone_remote:
        status["rclone_remote"] = str(rclone_remote)
        status.update(_rclone_status(str(rclone_remote)))
    if path.exists() and path.is_dir():
        status.update(_df_status(path))
    return status


def _rclone_status(remote: str) -> dict[str, Any]:
    if not shutil.which("rclone"):
        return {"rclone_available": False}
    try:
        out = subprocess.run(
            ["rclone", "about", remote, "--json"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"rclone_available": False}
    if out.returncode != 0:
        return {
            "rclone_available": True,
            "rclone_ok": False,
            "rclone_error": out.stderr.strip()[:240],
        }
    try:
        payload = json.loads(out.stdout)
    except json.JSONDecodeError:
        return {"rclone_available": True, "rclone_ok": False}
    status: dict[str, Any] = {"rclone_available": True, "rclone_ok": True}
    for key in ("total", "used", "free"):
        value = payload.get(key)
        if isinstance(value, int):
            status[f"rclone_{key}_gb"] = round(value / (1000**3), 1)
    return status


def _df_status(path: Path) -> dict[str, Any]:
    try:
        out = subprocess.run(["df", "-k", str(path)], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return {}
    lines = [line for line in out.stdout.splitlines() if line.strip()]
    if len(lines) < 2:
        return {}
    parts = lines[-1].split()
    if len(parts) < 6:
        return {}
    try:
        size_kb = int(parts[1])
        used_kb = int(parts[2])
        avail_kb = int(parts[3])
        capacity_pct = int(parts[4].rstrip("%"))
    except ValueError:
        return {}
    return {
        "filesystem": parts[0],
        "mount": parts[-1],
        "size_gb": round(size_kb * 1024 / (1000**3), 1),
        "used_gb": round(used_kb * 1024 / (1000**3), 1),
        "free_gb": round(avail_kb * 1024 / (1000**3), 1),
        "capacity_pct": capacity_pct,
    }


def _deep_update(base: dict[str, Any], updates: dict[str, Any]) -> None:
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_update(base[key], value)
        else:
            base[key] = value
