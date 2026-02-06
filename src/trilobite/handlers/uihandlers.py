from __future__ import annotations

import logging
import os
import time
from dataclasses import replace

from pandas import DataFrame

from trilobite.analysis.datasource import MarketDataSource
from trilobite.analysis.features import prices_to_log_returns
from trilobite.analysis.trainers.nn_direction import NNDirectionsConfig, NNDirectionsTrainer
from trilobite.state.state import AppState
from trilobite.config.config import AppConfig
from trilobite.tickers.tickerservice import Ticker
from trilobite.commands.uicommands import (
    CmdDisplayGraph,
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
from trilobite.utils.paths import data_dir
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

        if isinstance(cmd, CmdTrainNN):
            yield from self._handle_train_nn(cmd)

        if isinstance(cmd, CmdDisplayGraph):
            yield from self._handle_display_graph_of_period(cmd)

        else:
            yield EvtStatus(f"Unknown command: {cmd!r}")

    def _handle_update_all(self):
        """
        Handles update all situation
        """
        tickers = self._state.ticker.update()
        logger.info(f"Tickermap returned ..")
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

        yield EvtStatus(f"Building adjclose matrix ..", waittime=0)
        adj = ds.load_adjclose_matrix(period=self._cfg.analysis.period)
        yield EvtStatus(f"Qualified tickers(min_days={self._cfg.analysis.period}): {adj.shape[1]}", waittime=0)

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
        trainer = NNDirectionsTrainer(cfg)
        logger.debug(f"adj.shape={adj.shape}, rets.shape={rets.shape}")
        yield EvtStatus(
        f"n_factors={self._cfg.analysis.n_factors} | "
        f"lookback={self._cfg.analysis.lookback} | "
        f"horizon={self._cfg.analysis.horizon} | "
        f"epochs={self._cfg.analysis.epochs} | "
        f"device=cpu"
        )
        trainer.fit(rets)

        yield EvtStatus("Predicting latest...", waittime=0)
        pred = trainer.predict_latest(rets)

        ranked = pred.ranked(self._cfg.analysis.top_n)
        yield EvtPredictionRanked(topn=self._cfg.analysis.top_n, date=pred.date, ranked=ranked)

    def _handle_display_graph_of_period(self, cmd: CmdDisplayGraph):
        """
        Handles the request for graph display of a single ticker
        """
        df = self._state.repo.fetch_adjclose_series(self._cfg.analysis.ticker, self._cfg.analysis.period)
        #create plot here for now
        import matplotlib.pyplot as plt
        import subprocess
        import numpy as np

        x = np.arange(len(df))
        adjclose = df["adjclose"].to_numpy()

        coef = np.polyfit(x, adjclose, deg = 1)
        trend = np.poly1d(coef)(x)

        out_dir = data_dir(create=True)
        filename = f"{self._cfg.analysis.ticker}_{self._cfg.analysis.period}.png"
        out_path = out_dir / filename

        #set colors:
        plt.rcParams.update({
        "figure.facecolor": "#0f172a",
        "axes.facecolor": "#0f172a",
        "axes.edgecolor": "white",
        "axes.labelcolor": "white",
        "text.color": "white",
        "xtick.color": "white",
        "ytick.color": "white",
        "grid.color": "#e5e7eb",
        "grid.alpha": 0.25,
        })

        #plt.style.use("seaborn-v0_8-darkgrid")
        fig, ax = plt.subplots(figsize=(10,5))
        #ax.plot(df["date"], df["adjclose"], linewidth=2)
        ax.plot(df["date"], adjclose, label="Adj Close", linewidth=2, color="#38bdf8")
        ax.plot(df["date"], trend, label="Linear trend", linestyle="--", linewidth=2, color="#fbbf24")
        ax.set_title(f"{self._cfg.analysis.ticker} - Adjusted close ({self._cfg.analysis.period})")
        ax.set_xlabel("Date")
        ax.set_ylabel("Adjusted Close")
        ax.grid(True)
        ax.legend()
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        #display in kitty if using kitty
        term = os.environ.get("TERM", "")
        if "kitty" not in term.lower():
            yield EvtStatus("Not using kitty terminal, open plot manually", waittime=0)
        try:
            subprocess.run(["kitty", "+kitten", "icat", str(out_path)],
                           check=False)
        except FileNotFoundError:
            logger.error(f"Cannot find file, open plot manually")
            pass




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
        logger.debug(f"Updated: {ticker.tickersymbol} , from date {ticker.update_date}, with {count} rows added")

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

