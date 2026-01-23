from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class TickerUpdate:
    """
    Contains data about updates
    """

class TickerService:
    """
    Keeps track of tickers
    """
    def __init__(self) -> None:
        pass

    def update_tickerlist(self, fresh_ticker_list: list[str]) -> None:
        """
        The list of actual active tickers on the stock market

        Params:
        - fresh_ticker_list: a list of strings where each string is a ticker
        """
        self._fresh_ticker_list = fresh_ticker_list
        return None

    def update_stored_tickers(self, stored_ticker_dict: dict) -> None:
        """
        Stores a dict of current tickers in the database

        Params:
        - stored_ticker_dict: the dict of currently stored tickers. With the key
        being the ticker, and the value being a date object of the last date 
        the ticker was updated
        """
        self._stored_ticker_dict = stored_ticker_dict
        return None
