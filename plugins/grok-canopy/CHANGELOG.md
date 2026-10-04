# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-04

### Added

- Initial public release of the Grok Canopy parent-pointer check.
- `scripts/check.py` covers 124 bots. Every bot except Grok Bot has one parent. The tree has no cycle. Depth stays at most 4. The 11 wake cases stay as shipped.
- Persistent BotScore store at `scripts/store/botscore.json`, version 1, 124 bots. Scores use four penalties from a base of 100, floored at 0. Wake correction added nothing. Token burn is excluded.
