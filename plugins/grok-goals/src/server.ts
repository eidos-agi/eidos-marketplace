import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerTools } from "./register-tools.js";
import { GoalStore } from "./store.js";
import { SERVER_NAME, SERVER_VERSION } from "./version.js";

const INSTRUCTIONS = [
  "Grok Goals stores durable goals for a Grok Bot: plan, progress, next action, and approval gates.",
  "Do not expect this server to invent a plan or take an action.",
  "Before send, spend, post, or delete, read approval_policy. ask means stop and confirm. deny means refuse. auto means the bot may proceed.",
  "Pause, block, abandon, and complete keep the goal document. Nothing here deletes a goal.",
].join(" ");

export async function createGoalsServer(options: { packRoot: string }): Promise<{
  server: McpServer;
  store: GoalStore;
}> {
  const store = new GoalStore(options.packRoot);
  await store.init();
  const server = new McpServer(
    { name: SERVER_NAME, version: SERVER_VERSION },
    { instructions: INSTRUCTIONS },
  );
  registerTools(server, store);
  return { server, store };
}
