#!/usr/bin/env python3
"""authorship_store — author/judge separation for ctc.

The whole point of complex-test-cases is that a JUDGE must not be the AUTHOR of
the work it grades. This module is the ledger that makes that separation an
enforced FACT rather than an honor-system hope.

Every recorded case names two parties:

    author    — who WROTE the case (the rubric)
    producer  — who PRODUCED the work being graded against it

If author == producer, the case is a self-assessment with ceremony: the same
agent set the bar and cleared it. `check()` fails loudly on any such record, so
a repo cannot pass while carrying one.

Append-only. The file is `.complextestcases/authorship.jsonl`. Each line is one
JSON record. Nothing is ever edited or deleted in place.
"""

from __future__ import annotations

import json
from pathlib import Path

DIRNAME = ".complextestcases"
FILENAME = "authorship.jsonl"
SCHEMA = 1


def _store_path(root: Path) -> Path:
    return root / FILENAME


def find_root(start: Path) -> Path | None:
    """Nearest ancestor containing .complextestcases/ (returns that dir)."""
    for d in [start.resolve(), *start.resolve().parents]:
        if (d / DIRNAME).is_dir():
            return d / DIRNAME
    return None


def read(root: Path) -> list[dict]:
    f = _store_path(root)
    if not f.is_file():
        return []
    return [json.loads(ln) for ln in f.read_text().splitlines() if ln.strip()]


def record(root: Path, target: str, case: str, author: str, producer: str) -> dict:
    """Append one authorship record. author/producer are required and must be
    non-empty — an unnamed party is exactly the gap this ledger closes."""
    author = (author or "").strip()
    producer = (producer or "").strip()
    if not author or not producer:
        raise ValueError("both --author and --producer are required and non-empty")
    ev = {
        "schema": SCHEMA,
        "target": target,
        "case": case,
        "author": author,
        "producer": producer,
    }
    root.mkdir(parents=True, exist_ok=True)
    with open(_store_path(root), "a") as fh:
        fh.write(json.dumps(ev, sort_keys=True) + "\n")
    return ev


def violations(root: Path) -> list[dict]:
    """Records where author == producer — the self-graded ones."""
    return [r for r in read(root) if r.get("author") == r.get("producer")]


def check(root: Path) -> tuple[bool, list[dict]]:
    """(ok, violations). ok is True iff NO record has author == producer."""
    v = violations(root)
    return (not v, v)
