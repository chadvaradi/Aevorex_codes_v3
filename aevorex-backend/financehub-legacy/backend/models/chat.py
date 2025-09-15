"""
Pydantic models for Chat functionality.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for a user's chat message."""

    message: str = Field(..., min_length=1, description="The user's message.")


class ChatResponse(BaseModel):
    """Response model for the AI's chat message."""

    content: str = Field(..., description="The AI's response message.")
    type: str = Field(default="message", description="The type of the response.")
    is_last: bool = Field(
        default=True,
        description="Indicates if this is the final message in the stream.",
    )


# --- New request models for configuration endpoints ---


class ChatModelRequest(BaseModel):
    """Payload to set preferred AI model for a user session."""

    session_id: str = Field(
        ..., min_length=1, description="Client-side generated session identifier"
    )
    model: str = Field(
        ..., min_length=1, description="Model identifier as returned by /ai/models"
    )


class DeepToggleRequest(BaseModel):
    """Payload to opt-in/opt-out of deep analysis for a specific chat."""

    chat_id: str = Field(
        ..., min_length=1, description="Unique chat id (frontend generated)"
    )
    needs_deep: bool = Field(..., description="Whether deep analysis is requested")
