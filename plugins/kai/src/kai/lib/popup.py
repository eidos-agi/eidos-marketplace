"""Tk popup helpers for sensitive secret entry and confirmation.

Service-agnostic. The caller supplies a SecretService (from kai.lib.secrets)
that names the service, the dashboard URL, and the human-readable instructions
for how to obtain the secret. This module just renders + collects.

Why a popup instead of a terminal prompt?
- Secrets shouldn't pass through shell history, scrollback, or paste-buffer
  trails that AI assistants and screenshot tools can scrape.
- Some kai invocations come from non-interactive launchers (Raycast, IDE tasks)
  where stdin isn't a real TTY.
- Confirmation steps deserve a real UI — read this, edit that, click OK.

Cross-platform via Tk (Python stdlib). Falls back to terminal getpass when Tk
isn't available so kai never gets stuck on a missing GUI.

Storage target: kai uses **Eidos Vault** (`eidos vault`). Knox is Daniel's
personal secrets agent — out of scope for kai.

NOT in v0:
  - Themed/branded windows. Plain ttk widgets keep the dependency surface zero.
  - Async / non-blocking flows. Each call blocks until the user responds.
  - Multi-step wizards beyond entry + confirm.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kai.lib.secrets import SecretService


@dataclass
class SecretEntryResult:
    """Captured response from the secret-entry popup."""

    secret: str
    label: str
    write_to_vault: bool
    vault_path: str
    write_to_env_file: bool
    env_file_path: str
    cancelled: bool = False

    # Legacy aliases — kept so older callers keep working during the
    # Knox→Vault transition. Prefer the new names. Will be removed.
    @property
    def write_to_knox(self) -> bool:  # pragma: no cover - alias
        return self.write_to_vault

    @property
    def knox_key(self) -> str:  # pragma: no cover - alias
        return self.vault_path


@dataclass
class ConfirmResult:
    """Yes/no on the post-validation save plan."""

    confirmed: bool
    cancelled: bool = False


def prompt_for_secret(service: SecretService) -> SecretEntryResult:
    if _can_use_tk():
        try:
            return _tk_prompt_for_secret(service)
        except Exception:  # noqa: BLE001
            pass
    return _terminal_prompt_for_secret(service)


def confirm_save(
    service: SecretService,
    identity_lines: list[tuple[str, str]],
    vault_path: str | None,
    env_file_path: str | None,
) -> ConfirmResult:
    if _can_use_tk():
        try:
            return _tk_confirm_save(service, identity_lines, vault_path, env_file_path)
        except Exception:  # noqa: BLE001
            pass
    return _terminal_confirm_save(service, identity_lines, vault_path, env_file_path)


# ─── Tk implementation ───────────────────────────────────────────────────────


def _can_use_tk() -> bool:
    try:
        import tkinter  # noqa: F401
    except ImportError:
        return False
    return True


def _tk_prompt_for_secret(service: SecretService) -> SecretEntryResult:
    """Plain-English handoff popup with copy-URL + open-browser + paste-token + save.

    Single window. No confirm modal. The whole transaction is visible at once.
    """
    import tkinter as tk
    import webbrowser
    from tkinter import ttk

    result = SecretEntryResult(
        secret="", label=service.default_label,
        write_to_vault=True, vault_path=service.default_vault_path,
        write_to_env_file=False, env_file_path=service.default_env_file,
        cancelled=True,
    )

    root = tk.Tk()
    root.title(f"kai login — {service.display_name}")
    root.resizable(False, False)
    root.lift()
    root.attributes("-topmost", True)
    root.after_idle(root.attributes, "-topmost", False)
    # Reasonable starting width so the URL doesn't get cropped
    root.minsize(560, 420)

    pad_x = 16
    pad_y = 8

    # ── Title ──────────────────────────────────────────────────────────
    ttk.Label(
        root,
        text=f"Get your {service.display_name} token",
        font=("TkDefaultFont", 16, "bold"),
    ).pack(anchor="w", padx=pad_x, pady=(pad_y * 2, pad_y))

    # ── Friendly framing ───────────────────────────────────────────────
    ttk.Label(
        root,
        text=(
            "This is the part Claude can't do for you.\n"
            "You're already signed into the workspace in your browser; Claude isn't.\n"
            "Five steps below — under 30 seconds."
        ),
        justify="left",
        wraplength=520,
    ).pack(anchor="w", padx=pad_x, pady=(0, pad_y))

    # ── Step-by-step instructions ──────────────────────────────────────
    steps_frame = ttk.Frame(root)
    steps_frame.pack(anchor="w", padx=pad_x, pady=(0, pad_y), fill="x")

    instructions = service.instructions.strip().splitlines()
    if not instructions:
        instructions = [
            "1. Click \"Copy URL\" below.",
            "2. Paste in your browser address bar.",
            "3. Find the token on that page (look for an xoxb- or xoxp- prefix).",
            "4. Copy it.",
            "5. Paste in the field below, click Save.",
        ]
    for line in instructions:
        ttk.Label(steps_frame, text=line, justify="left", wraplength=520).pack(anchor="w")

    # ── URL row + buttons ──────────────────────────────────────────────
    url_frame = ttk.Frame(root)
    url_frame.pack(fill="x", padx=pad_x, pady=(pad_y, pad_y))

    ttk.Label(url_frame, text=f"{service.display_name} URL:", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
    url_var = tk.StringVar(value=service.dashboard_url)
    url_entry = ttk.Entry(url_frame, textvariable=url_var, width=60)
    url_entry.configure(state="readonly")
    url_entry.pack(fill="x", pady=(2, 6))

    btn_row = ttk.Frame(url_frame)
    btn_row.pack(anchor="w")

    copy_status = tk.StringVar(value="")

    def on_copy_url():
        root.clipboard_clear()
        root.clipboard_append(service.dashboard_url)
        root.update()  # without this, clipboard contents are lost when Tk closes
        copy_status.set("✓ copied")
        root.after(2000, lambda: copy_status.set(""))

    def on_open_browser():
        try:
            webbrowser.open(service.dashboard_url)
            copy_status.set("✓ opened in browser")
            root.after(2000, lambda: copy_status.set(""))
        except Exception as e:  # noqa: BLE001
            copy_status.set(f"× couldn't open: {e}")

    ttk.Button(btn_row, text="Copy URL", command=on_copy_url).pack(side="left", padx=(0, 6))
    ttk.Button(btn_row, text="Open in browser", command=on_open_browser).pack(side="left", padx=(0, 6))
    ttk.Label(btn_row, textvariable=copy_status, foreground="#0a8043").pack(side="left", padx=(8, 0))

    # ── Token paste row ────────────────────────────────────────────────
    paste_frame = ttk.Frame(root)
    paste_frame.pack(fill="x", padx=pad_x, pady=(pad_y * 2, pad_y))

    ttk.Label(
        paste_frame,
        text=service.secret_label or "Paste token here:",
        font=("TkDefaultFont", 11, "bold"),
    ).pack(anchor="w")
    secret_var = tk.StringVar()
    secret_entry = ttk.Entry(paste_frame, textvariable=secret_var, show="•", width=60)
    secret_entry.pack(fill="x", pady=(2, 0))
    secret_entry.focus_set()

    # ── Vault path (read-only display; edit via flag if needed) ────────
    vault_frame = ttk.Frame(root)
    vault_frame.pack(fill="x", padx=pad_x, pady=(pad_y, pad_y))
    ttk.Label(
        vault_frame,
        text=f"Will save to Eidos Vault path:  {service.default_vault_path}",
        foreground="#666",
    ).pack(anchor="w")

    # ── Bottom button bar ──────────────────────────────────────────────
    bottom_frame = ttk.Frame(root)
    bottom_frame.pack(fill="x", padx=pad_x, pady=(pad_y * 2, pad_y * 2))

    def on_save():
        s = secret_var.get().strip()
        if not s:
            copy_status.set("× empty — paste the token first")
            return
        result.secret = s
        result.label = service.default_label
        result.write_to_vault = True
        result.vault_path = service.default_vault_path
        result.write_to_env_file = False
        result.env_file_path = service.default_env_file
        result.cancelled = False
        root.destroy()

    def on_cancel():
        result.cancelled = True
        root.destroy()

    ttk.Button(bottom_frame, text="Cancel", command=on_cancel).pack(side="right", padx=(6, 0))
    save_btn = ttk.Button(bottom_frame, text="Save to Vault", command=on_save)
    save_btn.pack(side="right", padx=(0, 6))

    # Enter on the paste field saves; Escape cancels
    secret_entry.bind("<Return>", lambda _e: on_save())
    root.bind("<Escape>", lambda _e: on_cancel())
    root.protocol("WM_DELETE_WINDOW", on_cancel)
    root.mainloop()

    return result


def _tk_confirm_save(
    service: SecretService,
    identity_lines: list[tuple[str, str]],
    vault_path: str | None,
    env_file_path: str | None,
) -> ConfirmResult:
    import tkinter as tk
    from tkinter import ttk

    result = ConfirmResult(confirmed=False, cancelled=True)

    root = tk.Tk()
    root.title(f"kai login — {service.display_name} — confirm")
    root.resizable(False, False)
    root.lift()
    root.attributes("-topmost", True)
    root.after_idle(root.attributes, "-topmost", False)

    pad = {"padx": 12, "pady": 6}

    ttk.Label(
        root,
        text=f"{service.display_name} secret validated. Confirm save:",
        font=("TkDefaultFont", 13, "bold"),
    ).grid(row=0, column=0, columnspan=2, sticky="w", **pad)

    rows = list(identity_lines)
    if vault_path:
        rows.append(("write to Eidos Vault", vault_path))
    if env_file_path:
        rows.append(("write to env", env_file_path))

    for i, (k, v) in enumerate(rows, start=1):
        ttk.Label(root, text=f"{k}:").grid(row=i, column=0, sticky="e", **pad)
        e = ttk.Entry(root, width=50)
        e.insert(0, v)
        e.configure(state="readonly")
        e.grid(row=i, column=1, sticky="we", **pad)

    btn_frame = ttk.Frame(root)
    btn_frame.grid(row=len(rows) + 1, column=0, columnspan=2, sticky="e", **pad)

    def on_save():
        result.confirmed = True
        result.cancelled = False
        root.destroy()

    def on_cancel():
        result.confirmed = False
        result.cancelled = True
        root.destroy()

    ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side="right", padx=4)
    ttk.Button(btn_frame, text="Save", command=on_save).pack(side="right", padx=4)
    root.protocol("WM_DELETE_WINDOW", on_cancel)
    root.mainloop()

    return result


# ─── terminal fallback ───────────────────────────────────────────────────────


def _terminal_prompt_for_secret(service: SecretService) -> SecretEntryResult:
    import getpass

    print()
    print(f"=== kai login — {service.display_name} ===")
    print(service.instructions)
    print()
    print(f"Dashboard: {service.dashboard_url}")
    print()
    print("Paste the secret (hidden). Empty input cancels.")
    secret = getpass.getpass(f"{service.secret_label or 'Secret'}: ").strip()
    if not secret:
        return SecretEntryResult(
            secret="", label=service.default_label,
            write_to_vault=False, vault_path=service.default_vault_path,
            write_to_env_file=False, env_file_path=service.default_env_file,
            cancelled=True,
        )
    label = input(f"Label [{service.default_label}]: ").strip() or service.default_label
    vault_ans = input("Store in Eidos Vault? [Y/n]: ").strip().lower()
    write_to_vault = vault_ans != "n"
    vault_path = service.default_vault_path
    if write_to_vault:
        vault_path = input(f"Vault path [{service.default_vault_path}]: ").strip() or service.default_vault_path
    env_ans = input("Also write to env file? [y/N]: ").strip().lower()
    write_to_env = env_ans == "y"
    env_path = service.default_env_file
    if write_to_env:
        env_path = input(f"Env file [{service.default_env_file}]: ").strip() or service.default_env_file
    return SecretEntryResult(
        secret=secret, label=label,
        write_to_vault=write_to_vault, vault_path=vault_path,
        write_to_env_file=write_to_env, env_file_path=env_path,
        cancelled=False,
    )


def _terminal_confirm_save(
    service: SecretService,
    identity_lines: list[tuple[str, str]],
    vault_path: str | None,
    env_file_path: str | None,
) -> ConfirmResult:
    print()
    print(f"{service.display_name} secret validated:")
    for k, v in identity_lines:
        print(f"  {k}: {v}")
    print()
    print("Will write:")
    if vault_path:
        print(f"  Vault path: {vault_path}")
    if env_file_path:
        print(f"  env file:   {env_file_path}")
    ans = input("Save? [Y/n]: ").strip().lower()
    confirmed = ans != "n"
    return ConfirmResult(confirmed=confirmed, cancelled=not confirmed)
