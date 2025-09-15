"""
Chat Schemas
Pydantic models for chat endpoints, ensuring consistency with provider responses and improved validation.
"""

from typing import List, Optional, Literal, Any
from pydantic import BaseModel, Field, validator


class Message(BaseModel):
    """Represents a single chat message with a role and non-empty content."""
    role: Literal["user", "assistant", "system"]
    content: str

    @validator('content')
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("content must not be empty")
        return v


class ChatRequest(BaseModel):
    """Request model for chat endpoint, including messages, model info, and metadata for logging."""
    messages: List[Message]
    model: Optional[str] = Field(None, description="Alias or full model ID")
    ticker: Optional[str] = Field(None, description="Stock ticker symbol")
    stream: Optional[bool] = Field(False, description="Enable streaming response")
    timestamp: Optional[int] = Field(None, description="Unix timestamp for request logging/debugging")


class ChatResponse(BaseModel):
    """Response model for chat endpoint, matching provider response structure."""
    id: Optional[str] = Field(None, description="Unique identifier for the response")
    object: Optional[str] = Field(None, description="Type of object returned")
    created: Optional[int] = Field(None, description="Unix timestamp when response was created")
    model: Optional[str] = Field(None, description="Model ID used for generating the response")
    choices: Optional[List[dict[str, Any]]] = Field(None, description="List of generated choices")
    content: Optional[str] = Field(None, description="Primary content of the response")
    usage: Optional[dict[str, Any]] = Field(None, description="Usage statistics and tokens")


class ModelsResponse(BaseModel):
    """Response model listing available models with explicit default model ID."""
    models: dict[str, str]
    default_model_id: str = Field(..., description="Default model ID to be used if none specified")

