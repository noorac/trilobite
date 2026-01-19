from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

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
    conn: psycopg.Connection

    def ensure_instrument(self, ticker: str) -> int:
        ticker = ticker.strip().upper()
        if not ticker:
            raise ValueError("Ticker cannot be empty")

        with self.conn.cursor(row_factory=tuple_row) as cur:
            cur.execute(
                """
                INSERT INTO instrument (ticker)
                VALUES (%s)
                ON CONFLICT (ticker) DO UPDATE SET ticker = EXCLUDED.ticker
                RETURNING idf;
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
        Given an instrument_id, upserts daily OHLCV rows
        Expects df columns: date, open, high, low, close, adjclose, volume,
        dividends, stocksplits
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
        
        sql = 
        """
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


