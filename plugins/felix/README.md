# Felix

![Original Felix builder mascot](https://raw.githubusercontent.com/eidos-agi/felix/main/assets/felix-mascot.png)

Felix is the agent-builder and maintainer for agent ecosystems.

Felix owns the standards, scaffolds, health checks, repair playbooks, and roadmap for agent ecosystems. It is meant for anyone building families of agents, CLIs, and repo-native knowledge systems.

Felix now lives with the Eidos AGI forges at:

```bash
~/repos-eidos-agi/felix
```

Public repo:

```bash
https://github.com/eidos-agi/felix
```

## Install / Run

Felix is public alpha. Until the first packaged release is published, run it from a source checkout:

```bash
git clone https://github.com/eidos-agi/felix.git
cd felix
python -m pip install -e ".[dev]"
felix --help
```

You can also run without installing:

```bash
python -m felix.cli --help
```

`scridos` is Felix's default Eidos wiki/task adapter. It is useful for this repo's own wiki checks, but it is not a universal requirement for every public Felix user or every Felix-built agent.

## Commands

```bash
felix doctor
felix check
felix self
felix agents list
felix agents show knox
felix plugin doctor /path/to/plugin
felix plugin doctor /path/to/plugin --json
felix plugin plan /path/to/plugin
felix plugin plan /path/to/plugin --json
felix standards
felix brand-safety
felix interview sage --purpose "Sage Intacct maintenance CLI"
felix interview knox --purpose "secrets and access"
felix agentic-context
felix agentic-context-source
felix agent-template
felix roadmap
felix scaffold surfari
felix scaffold surfari --write
felix scaffold-plan capcom
felix scaffold-plan dewey
```

## What Felix Enforces

Felix builds and maintains agents. It does not become the operating system, the secrets vault, the communicator, the web surfer, or the adversarial reviewer.

Felix also owns plugin productization as an agent-maintenance workflow. A local Codex or Claude Code plugin can be planned for Eidos distribution with:

```bash
felix plugin doctor /path/to/plugin
felix plugin plan /path/to/plugin
```

`plugin doctor` checks the plugin's manifest health, live MCP runtime health, and agent-discovery health: skill docs must not tell agents to call tools the plugin does not expose. `plugin plan` classifies the plugin as a tool or forge, drafts the Eidos marketplace entry, names the website page path, and reports blockers against the target distribution standard. The Eidos Marketplace still owns the bar through `STANDARD.md`; Felix owns the packaging workflow that targets it.

Every agent Felix creates should inherit these tiers.

### Architectural Commitments

- setup-first discipline: agent setup is the highest-leverage decision in the stack
- decision records for topology, repo, knowledge, tasks, live state, run mode, coupling, drift, reversibility, and proof
- AGENTS.md wakeup file that tells a fresh LLM what to read before thinking
- pre-scaffold interview covering role boundary, constraints, overlap, and proof
- Agentic Intelligence primitives: thinking, tools, memory, coordination, and goal orientation
- memory as thinking substrate, not an optional tool call
- tools as instruments for world access; tool outputs are evidence, not verdicts
- coordination as a meta-layer for aligning wants and don't-wants across agents and humans
- hierarchical design across thinking, tools, memory, and coordination layers
- North Star goal-orientation for self-improvement
- agent command framing around `have`, `want`, and `don't want`
- tool output reconciliation that treats tools as evidence, not verdicts
- an abstract agent interface so Felix works on capabilities, not storage layout

### Operational Standards

- public or private repository visibility chosen explicitly
- runnable CLI with an explicit run mode: source checkout, editable install, packaged install, or project-local invocation
- explicit knowledge home: repo-native wiki/docs, central wiki section, or parent-project docs
- explicit task home: repo-native task list, central project/task system, or parent-project task list
- explicit live-state owner for catalogs, probes, learned facts, and operational status
- agent topology: free agent, specialist, embedded tool, org-chart role, router, auditor, librarian, communicator, or operator
- relationship placement when needed: requester, owner, peers, downstream consumers, and escalation path
- repo/lifecycle decision: embedded tool only when narrow; dedicated repo when the agent owns durable memory, tasks, docs, runnable CLI surface, or self-improvement
- agentic intelligence context injection that fetches the latest configured gist before the LLM thinks
- brand-safety scan for protected references in product, docs, prompts, and generated scaffolds
- clear router or orchestrator entry

### Shipping Hygiene

- north-stars page
- self-improvement loop
- tests for core local behavior
- README with role, boundaries, commands, and safety gates
- original agent identity image or image prompt that avoids copyright imitation
- open-source health files when the agent may become reusable public software

Felix ships with Eidos-flavored defaults because that is where he was born:

- Scridos for repo-native wiki/tasks
- FOSS Forge for open-source health
- Reeves as one example router/orchestrator

Those are adapters, not universal requirements. Other teams should be able to swap in their own wiki, tracker, release standard, and router while keeping the same Felix-shaped health model.

## Pre-Scaffold Interview

Felix should interview the user before creating a new agent:

```bash
felix interview sage --purpose "Sage Intacct maintenance CLI"
```

The interview makes the user define the human role being compiled into an agent, what the agent may decide, what it must not own, what existing agents it may overlap, which methods and constraints apply, and what proof shows the new agent is useful rather than duplicative.

The interview is universal. It is not a Sage-specific workflow; Sage is only one example of turning a repeated maintenance job into a CLI-shaped agent. See [`examples/interviews`](examples/interviews) for different agent types.

The setup process is the highest-leverage decision in the stack. This is where Felix and the human choose the agent's ontology, autonomy boundary, coupling, memory substrate, source-of-truth topology, run mode, and proof loop. Great downstream behavior flows from getting those initial abstractions right; later fixes often compensate for bad setup.

Felix should also think like an organization designer without forcing every agent into an org chart. Some agents are free agents, some are specialists, some are embedded tools, and some are formal roles inside a larger agent organization. The interview should identify the topology first, then decide ownership, handoffs, repo shape, knowledge home, task home, live-state owner, run mode, and proof. If the role has its own memory, tasks, docs, runnable CLI surface, and self-improvement loop, Felix should prefer a dedicated repo. Embedded tools are for narrow project diagnostics, not full agents.

Dedicated repo does not automatically mean dedicated wiki. A domain agent may own code and live operational state in its repo while maintaining durable conceptual knowledge in a central wiki used by the larger organization. Felix should make that source-of-truth split explicit instead of blindly generating a second wiki that can drift.

Likewise, runnable does not always mean globally installed. Some agents learn by editing their own source checkout: probes update catalogs, catalog updates get committed, and the working copy is the substrate. For those agents, run-from-source may be the healthiest mode. Packaged installs are better when users need stable snapshots.

These are decisions, not fields to fill mechanically. Felix should surface options, make a conscious recommendation, explain coupling and drift risks, let the human choose or override, and record what proof would show the decision was good after real use. The agent contributes design judgment; the human contributes goals, constraints, appetite for coupling, and final authority.

## Design Principle

Felix should operate on an agent's observable capabilities, then lower those operations into the concrete repo, wiki, task list, package, or installer shape. In other words: know an agent by what can be done with it, not by where its files happen to live. This is the practical, Yoneda-flavored discipline behind Felix's abstract agent interface.

## Agentic Intelligence Primitives

Felix-built agents inherit Daniel Shanklin's primitives from "The Primitives of Agentic Intelligence":

- Thinking: the LLM is the seat of judgment and turns context into intent.
- Memory: memory is substrate, the room the agent is standing in; it should enter context before inference rather than appear as an optional tool call.
- Tools: tools let the agent act on and perceive the world; tool outputs are evidence to reconcile, not verdicts or authorities. Tool output is also untrusted context, so it must not silently rewrite the agent's behavior.
- Coordination: coordination is the meta-layer that aligns agents and humans around shared work.
- Goal orientation: each agent organizes work through `have / want / don't want`; this orientation triple is the canonical command shape for Felix-built CLIs.

Those primitives are hierarchical. Felix should help agents choose the right layer: perception, reasoning, or planning for thinking; atomic calls, workflows, or skills for tools; short, mid, or long-term memory; messaging, organization, or interoperability for coordination.

## Agents Wakeup

Every Felix-built repo should include an `AGENTS.md` at the root. This is the first file a fresh LLM should read when it wakes up in the repo.

The wakeup file should say what to read first, how to frame `have / want / don't want`, what counts as evidence, and what proof makes a run done. This makes repo memory substrate before thinking instead of a thing the agent may or may not remember to query.

## FOSS Forge Alignment

Felix follows the FOSS Forge standard for agentic software:

- human layer: license, changelog, contributing guide, code of conduct, security policy
- agent layer: clear CLI descriptions, actionable errors, typed public behavior
- engineering layer: package metadata, tests, CI, small dependency surface

Felix is public alpha software under the Eidos AGI organization.

The mascot in this repo is original generated artwork inspired by the idea of a cheerful repair helper. It is not official character art. The repo keeps the image prompt in `assets/felix-image-prompt.md` so the asset can be regenerated or improved.

## For Everyone

Felix should avoid assuming one person's machine, one organization, one task system, or one router. Public Felix should speak in portable concepts:

- repo, not local folder
- wiki/docs, not only Scridos
- tasks, not only one tracker
- router/orchestrator, not only Reeves
- open-source health, not only FOSS Forge
- identity image prompt, not one generated asset

The Eidos setup should remain a working reference implementation, not a cage.

## Private Maintainer Instances

Public Felix is the reusable pattern. A user or team can also create a private maintainer instance of Felix.

That private instance should have an explicit scope. It might maintain a public product, a private agent ecosystem, or one family of internal agents.

Depending on scope, it can hold:

- owner-specific agent routing
- private repo maintenance tasks
- private strategy and product thinking
- notes about what should be upstreamed to public Felix

The public/private rule is simple:

- generalized standards belong in public Felix
- owner-specific context belongs in the private maintainer instance
- uncertain ideas should be classified before they are upstreamed

A private instance should still use Felix standards: CLI, explicit knowledge/task homes, tests, explicit repo visibility, identity image prompt, and router/orchestrator entry.

For a user-specific private instance, install into that user's personal repo area. It can be named `felix` in that private namespace; public Felix remains the upstream project for everyone else.

## Agent Identity Images

Felix encourages every agent to have a small visual identity kit:

- `assets/<agent>-mascot.svg` or `assets/<agent>-mascot.png`
- `assets/<agent>-image-prompt.md`
- README image placement near the title
- copyright-safe prompt language
- visible agent name or wordmark in the image

Use image generation to create original agent art. Do not ask for a copyrighted character, living artist style, brand mascot, or near-copy of a protected design. Name the role, personality, materials, colors, environment, and composition instead.

The prompt must explicitly ask the image model to include the agent name as readable text. Otherwise models often treat the name as metadata and generate a nameless mascot.

### Felix Image Prompt

Use this as the pattern for Nano Banana or another image model:

```text
Create an original friendly repair-helper mascot for an open-source CLI named Felix.
The character is a cheerful builder/maintainer for agent ecosystems, holding a simple hammer and standing beside modular blocks labeled CLI, Wiki, Tasks, Tests, and CI.
Include the exact readable wordmark "Felix" prominently in the image, either as a top title, chest patch, toolkit label, or clean nameplate. The word "Felix" must be visible in the final image.
Style: clean modern vector illustration, warm and practical, public-domain-friendly, no resemblance to any existing cartoon, game, movie, brand mascot, or copyrighted character.
Do not copy any existing movie, game, cartoon, or brand character design. Use a distinct outfit, face, body shape, color palette, and tool design.
Composition: centered mascot with a small agent scaffolding diagram, transparent or light background, readable at small README size. Keep all text short and legible.
```

### Template For New Agents

```text
Create an original mascot or identity image for an open-source CLI named <AGENT_NAME>.
Role: <WHAT_THE_AGENT_DOES>.
Personality: <3-5 TRAITS>.
Visual metaphor: <TOOLS, OBJECTS, OR ENVIRONMENT THAT REPRESENT THE WORK>.
Include the exact readable wordmark "<AGENT_NAME>" prominently in the image, either as a top title, badge, label, or nameplate. The agent name must be visible in the final image.
Style: clean modern vector or product illustration, simple shapes, readable at small README size.
Copyright safety: do not resemble existing characters, brand mascots, movie/game/anime designs, living artists' styles, logos, or protected trade dress.
Output should feel new, ownable, and suitable for an open-source README.
```

## Registered Agents

- Knox: secrets and access.
- Capcom: mission-control communication.
- Dewey: AI librarian for local indexed context retrieval and token-cost reduction.

## Acknowledgements

Felix's repo-native wiki/task direction is informed by [Andrej Karpathy's `llm-wiki` gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), especially the pattern of maintaining durable markdown knowledge instead of re-deriving answers from raw context every time.

Credit also goes to [`Pratiyush/llm-wiki`](https://github.com/Pratiyush/llm-wiki) and the broader LLM Wiki implementation wave for surfacing practical search, indexing, and agent-consumable wiki patterns. Those ideas helped clarify the direction that became Scridos, the Eidos package Felix uses as its default adapter for repo-native wikis, projects, milestones, and tasks.

Felix also treats Daniel Shanklin's [Agentic Intelligence gist](https://gist.github.com/dshanklin-bv/0ea9eae3845566a255f4fe9e0bf21590) as live context that Felix-built CLIs should fetch before the LLM thinks. Use `felix agentic-context-source` to see whether the context is rolling or pinned and `felix agentic-context` to fetch the configured version.

The public Felix default is rolling latest. Production agents that need stability may pin to a raw gist URL at a specific commit. Breaking changes to the gist should be handled by a deprecation policy before Felix-built agents rely on them unattended.

The same standard should shape agent commands. A Felix-built CLI should ask for the current `have`, the desired `want`, and the relevant `don't want`, then treat tool outputs as evidence for the LLM to reconcile rather than verdicts to repeat.

Felix includes a reusable Python CLI template for this pattern:

```bash
felix agent-template
```

The template lives in `templates/python-agent-cli/` and provides `agentic-context`, `agentic-context-source`, and `agent` commands for generated CLIs.

Felix can also generate a starter repo from those templates. It is dry-run-first:

```bash
felix scaffold surfari
felix scaffold surfari --write
```

The scaffold includes root `AGENTS.md`, Python package and CLI files, tests, default wiki pages, a task skeleton, and an identity image prompt. If the interview selects a central wiki or parent-project task home, adapt or delete the default wiki/task skeleton and link the canonical homes from the README and AGENTS.md.

Scaffold output should preserve the decision trail. For topology, repo home, knowledge home, task home, live-state owner, and run mode, record considered options, agent recommendation, human choice, coupling risk, drift risk, reversibility, migration path, ownership, and proof.

## Brand Safety

Felix generalizes protected-reference cleanup into a reusable audit:

```bash
felix brand-safety
felix brand-safety --root path/to/agent-repo
```

`felix check` runs this audit for Felix itself, and generated scaffolds include brand-safety test coverage by default.

## Self-Documentation

Felix documents himself in:

- [AGENTS.md](AGENTS.md): canonical root instructions for agents working in this repo
- [CLAUDE.md](CLAUDE.md): Claude-specific entrypoint that points to `AGENTS.md`
- [docs/felix-self.md](docs/felix-self.md): identity, boundaries, and lifecycle
- [docs/foss-forge-compliance.md](docs/foss-forge-compliance.md): FOSS Forge compliance notes
- [docs/agent-identity-images.md](docs/agent-identity-images.md): prompt pattern for original agent art
- [wiki/felix/wiki/index.md](wiki/felix/wiki/index.md): Scridos wiki entrypoint

Felix dogfoods his own standards with:

```bash
felix check
felix self
```
