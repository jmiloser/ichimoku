import pytest
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
from src.ticker import Ticker

"""
pytest -s tests/test_utils.py::test_ticker_info
pytest -s tests/test_utils.py::test_ticker_info tests/test_utils.py::test_ticker_passed_as_list
"""

# current_datetime = datetime.now()
# start_datetime = current_datetime - timedelta(days=15)
# future_datetime = current_datetime + timedelta(days=15)


def test_path_fixture(data_path):
    assert data_path.is_dir()


def test_save_read_ticker(data_path, tickers, start_datetime, current_datetime):
    _tickers = Ticker(data_path, tickers, start_datetime, current_datetime)
    _tickers.download_to_csv()
    tickers_dict = _tickers.ticker_to_df()
    for ticker in tickers.split(" "):
        file_path = data_path / f"{ticker}.csv"
        assert file_path.is_file()
        assert len(tickers_dict[ticker]) > 0
        assert tickers_dict[ticker].Date.dtype == "datetime64[ns]"


def test_max_date_is_most_recent_trading_date(
    data_path, tickers, current_datetime, start_datetime, future_datetime
):
    _tickers = Ticker(data_path, tickers, start_datetime, future_datetime)
    _tickers.download_to_csv()
    tickers_dict = _tickers.ticker_to_df()
    for ticker in tickers.split(" "):
        assert tickers_dict[ticker].Date.iloc[-1] <= pd.to_datetime(current_datetime.date())


def test_ticker_passed_as_list_or_str(data_path):
    ticker_list_test = Ticker(data_path, ["aapl", "F"])
    ticker_list_test.download_to_csv()
    assert Path(f"{data_path}/AAPL.csv").is_file()

    ticker_list_test = Ticker(data_path, ["sPy"])
    ticker_list_test.download_to_csv()
    assert Path(f"{data_path}/SPY.csv").is_file()

    ticker_list_test = Ticker(data_path, "MSFT nVda")
    ticker_list_test.download_to_csv()
    assert Path(f"{data_path}/MSFT.csv").is_file()
    assert Path(f"{data_path}/NVDA.csv").is_file()

    ticker_list_test = Ticker(data_path, "tQQQ")
    ticker_list_test.download_to_csv()
    assert Path(f"{data_path}/TQQQ.csv").is_file()


@pytest.mark.skip
def test_add_to_existing_ticker(data_path, ticker, current_datetime):
    # download 10 days of history 10 days before current date
    start = current_datetime - timedelta(days=20)
    end = current_datetime - timedelta(days=10)
    _ticker = Ticker(data_path, ticker, start, end)
    _ticker.download_to_csv()
    _ticker_dict = _ticker.ticker_to_df()
    assert _ticker_dict[ticker].Date.iloc[-1] <= pd.to_datetime(end.date())

    # update ticker to current day without downloading
    _ticker.update()
    _ticker_dict = _ticker.ticker_to_df()
    assert _ticker_dict[ticker].Date.iloc[-1] > pd.to_datetime(end.date())


def test_add_to_existing_ticker(data_path, ticker, current_datetime):
    # download 10 days of history 10 days before current date
    start = current_datetime - timedelta(days=20)
    end = current_datetime - timedelta(days=10)
    _ticker = Ticker(data_path, ticker, start, end)
    _ticker.download_to_csv()
    _ticker_dict = _ticker.ticker_to_df()

    # Ensure dates are timezone-naive
    _ticker_dict[ticker]["Date"] = pd.to_datetime(_ticker_dict[ticker]["Date"]).dt.tz_localize(None)
    end_naive = pd.to_datetime(end.date()).tz_localize(None)
    assert _ticker_dict[ticker].Date.iloc[-1] <= end_naive

    # update ticker to current day without downloading
    _ticker.update()
    _ticker_dict = _ticker.ticker_to_df()
    _ticker_dict[ticker]["Date"] = pd.to_datetime(_ticker_dict[ticker]["Date"]).dt.tz_localize(None)
    current_datetime_naive = pd.to_datetime(current_datetime).tz_localize(None)
    assert _ticker_dict[ticker].Date.iloc[-1] > end_naive
    assert _ticker_dict[ticker].Date.iloc[-1] <= current_datetime_naive


def test_flush_existing_data(data_path, ticker, current_datetime):
    # download 40 days of history from current date, without flushing
    start = current_datetime - timedelta(days=40)
    _ticker = Ticker(data_path, ticker, start)
    _ticker.download_to_csv(flush=False)
    _ticker_dict = _ticker.ticker_to_df()
    assert len(_ticker_dict[ticker]) > 10

    # download 10 days of history from current date, with flushing
    start = current_datetime - timedelta(days=10)
    _ticker = Ticker(data_path, ticker, start)
    _ticker.download_to_csv(flush=True)
    _ticker_dict = _ticker.ticker_to_df()
    assert len(_ticker_dict[ticker]) <= 10

    # download 40 days of history from current date, without flushing
    start = current_datetime - timedelta(days=40)
    _ticker = Ticker(data_path, ticker, start)
    _ticker.download_to_csv(flush=False)
    _ticker_dict = _ticker.ticker_to_df()
    assert len(_ticker_dict[ticker]) > 10
