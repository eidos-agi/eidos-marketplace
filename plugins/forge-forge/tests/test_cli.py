"""End-to-end tests for forge CLI: progressive reveal, typo suggestions, contract."""

import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, os.path.join(REPO, "cli.py"), *args],
        check=check,
        capture_output=True,
        text=True,
        cwd=REPO,
    )


def test_no_args_is_same_as_help() -> None:
    """`forge` with no args is identical to `forge --help`. Single discovery surface."""
    no_args = _run()
    help_out = _run("--help")
    assert no_args.returncode == 0
    assert help_out.returncode == 0
    assert no_args.stdout == help_out.stdout
    # And the output lists every subcommand.
    for cmd in ("find", "list", "info", "how", "for-project"):
        assert cmd in no_args.stdout


def test_typo_suggests_correct_command() -> None:
    result = _run("fnd", "foo", check=False)
    assert result.returncode == 2
    assert "unknown command" in result.stderr.lower()
    assert "did you mean 'forge find'" in result.stderr.lower()


def test_typo_with_no_close_match() -> None:
    result = _run("zzzzzzz", check=False)
    assert result.returncode == 2
    assert "unknown command" in result.stderr.lower()


def test_list_json_is_parseable() -> None:
    result = _run("list", "--json")
    payload = json.loads(result.stdout)
    assert "count" in payload
    assert "forges" in payload
    assert payload["count"] > 0


def test_list_quiet_one_per_line() -> None:
    result = _run("list", "--quiet")
    names = [n for n in result.stdout.strip().split("\n") if n]
    assert len(names) > 5
    assert all("forge" in n.lower() for n in names)


def test_list_filter_by_type() -> None:
    result = _run("list", "--type", "tool", "--json")
    payload = json.loads(result.stdout)
    for f in payload["forges"]:
        assert f.get("type") == "tool"


def test_find_returns_ranked_matches() -> None:
    result = _run("find", "test my API", "--json")
    payload = json.loads(result.stdout)
    assert "matches" in payload
    assert len(payload["matches"]) > 0
    scores = [m.get("match_score", 0) for m in payload["matches"]]
    assert scores == sorted(scores, reverse=True)


def test_info_unknown_name_suggests() -> None:
    # Use a name that's a typo but NOT a substring match — substring matching
    # is intentional fuzzy behavior in lib.get_forge_info, so we need a name
    # that fails both exact and substring lookup.
    result = _run("info", "machine-learning-forge", check=False)
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert "did_you_mean" in payload
    assert "forge" in payload["did_you_mean"]


def test_info_substring_match_succeeds() -> None:
    # Documents the lenient fuzzy: "ml" should resolve to "ml-forge".
    result = _run("info", "ml")
    payload = json.loads(result.stdout)
    assert payload["name"] == "ml-forge"


def test_info_known_returns_full_data() -> None:
    result = _run("info", "ml-forge", "--json")
    payload = json.loads(result.stdout)
    assert payload["name"] == "ml-forge"
    assert "description" in payload
    assert "skills" in payload


def test_for_project_recommends_for_self() -> None:
    """Run for-project on forge-forge's own repo — has pyproject + license + MCP."""
    result = _run("for-project", "--path", REPO, "--json")
    payload = json.loads(result.stdout)
    rec_names = {r["name"] for r in payload.get("recommended", [])}
    # forge-forge has all the signals: pyproject, license, MCP file
    assert "ship-forge" in rec_names
    assert "foss-forge" in rec_names


def test_help_lists_every_subcommand() -> None:
    result = _run("--help")
    for cmd in ("find", "list", "info", "how", "for-project"):
        assert cmd in result.stdout


def test_no_interactive_prompts() -> None:
    result = subprocess.run(
        [sys.executable, os.path.join(REPO, "cli.py"), "list"],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
        stdin=subprocess.DEVNULL,
        cwd=REPO,
    )
    assert result.returncode == 0
