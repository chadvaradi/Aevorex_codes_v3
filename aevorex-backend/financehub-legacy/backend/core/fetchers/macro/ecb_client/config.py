"""
ECB Configuration and Series Keys
=================================

Central configuration for all ECB SDMX dataflows and series keys.
This is the single source of truth for ECB data configuration.
"""

from typing import Dict, List, Tuple

# -----------------------
# ✅ Infláció (HICP)
# -----------------------
KEY_ECB_HICP_OVERALL = "M.U2.N.000000.4.ANR"  # ECB, monthly, headline HICP - Overall index
KEY_ECB_HICP_CORE = "M.U2.N.XEF000.4.ANR"  # ECB, monthly, core HICP - Excluding energy and food
KEY_ECB_HICP_ENERGY = "M.U2.N.072000.4.ANR"  # ECB, monthly, HICP - Energy component
KEY_ECB_HICP_TOTAL = KEY_ECB_HICP_OVERALL  # Alias for HICP Total

# -----------------------
# ✅ GDP (Forecast - SPF)
# -----------------------
KEY_ECB_GDP_FORECAST = "SPF.Q.U2.RGDP.POINT.LT.Q.AVG"  # ECB, quarterly, real GDP growth forecast (Survey of Professional Forecasters, long-term average)

# -----------------------
# ✅ Munkanélküliség
# -----------------------
KEY_ECB_UNEMPLOYMENT = "LFSI.M.I9.S.UNEHRT.TOTAL0.15_74.T"  # Eurostat, monthly, unemployment rate, Euro area (Labour Force Survey)

# -----------------------
# ✅ Kötvényhozamok (Yield Curve)
# -----------------------
KEY_ECB_YIELD_3M = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_3M"  # ECB, daily, 3-month government bond yield
KEY_ECB_YIELD_6M = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_6M"  # ECB, daily, 6-month government bond yield
KEY_ECB_YIELD_9M = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_9M"  # ECB, daily, 9-month government bond yield
KEY_ECB_YIELD_1Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_1Y"  # ECB, daily, 1-year government bond yield
KEY_ECB_YIELD_2Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y"  # ECB, daily, 2-year government bond yield
KEY_ECB_YIELD_3Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_3Y"  # ECB, daily, 3-year government bond yield
KEY_ECB_YIELD_4Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_4Y"  # ECB, daily, 4-year government bond yield
KEY_ECB_YIELD_5Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_5Y"  # ECB, daily, 5-year government bond yield
KEY_ECB_YIELD_6Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_6Y"  # ECB, daily, 6-year government bond yield
KEY_ECB_YIELD_7Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_7Y"  # ECB, daily, 7-year government bond yield
KEY_ECB_YIELD_8Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_8Y"  # ECB, daily, 8-year government bond yield
KEY_ECB_YIELD_9Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_9Y"  # ECB, daily, 9-year government bond yield
KEY_ECB_YIELD_10Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y"  # ECB, daily, 10-year government bond yield
KEY_ECB_YIELD_11Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_11Y"  # ECB, daily, 11-year government bond yield
KEY_ECB_YIELD_12Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_12Y"  # ECB, daily, 12-year government bond yield
KEY_ECB_YIELD_13Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_13Y"  # ECB, daily, 13-year government bond yield
KEY_ECB_YIELD_14Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_14Y"  # ECB, daily, 14-year government bond yield
KEY_ECB_YIELD_15Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_15Y"  # ECB, daily, 15-year government bond yield
KEY_ECB_YIELD_16Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_16Y"  # ECB, daily, 16-year government bond yield
KEY_ECB_YIELD_17Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_17Y"  # ECB, daily, 17-year government bond yield
KEY_ECB_YIELD_18Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_18Y"  # ECB, daily, 18-year government bond yield
KEY_ECB_YIELD_19Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_19Y"  # ECB, daily, 19-year government bond yield
KEY_ECB_YIELD_20Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_20Y"  # ECB, daily, 20-year government bond yield
KEY_ECB_YIELD_21Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_21Y"  # ECB, daily, 21-year government bond yield
KEY_ECB_YIELD_22Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_22Y"  # ECB, daily, 22-year government bond yield
KEY_ECB_YIELD_23Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_23Y"  # ECB, daily, 23-year government bond yield
KEY_ECB_YIELD_24Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_24Y"  # ECB, daily, 24-year government bond yield
KEY_ECB_YIELD_25Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_25Y"  # ECB, daily, 25-year government bond yield
KEY_ECB_YIELD_26Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_26Y"  # ECB, daily, 26-year government bond yield
KEY_ECB_YIELD_27Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_27Y"  # ECB, daily, 27-year government bond yield
KEY_ECB_YIELD_28Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_28Y"  # ECB, daily, 28-year government bond yield
KEY_ECB_YIELD_29Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_29Y"  # ECB, daily, 29-year government bond yield
KEY_ECB_YIELD_30Y = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_30Y"  # ECB, daily, 30-year government bond yield

# Yield Curve Maturity Mapping for ECB Client
KEY_ECB_YIELD_CURVE_MATURITIES = {
    "3M": KEY_ECB_YIELD_3M,
    "6M": KEY_ECB_YIELD_6M,
    "9M": KEY_ECB_YIELD_9M,
    "1Y": KEY_ECB_YIELD_1Y,
    "2Y": KEY_ECB_YIELD_2Y,
    "3Y": KEY_ECB_YIELD_3Y,
    "4Y": KEY_ECB_YIELD_4Y,
    "5Y": KEY_ECB_YIELD_5Y,
    "6Y": KEY_ECB_YIELD_6Y,
    "7Y": KEY_ECB_YIELD_7Y,
    "8Y": KEY_ECB_YIELD_8Y,
    "9Y": KEY_ECB_YIELD_9Y,
    "10Y": KEY_ECB_YIELD_10Y,
    "11Y": KEY_ECB_YIELD_11Y,
    "12Y": KEY_ECB_YIELD_12Y,
    "13Y": KEY_ECB_YIELD_13Y,
    "14Y": KEY_ECB_YIELD_14Y,
    "15Y": KEY_ECB_YIELD_15Y,
    "16Y": KEY_ECB_YIELD_16Y,
    "17Y": KEY_ECB_YIELD_17Y,
    "18Y": KEY_ECB_YIELD_18Y,
    "19Y": KEY_ECB_YIELD_19Y,
    "20Y": KEY_ECB_YIELD_20Y,
    "21Y": KEY_ECB_YIELD_21Y,
    "22Y": KEY_ECB_YIELD_22Y,
    "23Y": KEY_ECB_YIELD_23Y,
    "24Y": KEY_ECB_YIELD_24Y,
    "25Y": KEY_ECB_YIELD_25Y,
    "26Y": KEY_ECB_YIELD_26Y,
    "27Y": KEY_ECB_YIELD_27Y,
    "28Y": KEY_ECB_YIELD_28Y,
    "29Y": KEY_ECB_YIELD_29Y,
    "30Y": KEY_ECB_YIELD_30Y,
}

# -----------------------
# ✅ Kamatlábak (Policy Rates)
# -----------------------
KEY_ECB_POLICY_RATE = "FM.B.U2.EUR.4F.KR.MRR_FR.LEV"  # ECB, daily, main refinancing operations rate (MRO, fixed rate tenders)

# -----------------------
# Bank Lending Survey (BLS)
# -----------------------
# ECB, quarterly, credit standards for loans to enterprises
KEY_ECB_BLS_CREDIT_STANDARDS = "BLS.Q.U2.BN.A.CS.E"  

# -----------------------
# Consolidated Banking Data (CBD)
# -----------------------
# ECB, quarterly, Tier 1 capital ratio
KEY_ECB_CBD_TIER1_RATIO = "CBD.Q.U2.BN.A.T1R"  
# ECB, quarterly, Non-performing loans ratio
KEY_ECB_CBD_NPL_RATIO = "CBD.Q.U2.BN.A.NPLR"  

# -----------------------
# Composite Indicator of Systemic Stress (CISS)
# -----------------------
# ECB, daily, composite indicator of systemic stress
KEY_ECB_CISS_INDEX = "CISS.D.U2.EUR"  

# -----------------------
# Retail Payment Statistics (RPP)
# -----------------------
# ECB, annual, number of card payments
KEY_ECB_RPP_CARD_PAYMENTS = "RPP.A.U2.EUR.CARD.PAY"  
# ECB, annual, number of credit transfers
KEY_ECB_RPP_CREDIT_TRANSFERS = "RPP.A.U2.EUR.CREDIT.TRANSFERS"  

# -----------------------
# Trade Statistics (TRD)
# -----------------------
# ECB, monthly, exports of goods and services
KEY_ECB_TRD_EXPORTS = "TRD.M.U2.EUR.EXPORTS"  
# ECB, monthly, imports of goods and services
KEY_ECB_TRD_IMPORTS = "TRD.M.U2.EUR.IMPORTS"  

# -----------------------
# Interest Rate Statistics (IRS)
# -----------------------
# ECB, monthly, deposit interest rates
KEY_ECB_IRS_DEPOSIT_RATES = "IRS.M.U2.EUR.DEPOSIT.RATE"  
# ECB, monthly, lending interest rates
KEY_ECB_IRS_LENDING_RATES = "IRS.M.U2.EUR.LENDING.RATE"  

# -----------------------
# Money Market Statistics (MIR)
# -----------------------
# ECB, daily, overnight money market rate
KEY_ECB_MIR_OVERNIGHT_RATE = "MIR.D.U2.EUR.OVERNIGHT"  
# ECB, daily, 3-month money market rate
KEY_ECB_MIR_3M_RATE = "MIR.D.U2.EUR.3M"  

# -----------------------
# Investment Fund Statistics (IVF)
# -----------------------
# ECB, monthly, total assets of investment funds
KEY_ECB_IVF_TOTAL_ASSETS = "IVF.M.U2.EUR.TOTAL.ASSETS"  
# ECB, monthly, net sales of investment funds
KEY_ECB_IVF_NET_SALES = "IVF.M.U2.EUR.NET.SALES"  

# -----------------------
# Survey of Professional Forecasters (SPF)
# -----------------------
# ECB, quarterly, inflation forecast
KEY_ECB_SPF_INFLATION_FORECAST = "SPF.Q.U2.INFLATION.POINT.LT.Q.AVG"  

# -----------------------
# Payment System Statistics (PSS)
# -----------------------
# ECB, monthly, payment system volume
KEY_ECB_PSS_VOLUME = "PSS.M.U2.EUR.VOLUME"  
# ECB, monthly, payment system value
KEY_ECB_PSS_VALUE = "PSS.M.U2.EUR.VALUE"  

# -----------------------
# Central Bank Operations (CPP)
# -----------------------
# ECB, daily, open market operations
KEY_ECB_CPP_OMO = "CPP.D.U2.EUR.OMO"  
# ECB, daily, standing facilities
KEY_ECB_CPP_STANDING_FACILITIES = "CPP.D.U2.EUR.STANDING.FACILITIES"  

# -----------------------
# Securities Statistics (SEC)
# -----------------------
# ECB, monthly, securities issued
KEY_ECB_SEC_ISSUED = "SEC.M.U2.EUR.ISSUED"  
# ECB, monthly, securities held
KEY_ECB_SEC_HELD = "SEC.M.U2.EUR.HELD"  

# -----------------------
# Business Statistics (BSI)
# -----------------------
# Eurostat, monthly, business confidence indicator  # TODO: manual check needed
KEY_ECB_BSI_BUSINESS_CONFIDENCE = "BSI.M.U2.EUR.BUSINESS.CONFIDENCE"  
# Eurostat, monthly, industrial production index  # TODO: manual check needed
KEY_ECB_BSI_INDUSTRIAL_PRODUCTION = "BSI.M.U2.EUR.INDUSTRIAL.PRODUCTION"  

# -----------------------
# Euro Short-Term Rate (ESTR)
# -----------------------
# ECB, daily, euro short-term rate
KEY_ECB_ESTR_RATE = "ESTR.D.U2.EUR"  

# -----------------------
# ✅ Short-term Statistics (STS)
# -----------------------
# Eurostat, quarterly, capacity utilization in manufacturing
KEY_ECB_STS_CAPACITY_UTILIZATION = "STS.Q.U2.S.MAN.CU.U.S"

# -----------------------
# ✅ Monetary Aggregates
# -----------------------
# ECB, monthly, monetary aggregates (non-seasonally adjusted)
KEY_ECB_MONETARY_M1 = "BSI.M.U2.N.A.T00.A.1.Z5.0000.Z01.E"
KEY_ECB_MONETARY_M2 = "BSI.M.U2.N.A.T00.A.2.Z5.0000.Z01.E"
KEY_ECB_MONETARY_M3 = "BSI.M.U2.N.A.T00.A.3.Z5.0000.Z01.E"

# -----------------------
# ✅ FX Rates (EXR Dataflow)
# -----------------------
# ECB, daily, reference exchange rates
KEY_ECB_FX_EUR_USD = "EXR.D.USD.EUR.SP00.A"
KEY_ECB_FX_EUR_JPY = "EXR.D.JPY.EUR.SP00.A"
KEY_ECB_FX_EUR_GBP = "EXR.D.GBP.EUR.SP00.A"
KEY_ECB_FX_EUR_CHF = "EXR.D.CHF.EUR.SP00.A"
KEY_ECB_FX_EUR_CNY = "EXR.D.CNY.EUR.SP00.A"

# -----------------------
# ECB HTTP Client Configuration
# -----------------------
ECB_BASE_URL = "https://sdw-wsrest.ecb.europa.eu/service/data"
ECB_REQUEST_HEADERS = {
    "Accept": "application/vnd.sdmx.data+json;version=1.0.0",
    "User-Agent": "FinanceHub-ECB-Client/1.0"
}
ECB_TIMEOUT = 30.0
ECB_RETRY_ATTEMPTS = 3

# -----------------------
# Comprehensive ECB Series Configuration
# -----------------------
COMPREHENSIVE_ECB_SERIES = {
    "monetary_aggregates": [
        ("M1", KEY_ECB_MONETARY_M1),
        ("M2", KEY_ECB_MONETARY_M2),
        ("M3", KEY_ECB_MONETARY_M3),
    ],
    "inflation": [
        ("HICP_Overall", KEY_ECB_HICP_OVERALL),
        ("HICP_Core", KEY_ECB_HICP_CORE),
        ("HICP_Energy", KEY_ECB_HICP_ENERGY),
    ],
    "retail_rates": [
        ("Deposit_Rates", KEY_ECB_IRS_DEPOSIT_RATES),
        ("Lending_Rates", KEY_ECB_IRS_LENDING_RATES),
    ],
}

# -----------------------
# ECB Dataflows Configuration
# -----------------------
ECB_DATAFLOWS: Dict[str, Dict[str, any]] = {
    # Bank Lending Survey
    "bls": {
        "dataflow": "BLS",
        "series": [
            ("Credit_Standards", KEY_ECB_BLS_CREDIT_STANDARDS),
        ],
        "metadata": {
            "description": "ECB Bank Lending Survey - Credit Standards",
            "frequency": "quarterly",
            "source": "ECB SDMX",
        },
    },
    # Consolidated Banking Data
    "cbd": {
        "dataflow": "CBD",
        "series": [
            ("Tier1_Ratio", KEY_ECB_CBD_TIER1_RATIO),
            ("NPL_Ratio", KEY_ECB_CBD_NPL_RATIO),
        ],
        "metadata": {
            "description": "ECB Consolidated Banking Data - Capital Ratios",
            "frequency": "quarterly",
            "source": "ECB SDMX",
        },
    },
    # Composite Indicator of Systemic Stress
    "ciss": {
        "dataflow": "CISS",
        "series": [
            ("CISS_Index", KEY_ECB_CISS_INDEX),
        ],
        "metadata": {
            "description": "ECB Composite Indicator of Systemic Stress",
            "frequency": "daily",
            "source": "ECB SDMX",
        },
    },
    # Harmonised Index of Consumer Prices
    "hicp": {
        "dataflow": "ICP",
        "series": [
            ("HICP_Total", KEY_ECB_HICP_TOTAL),
            ("HICP_Core", KEY_ECB_HICP_CORE),
            ("HICP_Energy", KEY_ECB_HICP_ENERGY),
        ],
        "metadata": {
            "description": "ECB Harmonised Index of Consumer Prices",
            "frequency": "monthly",
            "source": "ECB SDMX",
        },
    },
    # Retail Payment Statistics
    "rpp": {
        "dataflow": "RPP",
        "series": [
            ("Card_Payments", KEY_ECB_RPP_CARD_PAYMENTS),
            ("Credit_Transfers", KEY_ECB_RPP_CREDIT_TRANSFERS),
        ],
        "metadata": {
            "description": "ECB Retail Payment Statistics",
            "frequency": "annual",
            "source": "ECB SDMX",
        },
    },
    # Trade Statistics
    "trd": {
        "dataflow": "TRD",
        "series": [
            ("Exports", KEY_ECB_TRD_EXPORTS),
            ("Imports", KEY_ECB_TRD_IMPORTS),
        ],
        "metadata": {
            "description": "ECB Trade Statistics",
            "frequency": "monthly",
            "source": "ECB SDMX",
        },
    },
    # Interest Rate Statistics
    "irs": {
        "dataflow": "IRS",
        "series": [
            ("Deposit_Rates", KEY_ECB_IRS_DEPOSIT_RATES),
            ("Lending_Rates", KEY_ECB_IRS_LENDING_RATES),
        ],
        "metadata": {
            "description": "ECB Interest Rate Statistics",
            "frequency": "monthly",
            "source": "ECB SDMX",
        },
    },
    # Money Market Statistics
    "mir": {
        "dataflow": "MIR",
        "series": [
            ("Overnight_Rate", KEY_ECB_MIR_OVERNIGHT_RATE),
            ("3M_Rate", KEY_ECB_MIR_3M_RATE),
        ],
        "metadata": {
            "description": "ECB Money Market Statistics",
            "frequency": "daily",
            "source": "ECB SDMX",
        },
    },
    # Investment Fund Statistics
    "ivf": {
        "dataflow": "IVF",
        "series": [
            ("Total_Assets", KEY_ECB_IVF_TOTAL_ASSETS),
            ("Net_Sales", KEY_ECB_IVF_NET_SALES),
        ],
        "metadata": {
            "description": "ECB Investment Fund Statistics",
            "frequency": "monthly",
            "source": "ECB SDMX",
        },
    },
    # Survey of Professional Forecasters
    "spf": {
        "dataflow": "SPF",
        "series": [
            ("GDP_Forecast", KEY_ECB_GDP_FORECAST),
            ("Inflation_Forecast", KEY_ECB_SPF_INFLATION_FORECAST),
        ],
        "metadata": {
            "description": "ECB Survey of Professional Forecasters",
            "frequency": "quarterly",
            "source": "ECB SDMX",
        },
    },
    # Payment System Statistics
    "pss": {
        "dataflow": "PSS",
        "series": [
            ("Volume", KEY_ECB_PSS_VOLUME),
            ("Value", KEY_ECB_PSS_VALUE),
        ],
        "metadata": {
            "description": "ECB Payment System Statistics",
            "frequency": "monthly",
            "source": "ECB SDMX",
        },
    },
    # Central Bank Operations
    "cpp": {
        "dataflow": "CPP",
        "series": [
            ("Open_Market_Operations", KEY_ECB_CPP_OMO),
            ("Standing_Facilities", KEY_ECB_CPP_STANDING_FACILITIES),
        ],
        "metadata": {
            "description": "ECB Central Bank Operations",
            "frequency": "daily",
            "source": "ECB SDMX",
        },
    },
    # Securities Statistics
    "sec": {
        "dataflow": "SEC",
        "series": [
            ("Securities_Issued", KEY_ECB_SEC_ISSUED),
            ("Securities_Held", KEY_ECB_SEC_HELD),
        ],
        "metadata": {
            "description": "ECB Securities Statistics",
            "frequency": "monthly",
            "source": "ECB SDMX",
        },
    },
    # Financial Markets
    "fm": {
        "dataflow": "FM",
        "series": [
            ("Policy_Rate", KEY_ECB_POLICY_RATE),
            ("Yield_1Y", KEY_ECB_YIELD_1Y),
            ("Yield_10Y", KEY_ECB_YIELD_10Y),
        ],
        "metadata": {
            "description": "ECB Financial Markets",
            "frequency": "daily",
            "source": "ECB SDMX",
        },
    },
    # Yield Curve
    "yield": {
        "dataflow": "YC",
        "series": [
            ("3M", KEY_ECB_YIELD_3M),
            ("6M", KEY_ECB_YIELD_6M),
            ("9M", KEY_ECB_YIELD_9M),
            ("1Y", KEY_ECB_YIELD_1Y),
            ("2Y", KEY_ECB_YIELD_2Y),
            ("3Y", KEY_ECB_YIELD_3Y),
            ("4Y", KEY_ECB_YIELD_4Y),
            ("5Y", KEY_ECB_YIELD_5Y),
            ("6Y", KEY_ECB_YIELD_6Y),
            ("7Y", KEY_ECB_YIELD_7Y),
            ("8Y", KEY_ECB_YIELD_8Y),
            ("9Y", KEY_ECB_YIELD_9Y),
            ("10Y", KEY_ECB_YIELD_10Y),
            ("11Y", KEY_ECB_YIELD_11Y),
            ("12Y", KEY_ECB_YIELD_12Y),
            ("13Y", KEY_ECB_YIELD_13Y),
            ("14Y", KEY_ECB_YIELD_14Y),
            ("15Y", KEY_ECB_YIELD_15Y),
            ("16Y", KEY_ECB_YIELD_16Y),
            ("17Y", KEY_ECB_YIELD_17Y),
            ("18Y", KEY_ECB_YIELD_18Y),
            ("19Y", KEY_ECB_YIELD_19Y),
            ("20Y", KEY_ECB_YIELD_20Y),
            ("21Y", KEY_ECB_YIELD_21Y),
            ("22Y", KEY_ECB_YIELD_22Y),
            ("23Y", KEY_ECB_YIELD_23Y),
            ("24Y", KEY_ECB_YIELD_24Y),
            ("25Y", KEY_ECB_YIELD_25Y),
            ("26Y", KEY_ECB_YIELD_26Y),
            ("27Y", KEY_ECB_YIELD_27Y),
            ("28Y", KEY_ECB_YIELD_28Y),
            ("29Y", KEY_ECB_YIELD_29Y),
            ("30Y", KEY_ECB_YIELD_30Y),
        ],
        "metadata": {
            "description": "ECB Euro Area Yield Curves",
            "frequency": "daily",
            "source": "ECB SDMX",
        },
    },
    # Business Statistics
    "bsi": {
        "dataflow": "BSI",
        "series": [
            ("Business_Confidence", KEY_ECB_BSI_BUSINESS_CONFIDENCE),
            ("Industrial_Production", KEY_ECB_BSI_INDUSTRIAL_PRODUCTION),
        ],
        "metadata": {
            "description": "ECB Business Statistics",
            "frequency": "monthly",
            "source": "Eurostat",  # TODO: manual check needed
        },
    },
    # ESTR (Euro Short-Term Rate)
    "estr": {
        "dataflow": "ESTR",
        "series": [
            ("ESTR_Rate", KEY_ECB_ESTR_RATE),
        ],
        "metadata": {
            "description": "ECB Euro Short-Term Rate",
            "frequency": "daily",
            "source": "ECB SDMX",
        },
    },
    # Short-term Statistics
    "sts": {
        "dataflow": "STS",
        "series": [
            ("Capacity_Utilization", KEY_ECB_STS_CAPACITY_UTILIZATION),
        ],
        "metadata": {
            "description": "Eurostat Short-term Statistics - Capacity Utilization in Manufacturing",
            "frequency": "quarterly",
            "source": "Eurostat",
        },
    },
    # Monetary Aggregates
    "monetary": {
        "dataflow": "BSI",
        "series": [
            ("M1", KEY_ECB_MONETARY_M1),
            ("M2", KEY_ECB_MONETARY_M2),
            ("M3", KEY_ECB_MONETARY_M3),
        ],
        "metadata": {
            "description": "ECB Monetary Aggregates (M1, M2, M3)",
            "frequency": "monthly",
            "source": "ECB SDMX",
        },
    },
    # Foreign Exchange Rates
    "fx": {
        "dataflow": "EXR",
        "series": [
            ("EUR_USD", KEY_ECB_FX_EUR_USD),
            ("EUR_JPY", KEY_ECB_FX_EUR_JPY),
            ("EUR_GBP", KEY_ECB_FX_EUR_GBP),
            ("EUR_CHF", KEY_ECB_FX_EUR_CHF),
            ("EUR_CNY", KEY_ECB_FX_EUR_CNY),
        ],
        "metadata": {
            "description": "ECB Reference Exchange Rates",
            "frequency": "daily",
            "source": "ECB SDMX",
        },
    },
}


# Helper functions
def get_dataflow_config(flow_name: str) -> Dict[str, any] | None:
    """Get configuration for a specific ECB dataflow."""
    return ECB_DATAFLOWS.get(flow_name)


def list_dataflows() -> List[str]:
    """List all available ECB dataflow names."""
    return list(ECB_DATAFLOWS.keys())


def get_series_for_dataflow(flow_name: str) -> List[Tuple[str, str]]:
    """Get series configuration for a specific dataflow."""
    config = get_dataflow_config(flow_name)
    if config:
        return config.get("series", [])
    return []
