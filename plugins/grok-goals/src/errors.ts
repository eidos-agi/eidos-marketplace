export type GoalErrorCode = "not_found" | "validation" | "io";

export class GoalStoreError extends Error {
  readonly code: GoalErrorCode;
  readonly details: unknown;

  constructor(code: GoalErrorCode, message: string, details?: unknown) {
    super(message);
    this.name = "GoalStoreError";
    this.code = code;
    this.details = details;
  }
}

export function isErrno(error: unknown, code: string): boolean {
  return (
    error instanceof Error &&
    "code" in error &&
    (error as NodeJS.ErrnoException).code === code
  );
}
