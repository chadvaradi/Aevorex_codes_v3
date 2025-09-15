"""
Image utility functions for base64 to file conversion
"""
import os
import base64
import uuid
import urllib.parse
import binascii
from typing import Optional, Tuple


def _strip_data_url(b64: str) -> Tuple[Optional[str], str]:
    """
    Data URL normalizálás: data:image/png;base64,... -> (mime, pure_b64)
    """
    if b64.startswith("data:"):
        header, _, payload = b64.partition(",")
        mime = header.split(";")[0][5:] or "image/png"
        return mime, payload
    return None, b64


def _normalize_b64(s: str) -> bytes:
    """
    Robusztus base64 dekódolás - kezeli az URL-enkódolást, whitespace-eket, paddinget
    """
    # URL-encoded? (%2B, %2F, %3D)
    if "%" in s:
        s = urllib.parse.unquote(s)
    
    # whitespace-ek ki
    s = "".join(s.split())
    
    # ha urlsafe variáns jött (-, _)
    try:
        return base64.b64decode(s, validate=True)
    except Exception:
        # pótold a paddinget
        pad = (-len(s)) % 4
        s = s + ("=" * pad)
        try:
            return base64.urlsafe_b64decode(s)
        except Exception:
            return base64.b64decode(s)


def save_base64_image(b64: str, out_dir: str, mime: Optional[str] = None) -> Tuple[str, str]:
    """
    Base64 string dekódolása és fájlba mentése.
    
    Args:
        b64: Base64 encoded image string
        out_dir: Output directory path
        mime: MIME type (optional)
    
    Returns:
        Tuple[filename, mime_type]
    
    Raises:
        binascii.Error: Invalid base64 input
    """
    try:
        mime2, payload = _strip_data_url(b64)
        if not mime:
            mime = mime2 or "image/png"

        # kiterjesztés MIME alapján
        ext = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
        }.get(mime, "png")

        raw = _normalize_b64(payload)

        os.makedirs(out_dir, exist_ok=True)
        fname = f"{uuid.uuid4().hex}.{ext}"
        fpath = os.path.join(out_dir, fname)
        with open(fpath, "wb") as f:
            f.write(raw)
        print(f"[image-save] wrote {fpath} ({len(raw)} bytes, mime={mime})")
        return fname, mime
    except binascii.Error as e:
        raise binascii.Error(f"Invalid base64: {e}")
