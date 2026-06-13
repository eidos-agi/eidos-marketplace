---
name: use-conduit
description: Use when work must be built, moved, verified, or run through Daniel's machine conduits; when distinguishing mac-mini-01 from rented remote Macs; or when deploying personal infrastructure plugins such as Tally to the right machine.
---

# Use Conduit

Use this plugin when the user wants Codex to build, sync, verify, or operate personal infrastructure through a known machine conduit.

## Primary Rule

Run the smallest relevant local CLI command first, then answer from live output:

```bash
/Users/dshanklin/repos-personal/conduit/scripts/conduit registry --json
/Users/dshanklin/repos-personal/conduit/scripts/conduit targets
/Users/dshanklin/repos-personal/conduit/scripts/conduit doctor mac-mini-01 --json
/Users/dshanklin/repos-personal/conduit/scripts/conduit proof --target mac-mini-01 --json
```

If that checkout is missing, try the installed plugin path:

```bash
/Users/dshanklin/plugins/conduit/scripts/conduit registry --json
```

## Data Model

- Machines are durable assets: `mac-mini-01`, `rentamac-cyprus-01`.
- Conduits are access paths to machines: `ssh-mac-mini-01`, `ssh-rentamac-cyprus-01`.
- Workloads are things to deploy or run: `tally-cfo`, `conduit`.
- Conduit proof records are JSONL observations under `registry/conduit-proofs/`.

Prefer commands that resolve through this model instead of hardcoding an SSH host.

## Plain-English Prompt Routing

Map Daniel's plain-English prompt to the smallest command that proves the answer:

- "what machines do you know about?" -> `scripts/conduit registry --json`
- "which Mac should Tally deploy to?" -> `scripts/conduit workloads` and `scripts/conduit registry --json`
- "is the apartment Mac mini reachable?" -> `scripts/conduit doctor mac-mini-01 --json`
- "check every Mac" -> `scripts/conduit check-macs --json`
- "prove the Mac mini before claiming work is done" -> `scripts/conduit proof --target mac-mini-01 --json`
- "run hostname on Cyprus" -> `scripts/conduit run --target rentamac-cyprus-01 -- hostname`
- "sync this plugin to the Mac mini" -> `scripts/conduit sync <source> <dest> --target mac-mini-01`

When answering, say whether the claim comes from registry data or from fresh
proof output. If the repo only has registry data, do not present it as live
reachability.

## Machine Boundary

- `mac-mini-01` means Daniel's personally owned apartment Mac mini at 220 E Broadway Ave Apt 1229.
- Charlotte is purchase provenance only.
- `rentamac-cyprus-01` is the rented remote Mac through Rent a Mac, currently known from SSH inventory as `rentamac` when reachable.
- Do not deploy personal-local infrastructure to `rentamac-cyprus-01` unless the user explicitly asks for the rented machine.

## Safety

- Do not delete remote files by default.
- Prefer `sync` without `--delete`.
- Before claiming remote work completed, run `proof`.
- If `mac-mini-01` is unconfigured, say that Conduit knows the machine identity but does not yet have a verified SSH endpoint.
