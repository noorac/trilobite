from __future__ import annotations

ENSURE_INSTRUMENT = """
INSERT INTO instrument (ticker, is_active, last_seen, deactivated_at)
VALUES (%s, TRUE, CURRENT_DATE, NULL)
ON CONFLICT (ticker) DO UPDATE SET
    ticker = EXCLUDED.ticker,
    is_active = TRUE,
    last_seen = CURRENT_DATE,
    deactivated_at = NULL
RETURNING id;
"""

LIST_ACTIVE_TICKERS = """
SELECT ticker
FROM instrument
WHERE is_active = TRUE
ORDER BY ticker;
"""

DEACTIVATE_TICKERS = """
UPDATE instrument
SET is_active = FALSE,
    deactivated_at = CURRENT_DATE
WHERE ticker = ANY(%s)
  AND is_active = TRUE;
"""

LAST_OHLCV_DATE_BY_TICKER = """
SELECT
    i.ticker,
    MAX(o.date) AS last_date
FROM instrument AS i
LEFT JOIN ohlcv_daily AS o ON o.instrument_id = i.id
GROUP BY i.ticker
ORDER BY i.ticker;
"""

LAST_OHLCV_DATE_FOR_TICKER = """
SELECT MAX(o.date) AS last_date
FROM instrument AS i
JOIN ohlcv_daily AS o ON o.instrument_id = i.id
WHERE i.ticker = %s;
"""

UPSERT_OHLCV_DAILY = """
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
    stocksplits = EXCLUDED.stocksplits;
"""

FETCH_ADJCLOSE_LONG = """
SELECT i.ticker, o.date, o.adjclose
FROM instrument AS i
JOIN ohlcv_daily AS o ON o.instrument_id = i.id
WHERE i.ticker = ANY(%s)
  AND o.date BETWEEN %s AND %s
ORDER BY i.ticker, o.date;
"""

LIST_TICKERS_WITH_MIN_OHLCV_DAYS = """
SELECT i.ticker
FROM instrument AS i
JOIN ohlcv_daily AS o ON o.instrument_id = i.id
WHERE o.date BETWEEN %s AND %s
GROUP BY i.ticker
HAVING COUNT(*) >= %s
ORDER BY i.ticker;
"""

FETCH_ADJCLOSE_SERIES_BETWEEN = """
SELECT o.date, o.adjclose
FROM instrument AS i
JOIN ohlcv_daily AS o ON o.instrument_id = i.id
WHERE i.ticker = %s
  AND o.date BETWEEN %s AND %s
ORDER BY o.date;
"""

FETCH_ADJCLOSE_SERIES_LEQ = """
SELECT o.date, o.adjclose
FROM instrument AS i
JOIN ohlcv_daily AS o ON o.instrument_id = i.id
WHERE i.ticker = %s
  AND o.date <= %s
ORDER BY o.date;
"""

