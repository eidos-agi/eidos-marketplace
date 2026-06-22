---
name: use-apple-a-day
description: Use when the user asks to check, monitor, clean up, or keep a Mac healthy with apple-a-day or aad.
---

# Use apple-a-day

apple-a-day is a read-only-by-default Mac health CLI. Use it to inspect health,
vitals, cleanup candidates, and launchd monitor state before doing expensive or
long-running local work.

## Start With Read-Only Proof

```bash
aad checkup --json --min-severity warning --fields severity,summary,fix
aad monitor --once --json
aad vitals --json --minutes 60
aad status
```

If `aad` is not on PATH, install or run it with `uvx`:

```bash
uvx --from apple-a-day aad checkup --json --min-severity warning --fields severity,summary,fix
```

## Safe Operating Boundary

- Checkups are read-only and should be the default first move.
- Treat every `fix` as a recommendation unless the user explicitly asks to
  execute it.
- Installing or uninstalling the vitals monitor changes launchd state; explain
  that action before running `aad install` or `aad uninstall`.
- Do not delete apps, caches, launch agents, or logs just because AAD flags
  them. Produce a cleanup packet first.

## Common Workflows

For a quick machine health answer:

```bash
aad checkup --json --min-severity warning --fields severity,summary,fix
```

For preflight before heavy local work:

```bash
aad checkup --json -c cpu_load -c thermal -c memory_pressure --min-severity warning
```

For an always-on Mac:

```bash
aad install
aad status
aad vitals --json --minutes 60
```

For cleanup planning:

```bash
aad checkup --json -c cleanup --min-severity info
```

Return the concrete findings, the evidence command used, and which actions
remain human-approved or destructive.
