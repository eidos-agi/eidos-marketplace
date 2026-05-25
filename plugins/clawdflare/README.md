# clawdflare

Opinionated Cloudflare MCP server — audit and fix your zones.

Read operations are free. Write operations require Touch ID or a PIN.

## The idea

AI agents are great at reading infrastructure and telling you what's wrong. They're less great at having unsupervised write access to your DNS and SSL settings. Clawdflare solves this by splitting access:

- **Read token** (env var) — the AI uses this freely to audit, inspect, and report
- **Write token** (macOS Keychain gated by Touch ID, or encrypted on disk) — returned only after local authorization

The AI never sees the write token. It never sees the Touch ID prompt, PIN, or decrypted secret. It gets back a success/failure result and that's it.

**[Full setup guide and security rationale →](SETUP.md)**

## Quick start

```bash
pip install -e ".[dev]"

# 1. Store a token for reuse
clawdflare store-token --account work
# On macOS, prefer Touch ID for write authorization:
clawdflare store-token --account work --write-auth touchid

# Or migrate an existing PIN-protected write token into Touch ID:
clawdflare migrate-touchid --account work

# 2. Go
clawdflare audit example.com
```

For AI-assisted work where the human pastes a token into a secure local prompt:

```bash
secret-paste run --env CLOUDFLARE_API_TOKEN -- \
  clawdflare store-token \
    --account jetta \
    --token-name jetta-status-cloudflare \
    --from-env CLOUDFLARE_API_TOKEN
```

`store-token` verifies the token, saves it as the read token, and encrypts it as
the write token behind a PIN for future reuse. It never prints the token.

## Usage

### CLI

```bash
clawdflare zones                    # list all zones
clawdflare audit example.com        # audit against best practices
clawdflare fix example.com          # dry-run: show what would change
clawdflare fix example.com --apply  # apply fixes (PIN required)
clawdflare ssl-status example.com   # SSL/TLS summary
clawdflare dns-records example.com  # list DNS records
clawdflare set-setting example.com ssl full  # set a setting (PIN required)
clawdflare purge-cache example.com --everything  # purge cache (PIN required)
clawdflare store-token --account work # store or rotate a reusable token
```

### MCP Server

```bash
clawdflare serve
```

Add to Claude Code settings:

```json
{
  "mcpServers": {
    "clawdflare": {
      "command": "uvx",
      "args": ["--from", "clawdflare", "clawdflare", "serve"],
      "env": {
        "CLOUDFLARE_API_TOKEN": "your-read-only-token"
      }
    }
  }
}
```

## Opinions

Clawdflare ships with opinionated defaults for security and performance. Run `clawdflare audit` to see how your zone stacks up:

- **SSL**: Full mode (not flexible — flexible leaves origin traffic unencrypted)
- **HTTPS**: Always redirect, HSTS with 1-year max-age and subdomains
- **TLS**: Minimum 1.2 (1.0/1.1 are deprecated and vulnerable), TLS 1.3 with 0-RTT
- **HTTP/3**: Enabled (QUIC reduces latency, especially on mobile)
- **Cache**: 4-hour browser TTL
- **Security**: Email obfuscation, hotlink protection, automatic HTTPS rewrites

Every opinion includes a reason. Disagree? Override with `clawdflare set-setting`.

## Security model

| Operation | Token used | AI can see token? | Authorization |
|---|---|---|---|
| `zones`, `audit`, `dns-records`, `ssl-status`, `zone-settings` | Read (env var) | Yes | None needed |
| `fix --apply`, `set-setting`, `purge-cache` | Write (Touch ID Keychain or encrypted vault) | Never | Touch ID when configured, PIN fallback |

See [SETUP.md](SETUP.md) for the full threat model and rationale.
