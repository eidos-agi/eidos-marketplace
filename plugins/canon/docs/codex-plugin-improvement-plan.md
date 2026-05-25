# Canon Codex Plugin Improvement Plan

Last researched: 2026-05-24

## Findings

OpenAI's current Codex docs separate three layers:

- `AGENTS.md` gives Codex consistent project instructions before work starts.
- Skills package repeatable workflow instructions, scripts, references, and assets.
- Plugins distribute skills, apps, MCP servers, and hooks across users or teams.

For Canon, that means the plugin should not try to enforce everything through
instructions. The durable design is:

1. Skill metadata routes Codex to Canon at the right time.
2. Skill body tells Codex how to reason about standards.
3. Scripts run deterministic checks.
4. Hooks and CI turn important checks into gates.

## Near-Term Changes

1. Improve routing metadata.
   - Canon's skill description should name the trigger conditions: code changes,
     repo/plugin changes, proof gates, verification, CI, and definitions of done.
   - This matters because Codex initially sees skill names and descriptions before
     reading full `SKILL.md` bodies.

2. Keep Canon available both as a plugin and as a repo-local skill.
   - Plugin distribution uses `skills/canon/SKILL.md`.
   - Repo-local authoring should expose `.agents/skills/canon` so Codex can find
     Canon while working inside the Canon source repo.

3. Move mechanics into scripts.
   - `canon verify` should become a real orchestrator over plugin validation,
     Felix plugin doctor, tests, manifest checks, and repo policy checks.
   - Repeated shell recipes should not live only in prose.

4. Add trusted lifecycle hooks only after the checks are stable.
   - A `Stop` hook can ask Codex to continue when it tries to finish without a
     verification claim.
   - A `PostToolUse` hook can add context after commands that touch generated or
     policy-sensitive files.
   - Plugin-bundled hooks require explicit user trust, so keep them small and
     inspectable.

5. Add CI.
   - Use a normal GitHub Actions workflow for `canon verify`.
   - Consider Codex GitHub Action later for PR review prompts or standards audits.

6. Add evals for the skill itself.
   - Test whether Codex chooses Canon for realistic prompts and avoids it when
     the task is unrelated.
   - Score outputs for evidence claims, skipped-check disclosure, and correct
     routing to Felix, Eidos, or Converge when Canon is not the owner.

## Sources

- https://developers.openai.com/codex/plugins
- https://developers.openai.com/codex/plugins/build
- https://developers.openai.com/codex/skills
- https://developers.openai.com/codex/guides/agents-md
- https://developers.openai.com/codex/hooks
- https://developers.openai.com/codex/github-action
- https://developers.openai.com/blog/skills-agents-sdk
