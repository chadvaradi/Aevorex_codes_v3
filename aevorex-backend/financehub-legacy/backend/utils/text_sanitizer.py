import re
from typing import Any, Mapping, Sequence

_EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF]", flags=re.UNICODE)

__all__ = [
    "strip_emoji",
    "sanitize_json",
]


def strip_emoji(text: str | None) -> str | None:
    """Return *text* with all emoji characters removed.

    If *text* is ``None``, returns ``None`` unchanged.
    """
    if text is None:
        return None
    return _EMOJI_RE.sub("", text)


def _rec(val: Any) -> Any:
    if isinstance(val, str):
        return strip_emoji(val)
    if isinstance(val, Mapping):
        return {k: _rec(v) for k, v in val.items()}
    if isinstance(val, Sequence) and not isinstance(val, (str, bytes, bytearray)):
        return [_rec(v) for v in val]
    return val


def sanitize_json(obj: Any) -> Any:
    """Recursively strip emojis from any string values inside *obj* (dict/list)."""
    return _rec(obj)
