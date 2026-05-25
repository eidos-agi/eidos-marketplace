# Knox

Knox is a local MCP broker focused on **capability-based secret brokering**.

## What it does

- Manages short-lived action sessions (`15`, `60`, or `180` minutes).
- Manages proxy tokens (agent-scoped, short-lived bearer grants).
- Enforces tool-scoped policy before every provider action.
- Keeps raw credentials in the OS credential store.
- Exposes MCP tools for session/proxy lifecycle and a generic `knox_invoke` action path.

## Tool surface

- `knox_issue_session`
- `knox_issue_proxy_token`
- `knox_revoke_session`
- `knox_revoke_proxy_token`
- `knox_session_status`
- `knox_proxy_token_status`
- `knox_pairing_status`
- `knox_pair_device`
- `knox_invoke`
- `knox_store_secret`
- `knox_list_secrets`
- `knox_pairing_status`
- `knox_pair_device`

## Storage posture

- Provider secrets are stored only in macOS Keychain for v1.
- No plaintext token fallback is allowed in v1 mode.

## Key setup flow

- Call `knox_store_secret` first with `dry_run: true` to preview the generated name:
  - `provider` (for example `github` or `openrouter`)
  - optional metadata: `source`, `project`, `environment`, `notes`
  - optional `key_name`
  - Issue a session scoped to `knox:store_secret`.
- Call `knox_store_secret` again with `session_token`, `provider`, pasted `secret`, and metadata.
- The tool stores secret material in Keychain and persists metadata in `~/.knox/registry.json` with restrictive file permissions.
- Issue a session scoped to `knox:list_secrets` before using `knox_list_secrets` to audit stored key names and metadata.
- You can also issue a `knox_issue_proxy_token` and store a `secret_bindings` map (for example `{"github": "github-ci-key"}`) that binds provider operations to explicit key names.

## Setup / pairing mode

- Knox can run in setup-required mode with `KNOX_REQUIRE_PAIRING=1`.
- First-time setup starts with:
  - `knox_pairing_status` (reports `paired: false` and setup-required state)
  - `knox_pair_device` to request a 6-digit pairing code.
- Complete pairing by calling `knox_pair_device` with `challenge_token` + `challenge_code`.
- Until paired, any non-setup tool returns a setup-required error with guidance:
  - `knox_issue_session`, `knox_issue_proxy_token`, `knox_store_secret`, `knox_list_secrets`, `knox_invoke`, and status/revoke tools.
- In v1, no session/proxy issuance is possible before pairing when setup mode is enabled.

### Pairing UX

- `knox_pairing_status` now returns a machine-readable state object:
  - `paired`, `pairing_required`, `status`, and `next_step`.
- `knox_pair_device` now always returns a guided payload:
  - `status` (`challenge_issued`, `paired`, or `already_paired`)
  - `challenge_token` (if starting flow)
  - `message`
  - `next_step` (copy/paste step for the next tool call)

## Notes

- Biometric approval is preferred by default (`authorize_human` path).
- Optional 6-digit challenge-based fallback can be enabled with `challenge_compat_mode`.
- For manual six-digit mode (no pop-up), pass `challenge_code_setup` with exactly six digits in the initial challenge call, then redeem with `challenge_token` + `challenge_code`.

## Mac UX (v1)

- On macOS, Knox shows simple native approval dialogs for session/proxy requests:
  - request summary (label / ttl / scopes),
  - explicit `Approve` / `Deny` actions.
- For fallback challenge mode without `challenge_code_setup`, Knox also shows the generated code in a local dialog.
- No browser is required for approvals.
- In code-first installs, the server can run in `KNOX_CODE_ONLY_APPROVAL=1` mode (default in plugin runtime), so every session/proxy request uses code flow and requires your 6-digit code (no biometrics required).

### Mac UX (v2 tray mode)

- Optional tray helper: `apps/KnoxMenuBar` is a native status-bar control surface that reads
  `~/.knox/approval-control.json` and shows pending approval requests with:
  - request details,
  - 6-digit code field,
  - `Approve` / `Deny`,
  - `Copy code` when a challenge code is available.
- The tray app is enabled when:
  - `KNOX_APPROVAL_MODE=tray` (per-request approval UI),
  - `KNOX_APPROVAL_MODE=hybrid` (tray approval + code fallback),
  - `KNOX_TRAY_BINARY` (optional explicit path to override binary lookup).
- v1 default behavior remains code-first (`KNOX_APPROVAL_MODE=code`) and does not require tray.

Build/run the tray helper:

```bash
cd apps/KnoxMenuBar
swift build -c release
```

Then launch with a running MCP server in tray/hybrid mode:

```bash
KNOX_APPROVAL_MODE=tray /usr/bin/python3 scripts/knox/bootstrap.py
```

If `KNOX_REQUIRE_PAIRING=1`, the tray shows setup state and blocks risky flows until pairing is complete.

```json
{
  "name": "knox_issue_session",
  "arguments": {
    "ttl_minutes": 15,
    "request_label": "manual-unlock-demo",
    "scopes": ["github:list_repos"],
    "challenge_compat_mode": true,
    "challenge_code_setup": "123456"
  }
}
```

Pairing example:

```json
{
  "name": "knox_pairing_status",
  "arguments": {}
}
```

```json
{
  "name": "knox_pair_device",
  "arguments": {
    "challenge_code_setup": "123456"
  }
}
```

Redeem pairing code:

```json
{
  "name": "knox_pair_device",
  "arguments": {
    "challenge_token": "<from-previous-call>",
    "challenge_code": "123456"
  }
}
```

Redeem:

```json
{
  "name": "knox_issue_session",
  "arguments": {
    "ttl_minutes": 15,
    "request_label": "manual-unlock-demo",
    "scopes": ["github:list_repos"],
    "challenge_token": "<from-previous-call>",
    "challenge_code": "123456"
  }
}
```
