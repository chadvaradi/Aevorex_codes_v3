from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, constr, conint


# ---- Requests ----

class ImageGenRequest(BaseModel):
    prompt: constr(strip_whitespace=True, min_length=1)
    model: Optional[str] = Field(
        default=None,
        description="Alias vagy teljes modell id; ha None → catalogue default."
    )
    n: conint(ge=1, le=8) = 1
    size: constr(pattern=r"^\d{2,4}x\d{2,4}$") = "1024x1024"

    # Opcionális extra paraméterek – csak továbbítjuk a provider felé, ha vannak
    seed: Optional[int] = None
    quality: Optional[Literal["high", "standard"]] = None
    style: Optional[str] = None
    negative_prompt: Optional[str] = None
    background: Optional[Literal["transparent", "white", "black"]] = None
    response_format: Optional[Literal["url", "b64_json"]] = None


class ImageAnalyzeRequest(BaseModel):
    image_data: constr(min_length=1)  # lehet pure b64 vagy data URL
    question: str = "Describe this image in detail"


class ImageAnalyzeResponse(BaseModel):
    model: str
    question: str
    analysis: str


# ---- Responses ----

class ImageItem(BaseModel):
    url: Optional[str] = None
    b64: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    mime_type: Optional[str] = None
    revised_prompt: Optional[str] = None
    seed: Optional[int] = None


class ImageGenResponse(BaseModel):
    model: str
    items: List[ImageItem]
    # opcionális meta
    processing_time_ms: Optional[int] = None


# ---- Models listing ----

class ImageModelsResponse(BaseModel):
    models: dict[str, str]  # alias -> id
    default: str
