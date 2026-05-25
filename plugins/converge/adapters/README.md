# Converge Adapters

Adapters turn some evidence surface into Converge rows. They are intentionally
plural. Converge is the row contract and operating doctrine, not a single
runtime.

## Required Row Shape

Every adapter should emit rows compatible with:

```bash
/Users/dshanklinbv/plugins/converge/schemas/converge-row.schema.json
```

Minimal row:

```json
{
  "target_id": "api-health:status-code",
  "target": 200,
  "probe": 500,
  "delta": -300,
  "class": "fail",
  "evidence": "curl -i http://localhost:3000/health returned HTTP 500",
  "next_action": "Fix the health endpoint dependency check."
}
```

## Adapter Families

| Adapter Family | Typical Target | Typical Probe |
|---|---|---|
| `pytest` | Test should pass | JUnit/test result row |
| `sql` | Expected count/value | Query result |
| `dbt` | Model/test freshness | dbt JSON artifact |
| `playwright` | UI behavior or screenshot state | Browser assertion/output |
| `ci` | Required workflow/check state | GitHub Actions/check-run result |
| `api` | Contract response | HTTP status/body/schema check |
| `spreadsheet` | Canonical table value | Workbook/computed value |
| `human_review` | Acceptance criterion | Reviewer decision with evidence |
| `eidos` | Docket/evidence loop condition | Eidos context/evidence/closeout artifact |

## Adapter Rules

- Emit rows; do not hide failures in prose.
- Preserve target, probe, delta, class, evidence, and next action.
- Prefer literal evidence paths or command output over summaries.
- Do not call models from adapters unless the user explicitly requests that.
- If a probe cannot run, emit `class: "blocked"` or `class: "missing"` with the unblock path.
- If a row used to pass and now fails, emit or update a regression row.
- If evidence is stale, emit or update a drift row.
- Keep examples valid with:

```bash
python3 /Users/dshanklinbv/plugins/converge/tests/validate_adapter_examples.py
```

## Aggregation

The row aggregator accepts one or more adapter row files, validates them against
`converge-row.schema.json`, merges by `target_id`, preserves conflicts, computes
weighted pass/fail/blocked totals, and emits the repair-focused map Codex should
work from:

```bash
python3 /Users/dshanklinbv/plugins/converge/adapters/aggregate_rows.py \
  path/to/reference-rows.json \
  path/to/pytest-rows.json
```

The output includes `score`, `weighted_totals`, `class_counts`, `conflicts`,
`repair_rows`, and `source_files`.

## Pytest Adapter

The pytest adapter converts JUnit XML into portable Converge rows:

```bash
python3 /Users/dshanklinbv/plugins/converge/adapters/pytest_adapter.py \
  --junit path/to/junit.xml \
  --out converge-rows.json
```

Each test case becomes `target_id = pytest:<classname>::<name>`, `target =
pass`, and a probe/class pair of `pass/pass`, `fail/fail`, `error/blocked`, or
`skipped/skip`.

## Reference Adapter

The JSON reference adapter is a small local helper for exercising the contract:

```bash
python3 /Users/dshanklinbv/plugins/converge/adapters/json_reference.py \
  /Users/dshanklinbv/plugins/converge/assets/templates/converge-spec.json
```

It is lab equipment, not the Converge engine.

To emit portable Converge rows:

```bash
python3 /Users/dshanklinbv/plugins/converge/adapters/json_reference.py \
  /Users/dshanklinbv/plugins/converge/assets/templates/converge-spec.json \
  --rows
```
