export const GOAL_STATUSES = [
  "draft",
  "active",
  "paused",
  "blocked",
  "completed",
  "abandoned",
] as const;

export const CREATE_STATUSES = ["draft", "active"] as const;

export const CATEGORIES = [
  "health",
  "finance",
  "career",
  "shipping",
  "other",
] as const;

export const OWNERS = ["user", "agent"] as const;

export const STEP_STATUSES = ["todo", "doing", "done", "skipped"] as const;

export const GATES = ["auto", "ask", "deny"] as const;

export const POLICY_ACTIONS = ["send", "spend", "post", "delete"] as const;

export type GoalStatus = (typeof GOAL_STATUSES)[number];
export type CreateStatus = (typeof CREATE_STATUSES)[number];
export type Category = (typeof CATEGORIES)[number];
export type Owner = (typeof OWNERS)[number];
export type StepStatus = (typeof STEP_STATUSES)[number];
export type Gate = (typeof GATES)[number];
export type PolicyAction = (typeof POLICY_ACTIONS)[number];

export interface PlanStep {
  id: string;
  title: string;
  owner: Owner;
  status: StepStatus;
  notes?: string;
}

export interface LastProgress {
  at: string;
  summary: string;
}

export interface NextAction {
  summary: string;
  owner: Owner;
  due?: string;
}

export interface ApprovalPolicy {
  send: Gate;
  spend: Gate;
  post: Gate;
  delete: Gate;
}

export interface Goal {
  id: string;
  title: string;
  objective: string;
  acceptance_criteria: string[];
  category?: Category;
  plan_steps: PlanStep[];
  status: GoalStatus;
  last_progress?: LastProgress;
  next_action?: NextAction;
  approval_policy: ApprovalPolicy;
  linked_routines: string[];
  memory_refs: string[];
  created_at: string;
  updated_at: string;
  owner_bot?: string;
}

export interface PlanStepInput {
  id?: string;
  title: string;
  owner: Owner;
  status?: StepStatus;
  notes?: string;
}

export interface CreateGoalInput {
  title: string;
  objective: string;
  acceptance_criteria?: string[];
  category?: Category;
  plan_steps?: PlanStepInput[];
  status?: CreateStatus;
  approval_policy?: Partial<ApprovalPolicy>;
  linked_routines?: string[];
  memory_refs?: string[];
  owner_bot?: string;
  next_action?: NextAction;
}

export interface GoalPatch {
  title?: string;
  objective?: string;
  acceptance_criteria?: string[];
  category?: Category | null;
  plan_steps?: PlanStepInput[];
  status?: GoalStatus;
  next_action?: NextAction | null;
  linked_routines?: string[];
  memory_refs?: string[];
  owner_bot?: string | null;
}

export interface StepUpdate {
  id: string;
  status: StepStatus;
  notes?: string | null;
}

export interface ProgressInput {
  id: string;
  summary: string;
  at?: string;
  next_action?: NextAction | null;
  step_updates?: StepUpdate[];
}

export interface ProgressEntry {
  at: string;
  summary: string;
  next_action?: NextAction | null;
  step_updates?: StepUpdate[];
}

export interface ProgressResult {
  goal: Goal;
  progress_entry: ProgressEntry;
}

export interface ListFilter {
  status?: GoalStatus;
  category?: Category;
}

export interface IndexGoal {
  id: string;
  title: string;
  status: GoalStatus;
  category?: Category;
  updated_at: string;
}

export interface GoalIndex {
  updated_at: string;
  goals: IndexGoal[];
}

export interface PackProduct {
  name: "grok-goals";
  title: string;
  kind: "prim-directory-pack";
  profile: string;
  profile_status: "in-repo-schema";
  schema_version: 1;
  description: string;
}

export const DEFAULT_APPROVAL_POLICY: ApprovalPolicy = {
  send: "ask",
  spend: "ask",
  post: "ask",
  delete: "ask",
};

export const TOOL_NAMES = [
  "goals_list",
  "goals_get",
  "goals_create",
  "goals_update",
  "goals_record_progress",
  "goals_set_approval_policy",
] as const;
