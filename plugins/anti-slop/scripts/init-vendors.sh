#!/usr/bin/env bash
# One-time: add community anti-slop repos as submodules.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

add() {
  local url="$1" path="$2"
  if [[ -d "$path/.git" ]] || [[ -f "$path/.git" ]]; then
    echo "skip (exists): $path"
    return
  fi
  git submodule add "$url" "$path"
}

add https://github.com/jalaalrd/anti-ai-slop-writing.git vendor/jalaalrd-anti-ai-slop-writing
add https://github.com/adewale/anti-slop-writing.git vendor/adewale-anti-slop-writing
add https://github.com/petergyang/no-ai-slop.git vendor/petergyang-no-ai-slop

./scripts/sync-upstream.sh
echo "Vendors initialized."
