import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  createInput,
  getInput,
  goalToolOutput,
  listInput,
  listOutput,
  policyToolInput,
  progressInput,
  progressOutput,
  updateInput,
} from "./mcp-schemas.js";
import { errorResult, okResult } from "./result.js";
import type { GoalStore } from "./store.js";

const readOnly = {
  readOnlyHint: true,
  destructiveHint: false,
  idempotentHint: true,
  openWorldHint: false,
};

const writes = {
  readOnlyHint: false,
  destructiveHint: false,
  idempotentHint: false,
  openWorldHint: false,
};

function guard<T>(run: (args: T) => Promise<object>): (args: T) => Promise<CallToolResult> {
  return async (args) => {
    try {
      return okResult(await run(args));
    } catch (error) {
      return errorResult(error);
    }
  };
}

export function registerTools(server: McpServer, store: GoalStore): void {
  registerReads(server, store);
  registerWrites(server, store);
}

function registerReads(server: McpServer, store: GoalStore): void {
  server.registerTool(
    "goals_list",
    {
      title: "List goals",
      description:
        "List goals in this pack. Filter by status, category, or both. Returns full goal documents, newest update first.",
      inputSchema: listInput,
      outputSchema: listOutput,
      annotations: readOnly,
    },
    guard(async (args) => ({ goals: await store.list(args) })),
  );

  server.registerTool(
    "goals_get",
    {
      title: "Get goal",
      description:
        "Fetch one goal by id, including its plan, latest progress, next action, and approval policy.",
      inputSchema: getInput,
      outputSchema: goalToolOutput,
      annotations: readOnly,
    },
    guard(async ({ id }) => ({ goal: await store.get(id) })),
  );
}

function registerWrites(server: McpServer, store: GoalStore): void {
  registerCreateAndUpdate(server, store);
  registerProgressAndPolicy(server, store);
}

function registerCreateAndUpdate(server: McpServer, store: GoalStore): void {
  server.registerTool(
    "goals_create",
    {
      title: "Create goal",
      description:
        "Create a goal in draft or active status. Pass the plan steps you already have; this server does not invent them. Omitted approval gates default to ask.",
      inputSchema: createInput,
      outputSchema: goalToolOutput,
      annotations: writes,
    },
    guard(async (args) => ({ goal: await store.create(args) })),
  );

  server.registerTool(
    "goals_update",
    {
      title: "Update goal",
      description:
        "Patch a goal. plan_steps replaces the whole list. Pass null for category, next_action, or owner_bot to clear it. Status can move to paused, blocked, completed, or abandoned; the document stays. Does not change approval gates.",
      inputSchema: updateInput,
      outputSchema: goalToolOutput,
      annotations: writes,
    },
    guard(async ({ id, ...patch }) => ({ goal: await store.update(id, patch) })),
  );
}

function registerProgressAndPolicy(server: McpServer, store: GoalStore): void {
  server.registerTool(
    "goals_record_progress",
    {
      title: "Record progress",
      description:
        "Record a meaningful advance. Sets last_progress, appends progress/<id>.jsonl, and can replace next_action or update plan steps by id. Null next_action clears it. Does not change goal status.",
      inputSchema: progressInput,
      outputSchema: progressOutput,
      annotations: writes,
    },
    guard(async (args) => {
      const recorded = await store.recordProgress(args);
      return { goal: recorded.goal, progress_entry: recorded.progress_entry };
    }),
  );

  server.registerTool(
    "goals_set_approval_policy",
    {
      title: "Set approval policy",
      description:
        "Set the gates for send, spend, post, and delete. Each is auto, ask, or deny. Omitted gates stay put. This only stores the policy; it never sends, spends, posts, or deletes.",
      inputSchema: policyToolInput,
      outputSchema: goalToolOutput,
      annotations: writes,
    },
    guard(async ({ id, ...gates }) => ({ goal: await store.setApprovalPolicy(id, gates) })),
  );
}
