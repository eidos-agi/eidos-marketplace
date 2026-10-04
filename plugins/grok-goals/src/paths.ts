import { join, resolve } from "node:path";

export function resolvePackPath(explicit?: string): string {
  const fromEnv = process.env.GROK_GOALS_PACK?.trim();
  const raw = explicit || fromEnv || join(process.cwd(), "data", "grok-goals.prim");
  return resolve(raw);
}
