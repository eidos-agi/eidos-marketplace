"""Shipr command line interface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .core import detect_release_model, record_attempt, release_frontier, write_release_model


def _print(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    for key, value in payload.items():
        print(f"{key}: {value}")


def _cmd_model(args: argparse.Namespace) -> None:
    model = detect_release_model(args.project, args.description or "")
    if args.write:
        path = write_release_model(args.project, model)
        model["written_to"] = str(path)
    _print(model, args.json)


def _cmd_attempt(args: argparse.Namespace) -> None:
    path, attempt = record_attempt(
        args.project,
        goal=args.goal,
        status=args.status,
        notes=args.notes or "",
        proofs=args.proof or [],
    )
    attempt["written_to"] = str(path)
    _print(attempt, args.json)


def _cmd_frontier(args: argparse.Namespace) -> None:
    _print(release_frontier(args.project), args.json)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="shipr",
        description="Shipr learns how each product ships and records proof-backed release memory.",
    )
    parser.add_argument("--version", action="version", version=f"shipr {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_model = sub.add_parser("model", help="Detect or refresh a product release model")
    p_model.add_argument("--project", type=Path, default=Path.cwd(), help="Project root")
    p_model.add_argument("--description", help="Optional product/release context")
    p_model.add_argument(
        "--write", action="store_true", help="Write .shipr/product-release-model.json"
    )
    p_model.add_argument("--json", action="store_true", help="Output JSON")

    p_attempt = sub.add_parser("attempt", help="Record a release attempt")
    p_attempt.add_argument("--project", type=Path, default=Path.cwd(), help="Project root")
    p_attempt.add_argument("--goal", required=True, help="Release goal")
    p_attempt.add_argument(
        "--status",
        default="planned",
        choices=["planned", "ready", "blocked", "shipped", "rolled_back"],
    )
    p_attempt.add_argument("--notes", help="Short release notes or blocker summary")
    p_attempt.add_argument("--proof", action="append", default=[], help="Proof command or artifact")
    p_attempt.add_argument("--json", action="store_true", help="Output JSON")

    p_frontier = sub.add_parser("frontier", help="Show current release frontier")
    p_frontier.add_argument("--project", type=Path, default=Path.cwd(), help="Project root")
    p_frontier.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args(argv)
    handlers = {
        "model": _cmd_model,
        "attempt": _cmd_attempt,
        "frontier": _cmd_frontier,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    main()
