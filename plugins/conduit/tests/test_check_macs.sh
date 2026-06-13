#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

mkdir -p "$tmpdir/bin" "$tmpdir/proofs"
cat >"$tmpdir/bin/ssh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail

args="$*"
if [[ "$args" == *"rentamac"* ]]; then
  echo "ssh: connect to host rentamac port 22: Operation timed out" >&2
  exit 255
fi

printf 'hostname=Daniels-Mini\n'
printf 'user=dshanklin\n'
printf 'pwd=/Users/dshanklin\n'
printf 'ProductName:\t\tmacOS\n'
SH
chmod +x "$tmpdir/bin/ssh"

set +e
output="$(PATH="$tmpdir/bin:$PATH" CONDUIT_PROOFS_DIR="$tmpdir/proofs" ./scripts/conduit check-macs --timeout 1 2>&1)"
status=$?
set -e

if [[ "$status" -eq 0 ]]; then
  echo "expected check-macs to fail when rentamac is unreachable" >&2
  echo "$output" >&2
  exit 1
fi
if [[ "$output" != *"ok: mac-mini-01"* ]]; then
  echo "expected mac-mini-01 ok report" >&2
  echo "$output" >&2
  exit 1
fi
if [[ "$output" != *"ok: daniel-laptop-01"* ]]; then
  echo "expected daniel-laptop-01 ok report" >&2
  echo "$output" >&2
  exit 1
fi
if [[ "$output" != *"fail: rentamac-cyprus-01"* ]]; then
  echo "expected rentamac-cyprus-01 failure report" >&2
  echo "$output" >&2
  exit 1
fi
if [[ "$output" != *"Operation timed out"* ]]; then
  echo "expected timeout detail in report" >&2
  echo "$output" >&2
  exit 1
fi

proof_file_count="$(find "$tmpdir/proofs" -type f -name '*.jsonl' | wc -l | tr -d ' ')"
if [[ "$proof_file_count" -ne 1 ]]; then
  echo "expected one proof ledger file, got $proof_file_count" >&2
  exit 1
fi

record_count="$(wc -l < "$(find "$tmpdir/proofs" -type f -name '*.jsonl')" | tr -d ' ')"
if [[ "$record_count" -ne 3 ]]; then
  echo "expected one record per Mac, got $record_count" >&2
  exit 1
fi
