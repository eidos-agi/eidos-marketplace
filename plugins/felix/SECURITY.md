# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Felix, please report it responsibly.

Use a private channel with the maintainer rather than opening a public issue for sensitive reports.

Please include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact

We aim to acknowledge critical reports within 48 hours.

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest private alpha | Yes |

## Disclosure Policy

Felix follows coordinated disclosure. Please give maintainers reasonable time to address the issue before public disclosure.

## Agentic Threat Notes

Felix may eventually scaffold or repair other agent repos. Treat generated commands, repo paths, install hooks, and CI files as sensitive behavior surfaces. Felix should never write secrets into Git, Scridos, logs, or chat.

