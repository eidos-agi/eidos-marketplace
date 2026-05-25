from __future__ import annotations

import tempfile
from pathlib import Path

from cartwright.cli import main
from cartwright.storage import CartwrightStore


def test_cartwright_init_is_idempotent(tmp_path):
    db = tmp_path / "cartwright.sqlite"
    code = main(["--db-path", str(db), "init"])
    assert code == 0
    code = main(["--db-path", str(db), "init"])
    assert code == 0
    store = CartwrightStore(str(db))
    store.initialize()


def test_cli_import_pasted_and_list_active(tmp_path):
    db = tmp_path / "cartwright.sqlite"
    main(["--db-path", str(db), "init"])
    code = main([
        "--db-path",
        str(db),
        "list",
        "import",
        "--source",
        "pasted",
        "--text",
        "1 gallon milk\n2 carrots",
    ])
    assert code == 0
    output = main([
        "--db-path",
        str(db),
        "list",
        "active",
    ])
    assert output == 0


def test_export_creates_content(tmp_path):
    db = tmp_path / "cartwright.sqlite"
    main(["--db-path", str(db), "init"])
    main([
        "--db-path",
        str(db),
        "list",
        "import",
        "--source",
        "pasted",
        "--text",
        "1 gallon milk",
    ])
    out = tmp_path / "list.md"
    code = main(["--db-path", str(db), "export", "drive", "--format", "markdown", "--output", str(out)])
    assert code == 0
    assert out.exists()
    assert "milk" in out.read_text()


def test_execute_generates_actions(tmp_path):
    db = tmp_path / "cartwright.sqlite"
    main(["--db-path", str(db), "init"])
    main([
        "--db-path",
        str(db),
        "list",
        "import",
        "--source",
        "pasted",
        "--text",
        "1 gallon milk\n2 bananas",
    ])
    code = main(["--db-path", str(db), "execute", "--mode", "browser", "--retailer", "walmart"])
    assert code == 0


def test_cli_remembers_source_connection_url(tmp_path):
    db = tmp_path / "cartwright.sqlite"
    main(["--db-path", str(db), "init"])
    code = main([
        "--db-path",
        str(db),
        "connections",
        "remember",
        "--source",
        "amazon",
        "--url",
        "https://www.amazon.com/alexaquantum/sp/alexaShoppingList",
        "--label",
        "Amazon shopping list",
    ])
    assert code == 0
    store = CartwrightStore(str(db))
    connection = store.get_source_connection("amazon")
    assert connection is not None
    assert connection["metadata"]["url"].startswith("https://www.amazon.com/")
