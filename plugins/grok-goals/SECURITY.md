# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in grok-goals, please report it responsibly.

**Email:** daniel@eidosagi.com

Please include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact

We will acknowledge receipt within 48 hours and provide a timeline for a fix.

## Scope

grok-goals is a local stdio MCP server. It reads and writes the pack directory named by `GROK_GOALS_PACK`. When that variable is unset, it creates an empty pack at `data/grok-goals.prim` under the process working directory. It does not:

- Send goal documents to a remote server
- Require network access to store or validate a goal
- Perform send, spend, post, or delete actions (it only records the approval policy)

Security concerns are most likely to involve:

- A pack path that points at a directory the process should not read or write
- Goal files that contain secrets, because the pack is plain JSON on disk
- Information disclosure if a live pack is committed or pasted into an issue

Set `GROK_GOALS_PACK` to a directory on the machine that runs the server. Keep that directory out of git. The fictional files under `examples/` are the only goal documents this repository ships.
