#!/usr/bin/env python3
"""Test all plugins in the Eidos marketplace.

For each plugin, reads .mcp.json, starts the MCP server via the configured
command, sends an MCP initialize handshake, and verifies the server responds
with capabilities. Reports pass/fail for each plugin.

Usage:
    python tools/test_plugins.py              # test all plugins
    python tools/test_plugins.py resume-resume ike  # test specific plugins
"""

import json
import subprocess
import sys
import time
from pathlib import Path

MARKETPLACE_ROOT = Path(__file__).parent.parent
PLUGINS_DIR = MARKETPLACE_ROOT / "plugins"
TIMEOUT_SECONDS = 90  # uvx first-run can be slow


def mcp_initialize_request() -> bytes:
    """Build an MCP initialize JSON-RPC request (raw JSON, newline-delimited)."""
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "eidos-plugin-tester", "version": "0.1.0"},
        },
    })
    return (payload + "\n").encode()


def read_mcp_response(proc, timeout: float) -> dict | None:
    """Read an MCP JSON-RPC response line from stdout."""
    import selectors

    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ)

    buf = b""
    deadline = time.time() + timeout

    while time.time() < deadline:
        remaining = deadline - time.time()
        events = sel.select(timeout=min(remaining, 1.0))
        if not events:
            continue
        chunk = proc.stdout.read1(4096) if hasattr(proc.stdout, "read1") else proc.stdout.read(4096)
        if not chunk:
            break
        buf += chunk
        # Try to parse each complete line as JSON
        if b"\n" in buf:
            for line in buf.split(b"\n"):
                line = line.strip()
                if not line:
                    continue
                # Skip Content-Length headers if present
                if line.startswith(b"Content-Length"):
                    continue
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue

    sel.close()
    return None


def test_plugin(plugin_dir: Path) -> dict:
    """Test a single plugin. Returns result dict."""
    name = plugin_dir.name
    mcp_file = plugin_dir / ".mcp.json"

    if not mcp_file.exists():
        return {"name": name, "status": "skip", "reason": "no .mcp.json"}

    try:
        mcp_config = json.loads(mcp_file.read_text())
    except json.JSONDecodeError as e:
        return {"name": name, "status": "fail", "reason": f"invalid .mcp.json: {e}"}

    # Get the first server config
    servers = list(mcp_config.items())
    if not servers:
        return {"name": name, "status": "skip", "reason": "empty .mcp.json"}

    server_name, config = servers[0]
    command = config.get("command", "")
    args = config.get("args", [])
    full_cmd = [command] + args

    result = {"name": name, "command": " ".join(full_cmd), "status": "fail"}

    # Start the server
    try:
        proc = subprocess.Popen(
            full_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        result["reason"] = f"command not found: {command}"
        return result
    except OSError as e:
        result["reason"] = f"failed to start: {e}"
        return result

    try:
        # Send initialize request
        proc.stdin.write(mcp_initialize_request())
        proc.stdin.flush()

        # Read response
        response = read_mcp_response(proc, timeout=TIMEOUT_SECONDS)

        if response is None:
            stderr = proc.stderr.read(2000).decode(errors="replace").strip()
            result["reason"] = f"no MCP response"
            if stderr:
                result["stderr"] = stderr[:500]
            return result

        if "result" in response:
            caps = response["result"].get("capabilities", {})
            server_info = response["result"].get("serverInfo", {})
            result["status"] = "pass"
            result["server"] = server_info.get("name", "unknown")
            result["version"] = server_info.get("version", "unknown")
            result["capabilities"] = list(caps.keys())
        elif "error" in response:
            result["reason"] = f"MCP error: {response['error']}"
        else:
            result["reason"] = f"unexpected response: {json.dumps(response)[:200]}"

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    return result


def main():
    # Find plugins to test
    if len(sys.argv) > 1:
        plugin_names = sys.argv[1:]
        plugin_dirs = [PLUGINS_DIR / name for name in plugin_names]
    else:
        plugin_dirs = sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir())

    print(f"Testing {len(plugin_dirs)} plugins...\n")

    results = []
    for plugin_dir in plugin_dirs:
        if not plugin_dir.exists():
            print(f"  {plugin_dir.name:20s}  SKIP  (directory not found)")
            continue

        print(f"  {plugin_dir.name:20s}  ", end="", flush=True)
        start = time.time()
        result = test_plugin(plugin_dir)
        elapsed = time.time() - start
        result["elapsed"] = round(elapsed, 1)
        results.append(result)

        if result["status"] == "pass":
            print(f"PASS  {result['server']} v{result['version']}  ({elapsed:.1f}s)")
        elif result["status"] == "skip":
            print(f"SKIP  {result['reason']}")
        else:
            print(f"FAIL  {result['reason']}")
            if "stderr" in result:
                for line in result["stderr"].split("\n")[:3]:
                    print(f"               {line}")

    # Summary
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    skipped = sum(1 for r in results if r["status"] == "skip")
    print(f"\n{'='*60}")
    print(f"  {passed} passed  {failed} failed  {skipped} skipped  ({len(results)} total)")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
