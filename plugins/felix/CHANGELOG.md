# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning once public releases begin.

## [Unreleased]

### Added

- PyPI release path for the `eidos-felix` package, including Hatchling build
  metadata, trusted-publisher workflow, build verification in CI, and release
  documentation.
- `felix cleanup scan`, `felix cleanup plan`, and guarded `felix cleanup apply` for duplicate plugin/software cleanup.
- `Agentic instruction:` sections and JSON `agentic_instruction` arrays for plugin planning, plugin doctor, and cleanup commands.

### Added
- Felix CLI for agent registry, standards, roadmap, doctor, and scaffold planning.
- `felix check` command for the standard local maintenance pass.
- Scridos wiki with project, milestones, and task list.
- Public credits for Karpathy's `llm-wiki` gist and `Pratiyush/llm-wiki`.
- Live `agentic-context` command and standard for fetching Daniel Shanklin's Agentic Intelligence gist before the LLM thinks.
- Agent command standard for `have / want / don't want` orientation and tool-output reconciliation.
- Reusable Python agent CLI template with `agentic-context`, `agentic-context-source`, and `agent` commands.
- Dry-run-first `felix scaffold <name>` command for generating starter agent repos from Felix templates.
- `felix brand-safety` audit plus generated scaffold brand-safety tests.
- `felix interview <name>` pre-scaffold role-boundary and overlap interview.
- Agentic Intelligence primitive standards for thinking, tools, memory, coordination, hierarchy, and North Star goal-orientation.
- AGENTS.md wakeup template for fresh LLM agents entering a repo.
- Registered Knox, Capcom, and Dewey as planned agents.
- FOSS Forge health files and self-documentation.
- Original Felix builder mascot.

## [0.1.0] - 2026-05-03

### Added
- Initial private alpha.
