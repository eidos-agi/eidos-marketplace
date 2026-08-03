# Upstream sources

## Tracked (vendor submodules)

| Path | Repo | Use |
|------|------|-----|
| `vendor/jalaalrd-anti-ai-slop-writing` | https://github.com/jalaalrd/anti-ai-slop-writing | Banned vocab + structural rules |
| `vendor/adewale-anti-slop-writing` | https://github.com/adewale/anti-slop-writing | Technical / DevRel prose |
| `vendor/petergyang-no-ai-slop` | https://github.com/petergyang/no-ai-slop | Structural editor / detector |

## Optional later

| Source | Notes |
|--------|--------|
| NousResearch/autonovel `ANTI-SLOP.md` | Fiction/long-form; extract patterns carefully |
| In-house ai-isms-filter | Ported into `anti-slop-audit` skill |

## Policy

1. **Pull automatically** (CI weekly + `./scripts/sync-upstream.sh`)
2. **Merge with provenance** into `references/banned-words.md`
3. **Ship only after PR review** — community lists can over-block technical language
4. House overrides live in `references/house-overrides.md`

## Licenses

Each submodule retains its license. Composite references are MIT under Eidos; do not strip upstream copyright headers from vendor trees.
