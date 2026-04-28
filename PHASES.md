# Eidos Marketplace — Phased Plan

> The runnable plan for building this marketplace to the [STANDARD](STANDARD.md). Any agent or human can resume here without prior session context.

## How to use this file

1. Find the first unchecked `[ ]` task below.
2. Do it. Stay within scope — don't skip ahead.
3. Tick it `[x]`. Add a one-line note in the same line if you learned something worth keeping.
4. Commit with a message that names the phase and task: `phase 0/1: add $schema to marketplace.json`.
5. Continue to the next unchecked task.

If a task is ambiguous, look at the most recent commit's message and diff for the convention. If still unclear, escalate to the maintainer (daniel@eidosagi.com) by opening an issue, then move on to a different unblocked task.

**Do not skip Phase 2.** Living with one plugin for two weeks before adding more is the discipline. Breadth without sustained depth breaks the trust thesis.

---

## Phase 0 — Marketplace baseline (target: ~30 min)

The marketplace.json is currently missing top-level metadata. Fix that, document the standard, set discovery signals on the repo.

- [x] Add `$schema: "https://anthropic.com/claude-code/marketplace.schema.json"` to `.claude-plugin/marketplace.json` (top of file). Schema URL is aspirational — Anthropic doesn't publish a hosted schema yet; the field is harmless if unresolved.
- [x] Add top-level `description` (112 chars, matches plan).
- [x] Add top-level `version: "0.1.0"`.
- [ ] **DEFERRED** — Add `metadata.pluginRoot: "./plugins"` and shorten `source` fields. Cannot empirically verify Claude Code accepts this shape without breaking installs; deferred until we have a test environment that round-trips. Existing `./plugins/<name>` paths work today.
- [x] Rewrite `README.md` to lead with the thesis (already done in commit 4046388 + a373b00).
- [x] Set GitHub topics: `agent-tools`, `claude-code`, `claude-plugin-marketplace`, `eidos-agi`, `mcp`. Verified via `gh api`.
- [x] Archive `eidos-agi/claude-plugins`. README replaced with redirect to this repo (commit 2b5fb49); repo archived 2026-04-28. The old marketplace was a single-plugin home for slack-cc, never expanded; 0 stars, 0 forks confirmed nobody depended on it.

---

## Phase 1 — cept onboarding (target: ~30 min)

cept (`eidos-agi/cept`, on PyPI as `cept`) is the flagship Tool. It demonstrates the bar for the Tool surface (à-la-carte install, single capability, uvx shim).

- [x] Create `plugins/cept/.claude-plugin/plugin.json` with: name, description, version, author, license, keywords, homepage, repository.
- [x] Create `plugins/cept/.mcp.json`: `{"cept": {"command": "uvx", "args": ["--from", "cept", "cept"]}}`.
- [x] Add cept entry to `.claude-plugin/marketplace.json` (now 9 plugins). Source: `./plugins/cept`; category `agent-tools`; tags + homepage + license + version per pyproject.toml.
- [x] Add the `x-eidos` block: `kind.type: "tool"` with signals `["single_capability", "uvx_shim", "mcp_server"]`. `audit` block populated by the hand-audit step below.
- [x] Run `python tools/test_plugins.py cept` — PASS in 1.6s; cept v0.1.0 server responds to MCP `initialize`.
- [x] Round-trip install verified: `claude plugins marketplace update eidos-marketplace` + `claude plugins install cept@eidos-marketplace` succeeded. `claude plugins list` confirms cept@eidos-marketplace v0.1.0 installed at user scope. The first attempt failed with "Plugin not found" due to stale marketplace cache — captured as the inaugural LEARNINGS.md entry.
- [x] Hand-audit cept against [STANDARD.md](STANDARD.md). [`AUDITS/cept.md`](AUDITS/cept.md) written with grade A; all three layers PASS; `x-eidos.audit` block populated in marketplace.json. Header: `audited_by: by-hand (foss-forge not yet onboarded)`.
- [x] Commit and push.

The hand-audit is a temporary debt. [STANDARD.md § Dogfooding](STANDARD.md#dogfooding--the-marketplace-maintains-itself-with-its-own-plugins) requires `foss-forge` to be the audit tool. Phase 4 retires this debt by re-auditing cept through `/foss-check`.

---

## Phase 2 — HARD STOP. Live with cept for two weeks. (resume on or after 2026-05-12)

This phase is a *literal* pause. No plugin onboarding. No marketplace.json plugin entries added. The trust thesis only operates if we resist breadth — and cept is what we live with so we feel the friction before scaling.

**Allowed during the pause:**
- Bug fixes to cept's marketplace.json entry, plugin.json, or .mcp.json
- Updates to `STANDARD.md`, `PHASES.md`, `LEARNINGS.md`, or `AUDITS/cept.md` reflecting what we learn
- Updates to `README.md` content (not adding plugins to the table)
- Closing/triaging marketplace issues
- **Designing the `/eidos-install` skill content** — draft `cockpit-eidos/briefs/eidos-install-skill.md` covering: the interview flow ("what are you doing?"), starter-set logic per project archetype (python-package, frontend-app, research, founder-ops, etc.), the hand-off pattern to `forge-forge` for forge-specific drilldown, and the cross-ecosystem pointers (when to mention `helios`, `omni`, `eidos-v5`). Design only; ship in Phase 3.
- **Designing the `rhea` plugin entry** — draft `plugins/rhea/.claude-plugin/plugin.json` and `.mcp.json` content (do NOT add to marketplace.json yet; that's Phase 3c). rhea is the second flagship Tool, sibling to cept: where cept does proprioception (self-awareness from your own transcript), rhea does adversarial sparring (`rhea_challenge`, `rhea_debate`, `rhea_simplify`, `rhea_unstick`). Mirror cept's plugin file shapes. Verify rhea's source repo has all STANDARD.md community-health files; if any are missing, file follow-up issues against `eidos-agi/rhea`.
- **Designing the `emux` plugin entry** — draft `plugins/emux/.claude-plugin/plugin.json` and `.mcp.json` (do NOT add to marketplace.json yet; that's Phase 3d). The package is already built, public, and pushed to [eidos-agi/emux](https://github.com/eidos-agi/emux). It exposes 6 MCP tools for attaching to and driving existing tmux sessions: list, register, unregister, send keys, capture pane, run (send+wait+capture). Maintains a registry of named sessions at `~/.config/emux/registry.json`. Operates on existing sessions only — never spawns or kills. Originally born from Phase 1's stale-cache friction (autonomous marketplace install round-trips), but the design is intentionally general: any tmux session can be driven, including Claude Code sessions, shells, long-running services, etc.

**Open design questions to resolve before Phase 3 (architectural debt flagged by cept review of commit b255b13):**

- [ ] **Rollback/downgrade workflow.** What happens when `foss-forge` audited a plugin to grade A, the user installed it, and it broke in their environment? Document the user's recourse: `claude plugins uninstall <name>` plus reporting back. Decide: do we surface a "report broken" affordance? Add a section to STANDARD.md about user-side recovery vs. marketplace-side removal.
- [ ] **`/eidos-install` discovery chicken-and-egg.** How does a brand-new user find `/eidos-install` itself? Today: README + the marketplace listing. Sufficient? Or do we need: (a) `eidos-install` mentioned in every Eidos-maintained README, (b) `npx eidos-install` as a one-liner in launch posts, (c) a CLAUDE.md template that suggests it. Pick a strategy; document it.
- [ ] **Versioning model — recommender vs. source-of-truth conflict.** When `forge-forge`'s cached or in-session view of a forge differs from `marketplace.json` (e.g., recommend block changed mid-session), the rule is **`marketplace.json` always wins** (recommenders are thin readers, no internal cache or pin). Make this explicit in STANDARD.md § Onboarding vs Discovery vs Installation. Add a STANDARD.md rule: "Recommenders MUST re-read `marketplace.json` per recommendation request; no caching across requests."
- [ ] **STANDARD.md enforcement beyond Phase 7 CI.** Currently the only enforcement is the Phase 7 CI staleness check. Phase 0 also has `python tools/test_plugins.py` for marketplace.json validation. Decide: do we add (a) a pre-commit hook running `tools/test_plugins.py`, (b) a JSON Schema file checked into the repo that editors validate against in real time, (c) a `CONTRIBUTING.md` checklist that says "before submitting, run `python tools/test_plugins.py`"? Pick at least one and add it to Phase 0.

These four are *design-only* during Phase 2. The fixes (STANDARD.md rule edits, README pointers, pre-commit hook) ship in Phase 3 alongside `eidos-install` and `forge-forge`. They do not gate the calendar resume condition — but they DO inform the "is the cadence sustainable?" question. If we can't resolve a blind spot in two weeks, that's signal the bar is too high and we should simplify before scaling.

**Not allowed:**
- Onboarding *any* new plugin (eidos-install, forge-forge, foss-forge, slack-cc, anything)
- Adding entries to marketplace.json's `plugins` array
- Phase 3+ tasks of any kind

**Resume conditions** — both must be true to proceed to Phase 3:

- [ ] Calendar: today's date is on or after **2026-05-12**
- [ ] Friction journal exists: `LEARNINGS.md` has at least one entry from the live-with-cept period (a maintenance pain we noticed; the absence of any entries means we weren't actually using cept and the pause didn't accomplish its goal)
- [ ] Resume answer recorded: a one-paragraph entry in `LEARNINGS.md` answering *"Is the cadence sustainable as designed, or do we simplify STANDARD.md before scaling?"* If we simplify, do that *before* Phase 3.

If the calendar date passes but no friction was logged, extend the pause. The pause's purpose isn't time; it's lived experience. Time is the proxy.

---

## Phase 3 — Onboard the two recommenders: `eidos-install` + `forge-forge`

After the Phase 2 pause, ship both recommenders together. `eidos-install` is the user-visible front door (a progressive-reveal forge that interviews and recommends starter sets); `forge-forge` is the forge-specific recommender it delegates to. Both are forges with the recommender signals; neither installs anything. See [STANDARD.md § Tools and Forges](STANDARD.md#tools-and-forges--two-surfaces-one-bar).

### Phase 3a — Source convention + `eidos-install` (progressive-reveal forge, lives in this repo)

`eidos-install` is one skill file. It does not need its own repo — it lives inside `eidos-marketplace` itself, alongside the listings it recommends.

- [ ] Decide source convention for skill-bearing plugins that live in another repo: `{"source": {"source": "github", "repo": "eidos-agi/<name>"}}`. Document the convention as a one-liner under [STANDARD.md § How submissions work](STANDARD.md#how-submissions-work-today). For plugins that live in this marketplace repo, the existing local-source pattern (`source: "<plugin-dir>"`) applies.
- [ ] Create `plugins/eidos-install/.claude-plugin/plugin.json` (`name: eidos-install`, `description: Progressive-reveal front door for the Eidos ecosystem`, version, license).
- [ ] Move the Phase 2 design draft from `cockpit-eidos/briefs/eidos-install-skill.md` into `plugins/eidos-install/skills/eidos-install/SKILL.md` with proper YAML frontmatter (`name: eidos-install`, `description: <interview-driven recommendation skill>`).
- [ ] Add `eidos-install` entry to `marketplace.json`. `x-eidos.kind.type: "forge"` with signals `["ships_skills", "opinionated_workflow", "progressive_reveal", "delegates_to_recommenders", "cross_ecosystem_pointers"]`. Document the delegations: `x-eidos.recommend.delegates_to: ["forge-forge"]`.
- [ ] Round-trip test: `claude plugins install eidos-install`. Run `/eidos-install`. Confirm interview flow works and produces sensible starter-set recommendations for at least three project archetypes (python-package, frontend-app, founder-ops).
- [ ] Verify hand-off: when the user finishes `/eidos-install`'s starter set, the skill should explicitly mention "for ongoing forge needs, use `/forge recommend-for <project>`" — pointing them at Phase 3b's `forge-forge`.
- [ ] Hand-audit `eidos-install` against STANDARD.md. Write `AUDITS/eidos-install.md`. Populate `x-eidos.audit` block. Header: `audited_by: by-hand (foss-forge not yet onboarded)`. Community-health requirements (LICENSE, CHANGELOG, etc.) are inherited from this marketplace repo since `eidos-install` lives here.

### Phase 3b — `forge-forge` (forge recommender)

`forge-forge`'s existing MCP tools (`forge_list`, `forge_find`, `forge_for_project`, `forge_how`, `forge_info`) already match the recommender shape — they describe and recommend; they don't install. This phase makes `forge-forge` discoverable and installable from the marketplace.

- [ ] In `eidos-agi/forge-forge`, ensure top-level `.claude-plugin/plugin.json` exists; skills at `skills/<name>/SKILL.md` with YAML frontmatter; MCP server entry point declared.
- [ ] Bring `forge-forge` up to STANDARD.md community-health files. Hand-audit.
- [ ] Add `forge-forge` entry to marketplace.json. `x-eidos.kind.type: "forge"` with signals `["ships_skills", "opinionated_workflow", "coordinates_with_other_forges"]`. Empty `x-eidos.recommend.for_projects` (no other forges yet to recommend).
- [ ] **Wire `forge-forge` to read `x-eidos.recommend` from the marketplace's `marketplace.json`** as its primary registry. No internal registry; just a thin reader of the public source-of-truth. If `forge-forge` already has its own `registry.yaml` (it does, at `~/repos-eidos-agi/forge-forge/registry.yaml`), keep it for development convenience but make `marketplace.json` the production source for the published plugin.
- [ ] Round-trip test: `claude plugins install forge-forge`. Confirm `/forge list` works (will show only forge-forge itself at this point — that's correct).
- [ ] Hand-audit `forge-forge` against STANDARD.md. Write `AUDITS/forge-forge.md`. Populate `x-eidos.audit` block.
- [ ] Verify graceful degradation: confirm `forge-forge` itself and `eidos-install` can be installed *without* the other being present. The two recommenders are independent.

### Phase 3c — `rhea` (the second flagship Tool, sibling to cept)

`rhea` is to outside-perspective sparring what `cept` is to self-perspective steering. Together they form the "two mirrors" pair: cept tells you what you missed in your own trajectory; rhea tells you what an adversarial outside reader would say. Both are Tool-kind, single-capability, uvx-shim, MCP-server. The pattern is identical to cept's Phase 1 onboarding — use that as the template.

- [ ] Move the Phase 2 design draft into `plugins/rhea/.claude-plugin/plugin.json` and `plugins/rhea/.mcp.json` (mirror cept's shape).
- [ ] Verify rhea's source repo (`eidos-agi/rhea`, on PyPI as `rhea`) passes the [Layer 1 — Community Health](STANDARD.md#layer-1--community-health-humans-contributing) bar: LICENSE, README ≥20 lines, CHANGELOG following Keep a Changelog, CONTRIBUTING, COC, SECURITY. If any are missing, fix in the source repo *before* adding the marketplace entry.
- [ ] Add `rhea` entry to `marketplace.json`. `x-eidos.kind.type: "tool"` with signals `["single_capability", "uvx_shim", "mcp_server"]`.
- [ ] Run `python tools/test_plugins.py rhea` — must PASS via MCP initialize.
- [ ] Round-trip test: `claude plugins install rhea@eidos-marketplace` from a fresh session.
- [ ] Hand-audit rhea against STANDARD.md (Phase 4 will retroactively re-audit via `/foss-check`). Write `AUDITS/rhea.md`. Populate `x-eidos.audit`. Header: `audited_by: by-hand (foss-forge not yet onboarded)`.
- [ ] Update README.md plugin table to add rhea to the Tools section with description: "Adversarial sparring partner — challenge, debate, simplify, unstick. Sibling to cept."
- [ ] Update `eidos-install` skill (Phase 3a draft) to recommend rhea alongside cept in starter sets that involve significant decisions (e.g., python-package archetype, founder-ops archetype). cept + rhea together = the proprioception+critique pair.

### Phase 3d — `emux` (Tool: TUI picker + MCP server for tmux sessions)

`emux` (eidos mux) is a single tool with two front-ends over one shared registry of named tmux sessions:

- **`emux`** — TUI picker. Lists registered + live sessions. Pick one → `tmux attach`. Stale entries flagged.
- **`emux mcp`** — MCP server. Six tools for agents to drive sessions: list, register, send keys, capture pane, run.
- **`emux ls`** / **`emux register`** / **`emux unregister`** — non-interactive scripting helpers.

Built originally for autonomous marketplace install round-trips (the agent surface), but the human surface (TUI picker for "which tmux session was I in?") earned equal weight in the design. The TUI is stdlib-only — `input()` + a numbered list — so it works in any terminal including remote SSH and dumb terms.

The package is already built ([`eidos-agi/emux`](https://github.com/eidos-agi/emux), public, 13/13 tests passing, live tmux smoke + CLI smoke verified). Phase 3d onboards it to the marketplace.

MCP tool surface (6 tools, exposed via `emux mcp`):
- `tmux_sessions()` — list live tmux sessions + registry (with stale flag)
- `tmux_register(name, session, description?, tags?)` — name a session
- `tmux_unregister(name)` — drop from registry; does not touch tmux
- `tmux_send(target, keys, enter, by_registry_name)` — send keystrokes
- `tmux_capture(target, lines, by_registry_name)` — read pane + scrollback
- `tmux_run(target, command, wait_seconds, ...)` — send + sleep + capture

Phase 3d tasks:

- [ ] Publish `emux` to PyPI via OIDC trusted publisher (mirror cept's `publish.yml` pattern). Tag `v0.1.0` and push.
- [ ] Add CHANGELOG, CONTRIBUTING, COC, SECURITY files to bring up to STANDARD.md community-health bar (deferred during initial build; required before marketplace listing).
- [ ] Add CI workflow (`.github/workflows/ci.yml`) running ruff + pytest on Python 3.11/3.12/3.13.
- [ ] Move the Phase 2 design draft into `plugins/emux/.claude-plugin/plugin.json` and `plugins/emux/.mcp.json` in the marketplace repo. Mirror cept's pattern.
- [ ] Add `emux` entry to `marketplace.json`. `x-eidos.kind.type: "tool"` with signals `["single_capability", "uvx_shim", "mcp_server"]`.
- [ ] Round-trip test: from a fresh session, install emux via the marketplace, then use it to drive a tmux session running another Claude Code instance — including the recursive dogfood of using emux to verify a marketplace install in an attached session.
- [ ] Hand-audit emux against STANDARD.md. Write `AUDITS/emux.md`. Populate `x-eidos.audit`.
- [ ] Update `eidos-install` skill (Phase 3a draft) to recommend emux for project archetypes that involve marketplace operations, CI/CD work, or agent-driven session steering.

Phase 3 is complete when:
1. A user can run `claude plugins install eidos-install`, run `/eidos-install`, and walk away with a coherent starter-set install plan that includes cept, rhea, emux, and forge-forge where appropriate.
2. A user can run `claude plugins install forge-forge` and use `/forge list` directly.
3. A user can run `claude plugins install rhea` and use `/rhea_challenge` (or any rhea verb) directly.
4. A user can run `claude plugins install emux` and use `tmux_register` + `tmux_send` + `tmux_capture` to drive a registered tmux session.
5. All four plugins work standalone; none require the others.

---

## Phase 4 — Onboard `foss-forge` and bootstrap the audit dogfood

`foss-forge` is the audit instrument. We cannot trust automated audits until `foss-forge` is itself a marketplace plugin in good standing AND has self-audited.

- [ ] In `eidos-agi/foss-forge`, ensure top-level `.claude-plugin/plugin.json`, skills layout, and STANDARD.md community-health files (LICENSE, README, CHANGELOG, CONTRIBUTING, COC, SECURITY).
- [ ] Add `foss-forge` entry to marketplace.json. `x-eidos.kind.type: "forge"` with signals. `x-eidos.recommend.for_projects: ["python-package", "github-repo", "open-source-prep"]`, `pairs_with: ["security-forge", "ship-forge"]`, `preflight_check: "/foss-check"`.
- [ ] Round-trip test: `claude plugins install foss-forge`. Confirm `/foss-check` runs.
- [ ] **Bootstrap audit**: run `/foss-check` against `eidos-agi/foss-forge` itself. Write `AUDITS/foss-forge.md` with the foss-check output verbatim. Header: `audited_by: foss-forge@<version>` (self-referential and proud). Populate `x-eidos.audit` in marketplace.json.
- [ ] If `foss-forge` self-audits below grade B: fix `foss-forge`'s source repo, re-tag, re-publish, re-audit. Phase 5 cannot start until `foss-forge` clears its own bar.
- [ ] Retroactively re-audit `cept` using `/foss-check`. Update `AUDITS/cept.md` and `cept`'s `x-eidos.audit` block. Header changes from `audited_by: by-hand` to `audited_by: foss-forge@<version>`. Phase 1's hand-audit debt is now retired.
- [ ] Retroactively re-audit `eidos-install` and `forge-forge` using `/foss-check`. Update `AUDITS/eidos-install.md`, `AUDITS/forge-forge.md`, and both `x-eidos.audit` blocks. Phase 3's hand-audit debt is now retired.
- [ ] Verify `forge-forge` correctly surfaces the now-onboarded `foss-forge` via `/forge recommend-for python-package`. Recommendation must show `foss-forge`'s audit grade inline.

After Phase 4, the dogfooding loop is closed: `forge-forge` recommends `foss-forge`; `foss-forge` audits everything (including itself); audits publish to both `marketplace.json` (machine-readable) and `AUDITS/` (human-readable).

---

## Phase 5 — Audit remaining plugins via `foss-forge`

The 9 plugins already in marketplace.json predate the standard. Now that `foss-forge` is operational, audit each one *through it*. No hand-grading. If `foss-forge` can't grade something, that is itself a `foss-forge` bug — fix the tool, not the workaround.

For each plugin below:

1. Run `/foss-check` against the plugin's source repo.
2. Address gaps in the source repo (LICENSE, README, CHANGELOG, etc.) until grade ≥B.
3. Write `AUDITS/<name>.md` with the foss-check output verbatim, plus a one-paragraph summary. Header: `audited_by: foss-forge@<version>`.
4. Populate `x-eidos.audit` in marketplace.json.
5. If it can't reach grade ≥B and the gap is in the plugin (not the tool), mark it removed: delete from marketplace.json, write `AUDITS/<name>.md` with the removal explanation.

Order — smallest blast radius first:

- [ ] probe-forge
- [ ] research-md
- [ ] resume-resume
- [ ] ike
- [ ] visionlog
- [ ] eidos-mail
- [ ] clawdflare
- [ ] railguey
- [ ] slack-cc (was in archived `eidos-agi/claude-plugins`; needs onboarding here. Source repo: `eidos-agi/slack-cc`. Note: install requires `--dangerously-load-development-channels` flag for private marketplace plugins.)

---

## Phase 6 — Onboard the rest of the operational forges

The marketplace's other maintenance operations — release, security audit, MCP linting, testing — also need to run via marketplace plugins, not by hand. Onboard each one and use it for its respective marketplace operation. Each onboarded forge gets its `x-eidos.recommend` block populated so `forge-forge` can surface it for the right project context.

- [ ] **security-forge** — onboard as a `github` source. Run `/secaudit` against `cept`, `forge-forge`, `foss-forge`, and any plugin already in `AUDITS/`. Extend `x-eidos.audit` schema with `security_grade` + `security_audit_date`. `x-eidos.recommend.pairs_with: ["foss-forge"]`.
- [ ] **ship-forge** — onboard. From now on, every change to marketplace.json that bumps a plugin version goes through `/ship` (commit message format, version bump check, release notes). `recommend.for_projects: ["pypi-package", "github-release"]`.
- [ ] **mcp-forge** — onboard. Use it to lint MCP-server plugins' tool descriptions and parameter schemas (the Agentic Quality layer of STANDARD.md). `recommend.for_projects: ["mcp-server"]`.
- [ ] **test-forge** — onboard. Replace `tools/test_plugins.py` with a `/test` invocation that calls test-forge against `marketplace.json` schema + per-entry assertions.
- [ ] **scribe** — onboard if it provides documentation-quality checks. Verify each plugin's README meets the "≥20 lines, install + usage example" bar from STANDARD.md.
- [ ] **brand-forge** — onboard. Use it to enforce visual + tone consistency on every README badge, AUDITS/ summary, and external-facing post.

After this phase, the marketplace's day-to-day operations are entirely run through plugins it lists, and `forge-forge`'s `/forge recommend-for <project>` returns useful recommendations for any of the major project archetypes (python-package, github-release, mcp-server, etc.). That is the proof of dogfooding.

---

## Phase 7 — Quality bar machinery (CI runs the same plugins)

Manual invocation doesn't scale. Move the dogfooded operations into CI so they re-run on every PR and on a quarterly schedule.

- [ ] `.github/workflows/audit.yml` — validates marketplace.json against the schema, lints required `x-eidos.kind` and `x-eidos.audit` fields per entry, runs `python tools/test_plugins.py` (or its test-forge replacement).
- [ ] `.github/workflows/foss-check.yml` — quarterly cron + manual dispatch. Runs `foss-forge` against each linked plugin's source repo (via `gh api`) and opens a PR updating `AUDITS/<name>.md` and `x-eidos.audit` if scores changed.
- [ ] `.github/workflows/security-audit.yml` — quarterly cron. Runs `security-forge` against each plugin's source repo, posts findings as issues if any are HIGH/CRITICAL.
- [ ] Wire CI to **fail if `x-eidos.audit.audit_date` is older than 95 days** for any plugin. This forces the quarterly cadence to be enforced, not aspirational.
- [ ] Add a "Verified eidos-grade" badge to each plugin's README in its source repo, linking back to its audit doc here.

---

## Phase 8 — External discoverability

Only after Phase 5 has 3+ plugins past audit and Phase 7 CI is green.

- [ ] Submit to [claudemarketplaces.com](https://claudemarketplaces.com).
- [ ] Make each plugin compatible with `npx skills add eidos-agi/<name>` where applicable (cross-tool reach beyond Claude Code).
- [ ] Write the launch post: blog on eidosagi.com, tweet, Hacker News. Tone: portfolio of how we ship, not "we built a marketplace." Lead with `claude plugins install eidos-install` as the one-line front door for new users, and mention `cept` as the highlight tool that ships with every starter set.

---

## Phase 9 — Ongoing

This is forever. The marketplace is alive.

- [ ] Quarterly re-audit cadence. Next: **2026-07-28**. Update every `AUDITS/<name>.md` and bump `x-eidos.audit.audit_date` in marketplace.json. CI from Phase 7 enforces this.
- [ ] Semver discipline. Every meaningful change to a plugin bumps `version` in its source repo's `pyproject.toml` *and* in marketplace.json (when we choose to pin).
- [ ] When a plugin falls below the bar, pull it. Public removal is a stronger signal than silent exclusion. Write the removal explanation in its audit file.
- [ ] When a plugin earns A grade and stays there for ≥6 months, mark it "core" in marketplace.json. Core plugins get prominence on the README.

---

## Standing principles (apply to every phase)

- **Quality > quantity.** Five A-grade plugins beats fifty mixed-grade ones for the trust thesis.
- **Public commits, public audits, public removals.** No silent state changes.
- **Slow accretion.** DHH wasn't credible at year 1; he was credible at year 5. Plan for the marathon.
- **The negative rule.** Don't commit anything to this repo a stranger wouldn't be glad to find.
