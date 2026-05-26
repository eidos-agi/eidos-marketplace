---
name: meeting2action
description: Use when installing, auditing, or operating the Eidos Google Meeting2Action that copies founder-call recording artifacts into the shared company Drive folder.
---

# Meeting2Action

Use this skill when the user asks to set up or check automation for routing
Google Meet recordings into the Eidos company Drive.

## Rules

- Do not install with a personal, Boone Voyage, or unverified Google account.
- Require `clasp show-authorized-user` to show an `@eidosagi.com` account before
  creating or pushing Apps Script code.
- Require the destination folder ID to be the Eidos company shared folder.
- Copy artifacts only. Do not move originals from `Meet Recordings`.
- Do not write HubSpot, send messages, or publish transcripts.
- If auth or folder ownership is unclear, stop and report the blocker.

## Install Flow

From the `eidos-marketplace` repo root:

```bash
plugins/meeting2action/scripts/install.sh <DEST_FOLDER_ID>
```

Then verify:

```bash
plugins/meeting2action/scripts/status.sh
```

## Operating Model

The Apps Script runs on a time trigger and scans the organizer's `Meet
Recordings` folder. It copies recent files whose names look like founder-call
recordings, transcripts, or notes into the destination Eidos folder, then records
the source ID in script properties to avoid duplicate copies.

Future versions may match Calendar attendees and write structured metadata.
