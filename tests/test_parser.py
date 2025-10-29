from parser_app.config import AppConfig
from parser_app.models import RawRecord
from parser_app.parsers.profile_parser import ProfileParser


def test_profile_parser_extracts_fields():
    config = AppConfig()
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
