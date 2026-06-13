# Cyprus SSH Auth Blocker

## ✅ CLOSED 2026-06-13

The `conduit_cloud_ed25519.pub` key was installed for the `rentamac` user on
`rentamac-1` (100.90.162.72) via `ssh-copy-id`. A fresh cloud proof now returns
`rentamac-cyprus-01 ok: true`. The mesh reaches Cyprus over Tailscale with the
shared `conduit_cloud` identity, same as mac-mini-01 and daniel-laptop-01.

---

## Current State (historical)

Conduit knows the rented Cyprus Mac:

```text
machine_id: rentamac-cyprus-01
conduit_id: ssh-rentamac-cyprus-01
ssh_spec: rentamac@rentamac-1
```

Latest live proof shows the endpoint is configured, but SSH authentication
fails:

```text
Permission denied (publickey,password,keyboard-interactive).
```

## What This Means

This is not a registry/model problem anymore. Conduit can resolve the target
and attempt the connection. The remaining blocker is access material or remote
account configuration.

## Do Not Do

- Do not store the Rent a Mac password in this repo.
- Do not paste private keys or passwords into docs, proof rows, or Linear.
- Do not treat Cyprus as a valid fallback until a fresh proof passes.

## Close Criteria

One of these must happen:

- The correct public key is installed for the `rentamac` user on `rentamac-1`.
- The correct SSH identity path is added as metadata-only config and the private
  key remains outside the repo.
- Daniel approves a secure credential handoff through Knox or another approved
  secret path.

Then run:

```bash
scripts/conduit doctor rentamac-cyprus-01 --json
scripts/conduit proof --target rentamac-cyprus-01 --json
scripts/conduit check-macs --json
```

The blocker is closed only when `rentamac-cyprus-01` returns `ok: true`.
