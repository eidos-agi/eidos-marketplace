# Tally CFO Conduit Runbook

Tally owns finance judgment. Conduit owns machine targeting and deployment
proof for the Tally plugin/workload.

## Target Policy

Preferred target:

```text
mac-mini-01
```

Fallback:

```text
rentamac-cyprus-01
```

Use the rented Cyprus machine only when Daniel explicitly asks or approves the
fallback.

## Preflight

```bash
scripts/conduit workloads --json
scripts/conduit doctor mac-mini-01 --json
scripts/conduit proof --target mac-mini-01 --json
```

## Deploy or Sync

Use the registry target, not a hardcoded SSH alias:

```bash
scripts/conduit plugin deploy ./path-to-tally-plugin --target mac-mini-01
```

or, for a non-plugin sync:

```bash
scripts/conduit sync ./path-to-tally-plugin ~/plugins/tally --target mac-mini-01
```

## Completion Proof

After deployment:

```bash
scripts/conduit proof --target mac-mini-01 --json
```

Report the proof path and whether the machine identity matched `mac-mini-01`.

## Boundaries

- Do not deploy finance-control workloads to Cyprus without Daniel approval.
- Do not store finance credentials in Conduit.
- Do not treat Tally ledger state as Conduit state.
