---
name: canon
description: Use when defining, enforcing, or reviewing agent operating standards after code, repo, plugin, workflow, or agent changes need proof gates, verification loops, AGENTS.md contracts, CI checks, or a durable definition of done.
---

# Canon

Canon is the canonical standards layer for agentic software work. Use it after
substantive code, repo, plugin, workflow, or agent changes when the user wants
standards enforced across Codex, Claude Code, CI, local scripts, or source-owned
plugin surfaces.

## Core Rule

Instruction files shape behavior. Executable checks enforce behavior. Prefer
the repo's deterministic verification commands over model self-assessment.

## Workflow

1. Identify the current repo and source-owned standard before editing generated
   caches, installed plugin copies, or marketplace bundles.
2. Read the nearest `AGENTS.md`, `README.md`, and verification docs before
   changing behavior.
3. Frame the work as `have`, `want`, and `don't want` when the task is broad or
   enforcement-related.
4. Add or update scripts for deterministic, repeated shell work.
5. Add or update executable gates for standards that must be reliable.
6. Run the narrowest meaningful verification command before claiming completion.

## Enforcement Stack

Use this order:

- `AGENTS.md` and skills for operating behavior
- repo scripts for deterministic local checks
- tests, linters, type checks, and security scans for hard signals
- CI gates for merge enforcement
- plugin packaging for reuse across repos and developers

## Boundaries

Canon does not create agents; use Felix for scaffolding and agent ecosystem
design. Canon does not own evidence loops; use Eidos for tracked execution.
Canon does not own target scoreboards; use Converge for target/probe grids,
drift monitors, and repair loops.

## Commands

```bash
canon doctor
canon check
canon verify
```

Treat command output as evidence to reconcile, not as a verdict to parrot.
