"""
Text Processing Helper Functions
===============================

Centralized text processing utilities for the FinanceHub application.
Consolidated from text_cleaners, text_parsers, and text_validators modules.
"""

import logging
import math
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode

import pandas as pd
from pydantic import HttpUrl, ValidationError

try:
    from backend.utils.logger_config import get_logger

    package_logger = get_logger(f"aevorex_finbot.core.helpers.{__name__}")
except ImportError:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    package_logger = logging.getLogger(
        f"aevorex_finbot.core.helpers_fallback.{__name__}"
    )


# --- Text Cleaning Section ---


def _clean_value(value: Any, *, context: str = "") -> Any | None:
    """
    Tisztítja és validálja a bemeneti értéket. Eltávolítja a placeholder
    értékeket (None, NaN, Inf, üres/specifikus placeholder stringek).
    """
    if value is None or pd.isna(value):
        return None

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value

    if isinstance(value, str):
        stripped_value = value.strip()
        if not stripped_value:
            return None
        placeholder_strings = {
            "none",
            "na",
            "n/a",
            "-",
            "",
            "#n/a",
            "null",
            "nan",
            "nat",
            "undefined",
            "nil",
            "(blank)",
            "<na>",
        }
        if stripped_value.lower() in placeholder_strings:
            return None
        return stripped_value

    return value


def parse_optional_float(value: Any, *, context: str = "") -> float | None:
    """
    Konvertálja a bemeneti értéket float-tá, ha lehetséges.
    Ha nem konvertálható vagy placeholder, None-t ad vissza.
    """
    cleaned = _clean_value(value, context=context)
    if cleaned is None:
        return None

    try:
        if isinstance(cleaned, (int, float)):
            return float(cleaned)
        if isinstance(cleaned, str):
            # Eltávolítja a szóközöket és egyéb karaktereket
            cleaned_str = cleaned.replace(",", "").replace(" ", "")
            return float(cleaned_str)
    except (ValueError, TypeError):
        package_logger.warning(
            f"Could not parse float from {value} in context: {context}"
        )
        return None

    return None


def parse_optional_int(value: Any, *, context: str = "") -> int | None:
    """
    Konvertálja a bemeneti értéket int-té, ha lehetséges.
    Ha nem konvertálható vagy placeholder, None-t ad vissza.
    """
    cleaned = _clean_value(value, context=context)
    if cleaned is None:
        return None

    try:
        if isinstance(cleaned, (int, float)):
            return int(cleaned)
        if isinstance(cleaned, str):
            # Eltávolítja a szóközöket és egyéb karaktereket
            cleaned_str = cleaned.replace(",", "").replace(" ", "")
            return int(float(cleaned_str))  # float-on keresztül int-té
    except (ValueError, TypeError):
        package_logger.warning(
            f"Could not parse int from {value} in context: {context}"
        )
        return None

    return None


# --- Text Parsing Section ---


def _validate_date_string(date_str: str) -> bool:
    """
    Validálja, hogy a dátum string megfelelő formátumú-e (YYYY-MM-DD).
    """
    if not isinstance(date_str, str):
        return False

    # YYYY-MM-DD formátum regex
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, date_str):
        return False

    try:
        from datetime import datetime

        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def normalize_url(url: str) -> str | None:
    """
    Normalizálja az URL-t, eltávolítja a felesleges részeket.
    """
    if not isinstance(url, str) or not url.strip():
        return None

    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    except Exception:
        package_logger.warning(f"Could not normalize URL: {url}")

    return None


# --- Text Validation Section ---


def validate_http_url(url: str) -> bool:
    """
    Validálja, hogy a string érvényes HTTP/HTTPS URL-e.
    """
    if not isinstance(url, str) or not url.strip():
        return False

    try:
        HttpUrl(url)
        return True
    except ValidationError:
        return False


def clean_url_params(url: str) -> str:
    """
    Eltávolítja a felesleges URL paramétereket és normalizálja az URL-t.
    """
    if not isinstance(url, str) or not url.strip():
        return ""

    try:
        parsed = urlsplit(url)
        # Eltávolítja a query paramétereket
        clean_parsed = parsed._replace(query="", fragment="")
        return urlunsplit(clean_parsed)
    except Exception:
        package_logger.warning(f"Could not clean URL: {url}")
        return url


def build_url_with_params(base_url: str, params: dict[str, Any]) -> str:
    """
    Épít egy URL-t paraméterekkel.
    """
    if not isinstance(base_url, str) or not base_url.strip():
        return ""

    try:
        parsed = urlsplit(base_url)
        query_params = parse_qs(parsed.query)

        # Hozzáadja az új paramétereket
        for key, value in params.items():
            if value is not None:
                query_params[key] = [str(value)]

        # Építi az új query stringet
        new_query = urlencode(query_params, doseq=True)
        new_parsed = parsed._replace(query=new_query)

        return urlunsplit(new_parsed)
    except Exception:
        package_logger.warning(f"Could not build URL with params: {base_url}, {params}")
        return base_url
