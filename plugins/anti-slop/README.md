# anti-slop

**Eidos AGI** plugin: continuous anti-AI-slop for prose, plus a world-class case-study gate.

UIZZE is to UI what this is to writing: not only “don’t look generic,” but a **quality gate** that can evolve with community detection patterns and (later) elite human exemplars.

| Skill | Job |
|-------|-----|
| **anti-slop** | Write under constraints that kill detectable LLM patterns |
| **anti-slop-audit** | Post-draft punch list (`file:line`) — same job as ai-isms-filter, owned here |
| **world-class-case-study** | Northstar/case-study prose: intent lock, pack ≠ essay, one mid, exemplar-ready |

Linear: [EID-1310](https://linear.app/eidos-agi/issue/EID-1310)

## Why this exists

Static ban lists rot. Case-study shipping optimized for archive completeness and shipped AI-sounding packets. This repo:

1. **Pulls** community anti-slop upstreams (submodules + `npx skills`)
2. **Merges** lexicons with provenance (curated continuous update — PRs, not silent overwrite)
3. **Ships** to eidos-marketplace and Grok plugins
4. **Later** scores drafts against elite exemplars (Stripe/Linear-style density), not only banned words

## Install

### Agent Skills CLI

```bash
npx skills add eidos-agi/anti-slop
# when published; until then, clone and:
npx skills add ./anti-slop   # from parent of this repo if supported
```

### Claude Code

```bash
# After marketplace listing:
claude plugins install anti-slop@eidos-marketplace

# Local dev:
# add this directory as a local plugin / copy skills/* to ~/.claude/skills/
cp -R skills/anti-slop skills/anti-slop-audit skills/world-class-case-study ~/.claude/skills/
```

### Grok

```bash
# Dev: symlink into Grok plugins
ln -sfn "$(pwd)" ~/.grok/plugins/anti-slop
```

### Continuous update (local)

```bash
./scripts/sync-upstream.sh      # submodule pull + merge lexicon
./scripts/doctor.sh             # stale check
# or:
npx skills update
```

Weekly GitHub Action opens a PR when upstreams change (see `.github/workflows/sync-upstream.yml`).

## Upstream sources (vendor/)

| Submodule | Focus |
|-----------|--------|
| [jalaalrd/anti-ai-slop-writing](https://github.com/jalaalrd/anti-ai-slop-writing) | Banned vocab, structural rules |
| [adewale/anti-slop-writing](https://github.com/adewale/anti-slop-writing) | Technical / DevRel prose |
| [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) | Structural pattern editor / detector |

First-time submodule init:

```bash
git submodule update --init --recursive
./scripts/sync-upstream.sh
```

## Case studies (Northstar)

**Archive** (deedee pack) can stay complete and boring.  
**Shelf prose** must load `world-class-case-study` + `anti-slop` + finish with `anti-slop-audit`.

Ship path:

```text
intent lock → pack/archive → prose (anti-slop) → anti-slop-audit → case-study gate → check-casestudies
```

## Phases

| Phase | Status |
|-------|--------|
| M0 Scaffold + dual skills + sync scripts | **in progress** |
| M1 CLI audit + CI | next |
| M2 world-class-case-study + Northstar HOW-TO | |
| M3 Exemplar catalog + weekly distill PR | |
| M4 Marketplace + Grok publish | |
| M5 Dogfood SO “cost of knowledge” rewrite | |

## License

MIT — Eidos AGI. Upstream submodules keep their own licenses; see `references/UPSTREAM.md`.
