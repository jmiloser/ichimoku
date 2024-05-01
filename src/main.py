from ticker import Ticker
from src.ichimoku import Ichimoku
from pathlib import Path


TICKERS = "AAPL NVDA QQQ ERX"
data_path = Path("data/holdings")


def download_tickers(path: Path, tickers):
    Ticker(path=data_path, tickers=TICKERS).download_to_csv()


def plot_ichimoku_from_directory(path: Path, tickers):
    ichimoku = Ichimoku(path=data_path, tickers=TICKERS, from_path=True)
    dict_of_tickers = ichimoku.add_features(ichimoku.tickers)
    for ticker in ichimoku.tickers:
        ichimoku.plot_ichimoku(dict_of_tickers[ticker], ticker)


def main():

    download_tickers(path=data_path, tickers=TICKERS)
    plot_ichimoku_from_directory(data_path, TICKERS)


if __name__ == "__main__":
    main()
