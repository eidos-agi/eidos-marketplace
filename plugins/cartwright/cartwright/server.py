from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from .constants import get_db_path
from .models import ItemSource
from .parsing import parse_connector_payload, parse_list_text
from .receipts import parse_receipt_text
from .execution import build_fulfillment_playbook
from .planning import build_plan
from .storage import CartwrightStore

mcp = FastMCP("cartwright")


def _store() -> CartwrightStore:
    return CartwrightStore(get_db_path(None))


def _err(msg: str) -> str:
    return json.dumps({"error": msg}, indent=2)


@mcp.tool()
def cartwright_get_profile() -> str:
    """Read the active Cartwright shopping profile."""
    try:
        store = _store()
        return json.dumps(store.get_profile(), indent=2, default=str)
    except Exception as e:
        return _err(f"Failed to read profile: {e}")


@mcp.tool()
def cartwright_update_profile(profile_json: str) -> str:
    """Replace the shopping profile with JSON payload."""
    try:
        payload = json.loads(profile_json)
    except json.JSONDecodeError as exc:
        return _err(f"Invalid JSON: {exc}")
    try:
        store = _store()
        store.set_profile(payload, source="mcp")
        return json.dumps({"status": "ok", "saved": True}, indent=2)
    except Exception as e:
        return _err(f"Failed to update profile: {e}")


@mcp.tool()
def cartwright_import_list(source: str, payload: str, source_ref: str | None = None) -> str:
    """Import list items from pasted text or connector payload."""
    try:
        source = _normalize_source(source)
        if source == "pasted_text":
            items = parse_list_text(payload, "pasted_text", base_confidence=0.93)
        else:
            items = parse_connector_payload(payload, source, base_confidence=0.78)
        store = _store()
        list_id = store.import_items(source, items, source_ref=source_ref)
        return json.dumps(
            {"status": "ok", "list_id": list_id, "imported": len(items)},
            indent=2,
            default=str,
        )
    except Exception as e:
        return _err(f"Failed to import list: {e}")


@mcp.tool()
def cartwright_import_receipt(source: str, receipt_text: str) -> str:
    """Import receipt text and extract likely staples for profile memory."""
    try:
        src = _normalize_source(source)
        retailer, date, items = parse_receipt_text(receipt_text, source=src)
        store = _store()
        store.add_receipt_items(src, retailer=retailer, items=items, receipt_date=date, raw_payload=receipt_text)
        return json.dumps(
            {"status": "ok", "retailer": retailer, "receipt_date": date, "imported": len(items)},
            indent=2,
            default=str,
        )
    except Exception as e:
        return _err(f"Failed to import receipt: {e}")


@mcp.tool()
def cartwright_get_active_list() -> str:
    """Return current active list state."""
    try:
        store = _store()
        items = store.get_active_items()
        return json.dumps({"count": len(items), "items": [item.to_dict() for item in items]}, indent=2, default=str)
    except Exception as e:
        return _err(f"Failed to get list: {e}")


@mcp.tool()
def cartwright_build_grocery_plan(
    retailer: str = "walmart",
    constraints: list[str] | None = None,
) -> str:
    """Build a Walmart-oriented plan from active list + profile + receipt staples."""
    try:
        constraints = constraints or []
        plan = build_plan(_store(), retailer=retailer, constraints=list(constraints))
        return json.dumps(plan.to_dict(), indent=2, default=str)
    except Exception as e:
        return _err(f"Failed to build plan: {e}")


@mcp.tool()
def cartwright_export_list(
    export_format: str = "markdown",
    list_id: int | None = None,
) -> str:
    """Produce list content in a deterministic wire format."""
    try:
        store = _store()
        items = [item.to_dict() for item in store.get_active_items()]
        if not items:
            return json.dumps({"status": "ok", "content": "", "format": export_format}, indent=2)
        if export_format not in {"markdown", "csv"}:
            return _err(f"unsupported export format {export_format}")
        if export_format == "markdown":
            content = "# Cartwright Export\n\n"
            for item in items:
                label = item["normalized_name"]
                unit = item["unit"] or ""
                content += f"- {item['quantity']} {unit} {label}\n"
        else:
            lines = ["normalized_name,quantity,unit,category,brand_preference,source,confidence,notes"]
            for item in items:
                safe = [str(item[k] or "").replace(",", " ") for k in ("normalized_name", "quantity", "unit", "category", "brand_preference", "source", "confidence")]
                lines.append(",".join(safe + [str(item.get("notes") or "")]))
            content = "\n".join(lines)
        store.log_export(list_id or store.get_active_list_id(), export_format, None, {"exported": len(items)})
        return json.dumps({"status": "ok", "format": export_format, "content": content}, indent=2, default=str)
    except Exception as e:
        return _err(f"Failed to export list: {e}")


@mcp.tool()
def cartwright_remember_source_url(source: str, url: str, label: str | None = None) -> str:
    """Remember a source URL, such as the user's Amazon shopping-list landing page."""
    try:
        store = _store()
        metadata = {"url": url}
        if label:
            metadata["label"] = label
        store.remember_source_connection(source, status="ready", metadata=metadata)
        return json.dumps({"status": "ok", "connection": store.get_source_connection(source)}, indent=2, default=str)
    except Exception as e:
        return _err(f"Failed to remember source URL: {e}")


@mcp.tool()
def cartwright_get_source_connection(source: str) -> str:
    """Read remembered metadata for a shopping source."""
    try:
        store = _store()
        return json.dumps({"connection": store.get_source_connection(source)}, indent=2, default=str)
    except Exception as e:
        return _err(f"Failed to get source connection: {e}")


@mcp.tool()
def cartwright_build_execution_playbook(
    retailer: str = "walmart",
    mode: str = "hybrid",
    constraints: list[str] | None = None,
    browser_profile: str = "default",
) -> str:
    """Build an execution playbook for connector + browser fulfillment."""
    try:
        constraints = constraints or []
        playbook = build_fulfillment_playbook(
            _store(),
            retailer=retailer,
            constraints=list(constraints),
            mode=mode,
            browser_profile=browser_profile,
        )
        return json.dumps(playbook.to_dict(), indent=2, default=str)
    except Exception as e:
        return _err(f"Failed to build execution playbook: {e}")


def _normalize_source(source: str) -> ItemSource:
    source = source.strip().lower()
    if source == "pasted":
        return "pasted_text"
    if source in {"browser", "browser_capture"}:
        return "browser_capture"
    if source in {"pasted_text", "screenshot", "gmail", "drive", "keep", "alexa", "walmart"}:
        return source
    raise ValueError(f"unsupported source '{source}'")


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
