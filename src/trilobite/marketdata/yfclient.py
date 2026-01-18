from datetime import date
import yfinance as yf
from pandas import DataFrame

class YFClient:
    """
    Gets the data
    """
    def get_ohlcv(self, ticker: str, start_date: date) -> DataFrame:
        """
        Gets the data from the date spesified until today, if no date object 
        is sent, it defaults to 1900, which is most likely max
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
