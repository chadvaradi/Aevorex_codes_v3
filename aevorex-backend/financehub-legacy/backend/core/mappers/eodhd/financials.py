from __future__ import annotations
from typing import Optional, Any, TYPE_CHECKING, Dict
from backend.core.mappers._mapper_base import logger
from backend.models.stock import FinancialStatementDataContainer

if TYPE_CHECKING:
    from ....models import FinancialStatementDataContainer


def map_eodhd_fundamentals_to_financials_data(
    eodhd_data: Dict[str, Any],
) -> FinancialStatementDataContainer:
    income_statement = {}
    balance_sheet = {}
    cash_flow = {}
    valuation = {}

    try:
        # Income Statement
        income_statement["revenue"] = _safe_get_float(
            eodhd_data, "Revenue", "income_statement"
        )
        income_statement["cost_of_revenue"] = _safe_get_float(
            eodhd_data, "CostOfRevenue", "income_statement"
        )
        income_statement["gross_profit"] = _safe_get_float(
            eodhd_data, "GrossProfit", "income_statement"
        )
        income_statement["operating_income"] = _safe_get_float(
            eodhd_data, "OperatingIncome", "income_statement"
        )
        income_statement["net_income"] = _safe_get_float(
            eodhd_data, "NetIncome", "income_statement"
        )
        income_statement["ebitda"] = _safe_get_float(
            eodhd_data, "EBITDA", "income_statement"
        )

        # Balance Sheet
        balance_sheet["total_assets"] = _safe_get_float(
            eodhd_data, "TotalAssets", "balance_sheet"
        )
        balance_sheet["total_liabilities_net_minority_interest"] = _safe_get_float(
            eodhd_data, "TotalLiabilitiesNetMinorityInterest", "balance_sheet"
        )
        balance_sheet["ordinary_shares_number"] = _safe_get_float(
            eodhd_data, "OrdinarySharesNumber", "balance_sheet"
        )
        balance_sheet["cash_and_cash_equivalents"] = _safe_get_float(
            eodhd_data, "CashAndCashEquivalents", "balance_sheet"
        )
        balance_sheet["receivables"] = _safe_get_float(
            eodhd_data, "Receivables", "balance_sheet"
        )
        balance_sheet["payables"] = _safe_get_float(
            eodhd_data, "Payables", "balance_sheet"
        )
        balance_sheet["long_term_debt"] = _safe_get_float(
            eodhd_data, "LongTermDebt", "balance_sheet"
        )

        # Cash Flow
        cash_flow["operating_cash_flow"] = _safe_get_float(
            eodhd_data, "OperatingCashFlow", "cash_flow"
        )
        cash_flow["investing_cash_flow"] = _safe_get_float(
            eodhd_data, "InvestingCashFlow", "cash_flow"
        )
        cash_flow["financing_cash_flow"] = _safe_get_float(
            eodhd_data, "FinancingCashFlow", "cash_flow"
        )
        cash_flow["free_cash_flow"] = _safe_get_float(
            eodhd_data, "FreeCashFlow", "cash_flow"
        )

        # Valuation
        valuation["eps"] = _safe_get_float(eodhd_data, "EPS", "valuation")
        valuation["pe_ratio"] = _safe_get_float(eodhd_data, "PERatio", "valuation")
        valuation["price_to_book_ratio"] = _safe_get_float(
            eodhd_data, "PriceToBookRatio", "valuation"
        )
        valuation["dividend_yield"] = _safe_get_float(
            eodhd_data, "DividendYield", "valuation"
        )

    except Exception as e:
        logger.error(f"Unexpected error while mapping EODHD fundamentals: {e}")

    return FinancialStatementDataContainer(
        income_statement=income_statement,
        balance_sheet=balance_sheet,
        cash_flow=cash_flow,
        valuation=valuation,
    )


def _safe_get_float(data: Dict[str, Any], key: str, section: str) -> Optional[float]:
    value = data.get(key)
    if value is None:
        logger.warning(f"Missing key '{key}' in section '{section}'")
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning(
            f"Invalid type for key '{key}' in section '{section}': expected float-convertible, got {type(value).__name__}"
        )
        return None
