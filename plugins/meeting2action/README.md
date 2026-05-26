# Meeting2Action

Codex plugin for installing and operating the Eidos Google Meet recordings
router.

The router is intentionally small: it copies recent matching files from the
meeting organizer's `Meet Recordings` folder into a shared Eidos company
`Founders Recordings` folder.

It does not move originals, mutate Calendar events, write HubSpot, or process
transcripts automatically.

## Safety

- Install only while authenticated as an `@eidosagi.com` Google account.
- Use a shared Eidos company Drive folder as the destination.
- Copy files; do not move them.
- Keep the original Meet/Calendar/email links intact.
- Treat transcript processing and HubSpot writes as later, reviewed steps.

## Install

Prerequisites:

- `npx` available.
- `npx -y @google/clasp show-authorized-user` reports an `@eidosagi.com` account.
- Apps Script API enabled for that account: `https://script.google.com/home/usersettings`.
- Destination folder ID for the Eidos company `Founders Recordings` folder.

```bash
plugins/meeting2action/scripts/install.sh <DEST_FOLDER_ID>
```

The installer checks `clasp login --status` and refuses non-Eidos accounts.
