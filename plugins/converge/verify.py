#!/usr/bin/env python3
"""Eidos plugin verification hook for Converge."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable


def run(command: list[str]) -> tuple[bool, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def verify(work_dir: Path | str | None = None, draft_dir: Path | str | None = None) -> dict[str, Any]:
    checks = [
        [PYTHON, "-m", "pytest", "tests", "-q"],
        [PYTHON, "tests/validate_adapter_examples.py"],
        [PYTHON, "adapters/aggregate_rows.py", "--help"],
    ]
    failures = []
    for command in checks:
        ok, output = run(command)
        if not ok:
            failures.append({"command": command, "output": output})

    required = [
        "plugin.yaml",
        "playbook.md",
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        "schemas/converge-row.schema.json",
        "schemas/converge-spec.schema.json",
    ]
    for rel in required:
        if not (ROOT / rel).is_file():
            failures.append({"command": ["file-exists", rel], "output": "missing"})

    reasons = ["Converge plugin checks passed"] if not failures else [
        f"{len(failures)} Converge plugin checks failed"
    ]
    return {
        "passed": not failures,
        "reasons": reasons,
        "detail": {
            "plugin_root": str(ROOT),
            "work_dir": str(work_dir) if work_dir is not None else None,
            "draft_dir": str(draft_dir) if draft_dir is not None else None,
            "failures": failures,
        },
    }


def main() -> int:
    result = verify()
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
