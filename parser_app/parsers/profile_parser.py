"""Concrete parser for Facebook profile like records."""
from __future__ import annotations

from typing import Sequence

from parser_app.config import AppConfig
from parser_app.models import ProfileRecord, RawRecord
from parser_app.parsers.base import BaseParser


class ProfileParser(BaseParser):
    """Parse raw lines into :class:`ProfileRecord` objects."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def parse(self, raw: RawRecord) -> ProfileRecord:
        parts = raw.parts(self.config.separator)
        additional_values = self._collect_additional_values(parts)
        indexed_values = self._build_indexed_values(parts, additional_values)

        ua = self._get_indexed_value(indexed_values, self.config.ua_index)
        cookie = self._get_indexed_value(indexed_values, self.config.cookie_index)
        remark = self._build_remark(indexed_values, self.config.remark_indices)
        username_values = self._collect_values(indexed_values, self.config.username_indices)
        password_values = self._collect_values(indexed_values, self.config.password_indices)
        fakey_values = self._collect_values(indexed_values, self.config.fakey_indices)
        full_remark = self._merge_remark_with_additional(remark, additional_values)

        record = ProfileRecord(
            name=self.config.profile_name.strip(),
            remark=full_remark,
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

    def _build_indexed_values(self, parts: list[str], additional_values: list[str]) -> dict[int, str]:
        values = {index: value for index, value in enumerate(parts, start=1)}
        if not additional_values or self.config.additional_breakdown_index <= 0:
            return values

        prefix = self.config.additional_breakdown_index * 100
        for order, value in enumerate(additional_values, start=1):
            values[prefix + order] = value
        return values

    def _get_indexed_value(self, indexed_values: dict[int, str], index: int) -> str:
        if index <= 0:
            return ""
        return indexed_values.get(index, "").strip()

    def _collect_additional_values(self, parts: list[str]) -> list[str]:
        if self.config.additional_breakdown_index <= 0:
            return []
        separator = self.config.additional_separator
        if not separator:
            return []
        source_pos = self.config.additional_breakdown_index - 1
        if source_pos < 0 or source_pos >= len(parts):
            return []
        source_value = parts[source_pos].strip()
        if not source_value:
            return []
        return [item.strip() for item in source_value.split(separator) if item.strip()]

    def _merge_remark_with_additional(self, remark: str, additional_values: list[str]) -> str:
        if not additional_values:
            return remark

        prefix = self.config.additional_breakdown_index * 100
        labeled_values = [
            f"[{prefix + order}] - {value}" for order, value in enumerate(additional_values, start=1)
        ]
        if not remark:
            return self.config.remark_delimiter.join(labeled_values)
        return self.config.remark_delimiter.join([remark, *labeled_values])

    def _build_remark(self, indexed_values: dict[int, str], indices: Sequence[int] | None = None) -> str:
        selected_indices: Sequence[int] = self.config.remark_indices if indices is None else indices
        indices_list = list(selected_indices)
        if not indices_list or all(index == 0 for index in indices_list):
            return ""

        values: list[str] = []
        for index in indices_list:
            if index <= 0:
                continue
            value = indexed_values.get(index, "")
            if value:
                values.append(value.strip())

        if not values:
            return ""

        return self.config.remark_delimiter.join(values)

    def _collect_values(self, indexed_values: dict[int, str], indices: Sequence[int]) -> list[str]:
        values: list[str] = []
        for index in indices:
            if index <= 0:
                continue
            value = indexed_values.get(index, "").strip()
            if value:
                values.append(value)
        return values
