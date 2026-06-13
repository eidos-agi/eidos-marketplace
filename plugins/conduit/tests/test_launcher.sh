#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Match the sparse PATH Codex gets over non-interactive SSH on Daniel's MacBook.
# The launcher should still find a Python with tomllib support.
export PATH="/Users/dshanklinbv/.cargo/bin:/usr/bin:/bin:/usr/sbin:/sbin"

output="$(./scripts/conduit targets)"

if [[ "$output" != *"mac-mini-01"* ]]; then
  echo "expected mac-mini-01 in targets output" >&2
  exit 1
fi
if [[ "$output" != *"daniel-laptop-01"* ]]; then
  echo "expected daniel-laptop-01 in targets output" >&2
  exit 1
fi
if [[ "$output" != *"rentamac-cyprus-01"* ]]; then
  echo "expected rentamac-cyprus-01 in targets output" >&2
  exit 1
fi
