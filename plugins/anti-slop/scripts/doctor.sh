#!/usr/bin/env bash
# Report freshness of upstream vendors and composite lexicon.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "anti-slop doctor"
echo "root: $ROOT"

if [[ ! -f references/banned-words.md ]]; then
  echo "FAIL: missing references/banned-words.md"
  exit 1
fi
echo "OK: banned-words.md present ($(wc -l < references/banned-words.md) lines)"

if [[ -f .gitmodules ]]; then
  echo "submodules:"
  git submodule status || true
else
  echo "WARN: no .gitmodules — run ./scripts/init-vendors.sh"
fi

# age of banned-words
if stat -f %m references/banned-words.md >/dev/null 2>&1; then
  mtime=$(stat -f %m references/banned-words.md)
else
  mtime=$(stat -c %Y references/banned-words.md)
fi
now=$(date +%s)
age_days=$(( (now - mtime) / 86400 ))
echo "banned-words age: ${age_days}d"
if (( age_days > 14 )); then
  echo "WARN: lexicon older than 14 days — run ./scripts/sync-upstream.sh"
fi

echo "skills:"
ls -1 skills
echo "doctor done"
