from __future__ import annotations

from datetime import date, timedelta
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import pandas as pd
import psycopg
from psycopg.rows import tuple_row
from pandas import DataFrame

def _none_if_na(x: Any) -> Any | None:
    """
    Converts pandas/numpy NA-like values (NAN/NAT) and None to None for SQL NULL
    """
    return None if x is None or pd.isna(x) else x

def _int_or_none(x: Any) -> int | None:
    """
    Converts NA-like values to None, else convert to int (for BIGINT)
    """
    x = _none_if_na(x)
    if x is None:
        return None
    return int(x)

def _float_or_none(x: Any) -> float | None:
    """
    Converts Na-like values to None, else convert to float(for NUMERIC)
    """
    x = _none_if_na(x)
    if x is None:
        return None
    return float(x)

@dataclass
class MarketRepo:
    """
    Repository for market-data persistence.

    Params:
    - conn: an open psycipg connection.
    """
    conn: psycopg.Connection

    def ensure_instrument(self, ticker: str) -> int:
        """
        Ensure a row exists in instrument for the given ticker and return its id

        Performs an upsert:
        - if the ticker doesnt exist, it is inserted
        - if it exists, it is updated to iself

        Params:
        - ticker: ticker symbol

        Returns:
        - int: the instrument id

        """
        ticker = ticker.strip().upper()
        if not ticker:
            raise ValueError("Ticker cannot be empty")

        with self.conn.cursor(row_factory=tuple_row) as cur:
            cur.execute(
                """
                INSERT INTO instrument (ticker, is_active, last_seen, deactivated_at)
                VALUES (%s, TRUE, CURRENT_DATE, NULL)
                ON CONFLICT (ticker) DO UPDATE SET 
                    ticker = EXCLUDED.ticker,
                    is_active = TRUE,
                    last_seen = CURRENT_DATE,
                    deactivated_at = NULL
                RETURNING id;
                """,
                (ticker,),
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("Failed to fetch instrument id after upsert")
            (instrument_id,) = row
        return int(instrument_id)

    def upsert_ohlcv_daily(self, instrument_id: int, df: DataFrame) -> int:
        """
        Upsert daily OHLCV rows into ahlcv_daily table for given instrument

        Params:
        - instrument_id: the id of the instrument in the instrument table
        - df: dataframe containing the daily data.

        Returns:
        - int: number of affected rows reported by psycopg for executemany, 
        returns 0 if the DataFrame is empty.
        """
        if df.empty:
            return 0
        cols = [
            "date",
            "open", 
            "high",
            "low",
            "close",
            "adjclose",
            "volume",
            "dividends",
            "stocksplits",
        ]
        missing = [c for c in cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing requires columns for upsert: {missing}")

        #Build the rows iterable, one tuple per dataframe row
        rows: Iterable[tuple] = (
            (
                instrument_id,
                r["date"], #This comes in as a python date from YFClient
                _float_or_none(r["open"]),
                _float_or_none(r["high"]),
                _float_or_none(r["low"]),
                _float_or_none(r["close"]),
                _float_or_none(r["adjclose"]),
                _int_or_none(r["volume"]),
                _float_or_none(r["dividends"]),
                _float_or_none(r["stocksplits"]),
            )
            for _, r in df[cols].iterrows()
        )
        
        sql = """
        INSERT INTO ohlcv_daily (
            instrument_id, date, open, high, low, close, adjclose, volume, dividends, stocksplits
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (instrument_id, date) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            adjclose = EXCLUDED.adjclose,
            volume = EXCLUDED.volume,
            dividends = EXCLUDED.dividends,
            stocksplits = EXCLUDED.stocksplits
        ;
        """

        with self.conn.cursor() as cur:
            cur.executemany(sql, rows)
            affected = cur.rowcount 

        self.conn.commit()
        return 0 if affected is None or affected < 0 else int(affected)

    def last_ohlcv_date_by_ticker(self) -> dict[str, date | None]:
        """
        Returns the latest stored OHLCV date per ticker

        Returns: a dict[ticker, date | None] for each instrument ticker, the max
        date in ohlcv_daily, or None if the ticker has no OHLCV rows yet
        """
        sql = """
        SELECT
            i.ticker,
            MAX(o.date) AS last_date
        FROM instrument AS i
        LEFT JOIN ohlcv_daily AS o
            on o.instrument_id = i.id
        GROUP BY i.ticker
        ORDER BY i.ticker;
        """

        with self.conn.cursor(row_factory=tuple_row) as cur:
            cur.execute(sql)
            rows: list[tuple[str, date | None]] = cur.fetchall()

        return dict(rows)

    def list_active_tickers(self) -> list[str]:
        """
        Returns all tickers currently marked as active in the DB
        """
        sql = """
        SELECT ticker
        FROM instrument
        WHERE is_active = TRUE
        ORDER BY ticker;
        """
        with self.conn.cursor(row_factory=tuple_row) as cur:
            cur.execute(sql)
            rows: list[tuple[str]] = cur.fetchall()
        return [t for (t,) in rows]

    def deactivate_tickers(self, tickers: list[str]) -> int:
        """
        Marks the given tickers as inactive, if currently active

        Returns number of rows updated
        """
        cleaned = sorted({t.strip().upper() for t in tickers if t and t.strip()})
        if not cleaned:
            return 0
        
        sql = """
        UPDATE instrument
        SET is_active = FALSE,
            deactivated_at = CURRENT_DATE
        WHERE ticker = ANY(%s)
            AND is_active = TRUE;
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (cleaned,))
            affected = cur.rowcount

        self.conn.commit()
        return 0 if affected is None or affected < 0 else int(affected)


    def list_tickers_with_min_ohlcv_days(self,
                                         min_days: int,
                                         *,
                                         end_date: date | None = None,
                                         ) -> list[str]:
        """
        Returns all tickers that have at least min_days OHLCV rows in the 
        inclusive data range. where start_date = end_date - min_days-1

        Note:
        - This counts only trading day rows, not calendar days
        - end date defaults to CURRENT_DATE in sql
        """
        if min_days <= 0:
            raise ValueError("min_days must be > 0")

        if end_date is None:
            with self.conn.cursor(row_factory=tuple_row) as cur:
                cur.execute("SELECT CURRENT_DATE;")
                (end_date_db,) = cur.fetchone()
            end_date = end_date_db

        start_date = end_date - timedelta(days=min_days-1)

        sql = """
        SELECT i.ticker
        FROM instrument AS i
        JOIN ohlcv_daily AS o
        ON o.instrument_id = i.id
        WHERE o.date BETWEEN %s AND %s
        GROUP BY i.ticker
        HAVING COUNT(*) >= %s
        ORDER BY i.ticker;
        """

        with self.conn.cursor(row_factory=tuple_row) as cur:
            cur.execute(sql, (start_date, end_date, min_days))
            rows: list[tuple[str]] = cur.fetchall()

        return [t for (t,) in rows]


    def fetch_adjclose_long(self,
                            tickers: Sequence[str],
                            *,
                            start_date: date,
                            end_date: date,
                            ) -> DataFrame:
        """
        Fetch adjclose as a long dataframe withc olums:
        - ticker (str), date(datetime64 or date) adjclose(float)
        """
        cleaned = sorted({t.strip().upper() for t in tickers if t and t.strip()})
        if not cleaned:
            return pd.DataFrame(columns=["ticker", "date", "adjclose"])

