# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in the Eidos SkillOpt marketplace
wrapper, please report it responsibly.

Email: daniel@eidosagi.com

Please include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact

## Scope

This plugin is an Eidos workflow wrapper around the upstream Microsoft SkillOpt
project. It does not collect telemetry, send data to a remote server, or modify
live agent skills by itself.

Security concerns are most likely to involve:

- accidental inclusion of secrets or private logs in rollout datasets
- unreviewed deployment of generated `best_skill.md` artifacts
- command injection through local experiment paths
- confusing upstream source state with Eidos audit approval

Always redact trajectories before optimization and require human review before
deploying a generated skill into a live agent workflow.
