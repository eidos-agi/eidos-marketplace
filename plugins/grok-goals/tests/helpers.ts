import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { readToolPayload } from "../src/result.js";
import { connectGoalsClient } from "../src/session.js";
import type { Goal } from "../src/types.js";

export async function tempPack(): Promise<{ root: string; remove: () => Promise<void> }> {
  const root = await mkdtemp(join(tmpdir(), "grok-goals-"));
  return {
    root,
    remove: () => rm(root, { recursive: true, force: true }),
  };
}

export async function openClient(root: string): Promise<{
  client: Client;
  close: () => Promise<void>;
}> {
  return connectGoalsClient(root);
}

export async function callOk(
  client: Client,
  name: string,
  args: Record<string, unknown>,
): Promise<Record<string, unknown>> {
  const result = await client.callTool({ name, arguments: args });
  const payload = readToolPayload(result);
  if (result.isError || payload.ok !== true) {
    throw new Error(`${name} failed: ${JSON.stringify(payload)}`);
  }
  return payload;
}

export function asGoal(payload: Record<string, unknown>): Goal {
  return payload.goal as Goal;
}
