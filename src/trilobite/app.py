from __future__ import annotations

from dataclasses import dataclass
import logging

from marketservice import MarketService
from trilobite.db.connect import connect
from trilobite.db.repo import MarketRepo
from trilobite.db.schema import create_schema
from trilobite.marketdata.yfclient import YFClient

logger = logging.getLogger(__name__)

@dataclass
class AppState:
    repo: MarketRepo
    market: MarketService

class App:
    """
    The main app
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

    def run(self, stdscr: "curses._CursesWindow") -> None:
        """
        Starting up the app system
        """
        logger.info("Starting curses..")
        ticker = "AAPL"
        df = self._state.market.get_ohlcv(ticker)

        instrument_id = self._state.repo.ensure_instrument(ticker)

        affected = self._state.repo.upsert_ohlcv_daily(instrument_id=instrument_id, df = df)

        count = affected if affected > 0 else len(df.index)
        return None

