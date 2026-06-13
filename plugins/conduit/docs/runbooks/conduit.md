# Conduit Runbook

## Registry Health

```bash
scripts/conduit registry --json
scripts/conduit targets
scripts/conduit workloads
```

Success means the registry parses and the known machine/conduit/workload model
is readable.

## Prove a Machine

```bash
scripts/conduit proof --target mac-mini-01 --json
```

Use this before claiming work completed on a target machine. Proof records are
append-only JSONL under `registry/conduit-proofs/`.

## Laptop Source Evidence

The laptop is registered as `daniel-laptop-01`. It is a source-evidence
machine, not the preferred deployment target.

```bash
scripts/conduit doctor daniel-laptop-01 --json
scripts/conduit proof --target daniel-laptop-01 --json
scripts/conduit inventory-repos --target daniel-laptop-01 --json
```

`inventory-repos` is read-only and metadata-only. It reports repo paths,
first-hop docs, `.omnidata` presence, Railway/Railguey/deploy signals, and
token aliases such as `RAILWAY_TOKEN`; it must not print or copy token values.

## Check Every Mac

```bash
scripts/conduit check-macs --json
```

Expected current state:

- `mac-mini-01`: should pass when on Daniel's network or when Bonjour resolves.
- `rentamac-cyprus-01`: currently fails with SSH auth until access is repaired.

## Run a Remote Command

```bash
scripts/conduit run --target mac-mini-01 -- hostname
scripts/conduit run --target rentamac-cyprus-01 -- hostname
```

Use `--target`; do not hardcode SSH aliases in user-facing workflows.

## Sync a Plugin

```bash
scripts/conduit sync ./some-plugin ~/plugins/some-plugin --target mac-mini-01
```

Default behavior must avoid destructive deletes. Use explicit approval before
adding any delete/sweep behavior.

## Troubleshooting

- Missing endpoint: inspect `registry/conduits.toml` and env overrides.
- Host key failure: verify the host out of band before changing known_hosts.
- Permission denied: credential/access issue; do not brute force or print
  secrets.
- Timeout: check Tailscale/Bonjour/network reachability.
