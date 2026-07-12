#!/usr/bin/env python3
"""ctc_anchor — anchor the falsifiability record so a red-history cannot be forged.

Zero dependencies. Stdlib only.

    ctc_anchor.py --seal        seal the current runs.jsonl (write runs.sealed)
    ctc_anchor.py --verify      exit 0 iff runs.jsonl matches the seal
    ctc_anchor.py --self-test   prove the check bites (seal → 0, tamper → nonzero)

WHY THIS EXISTS
===============
`ctc` proves a case is worth something by proving it was OBSERVED RED at least
once, and that proof lives in `.complextestcases/runs.jsonl`. But that file is a
plain local file. Anyone who can run `ctc run` can also open runs.jsonl in an
editor and hand-write a red result that never happened — forging the red history
that turns a VACUOUS case into a GREEN one. The whole gate is only as honest as
that file is un-forgeable.

WHAT WOULD NOT WORK
===================
A self-recomputable hash chain does NOT fix this. If the producer can run the
chaining code, the producer can re-chain any doctored file and the chain still
verifies. A tamper check whose key material is entirely inside the tamperer's
reach is theatre — it detects accidental corruption, never a motivated forger.

THE HONEST ANCHOR
=================
The seal must bind to something OUTSIDE the producer's silent reach. Git is that
anchor: on `--seal` we write a detached digest of runs.jsonl to `runs.sealed`, a
file INTENDED TO BE COMMITTED AND PUSHED. Once that commit is pushed, the sealed
digest lives in history that a forger cannot silently rewrite — a later edit to
runs.jsonl no longer matches the committed seal, and the divergence is visible to
anyone (a reviewer, CI, `git log`) who did not do the editing.

`runs.sealed` on its own local disk is only a convenience; it becomes a true
anchor the moment it is committed and pushed. `--seal` says so, loudly, every
time. This tool cannot force the commit — it can only make the un-committed state
obvious and make the committed state check out.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

DIRNAME = ".complextestcases"
RUNS = "runs.jsonl"
SEALED = "runs.sealed"
SCHEMA = 1


def find_root(start: Path) -> Path | None:
    """Nearest ancestor containing .complextestcases/ (same rule as ctc)."""
    for d in [start.resolve(), *start.resolve().parents]:
        if (d / DIRNAME).is_dir():
            return d
    return None


def digest_file(path: Path) -> str:
    """SHA-256 of the raw bytes of runs.jsonl. Any edit — a forged red result, a
    deleted line, a reordered run — changes these bytes and thus this digest."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def git_head(root: Path) -> str | None:
    try:
        p = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True,
        )
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, ValueError):
        return None


def seal(root: Path) -> int:
    runs = root / DIRNAME / RUNS
    if not runs.is_file():
        print(f"ctc_anchor: no {DIRNAME}/{RUNS} to seal — run `ctc run` first",
              file=sys.stderr)
        return 2
    dg = digest_file(runs)
    sealed = root / SEALED
    record = {
        "schema": SCHEMA,
        "algo": "sha256",
        "path": f"{DIRNAME}/{RUNS}",
        "digest": dg,
        "bytes": runs.stat().st_size,
        "sealed_at_head": git_head(root),
    }
    sealed.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(f"ctc_anchor: sealed {DIRNAME}/{RUNS}")
    print(f"  sha256: {dg}")
    print(f"  wrote:  {sealed}")
    print()
    print("  NOT YET ANCHORED. A seal on local disk that the same hand can rewrite")
    print("  is not an anchor. To make the red-history un-forgeable you MUST:")
    print(f"      git add {SEALED} && git commit -m 'seal falsifiability record'")
    print("      git push")
    print("  Only once this seal is in pushed history can a later edit to")
    print(f"  {DIRNAME}/{RUNS} be caught — the committed digest will no longer")
    print("  match the tampered file, and the divergence is visible to everyone")
    print("  who did not do the editing.")
    return 0


def verify(root: Path, quiet: bool = False) -> int:
    runs = root / DIRNAME / RUNS
    sealed = root / SEALED

    def say(msg: str, err: bool = False) -> None:
        if not quiet:
            print(msg, file=sys.stderr if err else sys.stdout)

    if not sealed.is_file():
        say(f"ctc_anchor: no {SEALED} — nothing sealed yet. Run `--seal`.", err=True)
        return 3
    if not runs.is_file():
        say(f"ctc_anchor: {DIRNAME}/{RUNS} is missing but a seal exists — the "
            "record was DELETED after sealing.", err=True)
        return 4
    try:
        record = json.loads(sealed.read_text())
    except (OSError, ValueError) as e:
        say(f"ctc_anchor: {SEALED} is unreadable: {e}", err=True)
        return 5

    want = record.get("digest")
    got = digest_file(runs)
    if want == got:
        say(f"ctc_anchor: VERIFIED — {DIRNAME}/{RUNS} matches the seal (sha256 "
            f"{got[:12]}…). Untampered since sealing.")
        say("  (Anchor is only as strong as the seal's git history. If runs.sealed")
        say("   is committed and pushed, this proof is un-forgeable.)")
        return 0
    say("ctc_anchor: TAMPERED — the falsifiability record no longer matches the "
        "seal.", err=True)
    say(f"  sealed sha256: {want}", err=True)
    say(f"  actual sha256: {got}", err=True)
    say(f"  {DIRNAME}/{RUNS} was edited after it was sealed. Any red-history it "
        "now claims is unproven. Re-run `ctc run` to regenerate honestly, then "
        "`--seal` and commit.", err=True)
    return 1


def self_test() -> int:
    """Prove the check BITES: in a throwaway repo, seal a record, verify it passes
    (exit 0), then tamper the record and verify it FAILS (nonzero). A verify that
    cannot go nonzero is exactly the theatre this tool exists to abolish — so the
    self-test refuses to pass unless it has watched the check fail."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ccdir = root / DIRNAME
        ccdir.mkdir()
        runs = ccdir / RUNS
        # A plausible runs.jsonl: one run with a real red result.
        runs.write_text(
            json.dumps({"schema": 1, "target": "demo", "results": [
                {"name": "refuses_bad", "dim": "refusal", "run": "false",
                 "status": "red", "exit": 1, "tail": "denied"}]},
                sort_keys=True) + "\n")

        # 1. seal
        if seal(root) != 0:
            print("SELF-TEST FAILED: seal did not succeed", file=sys.stderr)
            return 1
        if not (root / SEALED).is_file():
            print("SELF-TEST FAILED: seal produced no runs.sealed", file=sys.stderr)
            return 1

        # 2. verify freshly-sealed → MUST be 0
        rc = verify(root, quiet=True)
        if rc != 0:
            print(f"SELF-TEST FAILED: verify on a freshly-sealed repo returned "
                  f"{rc}, expected 0", file=sys.stderr)
            return 1

        # 3. tamper: forge a green result the run never produced
        forged = runs.read_text() + json.dumps(
            {"schema": 1, "target": "demo", "results": [
                {"name": "refuses_bad", "dim": "refusal", "run": "false",
                 "status": "red", "exit": 1, "tail": "FORGED"}]},
            sort_keys=True) + "\n"
        runs.write_text(forged)

        # 4. verify tampered → MUST be nonzero, or the check is theatre
        rc = verify(root, quiet=True)
        if rc == 0:
            print("SELF-TEST FAILED: verify returned 0 on a TAMPERED record — the "
                  "check does not bite, which is worse than no check.",
                  file=sys.stderr)
            return 1

        # 5. deletion is also tampering
        runs.unlink()
        rc = verify(root, quiet=True)
        if rc == 0:
            print("SELF-TEST FAILED: verify returned 0 when the record was "
                  "DELETED after sealing.", file=sys.stderr)
            return 1

    print("SELF-TEST PASSED:")
    print("  • freshly-sealed record verifies (exit 0)")
    print("  • record tampered after sealing FAILS verification (nonzero)")
    print("  • record deleted after sealing FAILS verification (nonzero)")
    print("The check bites. A forged red-history cannot pass verification against")
    print("a committed seal.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="ctc_anchor",
        description="Anchor the ctc falsifiability record against forgery.")
    ap.add_argument("--dir", help="repo root (default: nearest .complextestcases/)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--seal", action="store_true",
                   help="digest runs.jsonl into runs.sealed (then commit + push)")
    g.add_argument("--verify", action="store_true",
                   help="exit 0 iff runs.jsonl matches the seal, nonzero if edited")
    g.add_argument("--self-test", action="store_true",
                   help="prove the check bites: seal→0, tamper→nonzero")
    a = ap.parse_args(argv)

    if a.self_test:
        return self_test()

    start = Path(a.dir) if a.dir else Path(".")
    root = find_root(start)
    if root is None:
        print(f"ctc_anchor: no {DIRNAME}/ found from {start.resolve()} — "
              "run `ctc init` first", file=sys.stderr)
        return 2

    if a.seal:
        return seal(root)
    return verify(root)


if __name__ == "__main__":
    sys.exit(main())
