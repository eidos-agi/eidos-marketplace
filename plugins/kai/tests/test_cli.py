"""Smoke tests for kai."""

import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from kai.__main__ import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "kai" in result.stdout.lower()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "kai" in result.stdout.lower()


def test_root_lists_domains():
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    # Banner format: orient before you operate + active domains
    assert "Orient before you operate" in result.stdout
    assert "deploy" in result.stdout
    assert "doctor" in result.stdout
    assert "ideas" in result.stdout
    assert "feedback" in result.stdout
    assert "ops" in result.stdout
    # Lineage chain present
    assert "ideas" in result.stdout
    assert "research-md" in result.stdout
    assert "visionlog" in result.stdout


def test_deploy_lists_commands():
    result = runner.invoke(app, ["deploy"])
    assert result.exit_code == 0
    assert "status" in result.stdout
    assert "logs" in result.stdout


def test_deploy_help():
    result = runner.invoke(app, ["deploy", "--help"])
    assert result.exit_code == 0


def test_doctor_help():
    result = runner.invoke(app, ["doctor", "--help"])
    assert result.exit_code == 0


def test_doctor_runs():
    # Runs even if optional tools missing; only fails on missing required tools.
    # `git` is required and almost certainly present in test environments.
    result = runner.invoke(app, ["doctor"])
    # Exit code may be 0 or 1 depending on environment; just verify it ran
    assert "kai doctor" in result.stdout
    assert "present" in result.stdout or "MISSING" in result.stdout


def test_ops_guardrails_teach_api_first_mailbox_path():
    result = runner.invoke(app, ["ops", "guardrails"])
    assert result.exit_code == 0
    assert "When a platform has an API" in result.stdout
    assert "eidos vault set mail/<address>/password" in result.stdout
    assert "--stdin" in result.stdout
    assert "Reeves Vault" in result.stdout
    assert "legacy Reeves Vault/RheaOS" in result.stdout
    assert "Do not" in result.stdout


def test_ops_default_shows_guardrails():
    result = runner.invoke(app, ["ops"])
    assert result.exit_code == 0
    assert "kai ops guardrails" in result.stdout


def test_ops_employee_photo_reports_cross_workspace_gates():
    result = runner.invoke(
        app,
        [
            "ops",
            "employee-photo",
            "vybhav@eidosagi.com",
            "--name",
            "Vybhav Reddy",
            "--slack-user-id",
            "U0AV46EKF0B",
        ],
    )
    assert result.exit_code == 0
    assert "Employee profile photo" in result.stdout
    assert "approved headshot" in result.stdout
    assert "Slack" in result.stdout
    assert "Google Workspace" in result.stdout
    assert "users.setPhoto" in result.stdout
    assert "users.photos.update" in result.stdout


def test_ideas_help_when_no_args():
    # Ideas writes to <cockpit>/ideas/ — point at a tmp dir so test doesn't pollute
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "KAI_COCKPIT_ROOT": tmp}
        result = runner.invoke(app, ["ideas"], env=env)
        assert result.exit_code == 0
        assert "kai ideas" in result.stdout
        assert "add" in result.stdout
        assert "promote" in result.stdout


def test_ideas_add_writes_file():
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "KAI_COCKPIT_ROOT": tmp}
        result = runner.invoke(app, ["ideas", "add", "Test idea title"], env=env)
        assert result.exit_code == 0
        ideas_dir = Path(tmp) / "ideas"
        files = list(ideas_dir.glob("*.md"))
        assert len(files) == 1
        body = files[0].read_text()
        assert "Test idea title" in body
        assert "status: open" in body


def test_feedback_help_when_no_args():
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "KAI_COCKPIT_ROOT": tmp}
        result = runner.invoke(app, ["feedback"], env=env)
        assert result.exit_code == 0
        assert "kai feedback" in result.stdout
        # All five kinds advertised
        for kind in ("miss", "drift", "surprise", "win", "noise"):
            assert kind in result.stdout


def test_feedback_miss_writes_file():
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "KAI_COCKPIT_ROOT": tmp}
        result = runner.invoke(app, ["feedback", "miss", "wanted X"], env=env)
        assert result.exit_code == 0
        feedback_dir = Path(tmp) / "feedback"
        files = list(feedback_dir.glob("*.md"))
        assert len(files) == 1
        body = files[0].read_text()
        assert "kind: miss" in body
        assert "wanted X" in body
        # Lineage frozen
        assert "kai:" in body
        assert "python:" in body


def test_feedback_list_empty():
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "KAI_COCKPIT_ROOT": tmp}
        result = runner.invoke(app, ["feedback", "list"], env=env)
        assert result.exit_code == 0
        assert "No feedback entries" in result.stdout


def test_ideas_promote_marks_status():
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "KAI_COCKPIT_ROOT": tmp}
        runner.invoke(app, ["ideas", "add", "Promote me"], env=env)
        result = runner.invoke(app, ["ideas", "promote", "promote-me"], env=env)
        assert result.exit_code == 0
        files = list((Path(tmp) / "ideas").glob("*.md"))
        body = files[0].read_text()
        assert "status: promoted" in body


# --- Bootstrap: capture surfaces create a missing cockpit root ---------------


def test_feedback_bootstraps_missing_env_cockpit_root():
    # KAI_COCKPIT_ROOT points at a dir that does NOT exist yet. Capture must
    # bootstrap it rather than hard-fail (the original `kai feedback win` bug).
    with tempfile.TemporaryDirectory() as tmp:
        cockpit = Path(tmp) / "cockpit-eidos"
        assert not cockpit.exists()
        env = {**os.environ, "KAI_COCKPIT_ROOT": str(cockpit)}
        result = runner.invoke(app, ["feedback", "win", "bootstrap works"], env=env)
        assert result.exit_code == 0, result.stdout
        files = list((cockpit / "feedback").glob("*.md"))
        assert len(files) == 1
        assert "bootstrap works" in files[0].read_text()


def test_ideas_bootstraps_missing_env_cockpit_root():
    with tempfile.TemporaryDirectory() as tmp:
        cockpit = Path(tmp) / "cockpit-eidos"
        assert not cockpit.exists()
        env = {**os.environ, "KAI_COCKPIT_ROOT": str(cockpit)}
        result = runner.invoke(app, ["ideas", "add", "Bootstrapped idea"], env=env)
        assert result.exit_code == 0, result.stdout
        files = list((cockpit / "ideas").glob("*.md"))
        assert len(files) == 1
        assert "Bootstrapped idea" in files[0].read_text()


def test_feedback_bootstraps_missing_default_cockpit_root(monkeypatch):
    # No env override: the default fallback root is missing. Capture must still
    # bootstrap (proves the fix is not env-specific).
    import kai._paths as paths

    with tempfile.TemporaryDirectory() as tmp:
        default = Path(tmp) / "repos-eidos-agi" / "cockpit-eidos"
        assert not default.exists()
        monkeypatch.delenv("KAI_COCKPIT_ROOT", raising=False)
        monkeypatch.setattr(paths, "DEFAULT_COCKPIT_ROOT", default)
        env = {k: v for k, v in os.environ.items() if k != "KAI_COCKPIT_ROOT"}
        result = runner.invoke(app, ["feedback", "miss", "default bootstrap"], env=env)
        assert result.exit_code == 0, result.stdout
        files = list((default / "feedback").glob("*.md"))
        assert len(files) == 1
        assert "default bootstrap" in files[0].read_text()


def test_require_cockpit_root_stays_loud_when_missing(monkeypatch):
    # Non-capture paths must NOT bootstrap — require_cockpit_root stays loud.
    import typer

    import kai._paths as paths

    with tempfile.TemporaryDirectory() as tmp:
        missing = Path(tmp) / "nope"
        monkeypatch.setenv("KAI_COCKPIT_ROOT", str(missing))
        try:
            paths.require_cockpit_root()
            assert False, "expected require_cockpit_root to exit on missing root"
        except typer.Exit as exc:
            assert exc.exit_code == 1
        assert not missing.exists()
