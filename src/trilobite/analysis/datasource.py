from __future__ import annotations

from datetime import date, timedelta
from pandas import DataFrame
from trilobite.db.repo import MarketRepo

class MarketDataSource:
    def __init__(self, repo: MarketRepo) -> None:
        self._repo = repo


