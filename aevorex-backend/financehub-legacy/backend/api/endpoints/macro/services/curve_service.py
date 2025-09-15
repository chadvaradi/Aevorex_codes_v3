"""
Curve Service

Yield curve logic and calculations.
Handles yield curve data processing, analytics, and comparisons.
"""

from typing import Dict, Any, Optional, List
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class CurveService:
    """Service for yield curve logic and calculations."""

    def __init__(self):
        self.provider = "curve_service"

    async def calculate_spot_rates(self, curve_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate spot rates from yield curve data.
        Expects: curve_data = {'maturities': [...], 'yields': [...]}
        Returns: dict with normalized spot rates sorted by maturity.
        """
        logger.info("Calculating spot rates from curve data")
        maturities = curve_data.get("maturities")
        yields = curve_data.get("yields")
        if maturities is None or yields is None or len(maturities) != len(yields):
            logger.warning("Invalid curve data for spot rate calculation")
            return {"error": "Invalid curve data"}
        try:
            # Pair and sort by maturity
            pairs = sorted(zip(maturities, yields), key=lambda x: x[0])
            normalized = [{"maturity": float(m), "spot_rate": float(y)} for m, y in pairs]
            logger.info(f"Spot rates calculated for {len(normalized)} maturities")
            return {"spot_rates": normalized}
        except Exception as e:
            logger.error(f"Error in spot rate calculation: {e}")
            return {"error": "Exception during spot rate calculation"}

    async def calculate_forward_rates(self, curve_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate simple forward rates between consecutive maturities.
        Expects: curve_data = {'maturities': [...], 'yields': [...]}
        Returns: dict with forward rates.
        """
        logger.info("Calculating forward rates from curve data")
        maturities = curve_data.get("maturities")
        yields = curve_data.get("yields")
        if maturities is None or yields is None or len(maturities) != len(yields):
            logger.warning("Invalid curve data for forward rate calculation")
            return {"error": "Invalid curve data"}
        try:
            pairs = sorted(zip(maturities, yields), key=lambda x: x[0])
            forward_rates = []
            for i in range(len(pairs) - 1):
                m1, y1 = float(pairs[i][0]), float(pairs[i][1])
                m2, y2 = float(pairs[i+1][0]), float(pairs[i+1][1])
                if m2 == m1:
                    logger.warning(f"Duplicate maturity {m1} encountered in forward rate calculation")
                    continue
                # Simple forward rate approximation (not compounding)
                forward_rate = (y2 * m2 - y1 * m1) / (m2 - m1)
                forward_rates.append({
                    "start_maturity": m1,
                    "end_maturity": m2,
                    "forward_rate": forward_rate
                })
            logger.info(f"Forward rates calculated for {len(forward_rates)} intervals")
            return {"forward_rates": forward_rates}
        except Exception as e:
            logger.error(f"Error in forward rate calculation: {e}")
            return {"error": "Exception during forward rate calculation"}

    async def compare_curves(self, curve1: Dict[str, Any], curve2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two yield curves for shared maturities.
        Returns maturity, yield1, yield2, and difference for each shared maturity.
        """
        logger.info("Comparing two yield curves")
        m1 = curve1.get("maturities")
        y1 = curve1.get("yields")
        m2 = curve2.get("maturities")
        y2 = curve2.get("yields")
        if not (m1 and y1 and m2 and y2):
            logger.warning("Missing maturities or yields in one or both curves")
            return {"error": "Invalid curve input"}
        try:
            curve1_dict = {float(m): float(y) for m, y in zip(m1, y1)}
            curve2_dict = {float(m): float(y) for m, y in zip(m2, y2)}
            shared_maturities = sorted(set(curve1_dict.keys()) & set(curve2_dict.keys()))
            comparison = []
            for m in shared_maturities:
                v1 = curve1_dict[m]
                v2 = curve2_dict[m]
                comparison.append({
                    "maturity": m,
                    "yield1": v1,
                    "yield2": v2,
                    "difference": v2 - v1
                })
            logger.info(f"Compared curves at {len(comparison)} shared maturities")
            return {"comparison": comparison}
        except Exception as e:
            logger.error(f"Error comparing yield curves: {e}")
            return {"error": "Exception during curve comparison"}

    async def get_curve_analytics(self, curve_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute slope, average, max, min, and curvature of the yield curve.
        Slope: 10Y - 2Y. Curvature: 10Y + 2Y - 2*5Y.
        """
        logger.info("Calculating curve analytics")
        maturities = curve_data.get("maturities")
        yields = curve_data.get("yields")
        if maturities is None or yields is None or len(maturities) != len(yields):
            logger.warning("Invalid curve data for analytics")
            return {"error": "Invalid curve data"}
        try:
            m_dict = {float(m): float(y) for m, y in zip(maturities, yields)}
            y_values = list(m_dict.values())
            analytics = {
                "average_yield": sum(y_values) / len(y_values) if y_values else None,
                "max_yield": max(y_values) if y_values else None,
                "min_yield": min(y_values) if y_values else None
            }
            # Slope (10Y - 2Y)
            slope = None
            curvature = None
            m_2 = min(m_dict.keys(), key=lambda x: abs(x - 2.0)) if m_dict else None
            m_5 = min(m_dict.keys(), key=lambda x: abs(x - 5.0)) if m_dict else None
            m_10 = min(m_dict.keys(), key=lambda x: abs(x - 10.0)) if m_dict else None
            if m_2 is not None and m_10 is not None:
                slope = m_dict[m_10] - m_dict[m_2]
            if m_2 is not None and m_5 is not None and m_10 is not None:
                curvature = m_dict[m_10] + m_dict[m_2] - 2 * m_dict[m_5]
            analytics["slope_10y_2y"] = slope
            analytics["curvature_10y_5y_2y"] = curvature
            logger.info(f"Curve analytics calculated: {analytics}")
            return analytics
        except Exception as e:
            logger.error(f"Error in curve analytics calculation: {e}")
            return {"error": "Exception during analytics calculation"}


__all__ = ["CurveService"]
