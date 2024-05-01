import pytest
from pathlib import Path
from datetime import datetime, timedelta

# def pytest_addoption(parser):
#     parser.addoption("--workflow_options", action="store", default="-rA -v", help="Options used in github workflow.")
#     parser.addoption("--pytest_options", action="store", default="-rA -v --html=./tests/report.html --alluredir=./tests/allure-report", help="Options for reports.")


# def pytest_addoption(parser):
#     parser.addoption("--regen", action="store_true", help="Specify whether to regenerate persistent ticker for testing.")


@pytest.fixture(
    params=[
        "High",
        "Low",
        "Conversion",
        "Baseline",
        "SpanA",
        "SpanB",
        "Lagging",
        "CloseSpanA",
        "CloseSpanB",
        "ConversionBaseline",
    ]
)
def ichimoku_columns(request):
    return request.param


@pytest.fixture
def data_path(tmpdir):
    return Path(tmpdir)


@pytest.fixture
def tickers():
    return "AAPL GOOG ERX BNKU"


@pytest.fixture
def ticker():
    return "SPY"


@pytest.fixture
def current_datetime():
    return datetime.now()


@pytest.fixture
def start_datetime(current_datetime):
    return current_datetime - timedelta(days=15)


@pytest.fixture
def future_datetime(current_datetime):
    return current_datetime + timedelta(days=15)
