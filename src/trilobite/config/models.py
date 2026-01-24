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
class AppConfig:
    ticker: CFGTickerService
    db: CFGDataBase

