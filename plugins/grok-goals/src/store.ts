import { withLock } from "./lock.js";
import { ensurePack, readGoal } from "./pack.js";
import {
  createGoal,
  listGoals,
  recordProgress,
  reindexPack,
  setApprovalPolicy,
  updateGoal,
} from "./mutate.js";
import type {
  ApprovalPolicy,
  CreateGoalInput,
  Goal,
  GoalPatch,
  ListFilter,
  ProgressInput,
  ProgressResult,
} from "./types.js";

export class GoalStore {
  constructor(readonly root: string) {}

  init(): Promise<void> {
    return withLock(this.root, () => ensurePack(this.root));
  }

  list(filter: ListFilter = {}): Promise<Goal[]> {
    return withLock(this.root, () => listGoals(this.root, filter));
  }

  get(id: string): Promise<Goal> {
    return withLock(this.root, () => readGoal(this.root, id));
  }

  create(input: CreateGoalInput): Promise<Goal> {
    return withLock(this.root, () => createGoal(this.root, input));
  }

  update(id: string, patch: GoalPatch): Promise<Goal> {
    return withLock(this.root, () => updateGoal(this.root, id, patch));
  }

  recordProgress(input: ProgressInput): Promise<ProgressResult> {
    return withLock(this.root, () => recordProgress(this.root, input));
  }

  setApprovalPolicy(id: string, patch: Partial<ApprovalPolicy>): Promise<Goal> {
    return withLock(this.root, () => setApprovalPolicy(this.root, id, patch));
  }

  reindex(): Promise<void> {
    return withLock(this.root, () => reindexPack(this.root));
  }
}
