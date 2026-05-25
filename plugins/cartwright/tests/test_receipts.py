from __future__ import annotations

from cartwright.receipts import parse_receipt_text


def test_parse_receipt_reduces_to_shopping_items():
    text = """
    Walmart Receipt
    2026-05-20
    2 bananas  $3.00
    1 gallon milk  $4.50
    SUBTOTAL 7.50
    """
    retailer, date, items = parse_receipt_text(text, source="gmail")
    assert retailer == "Walmart"
    assert date == "2026-05-20"
    names = [i.normalized_name for i in items]
    assert "bananas" in names
    assert "milk" in names
    assert all(i.confidence >= 0.8 for i in items)
