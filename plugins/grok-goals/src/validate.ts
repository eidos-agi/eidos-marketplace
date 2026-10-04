import { readFileSync } from "node:fs";
import { join } from "node:path";
import { Ajv2020 } from "ajv/dist/2020.js";
import type { ErrorObject, ValidateFunction } from "ajv";
import { GoalStoreError } from "./errors.js";
import { packageRoot } from "./root.js";
import { isDateOrDateTime, isDateTime, isUuid } from "./time.js";
import type { Goal, GoalIndex, PackProduct } from "./types.js";

interface Validators {
  goal: ValidateFunction;
  product: ValidateFunction;
  index: ValidateFunction;
}

let validators: Validators | undefined;

function compileValidators(): Validators {
  const ajv = new Ajv2020({ allErrors: true, strict: true });
  ajv.addFormat("uuid", { type: "string", validate: isUuid });
  ajv.addFormat("date-time", { type: "string", validate: isDateTime });
  ajv.addFormat("iso-date", { type: "string", validate: isDateOrDateTime });
  const planStep = loadSchema("plan-step.schema.json");
  const goal = loadSchema("goal.schema.json");
  ajv.addSchema(planStep);
  return {
    goal: ajv.compile(goal),
    product: ajv.compile(loadSchema("product.schema.json")),
    index: ajv.compile(loadSchema("index.schema.json")),
  };
}

function loadSchema(name: string): object {
  const text = readFileSync(join(packageRoot, "schema", name), "utf8");
  return JSON.parse(text) as object;
}

function getValidators(): Validators {
  validators ??= compileValidators();
  return validators;
}

function formatErrors(errors: ErrorObject[] | null | undefined): string {
  if (!errors?.length) return "document is invalid.";
  const shown = errors.slice(0, 8).map((error) => {
    const path = error.instancePath || "/";
    return `${path} ${error.message ?? "is invalid"}`;
  });
  const extra = errors.length > 8 ? ` (+${errors.length - 8} more)` : "";
  return `${shown.join("; ")}${extra}`;
}

function errorDetails(errors: ErrorObject[] | null | undefined): unknown {
  return (errors ?? []).slice(0, 8).map((error) => ({
    path: error.instancePath || "/",
    message: error.message ?? "is invalid",
  }));
}

function assertSchema(validate: ValidateFunction, data: unknown, label: string): void {
  if (!validate(data)) {
    throw new GoalStoreError(
      "validation",
      `${label} is invalid: ${formatErrors(validate.errors)}`,
      errorDetails(validate.errors),
    );
  }
}

export function assertValidGoal(data: unknown): asserts data is Goal {
  assertSchema(getValidators().goal, data, "Goal document");
  const goal = data as Goal;
  const ids = goal.plan_steps.map((step) => step.id);
  if (new Set(ids).size !== ids.length) {
    throw new GoalStoreError("validation", "Plan step ids must be unique within a goal.");
  }
}

export function assertValidProduct(data: unknown): asserts data is PackProduct {
  assertSchema(getValidators().product, data, "product.json");
}

export function assertValidIndex(data: unknown): asserts data is GoalIndex {
  assertSchema(getValidators().index, data, "index.json");
}
