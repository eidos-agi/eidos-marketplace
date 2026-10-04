import { join } from "node:path";
import { validatePack } from "../src/pack-check.js";
import { packageRoot } from "../src/root.js";

const root = process.argv[2] ?? join(packageRoot, "examples", "grok-goals.prim");
const report = await validatePack(root);
console.log(`Valid pack (${report.goalCount} goals): ${root}`);
for (const title of report.titles) console.log(`- ${title}`);
