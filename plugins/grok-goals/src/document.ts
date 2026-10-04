import type {
  ApprovalPolicy,
  Goal,
  NextAction,
  PlanStep,
  PlanStepInput,
} from "./types.js";
import { DEFAULT_APPROVAL_POLICY } from "./types.js";

export function mergePolicy(
  base: ApprovalPolicy,
  patch?: Partial<ApprovalPolicy>,
): ApprovalPolicy {
  return {
    send: patch?.send ?? base.send,
    spend: patch?.spend ?? base.spend,
    post: patch?.post ?? base.post,
    delete: patch?.delete ?? base.delete,
  };
}

export function toPlanStep(step: PlanStep): PlanStep {
  const document: PlanStep = {
    id: step.id,
    title: step.title.trim(),
    owner: step.owner,
    status: step.status,
  };
  const notes = step.notes?.trim();
  if (notes) document.notes = notes;
  return document;
}

export function toNextAction(action: NextAction): NextAction {
  const document: NextAction = {
    summary: action.summary.trim(),
    owner: action.owner,
  };
  if (action.due) document.due = action.due;
  return document;
}

export function toGoalDocument(goal: Goal): Goal {
  const document: Goal = {
    id: goal.id,
    title: goal.title.trim(),
    objective: goal.objective.trim(),
    acceptance_criteria: goal.acceptance_criteria.map((item) => item.trim()),
    plan_steps: goal.plan_steps.map(toPlanStep),
    status: goal.status,
    approval_policy: mergePolicy(DEFAULT_APPROVAL_POLICY, goal.approval_policy),
    linked_routines: goal.linked_routines.map((item) => item.trim()),
    memory_refs: goal.memory_refs.map((item) => item.trim()),
    created_at: goal.created_at,
    updated_at: goal.updated_at,
  };
  if (goal.category) document.category = goal.category;
  if (goal.last_progress) {
    document.last_progress = {
      at: goal.last_progress.at,
      summary: goal.last_progress.summary.trim(),
    };
  }
  if (goal.next_action) document.next_action = toNextAction(goal.next_action);
  const owner = goal.owner_bot?.trim();
  if (owner) document.owner_bot = owner;
  return document;
}

export function blankStep(input: PlanStepInput, id: string): PlanStep {
  return toPlanStep({
    id,
    title: input.title,
    owner: input.owner,
    status: input.status ?? "todo",
    ...(input.notes ? { notes: input.notes } : {}),
  });
}
