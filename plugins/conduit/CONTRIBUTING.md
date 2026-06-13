# Contributing to Conduit

## Dev setup

Conduit is pure-stdlib Python (3.11+ for `tomllib`) plus a Bash launcher. No
third-party dependencies.

```bash
git clone git@github.com:dshanklin-bv/conduit.git
cd conduit
# launcher auto-selects a 3.11+ interpreter; override with CONDUIT_PYTHON
./scripts/conduit registry --json
```

## Tests

```bash
for t in tests/test_*.sh; do bash "$t"; done
```

CI runs the same suite on Python 3.11 / 3.12 / 3.13.

## Conventions

- The **registry** (`registry/*.toml`) is the source of truth; resolve work through
  it, never hardcode SSH aliases.
- Reach machines by **tailnet IP** from off-LAN callers (see
  `docs/mesh-conventions.md`).
- **Never commit secrets** — see `SECURITY.md` and `docs/secret-handling.md`. Only
  public key ids, hostnames, and vault/keychain references belong in the repo.
- Proof rows are append-only; do not rewrite history under `registry/conduit-proofs/`.

## Pull requests

Keep changes scoped, add/extend a test for behavior changes, and update
`CHANGELOG.md` under `[Unreleased]`.
