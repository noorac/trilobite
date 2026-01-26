from dataclasses import dataclass

from trilobite.db.repo import MarketRepo
from trilobite.marketdata.marketservice import MarketService
from trilobite.tickers.tickerservice import TickerService

@dataclass
class AppState:
    """
    Stores the state of different objects needed by App
    """
    repo: MarketRepo
    market: MarketService
    ticker: TickerService
