from __future__ import annotations

import json
import re
from collections.abc import Iterable
from typing import Any

from .models import CanonicalItem, ItemSource

_QUANTITY_UNIT_RE = re.compile(
    r"^(?P<quantity>\d+(?:\.\d+)?|\d+/\d+)?\s*"
    r"(?P<unit>lb|lbs|oz|g|kg|ml|l|liter|liters|gallon|gallons|qt|quarts|pack|pkg|bag|bunch|bottle|can|canister|ct|count)?\b"
    r"\s*(?:of\s+|x\s+|×\s*)?(?P<item>.*)$",
    re.IGNORECASE,
)

_BRAINS = {
    "dairy": {"milk", "butter", "cheese", "eggs", "yogurt", "cream", "yogurt"},
    "produce": {"apple", "apples", "banana", "bananas", "lettuce", "spinach", "carrot", "carrots", "veg", "vegetable", "vegetables"},
    "produce_alt": {"broccoli", "cucumber", "tomato", "tomatoes"},
    "bakery": {"bread", "bagel", "bagels"},
    "meat": {"chicken", "beef", "pork", "turkey"},
    "pantry": {"rice", "beans", "pasta", "flour", "sugar", "salt", "pepper"},
    "snacks": {"chips", "crackers", "nuts"},
    "beverages": {"juice", "water", "soda", "milk"},
}

_CATEGORY_ORDER = [
    ("dairy", _BRAINS["dairy"]),
    ("produce", set.union(_BRAINS["produce"], _BRAINS["produce_alt"])),
    ("bakery", _BRAINS["bakery"]),
    ("meat", _BRAINS["meat"]),
    ("pantry", _BRAINS["pantry"]),
    ("snacks", _BRAINS["snacks"]),
    ("beverages", _BRAINS["beverages"]),
]


def _normalize_plural(word: str) -> str:
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("es"):
        if word[-3] in ("h", "s", "x", "z", "c", "o"):
            return word[:-2]
        return word[:-1]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _normalize_unit(unit: str | None) -> str | None:
    if not unit:
        return None
    u = unit.lower()
    if u in {"gallons"}:
        return "gallon"
    if u in {"lbs"}:
        return "lb"
    return u

def normalize_name(value: str) -> str:
    value = re.sub(r"\(.*?\)", "", value)
    value = re.sub(r"\b(of|x|×)\b", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value)
    return value.strip().lower()


def _split_notes(raw: str) -> tuple[str, str | None]:
    for delimiter in (";", ","):
        note_parts = [seg.strip(" -") for seg in raw.split(delimiter, 1)]
        if len(note_parts) > 1 and note_parts[1]:
            return note_parts[0], note_parts[1]
    if len(note_parts) == 1:
        bracket = re.match(r"^(?P<item>.*)\((?P<note>.+)\)\s*$", raw)
        if bracket:
            return bracket.group("item").strip(), bracket.group("note").strip()
        return raw.strip(), None
    return note_parts[0], note_parts[1]


def guess_category(name: str) -> str:
    normalized = normalize_name(name)
    token = normalized.split()[0] if normalized else ""
    for category, terms in _CATEGORY_ORDER:
        if token in terms or any(term in normalized for term in terms):
            return category
    return "uncategorized"


def parse_line_to_item(
    raw_line: str,
    source: ItemSource,
    base_confidence: float = 0.93,
    normalize_plural: bool = True,
) -> CanonicalItem | None:
    line = raw_line.strip().lstrip("-*•")
    if not line:
        return None

    item_part, note = _split_notes(line)
    match = _QUANTITY_UNIT_RE.match(item_part)
    quantity = "1"
    unit = None
    item_text = item_part
    if match:
        quantity = (match.group("quantity") or "1").strip()
        unit = _normalize_unit(match.group("unit"))
        item_text = match.group("item").strip()
        if not item_text:
            item_text = item_part
    raw_text = line.strip()
    normalized_name = normalize_name(item_text)
    if normalize_plural:
        normalized_name = _normalize_plural(normalized_name)
    if not normalized_name:
        return None
    category = guess_category(normalized_name)
    brand_preference = None
    must_match_brand = False
    brand_match = re.match(r"^brand\\s*[:=]\\s*(?P<brand>[\\w&][\\w\\s&-]{1,40})\\s+(?P<name>.+)$", item_text, re.IGNORECASE)
    if brand_match:
        brand_preference = brand_match.group("brand").strip().lower()
        normalized_name = _normalize_plural(normalize_name(brand_match.group("name")))
        category = guess_category(normalized_name)
        must_match_brand = True
    return CanonicalItem(
        source=source,
        raw_text=raw_text,
        normalized_name=normalized_name,
        quantity=quantity,
        unit=unit,
        brand_preference=brand_preference,
        must_match_brand=must_match_brand,
        category=category,
        notes=note,
        confidence=min(1.0, base_confidence),
    )


def parse_list_text(
    text: str,
    source: ItemSource,
    base_confidence: float = 0.93,
    normalize_plural: bool = True,
) -> list[CanonicalItem]:
    text = text.replace("\\r\\n", "\n").replace("\\n", "\n")
    raw_lines = re.split(r"\n+", text.strip())
    items: list[CanonicalItem] = []
    for raw in raw_lines:
        item = parse_line_to_item(
            raw,
            source=source,
            base_confidence=base_confidence,
            normalize_plural=normalize_plural,
        )
        if item:
            items.append(item)
    return items


def _extract_strings(payload: Any) -> Iterable[str]:
    if payload is None:
        return []
    if isinstance(payload, str):
        yield payload
        return
    if isinstance(payload, list):
        for item in payload:
            yield from _extract_strings(item)
        return
    if isinstance(payload, dict):
        for key in ("text", "raw_text", "content", "items", "value", "body", "contentText"):
            if key in payload:
                yield from _extract_strings(payload[key])
        # Some connectors return row maps; fall back to all values.
        for value in payload.values():
            yield from _extract_strings(value)
        return
    yield str(payload)


def parse_connector_payload(payload_text: str, source: ItemSource, base_confidence: float = 0.8) -> list[CanonicalItem]:
    payload: object
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        payload = payload_text

    items: list[CanonicalItem] = []
    for candidate in _extract_strings(payload):
        for part in re.split(r"\r?\n+", candidate):
            part = part.strip()
            if not part:
                continue
            item = parse_line_to_item(part, source=source, base_confidence=base_confidence)
            if item:
                items.append(item)
    return items


def dedupe_items(items: list[CanonicalItem]) -> list[CanonicalItem]:
    merged: dict[str, CanonicalItem] = {}
    for item in items:
        key = item.merge_key()
        if key not in merged:
            merged[key] = item
            continue
        merged[key] = _merge_two_items(merged[key], item)
    return list(merged.values())


def _coerce_quantity(value: str) -> float:
    try:
        if "/" in value and value.count("/") == 1:
            top, bottom = value.split("/", 1)
            return float(top) / float(bottom)
        return float(value)
    except (ValueError, TypeError):
        return 1.0


def _merge_quantities(a: str, b: str) -> str:
    a_num = _coerce_quantity(a)
    b_num = _coerce_quantity(b)
    merged = a_num + b_num
    if merged.is_integer():
        return str(int(merged))
    return str(merged)


def _merge_two_items(a: CanonicalItem, b: CanonicalItem) -> CanonicalItem:
    merged_quantity = _merge_quantities(a.quantity, b.quantity)
    best_notes = (a.notes or "") + ((" | " + b.notes) if b.notes else "")
    if best_notes == " | ":
        best_notes = None
    if b.confidence > a.confidence:
        winner = b
    else:
        winner = a
    return CanonicalItem(
        source=winner.source,
        raw_text=f"{a.raw_text}; {b.raw_text}",
        normalized_name=winner.normalized_name,
        quantity=merged_quantity,
        unit=winner.unit or a.unit,
        brand_preference=winner.brand_preference or a.brand_preference,
        must_match_brand=winner.must_match_brand or a.must_match_brand,
        category=winner.category,
        notes=best_notes,
        confidence=max(a.confidence, b.confidence),
    )
