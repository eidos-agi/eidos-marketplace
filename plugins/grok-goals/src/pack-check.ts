import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import { GoalStoreError, isErrno } from "./errors.js";
import { readJson } from "./io.js";
import { readAllGoals } from "./pack.js";
import { isDateTime, isUuid } from "./time.js";
import type { Goal, GoalIndex } from "./types.js";
import { assertValidIndex, assertValidProduct } from "./validate.js";

const PACK_ENTRIES = new Set(["product.json", "index.json", "goals", "progress"]);
const JOURNAL_KEYS = new Set(["at", "summary", "next_action", "step_updates"]);

export interface PackReport {
  root: string;
  goalCount: number;
  titles: string[];
}

export async function validatePack(root: string): Promise<PackReport> {
  await assertPackEntries(root);
  assertValidProduct(await readJson(join(root, "product.json")));
  const goals = await readAllGoals(root);
  const index = await readJson(join(root, "index.json"));
  assertValidIndex(index);
  assertIndexMatches(index, goals);
  await assertJournals(root, goals);
  return {
    root,
    goalCount: goals.length,
    titles: goals.map((goal) => goal.title).sort(),
  };
}

async function assertPackEntries(root: string): Promise<void> {
  const entries = await readdir(root);
  for (const name of entries) {
    if (!PACK_ENTRIES.has(name)) {
      throw new GoalStoreError("validation", `Unexpected pack entry: ${name}`);
    }
  }
  if (!entries.includes("goals") || !entries.includes("product.json") || !entries.includes("index.json")) {
    throw new GoalStoreError("validation", "Pack is missing product.json, index.json, or goals/.");
  }
}

function assertIndexMatches(index: GoalIndex, goals: Goal[]): void {
  if (index.goals.length !== goals.length) {
    throw new GoalStoreError("validation", "Index goal count does not match goals/.");
  }
  const rows = new Map(index.goals.map((row) => [row.id, row]));
  if (rows.size !== index.goals.length) {
    throw new GoalStoreError("validation", "Index contains duplicate goal ids.");
  }
  for (const goal of goals) {
    const row = rows.get(goal.id);
    if (!row) throw new GoalStoreError("validation", `Index is missing ${goal.id}.`);
    const same =
      row.title === goal.title &&
      row.status === goal.status &&
      row.updated_at === goal.updated_at &&
      row.category === goal.category;
    if (!same) throw new GoalStoreError("validation", `Index is stale for ${goal.id}.`);
  }
}

async function assertJournals(root: string, goals: Goal[]): Promise<void> {
  const names = await progressNames(root);
  const byId = new Map(goals.map((goal) => [goal.id, goal]));
  const seen = new Set<string>();
  for (const name of names) {
    const id = journalId(name, byId);
    seen.add(id);
    const last = await lastJournalLine(join(root, "progress", name));
    const progress = byId.get(id)?.last_progress;
    if (!progress || progress.at !== last.at || progress.summary !== last.summary) {
      throw new GoalStoreError("validation", `Latest journal line for ${id} does not match last_progress.`);
    }
  }
  for (const goal of goals) {
    if (goal.last_progress && !seen.has(goal.id)) {
      throw new GoalStoreError("validation", `Goal ${goal.id} has last_progress but no progress journal.`);
    }
  }
}

function journalId(name: string, byId: Map<string, Goal>): string {
  if (!name.endsWith(".jsonl")) {
    throw new GoalStoreError("validation", `Unexpected file in progress/: ${name}`);
  }
  const id = name.slice(0, -".jsonl".length);
  if (!isUuid(id) || !byId.has(id)) {
    throw new GoalStoreError("validation", `Progress file does not match a goal: ${name}`);
  }
  return id;
}

async function progressNames(root: string): Promise<string[]> {
  try {
    return await readdir(join(root, "progress"));
  } catch (error) {
    if (isErrno(error, "ENOENT")) return [];
    throw error;
  }
}

async function lastJournalLine(filePath: string): Promise<{ at: string; summary: string }> {
  const text = await readFile(filePath, "utf8");
  const lines = text.split("\n").filter((line) => line.length > 0);
  if (lines.length === 0) {
    throw new GoalStoreError("validation", `Progress journal is empty: ${filePath}`);
  }
  const last = lines[lines.length - 1];
  if (!last) throw new GoalStoreError("validation", `Progress journal is empty: ${filePath}`);
  return parseJournalLine(last, filePath);
}

function parseJournalLine(line: string, filePath: string): { at: string; summary: string } {
  let parsed: unknown;
  try {
    parsed = JSON.parse(line) as unknown;
  } catch {
    throw new GoalStoreError("validation", `Invalid JSON in ${filePath}.`);
  }
  if (!parsed || typeof parsed !== "object") {
    throw new GoalStoreError("validation", `Progress line is not an object in ${filePath}.`);
  }
  const record = parsed as Record<string, unknown>;
  for (const key of Object.keys(record)) {
    if (!JOURNAL_KEYS.has(key)) {
      throw new GoalStoreError("validation", `Unexpected progress field "${key}" in ${filePath}.`);
    }
  }
  if (typeof record.at !== "string" || !isDateTime(record.at)) {
    throw new GoalStoreError("validation", `Progress time is invalid in ${filePath}.`);
  }
  if (typeof record.summary !== "string" || record.summary.trim().length === 0) {
    throw new GoalStoreError("validation", `Progress summary is empty in ${filePath}.`);
  }
  return { at: record.at, summary: record.summary };
}
