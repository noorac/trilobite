from __future__ import annotations

from typing import Callable, List
from dataclasses import dataclass, replace
from datetime import date, timedelta
from pandas import DataFrame
import logging

from trilobite.config.models import AppConfig, CFGTickerService, CFGDataBase
from trilobite.db.connect import DbSettings, connect
from trilobite.db.repo import MarketRepo
from trilobite.db.schema import create_schema
from trilobite.marketdata.yfclient import YFClient
from trilobite.marketdata.marketservice import MarketService
from trilobite.tickers.tickerclient import TickerClient
from trilobite.tickers.tickerservice import Ticker, TickerService
from trilobite.tui.uicontroller import UIController

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
    def __init__(self, cfg: AppConfig) -> None:
        logger.info("Running ..")

        self._cfg = cfg

        # DB wiring
        self._conn = connect(DbSettings(
            dbname=cfg.db.dbname,
            host=cfg.db.host,
            user=cfg.db.user,
            port=cfg.db.port,
        ))
        create_schema(self._conn)
        repo = MarketRepo(self._conn)

        # Market wiring
        yfclient = YFClient()
        market = MarketService(client=yfclient)

        # Ticker wiring
        tickerclient = TickerClient()
        ticker = TickerService(repo=repo, tickerclient=tickerclient, cfg=cfg.ticker)

        #UIController wiring

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

    def update_ticker(self, ticker: Ticker) -> None:
        """
        Performs an update of the data for the given ticker

        Params:
        - Ticker object containing ticker symbol, update_date, 
        check_for_corporate_actions flag
        """
        df = self._state.market.get_ohlcv(ticker.tickersymbol, ticker.update_date)

        if ticker.check_corporate_actions and self.detect_corporate_action(df):
            logger.info(f"Detected corporate actions, re-running with default date")
            fullupdate = replace(
                    ticker,
                    update_date = self._cfg.ticker.default_date,
                    check_corporate_actions = False,
            )
            return self.update_ticker(fullupdate)

        instrument_id = self._state.repo.ensure_instrument(ticker.tickersymbol)
        affected = self._state.repo.upsert_ohlcv_daily(instrument_id=instrument_id, df = df)
        count = affected if affected > 0 else len(df.index)
        logger.info(f"Updated: {ticker.tickersymbol} , from date {ticker.update_date}, with {count} rows added")

    def update_all(self) -> None:
        """
        Runs the update of all tickers after doing an update of todays tickers
        """
        for ticker in self._state.ticker.update():
            self.update_ticker(ticker)

    def run(self, stdscr: "curses._CursesWindow") -> None:
        """
        Starting up the UIController, takes in the stdscr from curses
        """
        logger.info("Running ..")
        ui = UIController(
                stdscr,
                on_update_all=self.update_all,
                on_quit=self.close,
        )
        ui.run()
        self.close()
        return None

