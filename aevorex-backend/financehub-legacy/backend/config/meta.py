"""
Application meta-information settings.
"""

from pydantic import BaseModel, Field, model_validator


class ApplicationMetaSettings(BaseModel):
    """General application meta-information."""

    NAME: str = Field(default="Aevorex FinBot", description="Internal application name.")
    VERSION: str = Field(
        default="2.2.0", description="Backend API version (Semantic Versioning)."
    )
    TITLE: str = Field(
        default="AEVOREX FinBot Premium API",
        description="Public API title (OpenAPI/Swagger).",
    )
    DESCRIPTION: str = Field(
        default="Aevorex Financial Intelligence Bot API. Real-time stock data, AI-driven analysis, and insights.",
        description="Detailed description for API documentation.",
    )

    @model_validator(mode="after")
    def _update_title_with_version(self) -> "ApplicationMetaSettings":
        """Updates the title with version number."""
        if self.VERSION not in self.TITLE:
            self.TITLE = f"{self.TITLE} (v{self.VERSION})"
        return self
