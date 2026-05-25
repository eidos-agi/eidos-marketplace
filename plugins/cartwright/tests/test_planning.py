from __future__ import annotations

from cartwright.parsing import parse_list_text
from cartwright.planning import build_plan
from cartwright.storage import CartwrightStore


def test_build_plan_suppresses_vegetables_when_constraint_present(tmp_path):
    db_file = tmp_path / "cartwright.sqlite"
    store = CartwrightStore(str(db_file))
    store.initialize()
    store.set_profile({"constraints": ["plenty of vegetables"]})
    items = parse_list_text("1 gallon milk\n2 carrots\n4 tomatoes", source="pasted_text")
    store.import_items("pasted", items)
    plan = build_plan(store, retailer="walmart", constraints=["plenty of vegetables"])
    names = [row["normalized_name"] for row in plan.list_items]
    assert "carrots" not in names
    assert "tomatoes" not in names
    assert "milk" in names


def test_build_plan_deduplicates_and_preserves_quantity(tmp_path):
    db_file = tmp_path / "cartwright.sqlite"
    store = CartwrightStore(str(db_file))
    store.initialize()
    items = parse_list_text("1 apple\n2 apples", source="pasted_text")
    store.import_items("pasted", items)
    plan = build_plan(store, retailer="walmart", constraints=[])
    apples = [row for row in plan.list_items if row["normalized_name"] == "apple" or row["normalized_name"] == "apples"]
    assert apples
    assert apples[0]["quantity"] == "3"
