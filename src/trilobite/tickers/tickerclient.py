import urllib.request
import json


class TickerClient:
    """
    Gets updated data online about which tickers exist on the market as of 
    the last updated day of the source.
    """

    NASDAQ_URL : str = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/refs/heads/main/nasdaq/nasdaq_tickers.json"
    NYSE_URL : str = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/refs/heads/main/nyse/nyse_tickers.json"
    AMEX_URL : str = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/refs/heads/main/amex/amex_tickers.json"

    def get_todays_tickers(self) -> list[str]:
        """
        Fetches and organizes the stock market ticker lists into one big list
        """
        def _fetch(url: str) -> list[str]:
            with urllib.request.urlopen(url) as response:
                tickers: list[str] = json.load(response)
            # Sometimes the source uses ^ instead of - in the tickers
            return [t.replace("^", "-").strip().upper() for t in tickers if t]

        nasdaq = _fetch(self.NASDAQ_URL)
        nyse = _fetch(self.NYSE_URL)
        amex = _fetch(self.AMEX_URL)

        seen: set[str] = set()
        combined: list[str] = []
        for t in nasdaq + nyse + amex:
            if t and t not in seen:
                seen.add(t)
                combined.append(t)
        return combined
