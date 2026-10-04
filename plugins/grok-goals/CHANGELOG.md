# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-04

### Added

- Initial public release of the Grok Goals MCP server.
- Six tools: `goals_create`, `goals_get`, `goals_list`, `goals_update`, `goals_record_progress`, and `goals_set_approval_policy`.
- JSON Schema for goals, plan steps, the pack product file, and the index.
- Skill `use-grok-goals` and a fictional demo pack under `examples/grok-goals.prim`.
- `GROK_GOALS_PACK` for the local pack path an installer sets. When it is unset, the server starts an empty pack. A live goal pack is never part of this repository.
