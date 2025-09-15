# modules/financehub/backend/config/_core.py
import logging
from pathlib import Path
from typing import List

# --- Logger ---
logger = logging.getLogger(__name__)


# --- Path Utilities ---
def get_project_root() -> Path:
    """
    Navigates up from the current file to find the project root,
    which is identified by the presence of 'modules', '.git', or 'financehub-legacy'.
    """
    # Start from the directory of the current file
    current_path = Path(__file__).parent
    # Look for a known marker, like the 'modules' directory, '.git' folder, or 'financehub-legacy'
    while current_path != current_path.parent:
        if (
            (current_path / "modules").is_dir() 
            or (current_path / ".git").is_dir()
            or (current_path / "financehub-legacy").is_dir()
        ):
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError("Project root could not be determined.")


# --- Parsing Utilities ---
def _parse_env_list_str_utility(env_var_value: str | None) -> List[str]:
    """
    Parses a comma-separated string from an environment variable into a list of strings.
    Returns an empty list if the input is None or empty.
    """
    if not env_var_value:
        return []
    return [item.strip() for item in env_var_value.split(",") if item.strip()]


# --- Settings Loader Utility ---
from pydantic_settings import BaseSettings
from .env_loader import load_environment_once

def load_settings(settings_cls: type[BaseSettings]):
    """
    Initializes a settings object from a Pydantic BaseSettings class,
    using the shared env_loader.
    This ensures consistent environment variable loading across configs.
    """
    return load_environment_once(settings_cls)
