"""
EMA Crossover Trading Strategy Analysis

This notebook implements an Exponential Moving Average (EMA) Crossover trading strategy
and compares its performance metrics against a simple Buy and Hold strategy.

Three main sections:
1. Basic RSL and EMA Crossover Signal Generation
2. Single Asset Analysis (EMA Crossover vs Buy and Hold)
3. Multi-Asset Analysis (EMA Crossover vs Buy and Hold)
"""

import marimo as mo
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

__generated_with = "0.7.9"
app = mo.App(width="full")

# ============================================================================
# SECTION 1: Basic RSL and EMA Crossover Signal Generation
# ============================================================================

def calculate_rsl(close, length=26):
    """
    Calculate Relative Strength Levy (RSL) as the ratio of short-term to long-term EMA.
    """
    ema_short = close.ewm(span=length//2, adjust=False).mean()
    ema_long = close.ewm(span=length, adjust=False).mean()
    rsl = ema_short / ema_long
    return rsl


def ema_crossover_signals(close, short_span=12, long_span=26):
    """
    Generate buy/sell signals based on EMA crossovers.
    Buy when short EMA crosses above long EMA.
    Sell when short EMA crosses below long EMA.
    """
    ema_short = close.ewm(span=short_span, adjust=False).mean()
    ema_long = close.ewm(span=long_span, adjust=False).mean()
    signal = pd.Series(0, index=close.index)
    signal.loc[ema_short > ema_long] = 1
    signal.loc[ema_short < ema_long] = -1
    buy_signals = (signal.diff() == 2)
    sell_signals = (signal.diff() == -2)
    return buy_signals, sell_signals


def generate_signals(asset='BTC-USD', start_date='2023-01-01', end_date=None):
    """
    Download asset data, calculate RSL and EMA cross signals, and plot.
    """
    if end_date is None:
        end_date = pd.Timestamp.today().strftime('%Y-%m-%d')
    
    data = yf.Ticker(asset).history(start=start_date, end=end_date)
    close = data['Close']
    rsl = calculate_rsl(close)
    buy_signals, sell_signals = ema_crossover_signals(close)
    
    # Plotting
    plt.figure(figsize=(16, 8))
    plt.plot(close.index, close, label='Close Price', linewidth=2, color='deepskyblue')
    plt.plot(rsl.index, rsl, label='Relative Strength Levy (proxy)', color='orange', alpha=0.6)
    plt.plot(close.index[buy_signals.values], close[buy_signals.values], '^', 
             markersize=12, color='green', label='Buy Signal')
    plt.plot(close.index[sell_signals.values], close[sell_signals.values], 'v', 
             markersize=12, color='red', label='Sell Signal')
    plt.title(f'{asset} Buy/Sell Signals based on RSL and EMA Crossings')
    plt.legend()
    plt.grid(True)
    plt.show()


# Example usage for Section 1:
# asset_to_analyze = 'BTC-USD'
# generate_signals(asset=asset_to_analyze)


# ============================================================================
# SECTION 2: Single Asset Analysis - EMA Crossover vs Buy and Hold
# ============================================================================

def fetch_data(asset, start_date, end_date):
    """Downloads asset data."""
    print(f"Fetching data for {asset} from {start_date} to {end_date}...")
    data = yf.Ticker(asset).history(start=start_date, end=end_date)
    return data.ffill().dropna()


def ema_crossover_signals_position(close, short_span=12, long_span=26):
    """
    Generate position signals (1 for Long, 0 for Cash) based on EMA crossovers.
    """
    ema_short = close.ewm(span=short_span, adjust=False).mean()
    ema_long = close.ewm(span=long_span, adjust=False).mean()
    
    # Position: 1 for Long, 0 for Cash
    signal = pd.Series(0, index=close.index)
    signal.loc[ema_short > ema_long] = 1  # Go Long when short EMA > long EMA
    signal.loc[ema_short < ema_long] = 0  # Go to Cash when short EMA < long EMA
    
    # Identify trade entry/exit points (for visualization)
    buy_signals = (signal.diff() == 1)
    sell_signals = (signal.diff() == -1)
    
    return signal, buy_signals, sell_signals


def calculate_metrics(returns, cumulative_wealth, name):
    """
    Calculates key trading metrics: Total Return, CAGR, Volatility, Max Drawdown, and Sharpe Ratio.
    """
    # 1. Total Return
    total_return = (cumulative_wealth.iloc[-1] / cumulative_wealth.iloc[0]) - 1
    
    # 2. CAGR (Annualized Return)
    years = (cumulative_wealth.index[-1] - cumulative_wealth.index[0]).days / 365.25
    cagr = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
    
    # 3. Volatility (Annualized Standard Deviation)
    volatility = returns.std() * np.sqrt(252)
    
    # 4. Max Drawdown
    peak = cumulative_wealth.expanding(min_periods=1).max()
    drawdown = (cumulative_wealth / peak) - 1
    max_drawdown = drawdown.min()
    
    # 5. Sharpe Ratio (Assumes risk-free rate of 0 for simplicity)
    sharpe_ratio = cagr / volatility if volatility != 0 else np.nan
    
    return {
        'Strategy': name,
        'Total Return (%)': f'{total_return * 100:.2f}%',
        'CAGR (%)': f'{cagr * 100:.2f}%',
        'Annual Volatility (%)': f'{volatility * 100:.2f}%',
        'Max Drawdown (%)': f'{max_drawdown * 100:.2f}%',
        'Sharpe Ratio': f'{sharpe_ratio:.2f}'
    }


def plot_signals(data, asset):
    """Plot asset price with trade signals."""
    plt.figure(figsize=(16, 8))
    close = data['Close']
    rsl = data['RSL']
    buy_signals = data['Buy_Signal']
    sell_signals = data['Sell_Signal']
    
    plt.plot(close.index, close, label='Close Price', linewidth=2, color='deepskyblue')
    # RSL is plotted on a scaled version of the price axis for context
    plt.plot(rsl.index, rsl * close.mean(), 
             label='Relative Strength Levy (Scaled Proxy)', color='orange', alpha=0.6, linestyle='--')
    
    # Plot signals at the close price when they occur
    plt.plot(close.index[buy_signals.values], close[buy_signals.values], '^', 
             markersize=12, color='green', label='Buy Signal')
    plt.plot(close.index[sell_signals.values], close[sell_signals.values], 'v', 
             markersize=12, color='red', label='Sell Signal')
    
    plt.title(f'{asset} Buy/Sell Signals based on EMA Crossings')
    plt.legend()
    plt.grid(True)
    plt.show()


def run_single_asset_analysis(asset='BTC-USD', start_date='2023-01-01', end_date=None, initial_capital=10000):
    """
    Run complete analysis for a single asset: EMA Crossover vs Buy and Hold.
    """
    if end_date is None:
        end_date = pd.Timestamp.today().strftime('%Y-%m-%d')
    
    # Fetch data
    data = fetch_data(asset, start_date, end_date)
    print("\nData Head:")
    print(data.head())
    
    # Calculate indicators and signals
    data['RSL'] = calculate_rsl(data['Close'])
    data['Position'], data['Buy_Signal'], data['Sell_Signal'] = ema_crossover_signals_position(data['Close'])
    
    # Calculate Daily Returns
    data['Strategy_Return'] = data['Close'].pct_change() * data['Position'].shift(1)
    data['BuyHold_Return'] = data['Close'].pct_change()
    
    # Calculate Cumulative Wealth starting with INITIAL_CAPITAL
    data['Strategy_Cumulative'] = (1 + data['Strategy_Return'].fillna(0)).cumprod() * initial_capital
    data['BuyHold_Cumulative'] = (1 + data['BuyHold_Return'].fillna(0)).cumprod() * initial_capital
    
    # Drop initial rows used for EMA calculation where returns are unreliable
    data = data.dropna(subset=['Strategy_Cumulative', 'BuyHold_Cumulative'])
    
    # Calculate metrics
    metrics_strategy = calculate_metrics(
        data['Strategy_Return'].dropna(), 
        data['Strategy_Cumulative'].dropna(), 
        'EMA Crossover Model'
    )
    metrics_buyhold = calculate_metrics(
        data['BuyHold_Return'].dropna(), 
        data['BuyHold_Cumulative'].dropna(), 
        'Buy and Hold'
    )
    
    comparison_df = pd.DataFrame([metrics_strategy, metrics_buyhold])
    
    # Display results
    print("\n## 🚀 Performance Metrics Comparison")
    print(comparison_df.to_markdown(index=False))
    
    # Visualizations
    print("\n## 🖼️ Trade Signals Visualization")
    plot_signals(data, asset)
    
    print("\n## 💰 Cumulative Wealth Comparison")
    plt.figure(figsize=(14, 7))
    plt.plot(data['BuyHold_Cumulative'], label='Buy and Hold', color='blue', linewidth=3)
    plt.plot(data['Strategy_Cumulative'], label='EMA Crossover Model', 
             color='darkorange', linewidth=2, linestyle='--')
    plt.title(f'Cumulative Wealth: Active Strategy vs. Buy and Hold ({asset})')
    plt.xlabel('Date')
    plt.ylabel(f'Portfolio Value (Starting at ${initial_capital:,})')
    plt.legend()
    plt.grid(axis='y', alpha=0.5)
    plt.show()
    
    return data, comparison_df


# Example usage for Section 2:
# ASSET_TO_ANALYZE = 'BTC-USD'
# START_DATE = '2023-01-01'
# END_DATE = pd.Timestamp.today().strftime('%Y-%m-%d')
# INITIAL_CAPITAL = 10000
# data, metrics = run_single_asset_analysis(ASSET_TO_ANALYZE, START_DATE, END_DATE, INITIAL_CAPITAL)


# ============================================================================
# SECTION 3: Multi-Asset Analysis - EMA Crossover vs Buy and Hold
# ============================================================================

def plot_cumulative_wealth(data, asset, initial_capital=10000):
    """Plot cumulative wealth comparison."""
    plt.figure(figsize=(14, 5))
    plt.plot(data['BuyHold_Cumulative'], label='Buy and Hold', color='blue', linewidth=3)
    plt.plot(data['Strategy_Cumulative'], label='EMA Crossover Model', 
             color='darkorange', linewidth=2, linestyle='--')
    plt.title(f'{asset}: Cumulative Wealth Comparison (Start: ${initial_capital:,})')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.legend()
    plt.grid(axis='y', alpha=0.5)
    plt.show()


def run_analysis_for_asset(asset, start_date, end_date, initial_capital=10000):
    """
    Performs the full analysis (data, simulation, metrics, plots) for a single asset.
    """
    # --- 1. Data Fetching ---
    data = fetch_data(asset, start_date, end_date)
    if data.empty:
        print(f"Skipping {asset}: Could not retrieve historical data.")
        return None
    
    # --- 2. Signal Generation ---
    data['RSL'] = calculate_rsl(data['Close'])
    data['Position'], data['Buy_Signal'], data['Sell_Signal'] = ema_crossover_signals_position(data['Close'])
    
    # --- 3. Strategy Simulation ---
    data['Strategy_Return'] = data['Close'].pct_change() * data['Position'].shift(1)
    data['BuyHold_Return'] = data['Close'].pct_change()
    
    data['Strategy_Cumulative'] = (1 + data['Strategy_Return'].fillna(0)).cumprod() * initial_capital
    data['BuyHold_Cumulative'] = (1 + data['BuyHold_Return'].fillna(0)).cumprod() * initial_capital
    
    data = data.dropna(subset=['Strategy_Cumulative', 'BuyHold_Cumulative'])
    
    # --- 4. Metrics Calculation ---
    metrics_strategy = calculate_metrics(
        data['Strategy_Return'].dropna(), 
        data['Strategy_Cumulative'].dropna(), 
        'EMA Crossover Model'
    )
    metrics_buyhold = calculate_metrics(
        data['BuyHold_Return'].dropna(), 
        data['BuyHold_Cumulative'].dropna(), 
        'Buy and Hold'
    )
    comparison_df = pd.DataFrame([metrics_strategy, metrics_buyhold])
    
    # --- 5. Output and Plotting ---
    print(f"\n# 📊 Results for {asset}\n")
    print("## 🚀 Performance Metrics Comparison")
    print(comparison_df.to_markdown(index=False))
    print("\n-----------------------------------\n")
    
    print("\n## 🖼️ Trade Signals Visualization")
    plot_signals(data, asset)
    
    print("\n## 💰 Cumulative Wealth Comparison")
    plot_cumulative_wealth(data, asset, initial_capital)
    
    print("\n\n" + "="*80 + "\n\n")
    
    return data, comparison_df


def run_multi_asset_analysis(assets=['SPY', 'QQQ', 'DIA'], start_date='2023-01-01', 
                             end_date=None, initial_capital=10000):
    """
    Run analysis for multiple assets.
    """
    if end_date is None:
        end_date = pd.Timestamp.today().strftime('%Y-%m-%d')
    
    print("# 🚀 Multi-Asset Trading Strategy Analysis\n")
    print(f"Analyzing: {', '.join(assets)} starting from {start_date}")
    
    results = {}
    for asset in assets:
        result = run_analysis_for_asset(asset, start_date, end_date, initial_capital)
        if result is not None:
            results[asset] = result
    
    print("Analysis Complete.")
    return results


# Example usage for Section 3:
# ASSETS_TO_ANALYZE = ['SPY', 'QQQ', 'DIA']  # S&P 500, Nasdaq 100, Dow Jones
# START_DATE = '2023-01-01'
# END_DATE = pd.Timestamp.today().strftime('%Y-%m-%d')
# INITIAL_CAPITAL = 10000
# results = run_multi_asset_analysis(ASSETS_TO_ANALYZE, START_DATE, END_DATE, INITIAL_CAPITAL)


# ============================================================================
# Marimo cells
# ============================================================================


@app.cell
def __():
    import marimo as mo
    import pandas as pd

    return mo, pd


@app.cell
def __(mo):
    """Notebook title and description."""
    mo.md(
        "# EMA Crossover Trading Strategy Analysis\n"
        "This marimo notebook implements an Exponential Moving Average (EMA) Crossover "
        "trading strategy and compares it against a simple Buy & Hold baseline."
    )


@app.cell
def __(pd):
    """Configuration for the analysis window and capital."""
    asset = "BTC-USD"
    start_date = "2023-01-01"
    end_date = pd.Timestamp.today().strftime("%Y-%m-%d")
    initial_capital = 10_000
    return asset, start_date, end_date, initial_capital


@app.cell
def __(asset):
    """Section 1: basic EMA crossover signal visualization."""
    __import__(__name__).generate_signals(asset=asset)


@app.cell
def __(asset, start_date, end_date, initial_capital):
    """Section 2: single-asset backtest vs. buy & hold."""
    __import__(__name__).run_single_asset_analysis(
        asset=asset,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
    )


@app.cell
def __(asset, start_date, end_date, initial_capital):
    """Section 3: multi-asset analysis for a small ETF basket."""
    assets = ["SPY", "QQQ", "DIA"]
    # Reuse the same window and capital for each asset
    __import__(__name__).run_multi_asset_analysis(
        assets=assets,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
    )


if __name__ == "__main__":
    app.run()

