#!/usr/bin/env python3
"""Reference adapter for a simple Converge JSON target lattice.

This script intentionally stays small and non-canonical. Converge is the
target/probe/evidence/repair contract, not this Python implementation. Use this
adapter to exercise simple JSON specs, then replace it with SQL, tests, CI,
Playwright, spreadsheets, Eidos evidence, or any other adapter that emits the
same row shape.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


DEFAULT_ALIASES = {
    "pass": {"pass", "passed", "complete", "good", "green", "verified", "ratified", "shipped"},
    "fail": {"fail", "failed", "not_yet", "broken", "red", "missing"},
    "blocked": {"blocked", "stuck", "waiting", "needs_human", "external"},
    "skip": {"skip", "skipped", "not_applicable", "optional"},
}

STYLE_DESCRIPTIONS = {
    "exact_match": "Probe must equal target or match a strict expected output.",
    "tolerance_band": "Probe must stay inside an explicit acceptable band.",
    "staged_maturity": "Targets move through maturity stages before being considered done.",
    "regression_hardening": "Previously passing rows must not fall back without an intentional target change.",
    "drift_homeostasis": "Freshness and environment monitors must stay healthy.",
    "exploratory_narrowing": "Each iteration must eliminate hypotheses or reduce uncertainty.",
    "consensus_evidence": "Multiple independent evidence paths must agree.",
    "graceful_degradation": "Critical behavior must survive partial failures with explicit degraded modes.",
}


def load_spec(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("spec root must be a JSON object")
    return payload


def aliases(spec: dict[str, Any]) -> dict[str, set[str]]:
    merged = {key: set(values) for key, values in DEFAULT_ALIASES.items()}
    raw_aliases = spec.get("state_aliases", {})
    if isinstance(raw_aliases, dict):
        for bucket, values in raw_aliases.items():
            if bucket in merged and isinstance(values, list):
                merged[bucket].update(str(value).strip().lower() for value in values)
    return merged


def normalize_state(raw_state: Any, state_aliases: dict[str, set[str]]) -> str:
    value = str(raw_state or "").strip().lower()
    for bucket, values in state_aliases.items():
        if value in values:
            return bucket
    return "fail"


def weight(row: dict[str, Any]) -> float:
    raw_weight = row.get("weight", 1)
    try:
        value = float(raw_weight)
    except (TypeError, ValueError):
        return 1.0
    return value if value > 0 else 1.0


def number(raw_value: Any) -> float | None:
    if raw_value is None:
        return None
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return None


def comparison_class(delta_abs: float | None, tolerances: dict[str, float]) -> str:
    if delta_abs is None:
        return "missing"
    if delta_abs <= tolerances.get("match", 0.1):
        return "match"
    if delta_abs <= tolerances.get("rounding", 1.0):
        return "rounding"
    if delta_abs <= tolerances.get("miss_small", 1000.0):
        return "miss_small"
    return "miss_large"


def class_to_state(class_name: str) -> str:
    if class_name in {"match", "rounding"}:
        return "pass"
    if class_name == "missing":
        return "blocked"
    return "fail"


def collect_rows(spec: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in spec.get("scoreboard", []):
        if isinstance(row, dict):
            rows.append({"kind": "scoreboard", **row})

    for invariant in spec.get("invariants", []):
        if isinstance(invariant, dict):
            rows.append({"kind": "invariant", **invariant})

    for table in spec.get("decision_tables", []):
        if not isinstance(table, dict):
            continue
        table_name = table.get("name", "decision-table")
        for index, row in enumerate(table.get("rows", []), start=1):
            if isinstance(row, dict):
                rows.append({
                    "kind": "decision",
                    "id": row.get("id", f"{table_name}:{index}"),
                    "artifact": table_name,
                    "layer": "decision-row",
                    "required": row.get("required", True),
                    "weight": row.get("weight", 1),
                    "state": row.get("state", row.get("status")),
                    "evidence": row.get("evidence", row.get("test", "")),
                    "next_action": row.get("next_action", "Make this decision row pass."),
                })
    for grid in comparison_grids(spec):
        for row in grid["rows"]:
            rows.append({
                "kind": "target_probe",
                "id": row.get("id", "(comparison-row)"),
                "artifact": grid["name"],
                "layer": "target-probe",
                "required": row.get("required", True),
                "weight": row.get("weight", 1),
                "state": class_to_state(row["class"]),
                "evidence": row.get("evidence", ""),
                "next_action": row.get("next_action", ""),
                "comparison": row,
            })
    return rows


def comparison_grids(spec: dict[str, Any]) -> list[dict[str, Any]]:
    grids: list[dict[str, Any]] = []
    for grid in spec.get("target_probe_grids", []):
        if not isinstance(grid, dict):
            continue
        raw_tolerances = grid.get("tolerances", {})
        tolerances = {
            "match": number(raw_tolerances.get("match")) or 0.1,
            "rounding": number(raw_tolerances.get("rounding")) or 1.0,
            "miss_small": number(raw_tolerances.get("miss_small")) or 1000.0,
        }
        rows = []
        for row in grid.get("rows", []):
            if not isinstance(row, dict):
                continue
            target = number(row.get("target"))
            probe = number(row.get("probe"))
            delta = None if target is None or probe is None else probe - target
            delta_abs = None if delta is None else abs(delta)
            row_class = str(row.get("class") or comparison_class(delta_abs, tolerances))
            rows.append({
                **row,
                "target": target,
                "probe": probe,
                "delta": delta,
                "delta_abs": delta_abs,
                "class": row_class,
            })
        grids.append({
            "name": grid.get("name", "target-probe-grid"),
            "unit": grid.get("unit", "row"),
            "tolerances": tolerances,
            "rows": rows,
            "summary": comparison_summary(rows),
        })
    return grids


def comparison_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    required = [row for row in rows if row.get("required", True) is not False]
    target_abs = sum(abs(row["target"]) for row in required if row.get("target") is not None)
    delta_signed = sum(row["delta"] for row in required if row.get("delta") is not None)
    delta_abs = sum(row["delta_abs"] for row in required if row.get("delta_abs") is not None)
    in_sync = [row for row in required if row.get("class") in {"match", "rounding"}]
    denominator = len(required)
    return {
        "required_rows": denominator,
        "in_sync_rows": len(in_sync),
        "target_abs": target_abs,
        "delta_signed": delta_signed,
        "delta_abs": delta_abs,
        "pct_net": 0.0 if target_abs == 0 else delta_signed / target_abs * 100,
        "pct_gross": 0.0 if target_abs == 0 else delta_abs / target_abs * 100,
    }


def score(spec: dict[str, Any]) -> dict[str, Any]:
    state_aliases = aliases(spec)
    rows = collect_rows(spec)
    required = [row for row in rows if row.get("required", True) is not False]
    buckets = {"pass": [], "fail": [], "blocked": [], "skip": []}
    weighted = {"pass": 0.0, "fail": 0.0, "blocked": 0.0, "skip": 0.0}

    for row in required:
        state = normalize_state(row.get("state"), state_aliases)
        buckets[state].append(row)
        weighted[state] += weight(row)

    denominator = sum(weight(row) for row in required)
    numerator = weighted["pass"]
    pct = 1.0 if denominator == 0 else numerator / denominator
    return {
        "name": spec.get("name", "converge-spec"),
        "north_star": spec.get("north_star", {}),
        "required_rows": denominator,
        "passed_rows": numerator,
        "score": pct,
        "buckets": buckets,
        "weighted": weighted,
        "drift": drift_report(spec, state_aliases),
        "regressions": regression_report(spec, state_aliases),
        "iteration": iteration_report(spec),
        "comparison_grids": comparison_grids(spec),
        "style": convergence_style_report(spec),
    }


def contract_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for bucket in ("pass", "fail", "blocked"):
        for row in result["buckets"][bucket]:
            rows.append({
                "target_id": str(row.get("id", "(no id)")),
                "target": row.get("target", row.get("artifact", "")),
                "probe": row.get("probe", row.get("state", bucket)),
                "delta": row.get("delta", row.get("layer", row.get("kind", ""))),
                "class": bucket,
                "evidence": row.get("evidence", ""),
                "next_action": row.get("next_action", ""),
                "adapter": "json_reference",
                "convergence_style": result["style"]["primary"],
                "required": row.get("required", True),
                "weight": weight(row),
            })
    for grid in result["comparison_grids"]:
        for row in grid["rows"]:
            rows.append({
                "target_id": str(row.get("id", "(comparison-row)")),
                "target": row.get("target"),
                "probe": row.get("probe"),
                "delta": row.get("delta"),
                "class": row.get("class"),
                "evidence": row.get("evidence", row.get("cause", "")),
                "next_action": row.get("next_action", ""),
                "adapter": "json_reference",
                "convergence_style": result["style"]["primary"],
                "required": row.get("required", True),
                "weight": weight(row),
                "tolerance": grid["tolerances"].get("rounding"),
            })
    return rows


def convergence_style_report(spec: dict[str, Any]) -> dict[str, Any]:
    raw_style = spec.get("convergence_style", {})
    if not isinstance(raw_style, dict):
        raw_style = {}
    primary = str(raw_style.get("primary") or "tolerance_band")
    secondary_raw = raw_style.get("secondary", [])
    secondary = [str(value) for value in secondary_raw] if isinstance(secondary_raw, list) else []
    return {
        "primary": primary,
        "secondary": secondary,
        "why": raw_style.get("why", ""),
        "description": STYLE_DESCRIPTIONS.get(primary, "Custom convergence style."),
    }


def style_cautions(result: dict[str, Any]) -> list[str]:
    style = result["style"]["primary"]
    cautions: list[str] = []
    if style == "exact_match":
        for grid in result["comparison_grids"]:
            misses = [
                row for row in grid["rows"]
                if row.get("required", True) is not False and row["class"] != "match"
            ]
            if misses:
                cautions.append(
                    f"exact_match: {grid['name']} has {len(misses)} required rows not in strict match."
                )
    elif style == "tolerance_band":
        for grid in result["comparison_grids"]:
            summary = grid["summary"]
            if summary["required_rows"] and summary["in_sync_rows"] < summary["required_rows"]:
                cautions.append(
                    f"tolerance_band: {grid['name']} still has "
                    f"{summary['required_rows'] - summary['in_sync_rows']} rows outside tolerance."
                )
    elif style == "regression_hardening" and result["regressions"]:
        cautions.append(
            f"regression_hardening: {len(result['regressions'])} unintentional regressions remain."
        )
    elif style == "drift_homeostasis" and result["drift"]:
        cautions.append(
            f"drift_homeostasis: {len(result['drift'])} drift monitors need attention."
        )
    elif style == "exploratory_narrowing":
        latest = result["iteration"].get("latest")
        if isinstance(latest, dict) and not latest.get("hypothesis"):
            cautions.append("exploratory_narrowing: latest iteration lacks a recorded hypothesis.")
    elif style == "consensus_evidence":
        weak_rows = [
            row for bucket in ("pass", "fail", "blocked")
            for row in result["buckets"][bucket]
            if row.get("required", True) is not False and not row.get("evidence")
        ]
        if weak_rows:
            cautions.append(
                f"consensus_evidence: {len(weak_rows)} required rows lack evidence text."
            )
    elif style == "graceful_degradation":
        blocked_or_failed = len(result["buckets"]["fail"]) + len(result["buckets"]["blocked"])
        if blocked_or_failed:
            cautions.append(
                f"graceful_degradation: {blocked_or_failed} rows need bounded degraded-mode notes."
            )

    if "regression_hardening" in result["style"]["secondary"] and result["regressions"]:
        cautions.append(
            f"secondary regression_hardening: {len(result['regressions'])} regressions need explanation."
        )
    if "drift_homeostasis" in result["style"]["secondary"] and result["drift"]:
        cautions.append(
            f"secondary drift_homeostasis: {len(result['drift'])} drift monitors need refresh."
        )
    return cautions


def parse_iso_date(raw_value: Any) -> date | None:
    if not isinstance(raw_value, str) or not raw_value.strip():
        return None
    try:
        return datetime.strptime(raw_value.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def drift_report(spec: dict[str, Any], state_aliases: dict[str, set[str]]) -> list[dict[str, Any]]:
    today = date.today()
    stale_or_failing: list[dict[str, Any]] = []
    for monitor in spec.get("drift_monitors", []):
        if not isinstance(monitor, dict):
            continue
        state = normalize_state(monitor.get("state"), state_aliases)
        last_checked = parse_iso_date(monitor.get("last_checked"))
        freshness_days = monitor.get("freshness_days")
        try:
            freshness = int(freshness_days)
        except (TypeError, ValueError):
            freshness = None
        stale = last_checked is None
        if last_checked is not None and freshness is not None:
            stale = (today - last_checked).days > freshness
        if state != "pass" or stale:
            stale_or_failing.append({
                **monitor,
                "normalized_state": state,
                "stale": stale,
            })
    return stale_or_failing


def regression_report(
    spec: dict[str, Any],
    state_aliases: dict[str, set[str]],
) -> list[dict[str, Any]]:
    regressions: list[dict[str, Any]] = []
    for entry in spec.get("regression_history", []):
        if not isinstance(entry, dict):
            continue
        from_state = normalize_state(entry.get("from"), state_aliases)
        to_state = normalize_state(entry.get("to"), state_aliases)
        intentional = entry.get("intentional") is True
        if from_state == "pass" and to_state in {"fail", "blocked"} and not intentional:
            regressions.append(entry)
    return regressions


def iteration_report(spec: dict[str, Any]) -> dict[str, Any]:
    ledger = [entry for entry in spec.get("iteration_ledger", []) if isinstance(entry, dict)]
    if not ledger:
        return {"loops": 0, "latest": None, "stalled": False}
    policy = spec.get("iteration_policy", {})
    try:
        stall_threshold = int(policy.get("stall_threshold_loops", 3)) if isinstance(policy, dict) else 3
    except (TypeError, ValueError):
        stall_threshold = 3
    recent = ledger[-stall_threshold:]
    stalled = len(recent) == stall_threshold and all(
        float(entry.get("score_after", 0) or 0) <= float(entry.get("score_before", 0) or 0)
        for entry in recent
    )
    return {"loops": len(ledger), "latest": ledger[-1], "stalled": stalled}


def print_report(result: dict[str, Any]) -> None:
    north_star = result["north_star"]
    print(f"Spec: {result['name']}")
    if isinstance(north_star, dict) and north_star.get("statement"):
        print(f"North star: {north_star['statement']}")
    style = result["style"]
    print(f"Convergence style: {style['primary']} - {style['description']}")
    if style["secondary"]:
        print(f"Secondary styles: {', '.join(style['secondary'])}")
    if style.get("why"):
        print(f"Why: {style['why']}")
    print(
        "Score: "
        f"{result['passed_rows']:g} / {result['required_rows']:g} weighted = "
        f"{result['score']:.1%}"
    )
    print(
        "Rows: "
        f"{len(result['buckets']['pass'])} pass, "
        f"{len(result['buckets']['fail'])} fail, "
        f"{len(result['buckets']['blocked'])} blocked"
    )
    print()

    cautions = style_cautions(result)
    if cautions:
        print("STYLE cautions:")
        for caution in cautions:
            print(f"- {caution}")
        print()

    for bucket in ("fail", "blocked"):
        rows = result["buckets"][bucket]
        if not rows:
            continue
        print(f"{bucket.upper()} rows:")
        for row in rows:
            row_id = row.get("id", "(no id)")
            artifact = row.get("artifact", "")
            layer = row.get("layer", row.get("kind", ""))
            next_action = row.get("next_action", "")
            evidence = row.get("evidence", "")
            print(f"- {row_id} [{artifact} / {layer}]")
            if evidence:
                print(f"  evidence: {evidence}")
            if next_action:
                print(f"  next: {next_action}")
        print()

    for grid in result["comparison_grids"]:
        summary = grid["summary"]
        if not summary["required_rows"]:
            continue
        print(f"TARGET/PROBE grid: {grid['name']}")
        print(
            "In sync: "
            f"{summary['in_sync_rows']} / {summary['required_rows']} "
            f"({summary['in_sync_rows'] / summary['required_rows'] * 100:.1f}%)"
        )
        print(f"Delta signed: {summary['delta_signed']:+,.2f}")
        print(f"Delta absolute: {summary['delta_abs']:,.2f}")
        print(f"% off net: {summary['pct_net']:+.4f}%")
        print(f"% off gross: {summary['pct_gross']:.4f}%")
        for row in grid["rows"]:
            if row.get("required", True) is False or row["class"] in {"match", "rounding"}:
                continue
            delta = "missing" if row.get("delta") is None else f"{row['delta']:+,.2f}"
            print(f"- {row.get('id', '(row)')}: {row['class']} delta={delta}")
            if row.get("cause"):
                print(f"  cause: {row['cause']}")
            if row.get("next_action"):
                print(f"  next: {row['next_action']}")
        print()

    if result["drift"]:
        print("DRIFT monitors needing attention:")
        for monitor in result["drift"]:
            monitor_id = monitor.get("id", "(no id)")
            drift_type = monitor.get("type", "unknown")
            stale = "stale" if monitor.get("stale") else monitor.get("normalized_state", "fail")
            trigger = monitor.get("trigger", "")
            print(f"- {monitor_id} [{drift_type} / {stale}]")
            if trigger:
                print(f"  trigger: {trigger}")
        print()

    if result["regressions"]:
        print("REGRESSIONS needing attention:")
        for regression in result["regressions"]:
            row_id = regression.get("row_id", "(no row)")
            cause = regression.get("cause", "")
            next_action = regression.get("next_action", "")
            print(f"- {row_id}: {regression.get('from')} -> {regression.get('to')}")
            if cause:
                print(f"  cause: {cause}")
            if next_action:
                print(f"  next: {next_action}")
        print()

    iteration = result["iteration"]
    if iteration["loops"]:
        latest = iteration["latest"]
        print(f"Iterations: {iteration['loops']}")
        if isinstance(latest, dict):
            print(f"Latest repair target: {latest.get('repair_target', '(none)')}")
        if iteration["stalled"]:
            print("Stall signal: score has not improved across the recent iteration window.")
        print()


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3):
        print("Usage: json_reference.py path/to/converge-spec.json [--rows]", file=sys.stderr)
        return 2
    spec = load_spec(Path(argv[1]))
    result = score(spec)
    if len(argv) == 3 and argv[2] == "--rows":
        print(json.dumps(contract_rows(result), indent=2))
    elif len(argv) == 3:
        print(f"unknown option: {argv[2]}", file=sys.stderr)
        return 2
    else:
        print_report(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
