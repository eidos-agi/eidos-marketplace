#!/usr/bin/env python3
"""Publish source-owned Eidos plugins into the marketplace listing."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


MARKETPLACE_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_JSON = Path(".claude-plugin/marketplace.json")
BUNDLE_ITEMS = (
    ".claude-plugin",
    ".codex-plugin",
    ".mcp.json",
    "skills",
    "commands",
    "hooks",
    "scripts",
    "packages",
    "assets",
    "README.md",
    "LICENSE",
)


@dataclass
class PublishReport:
    name: str
    bundle_path: Path
    marketplace_entry: dict[str, Any]
    audit_path: Path


@dataclass
class CheckReport:
    name: str
    ok: bool
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def source_manifest_path(source: Path) -> Path:
    for candidate in (
        source / ".claude-plugin" / "plugin.json",
        source / ".codex-plugin" / "plugin.json",
    ):
        if candidate.exists():
            return candidate
    raise FileNotFoundError("source repo must contain .claude-plugin/plugin.json or .codex-plugin/plugin.json")


def public_plugin_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
    )
    return {key: manifest[key] for key in keys if key in manifest}


def copy_item(source: Path, destination: Path) -> None:
    if destination.exists():
        if destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()

    if source.is_dir():
        ignore = shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".ruff_cache")
        shutil.copytree(source, destination, ignore=ignore)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def normalize_mcp_config(config: dict[str, Any], source: Path) -> dict[str, Any]:
    source = source.resolve()

    def normalize_value(value: Any) -> Any:
        if not isinstance(value, str):
            return value
        try:
            path = Path(value).resolve()
            relative = path.relative_to(source)
        except (OSError, ValueError):
            return value
        return "${CLAUDE_PLUGIN_ROOT}/" + relative.as_posix()

    def normalize_server(server: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(server)
        normalized["args"] = [normalize_value(arg) for arg in normalized.get("args", [])]
        return normalized

    if "mcpServers" in config and isinstance(config["mcpServers"], dict):
        normalized = dict(config)
        normalized["mcpServers"] = {
            name: normalize_server(server) if isinstance(server, dict) else server
            for name, server in config["mcpServers"].items()
        }
        return normalized

    return {
        name: normalize_server(server) if isinstance(server, dict) else server
        for name, server in config.items()
    }


def render_bundle(source: Path, marketplace: Path, manifest: dict[str, Any]) -> Path:
    name = manifest["name"]
    bundle = marketplace / "plugins" / name
    bundle.mkdir(parents=True, exist_ok=True)

    for item in BUNDLE_ITEMS:
        source_item = source / item
        if source_item.exists():
            if item == ".mcp.json":
                write_json(bundle / item, normalize_mcp_config(load_json(source_item), source))
            else:
                copy_item(source_item, bundle / item)

    claude_manifest = bundle / ".claude-plugin" / "plugin.json"
    if not claude_manifest.exists():
        write_json(claude_manifest, public_plugin_manifest(manifest))

    return bundle


def classify_plugin(source: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    signals: list[str] = []
    if (source / "skills").exists() or manifest.get("skills"):
        signals.extend(["ships_skills", "opinionated_workflow"])
    if (source / ".mcp.json").exists() or manifest.get("mcpServers"):
        signals.append("mcp_server")

    if "ships_skills" in signals or "opinionated_workflow" in signals:
        return {"type": "forge", "signals": signals}

    return {"type": "tool", "signals": signals or ["single_capability"]}


def category_from_manifest(manifest: dict[str, Any], classification: dict[str, Any]) -> str:
    interface = manifest.get("interface", {})
    category = interface.get("category") or manifest.get("category")
    if isinstance(category, str) and category.strip():
        return category.strip().lower().replace(" ", "-")
    if classification["type"] == "forge":
        return "development"
    return "agent-tools"


def marketplace_entry(source: Path, manifest: dict[str, Any], audit_date: str) -> dict[str, Any]:
    name = manifest["name"]
    classification = classify_plugin(source, manifest)
    entry: dict[str, Any] = {
        "name": name,
        "description": manifest.get("description", ""),
        "source": f"./plugins/{name}",
        "category": category_from_manifest(manifest, classification),
        "homepage": manifest.get("homepage") or manifest.get("repository") or "",
    }

    for key in ("license", "version"):
        if manifest.get(key):
            entry[key] = manifest[key]
    if manifest.get("keywords"):
        entry["tags"] = manifest["keywords"]

    x_eidos: dict[str, Any] = {
        "kind": classification,
        "audit": {
            "audited_by": "pending",
            "audit_version": "STANDARD.md",
            "audit_date": audit_date,
            "grade": "PENDING",
            "audit_doc": f"AUDITS/{name}.md",
        },
    }
    if classification["type"] == "forge":
        x_eidos["recommend"] = {
            "for_projects": ["plugin", "marketplace-entry", "company-distribution"],
            "pairs_with": ["foss-forge", "ship-forge", "mcp-forge"],
            "preflight_check": f"/{name}",
        }
    entry["x-eidos"] = x_eidos
    return entry


def upsert_marketplace_entry(marketplace: Path, entry: dict[str, Any]) -> None:
    path = marketplace / MARKETPLACE_JSON
    data = load_json(path)
    plugins = data.setdefault("plugins", [])
    plugins[:] = [plugin for plugin in plugins if plugin.get("name") != entry["name"]]
    plugins.append(entry)
    plugins.sort(key=lambda plugin: plugin.get("name", ""))
    write_json(path, data)


def ensure_audit(marketplace: Path, entry: dict[str, Any], audit_date: str) -> Path:
    audit_path = marketplace / entry["x-eidos"]["audit"]["audit_doc"]
    if audit_path.exists():
        return audit_path

    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(
        "\n".join(
            [
                f"# Audit: {entry['name']}",
                "",
                f"## {audit_date} — Grade: PENDING",
                "",
                "- Community Health: PENDING — run foss-forge or the marketplace audit workflow.",
                "- Agentic Quality: PENDING — run Felix plugin doctor and MCP/skill checks.",
                "- Engineering: PENDING — verify package, CI, release, and install smoke evidence.",
                f"- Notes: Published into eidos-marketplace from `{entry['homepage']}`; audit must be completed before grading.",
                "",
            ]
        )
    )
    return audit_path


def publish(source: Path, marketplace: Path = MARKETPLACE_ROOT, audit_date: str | None = None) -> PublishReport:
    source = source.resolve()
    marketplace = marketplace.resolve()
    audit_date = audit_date or dt.date.today().isoformat()
    manifest = load_json(source_manifest_path(source))
    entry = marketplace_entry(source, manifest, audit_date)
    bundle = render_bundle(source, marketplace, manifest)
    upsert_marketplace_entry(marketplace, entry)
    audit_path = ensure_audit(marketplace, entry, audit_date)
    return PublishReport(entry["name"], bundle, entry, audit_path)


def check(name: str, marketplace: Path = MARKETPLACE_ROOT) -> CheckReport:
    marketplace = marketplace.resolve()
    blockers: list[str] = []
    warnings: list[str] = []
    data = load_json(marketplace / MARKETPLACE_JSON)
    entries = [entry for entry in data.get("plugins", []) if entry.get("name") == name]
    if not entries:
        return CheckReport(name=name, ok=False, blockers=[f"missing marketplace entry: {name}"])

    entry = entries[0]
    source = entry.get("source")
    if not isinstance(source, str) or not source.startswith("./plugins/"):
        blockers.append("marketplace entry source must point under ./plugins/")
        plugin_dir = marketplace / "plugins" / name
    else:
        plugin_dir = marketplace / source.removeprefix("./")

    relative_plugin_dir = plugin_dir.relative_to(marketplace)
    if not plugin_dir.exists():
        blockers.append(f"missing plugin directory: {relative_plugin_dir}")
    else:
        if not (plugin_dir / ".claude-plugin" / "plugin.json").exists():
            blockers.append(f"missing plugin manifest: {relative_plugin_dir}/.claude-plugin/plugin.json")
        if not any((plugin_dir / item).exists() for item in ("skills", ".mcp.json", "commands", "hooks")):
            warnings.append(f"plugin bundle has no skills, .mcp.json, commands, or hooks: {relative_plugin_dir}")

    audit_doc = entry.get("x-eidos", {}).get("audit", {}).get("audit_doc")
    if not isinstance(audit_doc, str):
        blockers.append("missing x-eidos.audit.audit_doc")
    elif not (marketplace / audit_doc).exists():
        blockers.append(f"missing audit doc: {audit_doc}")

    return CheckReport(name=name, ok=not blockers, blockers=blockers, warnings=warnings)


def print_check(report: CheckReport) -> None:
    print(f"{report.name}: {'OK' if report.ok else 'FAIL'}")
    for blocker in report.blockers:
        print(f"  BLOCKER {blocker}")
    for warning in report.warnings:
        print(f"  WARN {warning}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    publish_parser = subparsers.add_parser("publish", help="Render a source plugin into the marketplace")
    publish_parser.add_argument("source", type=Path)
    publish_parser.add_argument("--marketplace", type=Path, default=MARKETPLACE_ROOT)
    publish_parser.add_argument("--audit-date")

    check_parser = subparsers.add_parser("check", help="Check a marketplace plugin listing")
    check_parser.add_argument("name")
    check_parser.add_argument("--marketplace", type=Path, default=MARKETPLACE_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "publish":
        report = publish(args.source, args.marketplace, args.audit_date)
        print(f"published {report.name}")
        print(f"  bundle: {report.bundle_path}")
        print(f"  audit: {report.audit_path}")
        check_report = check(report.name, args.marketplace)
        print_check(check_report)
        return 0 if check_report.ok else 1

    if args.command == "check":
        report = check(args.name, args.marketplace)
        print_check(report)
        return 0 if report.ok else 1

    raise AssertionError(args.command)


if __name__ == "__main__":
    sys.exit(main())
