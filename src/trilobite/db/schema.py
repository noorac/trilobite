from __future__ import annotations

import psycopg

DDL= """
CREATE TABLE IF NOT EXISTS instrument (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS ohlcv_daily (
    instrument_id BIGINT NOT NULL REFERENCES instrument(id) ON DELETE CASCADE,
    date DATE NOT NULL,

    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    adjclose NUMERIC,

    volume BIGINT,
    dividends NUMERIC,
    stockstplits NUMERIC,

    PRIMARY KEY (instrument_id, date)

);

CREATE INDEX IF NOT EXISTS idx_ohlcv_daily_date
    ON ohlcv_daily(date);

CREATE INDEX IF NOT EXISTS idx_instrument_ticker
    ON instrument(ticker);
"""

def create_schema(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(DDL)
    conn.commit()
