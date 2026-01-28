from __future__ import annotations

import logging
import time
from dataclasses import replace

from pandas import DataFrame

from trilobite.analysis.datasource import MarketDataSource
from trilobite.analysis.features import prices_to_log_returns
from trilobite.analysis.trainers.nn_direction import NNDirectionsConfig, NNDirectionsTrainer
from trilobite.cli.runtimeflags import RuntimeFlags
from trilobite.state.state import AppState
from trilobite.config.models import AppConfig
from trilobite.tickers.tickerservice import Ticker
from trilobite.commands.uicommands import (
    CmdTrainNN,
    CmdNotAnOption, 
    CmdQuit, 
    CmdUpdateAll,
    Command, 
)
from trilobite.events.uievents import (
    EvtPredictionRanked,
    EvtExit,
    EvtStartUp,
    EvtStatus, 
    EvtProgress,
    Event, 
)
from trilobite.utils.utils import stagger_requests

logger = logging.getLogger(__name__)

class Handler:
    def __init__(self, state: AppState, cfg: AppConfig, flags: RuntimeFlags):
        self._state = state
        self._cfg = cfg
        self._flags = flags

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

        if isinstance(cmd, CmdTrainNN):
            yield from self._handle_train_nn(cmd)

        else:
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
        error_tickers = []
        for i, ticker, in enumerate(tickers, start=1):
            if self._cfg.misc.stagger_requests:
                time.sleep(stagger_requests())
            yield EvtProgress(f"{ticker.tickersymbol}", i, total)

            try:
                self.update_ticker(ticker)
            except Exception as e:
                #yield EvtStatus(f"Error updating {ticker.tickersymbol}: {e}")
                logger.exception(f"Error updating {ticker.tickersymbol}: {e}")
                error_tickers.append(ticker.tickersymbol)
                continue

        if len(error_tickers) > 0:
            yield EvtStatus(f"Following tickers failed to update: {error_tickers}", waittime=5)
        else:
            yield EvtStatus("All tickers updated", waittime=1)

    def _handle_train_nn(self, cmd: CmdTrainNN):
        yield EvtStatus("Loading data for NN training...", waittime=0)

        ds = MarketDataSource(self._state.repo)

        yield EvtStatus(f"Building adjclose matrix (min_days={self._cfg.analysis.min_days})...", waittime=0)
        adj = ds.load_adjclose_matrix(min_days=self._cfg.analysis.min_days)

        yield EvtStatus("Computing log returns...", waittime=0)
        rets = prices_to_log_returns(adj)

        yield EvtStatus("Training NN (PCA factors + GRU)...", waittime=0)

        cfg = NNDirectionsConfig(
            n_factors=self._cfg.analysis.n_factors,
            lookback=self._cfg.analysis.lookback,
            horizon=self._cfg.analysis.horizon,
            epochs=self._cfg.analysis.epochs,
            device="cpu",
        )
        trainer = NNDirectionsTrainer(self._flags, cfg)
        logger.info(f"adj.shape={adj.shape}, rets.shape={rets.shape}")
        trainer.fit(rets)

        yield EvtStatus("Predicting latest...", waittime=0)
        pred = trainer.predict_latest(rets)

        ranked = pred.ranked(cmd.top_n)
        yield EvtPredictionRanked(date=pred.date, ranked=ranked)

        yield EvtStatus("Done.", waittime=1)



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
