# backend/api/endpoints/well_known/well_known_router.py
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from pathlib import Path
import os

router = APIRouter()

@router.get("/.well-known/ai-plugin.json")
async def get_ai_plugin(request: Request):
    """Serve AI plugin manifest for ChatGPT compatibility."""
    # Go up from backend/api/endpoints/well_known/ to project root, then to .well-known/
    well_known_path = Path(__file__).parent.parent.parent.parent.parent / ".well-known" / "ai-plugin.json"
    if well_known_path.exists():
        return FileResponse(well_known_path, media_type="application/json")
    return {"error": "AI plugin manifest not found"}

@router.get("/.well-known/openapi.yaml")
async def get_openapi_spec(request: Request):
    """Serve OpenAPI specification for MCP compatibility."""
    # Go up from backend/api/endpoints/well_known/ to project root, then to .well-known/
    well_known_path = Path(__file__).parent.parent.parent.parent.parent / ".well-known" / "openapi.yaml"
    if well_known_path.exists():
        return FileResponse(well_known_path, media_type="application/x-yaml")
    return {"error": "OpenAPI specification not found"}

@router.get("/.well-known/health")
async def well_known_health():
    """Health check for .well-known endpoints."""
    return {
        "status": "ok",
        "message": "Well-known endpoints are available",
        "endpoints": [
            "/.well-known/ai-plugin.json",
            "/.well-known/openapi.yaml"
        ]
    }
