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
