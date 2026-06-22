"""Tests for `kai login <service>` — the service-agnostic secret-acquisition entry."""

from unittest.mock import patch

from typer.testing import CliRunner

from kai.__main__ import app
from kai.lib import secrets

runner = CliRunner()


def test_login_no_service_lists_registry():
    result = runner.invoke(app, ["login"])
    assert result.exit_code == 0
    # At least slack must appear since it's registered today
    assert "slack" in result.stdout
    # Vault path and env var columns surfaced
    assert "slack/eidos/kai-token" in result.stdout
    assert "KAI_SLACK_TOKEN" in result.stdout


def test_login_unknown_service_fails_loudly():
    result = runner.invoke(app, ["login", "wakanda"])
    assert result.exit_code == 1
    assert "wakanda" in result.stdout


def test_login_known_service_dispatches_to_acquire_secret():
    """`kai login slack` should call acquire_secret with the SLACK service."""
    fake_result = secrets.AcquireResult(
        success=True,
        service=secrets.SLACK,
        secret="xoxb-FAKE",
        actions=["wrote ~/.kai/.env (chmod 600)", "saved to Eidos Vault path 'slack/eidos/kai-token'"],
        identity=[("team", "Eidos"), ("user", "kai-bot"), ("bot_id", "B0123")],
        cancelled=False,
    )
    with patch("kai.commands.login.secrets.acquire_secret", return_value=fake_result) as mock_acquire:
        result = runner.invoke(app, ["login", "slack", "--no-browser", "--no-popup"])
        assert result.exit_code == 0, result.stdout
        # The right service was passed
        call_args = mock_acquire.call_args
        assert call_args.args[0] is secrets.SLACK
        assert call_args.kwargs["no_browser"] is True
        assert call_args.kwargs["no_popup"] is True
        # User and workspace surfaced from identity
        assert "kai-bot" in result.stdout
        assert "Eidos" in result.stdout
        # Each action printed
        assert "saved to Eidos Vault" in result.stdout


def test_login_cancelled_exits_one():
    cancelled = secrets.AcquireResult(
        success=False, service=secrets.SLACK, secret=None,
        actions=[], identity=[], cancelled=True,
    )
    with patch("kai.commands.login.secrets.acquire_secret", return_value=cancelled):
        result = runner.invoke(app, ["login", "slack", "--no-browser", "--no-popup"])
        assert result.exit_code == 1
        assert "cancelled" in result.stdout.lower()


def test_login_validation_failure_exits_one():
    failed = secrets.AcquireResult(
        success=False, service=secrets.SLACK, secret=None,
        actions=[], identity=[], cancelled=False,
    )
    with patch("kai.commands.login.secrets.acquire_secret", return_value=failed):
        result = runner.invoke(app, ["login", "slack", "--no-browser", "--no-popup"])
        assert result.exit_code == 1
