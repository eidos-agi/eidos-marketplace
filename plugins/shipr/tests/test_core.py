import json
from pathlib import Path

from shipr.core import (
    detect_release_model,
    ensure_shipr_ignored,
    record_attempt,
    release_frontier,
    write_release_model,
)


def test_detects_python_plugin_project(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    (tmp_path / ".codex-plugin").mkdir()
    (tmp_path / ".codex-plugin" / "plugin.json").write_text("{}")
    (tmp_path / "README.md").write_text("# Demo\n")

    model = detect_release_model(tmp_path, "demo release")

    assert model["product_id"] == tmp_path.name
    assert "python-package" in model["artifact_types"]
    assert "eidos-plugin" in model["artifact_types"]
    assert "Eidos AGI marketplace" in model["distribution_channels"]
    assert "ship-forge" in model["forge_stack"]


def test_write_model_and_frontier(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    path = write_release_model(tmp_path, detect_release_model(tmp_path))

    assert path.exists()
    frontier = release_frontier(tmp_path)
    assert frontier["status"] == "model_ready"
    assert frontier["attempt_count"] == 0


def test_record_attempt_uses_model_snapshot(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    write_release_model(tmp_path, detect_release_model(tmp_path))

    path, attempt = record_attempt(
        tmp_path,
        goal="ship demo",
        status="planned",
        proofs=["pytest -q"],
    )

    assert path.exists()
    assert attempt["goal"] == "ship demo"
    assert attempt["proofs"] == ["pytest -q"]
    assert json.loads(path.read_text())["release_model_snapshot"]["artifact_types"]


def test_write_model_ignores_shipr_memory_in_git_project(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")

    write_release_model(tmp_path, detect_release_model(tmp_path))

    assert ".shipr/" in (tmp_path / ".gitignore").read_text().splitlines()


def test_record_attempt_does_not_duplicate_shipr_ignore(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitignore").write_text("node_modules/\n.shipr/\n")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")

    record_attempt(tmp_path, goal="ship demo")

    assert (tmp_path / ".gitignore").read_text().splitlines().count(".shipr/") == 1


def test_ensure_shipr_ignored_leaves_non_git_project_alone(tmp_path: Path) -> None:
    assert ensure_shipr_ignored(tmp_path) is None
    assert not (tmp_path / ".gitignore").exists()
