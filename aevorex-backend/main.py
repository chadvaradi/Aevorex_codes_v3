from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
import uuid
import time
import os

from api.settings import settings

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    lambda msg: print(msg, end=""),  # Console output only
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> | {message}"
)

app = FastAPI(title=settings.api_title, version=settings.api_version)

# --- Statikus fájl kiszolgálás a képekhez ---
from pathlib import Path
STATIC_ROOT = Path(__file__).parent / "static"
STATIC_IMAGES_DIR = STATIC_ROOT / "images"

# Health & permission check
try:
    os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)
    test_file = STATIC_IMAGES_DIR / ".write_test"
    with open(test_file, "wb") as f:
        f.write(b".")
    os.remove(test_file)
    print(f"[static-health] ✅ Static directory writable: {STATIC_IMAGES_DIR}")
except Exception as e:
    raise RuntimeError(f"Static dir not writable: {STATIC_IMAGES_DIR} ({e})")

app.mount("/static", StaticFiles(directory=str(STATIC_ROOT)), name="static")

# --- CORS beállítás (wildcard-fix) ---
origins = settings.cors_origins
wildcard = len(origins) == 1 and origins[0] == "*"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if wildcard else origins,
    allow_credentials=False if wildcard else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    correlation_id = str(uuid.uuid4())[:8]
    logger.error(f"HTTP {exc.status_code}: {exc.detail} | Correlation ID: {correlation_id}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "correlation_id": correlation_id,
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    correlation_id = str(uuid.uuid4())[:8]
    logger.error(f"Unhandled exception: {str(exc)} | Correlation ID: {correlation_id}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "correlation_id": correlation_id,
            "timestamp": time.time()
        }
    )

# --- Health & meta ---
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"version": settings.api_version}

# --- API mountok / moduláris routerek ---
from api.core.router import router as core_router
app.include_router(core_router, prefix="/api/core", tags=["core"])

# mount finance router
from api.finance.router import router as finance_router
app.include_router(finance_router, prefix="/api/finance", tags=["finance"])

# mount llm router
from api.llm.router import router as llm_router
app.include_router(llm_router, prefix="/api/chat", tags=["chat"])

# mount image router (if exists)
try:
    from api.image.router import router as image_router
    app.include_router(image_router, prefix="/api/image", tags=["image"])
    logger.info("Image router mounted successfully.")
except Exception as e:
    logger.exception("Image router failed to mount")

logger.info("App initialized")
