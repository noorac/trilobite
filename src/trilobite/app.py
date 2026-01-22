from __future__ import annotations

from typing import List
from dataclasses import dataclass
from datetime import date
import logging
import json
import urllib.request

from trilobite.db.connect import connect
from trilobite.db.repo import MarketRepo
from trilobite.db.schema import create_schema
from trilobite.marketdata.yfclient import YFClient
from trilobite.marketdata.marketservice import MarketService

logger = logging.getLogger(__name__)

@dataclass
class AppState:
    """
    Stores the state of different objects needed by App
    """
    repo: MarketRepo
    market: MarketService

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
        client = YFClient()
        market = MarketService(client=client)

        #Create AppState
        self._state = AppState(repo=repo, market=market)
        return None

    def close(self) -> None:
        """
        Attempts to close the connection to the db
        """
        try:
            self._conn.close()
        except Exception:
            logger.exception("Failed at closing DB connection")

    def update_tickers(self, ticker: str, start_date: date) -> None:
        """
        Updates the tickers
        """
        #Make sure we have an instrument id for the ticker
        instrument_id = self._state.repo.ensure_instrument(ticker)
        #Fetch the data and store to dataframe
        df = self._state.market.get_ohlcv(ticker)
        #Ingest the data in the DB
        affected = self._state.repo.upsert_ohlcv_daily(instrument_id=instrument_id, df = df)
        #Number of affected rows
        count = affected if affected > 0 else len(df.index)
        return None

        
    def get_todays_tickers(self) -> list:
        """
        Returns a list of todays tickers
        """
        nasdaq_url: str = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/refs/heads/main/nasdaq/nasdaq_tickers.json"
        nyse_url: str = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/refs/heads/main/nyse/nyse_tickers.json"
        amex_url: str = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/refs/heads/main/amex/amex_tickers.json"




    def run(self, stdscr: "curses._CursesWindow") -> None:
        """
        Starting up the UIController, takes in the stdscr from curses
        """
        logger.info("Starting curses..")
        # TEMP TESTING
        #Setup ticker and instrument_id
        ticker = "GOOGL"

        #check for last date ticker was updated
        update_dict = self._state.repo.last_ohlcv_date_by_ticker()
        for ticker, start_date in update_dict.items():
            self.update_tickers(
                    ticker,
                    start_date if start_date is not None else date(1900,1,1)
            )

        self.close()
        # END TEMP TESTING
        return None

