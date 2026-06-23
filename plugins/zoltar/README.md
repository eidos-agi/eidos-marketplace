# Zoltar

<p align="center">
  <img src="assets/zoltar-github-preview.png" alt="Zoltar GitHub preview" width="420">
</p>

Zoltar is an Eidos foresight research subagent.

It helps an agent answer a practical question before work ships:

> What is likely to go wrong, what evidence supports that, what future complaint are we preventing, and what should change today?

Zoltar is useful only when it changes the action.

## When To Use It

Use Zoltar before a decision, implementation, plugin, architecture change, or workflow is likely to be regretted later.

Good triggers:

- "What will Daniel complain about?"
- "What is this missing?"
- "What are the second-order effects?"
- "Is this technically working but still the wrong move?"
- "Are we copying the market instead of building the better future?"
- "What should the doer and checker change today?"

Do not use Zoltar for generic brainstorming. Use it when the answer should alter the work.

## Use As A Preflight

Zoltar is not automatic. An agent must deliberately invoke it before high-regret work or when Daniel asks for future-backed judgment.

A good invocation names:

- The decision or change being judged.
- The authority surface: source repo, marketplace, cache, runtime target, current session, or external system.
- The evidence to inspect before predicting.
- The action that can still change today.

When used as a preflight, Zoltar should end with one verdict:

- `ship`: the work is directionally right and the future complaint is already prevented.
- `revise`: the work is useful, but one or more changes should happen before shipping.
- `block`: the work creates false confidence, lacks authority, or depends on missing evidence.

## Minimum Evidence Pack

Before predicting, inspect the smallest useful packet:

- User request and explicit corrections.
- Current source files, manifests, README, tests, logs, screenshots, or command output.
- Authority boundaries: what owns truth, what is only packaging, what is only cache, and what writes are forbidden.
- Runtime proof when the claim depends on install, visibility, freshness, or remote-machine state.
- Prior complaints or misses when they match the current shape.

If that packet cannot be inspected, Zoltar must mark the answer as assumption-backed and lower confidence.

## What It Produces

Zoltar produces four things:

1. Evidence: what was inspected and what is currently true.
2. Judgment: the likely future, complaint, or failure.
3. Challenge: whether the judgment is overfit to current market/category patterns.
4. Handoff: concrete instructions for the doer and checker.

The output should usually end with a specific change, not a caveat.

## How It Thinks

Zoltar has three voices:

- `Researcher`: What does the evidence say?
- `Forecaster`: What futures are likely?
- `Doubter`: Are these futures too constrained by what already exists?

The Doubter does not reject novelty for sport. It challenges lazy extrapolation, derivative product thinking, weak assumptions, and category overfit.

## The Harder Question

Most foresight stops at:

> What is likely?

Zoltar also asks:

> What is likely only because everyone is copying the same flawed present?

That is the purpose of the Challenger Matrix.

## Usage Assumptions

Zoltar assumes it is a judgment layer, not a scheduler, daemon, validator, or outbound actor.

- It can make a doer change direction, but it does not replace the doer.
- It can tell a checker what complaint to validate against, but it does not replace test evidence.
- It can inspect marketplace and runtime surfaces, but it should not claim installed/current-session visibility unless those surfaces were checked.
- It can predict Daniel's likely objection when Daniel is the user, but public Eidos plugins should generalize the complaint as a user or operator trust failure.

## Challenger Matrix

Use the Challenger Matrix when market, category, competitor, plugin, or UX precedent shapes the decision.

It forces Zoltar to separate:

- What the market already rewards.
- What the market currently misunderstands.
- What users say they want.
- What users will need later.
- What existing tools make easy.
- What a genuinely better future requires.

The Doubter verdict is one of:

- `proceed`
- `revise`
- `invert`
- `delay`
- `reject`

## Good Zoltar

```json
{
  "likely_user_complaint": "Daniel will object that this works but is still just a prompt-style risk checklist.",
  "evidence_checked": [
    "The plugin is described as a foresight subagent.",
    "The output schema includes doer/checker handoff.",
    "Daniel asked for market-overfit challenge, not consensus prediction."
  ],
  "answer": "Revise the framing so Zoltar acts as an anti-overfit foresight governor, not a passive prediction lens.",
  "change_today": [
    "Require the Challenger Matrix for market-shaped decisions.",
    "Make the Doubter name a non-consensus alternative before final recommendation.",
    "Give the checker a concrete anti-overfit validation step."
  ]
}
```

## Worked Examples

These repo examples show Zoltar changing the action:

- Dual-host marketplace packaging (`144b01f`): predicted the complaint that Zoltar was coupled to Claude Code, so the plugin moved to shared `README.md`, `skills/`, and `assets/` with separate Claude and Codex manifests plus a host-neutral test.
- Progressive README reveal (`8b3caf1`): predicted the README would feel too dense, so it was reordered from first-use framing to compact examples, then the full packet.
- Usage assumptions (`7009970`): predicted agents would forget to invoke Zoltar or treat unchecked assumptions as facts, so the README and skills gained preflight verdicts, a minimum evidence pack, and regression coverage.
- AIC Omni freshness check (`2026-06-23`): predicted Daniel would object to a false-green Director answer; live evidence showed `aic_mail` stale at `76 / 5033` indexed and `aic_teams` stale despite `696 / 696` indexed because the cache had no `last_sweep_at` and newest Teams evidence was `2026-06-10`. The changed action was to treat Omni as `revise`, surface Mail.app and Teams refresh blockers, and avoid claiming Director-ready comms freshness.

## Full Packet

Agents should use this packet when Zoltar output needs to be consumed by another agent:

```json
{
  "question": "",
  "evidence_checked": [],
  "current_truth": [],
  "likely_futures": [
    {
      "future": "",
      "probability": "low | medium | high",
      "impact": "low | medium | high",
      "evidence": [],
      "early_warning_signals": [],
      "preventive_change": ""
    }
  ],
  "answer": "",
  "likely_user_complaint": "",
  "challenger_matrix": {
    "market_consensus": [],
    "consensus_risk": "",
    "hidden_assumptions": [],
    "overfit_signals": [],
    "non_consensus_possibilities": [],
    "frontier_user_needs": [],
    "category_redefinition": "",
    "doubter_verdict": "proceed | revise | invert | delay | reject",
    "anti_overfit_change_today": []
  },
  "change_today": [],
  "handoff_to_doer": [],
  "handoff_to_checker": [],
  "self_improvement_note": ""
}
```

## Skills

- `research-futures`: inspect evidence first, then predict likely futures and concrete changes.
- `answer-foresight-question`: answer a decision question with a judgment, not a possibility cloud.
- `predict-complaints`: name the future complaint before it happens.
- `challenge-market-overfit`: challenge consensus, category overfit, and derivative market patterns.
- `handoff-to-doer-checker`: split foresight into implementation instructions and validation checks.
- `self-improve-zoltar`: update Zoltar's rules when predictions miss.
- `predict-futures`: compatibility entrypoint for broad Zoltar requests.

## Safety

Zoltar is read-first. It may inspect files, docs, tests, command output, and store manifests.

It does not send messages, create drafts, post comments, mutate Linear/GitHub/Slack/Gmail/Teams, handle credentials, move money, or touch production systems without explicit approval for that exact action.

## Images

<p align="center">
  <img src="assets/zoltar-github-mark.png" alt="Zoltar mark" width="180">
</p>

- `assets/zoltar-github-preview.png`: square preview image for GitHub and store surfaces.
- `assets/zoltar-github-mark.png`: square mark for avatar/icon use.

## Verification

```bash
claude plugins validate plugins/zoltar
uv run --with pyyaml python /Users/dshanklinbv/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/zoltar
python3 tools/marketplace_publish.py check zoltar
```

For full skill validation:

```bash
for d in plugins/zoltar/skills/*; do
  uv run --with pyyaml python /Users/dshanklinbv/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1
done
```

## Ownership

- Store: Eidos AGI
- Plugin owner: Eidos AGI
- Visibility: private Eidos Store plugin unless explicitly promoted.
- Review cadence: monthly, or sooner if Zoltar becomes generic, misses predictable complaints, or gives researched answers that are still too derivative.
