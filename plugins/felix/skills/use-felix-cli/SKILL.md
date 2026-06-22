---
name: use-felix-cli
description: Use when the user asks about Felix, agent scaffolding, agent standards, maintainer agents, repo health for an agent, pre-scaffold interviews, have/want/dont-want framing, AGENTS.md wakeup files, plugin setup placement, or whether a new agent should exist. This skill tells Codex to call the installed `felix` CLI first and use `felix-of-felix` only for maintaining public Felix itself.
---

# Use Felix CLI

Use the installed `felix` CLI for Felix-shaped work. Felix is the agent-builder and maintainer for agent ecosystems; Codex should not reimplement Felix's standards from memory when the live CLI can progressively reveal them.

## Primary Rule

Run the smallest relevant `felix` command first, then answer from live output and repo evidence. For planning and health commands, preserve Felix's `Agentic instruction:` section as operating guidance, not decoration.

Useful entrypoints:

```bash
felix --help
felix doctor
felix standards
felix roadmap
felix agent-template
felix interview <agent-name> --purpose "<purpose>"
felix scaffold-plan <agent-name>
felix agents --help
felix plugin doctor <plugin-or-repo-path>
felix plugin plan <plugin-or-repo-path>
felix cleanup scan
felix cleanup plan
felix cleanup apply <item-id> --confirm
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

Felix follows the Eidos CLI-first progressive-reveal standard. Plugins and MCP shims are signposts. The Felix CLI owns the deeper agent-building method, including standards, interviews, repo decisions, public/private boundaries, and proof loops. Its outputs combine evidence with concise agentic instructions so Codex knows how to interpret checks instead of treating them as raw logs.

Prefer this shape:

```text
Codex plugin -> felix CLI -> standards/interview/scaffold/health commands -> repo changes
```

Do not load or restate the whole Felix method unless the task requires it. Ask Felix for the next layer.

## When To Use Felix

Use Felix when the task involves:

- Creating or evaluating a new agent, CLI, maintainer, router, auditor, librarian, communicator, or operator.
- Deciding whether a repeated workflow deserves a dedicated repo.
- Cleaning up duplicate plugins/software or deciding which copy is canonical.
- Improving plugin quality by exposing distribution, validation, and duplicate-code gates.
- Designing `AGENTS.md` wakeup files and repo memory substrate.
- Framing an agent around `have`, `want`, and `don't want`.
- Running a pre-scaffold interview before creating durable agent software.
- Checking whether an agent repo has standards, proof, tests, docs, and boundaries.
- Keeping reusable public standards separate from private owner-specific context.

## Plugin Setup Placement

When setting up a plugin, plugin repo, or plugin distribution path, Felix must not assume the GitHub owner or local repo root. Ask the user where it belongs before creating, moving, publishing, or wiring plugin source.

Felix should know and present the live options:

```bash
find "$HOME" -maxdepth 1 -type d -name 'repos-*' | sort
gh org list
gh auth status
```

Default placement guidance:

- Personal infrastructure or owner-specific plugins: local root `$HOME/repos-personal`, GitHub owner `dshanklin-bv`, private unless explicitly approved otherwise.
- Eidos AGI reusable platform plugins: local root `$HOME/repos-eidos-agi`, GitHub org `eidos-agi`.
- Company/domain plugins: use the matching local root and GitHub org, such as `repos-greenmark-waste-solutions` with `greenmark-waste-solutions`, `repos-aic-holdings` with `aic-holdings`, `repos-eidos-capital` with `eidos-capital`, or `repos-momentito-ai` with `momentito-ai`.

The placement question should cover three fields: local folder, GitHub owner/org, and visibility. If the user's wording already clearly answers all three, state the inferred placement and proceed.

## Machine And Migration Boundary

When plugin work involves another machine, a move from laptop to Mac mini, or a remote/local comparison, Felix should coordinate with Transition and Conduit instead of guessing from paths:

```bash
transition classify "<plugin or agent work>"
transition inventory
conduit doctor mac-mini-01
conduit proof --target mac-mini-01
```

Transition decides whether the work should move, stay, or be reviewed. Conduit proves the target machine and access path. Felix still owns canonical-source discipline, duplicate-copy cleanup, and plugin validation after the machine boundary is proven.

## Source-Of-Truth Rules

- Use live `felix` CLI output before stale memory, old repo notes, or guesses.
- Treat `Agentic instruction:` output as Felix's current operating protocol for the command.
- Read the target repo's `AGENTS.md` and README before changing agent behavior.
- For duplicate plugin/software cleanup, identify the canonical source first, then inventory derived copies, sync outward, validate, and only then retire stale copies.
- Prefer `felix cleanup scan` and `felix cleanup plan` before manual cleanup. Use `felix cleanup apply <item-id> --confirm` only for a specific safe item returned by the plan.
- Do not duplicate business logic across Codex plugins, Claude plugins, MCP shims, marketplace bundles, installed caches, or source repos.
- Treat Felix outputs as evidence for Codex to reconcile, not verdicts to parrot.
- If Felix reports missing prerequisites or unclear boundaries, report the blocker plainly.
- If the installed `felix` command is missing a documented public command such as `plugin doctor`, refresh the public Felix install from `$HOME/repos-eidos-agi/felix` and then rerun the documented command.

## Boundary Rules

- Public Felix contains reusable standards, scaffolds, audits, and documentation patterns.
- Private maintainer instances may contain owner-specific routing, strategy, notes, and tasks.
- Classify uncertain ideas before upstreaming them into public Felix.
- Do not leak private owner context into public agent standards.

## Plugin Boundary

This plugin contains no Felix state. It is only a Codex routing layer for the local Felix and Felix-of-Felix CLIs.
