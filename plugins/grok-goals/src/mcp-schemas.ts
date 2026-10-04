import { z } from "zod";
import {
  CATEGORIES,
  CREATE_STATUSES,
  GATES,
  GOAL_STATUSES,
  OWNERS,
  STEP_STATUSES,
} from "./types.js";

const owner = z.enum(OWNERS);
const gate = z.enum(GATES);
const stepStatus = z.enum(STEP_STATUSES);

export const planStepInput = z.object({
  id: z.uuid().optional(),
  title: z.string().trim().min(1).max(200),
  owner,
  status: stepStatus.optional(),
  notes: z.string().trim().min(1).max(2000).optional(),
});

export const nextActionInput = z.object({
  summary: z.string().trim().min(1).max(500),
  owner,
  due: z.string().min(1).max(40).optional(),
});

export const policyInput = z.object({
  send: gate.optional(),
  spend: gate.optional(),
  post: gate.optional(),
  delete: gate.optional(),
});

const stepUpdateInput = z.object({
  id: z.uuid(),
  status: stepStatus,
  notes: z.string().trim().min(1).max(2000).nullable().optional(),
});

export const goalOutput = z.object({
  id: z.string(),
  title: z.string(),
  objective: z.string(),
  acceptance_criteria: z.array(z.string()),
  category: z.enum(CATEGORIES).optional(),
  plan_steps: z.array(
    z.object({
      id: z.string(),
      title: z.string(),
      owner,
      status: stepStatus,
      notes: z.string().optional(),
    }),
  ),
  status: z.enum(GOAL_STATUSES),
  last_progress: z.object({ at: z.string(), summary: z.string() }).optional(),
  next_action: nextActionInput.optional(),
  approval_policy: z.object({
    send: gate,
    spend: gate,
    post: gate,
    delete: gate,
  }),
  linked_routines: z.array(z.string()),
  memory_refs: z.array(z.string()),
  created_at: z.string(),
  updated_at: z.string(),
  owner_bot: z.string().optional(),
});

const progressEntryOutput = z.object({
  at: z.string(),
  summary: z.string(),
  next_action: nextActionInput.nullable().optional(),
  step_updates: z.array(stepUpdateInput).optional(),
});

export const listInput = z.object({
  status: z.enum(GOAL_STATUSES).optional(),
  category: z.enum(CATEGORIES).optional(),
});

export const getInput = z.object({
  id: z.uuid(),
});

export const createInput = z.object({
  title: z.string().trim().min(1).max(200),
  objective: z.string().trim().min(1).max(4000),
  acceptance_criteria: z.array(z.string().trim().min(1).max(500)).max(50).optional(),
  category: z.enum(CATEGORIES).optional(),
  plan_steps: z.array(planStepInput).max(100).optional(),
  status: z.enum(CREATE_STATUSES).optional(),
  approval_policy: policyInput.optional(),
  linked_routines: z.array(z.string().trim().min(1).max(200)).max(50).optional(),
  memory_refs: z.array(z.string().trim().min(1).max(200)).max(50).optional(),
  owner_bot: z.string().trim().min(1).max(200).optional(),
  next_action: nextActionInput.optional(),
});

export const updateInput = z.object({
  id: z.uuid(),
  title: z.string().trim().min(1).max(200).optional(),
  objective: z.string().trim().min(1).max(4000).optional(),
  acceptance_criteria: z.array(z.string().trim().min(1).max(500)).max(50).optional(),
  category: z.enum(CATEGORIES).nullable().optional(),
  plan_steps: z.array(planStepInput).max(100).optional(),
  status: z.enum(GOAL_STATUSES).optional(),
  next_action: nextActionInput.nullable().optional(),
  linked_routines: z.array(z.string().trim().min(1).max(200)).max(50).optional(),
  memory_refs: z.array(z.string().trim().min(1).max(200)).max(50).optional(),
  owner_bot: z.string().trim().min(1).max(200).nullable().optional(),
});

export const progressInput = z.object({
  id: z.uuid(),
  summary: z.string().trim().min(1).max(2000),
  at: z.string().min(1).max(40).optional(),
  next_action: nextActionInput.nullable().optional(),
  step_updates: z.array(stepUpdateInput).max(100).optional(),
});

export const policyToolInput = z.object({
  id: z.uuid(),
  send: gate.optional(),
  spend: gate.optional(),
  post: gate.optional(),
  delete: gate.optional(),
});

export const listOutput = z.object({
  ok: z.literal(true),
  goals: z.array(goalOutput),
});

export const goalToolOutput = z.object({
  ok: z.literal(true),
  goal: goalOutput,
});

export const progressOutput = z.object({
  ok: z.literal(true),
  goal: goalOutput,
  progress_entry: progressEntryOutput,
});
