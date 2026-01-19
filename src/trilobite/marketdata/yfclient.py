from datetime import date
import yfinance as yf
from pandas import DataFrame

class YFClient:
    """
    Yahoo Finance client based on yfinance. 

    This is intentionally small: it does no validation and no persistence. It 
    simply requests and normalizes the returned DataFrame.
    """
    def get_ohlcv(self, ticker: str, start_date: date) -> DataFrame:
        """
        Download daily OHLCV data for ticker from start_date until today.

        Params:
        - ticker: Ticker symbol accepted by Yahoo Finance
        - start_date: First day(inclusive) of the history request

        Returns:
        - pandas.DataFrame containing the data
        """
        t = yf.Ticker(ticker)
        df = t.history(
            start=start_date,
            end=None,
            interval="1d",
            actions=True,
            auto_adjust=False,
        )
        #turn date into it's own column, and rename columns to lowercase
        df = (
            df
            .reset_index()
            .rename(columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adjclose",
                "Volume": "volume",
                "Dividends": "dividends",
                "Stock Splits": "stocksplits",
                })
        )
        #strip the time and leave the date
        df["date"] = df["date"].dt.date
        return df
