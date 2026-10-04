import type { PackProduct } from "./types.js";

export function packProduct(): PackProduct {
  return {
    name: "grok-goals",
    title: "Grok Goals",
    kind: "prim-directory-pack",
    profile: "grok-goals.v1",
    profile_status: "in-repo-schema",
    schema_version: 1,
    description:
      "Durable goals for a Grok Bot. Each file in goals/ is one Goal. progress/ keeps earlier summaries.",
  };
}
