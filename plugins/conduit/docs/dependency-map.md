# Conduit Dependency Map

Conduit owns machine targeting, access paths, workload placement policy, and
proof records. It does not own every service that may run on those machines.

## Machines

| Machine | Role | Trust | Current Conduit Status |
| --- | --- | --- | --- |
| `mac-mini-01` | Personal-local substrate, plugin host, local-first services, finance evidence | `personal_local` | SSH reachable in latest proof |
| `daniel-laptop-01` | Personal-local source evidence, repos, photos, trip data, token pointers | `personal_local` | SSH reachable when laptop is online |
| `rentamac-cyprus-01` | Rented remote capacity, experiments, overflow, remote builds | `rented_remote` | SSH auth blocked in latest proof |

## Conduits

| Conduit | Machine | Access | Source of Truth |
| --- | --- | --- | --- |
| `ssh-mac-mini-01` | `mac-mini-01` | `dshanklin@Daniels-Mac-mini.local` by default | `registry/conduits.toml` |
| `ssh-daniel-laptop-01` | `daniel-laptop-01` | `dshanklinbv@daniels-macbook-pro.tail0ffb4a.ts.net` by default | `registry/conduits.toml` |
| `ssh-rentamac-cyprus-01` | `rentamac-cyprus-01` | `rentamac@rentamac-1` by default | `registry/conduits.toml` |

## Workloads

| Workload | Preferred Machine | Fallback | Policy |
| --- | --- | --- | --- |
| `tally-cfo` | `mac-mini-01` | `rentamac-cyprus-01` | Use Cyprus only if Daniel explicitly asks or approves fallback |
| `conduit` | `mac-mini-01` | `rentamac-cyprus-01` | Self-host on the owned Mac mini once SSH is configured |

## Service Inventory

See `registry/services.toml` for the current repo-known services. This file is
intentionally small until Conduit has run a structured inventory on each
machine.

## What Conduit Can Know From This Repo

- Durable machine identities.
- SSH conduit defaults and override env vars.
- Preferred workload placement.
- Latest committed or working-tree proof records.
- Whether a failure was endpoint, host-key, or auth related when stderr records it.

## What Conduit Cannot Know From This Repo Alone

- Complete live process inventory.
- Complete DNS and vendor topology.
- Credential truth or recovery paths.
- Whether a remote service works unless a proof command captured it.
- Whether uncommitted proof rows are durable.

## Next Dependency Work

1. Add structured service inventory for each Mac after live read-only inspection.
2. Add workload-specific deploy and rollback proofs.
3. Link DNS/vendor dependencies when they become relevant to a workload.
4. Keep secrets out of the repo; only store vault/keychain metadata references.
