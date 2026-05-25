# Eidos AGI Catalog Bootstrap

This repo contains the Codex bootstrap/catalog plugin for Eidos AGI plugins.

The public marketplace identity is **Eidos AGI**. This plugin is an entry inside
that marketplace, not a second store. Install or load it when Codex needs help
discovering the right Eidos AGI plugin for a task.

## Paste Into Codex

```text
I want to install the Eidos AGI plugin catalog for Codex so you can use it to find and add more Eidos plugins.

Please use the Eidos AGI marketplace as the single source of truth for Eidos plugins:
https://eidosagi.com/plugins

Store plugin source:
https://github.com/eidos-agi/eidos-plugin-store

If Codex cannot install plugins directly yet, say that plainly, use the source repo instructions, and keep using the Eidos AGI catalog as the source of truth.
```

## Catalog

- Human catalog: https://eidosagi.com/plugins
- Machine catalog: https://eidosagi.com/.well-known/eidos/plugin-store.json

## What It Does

- Reads the Eidos AGI plugin catalog.
- Recommends the right Eidos plugin for a task.
- Gives direct install steps when available.
- Falls back to source repo instructions when direct Codex install is not live.

## Status

This is the Codex bootstrap/catalog plugin for the public Eidos AGI marketplace.
