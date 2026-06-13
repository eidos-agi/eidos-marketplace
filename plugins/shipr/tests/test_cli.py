import json
import subprocess
import sys
from pathlib import Path


def test_cli_model_json(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "shipr.cli",
            "model",
            "--project",
            str(tmp_path),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["product_id"] == tmp_path.name
    assert "python-package" in payload["artifact_types"]
