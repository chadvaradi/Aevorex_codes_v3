"""AI Endpoints Package
Central place to expose AI-related routes (model catalogue, etc.)
"""

from fastapi import APIRouter

# Import sub-routers (only model catalogue for now)
try:
    from backend.api.endpoints.ai.models import router as models_router  # noqa: E402
except ModuleNotFoundError as e:
    import logging

    logging.getLogger(__name__).warning(
        "AI models router disabled – missing dependency %s", e
    )
    from fastapi import APIRouter as _APIRouter

    models_router = _APIRouter()

ai_router = APIRouter(tags=["AI"])

ai_router.include_router(models_router)

__all__ = ["ai_router"]
