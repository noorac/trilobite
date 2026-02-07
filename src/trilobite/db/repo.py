from __future__ import annotations

import logging
from datetime import date, timedelta
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import pandas as pd
import psycopg
from psycopg.rows import tuple_row
from pandas import DataFrame, to_numeric
from torch import TupleType

from trilobite.utils.utils import period_to_date
from trilobite.db import queries as q

logger = logging.getLogger(__name__)

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

    #Local methods
    def _execute(self, sql: str, params: tuple | None = None) -> int:
        with self.conn.cursor() as cur:
            cur.execute(sql, params or ()) #type: ignore[]
            rc = cur.rowcount
        self.conn.commit()
        return 0 if rc is None or rc < 0 else int(rc)

    def _executemany(self, sql: str, rows) -> int:
        with self.conn.cursor() as cur:
            cur.executemany(sql, rows)#type: ignore[]
            rc = cur.rowcount
        self.conn.commit()
        return 0 if rc is None or rc < 0 else int(rc)

    def _fetchone(self, sql: str, params: tuple | None = None) -> tuple[Any, ...] | None:
        with self.conn.cursor(row_factory=tuple_row) as cur:
            cur.execute(sql, params or ())#type: ignore[]
            return cur.fetchone()

    def _fetchall(self, sql: str, params: tuple | None = None) -> list[tuple[Any, ...]]:
        with self.conn.cursor(row_factory=tuple_row) as cur:
            cur.execute(sql, params or ())#type: ignore[]
            return cur.fetchall()

    def _scalar(self, sql: str, params: tuple | None = None):
        row = self._fetchone(sql, params)
        return None if row is None else row[0]


    #Local helpers
    def _clean_ticker(self, ticker: str) -> str:
        """
        Strips and capitalizes all letters in a ticker.

        Params:
        -ticker, a string

        Returns:
        - string, ticker
        """
        t = ticker.strip().upper()
        if not t:
            raise ValueError(f"Ticker cannot be empty")
        return t

    def _clean_tickers(self, tickers: Sequence[str]) -> list[str]:
        """
        Strips and capitalizes all letters in a sequence of tickers. 

        Params
        - tickers: a sequence of strings

        Returns
        - List, sorted. 
        """
        return sorted({t.strip().upper() for t in tickers if t and t.strip()})


    # Methods
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
        t = self._clean_ticker(ticker)
        instrument_id = self._scalar(q.ENSURE_INSTRUMENT, (t,))
        if instrument_id is None:
            raise RuntimeError(f"Failed to fetch instrument id after upsert")
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
        return self._executemany(q.UPSERT_OHLCV_DAILY, rows)

    def last_ohlcv_date_for_ticker(self, ticker: str) -> date | None:
        """
        Returns the latest stored OHLCV date for a single ticker
        (as opposed to all tickers)
        """
        t = self._clean_ticker(ticker)
        return self._scalar(q.LAST_OHLCV_DATE_FOR_TICKER, (t,))

    def last_ohlcv_date_for_all_tickers(self) -> dict[str, date | None]:
        """
        Returns the latest stored OHLCV date per ticker

        Returns: a dict[ticker, date | None] for each instrument ticker, the max
        date in ohlcv_daily, or None if the ticker has no OHLCV rows yet
        """
        rows = self._fetchall(q.LAST_OHLCV_DATE_FOR_ALL_TICKERS)
        return {ticker: last_date for (ticker, last_date) in rows}

    def list_active_tickers(self) -> list[str]:
        """
        Returns all tickers currently marked as active in the DB
        """
        return [t for (t,) in self._fetchall(q.LIST_ACTIVE_TICKERS)]

    def deactivate_tickers(self, tickers: list[str]) -> int:
        """
        Marks the given tickers as inactive, if currently active

        Returns number of rows updated
        """
        cleaned = self._clean_tickers(tickers)
        if not cleaned:
            return 0
        return self._execute(q.DEACTIVATE_TICKERS, (cleaned,))

    def fetch_adjclose_long(self, tickers: Sequence[str], *, start_date: date, end_date: date) -> DataFrame:
        """
        Fetch adjclose as a long dataframe withc olums:
        - ticker (str), date(datetime64 or date) adjclose(float)
        """
        logger.debug("Start ..")
        cleaned = self._clean_tickers(tickers)
        if not cleaned:
            return pd.DataFrame(columns=["ticker", "date", "adjclose"]) #type: ignore
        rows = self._fetchall(q.FETCH_ADJCLOSE_LONG, (cleaned, start_date, end_date))
        df = pd.DataFrame(rows, columns = ["ticker", "date", "adjclose"]) #type: ignore
        df["ticker"] = df["ticker"].astype(str)
        df["date"] = pd.to_datetime(df["date"])
        df["adjclose"] = pd.to_numeric(df["adjclose"], errors="coerce")
        logger.debug("End ..")
        return df


    def fetch_adjclose_series(self, ticker: str, period: str) -> DataFrame:
        """
        Fetch a single tickers adjclose sereis from the DB.
        
        Params:
        - ticker: e.g. "AAPL"
        - period: eg.. "30d", "6m"

        Returns:
        - dataframe with columns date and adjclose(float)
        """
        cleaned = self._clean_ticker(ticker)
        end_date = self.last_ohlcv_date_for_ticker(cleaned)
        if end_date is None:
            return pd.DataFrame(columns=["date", "adjclose"]) #type: ignore
        
        start_date, end_date = period_to_date(period, end_date=end_date)

        if start_date is None:
            rows = self._fetchall(q.FETCH_ADJCLOSE_SERIES_LEQ, (cleaned, end_date))
        else:
            rows = self._fetchall(q.FETCH_ADJCLOSE_SERIES_BETWEEN, (cleaned, start_date, end_date))

        df = pd.DataFrame(rows, columns=["date", "adjclose"])#type: ignore
        df["date"] = pd.to_datetime(df["date"])
        df["adjclose"] = pd.to_numeric(df["adjclose"], errors="coerce")
        return df

    def list_tickers_with_full_ohlcv_coverage(self, period: str, *, end_date: date | None = None) -> list[str]:
        """
        Queries the db for a list of tickers that have data for the given 
        period

        Params:
        - period: string, e.g. 3y, 2w, 66d
        - end_date, date, can be sendt the end date if not using today as last
        day

        Returns:
        - list of strings, tickers

        """
        if end_date is None:
            end_date = self._scalar("SELECT CURRENT_DATE;")
            if end_date is None:
                raise RuntimeError("DB returned NULL for CURRENT_DATE")

        start_date, end_date = period_to_date(period, end_date=end_date)
        if start_date is None:
            # “max/all”: coverage doesn't make sense
            # Option: return all active tickers; or require a min start date.
            logger.warning(f"Period needs a start date when comparing tickers, start_date is None")
            raise RuntimeError

        rows = self._fetchall(
            q.LIST_TICKERS_WITH_FULL_COVERAGE_IN_RANGE,
            (start_date, end_date, start_date, end_date),
        )
        return [t for (t,) in rows]

