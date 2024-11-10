from src.ticker import Ticker
import yfinance as yf
from pathlib import Path
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta
import gc


class WriteError(Exception):
    pass


class Ichimoku:
    def __init__(
        self,
        path: Path,
        tickers="SPY",
        period="1y",
        interval="1d",
        conversion_window=9,
        baseline_window=26,
        span_window=52,
        volume: bool = True,
        plot=True,
        from_path=False,
    ):
        self.path = path
        _tickers = tickers if isinstance(tickers, list) else tickers.replace(",", " ").split()
        self._tickers = [_ticker.upper() for _ticker in _tickers]
        self.period = period
        self.interval = interval
        self.conversion_window = conversion_window
        self.baseline_window = baseline_window
        self.span_window = span_window
        self.volume = volume
        self.plot = plot
        self.from_path = from_path

    def add_features(self, tickers):
        dict_of_tickers = {}
        if self.from_path:
            t = Ticker(self.path, tickers)
            tickers_dict = t.ticker_to_df()
            for ticker in tickers:
                # use ticker download with flush old data, causing previous downloaded date ranges to be used
                df = tickers_dict[ticker].set_index("Date")
                dict_of_tickers[ticker] = self._calculate_features(df)
        else:
            for ticker in tickers:
                df = yf.download(
                    tickers=ticker,
                    period=self.period,
                    interval=self.interval,
                    multi_level_index=False,
                )
                dict_of_tickers[ticker] = self._calculate_features(df)
        return dict_of_tickers

    def plot_ichimoku(self, df, name="Candlestick"):
        trace_dict = {}
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            subplot_titles=("", ""),
            row_heights=(1000, 400),
            vertical_spacing=0.005,
        )

        def _fill_color(df):
            dfs = []
            df["group"] = df["label"].ne(df["label"].shift()).cumsum()
            df = df.groupby("group")

            for name, data in df:
                dfs.append(data)

            for df in dfs:
                fig.add_traces(
                    go.Scatter(
                        x=df.index,
                        y=df.SpanA,
                        line=dict(color="rgba(0,0,0,0)"),
                        showlegend=False,
                    )
                )

                fig.add_traces(
                    go.Scatter(
                        x=df.index,
                        y=df.SpanB,
                        line=dict(color="rgba(0,0,0,0)"),
                        fill="tonexty",
                        fillcolor=(
                            "rgba(0,250,0,0.2)" if df["label"].iloc[0] >= 1 else "rgba(250,0,0,0.2)"
                        ),
                        showlegend=False,
                    )
                )

        # determine non trading day gaps in plots
        alldays = set(
            df.index[0] + timedelta(x)
            for x in range((df.index[len(df.index) - 1] - df.index[0]).days)
        )
        missing = sorted(set(alldays) - set(df.index))

        df["label"] = np.where(df["SpanA"] > df["SpanB"], 1, 0)
        if self.volume:
            green_volume_df = df[df["Close"] > df["Open"]]
            red_volume_df = df[df["Close"] < df["Open"]]
            df["Volume_MA20"] = df["Volume"].rolling(window=20).mean()

        candle = go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name=name,
        )
        baseline = go.Scatter(
            x=df.index,
            y=df["Baseline"],
            line=dict(color="pink", width=2),
            name="Baseline",
        )
        conversion = go.Scatter(
            x=df.index,
            y=df["Conversion"],
            line=dict(color="black", width=1),
            name="Conversion",
        )
        lagging = go.Scatter(
            x=df.index,
            y=df["Lagging"],
            line=dict(color="purple", width=2, dash="dot"),
            name="Lagging",
        )
        span_a = go.Scatter(
            x=df.index,
            y=df["SpanA"],
            line=dict(color="green", width=2, dash="dot"),
            name="Span A",
        )
        span_b = go.Scatter(
            x=df.index,
            y=df["SpanB"],
            line=dict(color="red", width=1, dash="dot"),
            name="Span B",
        )

        if self.volume:
            red_volume = go.Bar(
                x=red_volume_df.index,
                y=red_volume_df.Volume,
                showlegend=False,
                marker_color="red",
                name="Red Volume",
            )
            black_volume = go.Bar(
                x=green_volume_df.index,
                y=green_volume_df.Volume,
                showlegend=False,
                marker_color="black",
                name="Black Volume",
            )
            ma20_volume = go.Scatter(
                x=df.index,
                y=df["Volume_MA20"],
                mode="lines",
                name="Volume MA20",
                line=dict(color="blue"),
            )

        fig.add_trace(candle, row=1, col=1)
        fig.add_trace(baseline, row=1, col=1)
        fig.add_trace(conversion, row=1, col=1)
        fig.add_trace(lagging, row=1, col=1)
        fig.add_trace(span_a, row=1, col=1)
        fig.add_trace(span_b, row=1, col=1)
        trace_dict["candle"] = candle
        trace_dict["baseline"] = baseline
        trace_dict["conversion"] = conversion
        trace_dict["lagging"] = lagging
        trace_dict["span_a"] = span_a
        trace_dict["span_b"] = span_b

        if self.volume:
            fig.add_trace(red_volume, row=2, col=1)
            fig.add_trace(black_volume, row=2, col=1)
            fig.add_trace(ma20_volume, row=2, col=1)
            trace_dict["red_volume"] = red_volume
            trace_dict["black_volume"] = black_volume
            trace_dict["ma20_volume"] = ma20_volume

        _fill_color(df)

        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list(
                        [
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(count=2, label="2y", step="year", stepmode="backward"),
                            dict(step="all"),
                        ]
                    )
                ),
                rangeslider=dict(visible=not self.volume),
                rangebreaks=[dict(values=missing)],
                type="date",
            )
        )

        del df
        gc.collect()

        if self.plot:
            fig.show()

        return (fig, trace_dict)

    def _calculate_features(self, df):
        high = df["High"].rolling(window=self.conversion_window).max()
        low = df["Low"].rolling(window=self.conversion_window).min()
        df["Conversion"] = (high + low) / 2

        high = df["High"].rolling(window=self.baseline_window).max()
        low = df["Low"].rolling(window=self.baseline_window).min()
        df["Baseline"] = (high + low) / 2

        df["SpanA"] = ((df["Conversion"] + df["Baseline"]) / 2).shift(self.baseline_window)
        high = df["High"].rolling(window=self.span_window).max()
        low = df["Low"].rolling(window=self.span_window).min()
        df["SpanB"] = ((high + low) / 2).shift(self.baseline_window)
        df["Lagging"] = df["Close"].shift(-self.baseline_window)

        df["CloseSpanA"] = np.where(df["Close"] > df["SpanA"], 1, 0)
        df["CloseSpanB"] = np.where(df["Close"] > df["SpanB"], 1, 0)
        df["ConversionBaseline"] = np.where(df["Conversion"] > df["Baseline"], 1, 0)

        del high, low
        gc.collect()

        return df

    @property
    def tickers(self):
        return self._tickers
