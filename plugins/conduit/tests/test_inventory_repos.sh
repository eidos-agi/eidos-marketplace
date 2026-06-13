#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

mkdir -p "$tmpdir/bin"
cat >"$tmpdir/bin/ssh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail

cat <<'JSON'
{
  "schema_version": "conduit.laptop_repo_inventory.v1",
  "roots": ["~/repos-personal"],
  "max_depth": 2,
  "count": 1,
  "repos": [
    {
      "path": "/Users/dshanklinbv/repos-personal/ds-dot-com",
      "name": "ds-dot-com",
      "has_omnidata": true,
      "has_railguey_reference": true,
      "has_railway_reference": true,
      "has_railway_token_alias": true,
      "has_deploy_reference": false,
      "first_hop_docs": ["infra/README.md"],
      "signals": ["omnidata", "railguey", "railway", "railway_token_alias"],
      "signal_files": ["infra/README.md"],
      "railway_token_aliases": [{"file": ".env.local", "key": "RAILWAY_TOKEN"}]
    }
  ]
}
JSON
SH
chmod +x "$tmpdir/bin/ssh"

output="$(PATH="$tmpdir/bin:$PATH" ./scripts/conduit inventory-repos --target daniel-laptop-01 --json)"

python3 - "$output" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
assert payload["ok"] is True
assert payload["machine_id"] == "daniel-laptop-01"
assert payload["conduit_id"] == "ssh-daniel-laptop-01"
assert payload["repos"][0]["has_railway_reference"] is True
assert payload["repos"][0]["has_railway_token_alias"] is True
assert payload["repos"][0]["railway_token_aliases"][0]["key"] == "RAILWAY_TOKEN"
if "secret" in sys.argv[1].lower() or "token-value" in sys.argv[1].lower():
    raise SystemExit("inventory output leaked a secret-shaped value")
PY
