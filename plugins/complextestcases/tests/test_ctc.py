"""Every test here is a way a proof gate dies."""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import ctc  # noqa: E402


def _suite(tmp_path) -> ctc.Suite:
    d = tmp_path / ctc.DIRNAME
    d.mkdir()
    (d / "config.json").write_text(json.dumps(ctc.DEFAULT_CONFIG))
    return ctc.Suite(d)


def _add(s, target, name, dim, run, why="because"):
    s.append("cases.jsonl", {"target": target, "name": name, "dim": dim,
                             "run": run, "why": why})
    return ctc.Suite(s.dir)


# ── THE RULE ──────────────────────────────────────────────────────────────────


def test_a_case_never_seen_red_is_vacuous(tmp_path):
    """The keystone. A check that has never caught anything has not earned the
    right to certify anything — even though it is passing right now."""
    s = _add(_suite(tmp_path), "t", "always_true", "negative", "true")
    s.execute("t")                       # green on its first and only run
    st = ctc.Suite(s.dir).status("t")
    assert st["cases"][0]["verdict"] == "VACUOUS"
    assert st["score"] == 0, "a vacuous suite must score ZERO, not green"


def test_a_case_seen_red_then_green_is_honest(tmp_path):
    """Red-before-green. The case proved it can fail, so its green means
    something."""
    flag = tmp_path / "built"
    s = _add(_suite(tmp_path), "t", "real", "negative", f"test -f {flag}")
    s.execute("t")                       # RED — the thing isn't built
    assert ctc.Suite(s.dir).status("t")["cases"][0]["verdict"] == "RED"
    flag.touch()                         # build it
    s2 = ctc.Suite(s.dir)
    s2.execute("t")
    assert ctc.Suite(s.dir).status("t")["cases"][0]["verdict"] == "GREEN"


def test_the_lazy_negative_case_is_caught_by_redcheck(tmp_path):
    """The case an agent writes for itself, every time.

    `! ./validate.sh garbage` — "it should fail on bad input." It is GREEN before
    the validator exists, because the script isn't there, the call fails, and `!`
    flips that into a pass. It passes for the WRONG REASON and would ship green
    forever. Redcheck catches it at authoring time, for free.
    """
    s = _add(_suite(tmp_path), "v", "lazy", "negative",
             "! ./validate.sh garbage 2>/dev/null")
    res = s.execute("v")
    assert res[0]["status"] == "green", (
        "the lazy negative case is green before the feature exists — that IS the "
        "bug this tool exists to surface"
    )


# ── TAMPERING ─────────────────────────────────────────────────────────────────


def test_weakening_a_case_to_make_it_pass_erases_its_red_history(tmp_path):
    """The single most common way a proof gate dies, and it dies silently.

    Falsifiability is keyed to the COMMAND TEXT, so a weakened case is a NEW case
    with no red history. There is no path from 'edit the test until it goes green'
    to green.
    """
    flag = tmp_path / "built"
    s = _add(_suite(tmp_path), "t", "strict", "negative", f"test -f {flag}")
    s.execute("t")                                   # seen RED. Earned.
    assert "strict" in ctc.Suite(s.dir).falsifiable("t")

    # Now weaken it rather than doing the work.
    s2 = ctc.Suite(s.dir)
    s2.append("cases.jsonl", {"target": "t", "name": "strict", "dim": "negative",
                              "run": "true", "amended": True, "was": f"test -f {flag}",
                              "reason": "make it pass", "by": "agent"})
    s3 = ctc.Suite(s.dir)
    s3.execute("t")                                  # green now, trivially
    st = ctc.Suite(s.dir).status("t")
    assert st["cases"][0]["verdict"] == "VACUOUS", (
        "a case weakened until it passes must NOT inherit the red history of the "
        "case it replaced"
    )
    assert st["score"] == 0


# ── SHALLOWNESS ───────────────────────────────────────────────────────────────


def test_an_all_happy_suite_is_shallow_not_passing(tmp_path):
    """8/8 green with no refusal case and no adversary case is not a pass. It is
    the green checkmark that means nothing."""
    s = _suite(tmp_path)
    for i in range(6):
        s = _add(s, "t", f"happy{i}", "happy", "true")
    st = s.status("t")
    assert st["verdict"] == "SHALLOW"
    assert not st["ok"]
    for d in ("negative", "adversary", "refusal"):
        assert d in st["reason"]


def test_the_car_suite_spans_the_dimensions_that_matter(tmp_path):
    """The suite that would have stopped the 84-month loan."""
    s = _suite(tmp_path)
    s = _add(s, "car", "insurance_before_signature", "ordering",
             "false", "the cost lands 4 weeks after the signature, unrecoverable")
    s = _add(s, "car", "payment_target_met_via_84_months", "adversary",
             "false", "the dealer satisfies the stated metric AGAINST him")
    s = _add(s, "car", "refuses_when_tco_exceeds_income", "refusal",
             "false", "the correct answer is DON'T BUY, and no agent writes this")
    s = _add(s, "car", "rejects_rolled_back_odometer", "lying_input",
             "false", "the world lies on purpose")
    s = _add(s, "car", "refuses_uninsurable_vin", "negative",
             "false", "the system must be able to say NO to a specific car")
    st = s.status("car")
    assert st["verdict"] != "SHALLOW", st["reason"]
    assert set(st["dims"]) >= {"adversary", "refusal", "ordering", "negative"}


# ── CLI ───────────────────────────────────────────────────────────────────────


def test_add_refuses_a_case_with_no_why(tmp_path):
    """A case whose author cannot say what it protects is not protecting
    anything."""
    _suite(tmp_path)  # .complextestcases/ exists
    r = subprocess.run(
        [sys.executable, str(Path(ctc.__file__)), "--dir", str(tmp_path),
         "add", "t", "--name", "x", "--dim", "happy", "--run", "true",
         "--why", "   "],
        capture_output=True, text=True)
    assert r.returncode != 0
    assert "why" in (r.stderr + r.stdout).lower()


# ── BROKEN: a typo must not be able to certify a claim ────────────────────────


def test_a_prose_case_is_broken_not_red(tmp_path):
    """The bug telos shipped in its own charter.

    `assert every record in amendments.jsonl has a non-empty approved_by` is prose.
    It exits 127 — command not found — so it never ran. But it is permanently
    "failing", which is visually identical to a case that is honestly failing, and
    it would satisfy a naive falsifiability check ("it was seen red!") while having
    tested nothing at all.
    """
    s = _add(_suite(tmp_path), "t", "prose", "negative",
             "assert every record in amendments.jsonl has a non-empty approved_by")
    res = s.execute("t")
    assert res[0]["exit"] in ctc.NOT_EXECUTABLE
    st = ctc.Suite(s.dir).status("t")
    assert st["cases"][0]["verdict"] == "BROKEN", (
        "a case that could not be EXECUTED is not a case that FAILED"
    )


def test_a_broken_case_never_earns_red_history(tmp_path):
    """The attack this closes: seed a case with a typo so it 'goes red', then fix
    the typo to something trivially true and claim the case is proven falsifiable.
    """
    s = _add(_suite(tmp_path), "t", "typo", "negative", "thiscommanddoesnotexist")
    s.execute("t")                       # exit 127 — "red", but never ran
    assert "typo" not in ctc.Suite(s.dir).falsifiable("t"), (
        "exit 127 must NOT count as red history — otherwise a typo certifies a "
        "claim"
    )


def test_a_case_runs_from_the_repo_root_not_the_ctc_cwd(tmp_path, monkeypatch):
    """A case is authored against its repo — a relative command must resolve from
    the repo root, not from wherever the ctc process sits. The bug this closes:
    `ctc --dir <repo> run` from another directory made every relative case fail
    to find its file, a false red that then minted falsifiability."""
    (tmp_path / "marker.txt").write_text("here")     # at the repo root
    s = _add(_suite(tmp_path), "t", "rel", "negative", "cat marker.txt")
    monkeypatch.chdir(tmp_path.parent)               # run ctc from somewhere else
    res = s.execute("t")
    assert res[0]["status"] == "green", (
        "a relative case must run from the repo root, not the ctc cwd"
    )


def test_a_case_that_cannot_execute_is_broken_not_red(tmp_path):
    """The exit-2 sibling of the prose-case attack: a command the interpreter
    cannot run at all (python can't open the file, a shell parse error) exits 2 —
    it never ran the case logic, so it must be BROKEN, never red history."""
    s = _add(_suite(tmp_path), "t", "cannot_run", "negative",
             "python3 this_script_does_not_exist_xyz.py")
    res = s.execute("t")
    assert res[0]["exit"] == 2 and res[0]["exit"] in ctc.NOT_EXECUTABLE
    assert ctc.Suite(s.dir).status("t")["cases"][0]["verdict"] == "BROKEN"
    assert "cannot_run" not in ctc.Suite(s.dir).falsifiable("t"), (
        "exit 2 must NOT mint falsifiability — the case never executed"
    )


def test_a_hung_case_is_broken_not_a_hang(tmp_path):
    """A case that hangs must be killed and marked BROKEN — never block the whole
    run forever. (case_timeout_sec, exit 124.)"""
    import time
    d = tmp_path / ctc.DIRNAME
    d.mkdir()
    cfg = dict(ctc.DEFAULT_CONFIG)
    cfg["case_timeout_sec"] = 1
    (d / "config.json").write_text(json.dumps(cfg))
    s = ctc.Suite(d)
    s.append("cases.jsonl", {"target": "t", "name": "hang", "dim": "negative",
                             "run": "sleep 30", "why": "hangs"})
    s = ctc.Suite(d)
    t0 = time.time()
    res = s.execute("t")
    assert time.time() - t0 < 10, "the timeout must kill the case, not wait 30s"
    assert res[0]["exit"] == ctc.TIMEOUT_EXIT
    assert ctc.Suite(d).status("t")["cases"][0]["verdict"] == "BROKEN"


def test_env_unavailable_case_is_skipped_not_red(tmp_path):
    """A case may report exit 77 to SKIP when its environment is absent — that is
    SKIPPED, never a false RED, does not fail the suite, and mints no history."""
    s = _add(_suite(tmp_path), "t", "needs_env", "negative", "exit 77")
    s.execute("t")
    assert ctc.Suite(s.dir).status("t")["cases"][0]["verdict"] == "SKIPPED"
    assert "needs_env" not in ctc.Suite(s.dir).falsifiable("t"), (
        "a skipped case never ran — it must not mint falsifiability"
    )


def test_changing_the_judge_drops_earned_red_history(tmp_path):
    """Anchor: a case that names its judge keeps earned red-history ONLY while
    that judge is unchanged. Weaken the judge but keep the command identical, and
    the earned red no longer counts — the deepest tamper vector, closed for cases
    that opt in."""
    judge = tmp_path / "judge.sh"
    judge.write_text("exit 1\n")             # the thing isn't built yet -> RED
    s = _suite(tmp_path)
    s.append("cases.jsonl", {"target": "t", "name": "anchored", "dim": "negative",
                             "run": "sh judge.sh", "anchor": "judge.sh", "why": "x"})
    s = ctc.Suite(s.dir)
    s.execute("t")
    assert "anchored" in ctc.Suite(s.dir).falsifiable("t"), "red should be earned"
    judge.write_text("exit 0\n")             # weaken the judge; command unchanged
    ctc.Suite(s.dir).execute("t")            # now green
    assert "anchored" not in ctc.Suite(s.dir).falsifiable("t"), (
        "earned red-history must NOT survive a changed judge"
    )


def test_a_crash_in_a_structured_case_is_broken_not_red(tmp_path):
    """crash-vs-red: an exit code cannot tell a judged failure from a crash — both
    exit 1. A structured case (verdict_protocol) AFFIRMS its verdict with a
    CTC_VERDICT token. One that judges FAIL earns a real red; one that crashes
    emits no token and is BROKEN, minting no falsifiability."""
    s = _suite(tmp_path)
    s.append("cases.jsonl", {"target": "t", "name": "judged_fail", "dim": "negative",
        "run": "echo CTC_VERDICT: FAIL; exit 1", "verdict_protocol": True, "why": "x"})
    s.append("cases.jsonl", {"target": "t", "name": "crashed", "dim": "negative",
        "run": "python3 -c 'raise ValueError(\"boom\")'", "verdict_protocol": True, "why": "x"})
    s = ctc.Suite(s.dir)
    s.execute("t")
    v = {c["name"]: c["verdict"] for c in ctc.Suite(s.dir).status("t")["cases"]}
    assert v["judged_fail"] == "RED", v
    assert v["crashed"] == "BROKEN", v
    fals = ctc.Suite(s.dir).falsifiable("t")
    assert "judged_fail" in fals and "crashed" not in fals, fals
