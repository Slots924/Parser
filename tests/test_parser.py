from parser_app.config import AppConfig
from parser_app.models import RawRecord
from parser_app.parsers.profile_parser import ProfileParser


def test_profile_parser_extracts_fields():
    config = AppConfig(
        remark_indices=(6, 7),
        remark_delimiter=" :: ",
    )
    parser = ProfileParser(config)
    raw = RawRecord(
        line_no=1,
        content="email :: token :: ua :: extra :: cookie :: remark section :: trailing",
    )

    record = parser.parse(raw)

    assert record.ua == "ua"
    assert record.cookie == "cookie"
    assert record.remark == "remark section :: trailing"
    assert record.proxytype == config.proxy_type
    assert record.tab == config.tab_value


def test_profile_parser_skips_remark_and_ua_when_index_zero():
    config = AppConfig(remark_indices=(0,), ua_index=0)
    parser = ProfileParser(config)
    raw = RawRecord(
        line_no=1,
        content="email :: token :: ua :: extra",
    )

    record = parser.parse(raw)

    assert record.ua == ""
    assert record.remark == ""


def test_profile_parser_uses_custom_remark_delimiter():
    config = AppConfig(remark_indices=(1, 4, 2), remark_delimiter=" || ")
    parser = ProfileParser(config)
    raw = RawRecord(line_no=1, content="alpha :: beta :: gamma :: delta")

    record = parser.parse(raw)

    assert record.remark == "alpha || delta || beta"


def test_profile_parser_handles_single_remark_index():
    config = AppConfig(remark_indices=(6,))
    parser = ProfileParser(config)
    raw = RawRecord(
        line_no=1,
        content="name :: token :: ua :: extra :: cookie :: only one",
    )

    record = parser.parse(raw)

    assert record.remark == "only one"


def test_profile_parser_handles_repeated_zero_indices():
    config = AppConfig(remark_indices=(0, 6, 0))
    parser = ProfileParser(config)
    raw = RawRecord(
        line_no=1,
        content="name :: token :: ua :: extra :: cookie :: final remark",
    )

    record = parser.parse(raw)

    assert record.remark == "final remark"
