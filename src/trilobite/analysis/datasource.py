from __future__ import annotations

from datetime import date, timedelta
import logging
from pandas import DataFrame
from trilobite.db.repo import MarketRepo
from trilobite.utils.utils import period_to_date

logger = logging.getLogger(__name__)

class MarketDataSource:
    def __init__(self, repo: MarketRepo) -> None:
        self._repo = repo


    def load_adjclose_matrix(self,
                             *,
                             period: str,
                             end_date: date | None = None,
                             ) -> DataFrame:
        """
        Loads the matrix for all adjclose values
        """
        tickers = self._repo.list_tickers_with_min_ohlcv_days(period, end_date=end_date)

        if end_date is None:
            with self._repo.conn.cursor() as cur:
                cur.execute("SELECT CURRENT_DATE;")
                (end_date_db,) = cur.fetchone()
            end_date = end_date_db

        #start_date = end_date - timedelta(days=min_days - 1)
        start_date, end_date = period_to_date(period, end_date=end_date)
        long_df = self._repo.fetch_adjclose_long(tickers, start_date=start_date, end_date=end_date)
        logger.debug(f"Long df rows: {len(long_df)}")

        wide = long_df.pivot(index="date", columns="ticker", values="adjclose").sort_index()
        logger.debug(f"Wide before dropna: {wide.shape}")
        wide = wide.dropna(axis=1)
        logger.debug(f"Wide after dropna(axis=1): {wide.shape}")
        return wide

