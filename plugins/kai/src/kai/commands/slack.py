"""kai slack — operate in Slack as kai.

When an agent (or Daniel kai Vybhav) needs to read, write, manage, admin,
diagnose, or update Slack from the terminal, this is the toolkit. Thin wrapper
over slack-sdk for runtime ops + slack-cli for app/manifest lifecycle.

Auth: requires `KAI_SLACK_TOKEN` env var. Either a user token (xoxp-) or
a bot token (xoxb-) works — pick based on what kai needs to do:
  - xoxp- (user) → acts as you, can read DMs and full history
  - xoxb- (bot) → acts as a bot, cleaner for automation

The privilege boundary is at the Slack-app layer (kai vs @Eidos), not inside kai.
See PLATFORMS.md and SLACK.md at the repo root for the full architecture.

Channel arguments accept either a channel ID (C0123ABCD) or a name (#general
or general). Names resolve to IDs via conversations.list (cached per-process).

Substrate guards (per CONVENTIONS.md "make the wrong action harder than the right action"):
  - Every mutating verb honors --dry-run. Prints API call shape; exits zero without calling Slack.
  - Irreversible verbs require --yes (archive, kick, convert-to-private, message delete,
    bookmark remove, usergroup remove, schedule cancel, file delete). Hard fail without it.

Storage: none — pure dispatcher to Slack's Web API.

NOT in v0:
  - Real-time event streaming (RTM / Socket Mode). Use slack-eidos for that.
  - Canvas / Block Kit composition. Plain text first.
  - OAuth install flow. Bring your own token.
  - Rate-limit handling beyond slack-sdk's defaults. Add if we hit walls.
  - DM sending by user name. Use channel IDs (D...) directly.
  - Admin-grade APIs requiring Enterprise Grid (admin.conversations.*, admin.users.*).
  - Huddle / call control. No durable CLI use case.
  - Status / DnD / personal ergonomics. Belongs in the Slack app, not a CLI verb.
  - Custom emoji upload. Rare, file-heavy, low ROI.
  - convert-to-public. Slack does not expose this API.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table


app = typer.Typer(
    name="slack",
    help="Operate in Slack as kai — read, write, manage, admin.",
    invoke_without_command=True,
    no_args_is_help=False,
    add_completion=False,
)

_console = Console()

TOKEN_ENV = "KAI_SLACK_TOKEN"
CONFIG_TOKEN_ENV = "KAI_SLACK_CONFIG_TOKEN"
ADMIN_TOKEN_ENV = "KAI_SLACK_ADMIN_TOKEN"
SLACK_APP_ID = "A0B2CC38GJW"
SLACK_TEAM_DOMAIN = "eidosagi"
SLACK_TEAM_ID = "T0AV46DB675"


# ─── auth + helpers ──────────────────────────────────────────────────────────


def _client():
    """Build a slack-sdk WebClient. Fail loud if no token."""
    token = os.environ.get(TOKEN_ENV)
    if not token:
        _console.print(
            f"[red]No Slack token.[/red] Set [bold]${TOKEN_ENV}[/bold] "
            f"to a user token (xoxp-) or bot token (xoxb-).\n"
            f"[dim]Generate at https://api.slack.com/apps → your app → OAuth & Permissions.[/dim]",
        )
        raise typer.Exit(1)
    if not (token.startswith("xoxp-") or token.startswith("xoxb-")):
        _console.print(
            f"[yellow]Warning:[/yellow] ${TOKEN_ENV} doesn't start with xoxp- or xoxb-. "
            "Continuing anyway."
        )
    from slack_sdk import WebClient
    return WebClient(token=token)


@lru_cache(maxsize=1)
def _channel_index() -> dict[str, str]:
    """name → id map. Cached for the process lifetime."""
    client = _client()
    index: dict[str, str] = {}
    cursor: str | None = None
    while True:
        resp = client.conversations_list(
            cursor=cursor, limit=200, exclude_archived=True,
            types="public_channel,private_channel",
        )
        for ch in resp.get("channels", []):
            index[ch["name"]] = ch["id"]
        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
    return index


def _resolve_channel(channel: str) -> str:
    """Accept a channel ID or name (with or without #). Return the ID."""
    if channel.startswith(("C", "D", "G")) and len(channel) >= 9:
        return channel
    name = channel.lstrip("#")
    idx = _channel_index()
    if name not in idx:
        _console.print(
            f"[red]No channel named '{name}'.[/red] "
            f"Pass a channel ID directly or check `kai slack channels`."
        )
        raise typer.Exit(1)
    return idx[name]


def _resolve_user(user: str) -> str:
    """Accept a user ID (U... or W...) or @handle. Return ID. Falls back to as-given."""
    if user.startswith(("U", "W")) and len(user) >= 9:
        return user
    handle = user.lstrip("@")
    try:
        client = _client()
        resp = client.users_list(limit=200)
        for u in resp.get("members", []):
            if u.get("name") == handle or u.get("profile", {}).get("display_name") == handle:
                return u["id"]
    except Exception:  # noqa: BLE001
        pass
    return user  # let Slack reject it loudly downstream


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _config_token() -> str:
    """Token for Slack app-configuration APIs such as apps.icon.set."""
    token = os.environ.get(CONFIG_TOKEN_ENV) or os.environ.get(TOKEN_ENV)
    if not token:
        _console.print(
            f"[red]No Slack app-configuration token.[/red] Set ${CONFIG_TOKEN_ENV} "
            f"to a user/service token with [bold]app_configurations:write[/bold]."
        )
        raise typer.Exit(1)
    if token.startswith("xoxb-"):
        _console.print(
            "[red]The current Slack token is a bot token.[/red] "
            "Slack's apps.icon.set API requires a user/service token with "
            "[bold]app_configurations:write[/bold].\n"
            "[dim]Mint one with `slack auth token`, then export it as "
            f"${CONFIG_TOKEN_ENV} before running this command.[/dim]"
        )
        raise typer.Exit(1)
    return token


def _post_app_icon(token: str, app_id: str, icon_path: Path):
    """Set the Slack app icon through apps.icon.set."""
    from slack_sdk import WebClient

    client = WebClient(token=token)
    with icon_path.open("rb") as f:
        return client.api_call(
            "apps.icon.set",
            http_verb="POST",
            data={"app_id": app_id},
            files={"file": f},
        )


def _admin_token() -> str:
    """Token for Slack Admin APIs."""
    token = os.environ.get(ADMIN_TOKEN_ENV)
    if not token:
        _console.print(
            f"[red]No Slack admin token.[/red] Set ${ADMIN_TOKEN_ENV} to a user token "
            "with [bold]admin.teams:write[/bold].\n"
            "[dim]Slack documents workspace-icon API access as Enterprise-only; "
            "non-Enterprise workspaces should use the workspace admin UI.[/dim]"
        )
        raise typer.Exit(1)
    if token.startswith("xoxb-"):
        _console.print(
            "[red]The current Slack admin token is a bot token.[/red] "
            "admin.teams.settings.setIcon requires an admin/owner user token "
            "with [bold]admin.teams:write[/bold]."
        )
        raise typer.Exit(1)
    return token


def _post_workspace_icon(token: str, team_id: str, image_url: str):
    """Set the Slack workspace icon through admin.teams.settings.setIcon."""
    from slack_sdk import WebClient

    client = WebClient(token=token)
    return client.admin_teams_settings_setIcon(team_id=team_id, image_url=image_url)


def _fmt_ts(slack_ts: str) -> str:
    """Slack timestamps are float strings ('1730481234.123456'). Render as UTC."""
    try:
        dt = datetime.fromtimestamp(float(slack_ts), tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return slack_ts


def _require_yes(yes: bool, verb: str, target: str) -> None:
    """Substrate guard: irreversible verbs refuse to run without --yes."""
    if not yes:
        _console.print(
            f"[red]{verb} is irreversible.[/red] Re-run with [bold]--yes[/bold] "
            f"to confirm. Target: [bold]{target}[/bold].\n"
            f"[dim]Or pass --dry-run first to see exactly what would happen.[/dim]"
        )
        raise typer.Exit(2)


# ─── help ────────────────────────────────────────────────────────────────────


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        _show_help()


def _show_help() -> None:
    _console.print()
    _console.print("[bold]kai slack[/bold] — operate in Slack as kai")
    _console.print()
    _console.print("[bold cyan]Setup & lifecycle[/bold cyan]")
    _console.print("  [bold]login[/bold]                           Browser → popup → validate → save token to Eidos Vault")
    _console.print("  [bold]doctor[/bold]                          End-to-end health: slack-cli, install, scopes, vault, token")
    _console.print("  [bold]brand[/bold]                           Show Slack app brand fields and icon asset paths")
    _console.print("  [bold]icon set[/bold]                        Upload the canonical kai icon via apps.icon.set")
    _console.print("  [bold]icon set-workspace[/bold]              Upload the company icon via admin.teams.settings.setIcon")
    _console.print("  [bold]manifest init[/bold]                   Scaffold the slack-cli project at .slack-config/")
    _console.print("  [bold]manifest validate[/bold]               Validate the local manifest.json")
    _console.print("  [bold]manifest info[/bold] [--source remote] Show current manifest (project or remote)")
    _console.print("  [bold]manifest push --yes[/bold]             Apply local manifest scopes to the kai app")
    _console.print("  [bold]manifest pull[/bold]                   Overwrite local manifest with remote (live) version")
    _console.print()
    _console.print("[bold cyan]Read[/bold cyan]")
    _console.print("  [bold]me[/bold]                              Sanity check — show authenticated identity")
    _console.print("  [bold]channels[/bold] [--joined]             List channels")
    _console.print("  [bold]info[/bold] <ch>                       Channel info — creator, topic, members, archived?")
    _console.print("  [bold]members[/bold] <ch>                    List channel members")
    _console.print("  [bold]read[/bold] <ch> [-n N]                Last N messages, newest first")
    _console.print("  [bold]thread[/bold] <ch> <ts>                Read a thread")
    _console.print('  [bold]search[/bold] "<query>"                Full-text search (xoxp- token)')
    _console.print()
    _console.print("[bold cyan]Write — content[/bold cyan]")
    _console.print('  [bold]send[/bold] <ch> "<text>"              Post a message')
    _console.print('  [bold]message edit[/bold] <ch> <ts> "..."    Edit your own message')
    _console.print("  [bold]message delete[/bold] <ch> <ts>        Delete your own message [--yes]")
    _console.print("  [bold]react[/bold] <ch> <ts> <emoji>         Add a reaction")
    _console.print("  [bold]pin[/bold] / [bold]unpin[/bold] <ch> <ts>           Pin / unpin a message")
    _console.print('  [bold]bookmark add[/bold] <ch> "<title>" <url>')
    _console.print("  [bold]bookmark remove[/bold] <ch> <id>       [--yes]")
    _console.print("  [bold]bookmark list[/bold] <ch>")
    _console.print("  [bold]dm open[/bold] <user>                  Open a DM, return the channel ID")
    _console.print('  [bold]schedule[/bold] <ch> "<text>" --at <iso>')
    _console.print("  [bold]schedule list[/bold]")
    _console.print("  [bold]schedule cancel[/bold] <ch> <id>       [--yes]")
    _console.print()
    _console.print("[bold cyan]Write — topology and membership[/bold cyan]")
    _console.print('  [bold]create[/bold] <name> [--private] [--topic "…"] [--purpose "…"] [--invite a,b,c]')
    _console.print("  [bold]archive[/bold] <ch> --yes              Close a channel")
    _console.print("  [bold]unarchive[/bold] <ch>                  Reopen")
    _console.print("  [bold]rename[/bold] <ch> <new>")
    _console.print('  [bold]topic[/bold] <ch> "…"                  Set topic line')
    _console.print('  [bold]purpose[/bold] <ch> "…"                Set purpose paragraph')
    _console.print("  [bold]invite[/bold] <ch> <users…>            Add member(s)")
    _console.print("  [bold]kick[/bold] <ch> <user> --yes")
    _console.print("  [bold]convert-to-private[/bold] <ch> --yes   ONE-WAY — Slack does not allow undo")
    _console.print()
    _console.print("[bold cyan]Write — user groups[/bold cyan]")
    _console.print('  [bold]usergroup create[/bold] <handle> --name "…" [--users a,b,c]')
    _console.print("  [bold]usergroup add[/bold] <handle> <users…>")
    _console.print("  [bold]usergroup remove[/bold] <handle> <users…> --yes")
    _console.print("  [bold]usergroup list[/bold]")
    _console.print()
    _console.print("[bold cyan]Write — files[/bold cyan]")
    _console.print("  [bold]file delete[/bold] <file_id> --yes")
    _console.print()
    _console.print(f"[dim]Auth: ${TOKEN_ENV} (xoxp- user token or xoxb- bot token).[/dim]")
    _console.print("[dim]Substrate: every mutating verb honors --dry-run; irreversible ones require --yes.[/dim]")
    _console.print()


# ─── brand ──────────────────────────────────────────────────────────────────


@app.command("brand")
def cmd_brand(json_out: bool = typer.Option(False, "--json", help="Emit JSON")):
    """Show the canonical kai Slack brand and icon paths."""
    root = _repo_root()
    icon_svg = root / "assets" / "kai-slack-icon.svg"
    icon_512 = root / "assets" / "kai-slack-icon-512.png"
    icon_128 = root / "assets" / "kai-slack-icon-128.png"
    brand_doc = root / "BRAND.md"
    admin_url = f"https://api.slack.com/apps/{SLACK_APP_ID}/general"
    payload = {
        "app_name": "kai",
        "bot_display_name": "kai",
        "description": "Founder multitool for Eidos AGI. The conjunction that joins.",
        "background_color": "#161210",
        "app_id": SLACK_APP_ID,
        "team_domain": SLACK_TEAM_DOMAIN,
        "admin_url": admin_url,
        "icon_svg": str(icon_svg),
        "icon_512_png": str(icon_512),
        "icon_128_png": str(icon_128),
        "brand_doc": str(brand_doc),
    }
    if json_out:
        typer.echo(json.dumps(payload))
        return

    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column("Field", style="bold")
    table.add_column("Value", overflow="fold")
    table.add_row("app name", payload["app_name"])
    table.add_row("bot display name", payload["bot_display_name"])
    table.add_row("description", payload["description"])
    table.add_row("background", payload["background_color"])
    table.add_row("icon source", payload["icon_svg"])
    table.add_row("slack upload", payload["icon_512_png"])
    table.add_row("small preview", payload["icon_128_png"])
    table.add_row("brand doc", payload["brand_doc"])
    table.add_row("slack admin", payload["admin_url"])
    _console.print()
    _console.print("[bold]kai Slack brand[/bold]")
    _console.print()
    _console.print(table)
    _console.print()
    _console.print("[dim]Slack app icons are uploaded in Basic Information → Display Information.[/dim]")
    _console.print()


icon_app = typer.Typer(name="icon", help="Slack app icon maintenance.", no_args_is_help=True)
app.add_typer(icon_app, name="icon")


@icon_app.command("set")
def cmd_icon_set(
    icon_path: Path = typer.Option(
        None,
        "--file",
        "-f",
        help="PNG to upload. Defaults to assets/kai-slack-icon-512.png.",
    ),
    app_id: str = typer.Option(SLACK_APP_ID, "--app-id", help="Slack app ID to update."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print what would be uploaded."),
):
    """Upload kai's Slack app icon.

    Requires a user/service token with Slack scope `app_configurations:write`.
    Bot tokens cannot update app configuration.
    """
    root = _repo_root()
    target = icon_path or (root / "assets" / "kai-slack-icon-512.png")
    target = target.expanduser()
    if not target.is_absolute():
        target = root / target
    if not target.exists():
        _console.print(f"[red]Icon file not found:[/red] {target}")
        raise typer.Exit(1)
    if target.suffix.lower() != ".png":
        _console.print(f"[red]Slack icon upload expects a PNG:[/red] {target}")
        raise typer.Exit(1)

    if dry_run:
        _console.print(f"[dim]would call[/dim] apps.icon.set app_id={app_id} file={target}")
        _console.print(f"[dim]requires[/dim] ${CONFIG_TOKEN_ENV} with app_configurations:write")
        return

    token = _config_token()
    try:
        resp = _post_app_icon(token, app_id, target)
    except Exception as e:  # noqa: BLE001
        response = getattr(e, "response", None)
        if response is not None:
            error = getattr(response, "data", {}).get("error", "unknown_error")
            _console.print(f"[red]Slack rejected icon upload:[/red] {error}")
        else:
            _console.print(f"[red]Slack icon upload failed:[/red] {e}")
        raise typer.Exit(1)

    if not resp.get("ok", False):
        _console.print(f"[red]Slack rejected icon upload:[/red] {resp.get('error', 'unknown_error')}")
        raise typer.Exit(1)

    _console.print(f"[green]✓ uploaded kai Slack icon[/green] → app {app_id}")


@icon_app.command("set-workspace")
def cmd_icon_set_workspace(
    image_url: str = typer.Argument(
        "https://eidosagi.com/logo-800.png",
        help="Public image URL Slack should use for the workspace icon.",
    ),
    team_id: str = typer.Option(SLACK_TEAM_ID, "--team-id", help="Slack workspace/team ID."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print the API call shape."),
):
    """Upload the Eidos AGI company icon as the Slack workspace icon.

    Slack documents this API as Enterprise-only. On regular Free/Pro/Business+
    workspaces, use Slack's admin UI: Admin → Edit workspace → Workspace icon.
    """
    if dry_run:
        _console.print(
            "[dim]would call[/dim] admin.teams.settings.setIcon "
            f"team_id={team_id} image_url={image_url}"
        )
        _console.print(f"[dim]requires[/dim] ${ADMIN_TOKEN_ENV} with admin.teams:write")
        _console.print("[dim]Slack docs mark this API Enterprise-only.[/dim]")
        return

    token = _admin_token()
    try:
        resp = _post_workspace_icon(token, team_id, image_url)
    except Exception as e:  # noqa: BLE001
        response = getattr(e, "response", None)
        if response is not None:
            error = getattr(response, "data", {}).get("error", "unknown_error")
            _console.print(f"[red]Slack rejected workspace-icon upload:[/red] {error}")
            if error in {"feature_not_enabled", "missing_scope", "not_an_admin", "not_allowed_token_type"}:
                _console.print(
                    "[dim]Fallback: open Slack Admin → Edit workspace → Workspace icon, "
                    "then upload the same company icon PNG.[/dim]"
                )
        else:
            _console.print(f"[red]Slack workspace-icon upload failed:[/red] {e}")
        raise typer.Exit(1)

    if not resp.get("ok", False):
        _console.print(f"[red]Slack rejected workspace-icon upload:[/red] {resp.get('error', 'unknown_error')}")
        raise typer.Exit(1)

    _console.print(f"[green]✓ uploaded Eidos AGI workspace icon[/green] → team {team_id}")


# ─── login (delegates to kai.lib.secrets.acquire_secret) ─────────────────────


@app.command("login")
def cmd_login(
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't open the browser"),
    no_popup: bool = typer.Option(False, "--no-popup", help="Skip the GUI popup; use the terminal flow"),
):
    """Bootstrap the Slack token: opens browser → popup → validates → saves to Eidos Vault.

    Delegates to `kai.lib.secrets.acquire_secret(SLACK)`. Same pattern works for
    every platform kai integrates with; see kai/lib/secrets.py.
    """
    from kai.lib.secrets import SLACK, acquire_secret

    result = acquire_secret(
        SLACK,
        no_browser=no_browser,
        no_popup=no_popup,
        print_fn=lambda msg: _console.print(f"[yellow]{msg}[/yellow]"),
    )
    if result.cancelled:
        _console.print("[yellow]Cancelled — no token written.[/yellow]")
        raise typer.Exit(1)
    if not result.success:
        raise typer.Exit(1)

    identity = dict(result.identity)
    user = identity.get("user", "?")
    workspace = identity.get("team", "?")
    _console.print()
    _console.print(f"[green]✓ logged in[/green] as [bold]{user}[/bold] in [bold]{workspace}[/bold]")
    for a in result.actions:
        _console.print(f"  [green]✓[/green] {a}")
    _console.print()


# ─── read verbs ──────────────────────────────────────────────────────────────


@app.command("me")
def cmd_me():
    """Sanity check — show authenticated identity."""
    client = _client()
    resp = client.auth_test()
    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for field in ("user", "user_id", "team", "team_id", "url", "bot_id"):
        if field in resp:
            table.add_row(field, str(resp[field]))
    _console.print()
    _console.print(table)
    _console.print()


@app.command("channels")
def cmd_channels(
    joined: bool = typer.Option(False, "--joined", help="Only channels you're a member of"),
    json_out: bool = typer.Option(False, "--json"),
):
    """List channels (public + private you can see)."""
    client = _client()
    channels = []
    cursor: str | None = None
    while True:
        resp = client.conversations_list(
            cursor=cursor, limit=200, exclude_archived=True,
            types="public_channel,private_channel",
        )
        for ch in resp.get("channels", []):
            if joined and not ch.get("is_member"):
                continue
            channels.append(ch)
        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    if json_out:
        typer.echo(json.dumps([
            {"id": c["id"], "name": c["name"], "private": c.get("is_private", False),
             "members": c.get("num_members", 0)}
            for c in channels
        ]))
        return

    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Type", style="dim")
    table.add_column("Members", style="dim", justify="right")
    for c in channels:
        kind = "private" if c.get("is_private") else "public"
        if c.get("is_member"):
            kind += " · joined"
        table.add_row(c["id"], "#" + c["name"], kind, str(c.get("num_members", "?")))
    _console.print()
    _console.print(f"[dim]{len(channels)} channels[/dim]")
    _console.print(table)
    _console.print()


@app.command("info")
def cmd_info(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    json_out: bool = typer.Option(False, "--json"),
):
    """Channel info — creator, topic, members, archived state."""
    client = _client()
    channel_id = _resolve_channel(channel)
    resp = client.conversations_info(channel=channel_id, include_num_members=True)
    ch = resp.get("channel", {})

    if json_out:
        typer.echo(json.dumps(ch, default=str))
        return

    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("id", ch.get("id", "?"))
    table.add_row("name", "#" + ch.get("name", "?"))
    table.add_row("private", str(ch.get("is_private", False)))
    table.add_row("archived", str(ch.get("is_archived", False)))
    table.add_row("members", str(ch.get("num_members", "?")))
    table.add_row("creator", ch.get("creator", "?"))
    created = ch.get("created")
    if created:
        table.add_row("created", datetime.fromtimestamp(int(created), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    table.add_row("topic", ch.get("topic", {}).get("value", "") or "[dim](empty)[/dim]")
    table.add_row("purpose", ch.get("purpose", {}).get("value", "") or "[dim](empty)[/dim]")
    _console.print()
    _console.print(table)
    _console.print()


@app.command("members")
def cmd_members(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    json_out: bool = typer.Option(False, "--json"),
):
    """List channel members."""
    client = _client()
    channel_id = _resolve_channel(channel)
    members: list[str] = []
    cursor: str | None = None
    while True:
        resp = client.conversations_members(channel=channel_id, cursor=cursor, limit=200)
        members.extend(resp.get("members", []))
        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    if json_out:
        typer.echo(json.dumps(members))
        return

    _console.print()
    _console.print(f"[dim]{len(members)} members of[/dim] [bold]{channel}[/bold]")
    for m in members:
        _console.print(f"  {m}")
    _console.print()


@app.command("read")
def cmd_read(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    n: int = typer.Option(20, "-n", "--limit", help="Number of messages to fetch"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON list"),
):
    """Read the last N messages from a channel (default 20, newest first)."""
    client = _client()
    channel_id = _resolve_channel(channel)
    resp = client.conversations_history(channel=channel_id, limit=n)
    messages = resp.get("messages", [])

    if json_out:
        typer.echo(json.dumps([
            {"ts": m.get("ts"), "user": m.get("user"), "text": m.get("text")}
            for m in messages
        ]))
        return

    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("When", style="dim", no_wrap=True)
    table.add_column("Who", style="bold", no_wrap=True)
    table.add_column("Text", overflow="fold")
    for m in messages:
        when = _fmt_ts(m.get("ts", ""))
        who = m.get("user") or m.get("bot_id") or m.get("username") or "?"
        text = (m.get("text") or "").replace("\n", " ⏎ ")
        table.add_row(when, who, text)
    _console.print()
    _console.print(table)
    _console.print()


@app.command("thread")
def cmd_thread(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    ts: str = typer.Argument(..., help="Thread parent timestamp"),
    json_out: bool = typer.Option(False, "--json"),
):
    """Read a thread by parent timestamp."""
    client = _client()
    channel_id = _resolve_channel(channel)
    resp = client.conversations_replies(channel=channel_id, ts=ts)
    messages = resp.get("messages", [])

    if json_out:
        typer.echo(json.dumps([
            {"ts": m.get("ts"), "user": m.get("user"), "text": m.get("text")}
            for m in messages
        ]))
        return

    if not messages:
        _console.print("[dim]Empty thread.[/dim]")
        return
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("When", style="dim", no_wrap=True)
    table.add_column("Who", style="bold", no_wrap=True)
    table.add_column("Text", overflow="fold")
    for m in messages:
        when = _fmt_ts(m.get("ts", ""))
        who = m.get("user") or m.get("bot_id") or "?"
        text = (m.get("text") or "").replace("\n", " ⏎ ")
        table.add_row(when, who, text)
    _console.print()
    _console.print(table)
    _console.print()


@app.command("search")
def cmd_search(
    query: str = typer.Argument(..., help="Search query (Slack search syntax supported)"),
    n: int = typer.Option(20, "-n", "--limit", help="Number of results"),
    json_out: bool = typer.Option(False, "--json"),
):
    """Search across messages. Requires a user token (xoxp-)."""
    client = _client()
    resp = client.search_messages(query=query, count=n)
    matches = resp.get("messages", {}).get("matches", [])

    if json_out:
        typer.echo(json.dumps([
            {"ts": m.get("ts"), "user": m.get("user"), "text": m.get("text"),
             "channel": m.get("channel", {}).get("name")}
            for m in matches
        ]))
        return

    if not matches:
        _console.print("[dim]No matches.[/dim]")
        return
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("When", style="dim", no_wrap=True)
    table.add_column("Channel", style="bold", no_wrap=True)
    table.add_column("Who", style="bold", no_wrap=True)
    table.add_column("Text", overflow="fold")
    for m in matches:
        when = _fmt_ts(m.get("ts", ""))
        ch = "#" + m.get("channel", {}).get("name", "?")
        who = m.get("username") or m.get("user") or "?"
        text = (m.get("text") or "").replace("\n", " ⏎ ")
        table.add_row(when, ch, who, text)
    _console.print()
    _console.print(table)
    _console.print()


# ─── content write verbs ─────────────────────────────────────────────────────


@app.command("send")
def cmd_send(
    channel: str = typer.Argument(..., help="Channel ID or name (with or without #)"),
    text: str = typer.Argument(..., help="Message text"),
    thread_ts: str = typer.Option(None, "--thread-ts", help="Reply in this thread"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be sent without sending"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON response"),
):
    """Send a message to a channel."""
    if dry_run:
        _console.print(f"[dim]would send to[/dim] [bold]{channel}[/bold]")
        if thread_ts:
            _console.print(f"[dim]in thread[/dim] {thread_ts}")
        _console.print(f"[cyan]{text}[/cyan]")
        return

    client = _client()
    channel_id = _resolve_channel(channel)
    kwargs = {"channel": channel_id, "text": text}
    if thread_ts:
        kwargs["thread_ts"] = thread_ts
    resp = client.chat_postMessage(**kwargs)

    if json_out:
        typer.echo(json.dumps({"ts": resp["ts"], "channel": resp["channel"]}))
        return
    _console.print(f"[green]✓ sent[/green]  ts=[dim]{resp['ts']}[/dim]  channel=[dim]{resp['channel']}[/dim]")


# message subgroup --------------------------------------------------------------

message_app = typer.Typer(name="message", help="Edit or delete messages.", no_args_is_help=True)
app.add_typer(message_app, name="message")


@message_app.command("edit")
def cmd_message_edit(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    ts: str = typer.Argument(..., help="Message timestamp"),
    text: str = typer.Argument(..., help="New message text"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Edit your own message."""
    if dry_run:
        _console.print(f"[dim]would edit[/dim] {channel}@{ts}")
        _console.print(f"[cyan]{text}[/cyan]")
        return
    client = _client()
    channel_id = _resolve_channel(channel)
    client.chat_update(channel=channel_id, ts=ts, text=text)
    _console.print(f"[green]✓ edited[/green] {channel}@{ts}")


@message_app.command("delete")
def cmd_message_delete(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    ts: str = typer.Argument(..., help="Message timestamp"),
    yes: bool = typer.Option(False, "--yes", help="Confirm irreversible deletion"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Delete a message. Irreversible."""
    if dry_run:
        _console.print(f"[dim]would delete[/dim] {channel}@{ts}")
        return
    _require_yes(yes, "message delete", f"{channel}@{ts}")
    client = _client()
    channel_id = _resolve_channel(channel)
    client.chat_delete(channel=channel_id, ts=ts)
    _console.print(f"[green]✓ deleted[/green] {channel}@{ts}")


@app.command("react")
def cmd_react(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    ts: str = typer.Argument(..., help="Message timestamp"),
    emoji: str = typer.Argument(..., help="Emoji name (no colons)"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Add a reaction to a message."""
    if dry_run:
        _console.print(f"[dim]would react[/dim] [bold]{emoji.strip(':')}[/bold] to {channel} ts={ts}")
        return
    client = _client()
    channel_id = _resolve_channel(channel)
    client.reactions_add(channel=channel_id, timestamp=ts, name=emoji.strip(":"))
    _console.print(f"[green]✓ reacted[/green] :{emoji.strip(':')}:")


@app.command("pin")
def cmd_pin(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    ts: str = typer.Argument(..., help="Message timestamp"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Pin a message."""
    if dry_run:
        _console.print(f"[dim]would pin[/dim] {channel}@{ts}")
        return
    client = _client()
    channel_id = _resolve_channel(channel)
    client.pins_add(channel=channel_id, timestamp=ts)
    _console.print(f"[green]✓ pinned[/green] {channel}@{ts}")


@app.command("unpin")
def cmd_unpin(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    ts: str = typer.Argument(..., help="Message timestamp"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Unpin a message."""
    if dry_run:
        _console.print(f"[dim]would unpin[/dim] {channel}@{ts}")
        return
    client = _client()
    channel_id = _resolve_channel(channel)
    client.pins_remove(channel=channel_id, timestamp=ts)
    _console.print(f"[green]✓ unpinned[/green] {channel}@{ts}")


# bookmark subgroup -------------------------------------------------------------

bookmark_app = typer.Typer(name="bookmark", help="Channel bookmarks.", no_args_is_help=True)
app.add_typer(bookmark_app, name="bookmark")


@bookmark_app.command("add")
def cmd_bookmark_add(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    title: str = typer.Argument(..., help="Bookmark title"),
    url: str = typer.Argument(..., help="URL to bookmark"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Add a bookmark to a channel."""
    if dry_run:
        _console.print(f"[dim]would bookmark[/dim] {channel}: [bold]{title}[/bold] → {url}")
        return
    client = _client()
    channel_id = _resolve_channel(channel)
    resp = client.bookmarks_add(channel_id=channel_id, title=title, type="link", link=url)
    bm_id = resp.get("bookmark", {}).get("id", "?")
    _console.print(f"[green]✓ bookmarked[/green] id=[dim]{bm_id}[/dim]")


@bookmark_app.command("remove")
def cmd_bookmark_remove(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    bookmark_id: str = typer.Argument(..., help="Bookmark ID"),
    yes: bool = typer.Option(False, "--yes"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Remove a bookmark."""
    if dry_run:
        _console.print(f"[dim]would remove bookmark[/dim] {bookmark_id} from {channel}")
        return
    _require_yes(yes, "bookmark remove", f"{channel}#{bookmark_id}")
    client = _client()
    channel_id = _resolve_channel(channel)
    client.bookmarks_remove(channel_id=channel_id, bookmark_id=bookmark_id)
    _console.print(f"[green]✓ removed[/green] {bookmark_id}")


@bookmark_app.command("list")
def cmd_bookmark_list(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    json_out: bool = typer.Option(False, "--json"),
):
    """List channel bookmarks."""
    client = _client()
    channel_id = _resolve_channel(channel)
    resp = client.bookmarks_list(channel_id=channel_id)
    bookmarks = resp.get("bookmarks", [])
    if json_out:
        typer.echo(json.dumps(bookmarks, default=str))
        return
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Title", style="bold")
    table.add_column("Link", overflow="fold")
    for b in bookmarks:
        table.add_row(b.get("id", "?"), b.get("title", ""), b.get("link", ""))
    _console.print()
    _console.print(table)
    _console.print()


# dm subgroup -------------------------------------------------------------------

dm_app = typer.Typer(name="dm", help="Direct-message control.", no_args_is_help=True)
app.add_typer(dm_app, name="dm")


@dm_app.command("open")
def cmd_dm_open(
    user: str = typer.Argument(..., help="User ID or @handle"),
    json_out: bool = typer.Option(False, "--json"),
):
    """Open a DM with a user. Returns the DM channel ID."""
    client = _client()
    user_id = _resolve_user(user)
    resp = client.conversations_open(users=user_id)
    channel = resp.get("channel", {})
    if json_out:
        typer.echo(json.dumps({"channel_id": channel.get("id"), "user": user_id}))
        return
    _console.print(f"[green]✓ opened DM[/green] channel=[dim]{channel.get('id')}[/dim] with [bold]{user}[/bold]")


# schedule subgroup -------------------------------------------------------------

schedule_app = typer.Typer(name="schedule", help="Scheduled messages.", no_args_is_help=True)
app.add_typer(schedule_app, name="schedule")


@schedule_app.callback(invoke_without_command=True)
def schedule_root(
    ctx: typer.Context,
    channel: str = typer.Argument(None, help="Channel ID or name (positional, when scheduling a new message)"),
    text: str = typer.Argument(None, help="Message text"),
    at: str = typer.Option(None, "--at", help="ISO 8601 send time (e.g. 2026-05-08T09:00:00-04:00)"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_out: bool = typer.Option(False, "--json"),
):
    """Schedule a message for later (when called with positional args + --at)."""
    if ctx.invoked_subcommand is not None:
        return
    if not (channel and text and at):
        _console.print("[dim]Usage:[/dim] kai slack schedule <channel> \"<text>\" --at <iso>")
        _console.print("[dim]       kai slack schedule list[/dim]")
        _console.print("[dim]       kai slack schedule cancel <channel> <id>[/dim]")
        raise typer.Exit(0)
    try:
        post_at = int(datetime.fromisoformat(at).timestamp())
    except ValueError:
        _console.print(f"[red]Bad --at value[/red]: {at}. Use ISO 8601 (e.g. 2026-05-08T09:00:00-04:00).")
        raise typer.Exit(1)
    if dry_run:
        _console.print(f"[dim]would schedule to[/dim] [bold]{channel}[/bold] at [bold]{at}[/bold]")
        _console.print(f"[cyan]{text}[/cyan]")
        return
    client = _client()
    channel_id = _resolve_channel(channel)
    resp = client.chat_scheduleMessage(channel=channel_id, post_at=post_at, text=text)
    sm_id = resp.get("scheduled_message_id", "?")
    if json_out:
        typer.echo(json.dumps({"scheduled_message_id": sm_id, "channel": channel_id, "post_at": post_at}))
        return
    _console.print(f"[green]✓ scheduled[/green] id=[dim]{sm_id}[/dim] post_at=[dim]{at}[/dim]")


@schedule_app.command("list")
def cmd_schedule_list(json_out: bool = typer.Option(False, "--json")):
    """List your queued scheduled messages."""
    client = _client()
    resp = client.chat_scheduledMessages_list()
    msgs = resp.get("scheduled_messages", [])
    if json_out:
        typer.echo(json.dumps(msgs, default=str))
        return
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Channel", style="bold", no_wrap=True)
    table.add_column("Post at", style="dim", no_wrap=True)
    table.add_column("Text", overflow="fold")
    for m in msgs:
        post_at = m.get("post_at")
        when = datetime.fromtimestamp(int(post_at), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC") if post_at else "?"
        text = (m.get("text") or "").replace("\n", " ⏎ ")
        table.add_row(m.get("id", "?"), m.get("channel_id", "?"), when, text)
    _console.print()
    _console.print(f"[dim]{len(msgs)} scheduled messages[/dim]")
    _console.print(table)
    _console.print()


@schedule_app.command("cancel")
def cmd_schedule_cancel(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    scheduled_id: str = typer.Argument(..., help="Scheduled message ID"),
    yes: bool = typer.Option(False, "--yes"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Cancel a queued scheduled message."""
    if dry_run:
        _console.print(f"[dim]would cancel[/dim] {scheduled_id} in {channel}")
        return
    _require_yes(yes, "schedule cancel", f"{channel}#{scheduled_id}")
    client = _client()
    channel_id = _resolve_channel(channel)
    client.chat_deleteScheduledMessage(channel=channel_id, scheduled_message_id=scheduled_id)
    _console.print(f"[green]✓ cancelled[/green] {scheduled_id}")


# ─── topology + membership verbs ─────────────────────────────────────────────


@app.command("create")
def cmd_create(
    name: str = typer.Argument(..., help="Channel name (no leading #)"),
    private: bool = typer.Option(False, "--private", help="Create as private channel"),
    topic: str = typer.Option(None, "--topic", help="Channel topic (one line)"),
    purpose: str = typer.Option(None, "--purpose", help="Channel purpose (paragraph)"),
    invite: str = typer.Option(None, "--invite", help="Comma-separated users to invite"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_out: bool = typer.Option(False, "--json"),
):
    """Create a channel. One-shot provisioning: create → setTopic → setPurpose → invite."""
    name = name.lstrip("#")
    if dry_run:
        kind = "private" if private else "public"
        _console.print(f"[dim]would create[/dim] [bold]#{name}[/bold] ({kind})")
        if topic:
            _console.print(f"[dim]  topic:[/dim] {topic}")
        if purpose:
            _console.print(f"[dim]  purpose:[/dim] {purpose}")
        if invite:
            _console.print(f"[dim]  invite:[/dim] {invite}")
        return

    client = _client()
    resp = client.conversations_create(name=name, is_private=private)
    channel_id = resp["channel"]["id"]
    actions = [f"created #{name} ({channel_id})"]

    if topic:
        client.conversations_setTopic(channel=channel_id, topic=topic)
        actions.append("topic set")
    if purpose:
        client.conversations_setPurpose(channel=channel_id, purpose=purpose)
        actions.append("purpose set")
    if invite:
        users = ",".join(_resolve_user(u.strip()) for u in invite.split(","))
        client.conversations_invite(channel=channel_id, users=users)
        actions.append(f"invited {len(invite.split(','))}")

    # Bust the channel cache so subsequent name lookups in the same process see the new channel
    _channel_index.cache_clear()

    if json_out:
        typer.echo(json.dumps({"channel_id": channel_id, "name": name, "actions": actions}))
        return
    for a in actions:
        _console.print(f"[green]✓[/green] {a}")


@app.command("archive")
def cmd_archive(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    yes: bool = typer.Option(False, "--yes", help="Confirm — archiving closes the channel"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Archive (close) a channel. Reversible via `unarchive`."""
    if dry_run:
        _console.print(f"[dim]would archive[/dim] [bold]{channel}[/bold]")
        return
    _require_yes(yes, "archive", channel)
    client = _client()
    channel_id = _resolve_channel(channel)
    client.conversations_archive(channel=channel_id)
    _channel_index.cache_clear()
    _console.print(f"[green]✓ archived[/green] {channel}")


@app.command("unarchive")
def cmd_unarchive(
    channel: str = typer.Argument(..., help="Channel ID (archived channels are excluded from the name index)"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Unarchive (reopen) a channel. Pass channel ID, not name."""
    # `_resolve_channel` excludes archived channels from its index, so accept ID only here.
    if not (channel.startswith(("C", "G")) and len(channel) >= 9):
        _console.print(
            f"[red]Pass a channel ID for unarchive[/red] (archived channels are excluded from the name index)."
        )
        raise typer.Exit(1)
    if dry_run:
        _console.print(f"[dim]would unarchive[/dim] [bold]{channel}[/bold]")
        return
    client = _client()
    client.conversations_unarchive(channel=channel)
    _channel_index.cache_clear()
    _console.print(f"[green]✓ unarchived[/green] {channel}")


@app.command("rename")
def cmd_rename(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    new: str = typer.Argument(..., help="New channel name (no leading #)"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Rename a channel."""
    new_name = new.lstrip("#")
    if dry_run:
        _console.print(f"[dim]would rename[/dim] {channel} → [bold]#{new_name}[/bold]")
        return
    client = _client()
    channel_id = _resolve_channel(channel)
    client.conversations_rename(channel=channel_id, name=new_name)
    _channel_index.cache_clear()
    _console.print(f"[green]✓ renamed[/green] → #{new_name}")


@app.command("topic")
def cmd_topic(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    text: str = typer.Argument(..., help="Topic text (one line)"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Set the channel's one-line topic."""
    if dry_run:
        _console.print(f"[dim]would set topic of[/dim] {channel} [dim]to:[/dim] [cyan]{text}[/cyan]")
        return
    client = _client()
    channel_id = _resolve_channel(channel)
    client.conversations_setTopic(channel=channel_id, topic=text)
    _console.print(f"[green]✓ topic set[/green]")


@app.command("purpose")
def cmd_purpose(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    text: str = typer.Argument(..., help="Purpose text (paragraph)"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Set the channel's longer purpose statement."""
    if dry_run:
        _console.print(f"[dim]would set purpose of[/dim] {channel} [dim]to:[/dim] [cyan]{text}[/cyan]")
        return
    client = _client()
    channel_id = _resolve_channel(channel)
    client.conversations_setPurpose(channel=channel_id, purpose=text)
    _console.print(f"[green]✓ purpose set[/green]")


@app.command("invite")
def cmd_invite(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    users: list[str] = typer.Argument(..., help="One or more user IDs or @handles"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Invite one or more users to a channel."""
    if dry_run:
        _console.print(f"[dim]would invite[/dim] {', '.join(users)} [dim]to[/dim] [bold]{channel}[/bold]")
        return
    client = _client()
    channel_id = _resolve_channel(channel)
    user_ids = ",".join(_resolve_user(u) for u in users)
    client.conversations_invite(channel=channel_id, users=user_ids)
    _console.print(f"[green]✓ invited[/green] {len(users)} user(s)")


@app.command("kick")
def cmd_kick(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    user: str = typer.Argument(..., help="User ID or @handle"),
    yes: bool = typer.Option(False, "--yes"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Remove a user from a channel."""
    if dry_run:
        _console.print(f"[dim]would kick[/dim] {user} [dim]from[/dim] [bold]{channel}[/bold]")
        return
    _require_yes(yes, "kick", f"{user} from {channel}")
    client = _client()
    channel_id = _resolve_channel(channel)
    user_id = _resolve_user(user)
    client.conversations_kick(channel=channel_id, user=user_id)
    _console.print(f"[green]✓ kicked[/green] {user}")


@app.command("convert-to-private")
def cmd_convert_to_private(
    channel: str = typer.Argument(..., help="Channel ID or name"),
    yes: bool = typer.Option(False, "--yes"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Convert a public channel to private. ONE-WAY — Slack does not allow undo."""
    if dry_run:
        _console.print(f"[dim]would convert[/dim] [bold]{channel}[/bold] [dim]to private (irreversible)[/dim]")
        return
    _require_yes(yes, "convert-to-private", channel)
    client = _client()
    channel_id = _resolve_channel(channel)
    client.conversations_convertToPrivate(channel=channel_id)
    _channel_index.cache_clear()
    _console.print(f"[green]✓ converted to private[/green] {channel}  [yellow](no API to undo)[/yellow]")


# ─── usergroup subgroup ──────────────────────────────────────────────────────


usergroup_app = typer.Typer(name="usergroup", help="User group (e.g. @gifty-team) admin.", no_args_is_help=True)
app.add_typer(usergroup_app, name="usergroup")


@usergroup_app.command("create")
def cmd_usergroup_create(
    handle: str = typer.Argument(..., help="Handle (no leading @)"),
    name: str = typer.Option(..., "--name", help="Display name for the group"),
    users: str = typer.Option(None, "--users", help="Comma-separated initial members"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Create a user group."""
    handle = handle.lstrip("@")
    if dry_run:
        _console.print(f"[dim]would create usergroup[/dim] [bold]@{handle}[/bold] ([dim]{name}[/dim])")
        if users:
            _console.print(f"[dim]  with members:[/dim] {users}")
        return
    client = _client()
    resp = client.usergroups_create(name=name, handle=handle)
    ug_id = resp.get("usergroup", {}).get("id", "?")
    if users:
        user_ids = ",".join(_resolve_user(u.strip()) for u in users.split(","))
        client.usergroups_users_update(usergroup=ug_id, users=user_ids)
    _console.print(f"[green]✓ created[/green] @{handle} id=[dim]{ug_id}[/dim]")


def _usergroup_id(handle_or_id: str) -> str:
    if handle_or_id.startswith("S") and len(handle_or_id) >= 9:
        return handle_or_id
    handle = handle_or_id.lstrip("@")
    client = _client()
    resp = client.usergroups_list(include_users=False)
    for g in resp.get("usergroups", []):
        if g.get("handle") == handle:
            return g["id"]
    _console.print(f"[red]No user group with handle '{handle}'.[/red]")
    raise typer.Exit(1)


@usergroup_app.command("add")
def cmd_usergroup_add(
    handle: str = typer.Argument(..., help="Group handle or ID"),
    users: list[str] = typer.Argument(..., help="Users to add"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Add members to a user group."""
    if dry_run:
        _console.print(f"[dim]would add[/dim] {', '.join(users)} [dim]to[/dim] [bold]@{handle.lstrip('@')}[/bold]")
        return
    client = _client()
    ug_id = _usergroup_id(handle)
    current = client.usergroups_users_list(usergroup=ug_id).get("users", [])
    new_ids = [_resolve_user(u) for u in users]
    merged = list(dict.fromkeys(current + new_ids))
    client.usergroups_users_update(usergroup=ug_id, users=",".join(merged))
    _console.print(f"[green]✓ added[/green] {len(new_ids)} member(s) (now {len(merged)} total)")


@usergroup_app.command("remove")
def cmd_usergroup_remove(
    handle: str = typer.Argument(..., help="Group handle or ID"),
    users: list[str] = typer.Argument(..., help="Users to remove"),
    yes: bool = typer.Option(False, "--yes"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Remove members from a user group."""
    if dry_run:
        _console.print(f"[dim]would remove[/dim] {', '.join(users)} [dim]from[/dim] [bold]@{handle.lstrip('@')}[/bold]")
        return
    _require_yes(yes, "usergroup remove", f"@{handle.lstrip('@')}")
    client = _client()
    ug_id = _usergroup_id(handle)
    current = client.usergroups_users_list(usergroup=ug_id).get("users", [])
    remove_ids = {_resolve_user(u) for u in users}
    merged = [u for u in current if u not in remove_ids]
    client.usergroups_users_update(usergroup=ug_id, users=",".join(merged))
    _console.print(f"[green]✓ removed[/green] {len(remove_ids)} member(s) (now {len(merged)} total)")


@usergroup_app.command("list")
def cmd_usergroup_list(
    json_out: bool = typer.Option(False, "--json"),
):
    """List user groups."""
    client = _client()
    resp = client.usergroups_list()
    groups = resp.get("usergroups", [])
    if json_out:
        typer.echo(json.dumps(groups, default=str))
        return
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Handle", style="bold", no_wrap=True)
    table.add_column("Name", overflow="fold")
    table.add_column("Members", style="dim", justify="right")
    for g in groups:
        table.add_row(
            g.get("id", "?"),
            "@" + g.get("handle", "?"),
            g.get("name", ""),
            str(g.get("user_count", "?")),
        )
    _console.print()
    _console.print(table)
    _console.print()


# ─── file subgroup ───────────────────────────────────────────────────────────


file_app = typer.Typer(name="file", help="File admin.", no_args_is_help=True)
app.add_typer(file_app, name="file")


@file_app.command("delete")
def cmd_file_delete(
    file_id: str = typer.Argument(..., help="File ID (F...)"),
    yes: bool = typer.Option(False, "--yes"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Delete a file. Irreversible."""
    if dry_run:
        _console.print(f"[dim]would delete file[/dim] {file_id}")
        return
    _require_yes(yes, "file delete", file_id)
    client = _client()
    client.files_delete(file=file_id)
    _console.print(f"[green]✓ deleted[/green] {file_id}")


@file_app.command("upload")
def cmd_file_upload(
    channel: str = typer.Argument(..., help="Channel ID or name (with or without #)"),
    path: Path = typer.Argument(..., help="Local file path to upload"),
    title: str | None = typer.Option(None, "--title", help="Slack file title"),
    initial_comment: str | None = typer.Option(None, "--initial-comment", help="Message text to post with the file"),
    thread_ts: str | None = typer.Option(None, "--thread-ts", help="Reply in this thread"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be uploaded without sending"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON response"),
):
    """Upload a local file to a channel using Slack's current file-upload flow."""
    target = path.expanduser()
    if not target.exists() or not target.is_file():
        _console.print(f"[red]File not found:[/red] {target}")
        raise typer.Exit(1)

    channel_id = channel if channel.startswith(("C", "D", "G")) and len(channel) >= 9 else channel.lstrip("#")
    file_title = title or target.name
    if dry_run:
        _console.print(f"[dim]would upload[/dim] {target}")
        _console.print(f"[dim]to channel[/dim] [bold]{channel}[/bold]")
        _console.print(f"[dim]title[/dim] {file_title}")
        if thread_ts:
            _console.print(f"[dim]in thread[/dim] {thread_ts}")
        if initial_comment:
            _console.print(f"[cyan]{initial_comment}[/cyan]")
        return

    client = _client()
    channel_id = _resolve_channel(channel)
    kwargs = {
        "channel": channel_id,
        "file": str(target),
        "title": file_title,
    }
    if initial_comment:
        kwargs["initial_comment"] = initial_comment
    if thread_ts:
        kwargs["thread_ts"] = thread_ts
    resp = client.files_upload_v2(**kwargs)

    file_obj = resp.get("file") or {}
    if json_out:
        typer.echo(json.dumps({
            "channel": channel_id,
            "file_id": file_obj.get("id"),
            "permalink": file_obj.get("permalink"),
        }))
        return
    link = file_obj.get("permalink") or "(no permalink returned)"
    _console.print(f"[green]✓ uploaded[/green]  file=[dim]{file_obj.get('id', '?')}[/dim]  {link}")


# ─── slack-cli wrapping (manifest + doctor) ──────────────────────────────────
#
# These verbs wrap the official slack-cli (`slack`). We do this because
# slack-cli is project-context-bound (needs slack.json + a linked app) which
# is awkward for kai's classic-OAuth use case. kai keeps a minimal slack-cli
# project in `.slack-config/` inside the kai repo and dispatches all
# scope/manifest operations from there. Users get one command per intent;
# slack-cli's project model is invisible.


import shutil as _shutil
import subprocess as _subprocess
from pathlib import Path as _Path


def _kai_repo_root() -> _Path:
    """Locate kai's repo root by walking up from this file."""
    here = _Path(__file__).resolve()
    # src/kai/commands/slack.py → repo root is parents[3]
    return here.parents[3]


def _slack_config_dir() -> _Path:
    """The slack-cli project scaffold lives in <kai-repo>/.slack-config/."""
    return _kai_repo_root() / ".slack-config"


def _slack_cli_available() -> bool:
    return _shutil.which("slack") is not None


def _run_slack_cli(args: list[str], *, capture: bool = False) -> _subprocess.CompletedProcess:
    """Run slack-cli inside the kai .slack-config project context."""
    if not _slack_cli_available():
        _console.print("[red]slack CLI not on PATH.[/red] Install from https://docs.slack.dev/tools/slack-cli")
        raise typer.Exit(1)
    cfg = _slack_config_dir()
    if not cfg.exists():
        _console.print(
            f"[red]No slack-cli scaffold at {cfg}.[/red] "
            "Run [bold]kai slack manifest init[/bold] first."
        )
        raise typer.Exit(1)
    return _subprocess.run(
        ["slack", *args],
        cwd=cfg,
        capture_output=capture,
        text=True,
    )


# manifest subgroup -------------------------------------------------------------

manifest_app = typer.Typer(
    name="manifest",
    help="Manage the kai Slack app's manifest (scopes, display, settings) via slack-cli.",
    no_args_is_help=True,
)
app.add_typer(manifest_app, name="manifest")


@manifest_app.command("init")
def cmd_manifest_init(
    force: bool = typer.Option(False, "--force", help="Overwrite an existing scaffold"),
):
    """Create the slack-cli project scaffold at .slack-config/ if absent."""
    cfg = _slack_config_dir()
    if cfg.exists() and not force:
        _console.print(f"[yellow]Already exists:[/yellow] {cfg}")
        _console.print("[dim]Pass --force to overwrite.[/dim]")
        return
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "slack.json").write_text(
        '{\n'
        '  "hooks": {\n'
        '    "get-manifest": "bash -c \'cat manifest.json\'"\n'
        '  }\n'
        '}\n'
    )
    if not (cfg / "manifest.json").exists():
        # Default kai manifest — full scopes from SLACK.md
        (cfg / "manifest.json").write_text("""\
{
  "display_information": {
    "name": "kai",
    "description": "Founder multitool for Eidos AGI. The conjunction that joins.",
    "background_color": "#161210"
  },
  "features": {
    "bot_user": {
      "display_name": "kai",
      "always_online": false
    }
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "bookmarks:read", "bookmarks:write",
        "channels:history", "channels:manage", "channels:read",
        "chat:write", "chat:write.public",
        "files:write",
        "groups:history", "groups:read", "groups:write",
        "im:history", "im:read", "im:write",
        "mpim:history", "mpim:read",
        "pins:read", "pins:write",
        "reactions:write",
        "usergroups:read", "usergroups:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "org_deploy_enabled": false,
    "socket_mode_enabled": false,
    "token_rotation_enabled": false
  }
}
""")
    _console.print(f"[green]✓ scaffolded[/green] {cfg}/")
    _console.print("[dim]Edit manifest.json to change scopes; then `kai slack manifest push` to apply.[/dim]")


@manifest_app.command("validate")
def cmd_manifest_validate():
    """Validate the local manifest.json (slack-cli schema check)."""
    r = _run_slack_cli(["manifest", "validate"], capture=True)
    if r.returncode == 0:
        _console.print("[green]✓ manifest valid[/green]")
        return
    _console.print(f"[red]✗ invalid manifest[/red]\n{r.stderr or r.stdout}")
    raise typer.Exit(1)


@manifest_app.command("info")
def cmd_manifest_info(
    source: str = typer.Option("project", "--source", help="'project' (local file) or 'remote' (live on Slack)"),
):
    """Show the current manifest — local file or live remote (after install)."""
    if source not in ("project", "remote"):
        _console.print(f"[red]--source must be 'project' or 'remote'[/red] (got {source!r})")
        raise typer.Exit(1)
    r = _run_slack_cli(["manifest", "info", "--source", source], capture=True)
    if r.returncode != 0:
        _console.print(f"[red]{r.stderr or r.stdout}[/red]")
        raise typer.Exit(1)
    _console.print(r.stdout)


@manifest_app.command("push")
def cmd_manifest_push(
    yes: bool = typer.Option(False, "--yes", help="Confirm — re-install applies new scopes"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Apply the local manifest to the linked kai app (validate → install).

    Effect: slack-cli re-installs the app with current local manifest.json.
    The bot token does NOT change; new scopes take effect on next API call.
    """
    cfg = _slack_config_dir()
    if dry_run:
        _console.print(f"[dim]would push manifest from[/dim] {cfg}/manifest.json")
        _console.print("[dim]would run:[/dim] slack manifest validate && slack app install --team eidosagi")
        return
    _require_yes(yes, "manifest push", "the kai Slack app")
    # Validate first
    v = _run_slack_cli(["manifest", "validate"], capture=True)
    if v.returncode != 0:
        _console.print(f"[red]manifest validation failed:[/red]\n{v.stderr or v.stdout}")
        raise typer.Exit(1)
    _console.print("[green]✓ manifest valid[/green] — installing…")
    # Apply
    i = _run_slack_cli(["app", "install", "--team", "eidosagi"], capture=True)
    if i.returncode != 0:
        _console.print(f"[red]install failed:[/red]\n{i.stderr or i.stdout}")
        raise typer.Exit(1)
    _console.print("[green]✓ kai app re-installed with current manifest.[/green]")
    _console.print("[yellow]Reminder:[/yellow] bot token unchanged, but new scopes are live.")


@manifest_app.command("pull")
def cmd_manifest_pull():
    """Read the live manifest from Slack and overwrite the local manifest.json."""
    cfg = _slack_config_dir()
    r = _run_slack_cli(["manifest", "info", "--source", "remote"], capture=True)
    if r.returncode != 0:
        _console.print(f"[red]could not read remote manifest:[/red]\n{r.stderr or r.stdout}")
        raise typer.Exit(1)
    target = cfg / "manifest.json"
    target.write_text(r.stdout)
    _console.print(f"[green]✓ pulled remote manifest[/green] → {target}")


# doctor ------------------------------------------------------------------------


@app.command("doctor")
def cmd_doctor():
    """End-to-end health check: slack-cli auth, kai-app install, scopes, vault, token validity."""
    import os as _os
    rows: list[tuple[str, str, str]] = []

    def row(check: str, status: str, note: str = ""):
        rows.append((check, status, note))

    # 1. slack CLI present
    if _slack_cli_available():
        row("slack CLI on PATH", "✓", _shutil.which("slack") or "")
    else:
        row("slack CLI on PATH", "✗", "install from https://docs.slack.dev/tools/slack-cli")

    # 2. slack-cli authed to a workspace
    if _slack_cli_available():
        r = _subprocess.run(["slack", "auth", "list"], capture_output=True, text=True)
        if r.returncode == 0 and "eidosagi" in r.stdout.lower():
            row("slack-cli authed", "✓", "eidosagi workspace")
        elif r.returncode == 0 and "not logged in" in r.stdout.lower():
            row("slack-cli authed", "✗", "run `slack login` (see SLACK.md)")
        else:
            row("slack-cli authed", "?", r.stdout.strip().split("\n")[0] if r.stdout else "unknown")

    # 3. .slack-config scaffold present
    cfg = _slack_config_dir()
    if (cfg / "slack.json").exists() and (cfg / "manifest.json").exists():
        row(".slack-config scaffold", "✓", str(cfg))
    else:
        row(".slack-config scaffold", "✗", "run `kai slack manifest init`")

    # 4. kai app linked + installed
    apps_json = cfg / ".slack" / "apps.json"
    if apps_json.exists():
        try:
            import json as _json
            d = _json.loads(apps_json.read_text())
            apps = d.get("apps", {})
            if apps:
                first = next(iter(apps.values()))
                row("kai app linked", "✓", f"app_id={first.get('app_id')} team={first.get('team_domain')}")
            else:
                row("kai app linked", "✗", "run `slack app link --team eidosagi --app <APP_ID>`")
        except Exception as e:  # noqa: BLE001
            row("kai app linked", "?", f"could not parse apps.json: {e}")
    else:
        row("kai app linked", "✗", "run `slack app link` from .slack-config/")

    # 5. token in Eidos Vault
    token_in_vault = False
    token_value: str | None = None
    if _shutil.which("eidos"):
        r = _subprocess.run(
            ["eidos", "vault", "get", "slack/eidos/kai-token"],
            capture_output=True, text=True,
        )
        if r.returncode == 0 and r.stdout.strip().startswith(("xoxb-", "xoxp-")):
            token_in_vault = True
            token_value = r.stdout.strip()
            row("token in Eidos Vault", "✓", f"slack/eidos/kai-token (prefix={token_value[:7]})")
        else:
            row("token in Eidos Vault", "✗", "run `kai login slack`")
    else:
        row("token in Eidos Vault", "?", "eidos CLI not on PATH — skipped")

    # 6. token actually works (auth.test)
    if token_value:
        try:
            from slack_sdk import WebClient
            client = WebClient(token=token_value)
            auth = client.auth_test()
            row("token validates", "✓", f"team={auth.get('team')} user={auth.get('user')}")
        except Exception as e:  # noqa: BLE001
            row("token validates", "✗", f"auth.test failed: {e}")
    elif token_in_vault is False:
        row("token validates", "—", "no token to validate yet")

    # 7. KAI_SLACK_TOKEN env var (optional convenience)
    env_token = _os.environ.get(TOKEN_ENV)
    if env_token:
        prefix = env_token[:7]
        row(f"${TOKEN_ENV}", "✓", f"set (prefix={prefix})")
    else:
        row(f"${TOKEN_ENV}", "—", "not set; load with `export KAI_SLACK_TOKEN=$(eidos vault get slack/eidos/kai-token)`")

    # Render
    _console.print()
    _console.print("[bold]kai slack doctor[/bold] — end-to-end health")
    _console.print()
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("Check", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Note", style="dim", overflow="fold")
    for check, status, note in rows:
        if status == "✓":
            status_str = "[green]✓[/green]"
        elif status == "✗":
            status_str = "[red]✗[/red]"
        elif status == "—":
            status_str = "[dim]—[/dim]"
        else:
            status_str = f"[yellow]{status}[/yellow]"
        table.add_row(check, status_str, note)
    _console.print(table)
    _console.print()

    # Exit non-zero if any check failed
    if any(s == "✗" for _, s, _ in rows):
        raise typer.Exit(1)
