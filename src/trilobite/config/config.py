from __future__ import annotations

from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class CFGDev:
    dev: bool = False
    debug: bool = False
    dry_run: bool = False
    consolelog: bool = False

@dataclass(frozen=True)
class CFGTickerService:
    """
    Stores config settings for TickerService
    """
    default_date: date = date(1975,1,1)
    default_timedelta: int = 1

@dataclass(frozen=True)
class CFGDataBase:
    dbname: str = "trilobite"
    host: str  = "/run/postgresql"
    user: str | None = None
    port: int = 5432

@dataclass(frozen=True)
class CFGMisc:
    #Stagger requests to yahoo, start at 0.1s, add amount as upper limit,
    #e.g. 0.2, using random the request will wait 0.1-0.3s between requests
    stagger_requests: bool = True
    stagger_start: float = 0.1
    stagger_amount: float = 0.2

@dataclass(frozen=True)
class CFGAnalysis:
    top_n: int = 20
    n_factors: int = 20
    #Using period instead
    #min_days: int = 1260
    lookback: int = 60
    horizon: int = 1
    epochs: int = 10
    period: str = "3y"
    ticker: str = "AAPL"

@dataclass(frozen=True)
class AppConfig:
    dev: CFGDev
    ticker: CFGTickerService
    db: CFGDataBase
    misc: CFGMisc
    analysis: CFGAnalysis

