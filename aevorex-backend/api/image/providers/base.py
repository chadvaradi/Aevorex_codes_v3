from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ImageGenResult:
    """Egyetlen generált kép metaadatai."""
    url: Optional[str] = None          # preferált: CDN/HTTP URL
    b64: Optional[str] = None          # fallback: base64 (ha nincs URL)
    revised_prompt: Optional[str] = None
    seed: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    raw: Optional[Dict[str, Any]] = None  # szolgáltatói nyers válasz-szelet


class BaseImageProvider(ABC):
    """Képgeneráló provider absztrakt bázisosztály."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        n: int = 1,
        size: str = "1024x1024",
        **kwargs: Any,
    ) -> List[ImageGenResult]:
        """
        Képe(ke)t generál a megadott prompt alapján.

        Returns:
            A generált képek listája (URL-első, base64-fallback).
        """
