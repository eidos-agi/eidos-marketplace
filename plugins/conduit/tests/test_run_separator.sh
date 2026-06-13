#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

mkdir -p "$tmpdir/bin"
cat >"$tmpdir/bin/ssh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail

if [[ "$*" == *" -- "* ]]; then
  echo "unexpected separator passed to ssh: $*" >&2
  exit 2
fi

echo "$*"
SH
chmod +x "$tmpdir/bin/ssh"

output="$(PATH="$tmpdir/bin:$PATH" ./scripts/conduit run --target daniel-laptop-01 -- echo ok)"

if [[ "$output" != *"echo ok"* ]]; then
  echo "expected remote command in ssh invocation" >&2
  exit 1
fi
