from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class BaseFetcher(ABC):
    """
    Abstract base class for all data fetchers.
    """

    @abstractmethod
    async def fetch_ohlcv(self, ticker: str, **kwargs) -> Any:
        """
        Fetch OHLCV data for a given ticker.
        """
        raise NotImplementedError

    @abstractmethod
    async def fetch_quote(self, ticker: str, **kwargs) -> Any:
        """
        Fetch quote data for a given ticker.
        """
        raise NotImplementedError

    @abstractmethod
    async def fetch_fundamentals(self, ticker: str, **kwargs) -> Any:
        """
        Fetch fundamental data for a given ticker.
        """
        raise NotImplementedError

    @abstractmethod
    async def fetch_news(self, ticker: str, **kwargs) -> Any:
        """
        Fetch news for a given ticker.
        """
        raise NotImplementedError
