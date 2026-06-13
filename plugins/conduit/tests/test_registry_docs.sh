#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

scripts/conduit registry --json >"$tmpdir/registry.json"
python3 - "$tmpdir/registry.json" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as handle:
    data = json.load(handle)

for key in ["machines", "conduits", "services", "workloads"]:
    if key not in data:
        raise SystemExit(f"missing registry key: {key}")
    if not isinstance(data[key], list) or not data[key]:
        raise SystemExit(f"registry key must be a non-empty list: {key}")

machine_ids = {item["id"] for item in data["machines"]}
for service in data["services"]:
    if service["machine_id"] not in machine_ids:
        raise SystemExit(f"service targets unknown machine: {service['id']}")
PY

required_docs=(
  docs/up-and-running-eisenhower.md
  docs/bootstrap.md
  docs/dependency-map.md
  docs/secret-handling.md
  docs/runbooks/conduit.md
  docs/runbooks/tally-cfo.md
)

for doc in "${required_docs[@]}"; do
  if [[ ! -s "$doc" ]]; then
    echo "missing required doc: $doc" >&2
    exit 1
  fi
done

scripts/conduit services --json >"$tmpdir/services.json"
python3 -m json.tool "$tmpdir/services.json" >/dev/null
