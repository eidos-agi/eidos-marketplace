#!/usr/bin/env python3
"""Convert pytest/JUnit XML into portable Converge rows."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


CLASS_RANK = {"pass": 0, "skip": 1, "blocked": 2, "fail": 3}


def child_named(element: ET.Element, suffix: str) -> ET.Element | None:
    for child in list(element):
        if child.tag == suffix or child.tag.endswith(f"}}{suffix}"):
            return child
    return None


def child_text(child: ET.Element | None) -> str:
    if child is None:
        return ""
    pieces = []
    message = child.attrib.get("message", "").strip()
    if message:
        pieces.append(message)
    text = (child.text or "").strip()
    if text and text not in pieces:
        pieces.append(text)
    return "\n".join(pieces)


def testcase_status(testcase: ET.Element) -> tuple[str, str, str, str]:
    failure = child_named(testcase, "failure")
    if failure is not None:
        detail = child_text(failure)
        return "fail", "fail", detail, "Fix the failing pytest case and rerun it."

    error = child_named(testcase, "error")
    if error is not None:
        detail = child_text(error)
        return "error", "blocked", detail, "Unblock the errored pytest case and rerun it."

    skipped = child_named(testcase, "skipped")
    if skipped is not None:
        detail = child_text(skipped)
        return "skipped", "skip", detail, "Decide whether this skipped test is required for the north star."

    return "pass", "pass", "", ""


def testcase_to_row(testcase: ET.Element) -> dict[str, Any]:
    classname = testcase.attrib.get("classname") or testcase.attrib.get("file") or "unknown"
    name = testcase.attrib.get("name") or "(unnamed)"
    file_path = testcase.attrib.get("file", "")
    probe, row_class, detail, next_action = testcase_status(testcase)
    target_id = f"pytest:{classname}::{name}"
    evidence_bits = [target_id]
    if file_path:
        evidence_bits.append(file_path)
    if detail:
        evidence_bits.append(detail)

    return {
        "target_id": target_id,
        "target": "pass",
        "probe": probe,
        "delta": detail,
        "class": row_class,
        "evidence": " | ".join(evidence_bits),
        "next_action": next_action,
        "adapter": "pytest",
        "convergence_style": "regression_hardening",
        "required": row_class != "skip",
        "weight": 1,
    }


def junit_rows(path: Path) -> list[dict[str, Any]]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"could not parse JUnit XML {path}: {exc}") from exc
    rows = [testcase_to_row(testcase) for testcase in root.iter() if testcase.tag == "testcase" or testcase.tag.endswith("}testcase")]
    return sorted(rows, key=lambda row: (row["target_id"], CLASS_RANK.get(str(row["class"]), 99)))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--junit", required=True, help="Path to pytest JUnit XML output.")
    parser.add_argument("--out", help="Optional path to write Converge rows JSON.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    rows = junit_rows(Path(args.junit))
    payload = json.dumps(rows, indent=2)
    if args.out:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        print(f"pytest_adapter.py: {exc}", file=sys.stderr)
        raise SystemExit(1)
