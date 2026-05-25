# Changelog

## 0.2.2

- Added OpenClaw-mode fulfillment with snapshot/act flow payloads (`mode=openclaw`) for CDP-style browser execution.
- Added `--browser-profile` passthrough to select managed vs user browser profiles for browser execution planning.
- Kept execution strict on approval gating; no state-changing checkout actions are executed directly in V1.

## 0.2.1

- Added execution playbook generation for browser- and connector-based fulfillment.
- Added `cartwright execute` CLI command and `cartwright_build_execution_playbook` MCP tool.
- Added `browser_capture` as a first-class list import source for pasted OCR/scraped text handoff scenarios.
- Added action-level approval checks to keep browser-driven shopping gated and auditable.

## 0.1.0

- Initial Cartwright personal shopping plugin.
- Added shopping behavior, purchase boundaries, and marketplace metadata.
- Added seamless shopping flow, reusable profile template, and purchase brief template.
- Added grocery shopping-list source discovery for Google Keep, Google-device lists, Alexa lists, receipts, Drive, and retailer history.
- Added per-source grocery list retrieval playbook with direct routes and fallbacks.
- Added data integration plan for Keep, Alexa, Gmail, Drive, Walmart, OCR, pasted text, and local canonical storage.

## 0.2.0

- Added local `cartwright.sqlite` store and canonical item schema.
- Added CLI and MCP runtime entry points for profile/list/receipt importing, grocery planning, and exports.
- Added `pyproject.toml` and MCP registration for local stdio execution.
- Added parsers for pasted lists, connector payloads, and receipt extraction with duplicate merging.
