from __future__ import annotations

import re
from datetime import datetime

from .models import CanonicalItem
from .parsing import guess_category, normalize_name, parse_line_to_item

_RECEIPT_HEADER_WORDS = [
    "receipt",
    "order",
    "subtotal",
    "total",
    "tax",
    "card",
    "visa",
    "mastercard",
    "thanks",
    "thank",
    "refund",
]

_DATE_RE = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\w+ \d{1,2}, \d{4})"
)


def parse_receipt_text(raw_text: str, source: str = "gmail") -> tuple[str | None, str | None, list[CanonicalItem]]:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    retailer = None
    receipt_date = None
    for line in lines[:12]:
        low = line.lower()
        for keyword in ("walmart", "target", "kroger", "aldi", "costco", "instacart", "wegmans"):
            if keyword in low and not retailer:
                retailer = keyword.title()
                break
        if receipt_date is None:
            match = _DATE_RE.search(line)
            if match:
                receipt_date = _normalize_date(match.group("date"))
    items: list[CanonicalItem] = []
    for line in lines:
        low = line.lower()
        # Skip date-like lines and obvious non-item lines.
        if re.match(r"^\d{4}-\d{2}-\d{2}$", line):
            continue
        if any(stop in low for stop in _RECEIPT_HEADER_WORDS):
            continue
        if " " not in line and _DATE_RE.search(line):
            continue
        # Skip address and payment noise.
        if "@" in low or "address" in low or "balance" in low:
            continue
        if any(x in low for x in ("thank", "card", "paid", "payment", "subtotal", "shipping", "tax", "total")):
            continue
        line = re.sub(r"\s+\$\s*\d+(?:\.\d{2})?\s*$", "", line)
        item = parse_line_to_item(line, source=source, base_confidence=0.87, normalize_plural=False)
        if not item:
            continue
        name = normalize_name(item.normalized_name)
        if not name:
            continue
        # Avoid numeric only or generic header tokens.
        if len(name) < 2 or name in {"item", "delivery", "service", "pickup", "order"}:
            continue
        item = CanonicalItem(
            source=item.source,
            raw_text=item.raw_text,
            normalized_name=name,
            quantity=item.quantity or "1",
            unit=item.unit,
            brand_preference=item.brand_preference,
            must_match_brand=False,
            category=guess_category(name),
            notes="from_receipt",
            confidence=item.confidence,
        )
        items.append(item)
    return retailer, receipt_date, items


def _normalize_date(value: str) -> str | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y"):
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.date().isoformat()
        except ValueError:
            continue
    return None
