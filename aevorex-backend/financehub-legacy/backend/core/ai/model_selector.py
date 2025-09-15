from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ModelChoice = dataclass


@dataclass
class SelectedModel:
    provider: Literal["openrouter"]
    model_id: str
    temperature: float
    max_output_tokens: int


def select_model(
    *,
    query_type: Literal["summary", "indicator", "news", "hybrid", "sentiment"],
    expected_context_tokens: int,
    plan: Literal["free", "pro", "team", "enterprise"],
) -> SelectedModel:
    """Pick a cost‑efficient model based on query type and context size.

    P0 heuristic - specialized models for different tasks:
    - sentiment → meta-llama/llama-3.3-8b-instruct:free (fast, focused)
    - indicator/news → mistralai/mistral-7b-instruct:free (balanced)
    - default → google/gemini-2.0-flash-001 (general purpose)
    """
    provider = "openrouter"

    # Specialized model selection by query type
    if query_type == "sentiment":
        model_id = "meta-llama/llama-3.3-8b-instruct:free"
        temp = 0.0  # Deterministic for sentiment analysis
        max_out = 200  # Short sentiment responses
    elif query_type in ["indicator", "news"]:
        model_id = "mistralai/mistral-7b-instruct:free"
        temp = 0.2  # Slightly creative for analysis
        max_out = 500  # Medium-length analysis
    else:
        # Default for summary, hybrid, and other types
        model_id = "google/gemini-2.0-flash-001"
        temp = 0.35  # Balanced creativity
        max_out = 1500  # Longer responses for summaries

    # Override with plan-based limits if more restrictive
    if plan == "free":
        max_out = min(max_out, 700)
    elif plan == "pro":
        max_out = min(max_out, 1500)
    else:
        max_out = min(max_out, 2500)

    return SelectedModel(
        provider=provider,
        model_id=model_id,
        temperature=temp,
        max_output_tokens=max_out,
    )
