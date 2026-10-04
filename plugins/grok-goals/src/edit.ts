import { randomUUID } from "node:crypto";
import { blankStep, mergePolicy, toGoalDocument, toNextAction, toPlanStep } from "./document.js";
import { GoalStoreError } from "./errors.js";
import { nowIso } from "./time.js";
import type {
  CreateGoalInput,
  Goal,
  GoalPatch,
  ProgressEntry,
  ProgressInput,
  StepUpdate,
} from "./types.js";
import { DEFAULT_APPROVAL_POLICY } from "./types.js";

export function normalizePlanStep(input: Parameters<typeof blankStep>[0]): ReturnType<typeof blankStep> {
  return blankStep(input, input.id ?? randomUUID());
}

export function buildNewGoal(input: CreateGoalInput, now = nowIso()): Goal {
  const status = input.status ?? "draft";
  if (status !== "draft" && status !== "active") {
    throw new GoalStoreError("validation", "Create only accepts draft or active.");
  }
  return toGoalDocument({
    id: randomUUID(),
    title: input.title,
    objective: input.objective,
    acceptance_criteria: input.acceptance_criteria ?? [],
    ...(input.category ? { category: input.category } : {}),
    plan_steps: (input.plan_steps ?? []).map(normalizePlanStep),
    status,
    ...(input.next_action ? { next_action: input.next_action } : {}),
    approval_policy: mergePolicy(DEFAULT_APPROVAL_POLICY, input.approval_policy),
    linked_routines: input.linked_routines ?? [],
    memory_refs: input.memory_refs ?? [],
    created_at: now,
    updated_at: now,
    ...(input.owner_bot ? { owner_bot: input.owner_bot } : {}),
  });
}

export function assertPatchPresent(patch: GoalPatch): void {
  const present = Object.values(patch).some((value) => value !== undefined);
  if (!present) {
    throw new GoalStoreError("validation", "Provide at least one field to update.");
  }
}

export function applyPatch(current: Goal, patch: GoalPatch, now = nowIso()): Goal {
  assertPatchPresent(patch);
  const next: Goal = { ...current, updated_at: now };
  if (patch.title !== undefined) next.title = patch.title;
  if (patch.objective !== undefined) next.objective = patch.objective;
  if (patch.acceptance_criteria !== undefined) {
    next.acceptance_criteria = patch.acceptance_criteria;
  }
  assignCategory(next, patch);
  if (patch.plan_steps !== undefined) {
    next.plan_steps = patch.plan_steps.map(normalizePlanStep);
  }
  if (patch.status !== undefined) next.status = patch.status;
  assignNextAction(next, patch);
  if (patch.linked_routines !== undefined) next.linked_routines = patch.linked_routines;
  if (patch.memory_refs !== undefined) next.memory_refs = patch.memory_refs;
  assignOwner(next, patch);
  return toGoalDocument(next);
}

function assignCategory(next: Goal, patch: GoalPatch): void {
  if (patch.category === undefined) return;
  if (patch.category === null) delete next.category;
  else next.category = patch.category;
}

function assignNextAction(next: Goal, patch: GoalPatch): void {
  if (patch.next_action === undefined) return;
  if (patch.next_action === null) delete next.next_action;
  else next.next_action = patch.next_action;
}

function assignOwner(next: Goal, patch: GoalPatch): void {
  if (patch.owner_bot === undefined) return;
  if (patch.owner_bot === null) delete next.owner_bot;
  else next.owner_bot = patch.owner_bot;
}

export function applyStepUpdates(steps: Goal["plan_steps"], updates: StepUpdate[]): Goal["plan_steps"] {
  const ids = updates.map((update) => update.id);
  if (new Set(ids).size !== ids.length) {
    throw new GoalStoreError("validation", "Plan step ids in step_updates must be unique.");
  }
  const known = new Set(steps.map((step) => step.id));
  for (const update of updates) {
    if (!known.has(update.id)) {
      throw new GoalStoreError("validation", `No plan step with id ${update.id}.`);
    }
    assertNotes(update.notes);
  }
  const byId = new Map(updates.map((update) => [update.id, update]));
  return steps.map((step) => mergeStep(step, byId.get(step.id)));
}

function assertNotes(notes: string | null | undefined): void {
  if (notes !== undefined && notes !== null && !notes.trim()) {
    throw new GoalStoreError(
      "validation",
      "Step notes cannot be empty. Pass null to clear them.",
    );
  }
}

function mergeStep(
  step: Goal["plan_steps"][number],
  update: StepUpdate | undefined,
): Goal["plan_steps"][number] {
  if (!update) return step;
  const notes = update.notes === undefined ? step.notes : update.notes ?? undefined;
  return toPlanStep({
    id: step.id,
    title: step.title,
    owner: step.owner,
    status: update.status,
    ...(notes ? { notes } : {}),
  });
}

export function applyProgress(current: Goal, input: ProgressInput, recordedAt: string): Goal {
  const at = input.at ?? recordedAt;
  const next: Goal = {
    ...current,
    last_progress: { at, summary: input.summary },
    updated_at: recordedAt,
    plan_steps: input.step_updates?.length
      ? applyStepUpdates(current.plan_steps, input.step_updates)
      : current.plan_steps,
  };
  if (input.next_action === null) delete next.next_action;
  else if (input.next_action) next.next_action = input.next_action;
  return toGoalDocument(next);
}

export function toProgressEntry(input: ProgressInput, at: string): ProgressEntry {
  const entry: ProgressEntry = { at, summary: input.summary.trim() };
  if (input.next_action === null) entry.next_action = null;
  else if (input.next_action) entry.next_action = toNextAction(input.next_action);
  if (input.step_updates?.length) entry.step_updates = input.step_updates;
  return entry;
}
