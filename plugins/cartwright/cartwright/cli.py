from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

from .constants import get_db_path
from .parsing import parse_connector_payload, parse_list_text
from .receipts import parse_receipt_text
from .execution import build_fulfillment_playbook
from .storage import CartwrightStore
from .planning import build_plan


def _normalize_source(source: str) -> str:
    mapping = {
        "pasted": "pasted_text",
        "screenshot": "screenshot",
        "gmail": "gmail",
        "drive": "drive",
        "alexa": "alexa",
        "keep": "keep",
        "browser_capture": "browser_capture",
        "browser": "browser_capture",
    }
    return mapping.get(source, source)


def _stdout_json(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _read_input_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    return sys.stdin.read()


def cmd_init(store: CartwrightStore, args: argparse.Namespace) -> int:
    del args
    store.initialize()
    print(f"cartwright initialized at {store.db_path}")
    return 0


def cmd_profile_get(store: CartwrightStore, args: argparse.Namespace) -> int:
    del args
    _stdout_json(store.get_profile())
    return 0


def cmd_profile_set(store: CartwrightStore, args: argparse.Namespace) -> int:
    if args.json:
        payload = json.loads(args.json)
    elif args.file:
        payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
    else:
        payload = json.loads(_read_input_text(args))
    store.set_profile(payload)
    print("profile saved")
    return 0


def cmd_list_import(store: CartwrightStore, args: argparse.Namespace) -> int:
    payload = _read_input_text(args)
    canonical_source = _normalize_source(args.source)
    if args.source == "pasted":
        items = parse_list_text(payload, "pasted_text")
    elif args.source == "screenshot":
        items = parse_connector_payload(payload, "screenshot", base_confidence=0.74)
    elif args.source == "gmail":
        items = parse_connector_payload(payload, "gmail", base_confidence=0.76)
    elif args.source == "drive":
        items = parse_connector_payload(payload, "drive", base_confidence=0.82)
    elif args.source == "alexa":
        items = parse_connector_payload(payload, "alexa", base_confidence=0.78)
    elif args.source == "keep":
        items = parse_connector_payload(payload, "keep", base_confidence=0.77)
    elif args.source in {"browser_capture", "browser"}:
        items = parse_connector_payload(payload, "browser_capture", base_confidence=0.69)
    else:
        raise ValueError(f"unsupported source {args.source}")

    list_id = store.import_items(canonical_source, items)
    _stdout_json(
        {
            "list_id": list_id,
            "imported": len(items),
            "source": canonical_source,
            "items": [item.to_dict() for item in items],
        }
    )
    return 0


def cmd_list_active(store: CartwrightStore, args: argparse.Namespace) -> int:
    del args
    items = store.get_active_items()
    _stdout_json({"items": [item.to_dict() for item in items], "count": len(items)})
    return 0


def cmd_receipts_import(store: CartwrightStore, args: argparse.Namespace) -> int:
    payload = _read_input_text(args)
    source = args.source if args.source else "gmail"
    retailer, date, items = parse_receipt_text(payload, source=source)
    store.add_receipt_items(source, retailer=retailer, items=items, receipt_date=date, raw_payload=payload)
    _stdout_json(
        {
            "retailer": retailer,
            "receipt_date": date,
            "imported": len(items),
        }
    )
    return 0


def _build_markdown(items: list[dict]) -> str:
    output = io.StringIO()
    output.write("# Cartwright Grocery List\n")
    output.write("\n")
    for idx, item in enumerate(items, start=1):
        unit = item.get("unit") or ""
        quantity = item.get("quantity") or "1"
        notes = item.get("notes")
        note_text = f" ({notes})" if notes else ""
        output.write(
            f"{idx}. {item.get('normalized_name')} - {quantity} {unit}{note_text}\n".replace("  ", " ").strip()
            + "\n"
        )
    return output.getvalue()


def _build_csv(items: list[dict]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "normalized_name",
            "quantity",
            "unit",
            "brand_preference",
            "category",
            "notes",
            "source",
        ],
    )
    writer.writeheader()
    writer.writerows(
        {
            "normalized_name": item.get("normalized_name"),
            "quantity": item.get("quantity"),
            "unit": item.get("unit"),
            "brand_preference": item.get("brand_preference"),
            "category": item.get("category"),
            "notes": item.get("notes"),
            "source": item.get("source"),
        }
        for item in items
    )
    return output.getvalue()


def cmd_export_drive(store: CartwrightStore, args: argparse.Namespace) -> int:
    plan = build_plan(store, retailer=args.retailer, constraints=args.constraints)
    items = plan.list_items
    if args.format == "markdown":
        content = _build_markdown(items)
    elif args.format == "csv":
        content = _build_csv(items)
    else:
        raise ValueError(f"unsupported format {args.format}")

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        store.log_export(store.get_active_list_id(), args.format, args.output, plan.to_dict())
        print(f"exported to {args.output}")
    else:
        print(content)
        store.log_export(store.get_active_list_id(), args.format, None, plan.to_dict())
    return 0


def cmd_groceries_plan(store: CartwrightStore, args: argparse.Namespace) -> int:
    plan = build_plan(store, retailer=args.retailer, constraints=args.constraints)
    _stdout_json(plan.to_dict())
    return 0


def cmd_connections_get(store: CartwrightStore, args: argparse.Namespace) -> int:
    _stdout_json({"connection": store.get_source_connection(args.source)})
    return 0


def cmd_connections_remember(store: CartwrightStore, args: argparse.Namespace) -> int:
    metadata = {}
    if args.url:
        metadata["url"] = args.url
    if args.label:
        metadata["label"] = args.label
    store.remember_source_connection(args.source, status=args.status, metadata=metadata)
    _stdout_json({"status": "ok", "connection": store.get_source_connection(args.source)})
    return 0


def cmd_execute(store: CartwrightStore, args: argparse.Namespace) -> int:
    playbook = build_fulfillment_playbook(
        store,
        retailer=args.retailer,
        constraints=args.constraints,
        mode=args.mode,
        browser_profile=args.browser_profile,
    )
    _stdout_json(playbook.to_dict())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cartwright")
    parser.add_argument("--db-path", default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.set_defaults(func=cmd_init)

    profile = sub.add_parser("profile")
    profile_sub = profile.add_subparsers(dest="profile_cmd", required=True)

    profile_get = profile_sub.add_parser("get")
    profile_get.set_defaults(func=cmd_profile_get)

    profile_set = profile_sub.add_parser("set")
    profile_set.add_argument("--json")
    profile_set.add_argument("--file")
    profile_set.set_defaults(func=cmd_profile_set)

    list_cmd = sub.add_parser("list")
    list_sub = list_cmd.add_subparsers(dest="list_cmd", required=True)
    import_list = list_sub.add_parser("import")
    import_list.add_argument(
        "--source",
        required=True,
        choices=["pasted", "screenshot", "gmail", "drive", "alexa", "keep", "browser_capture", "browser"],
    )
    import_list.add_argument("--text")
    import_list.add_argument("--file")
    import_list.set_defaults(func=cmd_list_import)

    list_active = list_sub.add_parser("active")
    list_active.set_defaults(func=cmd_list_active)

    receipts = sub.add_parser("receipts")
    receipts_sub = receipts.add_subparsers(dest="receipts_cmd", required=True)
    receipts_import = receipts_sub.add_parser("import")
    receipts_import.add_argument("--source", default="gmail")
    receipts_import.add_argument("--text")
    receipts_import.add_argument("--file")
    receipts_import.set_defaults(func=cmd_receipts_import)

    groceries = sub.add_parser("groceries")
    groceries_plan = groceries.add_subparsers(dest="groceries_cmd", required=True)
    groceries_plan_parser = groceries_plan.add_parser("plan")
    groceries_plan_parser.add_argument("--retailer", default="walmart")
    groceries_plan_parser.add_argument("--constraints", nargs="*", default=[])
    groceries_plan_parser.set_defaults(func=cmd_groceries_plan)

    connections = sub.add_parser("connections")
    connections_sub = connections.add_subparsers(dest="connections_cmd", required=True)

    connections_get = connections_sub.add_parser("get")
    connections_get.add_argument("--source", required=True)
    connections_get.set_defaults(func=cmd_connections_get)

    connections_remember = connections_sub.add_parser("remember")
    connections_remember.add_argument("--source", required=True)
    connections_remember.add_argument("--url")
    connections_remember.add_argument("--label")
    connections_remember.add_argument("--status", default="ready")
    connections_remember.set_defaults(func=cmd_connections_remember)

    export = sub.add_parser("export")
    export.add_argument("drive", choices=["drive"])
    export.set_defaults(func=cmd_export_drive)
    export.add_argument("--format", choices=["markdown", "csv"], default="markdown")
    export.add_argument("--retailer", default="walmart")
    export.add_argument("--constraints", nargs="*", default=[])
    export.add_argument("--output")

    execute = sub.add_parser("execute")
    execute.add_argument("--retailer", default="walmart")
    execute.add_argument("--constraints", nargs="*", default=[])
    execute.add_argument(
        "--mode",
        choices=["connector", "browser", "hybrid"],
        default="hybrid",
    )
    execute.add_argument("--browser-profile", default="default")
    execute.set_defaults(func=cmd_execute)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = CartwrightStore(get_db_path(args.db_path))
    if args.command == "init":
        return args.func(store, args)
    if args.command == "profile":
        return args.func(store, args)
    if args.command == "list":
        return args.func(store, args)
    if args.command == "receipts":
        return args.func(store, args)
    if args.command == "groceries":
        return args.func(store, args)
    if args.command == "connections":
        return args.func(store, args)
    if args.command == "export":
        return args.func(store, args)
    if args.command == "execute":
        return args.func(store, args)
    raise ValueError("unknown command")


if __name__ == "__main__":
    raise SystemExit(main())
