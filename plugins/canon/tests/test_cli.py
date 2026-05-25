from canon.cli import main


def test_agentic_context_source(capsys):
    assert main(["agentic-context-source"]) == 0
    output = capsys.readouterr().out
    assert "gist.githubusercontent.com" in output


def test_agent_brief(capsys):
    assert main(["agent", "test work"]) == 0
    output = capsys.readouterr().out
    assert "Have:" in output
    assert "Want:" in output
    assert "Don't want:" in output


def test_verify(capsys):
    assert main(["verify"]) == 0
    output = capsys.readouterr().out
    assert "Required repo files: ok" in output
    assert "Codex plugin manifest: ok" in output
    assert "Canon skill: ok" in output
