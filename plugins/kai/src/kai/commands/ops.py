"""kai ops — process guardrails for founder operations.

These are not platform implementations. They are compact runbooks for the
moments where kai should stop browser thrash and route the operator toward the
right deterministic tool.
"""
from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


app = typer.Typer(
    name="ops",
    help="Founder-ops guardrails — route risky workflows to the right CLI.",
    invoke_without_command=True,
    no_args_is_help=False,
    add_completion=False,
)

_console = Console()


def _local_image_dimensions(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")

    if not data.startswith(b"\xff\xd8"):
        return None

    index = 2
    sof_markers = {
        0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
        0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
    }
    while index + 3 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        while index < len(data) and data[index] == 0xFF:
            index += 1
        if index >= len(data):
            return None
        marker = data[index]
        index += 1
        if marker in (0xD8, 0xD9):
            continue
        if index + 2 > len(data):
            return None
        segment_length = int.from_bytes(data[index:index + 2], "big")
        if segment_length < 2 or index + segment_length > len(data):
            return None
        if marker in sof_markers and segment_length >= 7:
            height = int.from_bytes(data[index + 3:index + 5], "big")
            width = int.from_bytes(data[index + 5:index + 7], "big")
            return width, height
        index += segment_length
    return None


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        guardrails()


@app.command("guardrails")
def guardrails() -> None:
    """Show the API-first guardrail for credentials and platform provisioning."""
    _console.print()
    _console.print("[bold]kai ops guardrails[/bold]")
    _console.print("[dim]When a platform has an API, do not start with the admin UI.[/dim]")
    _console.print()

    table = Table(show_header=True, header_style="bold cyan", box=None, pad_edge=False)
    table.add_column("Situation", style="bold")
    table.add_column("Correct path")
    table.add_column("Do not")
    table.add_row(
        "Create mailbox / platform identity",
        "Use the provider API through the owning CLI, then store generated credentials with `eidos vault set --stdin`.",
        "Drive Chrome/admin pages as the first plan.",
    )
    table.add_row(
        "Secret is not in Eidos Vault",
        "Check both current `reeves vault` and legacy Reeves Vault/RheaOS metadata before declaring it missing; then promote/rotate the operational secret into Eidos Vault.",
        "Assume one empty vault surface means the personal Keeper mirror has no record.",
    )
    table.add_row(
        "Generated password or token",
        "Keep it in memory/stdin, save once to Eidos Vault, and verify by reading only path/status.",
        "Echo it, pass it as a command argument, or leave it in scrollback.",
    )
    table.add_row(
        "CLI ownership unclear",
        "Run `eidos --help` first; kai is the founder-ops router, eidos owns vault/mail/public platform surfaces.",
        "Add `kai mail` or duplicate Eidos Vault behavior in kai.",
    )
    _console.print(table)
    _console.print()
    _console.print("[bold]Mailbox pattern[/bold]")
    _console.print("  1. Find the owning API credential in Eidos Vault.")
    _console.print("  2. If missing, check current `reeves vault` and legacy Reeves Vault/RheaOS metadata.")
    _console.print("  3. If the secret is only in Reeves/Knox/Keeper, stop and promote or rotate it into Eidos Vault.")
    _console.print("  4. Generate the mailbox password locally without printing it.")
    _console.print("  5. Create the mailbox through the provider API.")
    _console.print("  6. Save the mailbox password with `eidos vault set mail/<address>/password --stdin`.")
    _console.print("  7. Verify mailbox existence and vault path, not the secret value.")
    _console.print()


@app.command("employee-photo")
def employee_photo(
    email: str = typer.Argument(..., help="Employee primary company email."),
    name: str = typer.Option("", "--name", help="Employee display name."),
    slack_user_id: str = typer.Option("", "--slack-user-id", help="Slack user ID, if already resolved."),
    photo_source: str = typer.Option("", "--photo-source", help="Approved headshot path or Drive URL."),
    json_output: bool = typer.Option(False, "--json", help="Print the checklist as JSON."),
) -> None:
    """Show the approval-gated Slack + Google Workspace photo procedure."""
    subject = name or email
    missing: list[str] = []
    dimensions: tuple[int, int] | None = None
    if not photo_source:
        missing.append("approved headshot file or canonical Drive URL")
    elif not photo_source.startswith(("http://", "https://")):
        path = Path(photo_source).expanduser()
        if not path.exists():
            missing.append("photo source path exists locally or is a canonical Drive URL")
        else:
            dimensions = _local_image_dimensions(path)
            if dimensions is None:
                missing.append("readable PNG/JPEG photo source")
            elif dimensions[0] < 512 or dimensions[1] < 512:
                missing.append("Slack-compatible headshot at least 512x512")
    if not slack_user_id:
        missing.append("Slack user ID resolved from company email")

    payload = {
        "procedure": "employee-profile-photo",
        "employee": {
            "name": name,
            "email": email,
            "slack_user_id": slack_user_id,
            "photo_source": photo_source,
            "photo_dimensions": dimensions,
        },
        "status": "blocked" if missing else "ready-for-admin-update",
        "missing": missing,
        "hard_stops": [
            "Do not invent, scrape, or generate an employee likeness.",
            "Do not use non-Kai Slack tokens or a different workspace token.",
            "Do not substitute a non-Eidos Google account for Eidos Workspace admin access.",
        ],
        "steps": [
            "Confirm the employee-approved square PNG/JPEG headshot, minimum 512x512.",
            "Resolve the Slack user by company email and record the current profile photo URL.",
            "Update Slack with users.setPhoto using an authorized user token, or use the Slack UI under the employee/admin-approved path.",
            "Open Google Workspace Admin or Admin SDK Directory as an Eidos admin and update users/{email}/photos/thumbnail.",
            "Re-read both surfaces and record proof: Slack profile image URL plus Google user photo response or Admin Console screenshot.",
        ],
    }

    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    _console.print()
    _console.print(Panel.fit(
        f"[bold]Employee profile photo[/bold]\n[dim]{subject} <{email}>[/dim]",
        border_style="cyan",
    ))

    if missing:
        _console.print("[bold red]Blocked gates[/bold red]")
        for item in missing:
            _console.print(f"  - {item}")
        _console.print()

    table = Table(show_header=True, header_style="bold cyan", box=None, pad_edge=False)
    table.add_column("Surface", style="bold")
    table.add_column("Action")
    table.add_column("Proof")
    table.add_row(
        "Slack",
        "Set the approved image with `users.setPhoto` using an authorized user token, or use the employee/admin-approved UI path.",
        "Profile image URL changed after re-reading the Slack user profile.",
    )
    table.add_row(
        "Google Workspace",
        "Use Admin Console or Admin SDK Directory `users.photos.update` as an Eidos admin for the employee email.",
        "Admin SDK photo response or Admin Console screenshot confirms the new photo.",
    )
    _console.print(table)
    _console.print()
    _console.print("[bold]Hard stops[/bold]")
    for stop in payload["hard_stops"]:
        _console.print(f"  - {stop}")
    _console.print()
