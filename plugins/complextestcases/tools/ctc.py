#!/usr/bin/env python3
"""complex-test-cases — the case authority.

Zero dependencies. Stdlib only.

    ctc init                       scaffold .complextestcases/
    ctc add <target> --name ...    author one case (before the work)
    ctc redcheck <target>          run BEFORE building; every case MUST fail
    ctc run <target>               run the suite; ledger the result
    ctc status <target>            the honest verdict
    ctc amend <target> --name ...  change a case (loud, ledgered, loses red history)
    ctc retire <target> --name ... soft-delete a case that stopped catching

WHY THIS EXISTS
===============
Every accountability system in this ecosystem is a JUDGE — converge scores target
rows, staircase gates promises, docket closes tasks, telos signals drift. Not one
of them is an AUTHOR. Every one grades work against a rubric handed to it by the
same agent whose work it is about to grade.

That is not accountability. It is a self-assessment with ceremony, and it is why
converge ships a PASS class literally named `pass_with_bypass`, and why a real
converge row can read "every tmux call is monkeypatched — these prove logic, not
real tmux behavior" and still be classed as a pass. The row confesses and the
scoreboard is indifferent, because the row IS the rubric.

The ceiling on every downstream gate is the quality of its cases. Fix the cases and
converge, staircase, docket and telos all get sharper for free. Leave them and no
amount of gate-building helps.

THE RULE
========
**A case must have been OBSERVED RED at least once.**

A test that has never failed has never been tested. It may assert something true by
construction. It may grep a string that is always present. It may be a "negative"
case that passes because the feature does not exist yet rather than because the
system correctly refused. All three are indistinguishable from a real check — until
you watch the check fail. Watching it fail is the only evidence it can detect the
absence of the thing.

Falsifiability is keyed to the case's COMMAND TEXT, not its name. So weakening a
case to make it pass turns it into a brand-new case with no red history — VACUOUS,
and it certifies nothing. The only route back to green is to be seen red first,
which means reverting the code. Honest either way.

WHERE THE DIMENSIONS CAME FROM
==============================
A nineteen-year-old buying his first car. Ask an agent to help and it will happily
find a 2019 Mustang GT inside budget, negotiate to his stated monthly payment,
and close — and the dealer will meet that payment with an 84-month term at 14% APR
plus a $2,400 F&I package. Every check the agent wrote for itself passes. The
metric moves. The outcome is a seven-year catastrophe.

Every dimension below is a way that story goes wrong, and NONE of them is a unit
test.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import authorship_store

__version__ = "0.1.0"

DIRNAME = ".complextestcases"
SCHEMA = 1

DIMENSIONS: dict[str, str] = {
    # ── the ordinary ones ────────────────────────────────────────────────────
    "happy": "the thing works on the intended path. Necessary, and worth almost "
             "nothing on its own — this is the case the builder would have "
             "written anyway.",
    "edge": "a boundary: empty, zero, max, unicode, concurrent, missing, "
            "duplicated, out of order.",
    "regression": "the specific bug this fixes, asserted to stay dead.",

    # ── the ones that actually catch things ──────────────────────────────────
    "negative": "the system must correctly REFUSE. A check that can never say no "
                "cannot meaningfully say yes. Careful: a lazy negative case "
                "passes because the call failed (feature missing) rather than "
                "because the system refused — which is exactly what redcheck "
                "catches.",

    "integration": "end-to-end through the REAL surface. No mock, no stub, no "
                   "monkeypatch. `emux-web:010` had 41 green tests and its own "
                   "delta said they proved nothing about real tmux; it passed "
                   "anyway. Mocked is not tested, it is rehearsed.",

    "adversary": "someone is actively making failure LOOK LIKE SUCCESS. The "
                 "dealer meets the monthly payment target — via 84 months at "
                 "14%. Payment target: met. Naive scoreboard: PASS. A suite "
                 "with no adversary in it tests compliance, not judgment.",

    "ordering": "every step correct, in the wrong sequence, is total failure. "
                "Insurance quoted BEFORE the signature. Inspection BEFORE the "
                "deposit. Step-level checks are structurally blind to this: "
                "each one passes while the outcome is unrecoverable.",

    "irreversible": "the point of no return, and what must be true before it. "
                    "A signature, a delete, a send, a payment. What is cheap now "
                    "and impossible later.",

    "lying_input": "the world is feeding you false data ON PURPOSE. Rolled-back "
                   "odometer. Salvage title laundered across state lines. A "
                   "suite that only supplies honest inputs has never tested the "
                   "thing that actually breaks.",

    "refusal": "THE HARDEST CASE, and the one no agent ever writes for itself: "
               "the scenario whose CORRECT OUTCOME IS DON'T. He has $12k, earns "
               "$30k, and the true cost of ownership is $9k/yr — the right answer "
               "is do not buy this car. Success here looks like not delivering "
               "the thing you were asked to deliver, so every incentive inside "
               "the task points away from writing it. It can only come from "
               "outside.",

    "unsolicited": "did the system RAISE what nobody asked about? Insurance was "
                   "never in the request. The stated task is 'buy a car'; the "
                   "real task is 'my son isn't fleeced'. This dimension has no "
                   "'target' at all — it scores what the system volunteered.",
}

# A suite that is all-happy proves the happy path and nothing else. These are the
# dimensions whose absence has actually cost us something, so they are the floor.
DEFAULT_CONFIG = {
    "schema": SCHEMA,
    "min_cases": 4,
    "require_dimensions": ["negative", "adversary", "refusal"],
    # Cases that have stopped catching anything are retired, not accumulated — a
    # suite that only grows becomes a suite nobody runs.
    "retire_after_green_runs": 50,
    # A case that hangs blocks the whole run forever. Kill it after this many
    # seconds and treat it as BROKEN (it did not complete). Generous by default;
    # a real case finishes in seconds.
    "case_timeout_sec": 300,
}


# A command that could not be EXECUTED did not fail — it never ran. The shell
# reports 127 (not found) and 126 (not executable) for exactly this.
#
# This distinction is load-bearing, and it was earned by shipping the bug: telos's
# own charter carried two "cases" that were PROSE ("assert every record in
# amendments.jsonl has a non-empty approved_by ..."). They exit 127 forever. A
# prose case is PERMANENTLY RED — visually identical to a case that is honestly
# failing — and it would satisfy a naive falsifiability check ("it was seen red!")
# while never having tested anything at all. A typo would certify a claim.
#
# So BROKEN is its own verdict, it NEVER counts as red history, and a suite that
# contains one cannot be redchecked.
# Exit codes that mean the case DID NOT RUN — its failure is ABSENT, not RED, and
# must never mint falsifiability. 127 = command not found, 126 = not executable
# (the prose-case class in the comment above). 2 = the interpreter/shell could not
# run the command at all: python "can't open file 'x'", argparse usage error, and
# a shell parse error (an unbalanced quote) all exit 2 — none of them ran the
# case's logic. A case signals a genuine red with exit 1. 124 = the case ran but
# was killed by the timeout (below): it did not complete, so it did not fail —
# BROKEN, never red. 125 = a structured case (verdict_protocol) exited without
# ever affirming a CTC_VERDICT — it crashed before judging, so it is BROKEN too.
NOT_EXECUTABLE = (2, 124, 125, 126, 127)
NO_VERDICT = 125

# A case may report exit 77 to SKIP: its environment is not available here (a gui
# case on a headless box, a case needing a service that is not running). SKIP is
# NOT a fail — a false red in CI is worse than an honest "not run here". A skipped
# case is reported, counts neither green nor vacuous, and never fails the suite.
SKIP_EXIT = 77
TIMEOUT_EXIT = 124

# A case may AFFIRM its verdict by printing `CTC_VERDICT: PASS|FAIL|SKIP`. This
# closes the crash-vs-red hole: an exit code cannot tell a judged failure
# (sys.exit(1)) from a crash (an unhandled exception also exits 1). A structured
# case (`verdict_protocol: true`) that reaches a verdict SAYS so; if it exits
# without the token it crashed before judging — BROKEN, not a false red. The
# token is authoritative when present; last one wins.
_VERDICT_RE = re.compile(r"CTC_VERDICT:\s*(PASS|FAIL|SKIP)", re.IGNORECASE)


def _verdict_token(text: str) -> str | None:
    m = list(_VERDICT_RE.finditer(text or ""))
    return m[-1].group(1).upper() if m else None


def _fail(msg: str) -> SystemExit:
    print(f"ctc: {msg}", file=sys.stderr)
    return SystemExit(2)


def find_root(start: Path) -> Path | None:
    for d in [start.resolve(), *start.resolve().parents]:
        if (d / DIRNAME).is_dir():
            return d / DIRNAME
    return None


class Suite:
    """The case ledger for one repo. Append-only; the run history IS the proof."""

    def __init__(self, root: Path):
        self.dir = root
        self.config = dict(DEFAULT_CONFIG)
        cfg = root / "config.json"
        if cfg.is_file():
            self.config.update(json.loads(cfg.read_text()))
        self.cases = self._read("cases.jsonl")
        self.runs = self._read("runs.jsonl")

    def _read(self, name: str) -> list[dict]:
        f = self.dir / name
        if not f.is_file():
            return []
        return [json.loads(ln) for ln in f.read_text().splitlines() if ln.strip()]

    def append(self, name: str, ev: dict) -> dict:
        ev = {"schema": SCHEMA, **ev}
        with open(self.dir / name, "a") as fh:
            fh.write(json.dumps(ev, sort_keys=True) + "\n")
        return ev

    # -- the suite ------------------------------------------------------------
    def suite(self, target: str) -> dict[str, dict]:
        """Current cases for a target. Later events supersede earlier ones with
        the same name — that is what an amendment IS. Retired cases drop out."""
        out: dict[str, dict] = {}
        for e in self.cases:
            if e.get("target") != target:
                continue
            if e.get("retired"):
                out.pop(e["name"], None)
            else:
                out[e["name"]] = e
        return out

    def falsifiable(self, target: str) -> set[str]:
        """Cases observed RED at least once, AGAINST THE COMMAND THEY CARRY TODAY.

        Keying on the command text is the whole tamper-resistance property: weaken
        a case to make it pass and it becomes, to this function, a new case with
        no red history. A case may go further and declare an `anchor` — the path
        to the file(s) that ARE its judge — in which case the red is only trusted
        while the judge's content hash still matches, so weakening the judge
        (while keeping the command identical) also drops the earned history."""
        suite = self.suite(target)
        live = {n: c["run"] for n, c in suite.items()}
        cur_anchor = {n: self._anchor_hash(c) for n, c in suite.items()}
        out: set[str] = set()
        for run in self.runs:
            if run.get("target") != target:
                continue
            for r in run["results"]:
                name = r["name"]
                if r["status"] != "red" or r.get("exit") in NOT_EXECUTABLE:
                    continue
                if live.get(name) != r["run"]:
                    continue
                anchor = cur_anchor.get(name)
                if anchor is not None and r.get("anchor_hash") != anchor:
                    continue          # judge changed since this red — history void
                out.add(name)
        return out

    def _anchor_hash(self, case: dict) -> str | None:
        """Content hash of the file(s) a case declares as its judge (`anchor`),
        relative to the repo root. None when the case declares no anchor."""
        anchor = case.get("anchor")
        if not anchor:
            return None
        paths = [anchor] if isinstance(anchor, str) else list(anchor)
        h = hashlib.sha256()
        for rel in sorted(paths):
            f = self.dir.parent / rel
            h.update(rel.encode())
            h.update(f.read_bytes() if f.is_file() else b"\0MISSING\0")
        return h.hexdigest()[:16]

    def execute(self, target: str, ledger: bool = True) -> list[dict]:
        s = self.suite(target)
        if not s:
            raise _fail(
                f"no cases for {target!r}. Author them BEFORE the work — that is "
                "the only moment a redcheck is possible, and a case that was "
                "never red is a case that never worked."
            )
        timeout = self.config.get("case_timeout_sec", DEFAULT_CONFIG["case_timeout_sec"])
        results = []
        for name in sorted(s):
            c = s[name]
            # shell=True is the CONTRACT here, not an oversight: a case IS a shell
            # command, authored in-repo by the owner, exactly like a pytest node id
            # or a Makefile target. There is no untrusted input path into this.
            # Run from the REPO ROOT (the dir that holds .complextestcases), not
            # from wherever the ctc process happens to sit. A case is authored
            # against its repo — `python3 tests/ctc_checks.py x`, `pytest tests/…`
            # — so a relative command only means anything from the repo root.
            # Without this, `ctc --dir <repo> run` from elsewhere makes every
            # relative case fail to open its file (exit 2) — a false red that,
            # worse, used to MINT falsifiability. See NOT_EXECUTABLE.
            try:
                p = subprocess.run(c["run"], shell=True, cwd=self.dir.parent,
                                   capture_output=True, text=True, timeout=timeout)
                code = p.returncode
                tail = (p.stderr or p.stdout or "").strip()[-200:]
                # An affirmed CTC_VERDICT is authoritative over the exit code — the
                # only way to tell a judged FAIL from a crash that also exits 1.
                token = _verdict_token(p.stdout)
                if token:
                    code = {"PASS": 0, "FAIL": 1, "SKIP": SKIP_EXIT}[token]
                elif c.get("verdict_protocol"):
                    code = NO_VERDICT    # structured case never judged → it crashed
                    tail = ("verdict_protocol case exited without a CTC_VERDICT — "
                            "BROKEN (crashed before judging). " + tail)[:200]
            except subprocess.TimeoutExpired:
                code = TIMEOUT_EXIT      # BROKEN: it did not complete, so it did not fail
                tail = f"case exceeded case_timeout_sec={timeout}s — killed, treated as BROKEN"
            status = "skip" if code == SKIP_EXIT else "green" if code == 0 else "red"
            rec = {
                "name": name, "dim": c["dim"], "run": c["run"],
                "status": status,
                "exit": code,
                "tail": tail,
            }
            # Anchor the red-history to the case's JUDGE, not just its command
            # string. A case that declares `anchor` (a path to the file(s) that
            # ARE its check) records their content hash on every run; falsifiable()
            # then only trusts a red whose anchor still matches. Weaken the judge
            # and keep the command identical — the earned red no longer counts.
            ah = self._anchor_hash(c)
            if ah is not None:
                rec["anchor_hash"] = ah
            results.append(rec)
        if ledger:
            self.append("runs.jsonl", {"target": target, "results": results})
            self.runs = self._read("runs.jsonl")
        return results

    def status(self, target: str) -> dict:
        s = self.suite(target)
        if not s:
            return {"target": target, "verdict": "NO_SUITE", "ok": False,
                    "reason": "no cases authored", "cases": [], "score": 0}
        hist = [r for r in self.runs if r.get("target") == target]
        last = {r["name"]: r for r in (hist[-1]["results"] if hist else [])}
        fals = self.falsifiable(target)

        rows = []
        for name, c in sorted(s.items()):
            r = last.get(name)
            if r is None:
                v = "UNTESTED"
            elif r.get("exit") == SKIP_EXIT or r.get("status") == "skip":
                v = "SKIPPED"
            elif r.get("exit") in NOT_EXECUTABLE:
                v = "BROKEN"
            elif r["status"] == "red":
                v = "RED"
            elif name not in fals:
                v = "VACUOUS"
            else:
                v = "GREEN"
            rows.append({"name": name, "dim": c["dim"], "verdict": v,
                         "why": c.get("why", "")})

        red = [r for r in rows if r["verdict"] == "RED"]
        broken = [r for r in rows if r["verdict"] == "BROKEN"]
        vac = [r for r in rows if r["verdict"] in ("VACUOUS", "UNTESTED")]
        green = [r for r in rows if r["verdict"] == "GREEN"]
        skipped = [r for r in rows if r["verdict"] == "SKIPPED"]
        scored = len(rows) - len(skipped)
        dims = {c["dim"] for c in s.values()}
        need = [d for d in self.config["require_dimensions"] if d not in dims]
        short = len(s) < int(self.config["min_cases"])

        # SHALLOW outranks everything: a suite missing its required dimensions is
        # not a weak suite, it is the wrong suite. Reporting "8/8 green" on a
        # suite with no refusal case and no adversary case is precisely the
        # green-checkmark-that-means-nothing this tool exists to abolish.
        if short or need:
            bits = []
            if short:
                bits.append(f"{len(s)} case(s), floor is {self.config['min_cases']}")
            if need:
                bits.append("missing dimension(s): " + ", ".join(need))
            return {**_agg(target, rows, sorted(dims)),
                    "verdict": "SHALLOW", "ok": False,
                    "reason": "; ".join(bits) + " — a suite that does not span "
                              "dimensions proves one path, not the claim. "
                              + "; ".join(f"{d}: {DIMENSIONS[d]}" for d in need)}
        if broken:
            return {**_agg(target, rows, sorted(dims)),
                    "verdict": "BROKEN", "ok": False,
                    "reason": f"{len(broken)} case(s) could not be EXECUTED "
                              "(exit 126/127): "
                              + ", ".join(r["name"] for r in broken)
                              + " — they never ran. They are not failing, they "
                                "are ABSENT, wearing a failing case's clothes. "
                                "A prose 'case' is permanently red and looks "
                                "exactly like an honest failure; a typo would "
                                "certify a claim. Write a real command."}
        if red:
            return {**_agg(target, rows, sorted(dims)),
                    "verdict": "RED", "ok": False,
                    "reason": f"{len(red)} case(s) failing: "
                              + ", ".join(r["name"] for r in red)}
        if vac:
            return {**_agg(target, rows, sorted(dims)),
                    "verdict": "VACUOUS", "ok": False,
                    "reason": f"{len(vac)} case(s) never observed RED: "
                              + ", ".join(r["name"] for r in vac)
                              + " — a check that has never caught anything has "
                                "not earned the right to certify anything. Run "
                                "`ctc redcheck` BEFORE the work."}
        return {**_agg(target, rows, sorted(dims)),
                "verdict": "GREEN", "ok": True,
                "reason": f"{len(green)}/{scored} green, all proven falsifiable, "
                          f"spanning {', '.join(sorted(dims))}"
                          + (f" ({len(skipped)} skipped — env not available here)"
                             if skipped else "")}


def _agg(target, rows, dims) -> dict:
    def n(*v):
        return sum(r["verdict"] in v for r in rows)
    green = n("GREEN")
    skipped = n("SKIPPED")
    scored = len(rows) - skipped          # a skipped case is not evaluated here
    return {
        "target": target, "cases": rows, "dims": dims,
        "green": green, "red": n("RED"), "vacuous": n("VACUOUS", "UNTESTED"),
        "skipped": skipped, "total": len(rows),
        # The honest score. VACUOUS counts as ZERO, not as green — that is the
        # entire difference between this and every scoreboard it replaces. SKIPPED
        # is neither green nor vacuous: it leaves the denominator, never inflating
        # or deflating the score with a case that did not run here.
        "score": round(100 * green / scored) if scored else 0,
    }


# ── commands ──────────────────────────────────────────────────────────────────


def load(a) -> Suite:
    root = find_root(Path(a.dir or "."))
    if root is None:
        raise _fail(f"no {DIRNAME}/ found — run `ctc init`")
    return Suite(root)


def cmd_init(a) -> int:
    root = Path(a.dir or ".") / DIRNAME
    if root.is_dir():
        raise _fail(f"{root} already exists")
    root.mkdir(parents=True)
    (root / "config.json").write_text(json.dumps(DEFAULT_CONFIG, indent=2) + "\n")
    (root / "README.md").write_text(
        "# .complextestcases\n\n"
        "The case authority for this repo.\n\n"
        "`cases.jsonl` — every case ever authored (append-only; amendments and\n"
        "retirements are events, never edits).\n"
        "`runs.jsonl` — every run ever executed. THIS IS THE PROOF: it is the only\n"
        "place a case's falsifiability can be established, because it is the only\n"
        "record of a case having been seen RED.\n\n"
        "The rule: **a case must have been observed RED at least once.** A test\n"
        "that has never failed has never been tested.\n"
    )
    print(f"ctc: initialised {root}\n"
          f"  floor: {DEFAULT_CONFIG['min_cases']} cases, must include "
          f"{', '.join(DEFAULT_CONFIG['require_dimensions'])}\n"
          "  next: `ctc add <target> --name ... --dim ... --run ... --why ...`")
    return 0


def cmd_add(a) -> int:
    s = load(a)
    if a.dim not in DIMENSIONS:
        raise _fail("--dim must be one of:\n  "
                    + "\n  ".join(f"{k:14} {v}" for k, v in DIMENSIONS.items()))
    if a.name in s.suite(a.target):
        raise _fail(
            f"case {a.name!r} already exists on {a.target!r}. Changing an "
            "authored case is an AMENDMENT, not an add — `ctc amend`. (Rewriting "
            "the test until it goes green is exactly what this refusal exists to "
            "stop, and it is the single most common way a proof gate dies.)")
    if not (a.why or "").strip():
        raise _fail("--why is required: what breaks IN THE REAL WORLD if this "
                    "case passes when it should not? A case whose author cannot "
                    "say what it protects is not protecting anything.")
    s.append("cases.jsonl", {"target": a.target, "name": a.name, "dim": a.dim,
                             "run": a.run, "why": a.why.strip()})
    st = Suite(s.dir).status(a.target)
    print(f"ctc: case {a.name!r} [{a.dim}] added to {a.target!r} "
          f"({st['total']} case(s): {', '.join(st['dims'])})")
    if st["verdict"] == "SHALLOW":
        print(f"  SHALLOW — {st['reason']}")
    print(f"  next: `ctc redcheck {a.target}` BEFORE you build. Every case must "
          "be seen RED to be worth anything green.")
    return 0


def _render(st: dict) -> None:
    for c in st["cases"]:
        mark = {"GREEN": "✓", "RED": "✗", "VACUOUS": "?", "UNTESTED": "·",
                "BROKEN": "!", "SKIPPED": "–"}[c["verdict"]]
        print(f"  {mark} {c['verdict']:8} [{c['dim']:12}] {c['name']}")
    print(f"\n{st['verdict']}: {st['reason']}")
    print(f"score: {st['score']}  (VACUOUS scores ZERO — that is the point)")


def cmd_redcheck(a) -> int:
    s = load(a)
    res = s.execute(a.target)
    green = [r for r in res if r["status"] == "green"]
    broken = [r for r in res if r["exit"] in NOT_EXECUTABLE]
    for r in res:
        print(f"  {'RED ' if r['status']=='red' else 'GREEN'} "
              f"[{r['dim']:12}] {r['name']} (exit {r['exit']})")
    if broken:
        print(f"\nRED-CHECK FAILED: {len(broken)} case(s) could NOT BE EXECUTED "
              "(exit 126/127) — " + ", ".join(r["name"] for r in broken))
        print("Those commands never ran. A case that cannot run is not a case "
              "that fails — it is an ABSENT case that will sit permanently red, "
              "indistinguishable from an honest failure, forever. Write a real "
              "command.")
        return 1
    if green:
        print(f"\nRED-CHECK FAILED: {len(green)} case(s) are ALREADY GREEN before "
              "the work exists — " + ", ".join(r["name"] for r in green))
        print("A test that passes before you build the thing does not test the "
              "thing. Most often it asserts something already true, or it is a "
              "negative case passing for the WRONG REASON — the call failed "
              "because the feature is missing, not because the system refused.")
        print("Rewrite those to assert the SPECIFIC correct behavior, then "
              "redcheck again.")
        return 1
    print(f"\nRED-CHECK PASSED: {len(res)}/{len(res)} cases RED. Every case is "
          "proven capable of failing — now their green will mean something. "
          "Go build.")
    return 0


def cmd_run(a) -> int:
    s = load(a)
    s.execute(a.target)
    st = Suite(s.dir).status(a.target)
    _render(st)
    if a.json:
        print(json.dumps(st, indent=2))
    return 0 if st["ok"] else 1


def cmd_status(a) -> int:
    s = load(a)
    st = s.status(a.target)
    _render(st)
    if a.json:
        print(json.dumps(st, indent=2))
    return 0 if st["ok"] else 1


def cmd_amend(a) -> int:
    """Change an authored case. Deliberately loud.

    The amended case LOSES ITS RED HISTORY, because falsifiability is keyed to the
    command text. So a case weakened to make it pass has no proof it can fail, is
    VACUOUS, and cannot certify anything — until it is seen red again, which (if
    the code already works) means reverting the code. There is no path from
    'weaken the test' to 'green'."""
    s = load(a)
    old = s.suite(a.target).get(a.name)
    if not old:
        raise _fail(f"no case {a.name!r} on {a.target!r} — use `ctc add`")
    if not (a.reason or "").strip():
        raise _fail("--reason is required. A gate changed without a stated "
                    "reason is not an amendment, it is drift.")
    s.append("cases.jsonl", {
        "target": a.target, "name": a.name, "dim": a.dim or old["dim"],
        "run": a.run, "why": a.why or old.get("why", ""),
        "amended": True, "was": old["run"], "reason": a.reason.strip(),
        "by": a.by or "unknown"})
    print(f"ctc: case {a.name!r} AMENDED on {a.target!r} by {a.by or 'unknown'}\n"
          f"  was: {old['run']}\n  now: {a.run}\n")
    print("  This case now has NO RED HISTORY under its new command — it is "
          "VACUOUS until observed failing again. If the implementation already "
          "makes it pass, it cannot certify anything: a check that has never "
          "caught anything has not earned the right to certify anything.")
    return 0


def cmd_retire(a) -> int:
    """Soft-delete a case that has stopped catching. It stays in the ledger."""
    s = load(a)
    if a.name not in s.suite(a.target):
        raise _fail(f"no live case {a.name!r} on {a.target!r}")
    if not (a.reason or "").strip():
        raise _fail("--reason is required")
    s.append("cases.jsonl", {"target": a.target, "name": a.name, "retired": True,
                             "reason": a.reason.strip(), "by": a.by or "unknown"})
    print(f"ctc: case {a.name!r} RETIRED from {a.target!r} (soft — it stays in "
          "cases.jsonl). A suite that only grows becomes a suite nobody runs.")
    return 0


def cmd_authorship(a) -> int:
    """Author/judge separation ledger.

    The rest of this tool proves a case can FAIL. This proves the case and the
    work had DIFFERENT hands — the one property a self-graded suite can never
    have. `--check` (or `check`) exits nonzero if any recorded case was authored
    by the same party that produced the work it grades."""
    root = authorship_store.find_root(Path(a.dir or "."))
    if root is None:
        # For --check on a repo with no store yet, there are no violations, but
        # the charter guarantees the file exists. Be explicit rather than silent.
        raise _fail(f"no {DIRNAME}/ found — run `ctc init`")

    if a.action == "record":
        try:
            ev = authorship_store.record(
                root, a.target, a.case, a.author, a.producer)
        except ValueError as e:
            raise _fail(str(e))
        same = ev["author"] == ev["producer"]
        print(f"ctc: authorship recorded for {ev['case']!r} on {ev['target']!r}\n"
              f"  author:   {ev['author']}\n  producer: {ev['producer']}")
        if same:
            print("  WARNING: author == producer — this is a self-assessment. "
                  "`ctc authorship --check` will now FAIL until it is corrected.")
        return 0

    # check (either the `check` subaction or the --check flag)
    ok, viol = authorship_store.check(root)
    total = len(authorship_store.read(root))
    if ok:
        print(f"ctc: authorship OK — {total} record(s), none self-graded "
              "(author != producer everywhere).")
        return 0
    print(f"ctc: AUTHORSHIP VIOLATION — {len(viol)} case(s) authored by their own "
          "producer:", file=sys.stderr)
    for r in viol:
        print(f"  ✗ {r.get('case')!r} on {r.get('target')!r}: "
              f"author == producer == {r.get('author')!r}", file=sys.stderr)
    print("A case whose author is also the producer of the graded work is a "
          "self-assessment with ceremony — the exact failure this tool exists to "
          "abolish. Re-author it with an independent party.", file=sys.stderr)
    return 1


def cmd_dimensions(_a) -> int:
    for k, v in DIMENSIONS.items():
        print(f"\n{k}\n  {v}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="ctc",
        description="complex-test-cases — a case must have been seen RED")
    ap.add_argument("--dir", help="repo root (default: cwd)")
    ap.add_argument("--version", action="version",
                    version=f"%(prog)s {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help=f"scaffold {DIRNAME}/")
    s.set_defaults(fn=cmd_init)

    s = sub.add_parser("dimensions", help="what the dimensions mean, and why")
    s.set_defaults(fn=cmd_dimensions)

    s = sub.add_parser("add", help="author a case (BEFORE the work)")
    s.add_argument("target")
    s.add_argument("--name", required=True)
    s.add_argument("--dim", required=True, choices=list(DIMENSIONS))
    s.add_argument("--run", required=True, help="shell cmd; exit 0 iff satisfied")
    s.add_argument("--why", required=True,
                   help="what breaks in the real world if this wrongly passes")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("redcheck",
                       help="run BEFORE building — every case MUST fail")
    s.add_argument("target")
    s.set_defaults(fn=cmd_redcheck)

    s = sub.add_parser("run", help="run the suite and ledger the result")
    s.add_argument("target")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("status", help="the honest verdict")
    s.add_argument("target")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("amend", help="change a case (loud; loses red history)")
    s.add_argument("target")
    s.add_argument("--name", required=True)
    s.add_argument("--run", required=True)
    s.add_argument("--dim", choices=list(DIMENSIONS))
    s.add_argument("--why")
    s.add_argument("--reason", required=True)
    s.add_argument("--by")
    s.set_defaults(fn=cmd_amend)

    s = sub.add_parser("retire", help="soft-delete a case that stopped catching")
    s.add_argument("target")
    s.add_argument("--name", required=True)
    s.add_argument("--reason", required=True)
    s.add_argument("--by")
    s.set_defaults(fn=cmd_retire)

    # authorship: author/judge separation. `--check` and the `check` subaction
    # are the same thing; `record` appends a new (author, producer) pair.
    s = sub.add_parser("authorship",
                       help="author/judge separation ledger (record / --check)")
    s.add_argument("--check", dest="action", action="store_const", const="check",
                   help="exit 0 iff no recorded case has author == producer")
    s.set_defaults(fn=cmd_authorship, action="check", target=None,
                   case=None, author=None, producer=None)
    asub = s.add_subparsers(dest="action")
    r = asub.add_parser("record", help="record who authored a case vs produced the work")
    r.add_argument("target")
    r.add_argument("--case", required=True, help="the case name this covers")
    r.add_argument("--author", required=True, help="who WROTE the case")
    r.add_argument("--producer", required=True, help="who PRODUCED the graded work")
    r.set_defaults(fn=cmd_authorship, action="record")
    c = asub.add_parser("check", help="exit 0 iff no case has author == producer")
    c.set_defaults(fn=cmd_authorship, action="check")

    a = ap.parse_args(argv)
    try:
        return a.fn(a)
    except SystemExit as e:
        return int(e.code or 2)


if __name__ == "__main__":
    sys.exit(main())
