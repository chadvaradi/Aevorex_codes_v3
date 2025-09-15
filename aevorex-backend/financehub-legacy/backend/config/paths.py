"""
Filesystem path settings.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field, model_validator, DirectoryPath

from ._core import get_project_root, logger


class PathSettings(BaseModel):
    """Fájlrendszerbeli elérési utak."""

    PROJECT_ROOT: DirectoryPath = Field(default_factory=get_project_root)
    STATIC_DIR: Path | None = None
    TEMPLATES_DIR: Path | None = None
    LOG_DIR: Path | None = None

    @model_validator(mode="after")
    def _resolve_and_verify_paths(self) -> "PathSettings":
        if self.STATIC_DIR is None:
            self.STATIC_DIR = self.PROJECT_ROOT / "shared/frontend/dist"

        self.LOG_DIR = self._ensure_directory(
            self.LOG_DIR, self.PROJECT_ROOT / "logs", "LOG_DIR", True
        )

        return self

    def _ensure_directory(
        self,
        path: Path | None,
        default_path: Path,
        name: str,
        check_writable: bool = False,
    ) -> Path:
        """Helper to create and verify a directory."""
        dir_to_check = path or default_path

        try:
            dir_to_check.mkdir(parents=True, exist_ok=True)
            if check_writable and not (
                os.access(dir_to_check, os.W_OK) and os.access(dir_to_check, os.R_OK)
            ):
                logger.warning(
                    f"{name} directory is not readable/writable: {dir_to_check}"
                )
        except Exception as e:
            logger.error(
                f"Failed to create or access {name} directory at {dir_to_check}: {e}"
            )
            raise

        return dir_to_check
