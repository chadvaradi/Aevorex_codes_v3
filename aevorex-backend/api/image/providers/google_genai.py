from __future__ import annotations

import asyncio
import base64
from dataclasses import asdict
from io import BytesIO
from typing import Any, Dict, List, Optional

import httpx
from google import genai

from api.settings import settings
from api.image.catalogue import resolve_model
from .base import BaseImageProvider, ImageGenResult


class GoogleGeminiImageProvider(BaseImageProvider):
    """
    Google Gemini alapú képgenerálás és képelemzés a hivatalos (új) google-genai SDK-val.

    - Env: GEMINI_API_KEY (settings.google_api_key)
    - Képgenerálás:   models.generate_content(model="gemini-2.5-flash-image-preview", contents=[prompt])
                      -> inline_data (bájt) részeket visszaadjuk base64-ként
    - Képelemzés (VQA): models.generate_content(contents=[image_part, question])
                      -> szöveg választ adunk vissza
    """

    def __init__(self) -> None:
        self.api_key = settings.google_api_key
        if not self.api_key:
            raise RuntimeError("Missing GEMINI_API_KEY")

        print(f"[google-gemini] API key loaded: {self.api_key[:8]}...")

        # A google-genai kliens szinkron API; FastAPI alatt háttérszálon hívjuk meg.
        self.client = genai.Client(api_key=self.api_key)

        # Alapértelmezett modell-alias (feloldást a catalogue végzi, itt csak fallback)
        self.default_model_id = "gemini-2.5-flash-image-preview"

    # ---------- belső segéd függvények ----------

    async def _fetch_bytes_from_url(self, url: str) -> bytes:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.content

    def _part_to_image_results(
        self,
        part: Any,
        *,
        prompt: str,
        default_mime: str = "image/png",
    ) -> List[ImageGenResult]:
        """
        Egyetlen Part objektumból (inline_data / image_url / text) képi találatokat ad vissza.
        """
        import re
        
        _B64_RE = re.compile(r'^[A-Za-z0-9+/=_-]+$')
        
        def _looks_like_b64_bytes(buf: bytes) -> tuple[bool, bytes | None]:
            """Ha buf ASCII és valid base64, visszaadja a dekódolt bájtokat is."""
            try:
                s = buf.decode("ascii")
            except UnicodeDecodeError:
                return False, None
            if not _B64_RE.match(s):
                return False, None
            try:
                raw = base64.b64decode(s, validate=True)
                return True, raw
            except Exception:
                return False, None

        results: List[ImageGenResult] = []

        # inline_data (kép bájtban, SDK már kitölti a mime_type-et is sokszor)
        if getattr(part, "inline_data", None) is not None:
            data = part.inline_data.data  # lehet bytes VAGY base64 szöveg bytes-ben
            mime = getattr(part.inline_data, "mime_type", None) or default_mime

            b64: str
            raw: bytes

            if isinstance(data, (bytes, bytearray)):
                # Már base64? (ASCII)
                is_b64, maybe_raw = _looks_like_b64_bytes(data)
                if is_b64 and maybe_raw:
                    b64 = data.decode("ascii")      # ne kódoljuk újra
                    raw = maybe_raw                 # valódi képbájtok
                else:
                    raw = bytes(data)
                    b64 = base64.b64encode(raw).decode("ascii")
            elif isinstance(data, str):
                # Biztosan base64 sztring
                b64 = data
                raw = base64.b64decode(data, validate=False)
            else:
                # végső fallback
                raw = bytes(data)
                b64 = base64.b64encode(raw).decode("ascii")

            results.append(
                ImageGenResult(
                    url=None,
                    b64=b64,
                    width=None,
                    height=None,
                    mime_type=mime,
                    revised_prompt=prompt,
                    seed=None,
                    raw={"data": raw},  # ha később használnád
                )
            )
            return results

        # image_url (ritkább az outputban, de kezeljük)
        if getattr(part, "image_url", None) is not None:
            url = part.image_url.url
            results.append(
                ImageGenResult(
                    url=url,
                    b64=None,
                    width=None,
                    height=None,
                    mime_type=default_mime,
                    revised_prompt=prompt,
                    seed=None,
                    raw=None,
                )
            )
            return results

        # text / egyéb: nem kép
        return results

    # ---------- publikus API (interface implementáció) ----------

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
        Kép(ek) generálása promptból a Gemini image-preview modellel.

        Megjegyzések:
        - A google-genai jelenlegi (2025) implementációjában nincs stabil "n" paraméter;
          ha több képre van szükség, a hívást egymás után végezzük (n-szer).
        - A size paramétert a modell jellemzően figyelmen kívül hagyja, vagy kísérleti;
          itt elfogadjuk, de nem garantált, hogy a modell tiszteletben tartja.
        """
        model_id = resolve_model(model) if model else self.default_model_id
        # Eltávolítjuk a "google/" prefix-et, ha van
        if model_id.startswith("google/"):
            model_id = model_id[7:]  # "google/".__len__() == 7
        # A google-genai kliens szinkron → tegyük háttérszálra.
        async def _one_call() -> List[ImageGenResult]:
            def _sync_call():
                # A models.generate_content szinkron hívás.
                return self.client.models.generate_content(
                    model=model_id,
                    contents=[prompt],
                )

            resp = await asyncio.to_thread(_sync_call)

            results: List[ImageGenResult] = []
            # Válasz: candidates -> content.parts
            for cand in getattr(resp, "candidates", []) or []:
                content = getattr(cand, "content", None)
                parts = getattr(content, "parts", []) if content else []
                for p in parts:
                    results.extend(self._part_to_image_results(p, prompt=prompt))

            return results

        # Ha több képet kérünk, n-szer hívjuk (egyszerű és megbízható)
        all_results: List[ImageGenResult] = []
        for _ in range(max(1, int(n))):
            batch = None
            # Retry logika a Google API intermittens hibáihoz
            for retry in range(3):
                try:
                    batch = await _one_call()
                    if batch:
                        all_results.extend(batch)
                    break  # Sikeres volt, kilépünk a retry loop-ból
                except Exception as e:
                    # Némi diagnosztika, de nem dobjuk el a teljes kérést.
                    print(f"[google-gemini] generate() call failed (attempt {retry + 1}/3): {e}")
                    # Ha 429 quota hiba, dobjuk fel
                    msg = str(e)
                    if "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
                        raise RuntimeError("429: Gemini quota exceeded")
                    # Ha 500 INTERNAL és van még retry, várunk egy kicsit
                    if "500 INTERNAL" in msg and retry < 2:
                        await asyncio.sleep(1)  # 1 másodperc várakozás
                        continue
                    # Ha nincs batch és nincs több retry, dobjuk fel
                    if not batch and retry == 2:
                        raise

        return all_results

    async def analyze(
        self,
        image_data: str,  # base64 dataURL, tiszta base64, vagy URL
        question: str = "Describe this image in detail",
        **kwargs: Any,
    ) -> str:
        """
        Kép megértése (Vision Q&A) — szöveges választ ad vissza.
        """
        # Képet bájtokra alakítjuk
        try:
            if image_data.startswith("data:"):
                # dataURL → base64 rész
                header, _, payload = image_data.partition(",")
                mime = header.split(";")[0][5:] or "image/png"  # data: után
                img_bytes = base64.b64decode(payload)
            elif image_data.startswith("http"):
                img_bytes = await self._fetch_bytes_from_url(image_data)
                mime = "image/jpeg"
            else:
                # feltételezzük, hogy tiszta base64
                img_bytes = base64.b64decode(image_data)
                mime = "image/png"
        except Exception as e:
            raise RuntimeError(f"Invalid image input for analyze(): {e}")

        # A models.generate_content szinkron → háttérszálra tesszük.
        def _sync_call():
            # Egyszerű string lista használata a google-genai SDK-hoz
            return self.client.models.generate_content(
                model="gemini-2.5-flash",  # Vision-re a chat modellt használjuk
                contents=[question, genai.Part.from_bytes(data=img_bytes, mime_type=mime)],
            )

        try:
            resp = await asyncio.to_thread(_sync_call)
        except Exception as e:
            raise RuntimeError(f"Gemini analyze() failed: {e}")

        # Szöveg kinyerése (a google-genai SDK .text tulajdonságot biztosít)
        text = getattr(resp, "text", None)
        if text:
            return text

        # Ha nincs .text, próbáljuk összefűzni a text partokat
        chunks: List[str] = []
        for cand in getattr(resp, "candidates", []) or []:
            content = getattr(cand, "content", None)
            parts = getattr(content, "parts", []) if content else []
            for p in parts:
                # egyes SDK verziókban a p.text lehet
                t = getattr(p, "text", None)
                if isinstance(t, str):
                    chunks.append(t)
        return "\n".join(chunks) if chunks else "(no text response)"

    async def aclose(self) -> None:
        """Jelenleg nincs aktív erőforrás (httpx kliens nélkül), de a jövőre nézve itt a hook."""
        return