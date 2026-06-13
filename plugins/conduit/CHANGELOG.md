# Changelog

All notable changes to Conduit are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-06-13

### Added
- Registry model: `Machine`, `Conduit` (access path), `Workload`, and append-only
  `Conduit proof` rows (`registry/*.toml`, `registry/conduit-proofs/*.jsonl`).
- CLI (`scripts/conduit`): `registry`, `machines`, `conduits`, `services`,
  `workloads`, `targets`, `doctor`, `proof`, `check-macs`, `run`, `sync`,
  `inventory-repos`, `plugin deploy`.
- GitHub Actions cloud primary (`conduit-health.yml`): ephemeral tailnet node runs
  `check-macs` every 30 min and commits proofs to `main`.
- Per-machine account registry (`registry/accounts.toml`) and `scripts/transition`
  sync wrapper.
- Mesh conventions doc (`docs/mesh-conventions.md`): SSH-over-Tailscale transport,
  shared `conduit_cloud` identity, addressing by tailnet IP.

### Fixed
- Cyprus (`rentamac-cyprus-01`) SSH auth: `conduit_cloud` public key installed; all
  three machines now prove `ok: true`.

[Unreleased]: https://github.com/dshanklin-bv/conduit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/dshanklin-bv/conduit/releases/tag/v0.1.0
