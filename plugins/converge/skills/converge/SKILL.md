---
name: converge
description: Use when a user wants to give an AI agent or Codex explicit software targets, measurable completion criteria, deterministic scoreboards, evidence audits, and repair loops.
---

# Converge

Use this skill when the work is bigger than one obvious bugfix and the user
wants the software to become complete, trustworthy, or production-ready.

## Core Stance

The goal is convergence: give AI explicit targets, score progress against
evidence, repair the smallest failing rows, and repeat. "100%" is not a feeling
and not an LLM self-grade. It means every required target row is either passing
with evidence or explicitly blocked with an owner and next action.

The Greenmark v4 pattern is the model:

- A scoreboard is a diagnostic instrument, not an oracle.
- Deterministic checks run first because they are cheap and repeatable.
- Heuristic or LLM reasoning runs on demand for the rows that matter.
- Scores should fail in the safe direction: under-reporting done is better
  than over-reporting done.
- Completion is anchored to a north star outside the model.
- Drift, regression, and iteration are first-class signals, not afterthoughts.

## Contract First

Converge is the contract and operating doctrine, not a single runtime. Do not
overfit Converge to one JSON file, one Python script, or one repository shape.

The durable row contract is:

| Field | Meaning |
|---|---|
| `target_id` | Stable identifier for the target row. |
| `target` | Expected value, state, threshold, maturity stage, or behavior. |
| `probe` | Observed value from the implementation, test, query, UI, API, or evidence. |
| `delta` | Difference, transition, gap, or mismatch between probe and target. |
| `class` | Match/miss/block/drift/regression classification. |
| `evidence` | Literal proof or path to proof. |
| `next_action` | Smallest repair, refresh, escalation, or retirement move. |

Adapters produce rows. Aggregators summarize rows. Codex repairs rows. Eidos
preserves the outer evidence loop. The Python helpers in this plugin are local
reference utilities and adapters, not the Converge engine.

The starter lattice schema lives at:

```bash
/Users/dshanklinbv/plugins/converge/schemas/converge-spec.schema.json
```

The portable adapter row schema lives at:

```bash
/Users/dshanklinbv/plugins/converge/schemas/converge-row.schema.json
```

Good adapters include:

- unit/integration/e2e test output
- SQL/dbt result tables
- Playwright/browser probes
- API contract checks
- GitHub Actions or CI summaries
- spreadsheet comparison tabs
- shell command outputs
- Eidos evidence bundles
- human-reviewed acceptance tables

## Convergence Styles

Pick the convergence style that matches the work. A plugin, dashboard, API,
agent, or data pipeline should not all be judged by the same pressure.

| Style | Use When | Done Means |
|---|---|---|
| `exact_match` | The target is deterministic: generated files, schemas, known outputs, reconciliations. | Probe equals target within strict tolerance. |
| `tolerance_band` | The target has acceptable variance: performance, finance rounding, model eval scores. | Probe stays inside an explicit acceptable band. |
| `staged_maturity` | A system grows through phases. | Targets mature through declared, implemented, tested, verified, shipped, observed, hardened. |
| `regression_hardening` | Stability matters more than new surface area. | Previously passing rows stay passing and recurring failures become invariants. |
| `drift_homeostasis` | The environment changes: APIs, data, dependencies, user behavior. | Freshness monitors pass and deviations are corrected before green becomes stale. |
| `exploratory_narrowing` | The right implementation is unknown. | Each iteration eliminates hypotheses and shrinks uncertainty. |
| `consensus_evidence` | No single check is authoritative. | Multiple independent evidence paths agree. |
| `graceful_degradation` | Partial function is acceptable under failure. | Critical paths continue, degraded paths are explicit and bounded. |

Use one primary style and optional secondary styles. The primary style decides
what "closer" means; secondary styles provide guardrails.

## Target/Probe Grids

The Greenmark PDF-to-warehouse comparison grid is a core Converge pattern:
compare the external target against the system probe, compute the delta, classify
the row by tolerance, and aggregate the bias.

Use this for any software claim that can be measured numerically or discretely:

| Column | Meaning |
|---|---|
| Target | The outside or canonical value the system must match. |
| Probe | The value produced by the current implementation, query, API, UI, or test. |
| Delta | Probe minus target, preserving direction. |
| Tolerance | The acceptable difference for this target. |
| Class | `match`, `rounding`, `miss_small`, `miss_large`, or `missing`. |
| Cause | Current best explanation for non-match rows. |
| Next Action | Smallest repair or investigation that could move the row. |

Keep both row-level and aggregate signals:

- row color/status tells the agent where truth breaks
- signed delta tells whether the system under-counts or over-counts
- absolute delta tells mismatch magnitude
- gross percentage shows total drift from target
- net percentage shows directional bias after cancellations

Do not reduce this to pass/fail too early. The delta is the steering signal.

## Drift

Drift is when the world changes but the target lattice does not. Passing rows
can become dishonest if their evidence, evaluator, or assumptions age out.

Track these drift types:

| Drift Type | Meaning | Response |
|---|---|---|
| Spec drift | Requirements changed but targets still encode old intent. | Update target rows before repairing code. |
| Code drift | Implementation changed but docs, tests, or target rows did not. | Re-score affected rows and add traceability. |
| Data drift | Inputs, schemas, APIs, or distributions changed. | Add schema/sample monitors and refresh fixtures. |
| Evaluator drift | Checks no longer measure the north star. | Fix the evaluator before trusting green rows. |
| Context drift | Agent assumptions became stale across time or handoffs. | Re-read canonical surfaces and refresh evidence. |

Every score is time-bound: green as of a specific target version, evidence
snapshot, and evaluator version.

## Regression

Regression is when a row that used to pass stops passing. Regressions should be
treated as injury signals because they reveal instability in the convergence
process.

Converge should:

- keep score history, not just current state
- flag pass -> fail or pass -> blocked transitions
- distinguish intentional target changes from accidental breakage
- turn recurring regressions into invariants or tests
- ask whether a repair moved the system closer to the north star or just moved
  the error somewhere else

## Iteration

Iteration is the metabolism of Converge: target -> attempt -> score -> audit ->
repair -> re-score. Each loop should shrink uncertainty and leave better
substrate behind.

A good iteration:

- repairs the smallest row that moves the north star
- adds evidence, not just code
- records failed hypotheses when they teach something
- escalates when the score stalls across repeated loops
- retires obsolete targets instead of endlessly patching them

## Biology Lessons

Living systems maintain function despite noise, mutation, damage, and changing
environments. Converge should borrow these patterns:

| Biological Pattern | Software Meaning |
|---|---|
| Homeostasis | Track target bands and correct deviations before they become failures. |
| Feedback loops | Let every score directly shape the next repair target. |
| Immune memory | Promote repeated failures into durable checks. |
| Adaptation | Weight work by survival pressure: the north star, not equal row count. |
| Mutation and selection | Let AI generate repair hypotheses; deterministic checks select. |
| Developmental stages | Mature targets through declared, implemented, tested, verified, shipped, observed, hardened. |
| Redundancy | Important claims need multiple evidence paths. |
| Apoptosis | Kill or supersede targets that harm convergence or no longer serve the north star. |

## Target Tables

Create or refresh only the tables needed for the current scope. Prefer compact
JSON, CSV, Markdown tables, or repo-native formats over a giant prose spec.

| Table | Purpose |
|---|---|
| North Star | Names the actual business/product outcome and the scoring formula. |
| Target Inventory | Lists files, services, routes, commands, APIs, docs, and data surfaces in scope. |
| Layer Scoreboard | Crosses each target with completion layers such as declared, implemented, tested, verified, documented, shipped. |
| Decision Table | Captures branching business logic and expected outputs. |
| State Table | Captures legal states, transitions, guards, and side effects. |
| Invariant Table | Captures rules that must always hold, with check commands where possible. |
| Test Matrix | Maps scenarios to deterministic commands, expected results, and evidence. |
| Traceability Table | Links target -> implementation -> test -> evidence. |
| Evidence Audit | Stores literal proof: command output, screenshots, API responses, logs, or manual blocker notes. |
| Target/Probe Grid | Compares canonical target to current probe, with delta, tolerance class, cause, and next action. |
| Drift Monitors | Names assumptions, freshness windows, and recheck triggers. |
| Regression History | Records row transitions, previous evidence, cause, and whether intentional. |
| Iteration Ledger | Records loop number, score delta, repair target, hypothesis, result, and next move. |
| Repair Targets | Lists failing rows, smallest next repair, owner, status, and why it matters. |

## Workflow

1. Define the north star in one sentence.
2. Select the convergence style and the unit of completion: feature, module, route, metric, user flow,
   data contract, or repo.
3. Build the smallest useful target lattice. Do not spec the universe up front.
4. Mark required rows and optional rows explicitly.
5. Run deterministic checks and score them before asking the model to reason.
6. Audit non-green rows by collecting literal evidence, not summaries.
7. Repair the smallest failing layer that moves the north star.
8. Re-score after every meaningful repair.
9. Check for drift and regressions before claiming progress.
10. Stop when all required rows are passing or blocked with an owner, evidence,
   and next action.

## State Vocabulary

Use a small display vocabulary for humans:

| State | Meaning |
|---|---|
| `pass` | Required row is complete with evidence. |
| `fail` | Required row is not good enough; repair it. |
| `blocked` | External dependency or decision needed; name owner and unblock path. |
| `skip` | Not required for this north star; explain why. |

If a repo already has richer states, keep them internally but collapse to these
four in summaries.

## Operating Rules

- Never claim 100% from prose alone.
- Never let the LLM be the only judge of pass/fail.
- Prefer cheap checks for every row, and use LLM reasoning only for rows where
  the deterministic signal is incomplete.
- Treat false green as worse than false red.
- If a row cannot be checked yet, create the row anyway and mark it `blocked`
  or `fail` honestly.
- Use the repo's existing test and verification commands before inventing new
  harnesses.
- When scope is large, repair one layer or one artifact slice at a time.
- When a score improves, still check for regressions in previously passing rows.
- When a score stalls, inspect drift before adding more code.

## Reference Adapter

The plugin includes a small Python reference adapter for simple JSON specs, a
pytest/JUnit adapter, and a row aggregator. Use them to test the contract shape,
not as the canonical Converge engine:

```bash
python3 /Users/dshanklinbv/plugins/converge/adapters/json_reference.py path/to/converge-spec.json
python3 /Users/dshanklinbv/plugins/converge/adapters/pytest_adapter.py --junit path/to/junit.xml --out pytest-rows.json
python3 /Users/dshanklinbv/plugins/converge/adapters/aggregate_rows.py reference-rows.json pytest-rows.json
```

The template lives at:

```bash
/Users/dshanklinbv/plugins/converge/assets/templates/converge-spec.json
```
