# Security Policy

## Reporting a vulnerability

Report security issues privately to **daniel@eidosagi.com**. Do not open public
issues for vulnerabilities. Expect an initial response within 7 days.

## Threat model

Conduit orchestrates SSH access to personal-infrastructure machines over a
Tailscale tailnet. Its trust boundaries:

- **Identity:** access uses a dedicated SSH keypair (`conduit_cloud`). The public
  key is installed on target machines; the **private key never lives in this repo**
  — only as a CI secret or in the operator's `~/.ssh`.
- **Secrets policy:** the repo stores only public key ids, hostnames, usernames,
  and vault/keychain references — never passwords, private keys, tokens, or TOTP
  seeds. See `docs/secret-handling.md`.
- **Transport:** SSH over Tailscale; targets are reached by tailnet IP. Host-key
  verification must be handled out of band before trusting a new host.
- **Proofs:** `registry/conduit-proofs/*.jsonl` capture reachability evidence and
  must be reviewed so stdout/stderr never embed secret values.

## Supported versions

The latest released minor version receives security fixes.
