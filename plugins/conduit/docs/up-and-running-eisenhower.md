# Conduit Up-and-Running Eisenhower Matrix

This repo is private at `dshanklin-bv/conduit` and is the machine/conduit
registry for Daniel's personal infrastructure. It is currently strong enough to
answer machine-targeting questions, but not yet complete enough to explain all
infra end to end.

## Urgent and Important

Do these first to make Conduit reliable as the private source of truth.

| Need | Why it matters | Proof |
| --- | --- | --- |
| Commit current registry and proof changes | Recent Mac checks and Cyprus failures are only durable if committed | `git status --short` is clean after review |
| Fix stale README source path | README points to `/Users/dshanklinbv/...`, which is not present on this computer | README names `/Users/dshanklin/repos-personal/conduit` as the live checkout |
| Keep GitHub repo private | Machine locations, SSH aliases, and proof history are private infrastructure data | `gh repo view dshanklin-bv/conduit --json isPrivate` returns `true` |
| Record current Mac reachability | Conduit should distinguish reachable owned Mac, reachable laptop, and blocked rented Mac | `scripts/conduit check-macs --json` appends proof records |
| Register laptop source evidence | Laptop-only repos/photos/trip evidence need a durable machine target | `scripts/conduit doctor daniel-laptop-01 --json` passes |
| Fix Rent a Mac Cyprus SSH auth | `rentamac-cyprus-01` is known but not usable while SSH auth fails | See `docs/blockers/cyprus-ssh-auth.md`; `scripts/conduit doctor rentamac-cyprus-01 --json` must pass |
| Make plugin CLI path robust | The plugin skill must not depend on a missing `/Users/dshanklinbv` path | `@conduit` guidance resolves the repo-local `scripts/conduit` first |

## Important, Not Urgent

Do these to make the repo explain broader infrastructure instead of only access
paths.

| Need | Why it matters | Proof |
| --- | --- | --- |
| Add service inventory per machine | The registry knows machines, not all services running on them | `registry/services.toml` or equivalent exists |
| Add laptop repo inventory | Laptop may contain repo/infra facts missing on the Mac mini | `scripts/conduit inventory-repos --target daniel-laptop-01 --json` emits sanitized JSON |
| Add workload runbooks | Workloads need deploy, proof, rollback, and owner notes | Each workload has commands and success checks |
| Add dependency map | Eidos/Reeves infra needs DNS, services, databases, plugins, and machines connected | Dependency doc links workloads to conduits and vendors |
| Add secret-handling policy references | Agents need to know where credentials are stored without seeing them | Docs use `password_path` or vault/keychain metadata only |
| Add private-source bootstrap instructions | A new agent should know how to find the private repo and verify it | `docs/bootstrap.md` or README section exists |

## Urgent, Not Important

Handle only when they block current work.

| Need | Why it matters | Proof |
| --- | --- | --- |
| Re-run proof after network changes | Reachability can drift quickly | Fresh JSONL row under `registry/conduit-proofs/` |
| Override host env vars for a session | Useful when Bonjour or Tailscale names drift | `REEVES_MAC_MINI_01_HOST` or `REEVES_RENTAMAC_HOST` used only for the session |
| Sync plugin cache from source | Needed when `@conduit` behavior lags behind this repo | Installed skill matches repo skill |

## Not Urgent, Not Important

Avoid until the core source of truth is clean.

| Need | Why defer | Proof |
| --- | --- | --- |
| Decorative docs or diagrams | Current risk is missing facts, not presentation | Skip until registry and runbooks are complete |
| Broad refactors of CLI internals | Current commands are enough for registry, proof, run, and sync | Keep changes tied to failing proof or missing model |
| Public-facing writeup | This is private infrastructure and should remain private | No public repo or public docs |

## Plain-English Prompts for @conduit

These prompts should map to deterministic Conduit commands.

| Prompt | Expected command path |
| --- | --- |
| `@conduit what machines do you know about?` | `scripts/conduit registry --json` |
| `@conduit which Mac should Tally deploy to?` | `scripts/conduit workloads` plus `registry --json` |
| `@conduit is the apartment Mac mini reachable?` | `scripts/conduit doctor mac-mini-01 --json` |
| `@conduit check every Mac and report what failed` | `scripts/conduit check-macs --json` |
| `@conduit prove mac-mini-01 before claiming work is done` | `scripts/conduit proof --target mac-mini-01 --json` |
| `@conduit run hostname on Cyprus` | `scripts/conduit run --target rentamac-cyprus-01 -- hostname` |
| `@conduit sync this plugin to the Mac mini without deleting files` | `scripts/conduit sync <source> <dest> --target mac-mini-01` |

## Current Answerability

Conduit can answer:

- Which durable machines exist.
- Which conduit reaches each machine.
- Which machine should run a known workload.
- Whether a machine was reachable at the latest proof attempt.
- Whether Cyprus is blocked by SSH auth.

Conduit cannot yet answer from repo data alone:

- Everything running on every machine.
- Full DNS, cloud, vendor, and database topology.
- Complete deployment and rollback paths for every workload.
- Credential recovery or login truth.
- Why a remote host failed beyond the captured proof stderr.
