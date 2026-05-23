import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import marketplace_publish


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


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
