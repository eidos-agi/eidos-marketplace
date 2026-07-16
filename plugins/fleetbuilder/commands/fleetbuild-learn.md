---
description: Study the user's Claude Code transcripts and (re)distill .fleetbuilder/learnings.md — what Fleet they need, how they build, standing orders, antibodies.
allowed-tools: Bash, Read
---

Update FleetBuilder's learnings from the user's own transcripts.

Run the historian miner (fixed-cost — uses `claude -p`, never the raw API):

```
python3 "${CLAUDE_PLUGIN_ROOT}/tools/learn.py" --repo "$(pwd)" --sessions 30
```

Then read the refreshed `.fleetbuilder/learnings.md` and confirm the distilled lessons back
to the user in 3–5 bullets. If the extraction looks thin or noisy, say so — the miner is
heuristic (see tools/learn.py header for the ceiling).

$ARGUMENTS
