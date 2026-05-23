---
name: use-felix-cli
description: Use when the user asks about Felix, agent scaffolding, agent standards, maintainer agents, repo health for an agent, pre-scaffold interviews, have/want/dont-want framing, AGENTS.md wakeup files, or whether a new agent should exist. This skill tells Codex to call the installed `felix` CLI first and use `felix-of-felix` only for maintaining public Felix itself.
---

# Use Felix CLI

Use the installed `felix` CLI for Felix-shaped work. Felix is the agent-builder and maintainer for agent ecosystems; Codex should not reimplement Felix's standards from memory when the live CLI can progressively reveal them.

## Primary Rule

Run the smallest relevant `felix` command first, then answer from live output and repo evidence.

Useful entrypoints:

```bash
felix --help
felix doctor
felix status
felix boundaries
felix standards
felix roadmap
felix agent-template
felix interview <agent-name> --purpose "<purpose>"
felix classify "<discovery or proposed action>"
felix scaffold-plan <agent-name>
felix agents --help
felix repos --help
felix plugin doctor <plugin-or-repo-path>
felix plugin plan <plugin-or-repo-path>
```

Use `felix-of-felix` only when the task is about maintaining public Felix itself:

```bash
felix-of-felix --help
felix-of-felix status
felix-of-felix maintain
felix-of-felix assess
felix-of-felix judge
felix-of-felix classify "<proposed Felix change>"
```

## Architecture Principle

Felix follows the Eidos CLI-first progressive-reveal standard. Plugins and MCP shims are signposts. The Felix CLI owns the deeper agent-building method, including standards, interviews, repo decisions, public/private boundaries, and proof loops.

Prefer this shape:

```text
Codex plugin -> felix CLI -> standards/interview/scaffold/health commands -> repo changes
```

Do not load or restate the whole Felix method unless the task requires it. Ask Felix for the next layer.

## When To Use Felix

Use Felix when the task involves:

- Creating or evaluating a new agent, CLI, maintainer, router, auditor, librarian, communicator, or operator.
- Deciding whether a repeated workflow deserves a dedicated repo.
- Designing `AGENTS.md` wakeup files and repo memory substrate.
- Framing an agent around `have`, `want`, and `don't want`.
- Running a pre-scaffold interview before creating durable agent software.
- Checking whether an agent repo has standards, proof, tests, docs, and boundaries.
- Keeping reusable public standards separate from private owner-specific context.

## Source-Of-Truth Rules

- Use live `felix` CLI output before stale memory, old repo notes, or guesses.
- Read the target repo's `AGENTS.md` and README before changing agent behavior.
- Treat Felix outputs as evidence for Codex to reconcile, not verdicts to parrot.
- If Felix reports missing prerequisites or unclear boundaries, report the blocker plainly.
- On Daniel's machine, the installed `felix` command may be the private Felix CLI. If a public Felix command such as `plugin doctor` is missing from the installed CLI, run it from the public checkout instead: `cd /Users/dshanklinbv/repos-eidos-agi/felix && python -m felix.cli plugin doctor <path>`.

## Boundary Rules

- Public Felix contains reusable standards, scaffolds, audits, and documentation patterns.
- Private maintainer instances may contain owner-specific routing, strategy, notes, and tasks.
- Classify uncertain ideas before upstreaming them into public Felix.
- Do not leak private owner context into public agent standards.

## Plugin Boundary

This plugin contains no Felix state. It is only a Codex routing layer for the local Felix and Felix-of-Felix CLIs.
