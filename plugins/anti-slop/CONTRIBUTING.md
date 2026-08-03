# Contributing

## Dev setup

```bash
git clone https://github.com/eidos-agi/anti-slop.git
cd anti-slop
./scripts/init-vendors.sh   # optional first time
./scripts/doctor.sh
```

## Updating upstream

```bash
./scripts/sync-upstream.sh
# review references/banned-words.md
# open PR
```

## Adding house rules

Edit `references/house-overrides.md`. Do not remove provenance tags from merged lexicon without reason.

## Skills

Edit under `skills/*/SKILL.md`. Keep frontmatter `name` + `description` accurate for agent discovery.
