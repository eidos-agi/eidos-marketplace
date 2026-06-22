"""kai deploy — Railway deploys via railguey.

Storage: none — pure dispatcher to railguey.

NOT in v0:
  - Multi-account routing. railguey already handles this; kai just dispatches.
  - Confirmation prompts. railguey owns its own UX.
  - --dry-run wrapping. Pass through to railguey's native --dry-run when supported.
"""

import shutil
import subprocess

import typer
from rich.console import Console

app = typer.Typer(
    name="deploy",
    invoke_without_command=True,
    no_args_is_help=False,
    add_completion=False,
    help="Railway deploys (railguey).",
)
console = Console()


@app.callback()
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        _show_commands()


def _show_commands() -> None:
    console.print()
    console.print("[bold]kai deploy[/bold] — Railway deploys via railguey")
    console.print()
    console.print("Commands:")
    console.print("  [bold]status[/bold]    Show Railway project status")
    console.print("  [bold]logs[/bold]      Tail service logs")
    console.print("  [bold]list[/bold]      List Railway services")
    console.print()
    console.print("[dim]All commands shell out to `railguey`.[/dim]")
    console.print()


@app.command("status")
def status() -> None:
    """Show Railway project status."""
    _shell(["railguey", "status"])


@app.command("logs")
def logs(service: str = typer.Argument(..., help="Service name")) -> None:
    """Tail service logs."""
    _shell(["railguey", "logs", service])


@app.command("list")
def list_services() -> None:
    """List Railway services."""
    _shell(["railguey", "services"])


def _shell(cmd: list[str]) -> None:
    if shutil.which(cmd[0]) is None:
        console.print(f"[red]Command not found:[/red] [bold]{cmd[0]}[/bold]")
        console.print(f"[dim]kai dispatches to {cmd[0]}; install it first.[/dim]")
        raise typer.Exit(1)
    subprocess.run(cmd, check=False)
