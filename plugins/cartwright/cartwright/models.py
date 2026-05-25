from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ItemSource = Literal[
    "pasted_text",
    "screenshot",
    "gmail",
    "drive",
    "keep",
    "alexa",
    "walmart",
    "browser_capture",
]


@dataclass(frozen=True)
class CanonicalItem:
    source: ItemSource
    raw_text: str
    normalized_name: str
    quantity: str
    unit: str | None
    brand_preference: str | None
    must_match_brand: bool
    category: str
    notes: str | None
    confidence: float

    def merge_key(self) -> str:
        return f"{self.normalized_name}|{self.category}|{(self.brand_preference or '').lower()}"

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "raw_text": self.raw_text,
            "normalized_name": self.normalized_name,
            "quantity": self.quantity,
            "unit": self.unit,
            "brand_preference": self.brand_preference,
            "must_match_brand": self.must_match_brand,
            "category": self.category,
            "notes": self.notes,
            "confidence": self.confidence,
        }
