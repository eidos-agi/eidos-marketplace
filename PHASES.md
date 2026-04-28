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
- [ ] Decide fate of `eidos-agi/claude-plugins` (the duplicate marketplace). Recommend: archive with a README pointing here. Track decision in commit message.

---

## Phase 1 — cept onboarding (target: ~30 min)

cept (`eidos-agi/cept`, on PyPI as `cept`) is the flagship plugin. It demonstrates the bar.

- [ ] Create `plugins/cept/.claude-plugin/plugin.json` with: name, description, version (mirror `cept`'s pyproject.toml), homepage, repository, license, keywords
- [ ] Create `plugins/cept/.mcp.json` using the uvx-shim pattern: `{"cept": {"command": "uvx", "args": ["--from", "cept", "cept"]}}`
- [ ] Add cept entry to `.claude-plugin/marketplace.json` plugins array. Include: name, description, source (`"cept"`), category (`"productivity"` or `"agent-tools"` — pick one and use consistently), tags, homepage, license, version
- [ ] Run `python tools/test_plugins.py` to verify validation passes
- [ ] From a clean Claude Code session: `/plugin marketplace add eidos-agi/eidos-marketplace`, then `/plugin install cept@eidos-marketplace`. Confirm the MCP starts and the `cept` tool responds.
- [ ] Audit cept against [STANDARD.md](STANDARD.md). Write `AUDITS/cept.md` with grade, date, scorecard. Add the `x-eidos-quality` block to cept's marketplace.json entry.
- [ ] Commit and push. Phase 1 complete when round-trip works.

---

## Phase 2 — Live with it (target: 2 weeks, ending ~2026-05-12)

This is a deliberate pause. The trust thesis only operates if we resist breadth.

- [ ] Do NOT onboard new plugins until 2026-05-12.
- [ ] Watch maintenance friction. Anything that hurts (a bad PyPI release breaking the uvx shim, a stale audit, an agent invoking cept incorrectly because the description was unclear) gets logged in `LEARNINGS.md`.
- [ ] If the marketplace.json or any plugin shape needs to evolve based on real usage, evolve it. Don't bake in patterns that haven't been tested.
- [ ] At end of Phase 2, decide: is the cadence sustainable? If not, simplify the standard before scaling. If yes, proceed to Phase 3.

---

## Phase 3 — Onboard remaining MCP-server plugins already in marketplace.json

The existing 9 plugins predate the standard. Bring each up to bar one at a time, audit, document. Order matters — start with the smallest blast radius.

For each plugin below:

1. Verify the source repo passes [STANDARD.md](STANDARD.md). Add missing files (LICENSE, CHANGELOG.md, CONTRIBUTING.md, etc.) where needed.
2. Audit. Write `AUDITS/<name>.md`.
3. Add `x-eidos-quality` to the marketplace.json entry.
4. If it can't reach grade ≥B, mark it removed: delete from marketplace.json, write `AUDITS/<name>.md` with the removal explanation.

- [ ] resume-resume
- [ ] ike
- [ ] visionlog
- [ ] research-md
- [ ] railguey
- [ ] clawdflare
- [ ] eidos-mail
- [ ] forge-forge
- [ ] probe-forge

---

## Phase 4 — Onboard skill-bearing plugins (forges)

Skill-only forges (foss-forge, ship-forge, security-forge, mcp-forge, etc.) don't fit the uvx-shim pattern because they ship markdown, not Python. They need a different `source` type — github-source — so the marketplace pulls the repo's `skills/<name>/SKILL.md` directly.

- [ ] Decide source convention for skill-bearing plugins: `{"source": {"source": "github", "repo": "eidos-agi/<name>"}}`. Document in STANDARD.md.
- [ ] For each skill-bearing forge: ensure source repo has `.claude-plugin/plugin.json` (top-level), restructure skills to `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`).
- [ ] Add to marketplace.json. Audit. Document.

Forges to onboard (in priority order):

- [ ] foss-forge (smallest, most-used; the one we just used to ship cept)
- [ ] security-forge (paired with foss-forge for audits)
- [ ] mcp-forge (relevant since most plugins here are MCP servers)
- [ ] ship-forge (release pipeline standards)
- [ ] forge-forge (the meta-forge — last because it depends on the others)
- [ ] (others as needed: brand-forge, cli-forge, ml-forge, marketing-forge, nightingale-forge, refactor-forge, demo-forge, test-forge, etc.)

---

## Phase 5 — Quality bar machinery

Manual audit doesn't scale. Automate.

- [ ] Add CI workflow `.github/workflows/audit.yml` that validates marketplace.json against the schema and lints each entry's required fields.
- [ ] Add CI workflow that runs `foss-forge/foss-check` against each linked plugin repo (via gh api) and updates `AUDITS/<name>.md` if scores change.
- [ ] Write `CONTRIBUTING.md` describing the submission process for third-party plugins.
- [ ] Add a "Verified eidos-grade" badge to each plugin's README (linking back to its audit doc).

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
