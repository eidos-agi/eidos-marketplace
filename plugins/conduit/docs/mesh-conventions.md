# Conduit Mesh Conventions

How the machines in the Conduit mesh talk to each other. Source of truth for
"who reaches whom, with what identity, over what transport."

## Topology

- **Cloud primary** — GitHub Actions (`.github/workflows/conduit-health.yml`),
  always-on, every 30 min. Joins the tailnet as an ephemeral node, runs
  `conduit check-macs`, commits proofs to `main`.
- **Mac backup mesh** — the Macs are standby. No auto leader-election; failover
  is manual.
- **git = the consistency layer.** The box is cattle; state lives in git
  (`origin/main`). Every machine pulls; nothing diverges silently.

## Transport

**SSH over Tailscale.** Always reach a machine by its **tailnet IP**, never by a
Bonjour `.local` name — `.local` only resolves on the same LAN, so it fails from
the cloud runner or any remote machine. (This is why `test_mac_mini_conduit.sh`
"fails" off-LAN — expected, not a break.)

## Identity

Single shared key: **`conduit_cloud_ed25519`** (`conduit-cloud@railway-primary`).

- Public key is installed in `authorized_keys` on **all three machines**.
- Private key lives ONLY as the GitHub Actions secret `CONDUIT_CLOUD_SSH_KEY`
  and in `~/.ssh/` on the operator Mac — never in this repo (see
  `docs/secret-handling.md`).
- The Tailscale auth key for the cloud runner is the `TS_AUTHKEY` repo secret —
  **reusable + ephemeral, untagged** (untagged works: ACL grants are `*→*`).

## Machines & addressing

| machine_id | tailnet IP | ssh user | endpoint_env | notes |
|---|---|---|---|---|
| `mac-mini-01` | `100.83.12.9` | `dshanklin` | `REEVES_MAC_MINI_01_HOST` | primary anchor; reliable |
| `daniel-laptop-01` | `100.72.135.59` | `dshanklinbv` | `REEVES_LAPTOP_01_HOST` | best-effort (laptop sleeps); absent ≠ failure |
| `rentamac-cyprus-01` | `100.90.162.72` | `rentamac` | `REEVES_RENTAMAC_HOST` | remote capacity/overflow |

`conduits.toml` keeps a LAN-first `endpoint_default` (Bonjour) plus the
`endpoint_env` override. **Remote callers set the env var to the tailnet IP.**

## Conduit version & runtime

- All machines + the `reeves-store/plugins/conduit` install track **`origin/main`**.
- Requires **Python 3.11+** (`tomllib`); the launcher auto-selects via
  `CONDUIT_PYTHON` / known paths (mac-mini & laptop: `~/.local/bin/python3.x`;
  Cyprus: `/opt/homebrew/bin/python3`).

## emux (optional session layer)

[emux](https://github.com/eidos-agi/emux) ("Eidos mux") is a **local tmux
session registry + agent MCP** — it is NOT a transport and does not reach remote
machines on its own. Intended future use: run emux+tmux **on each machine** and
have Conduit SSH in and drive a **persistent, resumable** session there (so an
agent can pick up where it left off), layered on top of the SSH transport above.
