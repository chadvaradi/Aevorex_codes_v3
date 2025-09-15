from __future__ import annotations
from typing import Any

from ....utils.logger_config import get_logger
from ....models.stock import CompanyOverview
from .constants import FALLBACK_FUNDAMENTAL_DATA
from ..helpers import safe_format_value

logger = get_logger(__name__)

# Define the mapping from CompanyOverview fields to descriptive labels
# Using a structured dict for better control over order and formatting
FIELD_MAPPING = {
    "Áttekintés": {
        "Cégnév": "name",
        "Leírás": "description",
        "Iparág": "industry",
        "Szektor": "sector",
        "Ország": "country",
        "Weboldal": "url",
    },
    "Pénzügyi Mutatók": {
        "Piaci kapitalizáció": ("market_capitalization", "market_cap"),
        "P/E ráta (forward)": ("pe_ratio_forward", "pe_forward"),
        "P/E ráta (trailing)": ("pe_ratio_trailing", "pe_trailing"),
        "P/B ráta": ("price_to_book_ratio", "pb_ratio"),
        "P/S ráta": ("price_to_sales_ratio", "ps_ratio"),
        "PEG ráta": ("peg_ratio", "peg"),
        "Osztalékhozam (%)": ("dividend_yield", "dividend_yield"),
        "EPS (trailing)": ("eps_trailing", "eps_trailing"),
        "Béta": ("beta", "beta"),
    },
    "Technikai- és Várakozási Adatok": {
        "52 hetes csúcs": ("high_52_week", "high_52_week"),
        "52 hetes mélypont": ("low_52_week", "low_52_week"),
        "Elemzői célár": ("analyst_target_price", "analyst_target"),
        "Árbevétel (TTM)": ("revenue_ttm", "revenue_ttm"),
        "EBITDA": ("ebitda", "ebitda"),
    },
}


async def format_fundamental_data_for_prompt(
    symbol: str, company_overview: CompanyOverview | None
) -> tuple[str, bool]:
    """
    Formats the CompanyOverview data into a structured string for the AI prompt.
    Handles potential errors gracefully and ALWAYS returns a (string, bool) tuple.
    """
    func_name = "format_fundamental_data_for_prompt"
    logger.debug(f"[{symbol}] Running {func_name}..")
    if not company_overview:
        logger.warning(
            f"[{symbol}] {func_name}: Skipping, no CompanyOverview data provided."
        )
        return "Vállalati alapadatok nem állnak rendelkezésre.", False

    summary_points: dict[str, Any] = {}
    data_found = False

    try:
        # Helper to check if a value is present and not a 'not available' marker
        def is_valid(value: Any) -> bool:
            if value is None:
                return False
            if isinstance(value, str) and value.strip().upper() in ("N/A", "NONE", ""):
                return False
            return True

        # Process each section and its fields
        for section_title, fields in FIELD_MAPPING.items():
            section_summary_points = []
            for label, key_or_keys in fields.items():
                # Handle single key or tuple of fallback keys
                keys = (key_or_keys,) if isinstance(key_or_keys, str) else key_or_keys

                value = None
                for key in keys:
                    v = getattr(company_overview, key, None)
                    if is_valid(v):
                        value = v
                        break  # Found a valid value, stop checking fallbacks

                if is_valid(value):
                    formatted_value = safe_format_value(symbol, label, value)
                    section_summary_points.append(f"- {label}: {formatted_value}")
                    data_found = True

            if section_summary_points:
                summary_points[section_title] = "\n".join(section_summary_points)

        if not data_found:
            logger.warning(
                f"[{symbol}] {func_name}: No valid fundamental data points found in CompanyOverview object."
            )
            return "Nem található érvényes vállalati alapadat.", False

        # Assemble the final string from the sections
        final_summary = []
        for section_title, content in summary_points.items():
            final_summary.append(f"== {section_title} ==\n{content}")

        logger.debug(
            f"[{symbol}] {func_name}: Successfully formatted fundamental data."
        )
        return ".".join(final_summary), True

    except Exception as e:
        logger.error(
            f"[{symbol}] {func_name}: CRITICAL - Unexpected error: {e}", exc_info=True
        )
        return FALLBACK_FUNDAMENTAL_DATA, False
