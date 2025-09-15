"""
Settings for uploaded file processing.
"""

from pydantic import BaseModel, Field, model_validator
from pydantic.types import PositiveInt, NonNegativeInt

from ._core import _parse_env_list_str_utility


class FileProcessingSettings(BaseModel):
    """Beállítások a feltöltött fájlok feldolgozásához."""

    MAX_SIZE_BYTES: PositiveInt = Field(default=50 * 1024 * 1024)
    ALLOWED_MIME_TYPES: list[str] = Field(
        default_factory=lambda: [
            "text/plain",
            "text/markdown",
            "text/csv",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/gif",
            "text/x-python",
            "application/javascript",
            "text/html",
            "text/css",
            "application/json",
        ]
    )
    ALLOWED_EXTENSIONS: list[str] = Field(
        default_factory=lambda: [
            "txt",
            "md",
            "csv",
            "pdf",
            "docx",
            "jpg",
            "jpeg",
            "png",
            "webp",
            "gif",
            "py",
            "js",
            "html",
            "css",
            "json",
        ]
    )
    CHUNK_SIZE: PositiveInt = Field(default=1000)
    CHUNK_OVERLAP: NonNegativeInt = Field(default=100)

    @model_validator(mode="before")
    @classmethod
    def _parse_string_list_to_lower(cls, values):
        if "ALLOWED_MIME_TYPES" in values and values["ALLOWED_MIME_TYPES"]:
            values["ALLOWED_MIME_TYPES"] = _parse_env_list_str_utility(
                values["ALLOWED_MIME_TYPES"], "ALLOWED_MIME_TYPES", lowercase_items=True
            )
        if "ALLOWED_EXTENSIONS" in values and values["ALLOWED_EXTENSIONS"]:
            values["ALLOWED_EXTENSIONS"] = _parse_env_list_str_utility(
                values["ALLOWED_EXTENSIONS"], "ALLOWED_EXTENSIONS", lowercase_items=True
            )
        return values
