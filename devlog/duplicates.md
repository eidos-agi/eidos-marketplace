# Duplicates

## 2026-10-04 grok-canopy manifests

- **What changed:** `.claude-plugin/plugin.json` and `.grok-plugin/plugin.json` carry the same name, version, license, author, homepage, and keywords. The MIT LICENSE text matches the grok-goals license.
- **Why:** Claude and Grok hosts read different manifest paths. The publish request asks for both, the same way grok-goals shipped them. Removing either copy would drop a host. The license text is the MIT grant this plugin is required to ship.
- **Supporting Research:** `plugins/grok-goals` ships the same pair of manifests and the same MIT LICENSE.

## 2026-10-04 grok-goals manifests

- **What changed:** `.claude-plugin/plugin.json` and `.grok-plugin/plugin.json` carry the same name, version, license, author, homepage, and keywords.
- **Why:** The publish request asks for both manifests. Grok and Claude hosts read different paths. Removing either copy would drop a host. This duplication stays.
- **Supporting Research:** `plugins/shipr` ships the same pair of manifests.
