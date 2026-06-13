#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Match the sparse PATH Codex gets over non-interactive SSH on Daniel's MacBook.
export PATH="/Users/dshanklinbv/.cargo/bin:/usr/bin:/bin:/usr/sbin:/sbin"

output="$(./scripts/conduit doctor mac-mini-01)"

if [[ "$output" != *"doctor: mac-mini-01 via ssh-mac-mini-01"* ]]; then
  echo "expected mac-mini-01 doctor output" >&2
  echo "$output" >&2
  exit 1
fi
if [[ "$output" != *"- ok: ssh - Daniels-Mini"* ]]; then
  echo "expected ssh proof against Daniels-Mini" >&2
  echo "$output" >&2
  exit 1
fi
