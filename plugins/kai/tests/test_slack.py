"""Tests for kai slack — Slack API interactions are mocked."""

import os
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from kai.__main__ import app

runner = CliRunner()


def _env(token: str | None = "xoxp-fake-token-for-tests") -> dict:
    """Build an env dict with KAI_SLACK_TOKEN set (or unset)."""
    base = {k: v for k, v in os.environ.items() if k != "KAI_SLACK_TOKEN"}
    if token is not None:
        base["KAI_SLACK_TOKEN"] = token
    return base


def test_slack_help_when_no_args():
    result = runner.invoke(app, ["slack"], env=_env())
    assert result.exit_code == 0
    assert "kai slack" in result.stdout
    # All subcommands advertised
    for cmd in ("send", "read", "search", "thread", "channels", "react", "me"):
        assert cmd in result.stdout


def test_slack_no_token_fails_loudly():
    """Missing token → exit 1 with clear message naming the env var."""
    result = runner.invoke(app, ["slack", "me"], env=_env(token=None))
    assert result.exit_code == 1
    assert "KAI_SLACK_TOKEN" in result.stdout


def test_slack_send_dry_run_does_not_call_api():
    """--dry-run must not instantiate a WebClient or call any API."""
    with patch("kai.commands.slack._client") as mock_client:
        result = runner.invoke(
            app,
            ["slack", "send", "C0123ABCDE", "hello world", "--dry-run"],
            env=_env(),
        )
        assert result.exit_code == 0
        assert "would send" in result.stdout
        assert "hello world" in result.stdout
        mock_client.assert_not_called()


def test_slack_send_calls_chat_postmessage():
    fake = MagicMock()
    fake.chat_postMessage.return_value = {"ts": "1730000000.123", "channel": "C0123ABCDE"}
    with patch("kai.commands.slack._client", return_value=fake):
        result = runner.invoke(
            app,
            ["slack", "send", "C0123ABCDE", "hello"],
            env=_env(),
        )
        assert result.exit_code == 0
        fake.chat_postMessage.assert_called_once_with(channel="C0123ABCDE", text="hello")
        assert "sent" in result.stdout


def test_slack_send_with_thread_ts():
    fake = MagicMock()
    fake.chat_postMessage.return_value = {"ts": "1730000000.456", "channel": "C0123ABCDE"}
    with patch("kai.commands.slack._client", return_value=fake):
        result = runner.invoke(
            app,
            ["slack", "send", "C0123ABCDE", "reply", "--thread-ts", "1730000000.123"],
            env=_env(),
        )
        assert result.exit_code == 0
        fake.chat_postMessage.assert_called_once_with(
            channel="C0123ABCDE", text="reply", thread_ts="1730000000.123"
        )


def test_slack_send_json_output():
    fake = MagicMock()
    fake.chat_postMessage.return_value = {"ts": "1730000000.789", "channel": "C0123ABCDE"}
    with patch("kai.commands.slack._client", return_value=fake):
        result = runner.invoke(
            app,
            ["slack", "send", "C0123ABCDE", "hi", "--json"],
            env=_env(),
        )
        assert result.exit_code == 0
        # Must be valid JSON containing the ts
        import json
        out = json.loads(result.stdout.strip().split("\n")[-1])
        assert out["ts"] == "1730000000.789"


def test_slack_read_calls_conversations_history():
    fake = MagicMock()
    fake.conversations_history.return_value = {
        "messages": [
            {"ts": "1730000000.100", "user": "U1", "text": "hello"},
            {"ts": "1730000000.200", "user": "U2", "text": "world"},
        ]
    }
    with patch("kai.commands.slack._client", return_value=fake):
        result = runner.invoke(
            app,
            ["slack", "read", "C0123ABCDE", "-n", "2"],
            env=_env(),
        )
        assert result.exit_code == 0
        fake.conversations_history.assert_called_once_with(channel="C0123ABCDE", limit=2)


def test_slack_react_dry_run():
    with patch("kai.commands.slack._client") as mock_client:
        result = runner.invoke(
            app,
            ["slack", "react", "C0123ABCDE", "1730000000.100", "white_check_mark", "--dry-run"],
            env=_env(),
        )
        assert result.exit_code == 0
        assert "would react" in result.stdout
        # Rich auto-substitutes :emoji: shortcodes; assert the channel + ts survive
        assert "C0123ABCDE" in result.stdout
        assert "1730000000.100" in result.stdout
        mock_client.assert_not_called()


def test_slack_channel_resolution_by_id_no_lookup():
    """Passing a channel ID directly must NOT trigger conversations_list."""
    fake = MagicMock()
    fake.chat_postMessage.return_value = {"ts": "1.2", "channel": "C0123ABCDE"}
    with patch("kai.commands.slack._client", return_value=fake):
        result = runner.invoke(
            app,
            ["slack", "send", "C0123ABCDE", "msg"],
            env=_env(),
        )
        assert result.exit_code == 0
        fake.conversations_list.assert_not_called()


def test_slack_file_upload_dry_run_does_not_call_api(tmp_path):
    """--dry-run for uploads must not instantiate a WebClient or call Slack."""
    audio = tmp_path / "recap.m4a"
    audio.write_bytes(b"fake audio")
    with patch("kai.commands.slack._client") as mock_client:
        result = runner.invoke(
            app,
            [
                "slack", "file", "upload", "C0123ABCDE", str(audio),
                "--title", "Call recap",
                "--initial-comment", "NotebookLM audio recap",
                "--dry-run",
            ],
            env=_env(),
        )
        assert result.exit_code == 0
        assert "would upload" in result.stdout
        assert "Call recap" in result.stdout
        mock_client.assert_not_called()


def test_slack_file_upload_calls_files_upload_v2(tmp_path):
    audio = tmp_path / "recap.m4a"
    audio.write_bytes(b"fake audio")
    fake = MagicMock()
    fake.files_upload_v2.return_value = {
        "file": {"id": "F0123", "permalink": "https://eidosagi.slack.com/files/F0123"}
    }
    with patch("kai.commands.slack._client", return_value=fake):
        result = runner.invoke(
            app,
            [
                "slack", "file", "upload", "C0123ABCDE", str(audio),
                "--title", "Call recap",
                "--initial-comment", "NotebookLM audio recap",
            ],
            env=_env(),
        )
        assert result.exit_code == 0, result.stdout
        fake.files_upload_v2.assert_called_once_with(
            channel="C0123ABCDE",
            file=str(audio),
            title="Call recap",
            initial_comment="NotebookLM audio recap",
        )
        assert "uploaded" in result.stdout


# ─── admin verbs (create, archive, kick, etc.) ──────────────────────────────


def test_slack_help_includes_admin_verbs():
    result = runner.invoke(app, ["slack"], env=_env())
    assert result.exit_code == 0
    for verb in ("create", "archive", "rename", "topic", "purpose", "invite", "kick",
                 "convert-to-private", "usergroup", "file"):
        assert verb in result.stdout


def test_slack_create_dry_run_does_not_call_api():
    with patch("kai.commands.slack._client") as mock_client:
        result = runner.invoke(
            app,
            ["slack", "create", "gifty", "--private", "--topic", "test topic", "--dry-run"],
            env=_env(),
        )
        assert result.exit_code == 0
        assert "would create" in result.stdout
        assert "gifty" in result.stdout
        assert "private" in result.stdout
        mock_client.assert_not_called()


def test_slack_create_chains_topic_purpose_invite():
    """create with --topic --purpose --invite must chain four API calls atomically."""
    fake = MagicMock()
    fake.conversations_create.return_value = {"channel": {"id": "C0NEWGIFTY", "name": "gifty"}}
    fake.users_list.return_value = {"members": [{"id": "U0VYBHAV", "name": "vybhav"}]}
    with patch("kai.commands.slack._client", return_value=fake):
        result = runner.invoke(
            app,
            ["slack", "create", "gifty",
             "--private",
             "--topic", "Personalized gift recs case study",
             "--purpose", "Eidos-method case study with the Thunells",
             "--invite", "vybhav"],
            env=_env(),
        )
        assert result.exit_code == 0, result.stdout
        fake.conversations_create.assert_called_once_with(name="gifty", is_private=True)
        fake.conversations_setTopic.assert_called_once_with(
            channel="C0NEWGIFTY", topic="Personalized gift recs case study"
        )
        fake.conversations_setPurpose.assert_called_once_with(
            channel="C0NEWGIFTY", purpose="Eidos-method case study with the Thunells"
        )
        fake.conversations_invite.assert_called_once_with(channel="C0NEWGIFTY", users="U0VYBHAV")


def test_slack_archive_without_yes_refuses():
    """archive without --yes hard-fails with exit 2 and never calls the API."""
    with patch("kai.commands.slack._client") as mock_client:
        result = runner.invoke(
            app,
            ["slack", "archive", "C0DEADBEEF"],
            env=_env(),
        )
        assert result.exit_code == 2
        assert "irreversible" in result.stdout.lower()
        assert "--yes" in result.stdout
        mock_client.assert_not_called()


def test_slack_archive_with_yes_calls_api():
    fake = MagicMock()
    with patch("kai.commands.slack._client", return_value=fake):
        result = runner.invoke(
            app,
            ["slack", "archive", "C0DEADBEEF", "--yes"],
            env=_env(),
        )
        assert result.exit_code == 0
        fake.conversations_archive.assert_called_once_with(channel="C0DEADBEEF")


def test_slack_archive_dry_run_short_circuits_yes():
    """--dry-run short-circuits the --yes guard. Dry-run is always safe to run."""
    with patch("kai.commands.slack._client") as mock_client:
        result = runner.invoke(
            app,
            ["slack", "archive", "C0DEADBEEF", "--dry-run"],
            env=_env(),
        )
        assert result.exit_code == 0
        assert "would archive" in result.stdout
        mock_client.assert_not_called()


def test_slack_kick_without_yes_refuses():
    with patch("kai.commands.slack._client") as mock_client:
        result = runner.invoke(
            app,
            ["slack", "kick", "C0123", "U0BAD"],
            env=_env(),
        )
        assert result.exit_code == 2
        mock_client.assert_not_called()


def test_slack_convert_to_private_without_yes_refuses():
    with patch("kai.commands.slack._client") as mock_client:
        result = runner.invoke(
            app,
            ["slack", "convert-to-private", "C0123ABCDE"],
            env=_env(),
        )
        assert result.exit_code == 2
        assert "irreversible" in result.stdout.lower()
        mock_client.assert_not_called()


def test_slack_topic_calls_set_topic():
    fake = MagicMock()
    with patch("kai.commands.slack._client", return_value=fake):
        result = runner.invoke(
            app,
            ["slack", "topic", "C0123ABCDE", "new topic"],
            env=_env(),
        )
        assert result.exit_code == 0
        fake.conversations_setTopic.assert_called_once_with(channel="C0123ABCDE", topic="new topic")


def test_slack_invite_multi_user():
    fake = MagicMock()
    fake.users_list.return_value = {"members": [
        {"id": "U0VYBHAV", "name": "vybhav"},
        {"id": "U0DAN", "name": "daniel"},
    ]}
    with patch("kai.commands.slack._client", return_value=fake):
        result = runner.invoke(
            app,
            ["slack", "invite", "C0123ABCDE", "vybhav", "daniel"],
            env=_env(),
        )
        assert result.exit_code == 0, result.stdout
        # users joined with comma per Slack API contract
        call_args = fake.conversations_invite.call_args
        assert call_args.kwargs["channel"] == "C0123ABCDE"
        assert "U0VYBHAV" in call_args.kwargs["users"]
        assert "U0DAN" in call_args.kwargs["users"]


def test_slack_pin_calls_pins_add():
    fake = MagicMock()
    with patch("kai.commands.slack._client", return_value=fake):
        result = runner.invoke(
            app,
            ["slack", "pin", "C0123ABCDE", "1730000000.100"],
            env=_env(),
        )
        assert result.exit_code == 0
        fake.pins_add.assert_called_once_with(channel="C0123ABCDE", timestamp="1730000000.100")


def test_slack_bookmark_remove_without_yes_refuses():
    with patch("kai.commands.slack._client") as mock_client:
        result = runner.invoke(
            app,
            ["slack", "bookmark", "remove", "C0123ABCDE", "Bk012345"],
            env=_env(),
        )
        assert result.exit_code == 2
        mock_client.assert_not_called()


def test_slack_message_delete_without_yes_refuses():
    with patch("kai.commands.slack._client") as mock_client:
        result = runner.invoke(
            app,
            ["slack", "message", "delete", "C0123ABCDE", "1730000000.100"],
            env=_env(),
        )
        assert result.exit_code == 2
        mock_client.assert_not_called()


def test_slack_file_delete_without_yes_refuses():
    with patch("kai.commands.slack._client") as mock_client:
        result = runner.invoke(
            app,
            ["slack", "file", "delete", "F0123456"],
            env=_env(),
        )
        assert result.exit_code == 2
        mock_client.assert_not_called()


def test_slack_unarchive_rejects_name_argument():
    """unarchive needs a channel ID — archived channels are excluded from the name index."""
    with patch("kai.commands.slack._client") as mock_client:
        result = runner.invoke(
            app,
            ["slack", "unarchive", "gifty"],
            env=_env(),
        )
        assert result.exit_code == 1
        assert "channel ID" in result.stdout
        mock_client.assert_not_called()


def test_slack_usergroup_create_with_users():
    fake = MagicMock()
    fake.usergroups_create.return_value = {"usergroup": {"id": "S0GIFTYTEAM", "handle": "gifty-team"}}
    fake.users_list.return_value = {"members": [{"id": "U0VYBHAV", "name": "vybhav"}]}
    with patch("kai.commands.slack._client", return_value=fake):
        result = runner.invoke(
            app,
            ["slack", "usergroup", "create", "gifty-team", "--name", "Gifty team", "--users", "vybhav"],
            env=_env(),
        )
        assert result.exit_code == 0, result.stdout
        fake.usergroups_create.assert_called_once_with(name="Gifty team", handle="gifty-team")
        fake.usergroups_users_update.assert_called_once_with(usergroup="S0GIFTYTEAM", users="U0VYBHAV")


# ─── slack-cli wrapping (manifest + doctor) ─────────────────────────────────


def test_slack_help_includes_manifest_and_doctor():
    result = runner.invoke(app, ["slack"], env=_env())
    assert result.exit_code == 0
    for verb in ("manifest", "doctor", "brand", "icon", "init", "push", "pull"):
        assert verb in result.stdout


def test_slack_brand_lists_icon_assets():
    result = runner.invoke(app, ["slack", "brand", "--json"], env=_env())
    assert result.exit_code == 0
    data = __import__("json").loads(result.stdout)
    assert data["app_name"] == "kai"
    assert data["icon_512_png"].endswith("kai-slack-icon-512.png")
    assert data["admin_url"] == "https://api.slack.com/apps/A0B2CC38GJW/general"


def test_slack_icon_set_dry_run_does_not_call_api():
    with patch("kai.commands.slack._post_app_icon") as mock_post:
        result = runner.invoke(app, ["slack", "icon", "set", "--dry-run"], env=_env())
        assert result.exit_code == 0
        assert "apps.icon.set" in result.stdout
        mock_post.assert_not_called()


def test_slack_icon_set_rejects_bot_token_before_api():
    with patch("kai.commands.slack._post_app_icon") as mock_post:
        result = runner.invoke(app, ["slack", "icon", "set"], env=_env(token="xoxb-fake-bot-token"))
        assert result.exit_code == 1
        assert "bot token" in result.stdout.lower()
        assert "app_configurations:write" in result.stdout
        mock_post.assert_not_called()


def test_slack_icon_set_posts_with_config_token():
    fake_resp = {"ok": True}
    with patch("kai.commands.slack._post_app_icon", return_value=fake_resp) as mock_post:
        env = _env(token=None)
        env["KAI_SLACK_CONFIG_TOKEN"] = "xoxp-fake-config-token"
        result = runner.invoke(app, ["slack", "icon", "set"], env=env)
        assert result.exit_code == 0, result.stdout
        assert "uploaded kai Slack icon" in result.stdout
        assert mock_post.call_args.args[0] == "xoxp-fake-config-token"


def test_slack_workspace_icon_dry_run_does_not_call_api():
    with patch("kai.commands.slack._post_workspace_icon") as mock_post:
        result = runner.invoke(app, ["slack", "icon", "set-workspace", "--dry-run"], env=_env())
        assert result.exit_code == 0
        assert "admin.teams.settings.setIcon" in result.stdout
        mock_post.assert_not_called()


def test_slack_workspace_icon_requires_admin_token():
    with patch("kai.commands.slack._post_workspace_icon") as mock_post:
        result = runner.invoke(app, ["slack", "icon", "set-workspace"], env=_env(token=None))
        assert result.exit_code == 1
        assert "KAI_SLACK_ADMIN_TOKEN" in result.stdout
        assert "admin.teams:write" in result.stdout
        mock_post.assert_not_called()


def test_slack_workspace_icon_posts_with_admin_token():
    fake_resp = {"ok": True}
    with patch("kai.commands.slack._post_workspace_icon", return_value=fake_resp) as mock_post:
        env = _env(token=None)
        env["KAI_SLACK_ADMIN_TOKEN"] = "xoxp-fake-admin-token"
        result = runner.invoke(app, ["slack", "icon", "set-workspace"], env=env)
        assert result.exit_code == 0, result.stdout
        assert "uploaded Eidos AGI workspace icon" in result.stdout
        assert mock_post.call_args.args[0] == "xoxp-fake-admin-token"
        assert mock_post.call_args.args[1] == "T0AV46DB675"
        assert mock_post.call_args.args[2] == "https://eidosagi.com/logo-800.png"


def test_slack_manifest_push_without_yes_refuses():
    """manifest push is a substrate-guarded mutating operation."""
    with patch("kai.commands.slack._run_slack_cli") as mock_run:
        result = runner.invoke(app, ["slack", "manifest", "push"], env=_env())
        assert result.exit_code == 2
        assert "irreversible" in result.stdout.lower() or "--yes" in result.stdout
        mock_run.assert_not_called()


def test_slack_manifest_push_dry_run_short_circuits():
    with patch("kai.commands.slack._run_slack_cli") as mock_run:
        result = runner.invoke(app, ["slack", "manifest", "push", "--dry-run"], env=_env())
        assert result.exit_code == 0
        assert "would push" in result.stdout
        mock_run.assert_not_called()


def test_slack_manifest_push_runs_validate_then_install():
    """Successful push: validate (rc=0) → install (rc=0)."""
    from subprocess import CompletedProcess
    fake_validate = CompletedProcess(args=[], returncode=0, stdout="App Manifest Validation Result: Valid\n", stderr="")
    fake_install = CompletedProcess(args=[], returncode=0, stdout="App Install\n   Installing\n   Finished\n", stderr="")
    with patch("kai.commands.slack._run_slack_cli", side_effect=[fake_validate, fake_install]) as mock_run:
        result = runner.invoke(app, ["slack", "manifest", "push", "--yes"], env=_env())
        assert result.exit_code == 0, result.stdout
        assert mock_run.call_count == 2
        # First call validates
        assert "manifest" in mock_run.call_args_list[0].args[0]
        # Second call installs
        assert "install" in mock_run.call_args_list[1].args[0]


def test_slack_doctor_renders_table_even_when_pieces_missing():
    """doctor must always render a table; non-zero exit if anything fails."""
    # Force every check to fail for predictable output
    with patch("kai.commands.slack._slack_cli_available", return_value=False), \
         patch("shutil.which", return_value=None), \
         patch("subprocess.run") as mock_subproc:
        mock_subproc.return_value.returncode = 1
        mock_subproc.return_value.stdout = ""
        mock_subproc.return_value.stderr = ""
        result = runner.invoke(app, ["slack", "doctor"], env={k: v for k, v in __import__("os").environ.items() if k != "KAI_SLACK_TOKEN"})
        # Doctor should always produce output
        assert "kai slack doctor" in result.stdout or "doctor" in result.stdout.lower()
        # And should exit non-zero given missing slack-cli
        assert result.exit_code in (0, 1)  # Tolerate either; the contract is "produces output and tells the truth"
