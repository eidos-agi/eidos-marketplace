---
name: use-kai-cli
description: Use when the user mentions Kai, @kai, kai CLI, founder ops, company-building workflows, Eidos internal operations, platform provisioning guardrails, Slack operations through Kai, deploy routing, idea capture, or Kai feedback.
---

# Use Kai CLI

Kai is the internal Eidos AGI founder-ops multitool. It is CLI-first and
progressive-reveal: Codex should run the local `kai` command before inventing
company process in chat.

## First Move

Run the smallest live orientation command:

```bash
kai doctor
```

If the user asks for a specific Kai domain, inspect that domain next:

```bash
kai --help
kai ops --help
kai slack --help
kai deploy --help
kai ideas --help
kai feedback --help
```

## Operating Model

Kai is a dispatcher, not a place to reimplement every specialist. Use Kai to
find the right deterministic path, then follow the owning CLI or procedure.

Active domains:

- `kai doctor`: pre-flight for local tools.
- `kai ops`: founder-ops guardrails and company procedures.
- `kai slack`: Slack read/write/manage/admin operations through the Kai Slack app.
- `kai deploy`: Railway deploy routing through `railguey`.
- `kai ideas`: pre-roadmap idea capture.
- `kai feedback`: capture misses, drifts, surprises, wins, and noise about Kai itself.
- `kai login`: bootstrap a registered platform secret into Eidos Vault.

Planned domains may appear in help output but are not necessarily implemented:
`plan`, `vision`, `decide`, `forge`, `session`, `disk`, `orient`, `llm`, `mcp`.
If a planned domain is missing, report that plainly and use the current owning
surface instead, such as Linear, Eidos CLI, Eidos Company Formation, or the
specific platform CLI.

## Company-Building Routing

For vague company-building requests, start with:

```bash
kai ops guardrails
```

Then classify the work:

- Formation/legal/tax/entity state: use the Eidos Company Formation workflow and
  verify official sources before legal/tax claims.
- Platform identity, mailbox, Workspace, credentials, or DNS: follow `kai ops`
  guardrails; prefer APIs and Eidos Vault paths; stop before mutations.
- Slack channel, message, file, user, icon, or workspace operation: use
  `kai slack --help` and the narrowest Kai Slack command.
- Deployment: use `kai deploy --help`, then `kai deploy <service>` or the
  delegated `railguey` command.
- Pre-roadmap idea: use `kai ideas add` or `kai ideas note`.
- Kai missing capability: use `kai feedback miss "<what was missing>"`.

## Safety Boundaries

Do not use Kai as permission to mutate real-world state. Ask for explicit
approval before:

- creating/changing credentials;
- filing official forms;
- changing DNS, Workspace, Slack admin state, billing, or production deployment;
- sending outbound messages;
- exposing or retrieving secret values;
- paying fees or making commitments.

Kai uses Eidos Vault for platform secrets. Do not print secrets. Prefer
path/status checks over secret reads.

## Known Frictions

Some Kai commands require a cockpit root. If a command reports:

```text
cockpit-root not found
```

set `KAI_COCKPIT_ROOT` to the intended cockpit directory for that invocation or
report the missing cockpit root as the blocker.

`kai doctor` may show optional missing tools. Treat optional missing tools as
capability gaps, not total Kai failure.

## Closeout

When work reveals a stable Kai gap, leave feedback:

```bash
kai feedback miss "wanted Kai to do X, but Y was missing"
```

When Kai successfully routes or completes a workflow, capture a win if useful:

```bash
kai feedback win "Kai routed X to Y and produced Z evidence"
```
