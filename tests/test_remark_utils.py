import pytest

from parser_app.utils import RemarkParseError, parse_remark_indexes


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("", ()),
        ("   ", ()),
        (None, ()),
        ("7", (7,)),
        ("7,8,9", (7, 8, 9)),
        ("7 8 9", (7, 8, 9)),
        ("7, 8  10", (7, 8, 10)),
    ],
)
def test_parse_remark_indexes_valid(raw, expected):
    assert parse_remark_indexes(raw) == expected


@pytest.mark.parametrize(
    "raw, message",
    [
        ("0", "≥ 1"),
        ("-1", "не є"),
        ("7,7", "дублікат"),
        ("abc", "не є"),
    ],
)
def test_parse_remark_indexes_invalid(raw, message):
    with pytest.raises(RemarkParseError) as excinfo:
        parse_remark_indexes(raw)
    assert message in str(excinfo.value)
