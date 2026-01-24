from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from datetime import date

@dataclass(frozen=True)
class TickerUpdate:
    """
    Contains data about updates
    """

class TickerRepo(Protocol):
    """
    Protocol that allows for insertion of the last_ohlcv_date_by_ticker method
    into TickerService
    """
    def last_ohlcv_date_by_ticker(self) -> dict[str, date | None]:
        ...

class TickerService:
    """
    Keeps track of tickers
    """
    def __init__(self, repo: TickerRepo, tickerclient: TickerClient) -> None:
        self._ticker_list = []
        self._ticker_dict = {}

    def update_ticker_list(self, fresh_ticker_list: list[str]) -> None:
        """
        The list of actual active tickers on the stock market

        Params:
        - fresh_ticker_list: a list of strings where each string is a ticker
        """
        self._ticker_list = fresh_ticker_list
        return None

    def update_stored_tickers(self, stored_ticker_dict: dict) -> None:
        """
        Stores a dict of current tickers in the database

        Params:
        - stored_ticker_dict: the dict of currently stored tickers. With the key
        being the ticker, and the value being a date object of the last date 
        the ticker was updated
        """
        self._ticker_dict = stored_ticker_dict
        return None

    def populate_ticker_dict_with_fresh_tickers(self) -> None:
        """
        Incorporates the tickers from _ticker_list into _ticker_dict with 
        default value None as value for each key
        """
        for ticker in self._ticker_list:
            self._ticker_dict.setdefault(ticker, None)
        return None

    def prune_ticker_dict_with_fresh_tickers(self) -> None:
        """
        Removes entries from _ticker_dict if they are not also in _ticker_list
        """
        self._ticker_dict = {
            key: val 
            for key, val in self._ticker_dict.items()
            if key in self._ticker_list
        }
        return None

    def return_tickers(self, fresh_ticker_list: list[str], stored_ticker_dict: dict) -> dict:
        """
        Builds the updated tickers dict by calling methods in TickerService
        """
        self.update_ticker_list(fresh_ticker_list)
        self.update_stored_tickers(stored_ticker_dict)
        self.populate_ticker_dict_with_fresh_tickers()
        self.prune_ticker_dict_with_fresh_tickers()
        return self._ticker_dict

