# Zoltar Foresight Cases

These cases show Zoltar being used as a foresight research subagent, not as generic risk commentary.

Each case answers:

- What evidence was checked?
- What future complaint was prevented?
- What changed today?
- What should the doer and checker do next time?

## Case 1: Dual-Host Marketplace Packaging

```json
{
  "question": "Is Zoltar set up well as an Eidos marketplace plugin for both Claude Code and Codex?",
  "evidence_checked": [
    "User objected that the initial setup coupled Zoltar to Claude Code.",
    "Marketplace source contains separate `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` manifests.",
    "Shared behavior now lives in `README.md`, `skills/`, and `assets/`.",
    "`tests/test_marketplace_publish.py` asserts Zoltar is listed for both hosts and keeps Codex-only UI metadata out of the Claude manifest."
  ],
  "current_truth": [
    "The product is an Eidos plugin with host-specific adapters.",
    "Claude and Codex manifests share name, version, description, repository, license, and skills.",
    "The source, marketplace listing, and installed cache must still be checked separately."
  ],
  "likely_futures": [
    {
      "future": "Future agents will confuse host packaging with product ownership unless the repo keeps the shared payload separate from host manifests.",
      "probability": "high",
      "impact": "high",
      "evidence": [
        "The user explicitly complained about coupling Zoltar to Claude Code.",
        "The marketplace now has a dual-host maintenance skill and regression tests."
      ],
      "early_warning_signals": [
        "Behavior appears only in `.codex-plugin/plugin.json` interface metadata.",
        "Claude manifest grows Codex-only fields.",
        "A README edit says 'Claude plugin' instead of 'Eidos plugin'."
      ],
      "preventive_change": "Keep shared behavior in host-neutral files and validate both manifests before shipping."
    }
  ],
  "answer": "ship with continued dual-host checks",
  "likely_user_complaint": "Daniel will object that the plugin works in one host but is no longer a real marketplace primitive.",
  "change_today": [
    "Keep `maintain-dual-host-marketplace` as the maintenance gate.",
    "Keep the Zoltar host-neutral test in `tests/test_marketplace_publish.py`.",
    "Check source, root marketplace entries, local cache, and current-session visibility separately."
  ],
  "handoff_to_doer": [
    "Put new behavior in `README.md`, `skills/`, `assets/`, scripts, or docs unless it is truly host UI metadata.",
    "Do not make Claude or Codex the product owner."
  ],
  "handoff_to_checker": [
    "Run Claude manifest validation, Codex plugin validation, marketplace check, skill validation, and marketplace tests.",
    "Inspect both host manifests for accidental metadata drift."
  ],
  "self_improvement_note": "Zoltar should treat host-specific success as insufficient when marketplace ownership is the real product question."
}
```

## Case 2: Progressive README Reveal

```json
{
  "question": "Will the Zoltar README help a future agent use the plugin correctly?",
  "evidence_checked": [
    "User said the README could be clearer and more progressive.",
    "README now starts with visual identity, role, core question, triggers, preflight contract, then deeper packet details.",
    "The full JSON packet is no longer the first cognitive load."
  ],
  "current_truth": [
    "The README explains when to use Zoltar before the full schema.",
    "The worked examples section appears before the full packet.",
    "The README still stays concise enough for marketplace browsing."
  ],
  "likely_futures": [
    {
      "future": "If the README leads with schema or philosophy, agents will use Zoltar as a prompt pack instead of a decision tool.",
      "probability": "medium",
      "impact": "medium",
      "evidence": [
        "The user explicitly asked for clearer progressive reveal.",
        "The plugin has multiple skills and a full packet, which can overwhelm first use."
      ],
      "early_warning_signals": [
        "README grows long sections before 'When To Use It'.",
        "Examples disappear or become abstract.",
        "The full packet becomes the main selling point."
      ],
      "preventive_change": "Keep the README ordered from use case, to preflight, to examples, to full packet."
    }
  ],
  "answer": "ship, but preserve the progressive order",
  "likely_user_complaint": "Daniel will say the README is technically complete but still makes the agent work too hard to understand when to use Zoltar.",
  "change_today": [
    "Keep examples brief in the README.",
    "Move detailed case analysis to `docs/foresight-cases.md`.",
    "Protect the examples section with a test."
  ],
  "handoff_to_doer": [
    "When adding new Zoltar details, decide whether they belong in the short README or the deeper casebook.",
    "Do not bury the core question below long schema documentation."
  ],
  "handoff_to_checker": [
    "Read the README from top to bottom and verify a first-time agent can answer when, why, and how to use Zoltar in under a minute."
  ],
  "self_improvement_note": "Zoltar should predict documentation fatigue as a real failure mode, not a cosmetic issue."
}
```

## Case 3: Usage Assumptions And Preflight Contract

```json
{
  "question": "What is Zoltar likely missing even if its skills validate?",
  "evidence_checked": [
    "Zoltar had strong skill text but depended on agents remembering to invoke it.",
    "`challenge-market-overfit` already named manual invocation as a hidden assumption.",
    "The README and core skills now include preflight mode, a minimum evidence pack, and assumption-backed confidence rules.",
    "`tests/test_marketplace_publish.py` asserts these sections remain present."
  ],
  "current_truth": [
    "Zoltar is not automatic.",
    "It now requires `ship`, `revise`, or `block` when used before shipping.",
    "It now tells agents to avoid converting unchecked assumptions into confident futures."
  ],
  "likely_futures": [
    {
      "future": "Without a preflight contract, Zoltar will be praised as useful and then forgotten during actual implementation.",
      "probability": "high",
      "impact": "high",
      "evidence": [
        "The user asked to predict future complaints because that is how today's app changes are found.",
        "The plugin was implemented as skills, which are opt-in unless explicitly invoked."
      ],
      "early_warning_signals": [
        "Zoltar appears only in README examples.",
        "A future change validates tests but has no Zoltar verdict.",
        "Agents say 'Zoltar would probably...' without inspecting evidence."
      ],
      "preventive_change": "Require a named decision, authority surface, evidence pack, and preflight verdict for high-regret changes."
    }
  ],
  "answer": "revise completed",
  "likely_user_complaint": "Daniel will say this is a good idea that does not actually change agent behavior.",
  "change_today": [
    "Document preflight mode.",
    "Document the minimum evidence pack.",
    "Add tests that guard the usage-assumption contract."
  ],
  "handoff_to_doer": [
    "Use Zoltar before high-regret changes and state the verdict explicitly.",
    "Mark missing evidence as assumption-backed."
  ],
  "handoff_to_checker": [
    "Reject Zoltar output that lacks inspected evidence, a decision, and a concrete change.",
    "Check whether the implementation changed because of the forecast."
  ],
  "self_improvement_note": "Zoltar should treat non-durable behavior as a first-class miss type."
}
```

## Case 4: AIC Omni Freshness And Director False-Green Risk

```json
{
  "question": "Is AIC Omni ready to support AICDirector comms decisions from this chat?",
  "evidence_checked": [
    "`aic-mail doctor --pretty` reports `ok=false`, `total_messages=5033`, newest message `Jun 18, 2026 08:00 AM`, `age_days=5.63`, and next action to open Mail.app.",
    "`aic-teams doctor --pretty` reports AIC Teams source id 6 with `message_count=696`, `last_sweep_at=null`, and newest message `2026-06-10T21:43:07.147000Z`.",
    "`reeves_omni_3.cli doctor --json` reports `aic_mail` indexed `76 / 5033`, `indexed_delta=4957`, and stale.",
    "`reeves_omni_3.cli doctor --json` reports `aic_teams` indexed `696 / 696`, but stale due to missing `last_sweep_at` and old newest message.",
    "`aicdirector omni` surfaces both stale sources and names the Mail.app and Teams freshness blockers."
  ],
  "current_truth": [
    "The architectural boundary is right: AIC Omni owns source health, indexing, freshness, provenance, and search; AICDirector owns decisions.",
    "The current Director-facing output does not hide stale comms.",
    "The source state is not Director-ready for current comms freshness."
  ],
  "likely_futures": [
    {
      "future": "Daniel will trust the architecture but complain if AICDirector acts as if stale comms are live.",
      "probability": "high",
      "impact": "high",
      "evidence": [
        "Both `aicdirector omni` and Omni doctor surface stale source rows.",
        "Mail index trails upstream by 4957 records.",
        "Teams has full indexed count but no fresh sweep marker."
      ],
      "early_warning_signals": [
        "`control-panel` gives a first block without the Omni freshness section.",
        "A Teams answer does not mention newest message `2026-06-10`.",
        "A mail answer does not mention Mail.app hydration or indexed delta."
      ],
      "preventive_change": "Treat comms freshness as `revise` until Mail.app hydration, refresh ingest, and Teams extractor/sweep proof are current."
    },
    {
      "future": "A team may mistake `696 / 696` Teams indexed coverage for freshness.",
      "probability": "high",
      "impact": "medium",
      "evidence": [
        "Teams indexed delta is zero.",
        "Teams still has `last_sweep_at=null` and newest message outside the 2-day window."
      ],
      "early_warning_signals": [
        "Docs say 'fully indexed' without also saying 'stale'.",
        "Readiness checks use indexed delta alone."
      ],
      "preventive_change": "Keep `last_sweep_at` and newest-message age in the readiness bar, not only indexed counts."
    }
  ],
  "answer": "revise: the integration path is correct, but current comms freshness is not Director-ready",
  "likely_user_complaint": "Daniel will say this looks wired up but still cannot be trusted for current AIC comms because Mail is stale and Teams is a stale cache.",
  "challenger_matrix": {
    "market_consensus": [
      "Most search/index tools treat indexed document count as readiness.",
      "Most assistants hide source freshness behind synthesized answers."
    ],
    "consensus_risk": "A Director agent that behaves like ordinary search will create false confidence by answering from stale local evidence.",
    "hidden_assumptions": [
      "That indexed count means fresh enough.",
      "That source availability means Director readiness.",
      "That provider truth can be implied before auth exists."
    ],
    "overfit_signals": [
      "Teams looks complete by count but is stale by sweep evidence.",
      "Mail has a large upstream/indexed delta despite available adapter status."
    ],
    "non_consensus_possibilities": [
      "Make freshness a first-class blocker in every Director answer.",
      "Treat `indexed_delta=0` as insufficient without a current upstream sweep marker.",
      "Let AICDirector refuse or caveat comms decisions until Omni source rows are fresh."
    ],
    "frontier_user_needs": [
      "Evidence systems that say 'do not trust me yet' before synthesis.",
      "Director tools that separate architecture readiness from live operational readiness.",
      "Source health packets other agents can consume without reverse-engineering CLI output."
    ],
    "category_redefinition": "AIC Omni is not just search; it is a freshness-governed evidence substrate for Director decisions.",
    "doubter_verdict": "revise",
    "anti_overfit_change_today": [
      "Keep source freshness visible in `aicdirector omni` and `control-panel`.",
      "Do not claim Director-ready comms until Mail.app hydration and Teams sweep proof are current.",
      "Use indexed count plus upstream freshness markers as the readiness test."
    ]
  },
  "change_today": [
    "Run Mail.app hydration before relying on mail-derived decisions.",
    "Run explicit refresh ingest after Mail.app is hydrated.",
    "Run or repair the Teams extractor so source id 6 has a current `last_sweep_at` and newest message within the freshness window.",
    "Keep provider truth rows blocked until Microsoft auth/provider work is explicit."
  ],
  "handoff_to_doer": [
    "Do not edit AIC Nexus for this slice.",
    "Do not touch provider truth rows except to keep their blockers explicit.",
    "Make any future AICDirector answer carry `aic_mail` and `aic_teams` freshness when comms evidence is used."
  ],
  "handoff_to_checker": [
    "Check `aic-mail doctor --pretty` for `ok=true` and non-stale newest mail.",
    "Check `aic-teams doctor --pretty` for non-null current `last_sweep_at` and fresh newest message.",
    "Check `reeves_omni_3.cli doctor --json` for `source_freshness` rows with `stale=false` before calling comms Director-ready.",
    "Check `aicdirector omni` and `control-panel` still show blockers when freshness is stale."
  ],
  "self_improvement_note": "Zoltar should distinguish architecture-correct from live-ready whenever evidence freshness, indexed coverage, and provider truth are separate surfaces."
}
```
