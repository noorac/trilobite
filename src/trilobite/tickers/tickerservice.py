from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from datetime import date

from trilobite.tickers.tickerclient import TickerClient


class TickerRepo(Protocol):
    """
    Protocol that allows for insertion of the last_ohlcv_date_by_ticker method
    into TickerService
    """
    def last_ohlcv_date_by_ticker(self) -> dict[str, date | None]:
        ...

@dataclass(frozen=True)
class Ticker:
    """
    Contains data on tickers
    """
    ticker: str
    start_date: date
    lastdate: date | None
    check_corporate_actions: bool


class TickerService:
    """
    Keeps track of currently active tickers on the market
    """
    def __init__(self, repo: TickerRepo, tickerclient: TickerClient) -> None:
        self._repo = repo
        self._tickerclient = tickerclient

        self._ticker_list: list[str] = []
        self._ticker_dict: dict[str, date | None] = {}

    def _populate_missing_tickers(self) -> None:
        """
        Incorporates the tickers from _ticker_list into _ticker_dict with 
        default value None as value for each key
        """
        for ticker in self._ticker_list:
            self._ticker_dict.setdefault(ticker, None)

    def _prune_missing_tickers(self) -> None:
        """
        Removes entries from _ticker_dict if they are not also in _ticker_list
        """
        self._ticker_dict = {
            key: val 
            for key, val in self._ticker_dict.items()
            if key in set(self._ticker_list)
        }

    def _build_ticker_objects(self, ticker: str, lastdate: date | None) -> None:
        """
        Builds the objects of the Ticker class.
        """

    def update(self) -> dict[str, date | None]:
        """
        Runs a full update: gets a list[str] from tickerclient with current
        active tickers, gets dict{key:ticker,value:date_of_last_entry} from the
        DB, populates the dict with new tickers that are in the list but not the
        dict, then prunes no longer active tickers that are in the dict but not
        in the list.

        Returns:
        - dict{key:ticker, value:date_of_last_entry}
        """
        self._ticker_list = self._tickerclient.get_todays_tickers()
        
        #Temp used for testing during dev
        self._ticker_list = ["AAPL", "GOOGL", "DIS", "NVDA", "CAT", "META", "TSLA"]
        self._ticker_dict = self._repo.last_ohlcv_date_by_ticker()

        self._populate_missing_tickers()
        self._prune_missing_tickers()

        tickermap = []
        for key, val in self._ticker_dict.items():
            tickermap.append(self._build_ticker_objects(ticker=key, lastdate=val))

        #Update to dataclass object later?
        return self._ticker_dict
