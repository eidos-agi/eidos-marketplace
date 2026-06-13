# Conduit

Registry-backed Codex plugin for Daniel's machine conduits.

## Ownership

This is a personal infrastructure repo. The durable source lives at:

```text
/Users/dshanklin/repos-personal/conduit
```

The plugin install path may point here, but the repo under `repos-personal` is
the source of truth.

## Role

`conduit` owns the model and commands for reaching personal infrastructure machines. It is deliberately not a finance plugin and not tied to one Mac mini.

## Data Model

- `Machine`: an asset such as `mac-mini-01` or `rentamac-cyprus-01`.
- `Conduit`: a way to reach a machine, such as `ssh-mac-mini-01`.
- `Workload`: something that can be deployed, such as `tally-cfo`.
- `Conduit proof`: an observed record that a conduit reached the intended machine.

## Boundaries

- `mac-mini-01` is the owned apartment Mac mini physically set up at 220 E Broadway Ave Apt 1229.
- Charlotte is purchase provenance only, not the machine identity.
- `rentamac-cyprus-01` is the Rent a Mac Cyprus machine and must not be treated as `mac-mini-01`.
- Tally can depend on Conduit for build/deploy/proof, but Tally owns CFO judgment.

## Registry

```text
registry/
  machines.toml
  conduits.toml
  services.toml
  workloads.toml
  conduit-proofs/
```

The registry is the source of truth for machine identity and conduit selection. Commands should resolve workloads through the registry instead of hardcoding SSH aliases.

## Commands

```bash
scripts/conduit registry --json
scripts/conduit targets
scripts/conduit machines
scripts/conduit conduits
scripts/conduit services
scripts/conduit workloads
scripts/conduit doctor mac-mini-01
scripts/conduit proof --target mac-mini-01
scripts/conduit check-macs
scripts/conduit run --target mac-mini-01 -- hostname
scripts/conduit sync ./some-plugin ~/plugins/some-plugin --target mac-mini-01
scripts/conduit plugin deploy ./some-plugin --target mac-mini-01
```

The `scripts/conduit` launcher selects a Python with `tomllib` support. Set `CONDUIT_PYTHON` to override the interpreter explicitly.

## Configuration

The apartment Mac mini must be configured before remote commands can run:

```bash
export REEVES_MAC_MINI_01_HOST=<ssh-host-or-alias>
export REEVES_MAC_MINI_01_USER=<ssh-user>
```

If `REEVES_MAC_MINI_01_HOST` is absent, the CLI reports `mac-mini-01` as known but unconfigured.

## Proof

Before claiming anything was built through a conduit, run:

```bash
scripts/conduit proof --target mac-mini-01
```

Successful or failed proof attempts append JSONL records under `registry/conduit-proofs/`.

To verify every Mac in the registry and record a report for each one, run:

```bash
scripts/conduit check-macs
```

The command exits non-zero when any Mac is unreachable. Use `--json` for a machine-readable report.

## Readiness Docs

The repo now includes the private operating docs needed for agents to answer
plain-English Conduit questions without guessing:

```text
docs/up-and-running-eisenhower.md
docs/bootstrap.md
docs/dependency-map.md
docs/secret-handling.md
docs/runbooks/
```

Use `docs/up-and-running-eisenhower.md` for the current gap matrix and
`docs/dependency-map.md` for what Conduit can and cannot know from repo data.
