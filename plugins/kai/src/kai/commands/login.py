"""kai login — bootstrap a secret for any registered platform.

Service-agnostic entry to `kai.lib.secrets.acquire_secret`. Each platform
defines its SecretService once in `kai.lib.secrets` (dashboard URL,
instructions, validator, default vault path, env var). `kai login <name>`
then opens the dashboard, pops a paste window, validates, saves to
**Eidos Vault** (`eidos vault`), and optionally to an env file.

Same flow as `kai slack login` (which is just an alias). The point of
this command is forward-extensibility: when GitHub / Linear / Notion
SecretServices are registered, `kai login github` just works without
needing each platform module to grow its own login command.

Storage: kai uses Eidos Vault. Knox is Daniel's personal secrets agent
and is out of scope.

NOT in v0:
  - Multi-service in one invocation. Run once per platform.
  - Token rotation flows. `kai login <name>` is the way; it overwrites.
  - OAuth installation handshakes. Paste-the-token only.
"""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from kai.lib import secrets


_console = Console()


def login_cmd(
    service: str = typer.Argument(None, help="Service name from the registry (e.g. 'slack'). Omit to list."),
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't open the dashboard"),
    no_popup: bool = typer.Option(False, "--no-popup", help="Skip the GUI; use the terminal flow"),
):
    """Bootstrap a secret for a platform: dashboard → popup → validate → Vault save."""
    if not service:
        _list_services()
        return

    try:
        svc = secrets.get_service(service)
    except KeyError as e:
        _console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    result = secrets.acquire_secret(
        svc,
        no_browser=no_browser,
        no_popup=no_popup,
        print_fn=lambda msg: _console.print(f"[yellow]{msg}[/yellow]"),
    )
    if result.cancelled:
        _console.print("[yellow]Cancelled — no secret written.[/yellow]")
        raise typer.Exit(1)
    if not result.success:
        raise typer.Exit(1)

    identity = dict(result.identity)
    primary = identity.get("user") or identity.get("login") or "?"
    workspace = identity.get("team") or identity.get("org") or identity.get("workspace") or "?"
    _console.print()
    _console.print(
        f"[green]✓ {svc.display_name} login complete[/green] — "
        f"[bold]{primary}[/bold] @ [bold]{workspace}[/bold]"
    )
    for a in result.actions:
        _console.print(f"  [green]✓[/green] {a}")
    _console.print()


def _list_services() -> None:
    _console.print()
    _console.print("[bold]kai login[/bold] — registered platforms")
    _console.print()
    table = Table(show_header=True, header_style="bold cyan", box=None, pad_edge=False)
    table.add_column("Service", style="bold")
    table.add_column("Dashboard")
    table.add_column("Vault path", style="dim")
    table.add_column("Env var", style="dim")
    for name, svc in sorted(secrets.REGISTRY.items()):
        table.add_row(name, svc.dashboard_url, svc.default_vault_path, svc.env_var_name)
    _console.print(table)
    _console.print()
    _console.print("[dim]Use:[/dim] [cyan]kai login <service>[/cyan]")
    _console.print()
