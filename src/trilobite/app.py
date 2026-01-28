from __future__ import annotations

from typing import Callable, List
from dataclasses import dataclass, replace
from datetime import date, timedelta
from pandas import DataFrame
import logging

from trilobite.cli.runtimeflags import RuntimeFlags
from trilobite.cli.cliflags import CLIFlags
from trilobite.ui.cli.clicontroller import CLIController
from trilobite.config.models import AppConfig, CFGTickerService, CFGDataBase
from trilobite.db.connect import DbSettings, connect
from trilobite.db.repo import MarketRepo
from trilobite.db.schema import create_schema
from trilobite.handlers.uihandlers import Handler
from trilobite.marketdata.yfclient import YFClient
from trilobite.marketdata.marketservice import MarketService
from trilobite.state.state import AppState
from trilobite.tickers.tickerclient import TickerClient
from trilobite.tickers.tickerservice import Ticker, TickerService
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
logger = logging.getLogger(__name__)


class App:
    """
    The main app! This object will run most of the program
    """
    def __init__(self, cfg: AppConfig, flags: RuntimeFlags) -> None:
        logger.info("Running ..")
        self._flags = flags

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
        ticker = TickerService(repo=repo, tickerclient=tickerclient, cfg=cfg.ticker, flags=self._flags)

        #Create AppState
        self._state = AppState(repo=repo, market=market, ticker=ticker)

        #Handler wiring
        self._handler = Handler(self._state, self._cfg, self._flags)
        return None

    def close(self) -> None:
        """
        Attempts to close the connection to the db
        """
        try:
            self._conn.close()
        except Exception:
            logger.exception("Failed at closing DB connection")

    def run_headless(self, flags: CLIFlags) -> None:
        """
        Running headless version, takes in the argv list from terminal
        """
        ui = CLIController(flags=flags)
        self._run_loop(ui)

    def _run_loop(self, ui) -> None:
        logger.info(" > ")
        running = True
        while running:
            cmd: Command = ui.get_command()
            for evt in self._handler.handle(cmd):
                if isinstance(evt, EvtExit):
                    running = False
                else:
                    ui.handle_event(evt)

        self.close()
        return None


