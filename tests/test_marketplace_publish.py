import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import marketplace_publish

REPO_ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def test_codex_marketplace_is_single_eidos_agi_store() -> None:
    marketplace_path = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
    marketplace = json.loads(marketplace_path.read_text())

    assert marketplace["name"] == "eidos-agi"
    assert marketplace["interface"]["displayName"] == "Eidos AGI"
    assert all(entry["source"]["source"] == "local" for entry in marketplace["plugins"])
    assert all(
        entry["source"]["path"].startswith("./plugins/") for entry in marketplace["plugins"]
    )

    plugin_names = [entry["name"] for entry in marketplace["plugins"]]
    assert plugin_names == sorted(plugin_names)
    assert "eidos-plugin-store" in plugin_names

    for entry in marketplace["plugins"]:
        plugin_root = REPO_ROOT / entry["source"]["path"].removeprefix("./")
        codex_manifest = plugin_root / ".codex-plugin" / "plugin.json"
        claude_manifest = plugin_root / ".claude-plugin" / "plugin.json"
        assert codex_manifest.exists() or claude_manifest.exists(), (
            f"missing plugin manifest for {entry['name']}"
        )
        manifest = codex_manifest if codex_manifest.exists() else claude_manifest
        plugin_manifest = json.loads(manifest.read_text())
        assert plugin_manifest["name"] == entry["name"]

    catalog_manifest = json.loads(
        (REPO_ROOT / "plugins" / "eidos-plugin-store" / ".codex-plugin" / "plugin.json").read_text()
    )
    assert catalog_manifest["interface"]["displayName"] == "Eidos AGI Catalog"
    assert "not a separate store" in catalog_manifest["interface"]["longDescription"]


def test_marketplace_entries_resolve_to_bundles() -> None:
    for marketplace_path in (
        REPO_ROOT / ".agents" / "plugins" / "marketplace.json",
        REPO_ROOT / ".claude-plugin" / "marketplace.json",
    ):
        marketplace = json.loads(marketplace_path.read_text())
        for entry in marketplace["plugins"]:
            source = entry["source"]["path"] if isinstance(entry["source"], dict) else entry["source"]
            assert isinstance(source, str), f"invalid source for {entry['name']}"
            assert source.startswith("./plugins/"), f"invalid source for {entry['name']}"
            assert (REPO_ROOT / source.removeprefix("./")).exists(), (
                f"missing plugin bundle for {entry['name']}"
            )


def test_zoltar_is_dual_host_and_host_neutral() -> None:
    codex_marketplace = json.loads(
        (REPO_ROOT / ".agents" / "plugins" / "marketplace.json").read_text()
    )
    claude_marketplace = json.loads(
        (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text()
    )
    plugin_root = REPO_ROOT / "plugins" / "zoltar"

    codex_names = {entry["name"] for entry in codex_marketplace["plugins"]}
    claude_names = {entry["name"] for entry in claude_marketplace["plugins"]}
    assert "zoltar" in codex_names
    assert "zoltar" in claude_names
    assert (plugin_root / ".codex-plugin" / "plugin.json").exists()
    assert (plugin_root / ".claude-plugin" / "plugin.json").exists()

    codex_manifest = json.loads((plugin_root / ".codex-plugin" / "plugin.json").read_text())
    claude_manifest = json.loads((plugin_root / ".claude-plugin" / "plugin.json").read_text())
    assert codex_manifest["name"] == claude_manifest["name"] == "zoltar"
    assert codex_manifest["version"] == claude_manifest["version"]
    assert codex_manifest["skills"] == claude_manifest["skills"] == "./skills/"
    assert "interface" in codex_manifest
    assert "interface" not in claude_manifest


def test_zoltar_documents_preflight_and_assumption_contract() -> None:
    plugin_root = REPO_ROOT / "plugins" / "zoltar"
    readme = (plugin_root / "README.md").read_text()
    research_skill = (plugin_root / "skills" / "research-futures" / "SKILL.md").read_text()
    predict_skill = (plugin_root / "skills" / "predict-futures" / "SKILL.md").read_text()

    assert "## Use As A Preflight" in readme
    assert "## Minimum Evidence Pack" in readme
    assert "## Usage Assumptions" in readme
    assert "ship" in readme and "revise" in readme and "block" in readme
    assert "assumption-backed" in readme
    assert "## Preflight Mode" in research_skill
    assert "Do not imply Zoltar ran automatically" in research_skill
    assert "## Assumption Check" in predict_skill
    assert "Do not convert an unchecked assumption into a confident future" in predict_skill


def test_storemetheus_ships_dual_host_maintenance_skill() -> None:
    plugin_root = REPO_ROOT / "plugins" / "eidos-storemetheus"
    skill = plugin_root / "skills" / "maintain-dual-host-marketplace" / "SKILL.md"
    assert skill.exists()

    codex_manifest = json.loads((plugin_root / ".codex-plugin" / "plugin.json").read_text())
    claude_manifest = json.loads((plugin_root / ".claude-plugin" / "plugin.json").read_text())
    assert codex_manifest["version"] == claude_manifest["version"] == "0.1.1"
    assert codex_manifest["skills"] == claude_manifest["skills"] == "./skills/"

    body = skill.read_text()
    assert ".claude-plugin/plugin.json" in body
    assert ".codex-plugin/plugin.json" in body
    assert ".claude-plugin/marketplace.json" in body
    assert ".agents/plugins/marketplace.json" in body


def test_published_bundles_do_not_include_runtime_or_proof_noise() -> None:
    blocked_parts = {".git", ".venv", ".pytest_cache", ".ruff_cache", "__pycache__"}
    tracked = subprocess.check_output(
        ["git", "ls-files", "plugins"], cwd=REPO_ROOT, text=True
    ).splitlines()
    for tracked_path in tracked:
        path = Path(tracked_path)
        assert not (blocked_parts & set(path.parts)), f"runtime artifact in bundle: {path}"
        assert not path.name.endswith(".jsonl"), f"proof log in bundle: {path}"


def test_publish_renders_plugin_bundle_and_marketplace_entry(tmp_path: Path) -> None:
    marketplace = tmp_path / "marketplace"
    source = tmp_path / "source" / "felix"
    write_json(
        marketplace / ".claude-plugin" / "marketplace.json",
        {"name": "eidos-marketplace", "plugins": []},
    )
    write_json(
        source / ".codex-plugin" / "plugin.json",
        {
            "name": "felix",
            "version": "0.1.0",
            "description": "Use the live Felix CLI to build, assess, and maintain agent ecosystems.",
            "homepage": "https://github.com/eidos-agi/felix",
            "repository": "https://github.com/eidos-agi/felix",
            "license": "MIT",
            "keywords": ["felix", "agent-builder"],
            "skills": "./skills/",
            "interface": {"category": "Productivity"},
        },
    )
    (source / "skills" / "use-felix-cli").mkdir(parents=True)
    (source / "skills" / "use-felix-cli" / "SKILL.md").write_text("# Use Felix\n")

    report = marketplace_publish.publish(source, marketplace, audit_date="2026-05-23")

    assert report.name == "felix"
    assert (marketplace / "plugins" / "felix" / ".codex-plugin" / "plugin.json").exists()
    assert (marketplace / "plugins" / "felix" / ".claude-plugin" / "plugin.json").exists()
    assert (marketplace / "plugins" / "felix" / "skills" / "use-felix-cli" / "SKILL.md").exists()
    assert (marketplace / "AUDITS" / "felix.md").exists()

    marketplace_json = json.loads((marketplace / ".claude-plugin" / "marketplace.json").read_text())
    [entry] = marketplace_json["plugins"]
    assert entry["name"] == "felix"
    assert entry["source"] == "./plugins/felix"
    assert entry["homepage"] == "https://github.com/eidos-agi/felix"
    assert entry["x-eidos"]["kind"]["type"] == "forge"
    assert entry["x-eidos"]["audit"]["audit_doc"] == "AUDITS/felix.md"


def test_publish_uses_eidos_plugin_recommend_override(tmp_path: Path) -> None:
    marketplace = tmp_path / "marketplace"
    source = tmp_path / "source" / "shipr"
    write_json(
        marketplace / ".claude-plugin" / "marketplace.json",
        {"name": "eidos-marketplace", "plugins": []},
    )
    write_json(
        source / ".codex-plugin" / "plugin.json",
        {
            "name": "shipr",
            "version": "0.1.0",
            "description": "Persistent Eidos shipping operator.",
            "homepage": "https://github.com/eidos-agi/shipr",
            "license": "MIT",
            "skills": "./skills/",
        },
    )
    write_json(
        source / ".eidos-plugin.json",
        {
            "kind": {
                "type": "forge",
                "signals": ["ships_skills", "coordinates_with_other_forges"],
            },
            "recommend": {
                "for_projects": ["release", "shipping"],
                "pairs_with": ["forge-forge", "ship-forge", "learning-forge"],
                "preflight_check": "shipr frontier --json",
            },
        },
    )
    (source / "skills" / "use-shipr").mkdir(parents=True)
    (source / "skills" / "use-shipr" / "SKILL.md").write_text("# Use Shipr\n")

    marketplace_publish.publish(source, marketplace, audit_date="2026-06-11")

    marketplace_json = json.loads((marketplace / ".claude-plugin" / "marketplace.json").read_text())
    [entry] = marketplace_json["plugins"]
    assert entry["x-eidos"]["recommend"]["pairs_with"] == [
        "forge-forge",
        "ship-forge",
        "learning-forge",
    ]
    assert entry["x-eidos"]["recommend"]["preflight_check"] == "shipr frontier --json"


def test_check_fails_when_marketplace_entry_points_to_missing_bundle(tmp_path: Path) -> None:
    marketplace = tmp_path / "marketplace"
    write_json(
        marketplace / ".claude-plugin" / "marketplace.json",
        {
            "name": "eidos-marketplace",
            "plugins": [{"name": "foreman", "source": "./plugins/foreman"}],
        },
    )

    report = marketplace_publish.check("foreman", marketplace)

    assert not report.ok
    assert "missing plugin directory: plugins/foreman" in report.blockers


def test_publish_normalizes_source_repo_mcp_paths_to_plugin_root(tmp_path: Path) -> None:
    marketplace = tmp_path / "marketplace"
    source = tmp_path / "source" / "foreman"
    write_json(
        marketplace / ".claude-plugin" / "marketplace.json",
        {"name": "eidos-marketplace", "plugins": []},
    )
    write_json(
        source / ".claude-plugin" / "plugin.json",
        {
            "name": "foreman",
            "version": "0.3.1",
            "description": "Delegate scoped coding work to AI engineer workers.",
            "homepage": "https://github.com/eidos-agi/foreman",
            "license": "MIT",
            "skills": "./skills/",
            "mcpServers": {
                "foreman": {
                    "command": "python3",
                    "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/mcp_server.py"],
                }
            },
        },
    )
    write_json(
        source / ".mcp.json",
        {
            "mcpServers": {
                "foreman": {
                    "command": "python3",
                    "args": [str(source / "scripts" / "mcp_server.py")],
                }
            }
        },
    )
    (source / "scripts").mkdir(parents=True)
    (source / "scripts" / "mcp_server.py").write_text("print('ok')\n")
    (source / "skills" / "delegate-with-foreman").mkdir(parents=True)
    (source / "skills" / "delegate-with-foreman" / "SKILL.md").write_text("# Delegate\n")

    marketplace_publish.publish(source, marketplace, audit_date="2026-05-23")

    mcp_json = json.loads((marketplace / "plugins" / "foreman" / ".mcp.json").read_text())
    assert mcp_json["mcpServers"]["foreman"]["args"] == [
        "${CLAUDE_PLUGIN_ROOT}/scripts/mcp_server.py"
    ]
    assert marketplace_publish.check("foreman", marketplace).ok


def test_check_with_source_fails_when_bundle_drifted_from_source(tmp_path: Path) -> None:
    marketplace = tmp_path / "marketplace"
    source = tmp_path / "source" / "felix"
    write_json(
        marketplace / ".claude-plugin" / "marketplace.json",
        {"name": "eidos-marketplace", "plugins": []},
    )
    write_json(
        source / ".codex-plugin" / "plugin.json",
        {
            "name": "felix",
            "version": "0.1.0",
            "description": "Use the live Felix CLI.",
            "homepage": "https://github.com/eidos-agi/felix",
            "license": "MIT",
            "skills": "./skills/",
        },
    )
    (source / "skills" / "use-felix-cli").mkdir(parents=True)
    (source / "skills" / "use-felix-cli" / "SKILL.md").write_text("# Use Felix\n")
    marketplace_publish.publish(source, marketplace, audit_date="2026-05-23")

    (marketplace / "plugins" / "felix" / "skills" / "use-felix-cli" / "SKILL.md").write_text(
        "# Stale Felix\n"
    )

    report = marketplace_publish.check("felix", marketplace, source=source)

    assert not report.ok
    assert "bundle drift from source: skills/use-felix-cli/SKILL.md" in report.blockers


def test_check_with_source_ignores_python_cache_files(tmp_path: Path) -> None:
    marketplace = tmp_path / "marketplace"
    source = tmp_path / "source" / "foreman"
    write_json(
        marketplace / ".claude-plugin" / "marketplace.json",
        {"name": "eidos-marketplace", "plugins": []},
    )
    write_json(
        source / ".claude-plugin" / "plugin.json",
        {
            "name": "foreman",
            "version": "0.3.1",
            "description": "Delegate scoped coding work.",
            "homepage": "https://github.com/eidos-agi/foreman",
            "license": "MIT",
        },
    )
    (source / "packages" / "foreman-mcp" / "__pycache__").mkdir(parents=True)
    (source / "packages" / "foreman-mcp" / "__pycache__" / "noise.pyc").write_bytes(b"cache")
    (source / "packages" / "foreman-mcp" / "README.md").write_text("# MCP\n")
    marketplace_publish.publish(source, marketplace, audit_date="2026-05-23")

    report = marketplace_publish.check("foreman", marketplace, source=source)

    assert report.ok
