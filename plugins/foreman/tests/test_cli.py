from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
FOREMAN_CLI = REPO / "packages" / "foreman-cli" / "scripts" / "foreman.py"


def load_foreman_cli():
    spec = importlib.util.spec_from_file_location("foreman_cli_for_tests", FOREMAN_CLI)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_foreman_help_lists_core_commands() -> None:
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "foreman.py"), "--help"],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO,
    )

    assert "delegate" in result.stdout
    assert "collect" in result.stdout
    assert "control-submit" in result.stdout


def test_package_source_foreman_lists_core_commands() -> None:
    result = subprocess.run(
        [sys.executable, str(REPO / "packages" / "foreman-cli" / "scripts" / "foreman.py"), "--help"],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO,
    )

    assert "delegate" in result.stdout
    assert "agent-run" in result.stdout
    assert "control-submit" in result.stdout


def test_claude_emux_engine_requires_emux_tmux_and_claude() -> None:
    foreman = load_foreman_cli()

    assert foreman.engine_required_executables("claude-emux") == ["emux", "tmux", "claude"]


def test_emux_worker_name_is_stable() -> None:
    foreman = load_foreman_cli()

    assert foreman.emux_worker_name("20260601-abc123") == "foreman-20260601-abc123"


def test_claude_emux_worker_returns_exit_code_and_capture(tmp_path, monkeypatch, capsys) -> None:
    foreman = load_foreman_cli()

    monkeypatch.setenv("FOREMAN_ENGINE_CLAUDE_EMUX_PROMPT_DELAY_SEC", "0")
    monkeypatch.setenv("FOREMAN_ENGINE_CLAUDE_EMUX_READY_TIMEOUT_SEC", "0")
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    prompt_path = tmp_path / "worker.prompt.md"
    prompt_path.write_text("do the task", encoding="utf-8")
    log_path = tmp_path / "worker.log"
    row = {
        "id": "worker-1",
        "worktree_path": str(worktree),
        "prompt_path": str(prompt_path),
        "log_path": str(log_path),
        "timeout_sec": 5,
    }
    calls = []

    def fake_ensure(registry_name, session_name, worker_worktree, worker_id):
        calls.append(("ensure", registry_name, session_name, str(worker_worktree), worker_id))

    def fake_write_script(worker_row, worker_prompt_path, emux_output_path, exit_path):
        emux_output_path.write_text("CLAUDE_EMUX_OUTPUT\n", encoding="utf-8")
        exit_path.parent.mkdir(parents=True, exist_ok=True)
        exit_path.write_text("0\n", encoding="utf-8")
        script_path = worktree / ".foreman" / "run-claude-emux.sh"
        script_path.write_text("#!/bin/zsh\n", encoding="utf-8")
        return script_path

    def fake_run_checked(cmd, cwd=None):
        calls.append(("run_checked", cmd, cwd))

        class Result:
            stdout = ""
            stderr = ""
            returncode = 0

        return Result()

    def fake_subprocess_run(cmd, text=True, stdout=None, stderr=None, check=False):
        calls.append(("subprocess", cmd))

        class Result:
            stdout = "TMUX_CAPTURE\n"
            stderr = ""
            returncode = 0

        return Result()

    monkeypatch.setattr(foreman, "ensure_emux_tmux_session", fake_ensure)
    monkeypatch.setattr(foreman, "write_claude_emux_script", fake_write_script)
    monkeypatch.setattr(foreman, "run_checked", fake_run_checked)
    monkeypatch.setattr(foreman.subprocess, "run", fake_subprocess_run)

    exit_code, timed_out = foreman.run_claude_emux_worker(row, "do the task")

    assert exit_code == 0
    assert timed_out is False
    assert calls[0] == ("ensure", "foreman-worker-1", "foreman-worker-1", str(worktree), "worker-1")
    assert any(call[0] == "run_checked" and call[1][0:3] == ["emux", "send", "foreman-worker-1"] for call in calls)
    assert (worktree / ".foreman" / "claude-prompt.md").read_text(encoding="utf-8") == "do the task"
    output = capsys.readouterr().out
    assert "head_command=emux head foreman-worker-1" in output
    assert "prompt_delivery=claude interactive prompt argument" in output
    assert "CLAUDE_EMUX_OUTPUT" in output
    assert "TMUX_CAPTURE" in output


def test_claude_emux_script_defaults_to_interactive_claude(tmp_path, monkeypatch) -> None:
    foreman = load_foreman_cli()

    worktree = tmp_path / "worktree"
    worktree.mkdir()
    prompt_path = tmp_path / "worker.prompt.md"
    output_path = tmp_path / "worker.emux.log"
    exit_path = worktree / ".foreman" / "claude-emux.exit"
    row = {
        "id": "worker-1",
        "worktree_path": str(worktree),
    }

    script_path = foreman.write_claude_emux_script(row, prompt_path, output_path, exit_path)
    body = script_path.read_text(encoding="utf-8")

    assert "exit_code=$?" in body
    assert "status=$?" not in body
    assert "[foreman-emux] mode=interactive-argument" in body
    assert "[foreman-emux] command=claude --permission-mode acceptEdits <prompt>" in body
    assert 'claude --permission-mode acceptEdits "$(cat "$PROMPT_FILE")"' in body
    assert 'claude --permission-mode acceptEdits "$(cat "$PROMPT_FILE")"\nexit_code=$?' in body
    assert "claude -p" not in body


def test_claude_emux_override_prompt_argument_is_explicit(tmp_path, monkeypatch) -> None:
    foreman = load_foreman_cli()

    worktree = tmp_path / "worktree"
    worktree.mkdir()
    prompt_path = tmp_path / "worker.prompt.md"
    output_path = tmp_path / "worker.emux.log"
    exit_path = worktree / ".foreman" / "claude-emux.exit"
    row = {
        "id": "worker-1",
        "worktree_path": str(worktree),
    }
    monkeypatch.setenv("FOREMAN_ENGINE_CLAUDE_EMUX_CMD", "python3 /tmp/smoke_engineer.py -p {prompt}")

    script_path = foreman.write_claude_emux_script(row, prompt_path, output_path, exit_path)
    body = script_path.read_text(encoding="utf-8")

    assert "[foreman-emux] mode=override-argument" in body
    assert "python3 /tmp/smoke_engineer.py -p \"$(cat \"$PROMPT_FILE\")\"" in body
