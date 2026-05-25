from __future__ import annotations

import pytest

from cartwright.execution import build_fulfillment_playbook
from cartwright.parsing import parse_list_text
from cartwright.storage import CartwrightStore


def test_build_fulfillment_playbook_generates_browser_actions(tmp_path):
    db = tmp_path / "cartwright.sqlite"
    store = CartwrightStore(str(db))
    store.initialize()
    items = parse_list_text("1 gallon milk\n2 bananas", source="pasted_text")
    store.import_items("pasted_text", items)

    playbook = build_fulfillment_playbook(store, retailer="walmart", mode="browser", constraints=[])

    assert playbook.mode == "browser"
    assert playbook.retailer == "walmart"
    assert len(playbook.actions) == 2
    assert all(action.mode == "browser" for action in playbook.actions)
    assert all("search_url" in action.payload for action in playbook.actions)


def test_build_fulfillment_playbook_hybrid_includes_connector_and_browser_steps(tmp_path):
    db = tmp_path / "cartwright.sqlite"
    store = CartwrightStore(str(db))
    store.initialize()
    items = parse_list_text("2 tomatoes", source="pasted_text")
    store.import_items("pasted_text", items)

    playbook = build_fulfillment_playbook(store, retailer="walmart", mode="hybrid", constraints=[])

    assert len(playbook.actions) == 2
    modes = {action.mode for action in playbook.actions}
    assert modes == {"connector", "browser"}


def test_build_fulfillment_playbook_browser_snapshot_and_act(tmp_path):
    db = tmp_path / "cartwright.sqlite"
    store = CartwrightStore(str(db))
    store.initialize()
    items = parse_list_text("6 oranges", source="pasted_text")
    store.import_items("pasted_text", items)

    playbook = build_fulfillment_playbook(store, retailer="walmart", mode="browser", constraints=[])

    assert playbook.mode == "browser"
    assert len(playbook.actions) == 1
    action = playbook.actions[0]
    assert action.mode == "browser"
    assert action.action == "snapshot_and_act"
    assert action.payload["flow"][0]["step"] == "snapshot"


def test_invalid_execution_mode_is_rejected(tmp_path):
    db = tmp_path / "cartwright.sqlite"
    store = CartwrightStore(str(db))
    store.initialize()
    with pytest.raises(ValueError):
        build_fulfillment_playbook(store, retailer="walmart", mode="invalid")
