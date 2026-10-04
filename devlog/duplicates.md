# Duplicates

## 2026-10-04 grok-goals manifests

- **What changed:** `.claude-plugin/plugin.json` and `.grok-plugin/plugin.json` carry the same name, version, license, author, homepage, and keywords.
- **Why:** The publish request asks for both manifests. Grok and Claude hosts read different paths. Removing either copy would drop a host. This duplication stays.
- **Supporting Research:** `plugins/shipr` ships the same pair of manifests.
