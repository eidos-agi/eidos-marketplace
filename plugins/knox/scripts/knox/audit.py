from __future__ import annotations

import json
import hashlib
import time
from pathlib import Path

from . import config


def _audit_path() -> Path:
    config.ensure_directory(config.KNOX_ROOT)
    return config.KNOX_AUDIT_PATH


def _redact_payload(payload: dict[str, object]) -> dict[str, object]:
    # Keep only operation metadata and avoid leaking provider payload contents.
    allowed = {
        "provider",
        "operation",
        "idempotency_key",
        "request_label",
        "client_hint",
        "session",
        "result_status",
    }
    redacted: dict[str, object] = {}
    for key in allowed:
        if key in payload:
            redacted[key] = payload[key]
    return redacted


def _read_last_hash(path: Path) -> str | None:
    if not path.exists():
        return None

    last_line = None
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                last_line = line
    except OSError:
        return None

    if not last_line:
        return None

    try:
        parsed = json.loads(last_line)
    except json.JSONDecodeError:
        return None
    prev = parsed.get("hash")
    return str(prev) if isinstance(prev, str) else None


def log_event(event: str, payload: dict[str, object]) -> None:
    path = _audit_path()
    prev_hash = _read_last_hash(path)
    record_core = {
        "ts": int(time.time()),
        "event": event,
        "payload": _redact_payload(payload),
    }
    if prev_hash:
        record_core["prev_hash"] = prev_hash
    record = {
        "hash": hashlib.sha256(json.dumps(record_core, sort_keys=True, default=str).encode("utf-8")).hexdigest(),
        **record_core,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True))
        handle.write("\n")
