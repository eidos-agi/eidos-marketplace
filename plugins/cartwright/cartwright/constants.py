from __future__ import annotations

import os
from pathlib import Path

DB_FILE_NAME = "cartwright.sqlite"
DEFAULT_DB_PATH = Path.home() / ".cartwright" / DB_FILE_NAME


def get_db_path(override: str | None = None) -> str:
    if override:
        return str(Path(override).expanduser())
    env_path = os.environ.get("CARTWRIGHT_DB_PATH")
    if env_path:
        return str(Path(env_path).expanduser())
    return str(DEFAULT_DB_PATH)
