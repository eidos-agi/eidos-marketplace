from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
from urllib.parse import quote_plus

from typing import Any

from .planning import GroceryPlan, build_plan
from .storage import CartwrightStore


ExecutionMode = Literal["connector", "browser", "hybrid"]


@dataclass
class FulfillmentAction:
    index: int
    source_item: str
    quantity: str
    unit: str | None
    mode: ExecutionMode
    action: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "source_item": self.source_item,
            "quantity": self.quantity,
            "unit": self.unit,
            "mode": self.mode,
            "action": self.action,
            "payload": self.payload,
        }


@dataclass
class FulfillmentPlaybook:
    retailer: str
    mode: ExecutionMode
    constraints: list[str]
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    plan: GroceryPlan | None = None
    actions: list[FulfillmentAction] = field(default_factory=list)
    approval_required: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "retailer": self.retailer,
            "mode": self.mode,
            "constraints": self.constraints,
            "generated_at": self.generated_at,
            "plan": self.plan.to_dict() if self.plan else None,
            "actions": [action.to_dict() for action in self.actions],
            "approval_required": self.approval_required,
        }


def _walmart_search_url(item_name: str, brand: str | None = None) -> str:
    query = item_name
    if brand:
        query = f"{brand} {query}"
    return f"https://www.walmart.com/search?q={quote_plus(query)}"


def _handoff_payload(item: dict[str, Any], retailer: str) -> dict[str, Any]:
    return {
        "retailer": retailer,
        "item_name": item["normalized_name"],
        "preferred_quantity": f"{item.get('quantity', '1')} {item.get('unit') or ''}".strip(),
        "brand_preference": item.get("brand_preference"),
        "must_match_brand": item.get("must_match_brand"),
        "notes": item.get("notes"),
        "confidence": item.get("confidence"),
    }


def _approval_checks() -> list[str]:
    return [
        "No action is executed by Cartwright V1.",
        "User must approve every browser step that touches account state.",
        "Do not proceed to checkout, payment, coupons, or order confirmation without explicit approval.",
    ]


def build_fulfillment_playbook(
    store: CartwrightStore,
    retailer: str,
    constraints: list[str] | None = None,
    mode: str = "hybrid",
    browser_profile: str = "default",
) -> FulfillmentPlaybook:
    if mode not in {"connector", "browser", "hybrid"}:
        raise ValueError(f"unsupported execution mode '{mode}'")

    constraints = constraints or []
    plan = build_plan(store=store, retailer=retailer, constraints=constraints)
    actions: list[FulfillmentAction] = []

    for index, item in enumerate(plan.list_items, start=1):
        item_name = item["normalized_name"]
        unit = item.get("unit")
        quantity = item.get("quantity", "1")
        brand = item.get("brand_preference")
        should_search = mode in {"connector", "hybrid"}
        should_browser = mode in {"browser", "hybrid"}

        if should_search:
            actions.append(
                FulfillmentAction(
                    index=index,
                    source_item=item_name,
                    quantity=quantity,
                    unit=unit,
                    mode="connector",
                    action="search_and_stage",
                    payload={
                        "required_connector": "Walmart product_search + basket_builder",
                        "handoff": _handoff_payload(item, retailer),
                        "notes": "Connector call returns candidate matches; selection still needs user confirmation.",
                    },
                )
            )

        if should_browser:
            actions.append(
                FulfillmentAction(
                    index=index,
                    source_item=item_name,
                    quantity=quantity,
                    unit=unit,
                    mode="browser",
                    action="snapshot_and_act",
                    payload={
                        "tool": "browser.snapshot_and_act",
                        "profile": browser_profile,
                        "retailer": retailer,
                        "search_url": _walmart_search_url(item_name, brand),
                        "flow": [
                            {
                                "step": "snapshot",
                                "goal": "Get a fresh accessibility/UI tree with refs.",
                                "notes": "Refs are page-relative and must be refreshed after navigation.",
                            },
                            {
                                "step": "act",
                                "operation": "type",
                                "target_hint": "search input",
                                "text": f"{item_name} {brand}" if brand else item_name,
                            },
                            {
                                "step": "act",
                                "operation": "press_enter",
                                "target_hint": "search input",
                            },
                            {
                                "step": "act",
                                "operation": "click",
                                "target_hint": "first matching add-to-cart button",
                                "constraints": [
                                    f"Respect brand constraint: {brand or 'any trusted brand'}.",
                                    f"Apply quantity {quantity} {unit or ''}".strip(),
                                ],
                            },
                        ],
                        "approval_points": [
                            "Requires logged-in user session before any account action.",
                            "Stop and request approval before navigating to checkout.",
                        ],
                    },
                )
            )

    return FulfillmentPlaybook(
        retailer=retailer,
        mode=mode,
        constraints=constraints,
        plan=plan,
        actions=actions,
        approval_required=_approval_checks(),
    )
