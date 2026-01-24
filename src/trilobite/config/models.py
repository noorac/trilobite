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
