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

- [ ] Add `$schema: "https://anthropic.com/claude-code/marketplace.schema.json"` to `.claude-plugin/marketplace.json` (top of file)
- [ ] Add top-level `description` to marketplace.json: *"The plugin marketplace for Claude Code, by Eidos AGI. Curated agent-first plugins, audited to a public standard."*
- [ ] Add top-level `version: "0.1.0"` to marketplace.json
- [ ] Add `metadata.pluginRoot: "./plugins"` to marketplace.json so per-plugin `source` can drop the `./plugins/` prefix
- [ ] Update existing plugin entries' `source` fields to use the shorter form (e.g., `"resume-resume"` instead of `"./plugins/resume-resume"`)
- [ ] Rewrite `README.md` to lead with the thesis (visibility is the moat), not feature list. Reference [STANDARD.md](STANDARD.md) and [PHASES.md](PHASES.md).
- [ ] Set GitHub topics on the marketplace repo: `claude-code`, `claude-plugin-marketplace`, `mcp`, `agent-tools`, `eidos-agi`. Use `gh repo edit eidos-agi/eidos-marketplace --add-topic ...`
- [x] Archive `eidos-agi/claude-plugins`. README replaced with redirect to this repo (commit 2b5fb49); repo archived 2026-04-28. The old marketplace was a single-plugin home for slack-cc, never expanded; 0 stars, 0 forks confirmed nobody depended on it.

---

## Phase 1 — cept onboarding (target: ~30 min)

cept (`eidos-agi/cept`, on PyPI as `cept`) is the flagship plugin. It demonstrates the bar.

- [ ] Create `plugins/cept/.claude-plugin/plugin.json` with: name, description, version (mirror `cept`'s pyproject.toml), homepage, repository, license, keywords
- [ ] Create `plugins/cept/.mcp.json` using the uvx-shim pattern: `{"cept": {"command": "uvx", "args": ["--from", "cept", "cept"]}}`
- [ ] Add cept entry to `.claude-plugin/marketplace.json` plugins array. Include: name, description, source (`"cept"`), category (`"productivity"` or `"agent-tools"` — pick one and use consistently), tags, homepage, license, version
- [ ] Run `python tools/test_plugins.py` to verify validation passes
- [ ] From a clean Claude Code session: `/plugin marketplace add eidos-agi/eidos-marketplace`, then `/plugin install cept@eidos-marketplace`. Confirm the MCP starts and the `cept` tool responds.
- [ ] Audit cept by hand against [STANDARD.md](STANDARD.md) for now. Write `AUDITS/cept.md` with grade, date, scorecard, and a header note: `audited_via: by-hand (foss-forge not yet onboarded)`. Add the `x-eidos-quality` block to cept's marketplace.json entry.
- [ ] Commit and push. Phase 1 complete when round-trip works.

The hand-audit is a temporary debt: the [Dogfooding section of STANDARD.md](STANDARD.md#dogfooding--the-marketplace-maintains-itself-with-its-own-plugins) requires `foss-forge` to be the audit tool. Phase 3 retires that debt by onboarding `foss-forge` and re-auditing cept through it.

---

## Phase 2 — Live with it (target: 2 weeks, ending ~2026-05-12)

This is a deliberate pause. The trust thesis only operates if we resist breadth.

- [ ] Do NOT onboard new plugins until 2026-05-12.
- [ ] Watch maintenance friction. Anything that hurts (a bad PyPI release breaking the uvx shim, a stale audit, an agent invoking cept incorrectly because the description was unclear) gets logged in `LEARNINGS.md`.
- [ ] If the marketplace.json or any plugin shape needs to evolve based on real usage, evolve it. Don't bake in patterns that haven't been tested.
- [ ] At end of Phase 2, decide: is the cadence sustainable? If not, simplify the standard before scaling. If yes, proceed to Phase 3.

---

## Phase 3 — Onboard `foss-forge` first (the audit tool itself)

The marketplace's first job after Phase 2 is to make its own audit instrument an installable plugin. This is the dogfooding forcing function from [STANDARD.md § Dogfooding](STANDARD.md#dogfooding--the-marketplace-maintains-itself-with-its-own-plugins): we cannot run a `foss-check` audit on any other plugin until `foss-forge` is a marketplace plugin in good standing.

Skill-bearing forges don't fit the uvx-shim pattern because they ship markdown, not Python. They need a different `source` shape — `github`-source — so the marketplace pulls the repo's `skills/` directory directly.

- [ ] Decide source convention for skill-bearing plugins: `{"source": {"source": "github", "repo": "eidos-agi/<name>"}}`. Document the convention as a one-liner in [STANDARD.md](STANDARD.md) under "How submissions work."
- [ ] In `eidos-agi/foss-forge`, ensure top-level `.claude-plugin/plugin.json` exists and skills are at `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`).
- [ ] Bring `foss-forge` up to STANDARD.md (LICENSE, README, CHANGELOG, CONTRIBUTING, COC, SECURITY). It must pass the bar by hand because it cannot audit itself yet.
- [ ] Add `foss-forge` entry to marketplace.json. Run `python tools/test_plugins.py`.
- [ ] Round-trip test: `claude plugins install foss-forge`. Confirm `/foss-check` runs.
- [ ] Run `/foss-check` against `eidos-agi/foss-forge` itself — the bootstrap audit. Write `AUDITS/foss-forge.md` with the result. Header of the audit: `audited_via: foss-forge@<version>` (self-referential and proud).
- [ ] If `foss-forge` cannot self-audit to grade ≥B, fix it before continuing. Phase 4 cannot start until `foss-forge` clears its own bar.

Once `foss-forge` clears, retroactively re-audit `cept` using `/foss-check` and update `AUDITS/cept.md` with `audited_via: foss-forge@<version>`. The Phase 1 manual audit is replaced by the dogfooded one.

---

## Phase 4 — Audit the remaining plugins via `foss-forge`

The 9 plugins already in marketplace.json predate the standard. Now that `foss-forge` is operational, audit each one *through it*. No hand-grading. If `foss-forge` can't grade something, that is itself a `foss-forge` bug — fix the tool, not the workaround.

For each plugin below:

1. Run `/foss-check` against the plugin's source repo.
2. Address gaps in the source repo (LICENSE, README, CHANGELOG, etc.) until grade ≥B.
3. Write `AUDITS/<name>.md` with the foss-check output verbatim, plus a one-paragraph summary. Header: `audited_via: foss-forge@<version>`.
4. Add `x-eidos-quality` to the marketplace.json entry.
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
- [ ] forge-forge (the meta-forge; audit last because it depends on the others)
- [ ] slack-cc (was in archived `eidos-agi/claude-plugins`; needs onboarding here. Source repo: `eidos-agi/slack-cc`. Note: install requires `--dangerously-load-development-channels` flag for private marketplace plugins.)

---

## Phase 5 — Onboard the rest of the operational forges

The marketplace's other maintenance operations — release, security audit, MCP linting, testing — also need to run via marketplace plugins, not by hand. Onboard each one and use it for its respective marketplace operation.

- [ ] **security-forge** — onboard as a `github` source. Run `/secaudit` against `cept` and any plugin already in `AUDITS/`. Add a `security_audit` field to `x-eidos-quality`.
- [ ] **ship-forge** — onboard. From now on, every change to marketplace.json that bumps a plugin version goes through `/ship` (commit message format, version bump check, release notes).
- [ ] **mcp-forge** — onboard. Use it to lint MCP-server plugins' tool descriptions and parameter schemas (the Agentic Quality layer of STANDARD.md).
- [ ] **test-forge** — onboard. Replace `tools/test_plugins.py` with a `/test` invocation that calls test-forge against `marketplace.json` schema + per-entry assertions.
- [ ] **scribe** — onboard if it provides documentation-quality checks. Use it to verify each plugin's README meets the "≥20 lines, install + usage example" bar.
- [ ] **brand-forge** — onboard. Use it to enforce visual + tone consistency on every README badge, AUDITS/ summary, and external-facing post.

After this phase, the marketplace's day-to-day operations are entirely run through plugins it lists. That is the proof of dogfooding.

---

## Phase 6 — Quality bar machinery (CI runs the same plugins)

Manual invocation doesn't scale. Move the dogfooded operations into CI so they re-run on every PR and on a quarterly schedule.

- [ ] `.github/workflows/audit.yml` — validates marketplace.json against the schema, lints required fields per entry, runs `python tools/test_plugins.py` (or its test-forge replacement).
- [ ] `.github/workflows/foss-check.yml` — quarterly cron + manual dispatch. Runs `foss-forge` against each linked plugin's source repo (via `gh api`) and opens a PR updating `AUDITS/<name>.md` if scores changed.
- [ ] `.github/workflows/security-audit.yml` — quarterly cron. Runs `security-forge` against each plugin's source repo, posts findings as issues if any are HIGH/CRITICAL.
- [ ] Wire CI to fail if `x-eidos-quality.audited_at` is older than 95 days (forces the quarterly cadence to be enforced, not aspirational).
- [ ] Add a "Verified eidos-grade" badge to each plugin's README in its source repo, linking back to its audit doc here.

---

## Phase 6 — External discoverability

Only after Phase 4 has 3+ plugins past audit.

- [ ] Submit to [claudemarketplaces.com](https://claudemarketplaces.com).
- [ ] Make each plugin compatible with `npx skills add eidos-agi/<name>` where applicable (cross-tool reach beyond Claude Code).
- [ ] Write the launch post: blog on eidosagi.com, tweet, Hacker News. Tone: portfolio of how we ship, not "we built a marketplace."

---

## Phase 7 — Ongoing

This is forever. The marketplace is alive.

- [ ] Quarterly re-audit cadence. Next: **2026-07-28**. Update every `AUDITS/<name>.md` and bump `x-eidos-quality.audited_at` in marketplace.json.
- [ ] Semver discipline. Every meaningful change to a plugin bumps `version` in its source repo's `pyproject.toml` *and* in marketplace.json (when we choose to pin).
- [ ] When a plugin falls below the bar, pull it. Public removal is a stronger signal than silent exclusion. Write the removal explanation in its audit file.
- [ ] When a plugin earns A grade and stays there for ≥6 months, mark it "core" in marketplace.json. Core plugins get prominence on the README.

---

## Standing principles (apply to every phase)

- **Quality > quantity.** Five A-grade plugins beats fifty mixed-grade ones for the trust thesis.
- **Public commits, public audits, public removals.** No silent state changes.
- **Slow accretion.** DHH wasn't credible at year 1; he was credible at year 5. Plan for the marathon.
- **The negative rule.** Don't commit anything to this repo a stranger wouldn't be glad to find.
