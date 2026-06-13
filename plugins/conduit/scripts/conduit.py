#!/usr/bin/env python3
"""Machine/conduit registry for Daniel's Mac mini infrastructure."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = PLUGIN_ROOT / "registry"
CONDUIT_PROOFS_DIR = Path(os.getenv("CONDUIT_PROOFS_DIR", REGISTRY_DIR / "conduit-proofs"))

ALIASES = {
    "mac-mini-01": "mac-mini-01",
    "apartment-mac-mini": "mac-mini-01",
    "daniel-laptop": "daniel-laptop-01",
    "laptop": "daniel-laptop-01",
    "rentamac-cyprus": "rentamac-cyprus-01",
    "rentamac": "rentamac-cyprus-01",
}


REMOTE_REPO_INVENTORY_SCRIPT = r"""
import json
import os
import sys
from pathlib import Path

max_depth = int(sys.argv[1])
roots = [Path(os.path.expanduser(item)) for item in sys.argv[2:]]
skip_dirs = {".git", ".venv", "__pycache__", "node_modules", "dist", "build", ".cache"}
first_hop_candidates = (
    "infra/README.md",
    "infra/RAILWAY.md",
    "README.md",
    "TODO.md",
    "VAULT.md",
    "docs/OMNIDATA.md",
)
patterns = {
    "omnidata": ".omnidata",
    "railguey": "railguey",
    "railway": "railway",
    "railway_token_alias": "RAILWAY_TOKEN",
    "deploy": "deploy",
}


def is_git_repo(path):
    marker = path / ".git"
    return marker.is_dir() or marker.is_file()


def discover_repos(root):
    repos = []

    def walk(path, depth):
        if depth > max_depth:
            return
        if is_git_repo(path):
            repos.append(path)
            return
        try:
            children = sorted(path.iterdir(), key=lambda item: item.name)
        except OSError:
            return
        for child in children:
            if not child.is_dir() or child.name in skip_dirs:
                continue
            walk(child, depth + 1)

    if root.exists() and root.is_dir():
        walk(root, 0)
    return repos


def text_hits(path):
    hits = set()
    try:
        data = path.read_text(errors="ignore")[:250000]
    except (OSError, UnicodeError):
        return hits
    lowered = data.lower()
    for key, needle in patterns.items():
        if needle.lower() in lowered:
            hits.add(key)
    return hits


def token_aliases(repo):
    aliases = []
    for name in (".env.local", ".env"):
        envfile = repo / name
        if not envfile.is_file():
            continue
        try:
            lines = envfile.read_text(errors="ignore").splitlines()
        except OSError:
            continue
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key = stripped.split("=", 1)[0].strip()
            if key == "RAILWAY_TOKEN" or key.startswith("RAILWAY_"):
                aliases.append({"file": name, "key": key})
    return aliases


def inspect_repo(repo):
    hit_keys = set()
    hit_files = []
    for rel in first_hop_candidates:
        path = repo / rel
        if path.is_file():
            hit_keys.update(text_hits(path))
            hit_files.append(rel)
    for subdir in (".github/workflows", "infra", "docs"):
        base = repo / subdir
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".md", ".yml", ".yaml", ".toml", ".json"}:
                rel = str(path.relative_to(repo))
                hits = text_hits(path)
                if hits:
                    hit_keys.update(hits)
                    hit_files.append(rel)
    has_omnidata = (repo / ".omnidata").is_file()
    if has_omnidata:
        hit_keys.add("omnidata")
    aliases = token_aliases(repo)
    if aliases:
        hit_keys.add("railway_token_alias")
    return {
        "path": str(repo),
        "name": repo.name,
        "has_omnidata": has_omnidata,
        "has_railguey_reference": "railguey" in hit_keys,
        "has_railway_reference": "railway" in hit_keys,
        "has_railway_token_alias": "railway_token_alias" in hit_keys,
        "has_deploy_reference": "deploy" in hit_keys,
        "first_hop_docs": [rel for rel in first_hop_candidates if (repo / rel).is_file()],
        "signals": sorted(hit_keys),
        "signal_files": sorted(set(hit_files))[:40],
        "railway_token_aliases": aliases,
    }


repos = []
for root in roots:
    for repo in discover_repos(root):
        row = inspect_repo(repo)
        if row["has_omnidata"] or row["signals"] or row["railway_token_aliases"]:
            repos.append(row)

print(json.dumps({
    "schema_version": "conduit.laptop_repo_inventory.v1",
    "roots": [str(root) for root in roots],
    "max_depth": max_depth,
    "count": len(repos),
    "repos": repos,
}, indent=2, sort_keys=True))
"""


def load_toml(name: str) -> dict[str, Any]:
    with (REGISTRY_DIR / name).open("rb") as handle:
        return tomllib.load(handle)


def registry() -> dict[str, Any]:
    return {
        "machines": load_toml("machines.toml").get("machines", []),
        "conduits": load_toml("conduits.toml").get("conduits", []),
        "services": load_toml("services.toml").get("services", []),
        "workloads": load_toml("workloads.toml").get("workloads", []),
    }


def machine_by_id(machine_id: str) -> dict[str, Any]:
    canonical = ALIASES.get(machine_id, machine_id)
    for machine in registry()["machines"]:
        if machine["id"] == canonical:
            return machine
    raise SystemExit(f"unknown machine: {machine_id}")


def conduits_for_machine(machine_id: str) -> list[dict[str, Any]]:
    canonical = machine_by_id(machine_id)["id"]
    return [conduit for conduit in registry()["conduits"] if conduit["machine_id"] == canonical]


def conduit_by_id(conduit_id: str) -> dict[str, Any]:
    for conduit in registry()["conduits"]:
        if conduit["id"] == conduit_id:
            return conduit
    raise SystemExit(f"unknown conduit: {conduit_id}")


def preferred_conduit(machine_id: str) -> dict[str, Any]:
    conduits = conduits_for_machine(machine_id)
    if not conduits:
        raise SystemExit(f"machine has no conduits: {machine_id}")
    for conduit in conduits:
        if conduit.get("primary", False):
            return conduit
    return conduits[0]


def endpoint_for(conduit: dict[str, Any]) -> str | None:
    env_name = conduit.get("endpoint_env")
    if env_name and os.getenv(env_name):
        return os.getenv(env_name)
    return conduit.get("endpoint_default")


def user_for(conduit: dict[str, Any]) -> str | None:
    env_name = conduit.get("user_env")
    if env_name and os.getenv(env_name):
        return os.getenv(env_name)
    return conduit.get("user_default")


def ssh_spec_for(conduit: dict[str, Any]) -> str | None:
    endpoint = endpoint_for(conduit)
    if not endpoint:
        return None
    user = user_for(conduit)
    return f"{user}@{endpoint}" if user else endpoint


def resolve_machine_and_conduit(target: str, conduit_id: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    if conduit_id:
        conduit = conduit_by_id(conduit_id)
        return machine_by_id(conduit["machine_id"]), conduit
    machine = machine_by_id(target)
    return machine, preferred_conduit(machine["id"])


def require_ssh_spec(conduit: dict[str, Any]) -> str:
    ssh_spec = ssh_spec_for(conduit)
    if not ssh_spec:
        endpoint_env = conduit.get("endpoint_env", "CONDUIT_ENDPOINT")
        user_env = conduit.get("user_env")
        user_hint = f" and optionally {user_env}" if user_env else ""
        raise SystemExit(
            f"conduit {conduit['id']} is known but not configured. "
            f"Set {endpoint_env}{user_hint}."
        )
    return ssh_spec


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def emit(data: Any, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(data)


def enriched_conduit(conduit: dict[str, Any]) -> dict[str, Any]:
    return {
        **conduit,
        "endpoint": endpoint_for(conduit),
        "user": user_for(conduit),
        "ssh_spec": ssh_spec_for(conduit),
        "configured": bool(endpoint_for(conduit)),
    }


def target_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for machine in registry()["machines"]:
        conduits = [enriched_conduit(conduit) for conduit in conduits_for_machine(machine["id"])]
        rows.append({**machine, "conduits": conduits})
    return rows


def cmd_registry(args: argparse.Namespace) -> None:
    emit(registry(), as_json=args.json)


def cmd_targets(args: argparse.Namespace) -> None:
    rows = target_rows()
    if args.json:
        emit(rows, as_json=True)
        return
    for machine in rows:
        primary = " primary" if machine.get("primary") else ""
        print(f"{machine['id']} [{machine['kind']}{primary}]")
        print(f"  trust: {machine['trust_tier']}")
        print(f"  roles: {', '.join(machine.get('roles', []))}")
        print(f"  location: {machine.get('physical_location') or machine.get('region') or '(remote)'}")
        for conduit in machine["conduits"]:
            status = "configured" if conduit["configured"] else "unconfigured"
            print(f"  conduit: {conduit['id']} [{status}] endpoint={conduit['endpoint'] or '(missing)'}")
        print(f"  notes: {machine['notes']}")


def cmd_machines(args: argparse.Namespace) -> None:
    machines = registry()["machines"]
    if args.json:
        emit(machines, as_json=True)
        return
    for machine in machines:
        print(f"{machine['id']}: {machine['label']}")


def cmd_conduits(args: argparse.Namespace) -> None:
    conduits = [enriched_conduit(conduit) for conduit in registry()["conduits"]]
    if args.json:
        emit(conduits, as_json=True)
        return
    for conduit in conduits:
        status = "configured" if conduit["configured"] else "unconfigured"
        print(f"{conduit['id']} -> {conduit['machine_id']} [{conduit['kind']}, {status}]")


def cmd_workloads(args: argparse.Namespace) -> None:
    workloads = registry()["workloads"]
    if args.json:
        emit(workloads, as_json=True)
        return
    for workload in workloads:
        print(f"{workload['id']}: preferred={workload['preferred_machine_id']}")


def cmd_services(args: argparse.Namespace) -> None:
    services = registry()["services"]
    if args.json:
        emit(services, as_json=True)
        return
    for service in services:
        print(f"{service['id']}: machine={service['machine_id']} status={service['status']}")


def cmd_doctor(args: argparse.Namespace) -> None:
    machine, conduit = resolve_machine_and_conduit(args.target, args.conduit)
    enriched = enriched_conduit(conduit)
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    add("machine-known", True, machine["id"])
    add("conduit-known", True, conduit["id"])
    add("conduit-configured", enriched["configured"], enriched["ssh_spec"] or "missing SSH endpoint")
    if enriched["configured"] and conduit["kind"] == "ssh":
        proc = run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                f"ConnectTimeout={args.timeout}",
                require_ssh_spec(conduit),
                "hostname",
            ],
            check=False,
        )
        add("ssh", proc.returncode == 0, (proc.stdout or proc.stderr).strip())

    data = {"machine": machine, "conduit": enriched, "checks": checks}
    if args.json:
        emit(data, as_json=True)
        return
    print(f"doctor: {machine['id']} via {conduit['id']}")
    for check in checks:
        marker = "ok" if check["ok"] else "fail"
        print(f"- {marker}: {check['name']} - {check['detail']}")


def write_proof_record(record: dict[str, Any]) -> Path:
    CONDUIT_PROOFS_DIR.mkdir(parents=True, exist_ok=True)
    proof_path = CONDUIT_PROOFS_DIR / f"{datetime.now(timezone.utc).date().isoformat()}.jsonl"
    with proof_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return proof_path


def proof_probe_command() -> str:
    return "printf 'hostname='; hostname; printf 'user='; whoami; printf 'pwd='; pwd; sw_vers 2>/dev/null || uname -a"


def run_proof_probe(
    machine: dict[str, Any],
    conduit: dict[str, Any],
    *,
    timeout: int,
    record_type: str,
) -> dict[str, Any]:
    ssh_spec = ssh_spec_for(conduit)
    if not ssh_spec:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "type": record_type,
            "machine_id": machine["id"],
            "conduit_id": conduit["id"],
            "ssh_spec": None,
            "ok": False,
            "stdout": "",
            "stderr": "missing SSH endpoint",
        }
        proof_path = write_proof_record(record)
        return {**record, "proof_path": str(proof_path)}

    proc = run(["ssh", "-o", "BatchMode=yes", "-o", f"ConnectTimeout={timeout}", ssh_spec, proof_probe_command()], check=False)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": record_type,
        "machine_id": machine["id"],
        "conduit_id": conduit["id"],
        "ssh_spec": ssh_spec,
        "ok": proc.returncode == 0,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }
    proof_path = write_proof_record(record)
    return {**record, "proof_path": str(proof_path)}


def cmd_proof(args: argparse.Namespace) -> None:
    machine, conduit = resolve_machine_and_conduit(args.target, args.conduit)
    require_ssh_spec(conduit)
    record = run_proof_probe(machine, conduit, timeout=args.timeout, record_type="proof")
    if args.json:
        emit(record, as_json=True)
        return
    print(f"proof: {machine['id']} via {conduit['id']}")
    print(f"ssh: {record['ssh_spec']}")
    print(record["stdout"] or record["stderr"])
    print(f"recorded: {record['proof_path']}")
    if not record["ok"]:
        raise SystemExit(255)


def mac_machines() -> list[dict[str, Any]]:
    return [machine for machine in registry()["machines"] if "mac" in machine["kind"].lower()]


def cmd_check_macs(args: argparse.Namespace) -> None:
    results: list[dict[str, Any]] = []
    for machine in mac_machines():
        conduit = preferred_conduit(machine["id"])
        results.append(run_proof_probe(machine, conduit, timeout=args.timeout, record_type="mac_check"))

    if args.json:
        emit({"ok": all(result["ok"] for result in results), "results": results}, as_json=True)
    else:
        print("mac checks")
        for result in results:
            status = "ok" if result["ok"] else "fail"
            detail = result["stdout"] or result["stderr"] or "(no output)"
            first_line = detail.splitlines()[0] if detail else "(no output)"
            print(f"- {status}: {result['machine_id']} via {result['conduit_id']} ssh={result['ssh_spec'] or '(missing)'}")
            print(f"  {first_line}")
            print(f"  recorded: {result['proof_path']}")

    if any(not result["ok"] for result in results):
        raise SystemExit(1)


def cmd_run(args: argparse.Namespace) -> None:
    _, conduit = resolve_machine_and_conduit(args.target, args.conduit)
    ssh_spec = require_ssh_spec(conduit)
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        raise SystemExit("missing command after --")
    remote = " ".join(shlex.quote(part) for part in args.command)
    proc = run(["ssh", ssh_spec, remote], check=False)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    raise SystemExit(proc.returncode)


def cmd_sync(args: argparse.Namespace) -> None:
    _, conduit = resolve_machine_and_conduit(args.target, args.conduit)
    ssh_spec = require_ssh_spec(conduit)
    source = Path(args.source).expanduser()
    if not source.exists():
        raise SystemExit(f"source does not exist: {source}")
    destination = f"{ssh_spec}:{args.destination}"
    cmd = ["rsync", "-az", "--human-readable", "--info=stats2,name1", str(source), destination]
    if args.dry_run:
        cmd.insert(2, "--dry-run")
    proc = run(cmd, check=False)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    raise SystemExit(proc.returncode)


def cmd_inventory_repos(args: argparse.Namespace) -> None:
    machine, conduit = resolve_machine_and_conduit(args.target, args.conduit)
    ssh_spec = require_ssh_spec(conduit)
    roots = args.roots or ["~/repos-personal", "~/repos-eidos-agi", "~/Documents"]
    remote = " ".join(
        shlex.quote(part)
        for part in [
            "python3",
            "-c",
            REMOTE_REPO_INVENTORY_SCRIPT,
            str(args.max_depth),
            *roots,
        ]
    )
    proc = run(["ssh", "-o", "BatchMode=yes", ssh_spec, remote], check=False)
    if proc.returncode != 0:
        if args.json:
            emit(
                {
                    "ok": False,
                    "machine_id": machine["id"],
                    "conduit_id": conduit["id"],
                    "stderr": proc.stderr.strip(),
                    "stdout": proc.stdout.strip(),
                },
                as_json=True,
            )
        else:
            sys.stdout.write(proc.stdout)
            sys.stderr.write(proc.stderr)
        raise SystemExit(proc.returncode)

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        if args.json:
            emit(
                {
                    "ok": False,
                    "machine_id": machine["id"],
                    "conduit_id": conduit["id"],
                    "stderr": "remote inventory did not return JSON",
                    "stdout": proc.stdout.strip(),
                },
                as_json=True,
            )
        else:
            sys.stdout.write(proc.stdout)
            sys.stderr.write(proc.stderr)
        raise SystemExit(1)

    payload = {
        "ok": True,
        "machine_id": machine["id"],
        "conduit_id": conduit["id"],
        **payload,
    }
    if args.json:
        emit(payload, as_json=True)
        return
    print(f"repo inventory: {machine['id']} via {conduit['id']}")
    for repo in payload.get("repos", []):
        signals = ", ".join(repo.get("signals", [])) or "no signals"
        print(f"- {repo['name']}: {repo['path']} [{signals}]")


def cmd_plugin_deploy(args: argparse.Namespace) -> None:
    plugin_path = Path(args.plugin_path).expanduser().resolve()
    manifest = plugin_path / ".codex-plugin" / "plugin.json"
    if not manifest.exists():
        raise SystemExit(f"not a Codex plugin path, missing {manifest}")
    destination = f"{args.remote_root.rstrip('/')}/{plugin_path.name}"
    sync_args = argparse.Namespace(
        target=args.target,
        conduit=args.conduit,
        source=str(plugin_path) + "/",
        destination=destination,
        dry_run=args.dry_run,
    )
    cmd_sync(sync_args)


def add_common_target_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target", default="mac-mini-01")
    parser.add_argument("--conduit")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="conduit")
    sub = parser.add_subparsers(required=True)

    registry_cmd = sub.add_parser("registry")
    registry_cmd.add_argument("--json", action="store_true")
    registry_cmd.set_defaults(func=cmd_registry)

    targets_cmd = sub.add_parser("targets")
    targets_cmd.add_argument("--json", action="store_true")
    targets_cmd.set_defaults(func=cmd_targets)

    machines = sub.add_parser("machines")
    machines.add_argument("--json", action="store_true")
    machines.set_defaults(func=cmd_machines)

    conduits = sub.add_parser("conduits")
    conduits.add_argument("--json", action="store_true")
    conduits.set_defaults(func=cmd_conduits)

    workloads = sub.add_parser("workloads")
    workloads.add_argument("--json", action="store_true")
    workloads.set_defaults(func=cmd_workloads)

    services = sub.add_parser("services")
    services.add_argument("--json", action="store_true")
    services.set_defaults(func=cmd_services)

    doctor = sub.add_parser("doctor")
    doctor.add_argument("target", nargs="?", default="mac-mini-01")
    doctor.add_argument("--conduit")
    doctor.add_argument("--timeout", type=int, default=5)
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(func=cmd_doctor)

    proof = sub.add_parser("proof")
    add_common_target_args(proof)
    proof.add_argument("--timeout", type=int, default=5)
    proof.add_argument("--json", action="store_true")
    proof.set_defaults(func=cmd_proof)

    check_macs = sub.add_parser("check-macs")
    check_macs.add_argument("--timeout", type=int, default=5)
    check_macs.add_argument("--json", action="store_true")
    check_macs.set_defaults(func=cmd_check_macs)

    run_cmd = sub.add_parser("run")
    add_common_target_args(run_cmd)
    run_cmd.add_argument("command", nargs=argparse.REMAINDER)
    run_cmd.set_defaults(func=cmd_run)

    inventory_repos = sub.add_parser("inventory-repos")
    add_common_target_args(inventory_repos)
    inventory_repos.set_defaults(target="daniel-laptop-01")
    inventory_repos.add_argument("--max-depth", type=int, default=2)
    inventory_repos.add_argument("--root", dest="roots", action="append", default=[])
    inventory_repos.add_argument("--json", action="store_true")
    inventory_repos.set_defaults(func=cmd_inventory_repos)

    sync = sub.add_parser("sync")
    sync.add_argument("source")
    sync.add_argument("destination")
    add_common_target_args(sync)
    sync.add_argument("--dry-run", action="store_true")
    sync.set_defaults(func=cmd_sync)

    plugin = sub.add_parser("plugin")
    plugin_sub = plugin.add_subparsers(required=True)
    deploy = plugin_sub.add_parser("deploy")
    deploy.add_argument("plugin_path")
    add_common_target_args(deploy)
    deploy.add_argument("--remote-root", default="~/plugins")
    deploy.add_argument("--dry-run", action="store_true")
    deploy.set_defaults(func=cmd_plugin_deploy)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
