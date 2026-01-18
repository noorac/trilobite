import logging
from datetime import date

from pandas import DataFrame
from trilobite.marketdata.yfclient import YFClient

logger = logging.getLogger(__name__)

class MarketService:
    def __init__(self, client: YFClient) -> None:
        self._client = client

    def get_ohlcv(self, ticker: str, start_date: date = date(1900, 1, 1)) -> DataFrame:
        """
        Calls the client and returns the data
        """
        ticker = ticker.strip().upper()
        if not ticker:
            logger.warning("get_ohlcv was called with empty ticker")
            raise ValueError("Ticker cannot be empty")

        if not ticker.replace(".", "").replace("-", "").isalnum():
            logger.warning(f"Invalid ticker format: {ticker}")
            raise ValueError(f"Invalid ticker format: {ticker}")

        return self._client.get_ohlcv(ticker, start_date = start_date)

