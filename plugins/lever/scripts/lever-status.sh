#!/usr/bin/env bash
set -euo pipefail

if command -v lever >/dev/null 2>&1; then
  LEVER_BIN="$(command -v lever)"
else
  LEVER_BIN="/Users/dshanklin/repos-personal/lever/.venv/bin/lever"
fi

"$LEVER_BIN" doctor >/dev/null
"$LEVER_BIN" score "status check" --leverage-type infrastructure --constraint "plugin wrapper must prove CLI reachability" --compounding 4 --reversibility 5 --control 5 --optionality 4 >/dev/null
"$LEVER_BIN" agent-build "status check repeat work" --role "Status check agent" --repeatability 4 --boundedness 4 --proof-loop 4 --memory-fit 3 --refusal-boundary 4 --approval-risk low >/dev/null
"$LEVER_BIN" lessons --limit 1 >/dev/null
"$LEVER_BIN" distill --limit 1 >/dev/null
"$LEVER_BIN" improve --focus "plugin status check" --limit 1 >/dev/null
echo "lever: ok"
