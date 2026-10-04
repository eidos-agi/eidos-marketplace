import { applyPatch, applyProgress, buildNewGoal, toProgressEntry } from "./edit.js";
import { mergePolicy } from "./document.js";
import { GoalStoreError } from "./errors.js";
import { appendJsonLine } from "./io.js";
import { ensurePack, filterGoals, persistGoal, progressPath, readAllGoals, readGoal, writeIndex } from "./pack.js";
import { nowIso } from "./time.js";
import type {
  ApprovalPolicy,
  CreateGoalInput,
  Goal,
  GoalPatch,
  ListFilter,
  ProgressInput,
  ProgressResult,
} from "./types.js";
import { POLICY_ACTIONS } from "./types.js";

export async function createGoal(root: string, input: CreateGoalInput): Promise<Goal> {
  await ensurePack(root);
  const goal = buildNewGoal(input);
  await persistGoal(root, goal);
  return readGoal(root, goal.id);
}

export async function updateGoal(root: string, id: string, patch: GoalPatch): Promise<Goal> {
  const current = await readGoal(root, id);
  await persistGoal(root, applyPatch(current, patch));
  return readGoal(root, id);
}

export async function recordProgress(root: string, input: ProgressInput): Promise<ProgressResult> {
  const current = await readGoal(root, input.id);
  const recordedAt = nowIso();
  const at = input.at ?? recordedAt;
  const next = applyProgress(current, input, recordedAt);
  await persistGoal(root, next);
  const progressEntry = toProgressEntry(input, at);
  await appendJsonLine(progressPath(root, input.id), progressEntry);
  return { goal: await readGoal(root, input.id), progress_entry: progressEntry };
}

export async function setApprovalPolicy(
  root: string,
  id: string,
  patch: Partial<ApprovalPolicy>,
): Promise<Goal> {
  assertPolicyPatch(patch);
  const current = await readGoal(root, id);
  const next: Goal = {
    ...current,
    approval_policy: mergePolicy(current.approval_policy, patch),
    updated_at: nowIso(),
  };
  await persistGoal(root, next);
  return readGoal(root, id);
}

function assertPolicyPatch(patch: Partial<ApprovalPolicy>): void {
  const changes = POLICY_ACTIONS.filter((action) => patch[action] !== undefined);
  if (changes.length === 0) {
    throw new GoalStoreError(
      "validation",
      "Provide at least one gate: send, spend, post, or delete.",
    );
  }
}

export async function listGoals(root: string, filter: ListFilter): Promise<Goal[]> {
  return filterGoals(await readAllGoals(root), filter);
}

export async function reindexPack(root: string): Promise<void> {
  await ensurePack(root);
  await writeIndex(root, await readAllGoals(root));
}
