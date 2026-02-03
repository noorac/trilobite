import logging
from datetime import date

from pandas import DataFrame
from trilobite.marketdata.yfclient import YFClient

logger = logging.getLogger(__name__)

class MarketService:
    """
    Service wrapper for the market data retrieval.

    Params:
    - client: A concrete client implementation that knnows how to fetch OHLCV 
    data, e.g YFClient
    """
    def __init__(self, client: YFClient) -> None:
        self._client = client

    def get_ohlcv(self, ticker: str, start_date: date = date(1900, 1, 1)) -> DataFrame:
        """
        Normalizes and validates the ticker, then delegates the fetch of 
        OHLCV to the client.

        Params:
        - ticker: the instrument ticker symbol, e.g. "AAPL", "GOOGL"
        - start_date: first day(inclusive) to request from the data provider.
        Defaults to 1900-1-1 ( intended to go as far back as possible)

        Returns:
        - pandas.DataFrame containing the OHLCV data
        """
        logger.debug("Start ..")
        ticker = ticker.strip().upper()
        if not ticker:
            logger.warning("get_ohlcv was called with empty ticker")
            raise ValueError("Ticker cannot be empty")

        if not ticker.replace(".", "").replace("-", "").isalnum():
            logger.warning(f"Invalid ticker format: {ticker}")
            raise ValueError(f"Invalid ticker format: {ticker}")

        logger.debug("End ..")
        return self._client.get_ohlcv(ticker, start_date = start_date)

