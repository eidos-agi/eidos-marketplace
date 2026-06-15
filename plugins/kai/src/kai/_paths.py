"""kai path resolution — three-tier: --flag → env var → fallback.

Fail loud with a clear message when a required path doesn't exist.
Never silently substitute alternative paths.

NOT in v0:
  - Auto-discovery (walking up from cwd to find a cockpit). Explicit env
    var or --flag is the contract.
  - Multi-cockpit dispatch (per-pilot routing). Single shared cockpit-eidos
    is the v0 model; per-pilot adds when needed.
"""
from __future__ import annotations

import os
from pathlib import Path

import typer

REPOS_ROOT_ENV = "KAI_REPOS_ROOT"
DEFAULT_REPOS_ROOT = Path.home() / "repos-eidos-agi"

COCKPIT_ROOT_ENV = "KAI_COCKPIT_ROOT"
DEFAULT_COCKPIT_ROOT = Path.home() / "repos-eidos-agi" / "cockpit-eidos"

CONFIG_DIR_ENV = "KAI_CONFIG_DIR"
DEFAULT_CONFIG_DIR = Path.home() / ".kai"


def require_repos_root(override: Path | None = None) -> Path:
    """Resolve the eidos-agi repos root. --flag → env → fallback."""
    return _resolve(override, REPOS_ROOT_ENV, DEFAULT_REPOS_ROOT, "repos-root")


def require_cockpit_root(override: Path | None = None) -> Path:
    """Resolve the cockpit-eidos root. --flag → env → fallback.

    Fails loud when the resolved root is missing. Use for read/dispatch paths
    that must not invent a cockpit. Capture surfaces use ensure_cockpit_root.
    """
    return _resolve(override, COCKPIT_ROOT_ENV, DEFAULT_COCKPIT_ROOT, "cockpit-root")


def ensure_cockpit_root(override: Path | None = None) -> Path:
    """Resolve the cockpit-eidos root, creating it if absent. --flag → env → fallback.

    Capture surfaces (feedback, ideas) bootstrap the cockpit root so signal
    can be captured immediately on a fresh machine. Non-capture paths keep
    using require_cockpit_root and stay loud when the root is missing.
    """
    path = _resolve_path(override, COCKPIT_ROOT_ENV, DEFAULT_COCKPIT_ROOT)
    path.mkdir(parents=True, exist_ok=True)
    return path


def require_config_dir() -> Path:
    """Resolve ~/.kai (creates if absent — config always needs a home)."""
    override = os.environ.get(CONFIG_DIR_ENV)
    path = Path(override).expanduser() if override else DEFAULT_CONFIG_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def repo_path(name: str, repos_root: Path | None = None) -> Path:
    """Resolve <repos-root>/<name>. Used by dispatchers like `kai deploy`
    that need to know where a sibling repo lives."""
    root = require_repos_root(repos_root)
    target = root / name
    if not target.exists():
        typer.echo(
            f"repo not found: {target}\n"
            f"Set ${REPOS_ROOT_ENV} or pass --repos-root explicitly.",
            err=True,
        )
        raise typer.Exit(1)
    return target


def _resolve_path(override: Path | None, env_var: str, fallback: Path) -> Path:
    """Apply the three-tier precedence (--flag → env → fallback) without
    asserting existence. Existence policy is the caller's (loud vs. bootstrap)."""
    if override is not None:
        return override.expanduser().resolve()
    elif env_var in os.environ:
        return Path(os.environ[env_var]).expanduser().resolve()
    else:
        return fallback.expanduser().resolve()


def _resolve(override: Path | None, env_var: str, fallback: Path, label: str) -> Path:
    path = _resolve_path(override, env_var, fallback)

    if not path.exists():
        typer.echo(
            f"{label} not found: {path}\n"
            f"Set ${env_var} or pass --{label} explicitly.",
            err=True,
        )
        raise typer.Exit(1)
    return path
