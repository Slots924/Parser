"""Application-wide default settings used by the parser."""
from pathlib import Path

# Indices are 1-based throughout the project because they refer to human-friendly
# column positions in the raw input.
UA_INDEX = 3
COOKIE_INDEX = 5
REMARK_INDICES: tuple[int, ...] = (6, 7)

REMARK_DELIMITER = " :: "
SEPARATOR = " :: "
TAB_VALUE = "https://www.facebook.com/"
PROXY_TYPE = "noproxy"

OUTPUT_DIR = Path("results")
WORKBOOK_TITLE = "Parsed Data"

HEADERS: tuple[str, ...] = (
    "name",
    "remark",
    "tab",
    "platform",
    "username",
    "password",
    "fakey",
    "cookie",
    "proxytype",
    "ipchecker",
    "proxy",
    "proxyurl",
    "proxyid",
    "ip",
    "countrycode",
    "regioncode",
    "citycode",
    "ua",
    "resolution",
)
