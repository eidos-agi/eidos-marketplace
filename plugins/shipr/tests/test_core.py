import json
from pathlib import Path

from shipr.core import (
    detect_release_model,
    ensure_shipr_ignored,
    record_attempt,
    record_eidos_ship_attempt,
    release_frontier,
    summarize_eidos_ship_report,
    write_release_model,
)


def test_detects_python_plugin_project(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    (tmp_path / ".codex-plugin").mkdir()
    (tmp_path / ".codex-plugin" / "plugin.json").write_text("{}")
    (tmp_path / "README.md").write_text("# Demo\n")

    model = detect_release_model(tmp_path, "demo release")

    assert model["product_id"] == tmp_path.name
    assert "python-package" in model["artifact_types"]
    assert "eidos-plugin" in model["artifact_types"]
    assert "Eidos AGI marketplace" in model["distribution_channels"]
    assert "ship-forge" in model["forge_stack"]


def test_detects_eidos_store_route_for_plugin_project(tmp_path: Path) -> None:
    marketplace = tmp_path / "eidos-marketplace"
    marketplace.mkdir()
    plugin = tmp_path / "demo-plugin"
    plugin.mkdir()
    (plugin / "pyproject.toml").write_text("[project]\nname='demo-plugin'\n")
    (plugin / ".codex-plugin").mkdir()
    (plugin / ".codex-plugin" / "plugin.json").write_text('{"name": "demo-plugin"}')

    model = detect_release_model(plugin)

    assert model["release_routes"] == [
        {
            "id": "eidos-plugin-store",
            "channel": "Eidos AGI marketplace",
            "owner": "eidos-plugin-store",
            "tool": "eidos-marketplace/tools/marketplace_publish.py",
            "intent": "handoff plugin releases to the standard Eidos store publishing path",
            "handoff": {
                "target_project": str(marketplace),
                "source_project": str(plugin),
                "commands": [
                    (
                        f"cd {marketplace} && python3 tools/marketplace_publish.py "
                        f"publish {plugin} --audit-date <YYYY-MM-DD>"
                    ),
                    (
                        f"cd {marketplace} && python3 tools/marketplace_publish.py "
                        f"check demo-plugin --source {plugin}"
                    ),
                    "codex plugin add demo-plugin@eidos-agi",
                    "codex plugin list --marketplace eidos-agi | rg demo-plugin",
                ],
                "proofs": [
                    "marketplace publish command completed",
                    "marketplace check passed",
                    "store branch/PR merged into main",
                    "Codex install/list proof sees the plugin from eidos-agi",
                ],
            },
            "approval_gate": "public marketplace merge/publish remains explicit-human-approved",
        }
    ]


def test_write_model_and_frontier(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    path = write_release_model(tmp_path, detect_release_model(tmp_path))

    assert path.exists()
    frontier = release_frontier(tmp_path)
    assert frontier["status"] == "model_ready"
    assert frontier["attempt_count"] == 0


def test_record_attempt_uses_model_snapshot(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    write_release_model(tmp_path, detect_release_model(tmp_path))

    path, attempt = record_attempt(
        tmp_path,
        goal="ship demo",
        status="planned",
        proofs=["pytest -q"],
    )

    assert path.exists()
    assert attempt["goal"] == "ship demo"
    assert attempt["proofs"] == ["pytest -q"]
    assert json.loads(path.read_text())["release_model_snapshot"]["artifact_types"]


def test_frontier_uses_latest_ready_attempt_next_actions(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    write_release_model(tmp_path, detect_release_model(tmp_path))

    record_attempt(tmp_path, goal="prove demo", status="ready")
    frontier = release_frontier(tmp_path)

    assert frontier["latest_status"] == "ready"
    assert frontier["next_actions"] == [
        "request explicit human approval for public publish/deploy if needed",
        "record shipped or rolled_back after the irreversible step",
    ]


def test_frontier_routes_ready_plugin_to_standard_store_path(tmp_path: Path) -> None:
    marketplace = tmp_path / "eidos-marketplace"
    marketplace.mkdir()
    plugin = tmp_path / "demo-plugin"
    plugin.mkdir()
    (plugin / "pyproject.toml").write_text("[project]\nname='demo-plugin'\n")
    (plugin / ".codex-plugin").mkdir()
    (plugin / ".codex-plugin" / "plugin.json").write_text('{"name": "demo-plugin"}')
    write_release_model(plugin, detect_release_model(plugin))

    path, attempt = record_attempt(plugin, goal="ready for store", status="ready")
    frontier = release_frontier(plugin)

    assert path.exists()
    assert attempt["release_model_snapshot"]["release_routes"][0]["id"] == "eidos-plugin-store"
    assert attempt["next_actions"] == [
        "handoff to eidos-plugin-store using the standard marketplace_publish.py publish path",
        "verify store entry with marketplace_publish.py check and codex plugin install/list proof",
        "after explicit approval, merge the store PR and record shipped with PR + install proof",
    ]
    assert frontier["next_actions"] == attempt["next_actions"]


def test_summarizes_eidos_ship_report() -> None:
    report = {
        "ok": False,
        "repo": "/tmp/demo",
        "manifest": "/tmp/demo/.eidos/ship/manifest.toml",
        "shipment_style": "demo",
        "gates": [
            {"id": "git-clean-pushed", "facet": "workspace", "status": "fail", "ok": False},
            {
                "id": "node-build",
                "facet": "node",
                "status": "pass",
                "ok": True,
                "command": ["npm", "run", "build"],
            },
        ],
    }

    summary = summarize_eidos_ship_report(report)

    assert summary["status"] == "blocked"
    assert summary["blockers"] == ["git-clean-pushed"]
    assert summary["blocker_records"] == [
        {
            "id": "git-clean-pushed",
            "category": "workspace-hygiene",
            "owner": "release operator",
            "tool": "git",
            "severity": "high",
            "suggested_next_action": (
                "clean or isolate the workspace, confirm upstream state, then rerun eidos ship"
            ),
            "facet": "workspace",
        }
    ]
    assert summary["goal"] == "Run eidos ship for demo"
    assert summary["proofs"] == ["npm run build"]
    assert summary["source"]["tool"] == "eidos ship"


def test_record_eidos_ship_attempt_preserves_gate_summary(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"scripts":{"build":"echo ok"}}')
    write_release_model(tmp_path, detect_release_model(tmp_path))
    report = {
        "ok": False,
        "repo": str(tmp_path),
        "gates": [
            {
                "id": "node-validate",
                "facet": "node",
                "status": "pass",
                "ok": True,
                "command": ["npm", "run", "validate:capabilities"],
            },
            {"id": "git-clean-pushed", "facet": "workspace", "status": "fail", "ok": False},
        ],
    }

    path, attempt = record_eidos_ship_attempt(tmp_path, report)
    frontier = release_frontier(tmp_path)

    assert path.exists()
    assert attempt["status"] == "blocked"
    assert attempt["blockers"] == ["git-clean-pushed"]
    assert attempt["blocker_records"][0]["category"] == "workspace-hygiene"
    assert attempt["blocker_records"][0]["owner"] == "release operator"
    assert attempt["blocker_records"][0]["tool"] == "git"
    assert attempt["gate_summary"][0]["id"] == "node-validate"
    assert attempt["source"]["tool"] == "eidos ship"
    assert frontier["latest_status"] == "blocked"
    assert frontier["latest_blockers"] == ["git-clean-pushed"]
    assert frontier["latest_blocker_records"][0]["category"] == "workspace-hygiene"
    assert frontier["next_actions"] == [
        "workspace-hygiene blocker git-clean-pushed: clean or isolate the workspace, "
        "confirm upstream state, then rerun eidos ship (release operator via git)"
    ]


def test_eidos_ship_custom_blocker_gets_fallback_classification() -> None:
    report = {
        "ok": False,
        "repo": "/tmp/demo",
        "gates": [
            {
                "id": "custom-license-check",
                "facet": "legal",
                "status": "fail",
                "ok": False,
                "detail": "license notice missing",
            }
        ],
    }

    summary = summarize_eidos_ship_report(report)

    assert summary["blocker_records"] == [
        {
            "id": "custom-license-check",
            "category": "custom-gate",
            "owner": "release operator",
            "tool": "eidos ship",
            "severity": "medium",
            "suggested_next_action": (
                "inspect the gate detail, route to the owning tool, then rerun eidos ship"
            ),
            "facet": "legal",
            "detail": "license notice missing",
        }
    ]


def test_frontier_surfaces_recurring_blockers(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"scripts":{"build":"vite build"}}')
    write_release_model(tmp_path, detect_release_model(tmp_path))
    report = {
        "ok": False,
        "repo": str(tmp_path),
        "gates": [
            {
                "id": "node-build",
                "facet": "node",
                "status": "fail",
                "ok": False,
                "command": ["npm", "run", "build"],
            }
        ],
    }

    record_eidos_ship_attempt(tmp_path, report, goal="first blocked build")
    record_eidos_ship_attempt(tmp_path, report, goal="second blocked build")
    frontier = release_frontier(tmp_path)

    assert frontier["latest_blocker_records"][0]["category"] == "build"
    assert frontier["latest_blocker_records"][0]["owner"] == "node maintainer"
    assert frontier["recurring_blockers"] == [
        {
            "id": "node-build",
            "count": 2,
            "category": "build",
            "owner": "node maintainer",
            "tool": "npm",
            "severity": "high",
            "suggested_next_action": (
                "run the Node build command locally and fix the first build failure"
            ),
        }
    ]
    assert frontier["next_actions"][-1] == (
        "recurring blocker node-build seen 2 attempts: "
        "promote to durable gate repair with node maintainer via npm"
    )


def test_write_model_ignores_shipr_memory_in_git_project(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")

    write_release_model(tmp_path, detect_release_model(tmp_path))

    assert ".shipr/" in (tmp_path / ".gitignore").read_text().splitlines()


def test_record_attempt_does_not_duplicate_shipr_ignore(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitignore").write_text("node_modules/\n.shipr/\n")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")

    record_attempt(tmp_path, goal="ship demo")

    assert (tmp_path / ".gitignore").read_text().splitlines().count(".shipr/") == 1


def test_ensure_shipr_ignored_leaves_non_git_project_alone(tmp_path: Path) -> None:
    assert ensure_shipr_ignored(tmp_path) is None
    assert not (tmp_path / ".gitignore").exists()
