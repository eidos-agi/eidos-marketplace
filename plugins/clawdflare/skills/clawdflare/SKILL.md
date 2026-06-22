# Clawdflare

Use this skill when the user asks for Cloudflare, DNS, custom-domain, SSL/TLS, cache, zone-audit, or Railway domain troubleshooting through the Eidos plugin store.

## Operating Model

- Treat the Eidos marketplace plugin as the preferred Clawdflare surface.
- Read first. Use `clawdflare doctor`, `clawdflare accounts`, `clawdflare zones`, `clawdflare dns-records <zone>`, `clawdflare ssl-status <zone>`, and `clawdflare audit <zone>` before proposing writes.
- DNS changes must start as dry-runs. Use `dns-upsert-cname` for CNAME records and only pass `--apply` after the user has authorized the local write flow.
- Never ask the user to paste Cloudflare tokens into chat. Use Clawdflare setup, Keychain, Touch ID, PIN, Knox, or a local secret-paste flow.
- Stop at human gates: Cloudflare login, Google login, passkeys, MFA, token creation, billing, registrar purchase, and any browser approval dialog.
- For Railway custom domains, prefer DNS-only CNAME records unless the app-specific proof says Cloudflare proxying is supported.

## Commands

Start with the installed CLI surface:

```bash
clawdflare doctor
```

For a Railway CNAME:

```bash
clawdflare dns-upsert-cname \
  eidosagi.com research.eidosagi.com eidos-research-production.up.railway.app \
  --comment "Eidos Research Railway service"
```

Apply only after the dry-run is correct and the local write authorization path is configured:

```bash
clawdflare dns-upsert-cname \
  eidosagi.com research.eidosagi.com eidos-research-production.up.railway.app \
  --comment "Eidos Research Railway service" \
  --apply
```

## Proof

Before closing a Cloudflare task, report:

- The plugin source used.
- The account/zone checked, without exposing tokens.
- The DNS or SSL/TLS proof command and result.
- Whether the change was dry-run only, applied, or blocked by auth.
