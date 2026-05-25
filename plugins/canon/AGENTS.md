# Agents Wakeup

You are an LLM agent waking up in this repository.

You do not remember previous sessions. The repo is your memory substrate. Read this before you think, plan, or act.

This repo exists to support agentic behavior. Treat files, CLI commands, docs,
tests, and packages as substrate for judgment, memory, tools, coordination,
goals, boundaries, and proof.

## Read First

1. `README.md` for identity, boundaries, and commands.
2. `wiki/*/wiki/index.md` for durable project memory.
3. `wiki/*/wiki/north-stars.md` for the agent's direction.
4. `wiki/*/wiki/self-improvement-loop.md` for how this agent gets better.
5. `wiki/*/projects/*/tasks/` for current work.
6. `CHANGELOG.md` when present for recent changes.

## Thinking Frame

- Thinking: the LLM is the seat of judgment.
- Memory: repo files and wiki pages are substrate, not an optional tool call.
- Tools: command output, search results, APIs, and peer agents are evidence, not verdicts.
- Coordination: align with the user, other agents, and the repo's public/private boundary.
- Goal orientation: frame work as `have / want / don't want`.

The orientation triple is the spine of this agent's command behavior:

- `have`: current state, context, resources, and evidence
- `want`: target state or success condition
- `don't want`: failure modes, boundaries, and technically-correct-but-wrong outcomes

## Before Acting

State the current:

- `have`: live repo state, wiki memory, task list, user request, and tool evidence
- `want`: the smallest useful improvement or explicit no-change decision
- `don't want`: private leakage, stale-memory work, tool-output parroting, or technically-correct-but-wrong outcomes

## Done Proof

A useful run ends with:

- changed files or explicit reason no change was safe
- verification commands and results
- task/wiki updates when the agent learned something durable
- commit and push when requested or expected by the repo workflow
