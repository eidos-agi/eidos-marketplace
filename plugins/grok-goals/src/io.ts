import { appendFile, mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { basename, dirname } from "node:path";
import { GoalStoreError, isErrno } from "./errors.js";

export async function readJson(filePath: string): Promise<unknown> {
  let text: string;
  try {
    text = await readFile(filePath, "utf8");
  } catch (error) {
    if (isErrno(error, "ENOENT")) throw error;
    throw new GoalStoreError("io", `Could not read ${basename(filePath)}.`);
  }
  try {
    return JSON.parse(text) as unknown;
  } catch {
    throw new GoalStoreError("validation", `Invalid JSON in ${basename(filePath)}.`);
  }
}

export async function writeJson(filePath: string, value: unknown): Promise<void> {
  const temporary = `${filePath}.${process.pid}.tmp`;
  await writeFile(temporary, `${JSON.stringify(value, null, 2)}\n`);
  await rename(temporary, filePath);
}

export async function writeIfMissing(filePath: string, value: unknown): Promise<void> {
  try {
    await writeFile(filePath, `${JSON.stringify(value, null, 2)}\n`, { flag: "wx" });
  } catch (error) {
    if (isErrno(error, "EEXIST")) return;
    throw new GoalStoreError("io", `Could not create ${basename(filePath)}.`);
  }
}

export async function appendJsonLine(filePath: string, value: unknown): Promise<void> {
  await mkdir(dirname(filePath), { recursive: true });
  await appendFile(filePath, `${JSON.stringify(value)}\n`);
}
