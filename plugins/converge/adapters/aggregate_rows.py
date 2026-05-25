#!/usr/bin/env python3
"""Aggregate Converge adapter rows into a repair-focused summary."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
ROW_SCHEMA = ROOT / "schemas" / "converge-row.schema.json"

PASS_CLASSES = {"match", "rounding", "pass", "pass_real_surface"}
QUALIFIED_PASS_CLASSES = {"pass_controlled_harness", "pass_with_bypass"}
FAIL_CLASSES = {"miss_small", "miss_large", "fail", "drift", "regression"}
BLOCKED_CLASSES = {"missing", "blocked"}
SKIP_CLASSES = {"skip"}
CLASS_RANK = {
    "pass": 0,
    "pass_real_surface": 0,
    "match": 0,
    "rounding": 0,
    "pass_controlled_harness": 1,
    "pass_with_bypass": 2,
    "skip": 3,
    "blocked": 4,
    "missing": 4,
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
    if class_name in QUALIFIED_PASS_CLASSES:
        return "qualified_pass"
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
    proof_envelope = row.get("proof_envelope") if isinstance(row.get("proof_envelope"), dict) else {}
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
        "proof_envelope": proof_envelope,
        "fails_to_test": row.get("fails_to_test") or proof_envelope.get("fails_to_test") or [],
        "bypassed_controls": row.get("bypassed_controls") or proof_envelope.get("bypassed_controls") or [],
        "side_effects": row.get("side_effects") or proof_envelope.get("side_effects") or [],
    }


def slug(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return text[:80] or "gap"


def generated_gap_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    proof_envelope = row.get("proof_envelope") if isinstance(row.get("proof_envelope"), dict) else {}
    fails_to_test = row.get("fails_to_test") or proof_envelope.get("fails_to_test") or []
    if not fails_to_test:
        return []
    source_target_id = str(row["target_id"])
    return [
        {
            "target_id": f"{source_target_id}:gap:{slug(str(gap))}",
            "class": "missing",
            "target": f"Prove untested surface: {gap}",
            "probe": "No proof row supplied.",
            "delta": f"Generated from {source_target_id} proof envelope.",
            "evidence": row.get("evidence", ""),
            "next_action": row.get("next_action") or f"Add a real proof row for: {gap}",
            "adapter": "converge:proof-envelope",
            "source_file": row.get("_source_file", ""),
            "weight": weight(row),
            "generated_from": source_target_id,
            "gap": gap,
        }
        for gap in fails_to_test
    ]


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

    weighted_totals = {"pass": 0.0, "qualified_pass": 0.0, "fail": 0.0, "blocked": 0.0, "skip": 0.0, "total": 0.0}
    class_counts = {key: 0 for key in [
        "match",
        "rounding",
        "pass",
        "pass_real_surface",
        "pass_controlled_harness",
        "pass_with_bypass",
        "miss_small",
        "miss_large",
        "fail",
        "missing",
        "blocked",
        "drift",
        "regression",
        "skip",
    ]}
    proof_surface_counts = {"real_surface": 0, "controlled_harness": 0, "with_bypass": 0}
    bypass_rows: list[dict[str, Any]] = []
    negative_space_rows: list[dict[str, Any]] = []
    side_effect_rows: list[dict[str, Any]] = []
    generated_gaps: list[dict[str, Any]] = []
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
        if class_name == "pass_real_surface":
            proof_surface_counts["real_surface"] += 1
        elif class_name == "pass_controlled_harness":
            proof_surface_counts["controlled_harness"] += 1
        elif class_name == "pass_with_bypass":
            proof_surface_counts["with_bypass"] += 1
        proof_envelope = row.get("proof_envelope") if isinstance(row.get("proof_envelope"), dict) else {}
        bypassed_controls = row.get("bypassed_controls") or proof_envelope.get("bypassed_controls") or []
        fails_to_test = row.get("fails_to_test") or proof_envelope.get("fails_to_test") or []
        side_effects = row.get("side_effects") or proof_envelope.get("side_effects") or []
        if bypassed_controls:
            bypass_rows.append(repair_row(row))
        if fails_to_test:
            negative_space_rows.append(repair_row(row))
            generated_gaps.extend(generated_gap_rows(row))
        if side_effects:
            side_effect_rows.append(repair_row(row))

    denominator = weighted_totals["total"]
    score = 1.0 if denominator == 0 else weighted_totals["pass"] / denominator
    qualified_score = 1.0 if denominator == 0 else (weighted_totals["pass"] + weighted_totals["qualified_pass"]) / denominator
    repairs = [
        repair_row(row)
        for row in sorted(
            merged,
            key=lambda item: (-CLASS_RANK.get(str(item.get("class")), 99), -weight(item), item["target_id"]),
        )
        if is_required(row) and class_bucket(str(row.get("class"))) in {"qualified_pass", "fail", "blocked"}
    ]
    repairs.extend(generated_gaps)

    return {
        "score": score,
        "qualified_score": qualified_score,
        "weighted_totals": weighted_totals,
        "class_counts": class_counts,
        "proof_surface_counts": proof_surface_counts,
        "bypass_rows": bypass_rows,
        "negative_space_rows": negative_space_rows,
        "side_effect_rows": side_effect_rows,
        "generated_gap_rows": generated_gaps,
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
