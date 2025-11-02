"""Concrete parser for Facebook profile like records."""
from __future__ import annotations

from parser_app.config import AppConfig
from parser_app.models import ProfileRecord, RawRecord, safe_get
from parser_app.parsers.base import BaseParser


class ProfileParser(BaseParser):
    """Parse raw lines into :class:`ProfileRecord` objects."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def parse(self, raw: RawRecord) -> ProfileRecord:
        parts = raw.parts(self.config.separator)

        ua = safe_get(parts, self.config.ua_index)
        cookie = safe_get(parts, self.config.cookie_index)
        remark = self._build_remark(parts)

        record = ProfileRecord(
            remark=remark,
            tab=self.config.tab_value,
            cookie=cookie,
            proxytype=self.config.proxy_type,
            ua=ua,
        )
        return record

    def _build_remark(self, parts: list[str]) -> str:
        indices = list(self.config.remark_indices)
        if not indices or all(index == 0 for index in indices):
            return ""

        values: list[str] = []
        for index in indices:
            if index <= 0:
                continue
            value = safe_get(parts, index)
            if value:
                values.append(value.strip())

        if not values:
            return ""

        return self.config.remark_delimiter.join(values)
