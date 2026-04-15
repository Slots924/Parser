"""Persistence helpers for GUI form state."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

GUI_STATE_FILE = Path.home() / ".parser_app_gui_state.json"


def default_profile_name(opened_at: datetime | None = None) -> str:
    """Return default profile name in DD.MM format for app opening date."""
    opened_at = opened_at or datetime.now()
    return opened_at.strftime("%d.%m")


def load_gui_state(path: Path = GUI_STATE_FILE) -> dict[str, Any]:
    """Load persisted GUI state from JSON safely.

    Returns an empty dict for missing, malformed, or unreadable files.
    """
    try:
        if not path.exists():
            return {}
        raw_payload = path.read_text(encoding="utf-8")
        payload = json.loads(raw_payload)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}

    if not isinstance(payload, dict):
        return {}

    return payload


def save_gui_state(state: dict[str, Any], path: Path = GUI_STATE_FILE) -> None:
    """Persist GUI state to disk safely and atomically where possible."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as tmp:
            json.dump(state, tmp, ensure_ascii=False, indent=2)
            tmp_path = Path(tmp.name)
        tmp_path.replace(path)
    except OSError:
        return


def read_int(value: Any, default: int = 0, min_value: int = 0, max_value: int = 9999) -> int:
    """Read an integer value with defensive clamping."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(min_value, min(max_value, parsed))


def read_str(value: Any, default: str = "") -> str:
    """Read a string value defensively."""
    if value is None:
        return default
    if isinstance(value, str):
        return value
    return str(value)


def read_int_list(value: Any, size: int, default: int = 0) -> list[int]:
    """Read list-like int values with fixed size."""
    if not isinstance(value, (list, tuple)):
        return [default] * size

    normalized = [read_int(item, default=default) for item in value[:size]]
    if len(normalized) < size:
        normalized.extend([default] * (size - len(normalized)))
    return normalized
