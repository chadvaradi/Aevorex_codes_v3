"""
Environment loader for Aevorex FinBot backend.
Loads env.local exactly once and sets a flag so subsequent calls are no-ops.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

_LOGGER = logging.getLogger("aevorex_finbot.env_loader")
_FLAG_NAME = "_AEVOREX_ENV_LOADED"


def load_environment_once() -> None:
    """Load env.local (or .env) only once across the entire process.

    Hardens lookup so that uvicorn reload children and non-root CWD-ek esetén is
    garantált legyen a betöltés. A .env.* fájlokból származó értékek FELÜLÍRJÁK
    a folyamatban lévő üres/hiányzó változókat (override=True), de nem írják felül
    a már explicit beállított OS env értékeket.
    """
    if os.environ.get(_FLAG_NAME):
        return

    # 1) FinanceHub legacy env.local preferálása (mindig ez legyen az elsődleges forrás)
    root_env_path = None
    try:
        this_file = Path(__file__).resolve()
        financehub_env = this_file.parent.parent / "env.local"  # backend/env.local
        if financehub_env.exists():
            root_env_path = str(financehub_env)
    except Exception:
        root_env_path = None

    # 2) Ha van projektgyökér env.local → töltsük be először (override=True)
    if root_env_path:
        load_dotenv(root_env_path, override=True)
        _LOGGER.info("✅ Environment loaded from %s", root_env_path)
    else:
        _LOGGER.warning("⚠️ root env.local not found – attempting nearest .env lookup.")
        # 3) Másodlagos: legközelebbi env.local felkutatása
        env_path = find_dotenv("env.local")
        if env_path:
            load_dotenv(env_path, override=True)
            _LOGGER.info("✅ Environment loaded from %s", env_path)
        else:
            _LOGGER.warning(
                "⚠️ env.local not found – relying on system environment variables."
            )

    # 4) Másodlagos: .env mint kiegészítő forrás (nem kötelező)
    dot_env = find_dotenv()
    if dot_env:
        load_dotenv(dot_env, override=False)

    os.environ[_FLAG_NAME] = "1"
    
    # Validate environment variables after loading
    validate_env()

def validate_env():
    """Check presence of critical environment variables."""
    REQUIRED_ENV_VARS = [
        "FINBOT_API_KEYS__OPENROUTER",
        "FINBOT_EODHD__API_KEY", 
        "FINBOT_GOOGLE_AUTH__SECRET_KEY",
    ]
    missing = []
    for var in REQUIRED_ENV_VARS:
        value = os.environ.get(var)
        if value is None or value.strip() == "":
            missing.append(var)
    if missing:
        _LOGGER.error(f"Missing required environment variables: {', '.join(missing)}")
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    # Optionally: log success at debug level
    _LOGGER.debug("All required environment variables are present.")


# validate_env() moved to load_environment_once() function
