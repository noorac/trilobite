from __future__ import annotations

import logging
import time
from dataclasses import replace

from pandas import DataFrame

from trilobite.state.state import AppState
from trilobite.config.models import AppConfig
from trilobite.tickers.tickerservice import Ticker
from trilobite.commands.uicommands import (
    CmdNotAnOption, 
    CmdQuit, 
    CmdUpdateAll,
    Command, 
)
from trilobite.events.uievents import (
    EvtExit,
    EvtStartUp,
    EvtStatus, 
    EvtProgress,
    Event, 
)
from trilobite.utils.utils import stagger_requests

logger = logging.getLogger(__name__)

class Handler:
    def __init__(self, state: AppState, cfg: AppConfig):
        self._state = state
        self._cfg = cfg

    def handle(self, cmd):
        """
        Handles events returned from uicontroller
        """
        if isinstance(cmd, CmdQuit):
            yield EvtStatus("Quitting ..", waittime=1)
            yield EvtExit()
            return

        if isinstance(cmd, CmdUpdateAll):
            yield from self._handle_update_all()
            return

        if isinstance(cmd, CmdNotAnOption):
            yield EvtStatus("Not an option...", waittime=1)
            return

        yield EvtStatus(f"Unknown command: {cmd!r}")

    def _handle_update_all(self):
        """
        Handles update all situation
        """
        tickers = self._state.ticker.update()
        total = len(tickers)

        if total == 0:
            yield EvtStatus("No tickers found", waittime=1)
            return

        yield EvtStatus("Starting update of all tickers", waittime=1)

        for i, ticker, in enumerate(tickers, start=1):
            if self._cfg.misc.stagger_requests:
                time.sleep(stagger_requests())
            yield EvtProgress(f"{ticker.tickersymbol}", i, total)

            try:
                self.update_ticker(ticker)
            except Exception as e:
                yield EvtStatus(f"Error updating {ticker.tickersymbol}: {e}")
                logger.exception(f"Error updating {ticker.tickersymbol}: {e}")
                continue

        yield EvtStatus("All tickers updated", waittime=1)

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
