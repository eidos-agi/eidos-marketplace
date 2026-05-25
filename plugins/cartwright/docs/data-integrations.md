# Cartwright Data Integration Plan

This document describes practical data integrations for grocery lists, prior purchases, receipts, and Walmart delivery.

## Summary

| Source | Best integration | Status | Recommendation |
| --- | --- | --- | --- |
| Google Keep / Google-device lists | Google Keep API for Workspace domains; otherwise user export/paste/screenshot | Official API exists, but it is enterprise-oriented and admin/OAuth gated | Treat as optional advanced integration; use Drive/Gmail/user import as default |
| Alexa shopping list | No supported official list-sync API | Alexa List Management REST API was retired July 1, 2024 | Do not build on official sync; use user share/export/screenshot or a separate Cartwright list |
| Gmail receipts | Gmail API search and read | Official and viable with user authorization | Use as primary prior-purchase source |
| Google Drive docs/sheets | Drive search/read/export and Sheets values read | Official and viable with user authorization | Use for user-maintained lists, copied Keep lists, meal plans, and grocery docs |
| Walmart grocery/cart | Current Codex Walmart connector; Walmart OPD/Add-to-Cart/Affiliate if approved | Product/basket discovery viable; consumer history not exposed | Use for basket building and checkout handoff; use receipts for history |
| Screenshots/photos | Vision/OCR to structured list schema | Viable | Use for Alexa/Keep screenshots and paper lists |
| Pasted text | Local parser to structured list schema | Viable | Always support as lowest-friction fallback |
| Local canonical store | Local SQLite/JSON profile and list ledger | Viable | Make this Cartwright's reliable memory layer |

## Google Keep And Google-Device Lists

Official path:

- Google has a Keep API under Google Workspace for creating, listing, getting, deleting notes, downloading attachments, and changing note permissions.
- The API is positioned for enterprise administration/CASB use cases, not simple consumer Gmail automation.
- Domain-wide delegation or admin-approved OAuth is the realistic official path for production.

Implementation:

1. Add an optional `keep` source adapter.
2. Detect whether a direct Google Keep connector/API credential is available.
3. If available, list notes and filter by titles/labels/content such as `shopping`, `groceries`, `Walmart`, `grocery list`.
4. Parse list notes into Cartwright's canonical item schema.
5. If unavailable, ask the user to paste/export/screenshot the list or copy it into a Google Doc/Sheet.

Risk:

- Do not promise Keep access for normal personal Gmail accounts.
- Do not claim Drive search checked Keep; it only checks Drive files.

## Alexa Shopping Lists

Official path:

- Amazon retired Alexa List skills and the List Management REST API for Alexa Shopping and To-Do lists as of July 1, 2024.
- Alexa Shopping Actions still exist for shopping flows, but they are not a Shopping List sync API.
- Amazon retail seller/vendor APIs are not consumer shopping-list or order-history APIs.

Implementation:

1. Do not build a first-party Alexa list sync dependency.
2. Support import routes: paste, screenshot, share/export from Alexa app, email to self, or copy into Cartwright's canonical list.
3. Optionally evaluate unofficial MCP/browser-cookie bridges only as an explicit user-installed advanced integration.
4. Keep Alexa actions separate from list retrieval.

Risk:

- Unofficial bridges are fragile and may depend on cookies, scraping, or reverse-engineered endpoints.
- They should be opt-in and clearly marked unsupported.

## Gmail Receipts And Order Confirmations

Official path:

- Gmail API `users.messages.list` supports the `q` parameter for Gmail search syntax.
- Use narrow searches for receipts and order confirmations, then fetch selected messages.

Implementation:

1. Request least-privilege Gmail read access available in the connector/API environment.
2. Search queries:
   - `from:(walmart.com) (receipt OR order OR delivered)`
   - `subject:(Walmart receipt OR Walmart order OR grocery order)`
   - `(receipt OR "order confirmation" OR "your order") newer_than:180d`
   - retailer-specific variants for Costco, Target, Amazon, Instacart, Kroger, HEB, etc.
3. Extract:
   - retailer, date, line items, quantities, brands, sizes, prices, substitutions, delivery/pickup status.
4. Store normalized item facts as prior-purchase evidence, not current intent.

Risk:

- Gmail search differs from UI search in some edge cases.
- Receipts imply historical preference, not current need.
- Avoid broad mailbox reads when a narrow search will work.

## Google Drive Docs And Sheets

Official path:

- Drive API can search files by name, MIME type, and `fullText contains`.
- Docs and Sheets APIs can read document text/tables and spreadsheet values.

Implementation:

1. Search Drive for likely list files:
   - `shopping list`
   - `groceries`
   - `Walmart`
   - `Costco`
   - `meal plan`
   - `pantry`
2. Prefer recently modified docs/sheets and user-viewed files.
3. Read content through Docs/Sheets connectors.
4. Parse unchecked checklist rows, active sections, and recent meal-plan items.
5. Ignore archived/completed sections when detectable.

Risk:

- Drive full-text search can be noisy.
- Ask the user for the file name/link when search results are ambiguous.

## Walmart Grocery Delivery

Current path:

- In this Codex environment, Walmart exposes `product_search` and `basket_builder`.
- No Walmart order-history, receipt, favorites, reorder, account, delivery-slot, checkout, or payment tool is currently exposed.

Official/API path:

- Walmart's public official APIs are mainly Marketplace/Seller, Affiliate, OPD, Add-to-Cart, and partner APIs.
- Consumer account order history and personal receipts are not generally exposed as official public APIs.
- Checkout-style APIs are approval-gated or disabled in public service maps.

Implementation:

1. Use Walmart connector for product and basket discovery.
2. Use OPD/Add-to-Cart/Affiliate only if approved credentials become available.
3. Use Gmail/Drive/user-imported receipts for prior Walmart purchase intelligence.
4. Prepare a cart or checkout handoff, then stop for explicit approval.

Risk:

- Do not use seller APIs as if they were consumer account APIs.
- Do not claim delivery availability or checkout readiness without connector evidence.

## Screenshots, Photos, And Pasted Text

Implementation:

1. Accept pasted text as the baseline import path.
2. Accept screenshots/photos through vision/OCR when available.
3. Extract to canonical schema:

```json
{
  "source": "pasted_text | screenshot | gmail | drive | keep | alexa | walmart",
  "raw_text": "milk 2%",
  "normalized_name": "2% milk",
  "quantity": "1",
  "unit": "gallon",
  "brand_preference": null,
  "must_match_brand": false,
  "category": "dairy",
  "notes": null,
  "confidence": 0.93
}
```

4. Confirm low-confidence OCR, ambiguous quantities, or preference-sensitive substitutions.

Risk:

- OCR is not reliable enough to silently resolve ambiguous handwriting or cut-off screenshots.

## Local Canonical Store

Cartwright needs its own reliable memory layer because third-party list APIs are inconsistent.

Recommended local tables/files:

- `shopping_profile`: preferred retailers, brands, dietary rules, substitution rules, delivery preferences.
- `shopping_lists`: active imported lists with source provenance.
- `shopping_items`: normalized items, quantities, source, confidence, checked/completed state.
- `purchase_history`: receipt-derived item facts.
- `source_connections`: available connectors, last successful sync, permissions, failure reason.

Operating rule:

- External sources feed Cartwright.
- Cartwright's canonical list is the stable working state.
- User approval is required before writing back to external accounts or placing orders.

## Implementation Priority

1. Local canonical store and parser for pasted text.
2. Screenshot/photo OCR import.
3. Gmail receipt importer.
4. Drive docs/sheets shopping-list importer.
5. Walmart basket builder integration.
6. Optional Google Keep adapter for Workspace/admin-enabled accounts.
7. Alexa import via manual share/screenshot; unofficial bridge only if explicitly installed and accepted.
