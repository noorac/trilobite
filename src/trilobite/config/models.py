from __future__ import annotations

from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class CFGTickerService:
    """
    Stores config settings for TickerService
    """
    default_date: date
    default_timedelta: int

@dataclass(frozen=True)
class CFGDataBase:
    dbname: str
    host: str 
    user: str | None
    port: int

@dataclass(frozen=True)
class CFGMisc:
    stagger_requests: bool

@dataclass(frozen=True)
class CFGAnalysis:
    topn: int = 20
    min_days: int = 252 * 5
    lookback: int = 60
    horizon: int = 1
    epochs: int = 10

@dataclass(frozen=True)
class AppConfig:
    ticker: CFGTickerService
    db: CFGDataBase
    misc: CFGMisc
    analysis: CFGAnalysis

