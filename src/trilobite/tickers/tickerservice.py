from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from datetime import date, timedelta
import logging

from trilobite.config.models import CFGDev, CFGTickerService
from trilobite.tickers.tickerclient import TickerClient

logger = logging.getLogger(__name__)

class TickerRepo(Protocol):
    """
    Protocol that allows for insertion of the last_ohlcv_date_by_ticker method
    into TickerService
    """
    def last_ohlcv_date_by_ticker(self) -> dict[str, date | None]:
        ...

    def ensure_instrument(self, ticker: str) -> int:
        ...

    def list_active_tickers(self) -> list[str]:
        ...

    def deactivate_tickers(self, tickers: list[str]) -> int:
        ...

@dataclass(frozen=True)
class Ticker:
    """
    Contains data on tickers
    """
    tickersymbol: str
    update_date: date 
    check_corporate_actions: bool


class TickerService:
    """
    Keeps track of currently active tickers on the market
    """
    def __init__(self, repo: TickerRepo, tickerclient: TickerClient, cfg_ts: CFGTickerService, cfg_dev: CFGDev) -> None:
        self._repo = repo
        self._tickerclient = tickerclient
        self._cfg_ts = cfg_ts
        self._cfg_dev = cfg_dev

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

    def _find_start_date(self, lastdate: date | None) -> date:
        """
        Sets the start date for the ticker by deciding if lastdate is a date 
        or a Nonetype

        Params:
        - lastdate: either a date if it exists in the db and is previously 
        stored, or None if it doesn't exist

        Returns:
        - date object, lastdate if not None, default set in cfg if None
        """
        return (lastdate-timedelta(self._cfg_ts.default_timedelta)) if lastdate is not None else self._cfg_ts.default_date

    def _flag_lastdate(self, lastdate: date | None) -> bool:
        """
        Returns True or False based on if the lastdate is date object or None

        Params:
        - lastdate: date object or None

        Returns:
        - bool: True if lastdate is date, False if lastdate is None
        """
        return True if lastdate is not None else False

    def _build_ticker_objects(self, tickersymbol: str, lastdate: date | None) -> Ticker:
        """
        Builds the objects of the Ticker class.
        """
        return Ticker(
            tickersymbol = tickersymbol,
            update_date = self._find_start_date(lastdate),
            check_corporate_actions = self._flag_lastdate(lastdate),
            )

    def _reconsile_instruments(self, todays_tickers: list[str]) -> list[str]:
        """
        Ensure todays tickers exist, and are active in the DB, and deactivate DB
        tickers that are active but missing from todays list.

        Params:
        - list: todays list of true and real active tickers

        Returns:
        - list: tickers that were missing and got deactivated
        """
        todays_set = {t.strip().upper() for t in todays_tickers if t and t.strip()}
        for t in todays_set:
            self._repo.ensure_instrument(t)

        active_db = set(self._repo.list_active_tickers())
        missing = sorted(active_db - todays_set)

        if missing:
            self._repo.deactivate_tickers(missing)

        return missing

    def update(self, fullupdate=False) -> list[Ticker]:
        """
        Runs a full update: gets a list[str] from tickerclient with current
        active tickers, gets dict{key:ticker,value:date_of_last_entry} from the
        DB, populates the dict with new tickers that are in the list but not the
        dict, then prunes no longer active tickers that are in the dict but not
        in the list.

        Params:
        - fullupdate: requests fullupdate of every ticker to do a hard reset

        Returns:
        - dict{key:ticker, value:date_of_last_entry}
        """
        self._ticker_list = self._tickerclient.get_todays_tickers()

        if self._cfg_dev.dev:
            self._ticker_list = ["AAPL", "GOOGL", "DIS", "NVDA", "CAT", "META", "TSLA"]
        else:
            self._ticker_list = self._ticker_list
        
        deactivated = self._reconsile_instruments(self._ticker_list)
        logger.info(f"The following tickers were deactivated: {deactivated}")

        self._ticker_dict = self._repo.last_ohlcv_date_by_ticker()

        self._populate_missing_tickers()
        self._prune_missing_tickers()

        if fullupdate:
            logger.info(f"fullupdate True: Resetting all dates to None")
            for key, val in self._ticker_dict.items():
                self._ticker_dict[key] = None

        tickermap = []
        for key, val in self._ticker_dict.items():
            tickermap.append(self._build_ticker_objects(tickersymbol=key, lastdate=val))

        #Update to dataclass object later?
        return tickermap
