#!/usr/bin/env python3
"""Contract tests for the Converge adapter foundation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
ROW_SCHEMA = ROOT / "schemas" / "converge-row.schema.json"
SPEC_SCHEMA = ROOT / "schemas" / "converge-spec.schema.json"
SPEC_TEMPLATE = ROOT / "assets" / "templates" / "converge-spec.json"
PYTEST_FIXTURE = ROOT / "tests" / "fixtures" / "pytest-junit.xml"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_rows(rows: list[dict]) -> None:
    schema = load_json(ROW_SCHEMA)
    validator = jsonschema.Draft202012Validator(schema)
    failures = []
    for index, row in enumerate(rows):
        for error in validator.iter_errors(row):
            failures.append(f"row {index}: {error.message}")
    assert failures == []


def run_json(*args: str):
    result = subprocess.run(
        [PYTHON, *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def test_template_matches_converge_spec_schema():
    schema = load_json(SPEC_SCHEMA)
    payload = load_json(SPEC_TEMPLATE)
    jsonschema.Draft202012Validator(schema).validate(payload)


def test_pytest_adapter_emits_schema_valid_rows():
    rows = run_json(
        str(ROOT / "adapters" / "pytest_adapter.py"),
        "--junit",
        str(PYTEST_FIXTURE),
    )
    validate_rows(rows)

    by_id = {row["target_id"]: row for row in rows}
    assert by_id["pytest:tests.test_api::test_health_passes"]["class"] == "pass"
    assert by_id["pytest:tests.test_api::test_returns_200"]["class"] == "fail"
    assert by_id["pytest:tests.test_worker::test_job_runs"]["class"] == "blocked"
    assert by_id["pytest:tests.test_slow::test_external_service"]["class"] == "skip"
    assert len([row for row in rows if row["target_id"] == "pytest:tests.test_api::test_returns_200"]) == 2


def test_pytest_adapter_writes_out_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "pytest-rows.json"
        subprocess.run(
            [
                PYTHON,
                str(ROOT / "adapters" / "pytest_adapter.py"),
                "--junit",
                str(PYTEST_FIXTURE),
                "--out",
                str(out),
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        rows = load_json(out)
    validate_rows(rows)
    assert len(rows) == 5


def test_aggregator_merges_reference_and_pytest_rows():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        reference_rows = tmp / "reference-rows.json"
        pytest_rows = tmp / "pytest-rows.json"

        reference = subprocess.run(
            [
                PYTHON,
                str(ROOT / "adapters" / "json_reference.py"),
                str(SPEC_TEMPLATE),
                "--rows",
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        reference_rows.write_text(reference.stdout, encoding="utf-8")

        pytest_out = subprocess.run(
            [
                PYTHON,
                str(ROOT / "adapters" / "pytest_adapter.py"),
                "--junit",
                str(PYTEST_FIXTURE),
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        pytest_rows.write_text(pytest_out.stdout, encoding="utf-8")

        summary = run_json(
            str(ROOT / "adapters" / "aggregate_rows.py"),
            str(reference_rows),
            str(pytest_rows),
        )

    assert summary["source_files"] == [str(reference_rows), str(pytest_rows)]
    assert summary["score"] < 1
    assert summary["weighted_totals"]["total"] > 0
    assert summary["class_counts"]["fail"] >= 1
    assert any(row["target_id"] == "revenue-apr" for row in summary["repair_rows"])


def test_aggregator_preserves_conflicts():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        first = tmp / "first.json"
        second = tmp / "second.json"
        first.write_text(
            json.dumps([
                {
                    "target_id": "shared",
                    "target": "pass",
                    "probe": "pass",
                    "delta": "",
                    "class": "pass",
                    "evidence": "first",
                    "next_action": "",
                }
            ]),
            encoding="utf-8",
        )
        second.write_text(
            json.dumps([
                {
                    "target_id": "shared",
                    "target": "pass",
                    "probe": "fail",
                    "delta": "changed",
                    "class": "fail",
                    "evidence": "second",
                    "next_action": "repair",
                }
            ]),
            encoding="utf-8",
        )
        summary = run_json(
            str(ROOT / "adapters" / "aggregate_rows.py"),
            str(first),
            str(second),
        )

    assert len(summary["conflicts"]) == 1
    assert summary["conflicts"][0]["target_id"] == "shared"
    assert summary["class_counts"]["fail"] == 1
    assert summary["repair_rows"][0]["target_id"] == "shared"


def test_aggregator_keeps_bypassed_passes_out_of_full_green():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "rows.json"
        path.write_text(
            json.dumps([
                {
                    "target_id": "real-surface",
                    "target": "production behavior",
                    "probe": "production behavior",
                    "delta": "",
                    "class": "pass_real_surface",
                    "evidence": "prod proof",
                    "next_action": "",
                    "weight": 1,
                },
                {
                    "target_id": "controlled-loop",
                    "target": "production behavior",
                    "probe": "localhost with bypass",
                    "delta": "production bot control not tested",
                    "class": "pass_with_bypass",
                    "evidence": "danger-room proof",
                    "next_action": "Run production bot-control proof.",
                    "weight": 1,
                    "proof_envelope": {
                        "environment": "localhost",
                        "bypassed_controls": ["Supabase Auth CAPTCHA disabled"],
                        "fails_to_test": ["production Turnstile"],
                        "side_effects": ["test fixture reset"],
                    },
                },
            ]),
            encoding="utf-8",
        )
        summary = run_json(str(ROOT / "adapters" / "aggregate_rows.py"), str(path))

    assert summary["score"] == 0.5
    assert summary["qualified_score"] == 1.0
    assert summary["weighted_totals"]["qualified_pass"] == 1
    assert summary["class_counts"]["pass_with_bypass"] == 1
    assert summary["proof_surface_counts"]["with_bypass"] == 1
    assert summary["bypass_rows"][0]["target_id"] == "controlled-loop"
    assert summary["negative_space_rows"][0]["fails_to_test"] == ["production Turnstile"]
    assert summary["side_effect_rows"][0]["side_effects"] == ["test fixture reset"]
    assert summary["generated_gap_rows"] == [
        {
            "target_id": "controlled-loop:gap:production-turnstile",
            "class": "missing",
            "target": "Prove untested surface: production Turnstile",
            "probe": "No proof row supplied.",
            "delta": "Generated from controlled-loop proof envelope.",
            "evidence": "danger-room proof",
            "next_action": "Run production bot-control proof.",
            "adapter": "converge:proof-envelope",
            "source_file": str(path),
            "weight": 1.0,
            "generated_from": "controlled-loop",
            "gap": "production Turnstile",
        }
    ]
    assert any(row["target_id"] == "controlled-loop" for row in summary["repair_rows"])
    assert any(row["target_id"] == "controlled-loop:gap:production-turnstile" for row in summary["repair_rows"])


if __name__ == "__main__":
    raise SystemExit(subprocess.call([PYTHON, "-m", "pytest", __file__]))
