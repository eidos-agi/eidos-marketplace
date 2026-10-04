# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in grok-canopy, please report it responsibly.

**Email:** daniel@eidosagi.com

Please include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact

We will acknowledge receipt within 48 hours and provide a timeline for a fix.

## Scope

grok-canopy ships a local parent-pointer check and a BotScore JSON store. The check reads profiles under `/home/box/agent-data/agents` on the machine where it runs. It does not:

- Send profiles or scores to a remote server
- Require network access to check parents or read the store
- Change parents, wake cases, or scores

Security concerns are most likely to involve:

- Running the check against an agent directory the process should not read
- Copying additional private packs into this repository

The published store is `scripts/store/botscore.json`. Keep other personal data out of git.
