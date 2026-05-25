#!/usr/bin/env python3
"""Validate Converge adapter examples against the portable row schema."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "converge-row.schema.json"
EXAMPLES_DIR = ROOT / "adapters" / "examples"


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    failures: list[str] = []

    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(payload), key=lambda error: error.path)
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "$"
            failures.append(f"{path.name}:{location}: {error.message}")

    if failures:
        print("Adapter example validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Adapter examples valid: {len(list(EXAMPLES_DIR.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
