# Aevorex_codes/modules/financehub/backend/core./prompt_formatters/earnings_formatter.py
from __future__ import annotations

from ....utils.logger_config import get_logger
from ....models.stock import EarningsData
from .constants import FALLBACK_EARNINGS_DATA
from ..helpers import safe_format_value

logger = get_logger(__name__)


async def format_earnings_data_for_prompt(
    symbol: str, earnings_data: EarningsData | None
) -> str:
    """
    Formats the EarningsData object into a structured string for the AI prompt.
    Handles potential errors gracefully and ALWAYS returns a string.
    """
    func_name = "format_earnings_data_for_prompt"
    logger.debug(f"[{symbol}] Running {func_name}..")
    if not earnings_data:
        logger.info(f"[{symbol}] {func_name}: Skipping, no EarningsData provided.")
        return "Vállalati eredmény-információk nem állnak rendelkezésre."

    try:
        summary_points = []
        data_found = False

        # 1. Format Earnings History (Quarterly)
        if earnings_data.history and not earnings_data.history.empty:
            history_points = []
            # Take the last 4 quarters for a TTM view
            for _, row in earnings_data.history.head(4).iterrows():
                report_date = safe_format_value(
                    symbol, "reportDate", row.get("reportDate")
                )
                eps_actual = safe_format_value(
                    symbol, "epsActual", row.get("epsActual")
                )
                eps_estimate = safe_format_value(
                    symbol, "epsEstimate", row.get("epsEstimate")
                )

                # Only include if we have some data
                if eps_actual != "N/A" or eps_estimate != "N/A":
                    history_points.append(
                        f"- Dátum: {report_date}, Jelentett EPS: {eps_actual}, Várt EPS: {eps_estimate}"
                    )

            if history_points:
                summary_points.append(
                    "== Elmúlt Negyedéves Jelentések (EPS) ==\n"
                    + "\n".join(history_points)
                )
                data_found = True

        # 2. Format Earnings Trend (Quarterly)
        if earnings_data.trend and not earnings_data.trend.empty:
            trend_points = []
            # Take the last 4 quarters
            for _, row in earnings_data.trend.head(4).iterrows():
                period = safe_format_value(symbol, "period", row.get("period"))
                revenue_estimate = safe_format_value(
                    symbol, "revenueEstimate", row.get("revenueEstimate"), ","
                )
                earnings_estimate = safe_format_value(
                    symbol, "earningsEstimate", row.get("earningsEstimate"), ","
                )

                if revenue_estimate != "N/A" or earnings_estimate != "N/A":
                    trend_points.append(
                        f"- Időszak: {period}, Várt árbevétel: {revenue_estimate}, Várt nyereség: {earnings_estimate}"
                    )

            if trend_points:
                summary_points.append(
                    "== Elemzői Várakozások (Negyedéves) ==\n" + "\n".join(trend_points)
                )
                data_found = True

        # 3. Format Annual Earnings Data
        if earnings_data.annual and not earnings_data.annual.empty:
            annual_points = []
            # Take the last 2 years
            for _, row in earnings_data.annual.head(2).iterrows():
                report_date = safe_format_value(
                    symbol, "reportDate", row.get("reportDate")
                )
                eps = safe_format_value(symbol, "eps", row.get("eps"))

                if eps != "N/A":
                    annual_points.append(
                        f"- Év (jelentés dátuma): {report_date}, Teljes éves EPS: {eps}"
                    )

            if annual_points:
                summary_points.append(
                    "== Éves Jelentések (EPS) ==\n" + "\n".join(annual_points)
                )
                data_found = True

        if not data_found:
            logger.warning(
                f"[{symbol}] {func_name}: No valid data points found in EarningsData object."
            )
            return "Nem található érvényes adat a vállalati eredményekről."

        final_summary = ".".join(summary_points)
        logger.debug(f"[{symbol}] {func_name}: Successfully formatted earnings data.")
        return final_summary

    except Exception as e:
        logger.error(
            f"[{symbol}] {func_name}: CRITICAL - Unexpected error: {e}", exc_info=True
        )
        return FALLBACK_EARNINGS_DATA
