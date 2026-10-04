import { resolvePackPath } from "../src/paths.js";
import { GoalStore } from "../src/store.js";

const root = resolvePackPath(process.argv[2]);
const store = new GoalStore(root);
await store.reindex();
const goals = await store.list();
console.log(`Reindexed ${goals.length} goals in ${root}`);
