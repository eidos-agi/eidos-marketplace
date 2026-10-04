import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { GoalStoreError } from "./errors.js";

export function okResult(data: object): CallToolResult {
  const structuredContent = { ok: true, ...data } as Record<string, unknown>;
  return {
    content: [{ type: "text", text: JSON.stringify(structuredContent) }],
    structuredContent,
  };
}

export function errorResult(error: unknown): CallToolResult {
  if (!(error instanceof GoalStoreError)) console.error(error);
  const structuredContent = errorBody(error);
  return {
    isError: true,
    content: [{ type: "text", text: JSON.stringify(structuredContent) }],
    structuredContent,
  };
}

function errorBody(error: unknown): Record<string, unknown> {
  if (error instanceof GoalStoreError) {
    const payload: Record<string, unknown> = {
      code: error.code,
      message: error.message,
    };
    if (error.details !== undefined) payload.details = error.details;
    return { ok: false, error: payload };
  }
  const message = error instanceof Error ? error.message : "Unexpected failure.";
  return { ok: false, error: { code: "internal", message } };
}

export function readToolPayload(result: {
  structuredContent?: unknown;
  content?: Array<{ type: string; text?: string }>;
}): Record<string, unknown> {
  if (result.structuredContent && typeof result.structuredContent === "object") {
    return result.structuredContent as Record<string, unknown>;
  }
  const text = result.content?.find((item) => item.type === "text")?.text;
  if (!text) throw new Error("Tool result had no payload.");
  return JSON.parse(text) as Record<string, unknown>;
}
