"""
Filesystem path settings.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field, model_validator

from ._core import get_project_root, logger


class PathSettings(BaseModel):
    """Fájlrendszerbeli elérési utak."""

    PROJECT_ROOT: str = Field(default_factory=lambda: str(get_project_root()))
    STATIC_DIR: str | None = None
    TEMPLATES_DIR: str | None = None
    LOG_DIR: str | None = None

    @model_validator(mode="after")
    def _resolve_and_verify_paths(self) -> "PathSettings":
        if self.STATIC_DIR is None:
            self.STATIC_DIR = str(Path(self.PROJECT_ROOT) / "shared/frontend/dist")

        self.LOG_DIR = self._ensure_directory(
            self.LOG_DIR, str(Path(self.PROJECT_ROOT) / "logs"), "LOG_DIR", True
        )

        return self

    def _ensure_directory(
        self,
        path: str | None,
        default_path: str,
        name: str,
        check_writable: bool = False,
    ) -> str:
        """Helper to create and verify a directory."""
        dir_to_check = path or default_path
        dir_path = Path(dir_to_check)

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            if check_writable and not (
                os.access(dir_path, os.W_OK) and os.access(dir_path, os.R_OK)
            ):
                logger.warning(
                    f"{name} directory is not readable/writable: {dir_path}"
                )
        except Exception as e:
            logger.error(
                f"Failed to create or access {name} directory at {dir_path}: {e}"
            )
            raise

        return str(dir_path)
