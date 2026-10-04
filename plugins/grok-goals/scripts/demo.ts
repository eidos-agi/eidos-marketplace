import { rm } from "node:fs/promises";
import { join } from "node:path";
import type { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { validatePack } from "../src/pack-check.js";
import { readToolPayload } from "../src/result.js";
import { packageRoot } from "../src/root.js";
import { connectGoalsClient } from "../src/session.js";
import type { Goal } from "../src/types.js";

const demoRoot = join(packageRoot, "data", "demo.prim");

async function callTool(
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

function asGoal(payload: Record<string, unknown>): Goal {
  return payload.goal as Goal;
}

async function createHalf(client: Client): Promise<Goal> {
  const payload = await callTool(client, "goals_create", {
    title: "Train for a half marathon by March",
    objective:
      "Finish a half marathon in March. Build the mileage, keep the long run, and show up on race day.",
    acceptance_criteria: [
      "Long run reaches 13.1 miles at least once before race week",
      "Finish the March half marathon",
      "No two consecutive weeks skip the long run",
    ],
    category: "health",
    status: "active",
    owner_bot: "GrokGoals",
    plan_steps: [
      { title: "Pick the March race and write the weekly mileage", owner: "user" },
      { title: "Build the long run to 10 miles", owner: "user" },
      { title: "Taper for two weeks and run the race", owner: "user" },
    ],
  });
  return asGoal(payload);
}

async function showListAndGet(client: Client, id: string): Promise<void> {
  const listed = await callTool(client, "goals_list", { status: "active", category: "health" });
  const goals = listed.goals as Goal[];
  const match = goals.find((goal) => goal.id === id);
  if (!match) throw new Error("Active list did not include the new goal.");
  const fetched = asGoal(await callTool(client, "goals_get", { id }));
  console.log(`list active: ${goals.length} goal, title "${fetched.title}"`);
  console.log(`get: ${fetched.plan_steps.length} plan steps, status ${fetched.status}`);
}

async function recordPauseComplete(client: Client, goal: Goal): Promise<Goal> {
  const first = goal.plan_steps[0];
  if (!first) throw new Error("Expected a plan step.");
  const recorded = await callTool(client, "goals_record_progress", {
    id: goal.id,
    summary: "Picked the first Sunday in March and wrote a 12-week mileage sketch.",
    next_action: {
      summary: "Run the first easy week: three short runs, nothing heroic.",
      owner: "user",
      due: "2026-10-04",
    },
    step_updates: [{ id: first.id, status: "done" }],
  });
  const progressed = asGoal(recorded);
  console.log(`progress: ${progressed.last_progress?.summary}`);
  console.log(`next: ${progressed.next_action?.summary}`);
  const paused = asGoal(await callTool(client, "goals_update", { id: goal.id, status: "paused" }));
  console.log(`pause: status ${paused.status}, progress kept`);
  const completed = asGoal(
    await callTool(client, "goals_update", { id: goal.id, status: "completed" }),
  );
  console.log(`complete: status ${completed.status}, journal still on disk`);
  return completed;
}

async function main(): Promise<void> {
  await rm(demoRoot, { recursive: true, force: true });
  const session = await connectGoalsClient(demoRoot);
  try {
    const created = await createHalf(session.client);
    console.log(`created ${created.id} "${created.title}" (${created.status})`);
    await showListAndGet(session.client, created.id);
    const completed = await recordPauseComplete(session.client, created);
    if (completed.status !== "completed" || !completed.last_progress) {
      throw new Error("Completed goal lost its progress.");
    }
    const sample = await validatePack(join(packageRoot, "examples", "grok-goals.prim"));
    console.log(`sample pack: ${sample.goalCount} goals`);
    for (const title of sample.titles) console.log(`- ${title}`);
    console.log(`demo pack: ${demoRoot}`);
  } finally {
    await session.close();
  }
}

main().catch((error: unknown) => {
  console.error(error);
  process.exit(1);
});
