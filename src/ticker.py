import warnings
import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

TODAY = datetime.now()
START_DATE = "2017-08-01"
END_DATE = TODAY


class Ticker:
    def __init__(self, path: Path, tickers, start_date=START_DATE, end_date=END_DATE):
        if not isinstance(path, Path):
            warnings.warn(
                "Argument should be a pathlib.Path object. Casting to Path object.",
                category=Warning,
            )
            self.path = Path(path)
        else:
            self.path = path
        self.start_date = start_date
        self.end_date = end_date
        tickers = tickers if isinstance(tickers, list) else tickers.replace(",", " ").split()
        self.tickers = [ticker.upper() for ticker in tickers]

    def download_to_csv(self, flush=True):
        if flush:
            for file in self.path.glob("*.csv"):
                file.unlink(missing_ok=False)
        data = yf.download(self.tickers, self.start_date, self.end_date, group_by="ticker")
        if isinstance(data.columns, pd.MultiIndex):
            for ticker in self.tickers:
                data[ticker].reset_index().to_csv(self.path / f"{ticker}.csv", index=False)
        else:
            data.reset_index().to_csv(self.path / f"{self.tickers[0]}.csv", index=False)

    def update(self):
        _tickers = self.ticker_to_df()
        for ticker in self.tickers:
            last_date = _tickers[ticker].Date.iloc[-1].date()
            data = yf.download(
                ticker,
                last_date + timedelta(days=1),
                TODAY,
                group_by="ticker",
                multi_level_index=False,
            ).reset_index()
            _existing_ticker = pd.read_csv(f"{self.path}/{ticker}.csv", parse_dates=["Date"])
            data = pd.concat([_existing_ticker, data], ignore_index=True)
            data.to_csv(self.path / f"{self.tickers[0]}.csv", index=False)

    def ticker_to_df(self):
        tickers = {}
        for ticker in self.tickers:
            try:
                tickers[ticker] = pd.read_csv(f"{self.path}/{ticker}.csv", parse_dates=["Date"])
            except FileNotFoundError as fe:
                print(f"Ticker: {ticker} not downloaded. {fe}")
                continue
        return tickers
