import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";
import { packageRoot } from "../src/root.js";
import { TOOL_NAMES } from "../src/types.js";

test("tool docs name every MCP tool", () => {
  const openapi = JSON.parse(
    readFileSync(join(packageRoot, "docs", "tools.openapi.json"), "utf8"),
  ) as { paths: Record<string, unknown> };
  const plugin = JSON.parse(
    readFileSync(join(packageRoot, "docs", "grok-bot-plugin.json"), "utf8"),
  ) as { tools: string[] };
  const markdown = readFileSync(join(packageRoot, "docs", "tools.md"), "utf8");
  for (const name of TOOL_NAMES) {
    assert.ok(openapi.paths[`/tools/${name}`], `openapi missing ${name}`);
    assert.ok(markdown.includes(name), `tools.md missing ${name}`);
  }
  assert.deepEqual(plugin.tools, [...TOOL_NAMES]);
});
