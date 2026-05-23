import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import test_plugins


def test_server_configs_accepts_mcpservers_shape() -> None:
    config = {
        "mcpServers": {
            "foreman": {
                "command": "python3",
                "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/mcp_server.py"],
            }
        }
    }

    [(name, server)] = test_plugins.server_configs(config)

    assert name == "foreman"
    assert server["command"] == "python3"


def test_expand_plugin_root_resolves_marketplace_bundle_paths(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugins" / "foreman"

    assert test_plugins.expand_plugin_root(
        "${CLAUDE_PLUGIN_ROOT}/scripts/mcp_server.py", plugin_dir
    ) == str(plugin_dir / "scripts" / "mcp_server.py")


def test_research_md_marketplace_uses_mcp_serve_command() -> None:
    mcp_config = json.loads((test_plugins.PLUGINS_DIR / "research-md" / ".mcp.json").read_text())

    [(name, server)] = test_plugins.server_configs(mcp_config)

    assert name == "research-md"
    assert server["command"] == "uvx"
    assert server["args"] == ["--from", "research-md", "research-md", "mcp", "serve"]


def test_resume_resume_marketplace_declares_runtime_extras() -> None:
    mcp_config = json.loads((test_plugins.PLUGINS_DIR / "resume-resume" / ".mcp.json").read_text())

    [(name, server)] = test_plugins.server_configs(mcp_config)

    assert name == "resume-resume"
    assert server["command"] == "uvx"
    assert server["args"] == [
        "--from",
        "resume-resume",
        "--with",
        "scipy",
        "--with",
        "scikit-learn",
        "--with",
        "pandas",
        "resume-resume-mcp",
    ]
