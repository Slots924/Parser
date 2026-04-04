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


def test_profile_parser_builds_platform_username_password_and_fakey():
    config = AppConfig(
        platform_value="  facebook.com,amazon.com  ",
        username_indices=(1, 2, 0),
        password_indices=(3, 4, 0),
        fakey_indices=(5, 6, 0),
    )
    parser = ProfileParser(config)
    raw = RawRecord(line_no=1, content="username1 :: username2 :: password1 :: password2 :: key1 :: key2")

    record = parser.parse(raw)

    assert record.platform == "facebook.com,amazon.com"
    assert record.username == "username1,username2"
    assert record.password == '"password1","password2"'
    assert record.fakey == "key1,key2"


def test_profile_parser_skips_optional_fields_for_zero_indices():
    config = AppConfig(
        platform_value="  amazon.com  ",
        username_indices=(0, 0, 0),
        password_indices=(0, 0, 0),
        fakey_indices=(0, 0, 0),
    )
    parser = ProfileParser(config)
    raw = RawRecord(line_no=1, content="user :: pass :: key")

    record = parser.parse(raw)

    assert record.platform == "amazon.com"
    assert record.username == ""
    assert record.password == ""
    assert record.fakey == ""


def test_profile_parser_sets_name_from_config():
    config = AppConfig(profile_name="  My Profile  ")
    parser = ProfileParser(config)
    raw = RawRecord(line_no=1, content="user :: pass :: ua :: extra :: cookie")

    record = parser.parse(raw)

    assert record.name == "My Profile"


def test_profile_parser_strips_trailing_dot_from_username_values():
    config = AppConfig(username_indices=(1, 2, 0))
    parser = ProfileParser(config)
    raw = RawRecord(line_no=1, content="pkrouiky@tacoblastmail.com. :: second@example.com. :: pass")

    record = parser.parse(raw)

    assert record.username == "pkrouiky@tacoblastmail.com,second@example.com"


def test_profile_parser_appends_additional_breakdown_to_remark():
    config = AppConfig(
        remark_indices=(6, 0, 0),
        additional_breakdown_index=7,
        additional_separator="|",
        remark_delimiter=" :: ",
    )
    parser = ProfileParser(config)
    raw = RawRecord(
        line_no=1,
        content="a :: b :: ua :: d :: cookie :: base remark :: first| second |third",
    )

    record = parser.parse(raw)

    assert record.remark == "base remark :: [701] - first :: [702] - second :: [703] - third"


def test_profile_parser_can_use_700_indices_for_mapped_fields():
    config = AppConfig(
        additional_breakdown_index=7,
        additional_separator=";",
        username_indices=(701, 0, 0),
        password_indices=(702, 0, 0),
        fakey_indices=(703, 0, 0),
        ua_index=704,
    )
    parser = ProfileParser(config)
    raw = RawRecord(line_no=1, content="a :: b :: c :: d :: e :: f :: email;token;secret;ua-string")

    record = parser.parse(raw)

    assert record.username == "email"
    assert record.password == '"token"'
    assert record.fakey == "secret"
    assert record.ua == "ua-string"


def test_profile_parser_skips_additional_breakdown_when_index_is_zero():
    config = AppConfig(
        remark_indices=(6, 0, 0),
        additional_breakdown_index=0,
        additional_separator="|",
    )
    parser = ProfileParser(config)
    raw = RawRecord(line_no=1, content="a :: b :: ua :: d :: cookie :: base remark :: first|second")

    record = parser.parse(raw)

    assert record.remark == "base remark"
