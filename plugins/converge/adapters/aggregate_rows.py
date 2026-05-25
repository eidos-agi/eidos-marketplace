#!/usr/bin/env python3
"""Aggregate Converge adapter rows into a repair-focused summary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
ROW_SCHEMA = ROOT / "schemas" / "converge-row.schema.json"

PASS_CLASSES = {"match", "rounding", "pass"}
FAIL_CLASSES = {"miss_small", "miss_large", "fail", "drift", "regression"}
BLOCKED_CLASSES = {"missing", "blocked"}
SKIP_CLASSES = {"skip"}
CLASS_RANK = {
    "pass": 0,
    "match": 0,
    "rounding": 0,
    "skip": 1,
    "blocked": 2,
    "missing": 2,
    "miss_small": 3,
    "miss_large": 4,
    "drift": 5,
    "regression": 6,
    "fail": 7,
}


def load_schema() -> dict[str, Any]:
    return json.loads(ROW_SCHEMA.read_text(encoding="utf-8"))


def read_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = [payload]
    else:
        raise ValueError(f"{path} must contain a Converge row or array of rows")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"{path} contains a non-object row")
    return rows


def validate_rows(rows: list[dict[str, Any]], source: str, validator: jsonschema.Validator) -> None:
    failures = []
    for index, row in enumerate(rows):
        for error in validator.iter_errors(row):
            failures.append(f"{source} row {index}: {error.message}")
    if failures:
        raise ValueError("; ".join(failures))


def weight(row: dict[str, Any]) -> float:
    try:
        value = float(row.get("weight", 1))
    except (TypeError, ValueError):
        return 1.0
    return value if value > 0 else 1.0


def class_bucket(class_name: str) -> str:
    if class_name in PASS_CLASSES:
        return "pass"
    if class_name in FAIL_CLASSES:
        return "fail"
    if class_name in BLOCKED_CLASSES:
        return "blocked"
    if class_name in SKIP_CLASSES:
        return "skip"
    return "fail"


def is_required(row: dict[str, Any]) -> bool:
    return row.get("required", True) is not False


def choose_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return max(rows, key=lambda row: (CLASS_RANK.get(str(row.get("class")), 99), weight(row)))


def conflict_for(target_id: str, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    classes = {str(row.get("class", "")) for row in rows}
    probes = {json.dumps(row.get("probe"), sort_keys=True) for row in rows}
    if len(rows) < 2 or (len(classes) == 1 and len(probes) == 1):
        return None
    return {
        "target_id": target_id,
        "classes": sorted(classes),
        "rows": [
            {
                "adapter": row.get("adapter", ""),
                "class": row.get("class", ""),
                "probe": row.get("probe", ""),
                "evidence": row.get("evidence", ""),
                "source_file": row.get("_source_file", ""),
            }
            for row in rows
        ],
    }


def repair_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "target_id": row["target_id"],
        "class": row.get("class", ""),
        "target": row.get("target", ""),
        "probe": row.get("probe", ""),
        "delta": row.get("delta", ""),
        "evidence": row.get("evidence", ""),
        "next_action": row.get("next_action", ""),
        "adapter": row.get("adapter", ""),
        "source_file": row.get("_source_file", ""),
        "weight": weight(row),
    }


def summarize(paths: list[str]) -> dict[str, Any]:
    validator = jsonschema.Draft202012Validator(load_schema())
    grouped: dict[str, list[dict[str, Any]]] = {}

    for raw_path in paths:
        path = Path(raw_path)
        rows = read_rows(path)
        validate_rows(rows, raw_path, validator)
        for row in rows:
            annotated = dict(row)
            annotated["_source_file"] = raw_path
            grouped.setdefault(str(row["target_id"]), []).append(annotated)

    merged = [choose_row(rows) for rows in grouped.values()]
    conflicts = [
        conflict
        for target_id, rows in grouped.items()
        if (conflict := conflict_for(target_id, rows)) is not None
    ]

    weighted_totals = {"pass": 0.0, "fail": 0.0, "blocked": 0.0, "skip": 0.0, "total": 0.0}
    class_counts = {key: 0 for key in ["match", "rounding", "pass", "miss_small", "miss_large", "fail", "missing", "blocked", "drift", "regression", "skip"]}
    for row in merged:
        class_name = str(row.get("class", "fail"))
        class_counts.setdefault(class_name, 0)
        class_counts[class_name] += 1
        bucket = class_bucket(class_name)
        row_weight = weight(row)
        if not is_required(row):
            continue
        weighted_totals[bucket] += row_weight
        if bucket != "skip":
            weighted_totals["total"] += row_weight

    denominator = weighted_totals["total"]
    score = 1.0 if denominator == 0 else weighted_totals["pass"] / denominator
    repairs = [
        repair_row(row)
        for row in sorted(
            merged,
            key=lambda item: (-CLASS_RANK.get(str(item.get("class")), 99), -weight(item), item["target_id"]),
        )
        if is_required(row) and class_bucket(str(row.get("class"))) in {"fail", "blocked"}
    ]

    return {
        "score": score,
        "weighted_totals": weighted_totals,
        "class_counts": class_counts,
        "conflicts": conflicts,
        "repair_rows": repairs,
        "source_files": paths,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rows", nargs="+", help="One or more JSON files containing Converge rows.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    print(json.dumps(summarize(args.rows), indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        print(f"aggregate_rows.py: {exc}", file=sys.stderr)
        raise SystemExit(1)
