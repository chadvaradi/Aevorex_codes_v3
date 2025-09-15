from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class FinancialStatementItem(BaseModel):
    date: str = Field(
        ..., description="The date of the financial data point (e.g., '2023-12-31')."
    )
    value: Optional[float] = Field(
        None, description="The value of the financial metric."
    )


class FinancialStatementData(BaseModel):
    quarterly: List[FinancialStatementItem] = Field(
        default_factory=list, description="List of quarterly data points."
    )
    annual: List[FinancialStatementItem] = Field(
        default_factory=list, description="List of annual data points."
    )

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "balance_sheet": {
                    "quarterly": [
                        {"date": "2023-09-30", "value": 1000},
                        {"date": "2023-06-30", "value": 950},
                    ],
                    "annual": [{"date": "2022-12-31", "value": 3800}],
                }
            }
        }


class FinancialStatementDataContainer(BaseModel):
    """A container for various financial statement data structures."""

    balance_sheet: Dict[str, FinancialStatementData] = Field(default_factory=dict)
    income_statement: Dict[str, FinancialStatementData] = Field(default_factory=dict)
    cash_flow: Dict[str, FinancialStatementData] = Field(default_factory=dict)
