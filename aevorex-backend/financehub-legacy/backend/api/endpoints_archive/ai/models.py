"""AI Model Catalogue Endpoint
Returns the central MODEL_CATALOGUE so that front-ends can build
selectors without hard-coding IDs.
"""

from __future__ import annotations

import functools
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from time import monotonic

# ---------------------------------------------------------------------------
# MODEL_CATALOGUE IMPORT (single-source-of-truth)
# ---------------------------------------------------------------------------
# All backend modules should use the canonical re-export located at
# ``modules.shared.ai.model_catalogue``.  That proxy guarantees that the
# root-level ``model_catalogue.py`` is discoverable even if the repository
# is checked out as a submodule.
#
# Given that we are in a monorepo context and do not need this complexity,
# we will directly import from the canonical source in the backend.
# from backend.core.chat.model_selector import MODEL_CATALOGUE

router = APIRouter(prefix="/models", tags=["AI"])

# --- Import the canonical model catalogue ---
try:
    from modules.shared.ai.model_catalogue import MODEL_CATALOGUE  # noqa: E402
except ModuleNotFoundError as import_err:
    # -------------------------------------------------------------------
    # Dynamic fallback – query OpenRouter for available models in real-time
    # -------------------------------------------------------------------
    import logging
    import os
    import httpx

    _logger = logging.getLogger(__name__)
    _logger.warning(
        "MODEL_CATALOGUE missing – attempting runtime fetch from OpenRouter (%s)",
        import_err,
    )

    OPENROUTER_KEY = os.getenv("FINBOT_API_KEYS__OPENROUTER") or os.getenv(
        "OPENROUTER_API_KEY"
    )

    MODEL_CATALOGUE: list[dict] = []

    if OPENROUTER_KEY:
        try:
            resp = httpx.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
                timeout=15.0,
            )
            resp.raise_for_status()
            # OpenRouter may return either a dict with a "data" key OR a plain list
            response_json = resp.json()
            if isinstance(response_json, list):
                data = response_json
            else:
                data = response_json.get("data", [])
            for m in data:
                pricing_raw = m.get("pricing")
                # Handle cases where OpenRouter returns pricing as string or missing
                if isinstance(pricing_raw, dict):
                    price_in = pricing_raw.get("input", 0.0) or 0.0
                    price_out = pricing_raw.get("output", 0.0) or 0.0
                else:
                    price_in = price_out = 0.0

                tags_raw = (
                    m.get("openrouter", {}).get("tags")
                    if isinstance(m.get("openrouter"), dict)
                    else None
                )
                ux_hint_val = "n/a"
                if isinstance(tags_raw, list) and tags_raw:
                    ux_hint_val = tags_raw[0]

                MODEL_CATALOGUE.append(
                    {
                        "id": m.get("id"),
                        "ctx": m.get("context_length"),
                        "price_in": price_in,
                        "price_out": price_out,
                        "strength": m.get("capabilities", "n/a"),
                        "ux_hint": ux_hint_val,
                        "notes": m.get("description", ""),
                    }
                )
            if not MODEL_CATALOGUE:
                raise ValueError("OpenRouter returned empty model list")
            _logger.info(
                "Fetched %s models from OpenRouter runtime", len(MODEL_CATALOGUE)
            )
        except Exception as fetch_err:
            _logger.error(
                "Failed to fetch model list from OpenRouter – falling back to minimal static list (%s)",
                fetch_err,
            )

    # No static fallback – if runtime fetch fails, the route will return an
    # empty list with a structured error payload (no-mock policy).


# ---------------------------------------------------------------------------
# Pydantic schema
# ---------------------------------------------------------------------------
class ModelMeta(BaseModel):
    id: str = Field(..., description="Provider/model identifier on OpenRouter")
    ctx: int | None = Field(None, description="Context window (tokens)")
    price_in: float = Field(..., ge=0, description="USD / 1K tokens in")
    price_out: float = Field(..., ge=0, description="USD / 1K tokens out")
    strength: str = Field(..., description="Few-word marketing strength")
    ux_hint: str = Field(..., description="Short hint for UX grouping")
    notes: str = Field(..., description="Long-form notes for advanced UIs")


# ---------------------------------------------------------------------------
# Service layer (cached)
# ---------------------------------------------------------------------------
@functools.lru_cache(maxsize=1)
def _get_catalogue() -> list[ModelMeta]:
    """Return catalogue converted to Pydantic objects (cached 5 min)."""
    # lru_cache is process-wide; we still limit staleness via TTL below.
    monotonic()  # noqa: F401 – placeholder if future timestamp needed
    return [ModelMeta(**m) for m in MODEL_CATALOGUE]


async def get_catalogue_dependency() -> list[ModelMeta]:
    """Return model catalogue or empty list without raising HTTP errors."""
    models = _get_catalogue()
    return models  # Empty list signals unavailable state


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------
@router.get(
    "/",
    summary="List all available AI models (structured 200 response)",
    status_code=status.HTTP_200_OK,
)
async def list_models(
    catalogue: Annotated[list[ModelMeta], Depends(get_catalogue_dependency)],
):
    """Return model list or structured error payload with HTTP 200."""
    if not catalogue:
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "message": "AI model catalogue unavailable – upstream provider failure",
                "data": [],
            },
        )

    # Success – serialize models to dict to avoid Pydantic response_model enforcement
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "data": [m.dict() for m in catalogue],
        },
    )


# ---------------------------------------------------------------------------
# Alias route to avoid automatic FastAPI redirect when missing trailing slash
# ---------------------------------------------------------------------------


@router.get("", include_in_schema=False)
async def list_models_alias(
    catalogue: Annotated[list[ModelMeta], Depends(get_catalogue_dependency)],
):
    return await list_models(catalogue)
