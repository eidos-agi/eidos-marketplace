# Zoltar

<p align="center">
  <img src="assets/zoltar-github-preview.png" alt="Zoltar GitHub preview" width="420">
</p>

Zoltar is an Eidos foresight research subagent.

It investigates the current situation, predicts what is likely to happen next, challenges whether that prediction is too shaped by the existing market, and turns the answer into concrete changes for doer/checker agents.

Zoltar is useful only when it changes the action.

## What It Answers

Zoltar answers one practical question:

> What is likely to go wrong, what evidence supports that, what future complaint or failure are we preventing, and what should change today?

It also asks the harder second question:

> What is likely only because everyone is copying the same flawed present?

## How It Thinks

Zoltar uses three voices:

- `Researcher`: What does the evidence say?
- `Forecaster`: What futures are likely?
- `Doubter`: Are these futures too constrained by what already exists?

The Doubter does not replace research. It attacks lazy extrapolation, derivative product thinking, weak assumptions, and category overfit.

## Output Contract

Zoltar emits a compact packet that another agent can use:

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

The `challenger_matrix` is required when market, category, competitor, plugin, or UX precedent shapes the decision.

## Skills

- `research-futures`: inspect evidence first, then predict likely futures and concrete changes.
- `answer-foresight-question`: answer a decision question with a judgment, not a possibility cloud.
- `predict-complaints`: name the future complaint before it happens.
- `challenge-market-overfit`: challenge consensus, category overfit, and derivative market patterns.
- `handoff-to-doer-checker`: split foresight into implementation instructions and validation checks.
- `self-improve-zoltar`: update Zoltar's rules when predictions miss.
- `predict-futures`: compatibility entrypoint for broad Zoltar requests.

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
uv run --with pyyaml python /Users/dshanklinbv/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/zoltar
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
```

For full skill validation, run `quick_validate.py` against each directory under `plugins/zoltar/skills/`.

## Ownership

- Store: Eidos AGI
- Plugin owner: Eidos AGI
- Visibility: private Eidos Store plugin unless explicitly promoted.
- Review cadence: monthly, or sooner if Zoltar becomes generic, misses predictable complaints, or gives researched answers that are still too derivative.
