import { mkdir, readdir } from "node:fs/promises";
import { join } from "node:path";
import { toGoalDocument } from "./document.js";
import { GoalStoreError, isErrno } from "./errors.js";
import { readJson, writeIfMissing, writeJson } from "./io.js";
import { packProduct } from "./product.js";
import { isUuid, nowIso } from "./time.js";
import type { Goal, GoalIndex, IndexGoal, ListFilter } from "./types.js";
import { assertValidGoal, assertValidIndex } from "./validate.js";

export function goalPath(root: string, id: string): string {
  assertGoalId(id);
  return join(root, "goals", `${id}.json`);
}

export function progressPath(root: string, id: string): string {
  assertGoalId(id);
  return join(root, "progress", `${id}.jsonl`);
}

export function assertGoalId(id: string): void {
  if (!isUuid(id)) throw new GoalStoreError("validation", "Goal id must be a UUID.");
}

export async function ensurePack(root: string): Promise<void> {
  await mkdir(join(root, "goals"), { recursive: true });
  await mkdir(join(root, "progress"), { recursive: true });
  await writeIfMissing(join(root, "product.json"), packProduct());
  await writeIfMissing(join(root, "index.json"), emptyIndex());
}

function emptyIndex(): GoalIndex {
  return { updated_at: nowIso(), goals: [] };
}

export async function readGoal(root: string, id: string): Promise<Goal> {
  try {
    const parsed = await readJson(goalPath(root, id));
    assertValidGoal(parsed);
    if (parsed.id !== id) {
      throw new GoalStoreError("validation", `Goal id ${parsed.id} does not match its filename.`);
    }
    return parsed;
  } catch (error) {
    if (isErrno(error, "ENOENT")) {
      throw new GoalStoreError("not_found", "No goal with that id.");
    }
    throw error;
  }
}

export async function readAllGoals(root: string): Promise<Goal[]> {
  const names = await readGoalNames(root);
  const goals: Goal[] = [];
  for (const name of names) goals.push(await readGoal(root, name.slice(0, -".json".length)));
  return goals;
}

async function readGoalNames(root: string): Promise<string[]> {
  let names: string[];
  try {
    names = await readdir(join(root, "goals"));
  } catch (error) {
    if (isErrno(error, "ENOENT")) return [];
    throw error;
  }
  for (const name of names) {
    if (!name.endsWith(".json")) {
      throw new GoalStoreError("validation", `Unexpected file in goals/: ${name}`);
    }
  }
  return names.sort();
}

export function filterGoals(goals: Goal[], filter: ListFilter): Goal[] {
  return goals
    .filter((goal) => !filter.status || goal.status === filter.status)
    .filter((goal) => !filter.category || goal.category === filter.category)
    .sort(byRecent);
}

function byRecent(left: Goal, right: Goal): number {
  return right.updated_at.localeCompare(left.updated_at) || left.id.localeCompare(right.id);
}

export function toIndex(goals: Goal[], updatedAt = nowIso()): GoalIndex {
  const rows = goals.map(toIndexRow).sort((left, right) => {
    return right.updated_at.localeCompare(left.updated_at) || left.id.localeCompare(right.id);
  });
  return { updated_at: updatedAt, goals: rows };
}

function toIndexRow(goal: Goal): IndexGoal {
  const row: IndexGoal = {
    id: goal.id,
    title: goal.title,
    status: goal.status,
    updated_at: goal.updated_at,
  };
  if (!goal.category) return row;
  return {
    id: goal.id,
    title: goal.title,
    status: goal.status,
    category: goal.category,
    updated_at: goal.updated_at,
  };
}

export async function writeIndex(root: string, goals: Goal[]): Promise<void> {
  const index = toIndex(goals);
  assertValidIndex(index);
  await writeJson(join(root, "index.json"), index);
}

export async function persistGoal(root: string, goal: Goal): Promise<void> {
  const document = toGoalDocument(goal);
  assertValidGoal(document);
  await writeJson(goalPath(root, document.id), document);
  await writeIndex(root, await readAllGoals(root));
}
