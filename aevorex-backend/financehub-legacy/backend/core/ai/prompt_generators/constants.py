from typing import Final
from pathlib import Path

# --- Modul Szintű Konstansok ---
PROMPT_TEMPLATE_DIR: Final[Path] = Path(__file__).parent.parent / "prompt_templates"
DEFAULT_PREMIUM_ANALYSIS_TEMPLATE_FILE: Final[str] = "premium_analysis_v1.txt"

# Fallback üzenetek a formázókhoz
FALLBACK_PRICE_DATA: Final[str] = "{ Hiba az árfolyamadatok formázása közben }"
FALLBACK_INDICATOR_DATA: Final[str] = (
    "Hiba a technikai indikátorok feldolgozása közben."
)
FALLBACK_NEWS_DATA: Final[str] = "Hiba a hírek feldolgozása közben."
FALLBACK_FUNDAMENTAL_DATA: Final[str] = (
    "Hiba a vállalati alapadatok feldolgozása közben."
)
FALLBACK_FINANCIALS_DATA: Final[str] = (
    "Hiba a pénzügyi kimutatások adatainak feldolgozása közben."
)
FALLBACK_EARNINGS_DATA: Final[str] = (
    "Hiba a vállalati eredményjelentések adatainak feldolgozása közben."
)
UNEXPECTED_HELPER_ERROR: Final[str] = (
    "HIBA: Adatformázó segédfüggvény nem futott le, vagy váratlan hibát adott."
)
DEFAULT_NA_VALUE: Final[str] = "N/A"
DEFAULT_PROMPT_NA_TEXT: Final[str] = "N/A"

# --- Konfigurálható Értékek ---
DEFAULT_RELEVANCE_THRESHOLD: Final[float] = 0.8
DEFAULT_TARGET_NEWS_COUNT: Final[int] = 5
AI_PRICE_DAYS_FOR_PROMPT_DEFAULT: Final[int] = 60
