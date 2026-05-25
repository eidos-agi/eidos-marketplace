from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .models import CanonicalItem
from .parsing import dedupe_items
from .storage import CartwrightStore


@dataclass
class GroceryPlan:
    retailer: str
    constraints: list[str]
    list_items: list[dict[str, Any]] = field(default_factory=list)
    staples: list[str] = field(default_factory=list)
    uncertain: list[dict[str, Any]] = field(default_factory=list)
    substitutions: list[dict[str, str]] = field(default_factory=list)
    approval_required: list[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "retailer": self.retailer,
            "constraints": self.constraints,
            "list_items": self.list_items,
            "staples": self.staples,
            "uncertain_items": self.uncertain,
            "substitution_notes": self.substitutions,
            "approval_required_next_step": self.approval_required,
            "generated_at": self.generated_at,
        }


def _normalize_constraint_terms(constraints: list[str] | None) -> set[str]:
    terms = set()
    for constraint in constraints or []:
        lower = constraint.lower()
        terms.add(lower)
        if "vegetables" in lower or "vegetable" in lower or "veggies" in lower:
            terms.add("vegetables")
    return terms


def _suppressed_categories(constraints: set[str]) -> set[str]:
    suppressed = set()
    if "plenty of vegetables" in constraints or "vegetables" in constraints:
        suppressed.add("produce")
        suppressed.add("vegetable")
        suppressed.add("vegetables")
    if "plenty of dairy" in constraints or "full dairy" in constraints:
        suppressed.add("dairy")
    return suppressed


def _handoff(retailer: str, item: CanonicalItem) -> dict[str, Any]:
    return {
        "retailer": retailer,
        "intent": f"search_and_build_in_{retailer.lower()}",
        "handoff_item": item.normalized_name,
        "preferred_quantity": f"{item.quantity} {item.unit or ''}".strip(),
        "brand_constraint": item.brand_preference,
        "must_match_brand": item.must_match_brand,
        "required_connector": "product_search + basket_builder",
    }


def _quantity_merge_text(item: CanonicalItem, history_count: int) -> str:
    qty = item.quantity
    if history_count >= 3 and not item.quantity:
        qty = "2"
    return qty


def build_plan(store: CartwrightStore, retailer: str, constraints: list[str] | None = None) -> GroceryPlan:
    active_items = store.get_active_items()
    profile = store.get_profile()
    active_constraints = profile.get("constraints", [])
    if isinstance(active_constraints, str):
        active_constraints = [active_constraints]
    constraint_terms = _normalize_constraint_terms((constraints or []) + list(active_constraints))
    suppressed = _suppressed_categories(constraint_terms)

    profile_staples = profile.get("recent_staples", [])
    if not isinstance(profile_staples, list):
        profile_staples = []

    staples = sorted(set(store.get_recent_staples(days=180) + profile_staples))
    history = store.get_purchase_history(days=180)
    history_counts: dict[str, int] = {}
    for item in history:
        history_counts[item.normalized_name] = history_counts.get(item.normalized_name, 0) + 1

    merged = dedupe_items(active_items)
    item_rows = []
    uncertain = []
    substitutions = []
    for item in merged:
        if item.category in suppressed:
            continue
        if item.normalized_name in {normalize for normalize in suppressed}:
            continue
        row = item.to_dict()
        row["quantity"] = _quantity_merge_text(item, history_counts.get(item.normalized_name, 0))
        row["handoff"] = _handoff(retailer, item)
        row["recent_staple"] = item.normalized_name in staples
        item_rows.append(row)
        if item.confidence < 0.85:
            uncertain.append(
                {
                    "item": item.normalized_name,
                    "reason": "low-confidence source extraction",
                    "confidence": item.confidence,
                }
            )
        if not item.must_match_brand and not item.brand_preference:
            substitutions.append(
                {
                    "item": item.normalized_name,
                    "substitution": "Any trusted brand within size/volume range is acceptable.",
                }
            )
        elif item.brand_preference:
            substitutions.append(
                {
                    "item": item.normalized_name,
                    "substitution": f"Prefers {item.brand_preference}.",
                }
            )

    return GroceryPlan(
        retailer=retailer,
        constraints=sorted(constraint_terms),
        list_items=item_rows,
        staples=staples[:20],
        uncertain=uncertain,
        substitutions=substitutions,
        approval_required=[
            "No direct cart writeback or checkout is performed in Cartwright V1.",
            "Use Walmart connector calls externally for product_search and basket_builder with these item handoff payloads.",
            "Any account/cart action still requires explicit user approval.",
        ],
    )
