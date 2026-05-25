from __future__ import annotations

from cartwright.server import (
    cartwright_build_execution_playbook,
    cartwright_get_active_list,
    cartwright_build_grocery_plan,
    cartwright_get_source_connection,
    cartwright_import_list,
    cartwright_remember_source_url,
)
from cartwright.storage import CartwrightStore


def test_mcp_import_and_plan(tmp_path, monkeypatch):
    db = tmp_path / "cartwright.sqlite"
    monkeypatch.setenv("CARTWRIGHT_DB_PATH", str(db))
    store = CartwrightStore(str(db))
    store.initialize()
    result = cartwright_import_list("pasted", "1 loaf bread\n2 bananas")
    assert '"status": "ok"' in result
    list_result = cartwright_get_active_list()
    assert '"count": 2' in list_result
    plan_result = cartwright_build_grocery_plan()
    assert '"retailer": "walmart"' in plan_result


def test_mcp_build_execution_playbook(tmp_path, monkeypatch):
    db = tmp_path / "cartwright.sqlite"
    monkeypatch.setenv("CARTWRIGHT_DB_PATH", str(db))
    store = CartwrightStore(str(db))
    store.initialize()
    cartwright_import_list("pasted", "1 loaf bread\n2 bananas")
    execution_result = cartwright_build_execution_playbook(mode="browser")
    assert '"mode": "browser"' in execution_result
    assert '"action": "search_and_stage"' not in execution_result


def test_mcp_build_browser_execution_playbook(tmp_path, monkeypatch):
    db = tmp_path / "cartwright.sqlite"
    monkeypatch.setenv("CARTWRIGHT_DB_PATH", str(db))
    store = CartwrightStore(str(db))
    store.initialize()
    cartwright_import_list("pasted", "1 loaf bread\n2 bananas")
    execution_result = cartwright_build_execution_playbook(mode="browser", browser_profile="user")
    assert '"mode": "browser"' in execution_result
    assert '"snapshot_and_act"' in execution_result
    assert '"flow"' in execution_result


def test_mcp_remembers_source_url(tmp_path, monkeypatch):
    db = tmp_path / "cartwright.sqlite"
    monkeypatch.setenv("CARTWRIGHT_DB_PATH", str(db))
    store = CartwrightStore(str(db))
    store.initialize()
    result = cartwright_remember_source_url(
        "amazon",
        "https://www.amazon.com/alexaquantum/sp/alexaShoppingList",
        "Amazon shopping list",
    )
    assert '"status": "ok"' in result
    connection = cartwright_get_source_connection("amazon")
    assert "alexaShoppingList" in connection
