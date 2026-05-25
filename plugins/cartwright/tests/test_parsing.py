from __future__ import annotations

from cartwright.parsing import parse_line_to_item, parse_list_text, dedupe_items
from cartwright.models import CanonicalItem


def test_parse_pasted_line_with_quantity():
    item = parse_line_to_item("2 gallons 2% milk", source="pasted_text")
    assert item is not None
    assert item.normalized_name == "2% milk"
    assert item.quantity == "2"
    assert item.unit == "gallon"
    assert item.confidence == 0.93


def test_parse_list_text_keeps_notes_and_brands():
    items = parse_list_text("Milk, no oat milk\n1 gallon orange juice", source="pasted_text")
    assert len(items) == 2
    assert items[0].notes == "no oat milk"
    assert items[1].normalized_name == "orange juice"
    assert items[1].unit == "gallon"
    assert items[1].quantity == "1"


def test_dedupe_items_merges_duplicate_quantities():
    items = [
        CanonicalItem("pasted_text", "2 bananas", "bananas", "2", None, None, False, "produce", None, 0.9),
        CanonicalItem("pasted_text", "3 bananas", "bananas", "3", None, None, False, "produce", None, 0.8),
        CanonicalItem("pasted_text", "2 apples", "apples", "2", None, None, False, "produce", None, 0.95),
    ]
    merged = dedupe_items(items)
    merged_names = sorted(item.normalized_name for item in merged)
    assert merged_names == ["apples", "bananas"]
    merged_bananas = next(item for item in merged if item.normalized_name == "bananas")
    assert merged_bananas.quantity == "5"
