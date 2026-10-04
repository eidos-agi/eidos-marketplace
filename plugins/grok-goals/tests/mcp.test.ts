import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import type { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { progressPath } from "../src/pack.js";
import { readToolPayload } from "../src/result.js";
import { TOOL_NAMES } from "../src/types.js";
import type { Goal } from "../src/types.js";
import { asGoal, callOk, openClient, tempPack } from "./helpers.js";

test("MCP tools create, list, get, record progress, pause, and complete", async () => {
  const pack = await tempPack();
  const session = await openClient(pack.root);
  try {
    const names = await listedTools(session.client);
    assert.deepEqual(names, [...TOOL_NAMES]);
    const goal = await createHalf(session.client);
    await assertListed(session.client, goal.id);
    const completed = await advance(session.client, goal);
    assert.equal(completed.status, "completed");
    assert.match(completed.last_progress?.summary ?? "", /12-week mileage/);
    const journal = await readFile(progressPath(pack.root, goal.id), "utf8");
    assert.equal(journal.trim().split("\n").length, 1);
    const active = (await callOk(session.client, "goals_list", { status: "active" })).goals as Goal[];
    assert.equal(active.some((item) => item.id === goal.id), false);
  } finally {
    await session.close();
    await pack.remove();
  }
});

async function listedTools(client: Client): Promise<string[]> {
  const listed = await client.listTools();
  return listed.tools.map((tool) => tool.name);
}

async function createHalf(client: Client): Promise<Goal> {
  const goal = asGoal(
    await callOk(client, "goals_create", {
      title: "Train for a half marathon by March",
      objective: "Finish a half marathon in March. Build the mileage and show up.",
      acceptance_criteria: [
        "Long run reaches 13.1 miles before race week",
        "Finish the March half marathon",
      ],
      category: "health",
      status: "active",
      plan_steps: [
        { title: "Pick the March race and write the weekly mileage", owner: "user" },
        { title: "Build the long run to 10 miles", owner: "user" },
        { title: "Taper for two weeks and run the race", owner: "user" },
      ],
    }),
  );
  assert.equal(goal.plan_steps.length, 3);
  assert.equal(goal.approval_policy.spend, "ask");
  assert.equal(goal.status, "active");
  return goal;
}

async function assertListed(client: Client, id: string): Promise<void> {
  const goals = (await callOk(client, "goals_list", { status: "active" })).goals as Goal[];
  assert.equal(goals.some((goal) => goal.id === id), true);
  const fetched = asGoal(await callOk(client, "goals_get", { id }));
  assert.equal(fetched.title, "Train for a half marathon by March");
}

async function advance(client: Client, goal: Goal): Promise<Goal> {
  const step = goal.plan_steps[0];
  assert.ok(step);
  const recorded = asGoal(
    await callOk(client, "goals_record_progress", {
      id: goal.id,
      summary: "Picked the first Sunday in March and wrote a 12-week mileage sketch.",
      next_action: {
        summary: "Run the first easy week: three short runs.",
        owner: "user",
        due: "2026-10-04",
      },
      step_updates: [{ id: step.id, status: "done" }],
    }),
  );
  assert.equal(recorded.status, "active");
  assert.equal(recorded.plan_steps[0]?.status, "done");
  assert.equal(recorded.next_action?.due, "2026-10-04");
  const paused = asGoal(await callOk(client, "goals_update", { id: goal.id, status: "paused" }));
  assert.equal(paused.status, "paused");
  assert.equal(paused.last_progress?.summary, recorded.last_progress?.summary);
  return asGoal(await callOk(client, "goals_update", { id: goal.id, status: "completed" }));
}

test("missing goals and bad creates return structured errors", async () => {
  const pack = await tempPack();
  const session = await openClient(pack.root);
  try {
    const missing = await session.client.callTool({
      name: "goals_get",
      arguments: { id: "00000000-0000-4000-8000-000000000000" },
    });
    assert.equal(missing.isError, true);
    const body = readToolPayload(missing);
    assert.equal(body.ok, false);
    assert.equal((body.error as { code: string }).code, "not_found");
    const blank = await session.client.callTool({
      name: "goals_create",
      arguments: { title: "   ", objective: "Finish a half marathon in March." },
    });
    assert.equal(blank.isError, true);
    const text = blank.content.find((item) => item.type === "text");
    assert.match(text && "text" in text ? text.text : "", /title/i);
  } finally {
    await session.close();
    await pack.remove();
  }
});
