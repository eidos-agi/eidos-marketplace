import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { GoalStoreError } from "../src/errors.js";
import { progressPath } from "../src/pack.js";
import { GoalStore } from "../src/store.js";
import { tempPack } from "./helpers.js";

async function storeWith(root: string): Promise<GoalStore> {
  const store = new GoalStore(root);
  await store.init();
  return store;
}

test("store rejects duplicate steps and impossible due dates", async () => {
  const pack = await tempPack();
  try {
    const store = await storeWith(pack.root);
    const stepId = "11111111-1111-4111-8111-111111111111";
    await assert.rejects(
      () =>
        store.create({
          title: "Ship quarterly invoice export",
          objective: "Customers can download the CSV.",
          plan_steps: [
            { id: stepId, title: "Confirm columns", owner: "user" },
            { id: stepId, title: "Confirm columns again", owner: "agent" },
          ],
        }),
      (error: unknown) => error instanceof GoalStoreError && /unique/.test(error.message),
    );
    await assert.rejects(
      () =>
        store.create({
          title: "Ship quarterly invoice export",
          objective: "Customers can download the CSV.",
          status: "active",
          next_action: { summary: "Ask finance for the columns.", owner: "user", due: "2026-02-31" },
        }),
      (error: unknown) => error instanceof GoalStoreError && /due|invalid/i.test(error.message),
    );
  } finally {
    await pack.remove();
  }
});

test("progress journal appends and approval gates merge", async () => {
  const pack = await tempPack();
  try {
    const store = await storeWith(pack.root);
    const goal = await store.create({
      title: "Ship quarterly invoice export",
      objective: "Customers can download the CSV from billing.",
      status: "draft",
      plan_steps: [{ title: "Confirm the columns with finance", owner: "user" }],
    });
    assert.equal((await store.list({ status: "active" })).length, 0);
    const active = await store.update(goal.id, { status: "active" });
    assert.equal(active.status, "active");
    await store.recordProgress({ id: goal.id, summary: "Sent the column list to finance." });
    const second = await store.recordProgress({
      id: goal.id,
      summary: "Finance said yes to the five columns.",
      next_action: null,
    });
    assert.equal(second.goal.last_progress?.summary, "Finance said yes to the five columns.");
    assert.equal(second.goal.next_action, undefined);
    const lines = (await readFile(progressPath(pack.root, goal.id), "utf8")).trim().split("\n");
    assert.equal(lines.length, 2);
    await assert.rejects(
      () => store.update(goal.id, {}),
      (error: unknown) => error instanceof GoalStoreError && /at least one field/.test(error.message),
    );
    const gated = await store.setApprovalPolicy(goal.id, { spend: "deny" });
    assert.equal(gated.approval_policy.spend, "deny");
    assert.equal(gated.approval_policy.send, "ask");
    const reopened = await store.update(gated.id, { status: "paused" });
    assert.equal(reopened.last_progress?.summary, second.goal.last_progress?.summary);
  } finally {
    await pack.remove();
  }
});
