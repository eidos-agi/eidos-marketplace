from pathlib import Path


FORBIDDEN_REFERENCES = ("fix" + "-it", "fix" + " it", "fix" + "it", "wreck" + "-it", "wreck" + " it", "ral" + "ph", "dis" + "ney", "felix " + "jr")
IGNORED_PARTS = {".git", ".pytest_cache", ".ruff_cache", ".venv", "__pycache__"}
TEXT_SUFFIXES = {"", ".md", ".py", ".toml", ".txt"}


def test_repo_avoids_protected_brand_references():
    root = Path(__file__).resolve().parents[1]
    files = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix in TEXT_SUFFIXES
        and path != Path(__file__)
        and not any(part in IGNORED_PARTS for part in path.parts)
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in files)

    assert not any(reference in text for reference in FORBIDDEN_REFERENCES)
