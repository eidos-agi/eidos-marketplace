---
name: browser-autonomy
description: Use when a task involves browsing the web, opening or operating a website, using Browser or Chrome automation, logging in, working with username/password forms, handling account sessions, clicking through web UIs, inspecting pages, taking browser screenshots, or verifying web behavior. Prioritize doing the browser work directly instead of asking the user to do it.
---

# Browser Autonomy

## Default stance

When a user asks for browser-based work, assume they want the agent to operate the browser directly. Do the clicking, typing, navigation, inspection, screenshots, downloads, and verification yourself with available browser tools.

Do not ask the user to open pages, click buttons, inspect elements, copy text from the page, or complete ordinary web steps if browser automation can do it.

## Tool selection

- Use the Codex in-app Browser for local web targets such as `localhost`, `127.0.0.1`, `::1`, file URLs, and local app verification.
- Use Chrome automation for remote sites where the user's existing browser profile, signed-in sessions, cookies, extensions, or password manager may matter.
- Use web search or direct HTTP browsing for information gathering when page interaction or authentication is not needed.
- If no browser tool is currently callable, search for the relevant Browser or Chrome tools before falling back.

## Login and credential handling

Use only accounts, sessions, and credentials the user is authorized to use. Do not bypass access controls, MFA, CAPTCHA, paywalls, rate limits, or security prompts.

When authentication is needed, try these paths in order:

1. Reuse an existing signed-in session in the selected browser profile.
2. Use SSO or an already-authorized login flow available in the browser.
3. Use browser or password-manager autofill if it is already unlocked and available through the normal page or extension UI.
4. If a password manager asks for a local unlock, ask the user to unlock it locally; do not ask for the master password in chat.
5. If credentials are missing, expired, or require a new secret, ask the user for the minimum safe next step, such as signing in once in the browser or adding the credential to their password manager.

Never ask the user to paste passwords, API keys, recovery codes, or one-time codes into chat. Never read, export, dump, or scrape password stores. Do not store secrets in files, logs, notes, plans, or final answers.

## When to ask the user

Ask only when progress is blocked by something the agent cannot safely or legitimately complete:

- MFA, CAPTCHA, biometric prompts, hardware security keys, or account recovery.
- A missing credential that is not available through an existing browser session or authorized autofill.
- A permission, purchase, legal agreement, destructive account action, or identity assertion requiring explicit human consent.
- A website condition that demands human judgment outside the task.

Keep the ask concise and specific. After the user completes the blocking step, resume the browser work yourself.

## Completion standard

For browser tasks, finish by reporting what was done and, when useful, the page state or verification evidence. If the task touched credentials or login flows, mention only the outcome, never secret values.
