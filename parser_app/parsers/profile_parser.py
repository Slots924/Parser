"""Concrete parser for Facebook profile like records."""
from __future__ import annotations

from typing import Sequence

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
        remark = self._build_remark(parts, self.config.remark_indices)
        username_values = self._collect_values(parts, self.config.username_indices)
        password_values = self._collect_values(parts, self.config.password_indices)
        fakey_values = self._collect_values(parts, self.config.fakey_indices)

        record = ProfileRecord(
            remark=remark,
            tab=self.config.tab_value,
            platform=self.config.platform_value.strip(),
            username=",".join(username_values),
            password=",".join(f'"{value}"' for value in password_values),
            fakey=",".join(fakey_values),
            cookie=cookie,
            proxytype=self.config.proxy_type,
            ua=ua,
        )
        return record

    def _build_remark(self, parts: list[str], indices: Sequence[int] | None = None) -> str:
        selected_indices: Sequence[int] = self.config.remark_indices if indices is None else indices
        indices_list = list(selected_indices)
        if not indices_list or all(index == 0 for index in indices_list):
            return ""

        values: list[str] = []
        for index in indices_list:
            if index <= 0:
                continue
            value = safe_get(parts, index)
            if value:
                values.append(value.strip())

        if not values:
            return ""

        return self.config.remark_delimiter.join(values)

    def _collect_values(self, parts: list[str], indices: Sequence[int]) -> list[str]:
        values: list[str] = []
        for index in indices:
            if index <= 0:
                continue
            value = safe_get(parts, index).strip()
            if value:
                values.append(value)
        return values
