from datetime import datetime

from parser_app.gui_state import (
    default_profile_name,
    load_gui_state,
    read_int,
    read_int_list,
    read_str,
    save_gui_state,
)


def test_default_profile_name_uses_day_month_format():
    assert default_profile_name(datetime(2026, 4, 15, 10, 30, 0)) == "15.04"


def test_load_gui_state_returns_empty_for_invalid_json(tmp_path):
    state_path = tmp_path / "gui-state.json"
    state_path.write_text("{broken", encoding="utf-8")

    assert load_gui_state(state_path) == {}


def test_save_and_load_gui_state_roundtrip(tmp_path):
    state_path = tmp_path / "gui-state.json"
    payload = {"name": "15.04", "ua_index": 5, "raw_text": "line"}

    save_gui_state(payload, state_path)

    assert load_gui_state(state_path) == payload


def test_read_int_clamps_invalid_values():
    assert read_int("abc", default=2) == 2
    assert read_int(-10) == 0
    assert read_int(10_000) == 9999


def test_read_int_list_normalizes_size_and_types():
    assert read_int_list([1, "2", "bad"], size=4) == [1, 2, 0, 0]
    assert read_int_list("not-a-list", size=3) == [0, 0, 0]


def test_read_str_handles_none_and_other_types():
    assert read_str(None, default="x") == "x"
    assert read_str(123) == "123"
