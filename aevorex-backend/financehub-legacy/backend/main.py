# backend/main.py
# =============================================================================
# Main Application Entry Point
# =============================================================================

import sys
import os
from pathlib import Path

# --- Path setup to allow module imports ---
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Now we can import backend modules
from backend.config.env_loader import load_environment_once

# Ensure env variables are loaded once at startup
load_environment_once()

# ---------------------------------------------------------------------------
# Note: setuptools>=70.0 is now included in requirements.txt to provide
# pkg_resources for pandas_ta compatibility. No shim needed.
# ---------------------------------------------------------------------------

# --- Import modules after path is set ---
from backend.app_factory import create_app

# --- Create FastAPI application ---
app = create_app()

# --- Development server execution ---
if __name__ == "__main__":
    import uvicorn

    reload_enabled = os.getenv("UVICORN_RELOAD", "false").lower() in {
        "1",
        "true",
        "yes",
    }
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8084,
        reload=reload_enabled,
        reload_dirs=[str(current_dir)] if reload_enabled else None,
    )
