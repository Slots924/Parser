from parser_app.services.preview import preview_first_row


def test_preview_first_row_enumerates_values():
    lines = [
        "   ",
        "email :: token :: ua :: cookie :: trailing",
        "another line",
    ]

    result = preview_first_row(lines)

    assert result == [
        (1, "email"),
        (2, "token"),
        (3, "ua"),
        (4, "cookie"),
        (5, "trailing"),
    ]


def test_preview_first_row_allows_custom_separator():
    lines = ["field1, field2,, field4"]

    result = preview_first_row(lines, separator=",")

    assert result == [
        (1, "field1"),
        (2, "field2"),
        (3, ""),
        (4, "field4"),
    ]


def test_preview_first_row_handles_empty_input():
    assert preview_first_row([], separator=",") == []
