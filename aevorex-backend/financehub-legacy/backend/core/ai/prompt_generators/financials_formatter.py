from __future__ import annotations
import re
import pandas as pd
from typing import Any

from ....utils.logger_config import get_logger
from ....models.stock import FinancialsData
from .constants import FALLBACK_FINANCIALS_DATA
from ..helpers import safe_format_value

logger = get_logger(__name__)


async def format_financials_data_for_prompt(
    symbol: str, financials_data: FinancialsData | None
) -> str:
    """
    Formats the FinancialsData object into a structured string for the AI prompt.
    Handles potential errors gracefully and ALWAYS returns a string.
    """
    func_name = "format_financials_data_for_prompt"
    logger.debug(f"[{symbol}] Running {func_name}..")
    if not financials_data:
        logger.info(f"[{symbol}] {func_name}: Skipping, no FinancialsData provided.")
        return "Pénzügyi kimutatások adatai nem állnak rendelkezésre."

    try:
        summary_sections: dict[str, Any] = {}
        data_found = False

        # Mapping from FinancialsData fields to descriptive labels and section titles
        STATEMENT_MAPPING = {
            "Eredménykimutatás (fontosabb sorok)": financials_data.income_statement,
            "Mérleg (fontosabb sorok)": financials_data.balance_sheet,
            "Cash Flow (fontosabb sorok)": financials_data.cash_flow,
        }

        for section_title, statement_df in STATEMENT_MAPPING.items():
            if statement_df is None or statement_df.empty:
                continue

            section_points = []

            # Use the most recent year available
            if not statement_df.columns.empty:
                latest_year = statement_df.columns[0]
                logger.debug(
                    f"[{symbol}] {func_name}: Processing '{section_title}' for latest year '{latest_year}'."
                )

                # Take top N rows to keep it concise, assuming relevance by order
                for index, value in statement_df[latest_year].head(10).items():
                    # Check for non-null/non-zero values to make the summary meaningful
                    if pd.notna(value) and value != 0:
                        formatted_value = safe_format_value(
                            symbol, str(index), value, ","
                        )
                        # Clean up index name (e.g., "totalRevenue" -> "Total Revenue")
                        label = " ".join(
                            word.capitalize()
                            for word in re.sub(r"([A-Z])", r" \1", str(index)).split()
                        )
                        section_points.append(f"- {label}: {formatted_value}")
                        data_found = True

            if section_points:
                summary_sections[section_title] = "\n".join(section_points)

        if not data_found:
            logger.warning(
                f"[{symbol}] {func_name}: No valid data points found in any financial statement."
            )
            return "Nem található érvényes adat a pénzügyi kimutatásokban."

        # Assemble final summary string
        final_summary_parts = []
        for title, content in summary_sections.items():
            final_summary_parts.append(f"== {title} ==\n{content}")

        final_summary = ".".join(final_summary_parts)
        logger.debug(f"[{symbol}] {func_name}: Successfully formatted financial data.")
        return final_summary

    except Exception as e:
        logger.error(
            f"[{symbol}] {func_name}: CRITICAL - Unexpected error: {e}", exc_info=True
        )
        return FALLBACK_FINANCIALS_DATA
