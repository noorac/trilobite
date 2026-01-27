from __future__ import annotations

from datetime import date, timedelta
from pandas import DataFrame
from trilobite.db.repo import MarketRepo

class MarketDataSource:
    def __init__(self, repo: MarketRepo) -> None:
        self._repo = repo


    def load_adjclose_matrix(self,
                             *,
                             min_days: int,
                             end_date: date | None = None,
                             ) -> DataFrame:
        """
        Loads the matrix for all adjclose values
        """
        tickers = self._repo.list_tickers_with_min_ohlcv_days(min_days, end_date=end_date)

        if end_date is None:
            with self._repo.conn.cursor() as cur:
                cur.execute("SELECT CURRENT_DATE;")
                (end_date_db,) = cur.fetchone()
            end_date = end_date_db

        start_date = end_date - timedelta(days=min_days - 1)
        long_df = self._repo.fetch_adjclose_long(tickers, start_date=start_date, end_date=end_date)

        wide = long_df.pivot(index="date", columns="ticker", values="adjclose").sort_index()
        wide = wide.dropna(axis=1)
        return wide

