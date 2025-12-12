"""EMA crossover analysis helpers.

These functions were extracted from marimo notebooks so they can be imported from
marimo cells. In marimo, module-level definitions may not be available to the
runtime unless defined inside a cell.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf


def calculate_rsl(close: pd.Series, length: int = 26) -> pd.Series:
    """Relative Strength Levy (RSL) proxy as the ratio of short-term to long-term EMA."""

    ema_short = close.ewm(span=length // 2, adjust=False).mean()
    ema_long = close.ewm(span=length, adjust=False).mean()
    return ema_short / ema_long


def ema_crossover_signals(close: pd.Series, short_span: int = 12, long_span: int = 26):
    """Generate buy/sell boolean Series based on EMA crossovers."""

    ema_short = close.ewm(span=short_span, adjust=False).mean()
    ema_long = close.ewm(span=long_span, adjust=False).mean()

    signal = pd.Series(0, index=close.index)
    signal.loc[ema_short > ema_long] = 1
    signal.loc[ema_short < ema_long] = -1

    buy_signals = signal.diff() == 2
    sell_signals = signal.diff() == -2
    return buy_signals, sell_signals


def generate_signals(asset: str = "BTC-USD", start_date: str = "2023-01-01", end_date: str | None = None) -> None:
    """Download asset data, calculate RSL and EMA cross signals, and plot."""

    if end_date is None:
        end_date = pd.Timestamp.today().strftime("%Y-%m-%d")

    data = yf.Ticker(asset).history(start=start_date, end=end_date)
    close = data["Close"]
    rsl = calculate_rsl(close)
    buy_signals, sell_signals = ema_crossover_signals(close)

    plt.figure(figsize=(16, 8))
    plt.plot(close.index, close, label="Close Price", linewidth=2, color="deepskyblue")
    plt.plot(rsl.index, rsl, label="Relative Strength Levy (proxy)", color="orange", alpha=0.6)
    plt.plot(close.index[buy_signals.values], close[buy_signals.values], "^", markersize=12, color="green", label="Buy Signal")
    plt.plot(close.index[sell_signals.values], close[sell_signals.values], "v", markersize=12, color="red", label="Sell Signal")
    plt.title(f"{asset} Buy/Sell Signals based on RSL and EMA Crossings")
    plt.legend()
    plt.grid(True)
    plt.show()


def fetch_data(asset: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Downloads asset data."""

    print(f"Fetching data for {asset} from {start_date} to {end_date}...")
    data = yf.Ticker(asset).history(start=start_date, end=end_date)
    return data.ffill().dropna()


def ema_crossover_signals_position(close: pd.Series, short_span: int = 12, long_span: int = 26):
    """Generate position signals (1 for Long, 0 for Cash) based on EMA crossovers."""

    ema_short = close.ewm(span=short_span, adjust=False).mean()
    ema_long = close.ewm(span=long_span, adjust=False).mean()

    signal = pd.Series(0, index=close.index)
    signal.loc[ema_short > ema_long] = 1
    signal.loc[ema_short < ema_long] = 0

    buy_signals = signal.diff() == 1
    sell_signals = signal.diff() == -1

    return signal, buy_signals, sell_signals


def calculate_metrics(returns: pd.Series, cumulative_wealth: pd.Series, name: str) -> dict[str, str]:
    """Key performance metrics for a return series."""

    total_return = (cumulative_wealth.iloc[-1] / cumulative_wealth.iloc[0]) - 1
    years = (cumulative_wealth.index[-1] - cumulative_wealth.index[0]).days / 365.25
    cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
    volatility = returns.std() * np.sqrt(252)

    peak = cumulative_wealth.expanding(min_periods=1).max()
    drawdown = (cumulative_wealth / peak) - 1
    max_drawdown = drawdown.min()

    sharpe_ratio = cagr / volatility if volatility != 0 else np.nan

    return {
        "Strategy": name,
        "Total Return (%)": f"{total_return * 100:.2f}%",
        "CAGR (%)": f"{cagr * 100:.2f}%",
        "Annual Volatility (%)": f"{volatility * 100:.2f}%",
        "Max Drawdown (%)": f"{max_drawdown * 100:.2f}%",
        "Sharpe Ratio": f"{sharpe_ratio:.2f}",
    }


def plot_signals(data: pd.DataFrame, asset: str) -> None:
    """Plot asset price with trade signals."""

    plt.figure(figsize=(16, 8))
    close = data["Close"]
    rsl = data["RSL"]
    buy_signals = data["Buy_Signal"]
    sell_signals = data["Sell_Signal"]

    plt.plot(close.index, close, label="Close Price", linewidth=2, color="deepskyblue")
    plt.plot(
        rsl.index,
        rsl * close.mean(),
        label="Relative Strength Levy (Scaled Proxy)",
        color="orange",
        alpha=0.6,
        linestyle="--",
    )

    plt.plot(close.index[buy_signals.values], close[buy_signals.values], "^", markersize=12, color="green", label="Buy Signal")
    plt.plot(close.index[sell_signals.values], close[sell_signals.values], "v", markersize=12, color="red", label="Sell Signal")

    plt.title(f"{asset} Buy/Sell Signals based on EMA Crossings")
    plt.legend()
    plt.grid(True)
    plt.show()


def run_single_asset_analysis(
    asset: str = "BTC-USD",
    start_date: str = "2023-01-01",
    end_date: str | None = None,
    initial_capital: int = 10_000,
):
    """EMA Crossover vs Buy & Hold backtest for a single asset."""

    if end_date is None:
        end_date = pd.Timestamp.today().strftime("%Y-%m-%d")

    data = fetch_data(asset, start_date, end_date)

    data["RSL"] = calculate_rsl(data["Close"])
    data["Position"], data["Buy_Signal"], data["Sell_Signal"] = ema_crossover_signals_position(data["Close"])

    data["Strategy_Return"] = data["Close"].pct_change() * data["Position"].shift(1)
    data["BuyHold_Return"] = data["Close"].pct_change()

    data["Strategy_Cumulative"] = (1 + data["Strategy_Return"].fillna(0)).cumprod() * initial_capital
    data["BuyHold_Cumulative"] = (1 + data["BuyHold_Return"].fillna(0)).cumprod() * initial_capital

    data = data.dropna(subset=["Strategy_Cumulative", "BuyHold_Cumulative"])

    metrics_strategy = calculate_metrics(data["Strategy_Return"].dropna(), data["Strategy_Cumulative"].dropna(), "EMA Crossover Model")
    metrics_buyhold = calculate_metrics(data["BuyHold_Return"].dropna(), data["BuyHold_Cumulative"].dropna(), "Buy and Hold")

    comparison_df = pd.DataFrame([metrics_strategy, metrics_buyhold])

    print("\n## 🚀 Performance Metrics Comparison")
    try:
        print(comparison_df.to_markdown(index=False))
    except Exception:
        # pandas uses the optional `tabulate` dependency for to_markdown
        print(comparison_df.to_string(index=False))

    print("\n## 🖼️ Trade Signals Visualization")
    plot_signals(data, asset)

    print("\n## 💰 Cumulative Wealth Comparison")
    plt.figure(figsize=(14, 7))
    plt.plot(data["BuyHold_Cumulative"], label="Buy and Hold", color="blue", linewidth=3)
    plt.plot(data["Strategy_Cumulative"], label="EMA Crossover Model", color="darkorange", linewidth=2, linestyle="--")
    plt.title(f"Cumulative Wealth: Active Strategy vs. Buy and Hold ({asset})")
    plt.xlabel("Date")
    plt.ylabel(f"Portfolio Value (Starting at ${initial_capital:,})")
    plt.legend()
    plt.grid(axis="y", alpha=0.5)
    plt.show()

    return data, comparison_df


def plot_cumulative_wealth(data: pd.DataFrame, asset: str, initial_capital: int = 10_000) -> None:
    plt.figure(figsize=(14, 5))
    plt.plot(data["BuyHold_Cumulative"], label="Buy and Hold", color="blue", linewidth=3)
    plt.plot(data["Strategy_Cumulative"], label="EMA Crossover Model", color="darkorange", linewidth=2, linestyle="--")
    plt.title(f"{asset}: Cumulative Wealth Comparison (Start: ${initial_capital:,})")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(axis="y", alpha=0.5)
    plt.show()


def run_analysis_for_asset(asset: str, start_date: str, end_date: str, initial_capital: int = 10_000):
    data = fetch_data(asset, start_date, end_date)
    if data.empty:
        print(f"Skipping {asset}: Could not retrieve historical data.")
        return None

    data["RSL"] = calculate_rsl(data["Close"])
    data["Position"], data["Buy_Signal"], data["Sell_Signal"] = ema_crossover_signals_position(data["Close"])

    data["Strategy_Return"] = data["Close"].pct_change() * data["Position"].shift(1)
    data["BuyHold_Return"] = data["Close"].pct_change()

    data["Strategy_Cumulative"] = (1 + data["Strategy_Return"].fillna(0)).cumprod() * initial_capital
    data["BuyHold_Cumulative"] = (1 + data["BuyHold_Return"].fillna(0)).cumprod() * initial_capital

    data = data.dropna(subset=["Strategy_Cumulative", "BuyHold_Cumulative"])

    metrics_strategy = calculate_metrics(data["Strategy_Return"].dropna(), data["Strategy_Cumulative"].dropna(), "EMA Crossover Model")
    metrics_buyhold = calculate_metrics(data["BuyHold_Return"].dropna(), data["BuyHold_Cumulative"].dropna(), "Buy and Hold")
    comparison_df = pd.DataFrame([metrics_strategy, metrics_buyhold])

    print(f"\n# 📊 Results for {asset}\n")
    print("## 🚀 Performance Metrics Comparison")
    try:
        print(comparison_df.to_markdown(index=False))
    except Exception:
        print(comparison_df.to_string(index=False))
    print("\n-----------------------------------\n")

    print("\n## 🖼️ Trade Signals Visualization")
    plot_signals(data, asset)

    print("\n## 💰 Cumulative Wealth Comparison")
    plot_cumulative_wealth(data, asset, initial_capital)

    print("\n\n" + "=" * 80 + "\n\n")

    return data, comparison_df


def run_multi_asset_analysis(
    assets: list[str] | None = None,
    start_date: str = "2023-01-01",
    end_date: str | None = None,
    initial_capital: int = 10_000,
):
    if assets is None:
        assets = ["SPY", "QQQ", "DIA"]

    if end_date is None:
        end_date = pd.Timestamp.today().strftime("%Y-%m-%d")

    print("# 🚀 Multi-Asset Trading Strategy Analysis\n")
    print(f"Analyzing: {', '.join(assets)} starting from {start_date}")

    results = {}
    for asset in assets:
        result = run_analysis_for_asset(asset, start_date, end_date, initial_capital)
        if result is not None:
            results[asset] = result

    print("Analysis Complete.")
    return results
