from __future__ import annotations

from typing import Iterable


def estimate_tokens(text: str) -> int:
    """Rough token estimator without external deps (~4 chars/token)."""
    if not text:
        return 0
    # heuristic: avg 4 chars per token
    return max(1, len(text) // 4)


def fit_messages_into_budget(messages: Iterable[dict], max_tokens: int) -> list[dict]:
    """Return the last N messages that fit into the remaining token budget.

    messages: iterable of {role, content}
    """
    msgs = list(messages)
    kept: list[dict] = []
    used = 0
    for msg in reversed(msgs):
        t = estimate_tokens(str(msg.get("content", ""))) + 6  # role & json overhead
        if used + t > max_tokens:
            break
        kept.append(msg)
        used += t
    kept.reverse()
    return kept
