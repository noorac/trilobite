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
from trilobite.marketdata.tickerservice import TickerService
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
        client = YFClient()
        market = MarketService(client=client)
        ticker = TickerService()

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

    def update_tickers(self, ticker: str, start_date: date | None) -> None:
        """
        Updates the tickers
        """
        # check_for_corporate_action = True if start_date is not None
        # start_date = start_date if start_date is not None else date(1900,1,1)
        start_date, check_for_corporate_action = (start_date, True) if start_date is not None else (date(1900,1,1), False)
        #if start_date is not None else date(1900,1,1)
        #Make sure we have an instrument id for the ticker
        instrument_id = self._state.repo.ensure_instrument(ticker)
        #Fetch the data and store to dataframe
        df = self._state.market.get_ohlcv(ticker, start_date)
        #Ingest the data in the DB
        affected = self._state.repo.upsert_ohlcv_daily(instrument_id=instrument_id, df = df)
        #Number of affected rows
        count = affected if affected > 0 else len(df.index)
        logger.info(count)
        return None

        
    def get_todays_tickers(self) -> list:
        """
        Returns a list of todays tickers
        """
        nasdaq_url: str = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/refs/heads/main/nasdaq/nasdaq_tickers.json"
        nyse_url: str = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/refs/heads/main/nyse/nyse_tickers.json"
        amex_url: str = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/refs/heads/main/amex/amex_tickers.json"

        with urllib.request.urlopen(nyse_url) as response:
            nyse_tickers: List[str] = json.load(response)
        #cleanup
        nyse_tickers = [t.replace("^", "-") for t in nyse_tickers]

        with urllib.request.urlopen(amex_url) as response:
            amex_tickers: List[str] = json.load(response)
        #cleanup
        amex_tickers = [t.replace("^", "-") for t in amex_tickers]

        with urllib.request.urlopen(nasdaq_url) as response:
            nasdaq_tickers: List[str] = json.load(response)
        #cleanup
        nasdaq_tickers = [t.replace("^", "-") for t in nasdaq_tickers]

        #TEMP return list
        return ["AAPL", "GOOGL", "DIS", "NVDA", "CAT"]




    def run(self, stdscr: "curses._CursesWindow") -> None:
        """
        Starting up the UIController, takes in the stdscr from curses
        """
        logger.info("Starting curses..")
        # TEMP TESTING
        tickers = self.get_todays_tickers()
        update_dict = self._state.repo.last_ohlcv_date_by_ticker()
        ticker_dict = self._state.ticker.return_tickers(tickers, update_dict)
        for ticker, start_date in ticker_dict.items():
            self.update_tickers(
                    ticker,
                    start_date,
            )

        self.close()
        # END TEMP TESTING
        return None

