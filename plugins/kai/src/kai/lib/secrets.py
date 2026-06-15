"""kai secret-acquisition primitive.

The general flow for any platform kai operates on:

    1. Open the platform's dashboard in the browser.
    2. Pop a secret-entry window (parameterized per service).
    3. Validate the secret against the platform's API.
    4. Save to Eidos Vault (`eidos vault set`) and/or an env file.

The shape is universal across Slack / GitHub / Linear / Notion / Vercel / etc.
This module owns the orchestration; per-service knowledge (dashboard URL,
instructions, validator) lives in a SecretService instance.

Storage: kai uses **Eidos Vault** (`eidos vault`). Knox is Daniel's personal
secrets agent — out of scope for kai. Eidos Vault is the founder/team-shared
vault, exposed via the public `eidos` CLI per the kai ROADMAP guard rail
(*"kai login / kai vault / kai mail — those are the public eidos CLI's job."*).

NOT in v0:
  - OAuth installation flows. We only do paste-the-token flows for now.
  - Secret rotation / expiry tracking. The vault holds; kai acquires.
  - Multi-environment service variants beyond a single per-service entry.
  - Direct vault-API integration. We shell out to `eidos vault set` so we
    pick up auth + Touch ID / biometric gates from the public CLI for free.
"""
from __future__ import annotations

import os
import subprocess
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from kai.lib import popup as _popup


@dataclass(frozen=True)
class SecretService:
    """Describes a service kai can acquire a secret for.

    All fields are caller-facing (rendered in the popup or printed). The
    validator returns a list of (label, value) identity rows on success and
    raises on failure — this is what the confirmation popup displays.
    """

    name: str  # short id used by `kai login <name>` (e.g. "slack", "github")
    display_name: str  # human-readable (e.g. "Slack", "GitHub")
    dashboard_url: str  # the page kai opens in the browser
    instructions: str  # multi-line prose shown in the popup
    secret_label: str  # field label in the popup (e.g. "Bot token (xoxb-…)")
    default_label: str  # default reference label
    default_vault_path: str  # default Eidos Vault path
    env_var_name: str  # env var the platform module reads
    default_env_file: str  # default env file path
    validator: Callable[[str], list[tuple[str, str]]]  # raises on failure


@dataclass
class AcquireResult:
    """What `acquire_secret` returns to the caller."""

    success: bool
    service: SecretService
    secret: str | None
    actions: list[str]
    identity: list[tuple[str, str]]
    cancelled: bool = False


def acquire_secret(
    service: SecretService,
    *,
    no_browser: bool = False,
    no_popup: bool = False,
    print_fn: Callable[[str], None] = print,
) -> AcquireResult:
    """Run the full acquisition flow for one service.

    1. Open `service.dashboard_url` in the browser (unless no_browser).
    2. Pop the secret-entry window (or fall back to terminal if no_popup or no Tk).
    3. Run `service.validator(secret)` — it returns the identity rows or raises.
    4. Show confirm popup; on Save, write to Eidos Vault and/or env file.
    """
    if not no_browser:
        try:
            webbrowser.open(service.dashboard_url)
        except Exception:  # noqa: BLE001
            print_fn(f"(could not auto-open browser; visit {service.dashboard_url})")

    if no_popup:
        entry = _popup._terminal_prompt_for_secret(service)
    else:
        entry = _popup.prompt_for_secret(service)

    if entry.cancelled or not entry.secret:
        return AcquireResult(
            success=False, service=service, secret=None,
            actions=[], identity=[], cancelled=True,
        )

    # Validation
    try:
        identity = service.validator(entry.secret)
    except Exception as e:  # noqa: BLE001
        print_fn(f"{service.display_name} rejected the secret: {e}")
        return AcquireResult(
            success=False, service=service, secret=None,
            actions=[], identity=[], cancelled=False,
        )

    # No second popup — single-popup flow. Validation passed, we save.
    actions: list[str] = []

    # Write env file (the safer fallback — done first so a vault failure doesn't lose the token)
    if entry.write_to_env_file:
        env_path = Path(entry.env_file_path).expanduser()
        env_path.parent.mkdir(parents=True, exist_ok=True)
        existing: list[str] = env_path.read_text().splitlines() if env_path.exists() else []
        kept = [ln for ln in existing if not ln.startswith(f"{service.env_var_name}=")]
        kept.append(f"{service.env_var_name}={entry.secret}")
        env_path.write_text("\n".join(kept) + "\n")
        try:
            os.chmod(env_path, 0o600)
        except OSError:
            pass
        actions.append(f"wrote {env_path} (chmod 600)")

    # Write to Eidos Vault via `eidos vault set <path> <value>`
    if entry.write_to_vault:
        path = entry.vault_path
        try:
            subprocess.run(
                ["eidos", "vault", "set", path, entry.secret,
                 "-d", f"{service.display_name} secret (label: {entry.label})"],
                check=True, capture_output=True, text=True,
            )
            actions.append(f"saved to Eidos Vault path '{path}'")
        except FileNotFoundError:
            actions.append("(eidos CLI not on PATH — vault save skipped)")
        except subprocess.CalledProcessError as e:
            err = (e.stderr or e.stdout or "").strip().splitlines()[-1:] or [f"exit {e.returncode}"]
            actions.append(f"(eidos vault set failed: {err[0]})")
            if not entry.write_to_env_file:
                # Surface that the secret didn't land anywhere durable
                print_fn("Vault save failed and env file wasn't selected. Re-run kai login.")

    return AcquireResult(
        success=True, service=service, secret=entry.secret,
        actions=actions, identity=identity, cancelled=False,
    )


# ─── service registry ────────────────────────────────────────────────────────


def _validate_slack(token: str) -> list[tuple[str, str]]:
    """Validate via Slack's auth.test. Raises on failure; returns identity rows on success."""
    if not (token.startswith("xoxp-") or token.startswith("xoxb-")):
        raise ValueError("Slack tokens start with xoxp- or xoxb-.")
    from slack_sdk import WebClient
    client = WebClient(token=token)
    resp = client.auth_test()  # raises SlackApiError on bad token
    rows: list[tuple[str, str]] = []
    for k in ("team", "user", "user_id", "team_id", "bot_id"):
        v = resp.get(k)
        if v:
            rows.append((k, str(v)))
    return rows


SLACK = SecretService(
    name="slack",
    display_name="Slack",
    # Deep-link directly to the kai app's OAuth & Permissions page so the user
    # doesn't have to navigate. App ID is the kai Slack app installed in eidosagi.
    dashboard_url="https://api.slack.com/apps/A0B2CC38GJW/oauth",
    instructions=(
        "1. Click \"Copy URL\" below (or \"Open in browser\").\n"
        "2. Sign in to Slack if you aren't already.\n"
        "3. On the OAuth & Permissions page, find \"Bot User OAuth Token\".\n"
        "4. Click the Copy button next to it (token starts with xoxb-).\n"
        "5. Come back to this popup and paste in the field below.\n"
        "6. Click Save to Vault."
    ),
    secret_label="Bot User OAuth Token (xoxb-…):",
    default_label="kai-slack",
    default_vault_path="slack/eidos/kai-token",
    env_var_name="KAI_SLACK_TOKEN",
    default_env_file="~/.kai/.env",
    validator=_validate_slack,
)


# Service registry — `kai login <name>` looks here. Add new services as platforms come online.
REGISTRY: dict[str, SecretService] = {
    SLACK.name: SLACK,
}


def get_service(name: str) -> SecretService:
    if name not in REGISTRY:
        raise KeyError(
            f"No SecretService registered for '{name}'. "
            f"Known: {sorted(REGISTRY)}"
        )
    return REGISTRY[name]
