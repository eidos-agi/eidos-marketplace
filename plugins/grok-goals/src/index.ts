#!/usr/bin/env node
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { resolvePackPath } from "./paths.js";
import { createGoalsServer } from "./server.js";

async function main(): Promise<void> {
  const packRoot = resolvePackPath();
  const { server } = await createGoalsServer({ packRoot });
  await server.connect(new StdioServerTransport());
  console.error(`grok-goals mcp ready (pack: ${packRoot})`);
}

main().catch((error: unknown) => {
  console.error(error);
  process.exit(1);
});
