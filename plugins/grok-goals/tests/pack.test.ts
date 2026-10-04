import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import test from "node:test";
import { packProduct } from "../src/product.js";
import { validatePack } from "../src/pack-check.js";
import { packageRoot } from "../src/root.js";
import { GoalStore } from "../src/store.js";
import { CATEGORIES, GATES, GOAL_STATUSES, OWNERS, STEP_STATUSES } from "../src/types.js";

const exampleRoot = join(packageRoot, "examples", "grok-goals.prim");

test("example Prim pack validates and loads", async () => {
  const before = await readFile(join(exampleRoot, "index.json"), "utf8");
  const report = await validatePack(exampleRoot);
  assert.deepEqual(report.titles, [
    "Ship quarterly invoice export",
    "Train for a half marathon by March",
  ]);
  const store = new GoalStore(exampleRoot);
  const goals = await store.list();
  assert.equal(goals.length, 2);
  const half = goals.find((goal) => goal.category === "health");
  const shipping = goals.find((goal) => goal.category === "shipping");
  assert.equal(half?.plan_steps.length, 3);
  assert.equal(half?.approval_policy.post, "deny");
  assert.equal(shipping?.plan_steps.length, 3);
  assert.equal(shipping?.approval_policy.spend, "deny");
  assert.equal(shipping?.next_action?.owner, "agent");
  const after = await readFile(join(exampleRoot, "index.json"), "utf8");
  assert.equal(after, before);
  assert.deepEqual(JSON.parse(await readFile(join(exampleRoot, "product.json"), "utf8")), packProduct());
});

test("JSON Schema enums match the server constants", () => {
  const goal = JSON.parse(readFileSync(join(packageRoot, "schema", "goal.schema.json"), "utf8"));
  const step = JSON.parse(readFileSync(join(packageRoot, "schema", "plan-step.schema.json"), "utf8"));
  assert.deepEqual(goal.properties.status.enum, [...GOAL_STATUSES]);
  assert.deepEqual(goal.properties.category.enum, [...CATEGORIES]);
  assert.deepEqual(goal.$defs.gate.enum, [...GATES]);
  assert.deepEqual(goal.$defs.nextAction.properties.owner.enum, [...OWNERS]);
  assert.deepEqual(step.properties.status.enum, [...STEP_STATUSES]);
  assert.deepEqual(step.properties.owner.enum, [...OWNERS]);
});
