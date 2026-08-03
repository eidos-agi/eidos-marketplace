#!/usr/bin/env bash
# Pull vendor submodules and regenerate composite lexicon.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .gitmodules ]] || ! grep -q 'vendor/' .gitmodules 2>/dev/null; then
  echo "No vendor submodules yet. Run: ./scripts/init-vendors.sh"
  exit 0
fi

echo "→ submodule update --remote"
git submodule update --init --remote --merge

echo "→ merge lexicon"
python3 "$ROOT/scripts/merge-lexicon.py"

echo "→ done. Review git diff references/banned-words.md before commit."
