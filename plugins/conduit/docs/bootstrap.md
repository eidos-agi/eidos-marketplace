# Conduit Private Bootstrap

Use this when an agent needs to find and verify the private Conduit source of
truth on Daniel's machine.

## Find the Repo

```bash
cd /Users/dshanklin/repos-personal/conduit
git remote -v
gh repo view dshanklin-bv/conduit --json isPrivate,nameWithOwner,url
```

Expected:

- `nameWithOwner` is `dshanklin-bv/conduit`.
- `isPrivate` is `true`.
- The local checkout is `/Users/dshanklin/repos-personal/conduit`.

## First Reads

```bash
scripts/conduit registry --json
scripts/conduit targets
sed -n '1,220p' docs/dependency-map.md
sed -n '1,220p' docs/secret-handling.md
```

## First Proof

```bash
scripts/conduit check-macs --json
```

This appends proof rows under `registry/conduit-proofs/`. A failure is still a
useful proof record; report the exact failing conduit and stderr.

## Plugin Prompt Contract

The `@conduit` skill should answer from the smallest live command:

- Registry/model question: `scripts/conduit registry --json`
- Reachability question: `scripts/conduit doctor <machine> --json`
- Completion claim: `scripts/conduit proof --target <machine> --json`
- All-Mac health: `scripts/conduit check-macs --json`

Always distinguish registry facts from fresh proof facts.
