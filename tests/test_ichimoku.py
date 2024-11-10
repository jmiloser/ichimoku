import pytest
from src.ichimoku import Ichimoku
from src.ticker import Ticker


def test_ichimoku_cols_to_ticker(data_path, ticker, ichimoku_columns):
    col = ichimoku_columns
    ichimoku = Ichimoku(data_path, ticker)
    dict_of_tickers = ichimoku.add_features(ichimoku.tickers)
    for ticker in ichimoku.tickers:
        df = dict_of_tickers[ticker]
        assert col in df.columns


def test_ichimoku_cols_to_tickers(data_path, tickers, ichimoku_columns):
    col = ichimoku_columns
    ichimoku = Ichimoku(data_path, tickers)
    dict_of_tickers = ichimoku.add_features(ichimoku.tickers)
    for ticker in ichimoku.tickers:
        df = dict_of_tickers[ticker]
        assert col in df.columns


@pytest.mark.plot
def test_ichimoku_plot(data_path, tickers):
    ichimoku = Ichimoku(data_path, tickers, period="2y")
    dict_of_tickers = ichimoku.add_features(ichimoku.tickers)
    for ticker in ichimoku.tickers:
        ichimoku.plot_ichimoku(dict_of_tickers[ticker], ticker)


@pytest.mark.plot
def test_ichimoku_plot_without_volume(data_path, ticker):
    ichimoku = Ichimoku(data_path, ticker, volume=False)
    dict_of_tickers = ichimoku.add_features(ichimoku.tickers)
    for ticker in ichimoku.tickers:
        ichimoku.plot_ichimoku(dict_of_tickers[ticker], ticker)


@pytest.mark.plot
def test_ichimoku_without_plots(data_path, tickers):
    ichimoku = Ichimoku(data_path, tickers, plot=False)
    dict_of_tickers = ichimoku.add_features(ichimoku.tickers)
    for ticker in ichimoku.tickers:
        ichimoku.plot_ichimoku(dict_of_tickers[ticker], ticker)


@pytest.mark.plot
def test_ichimoku_plot_one_ticker_from_path(data_path, ticker, start_datetime, current_datetime):
    # download to temp dir
    _tickers = Ticker(data_path, ticker, start_datetime, current_datetime)
    _tickers.download_to_csv()

    ichimoku = Ichimoku(data_path, ticker, from_path=True)
    dict_of_tickers = ichimoku.add_features(ichimoku.tickers)
    for ticker in ichimoku.tickers:
        ichimoku.plot_ichimoku(dict_of_tickers[ticker], ticker)


@pytest.mark.skip
def test_ichimoku_plot_from_path(data_path, tickers, start_datetime, current_datetime):
    # download to temp dir
    _tickers = Ticker(data_path, tickers, start_datetime, current_datetime)
    _tickers.download_to_csv()

    ichimoku = Ichimoku(data_path, tickers, from_path=True)
    dict_of_tickers = ichimoku.add_features(ichimoku.tickers)
    for ticker in ichimoku.tickers:
        ichimoku.plot_ichimoku(dict_of_tickers[ticker], ticker)
