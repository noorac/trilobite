from __future__ import annotations

from typing import List
from dataclasses import dataclass
from datetime import date
from pandas import DataFrame
import logging
import json
import urllib.request

from trilobite.db.connect import connect
from trilobite.db.repo import MarketRepo
from trilobite.db.schema import create_schema
from trilobite.marketdata.yfclient import YFClient
from trilobite.marketdata.marketservice import MarketService
from trilobite.tickers.tickerclient import TickerClient
from trilobite.tickers.tickerservice import TickerService

logger = logging.getLogger(__name__)

@dataclass
class AppState:
    """
    Stores the state of different objects needed by App
    """
    repo: MarketRepo
    market: MarketService
    ticker: TickerService

class App:
    """
    The main app! This object will run most of the program
    """
    def __init__(self) -> None:
        logger.info("Initializing ..")

        # DB wiring
        self._conn = connect()
        create_schema(self._conn)
        repo = MarketRepo(self._conn)

        # Market wiring
        yfclient = YFClient()
        market = MarketService(client=yfclient)

        # Ticker wiring
        tickerclient = TickerClient()
        ticker = TickerService(repo=repo, tickerclient=tickerclient)

        #Create AppState
        self._state = AppState(repo=repo, market=market, ticker=ticker)
        return None

    def close(self) -> None:
        """
        Attempts to close the connection to the db
        """
        try:
            self._conn.close()
        except Exception:
            logger.exception("Failed at closing DB connection")

    def detect_corporate_action(self, df: DataFrame) -> bool:
        """
        Checks if Stocksplits or Dividends column of the given dataframe are
        different from 0.0, meaning there was a stocksplit or dividend action
        that day.

        Params:
        - df: the DataFrame to check

        Returns:
        - bool: returns True if there was a corporate action in the DataFrame
        """
        return ((df["dividends"] != 0.0).any() or (df["stocksplits"] != 0.0).any())

    def update_ticker(self, ticker: str, start_date: date | None) -> None:
        """
        Updates the tickers
        """
        start_date, check_for_corporate_action = (start_date, True) if start_date is not None else (date(1900,1,1), False)

        instrument_id = self._state.repo.ensure_instrument(ticker)
        df = self._state.market.get_ohlcv(ticker, start_date)
        if check_for_corporate_action:
            if self.detect_corporate_action(df):
                self.update_ticker(ticker, date(1900,1,1))

        #Ingest the data in the DB
        affected = self._state.repo.upsert_ohlcv_daily(instrument_id=instrument_id, df = df)
        #Number of affected rows
        count = affected if affected > 0 else len(df.index)
        logger.info(f"{ticker}: {count} added")
        return None

    def run(self, stdscr: "curses._CursesWindow") -> None:
        """
        Starting up the UIController, takes in the stdscr from curses
        """
        logger.info("Starting curses..")
        # TEMP TESTING
        ticker_dict = self._state.ticker.update()
        for ticker, start_date in ticker_dict.items():
            self.update_ticker(
                    ticker,
                    start_date,
            )

        self.close()
        # END TEMP TESTING
        return None

