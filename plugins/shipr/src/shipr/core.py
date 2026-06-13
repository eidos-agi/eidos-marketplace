"""Core release-model logic for Shipr."""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


MODEL_PATH = Path(".shipr/product-release-model.json")
ATTEMPTS_DIR = Path(".shipr/release-attempts")
SHIPR_IGNORE_ENTRY = ".shipr/"


def _exists(root: Path, *parts: str) -> bool:
    return (root.joinpath(*parts)).exists()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _project_uses_git(root: Path) -> bool:
    return (root / ".git").exists() or (root / ".gitignore").exists()


def _has_shipr_ignore(lines: list[str]) -> bool:
    ignored_forms = {".shipr", ".shipr/", ".shipr/*", ".shipr/**"}
    return any(line.strip() in ignored_forms for line in lines)


def ensure_shipr_ignored(project: Path) -> Path | None:
    """Keep Shipr's local release memory out of source-control status noise."""
    root = project.resolve()
    if not _project_uses_git(root):
        return None

    gitignore = root / ".gitignore"
    text = gitignore.read_text() if gitignore.exists() else ""
    if _has_shipr_ignore(text.splitlines()):
        return None

    if text and not text.endswith("\n"):
        text += "\n"
    gitignore.write_text(f"{text}{SHIPR_IGNORE_ENTRY}\n")
    return gitignore


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug[:80] or "release"


def detect_release_model(project: Path, description: str = "") -> dict[str, Any]:
    """Detect a conservative per-product release model from local project evidence."""
    root = project.resolve()
    product = root.name
    artifact_types: list[str] = []
    channels: list[str] = []
    proof_commands: list[str] = []
    approval_gates = [
        "credentials",
        "payments",
        "production mutations",
        "public publish/tag",
        "customer/outbound messaging",
    ]
    rollback: list[str] = []
    companions = ["forge-forge", "ship-forge", "security-forge", "learning-forge", "loss-forge"]

    if _exists(root, "pyproject.toml"):
        artifact_types.append("python-package")
        channels.append("PyPI or uvx")
        proof_commands.extend(
            [
                "python -m pytest -q",
                "python -m ruff check .",
                "python -m ruff format --check .",
            ]
        )
        rollback.append(
            "bump patch version and release a fixed package; yank only for severe package faults"
        )

    if _exists(root, ".codex-plugin", "plugin.json") or _exists(
        root, ".claude-plugin", "plugin.json"
    ):
        artifact_types.append("eidos-plugin")
        channels.append("Eidos AGI marketplace")
        proof_commands.extend(
            [
                "python tools/marketplace_publish.py check <plugin> --source <source-repo>",
                "codex plugin list --marketplace eidos-agi",
                "codex plugin add <plugin>@eidos-agi",
            ]
        )
        rollback.append("remove or pin marketplace entry, then refresh plugin cache")

    if _exists(root, ".agents", "plugins", "marketplace.json") or _exists(
        root, ".claude-plugin", "marketplace.json"
    ):
        artifact_types.append("plugin-marketplace")
        channels.append("Codex/Claude plugin marketplace")
        proof_commands.append("python -m pytest tests/test_marketplace_publish.py -q")
        rollback.append("revert marketplace entry and published bundle")

    if _exists(root, "package.json"):
        artifact_types.append("web-or-node-app")
        channels.append("npm/web deploy")
        proof_commands.extend(["npm test", "npm run build"])
        rollback.append("redeploy previous build or revert deployment")

    if _exists(root, "Dockerfile") or _exists(root, "railway.json"):
        artifact_types.append("service")
        channels.append("service deploy")
        proof_commands.extend(["docker build .", "curl -fsS <health-url>"])
        rollback.append("redeploy previous image or rollback provider deployment")

    if _exists(root, "app") or list(root.glob("*.xcodeproj")):
        artifact_types.append("mac-or-ios-app")
        channels.append("signed app distribution")
        proof_commands.append("xcodebuild test")
        approval_gates.append("code signing/notarization credentials")
        rollback.append("restore previous signed build")

    if _exists(root, "README.md") or _exists(root, "docs"):
        artifact_types.append("docs")
        proof_commands.append("verify README, changelog, and release notes match artifact version")

    if not proof_commands:
        proof_commands.append("define product-specific proof command before shipping")

    if not artifact_types:
        artifact_types.append("unknown")
        channels.append("undiscovered")

    release_model = {
        "schema_version": 1,
        "product_id": product,
        "project_root": str(root),
        "description": description,
        "artifact_types": sorted(set(artifact_types)),
        "distribution_channels": sorted(set(channels)),
        "proof_commands": list(dict.fromkeys(proof_commands)),
        "approval_gates": list(dict.fromkeys(approval_gates)),
        "rollback_paths": list(dict.fromkeys(rollback)),
        "forge_stack": companions,
        "learning_questions": [
            "What broke or slowed this release?",
            "What proof was missing until late?",
            "Which gate should become automatic next time?",
            "Which human approval should remain explicit?",
        ],
        "memory_paths": {
            "model": str(MODEL_PATH),
            "attempts_dir": str(ATTEMPTS_DIR),
        },
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    return release_model


def write_release_model(project: Path, model: dict[str, Any]) -> Path:
    root = project.resolve()
    ensure_shipr_ignored(root)
    path = root / MODEL_PATH
    _write_json(path, model)
    return path


def load_release_model(project: Path) -> dict[str, Any] | None:
    path = project.resolve() / MODEL_PATH
    if not path.exists():
        return None
    return _read_json(path)


def record_attempt(
    project: Path,
    goal: str,
    status: str = "planned",
    notes: str = "",
    proofs: list[str] | None = None,
) -> tuple[Path, dict[str, Any]]:
    root = project.resolve()
    ensure_shipr_ignored(root)
    model = load_release_model(root) or detect_release_model(root)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    attempt = {
        "schema_version": 1,
        "product_id": model["product_id"],
        "goal": goal,
        "status": status,
        "notes": notes,
        "proofs": proofs or [],
        "release_model_snapshot": {
            "artifact_types": model["artifact_types"],
            "distribution_channels": model["distribution_channels"],
            "proof_commands": model["proof_commands"],
            "approval_gates": model["approval_gates"],
            "forge_stack": model["forge_stack"],
        },
        "learning_prompts": model["learning_questions"],
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    path = root / ATTEMPTS_DIR / f"{timestamp}-{_slug(goal)}.json"
    _write_json(path, attempt)
    return path, attempt


def release_frontier(project: Path) -> dict[str, Any]:
    root = project.resolve()
    model = load_release_model(root)
    attempts_dir = root / ATTEMPTS_DIR
    attempts = sorted(attempts_dir.glob("*.json")) if attempts_dir.exists() else []
    if model is None:
        return {
            "status": "needs_release_model",
            "next_actions": ["run `shipr model --write`"],
            "attempt_count": len(attempts),
        }

    next_actions = [
        "run proof commands for this product",
        "record release attempt with `shipr attempt --write`",
        "route lessons to learning-forge after release",
    ]
    if not attempts:
        next_actions.insert(0, "record the first release attempt")

    return {
        "status": "model_ready",
        "product_id": model["product_id"],
        "artifact_types": model["artifact_types"],
        "distribution_channels": model["distribution_channels"],
        "proof_commands": model["proof_commands"],
        "approval_gates": model["approval_gates"],
        "attempt_count": len(attempts),
        "latest_attempt": str(attempts[-1]) if attempts else None,
        "next_actions": next_actions,
    }
