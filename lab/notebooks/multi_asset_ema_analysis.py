"""
Multi-Asset EMA Crossover Trading Strategy Analysis

This notebook runs the Exponential Moving Average (EMA) Crossover trading strategy
against a simple Buy and Hold strategy for multiple major market ETFs.

Two main sections:
1. Multi-Asset Analysis (EMA Crossover vs Buy and Hold)
2. Strategy Visualization (Price, EMAs, and Crossover Signals)
"""

import marimo as mo
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

__generated_with = "0.7.9"
app = mo.App(width="full")

# ============================================================================
# SECTION 1: Multi-Asset Analysis - EMA Crossover vs Buy and Hold
# ============================================================================

# --- USER CONFIGURATION ---
ASSETS_TO_ANALYZE = ['SPY', 'QQQ', 'DIA']  # S&P 500, Nasdaq 100, Dow Jones
START_DATE = '2023-01-01'
END_DATE = pd.Timestamp.today().strftime('%Y-%m-%d')
INITIAL_CAPITAL = 10000

# --- CORE FUNCTIONS ---

def fetch_data(asset, start_date, end_date):
    """Downloads asset data."""
    print(f"\n--- Fetching Data for {asset} ---")
    data = yf.Ticker(asset).history(start=start_date, end=end_date)
    return data.ffill().dropna()


def calculate_rsl(close, length=26):
    """Calculate Relative Strength Levy (RSL) as the ratio of short-term to long-term EMA."""
    ema_short = close.ewm(span=length//2, adjust=False).mean()
    ema_long = close.ewm(span=length, adjust=False).mean()
    rsl = ema_short / ema_long
    return rsl


def ema_crossover_signals(close, short_span=12, long_span=26):
    """Generate position signals (1 for Long, 0 for Cash) based on EMA crossovers."""
    ema_short = close.ewm(span=short_span, adjust=False).mean()
    ema_long = close.ewm(span=long_span, adjust=False).mean()
    
    # Position: 1 for Long, 0 for Cash
    signal = pd.Series(0, index=close.index)
    signal.loc[ema_short > ema_long] = 1
    signal.loc[ema_short < ema_long] = 0
    
    buy_signals = (signal.diff() == 1)
    sell_signals = (signal.diff() == -1)
    
    return signal, buy_signals, sell_signals


def calculate_metrics(returns, cumulative_wealth, name):
    """Calculates key trading metrics: Total Return, CAGR, Volatility, Max Drawdown, and Sharpe Ratio."""
    total_return = (cumulative_wealth.iloc[-1] / cumulative_wealth.iloc[0]) - 1
    years = (cumulative_wealth.index[-1] - cumulative_wealth.index[0]).days / 365.25
    cagr = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
    volatility = returns.std() * np.sqrt(252)
    
    peak = cumulative_wealth.expanding(min_periods=1).max()
    drawdown = (cumulative_wealth / peak) - 1
    max_drawdown = drawdown.min()
    
    # Sharpe Ratio (Assumes risk-free rate of 0 for simplicity)
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
    plt.figure(figsize=(16, 6))
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
    
    plt.title(f'{asset} Trading Signals (EMA Crossover)')
    plt.legend()
    plt.grid(True)
    plt.show()


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


# --- MAIN ITERATION LOGIC ---

def run_analysis_for_asset(asset, start_date, end_date, initial_capital=10000):
    """Performs the full analysis (data, simulation, metrics, plots) for a single asset."""
    # --- 1. Data Fetching ---
    data = fetch_data(asset, start_date, end_date)
    if data.empty:
        print(f"Skipping {asset}: Could not retrieve historical data.")
        return None
    
    # --- 2. Signal Generation ---
    data['RSL'] = calculate_rsl(data['Close'])
    data['Position'], data['Buy_Signal'], data['Sell_Signal'] = ema_crossover_signals(data['Close'])
    
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


def run_multi_asset_analysis(assets=None, start_date=None, end_date=None, initial_capital=10000):
    """
    Run analysis for multiple assets.
    
    Args:
        assets: List of asset symbols (defaults to ASSETS_TO_ANALYZE)
        start_date: Start date for analysis (defaults to START_DATE)
        end_date: End date for analysis (defaults to END_DATE)
        initial_capital: Starting capital (defaults to INITIAL_CAPITAL)
    """
    if assets is None:
        assets = ASSETS_TO_ANALYZE
    if start_date is None:
        start_date = START_DATE
    if end_date is None:
        end_date = END_DATE
    
    print("# 🚀 Multi-Asset Trading Strategy Analysis\n")
    print(f"Analyzing: {', '.join(assets)} starting from {start_date}")
    
    results = {}
    for asset in assets:
        result = run_analysis_for_asset(asset, start_date, end_date, initial_capital)
        if result is not None:
            results[asset] = result
    
    print("Analysis Complete.")
    return results


# Example usage for Section 1:
# results = run_multi_asset_analysis()


# ============================================================================
# SECTION 2: Strategy Visualization - Price, EMAs, and Crossover Signals
# ============================================================================

def plot_strategy_signals(ticker, start_date="2020-01-01", interval="1d", resample_period="W"):
    """
    Plots the closing price, EMA8, EMA200, and marks the buy/sell signals
    for a given ticker based on the EMA 8/200 strategy.
    
    Args:
        ticker: Stock/ETF symbol to analyze
        start_date: Start date for data retrieval
        interval: Data interval (default: "1d" for daily)
        resample_period: Period to resample data (default: "W" for weekly)
    """
    print(f"\n{'='*50}")
    print(f"PLOTTING SIGNALS FOR: {ticker}")
    print(f"{'='*50}")
    
    try:
        # Download data
        data = yf.download(ticker, start=start_date, interval=interval, progress=False, auto_adjust=True)
        
        if len(data) == 0:
            print(f"No data found for {ticker}")
            return
        
        # Convert to specified period (e.g., weekly)
        data = data.resample(resample_period).last().dropna()
        
        if len(data) < 200:
            print(f"Insufficient data ({len(data)} points) for EMA200 calculation after resampling.")
            return
        
        # Calculate EMAs
        data["EMA8"] = data["Close"].ewm(span=8, adjust=False).mean()
        data["EMA200"] = data["Close"].ewm(span=200, adjust=False).mean()
        
        # Detect crossover signals
        data["Buy_Signal"] = (data["EMA8"] > data["EMA200"]) & (data["EMA8"].shift(1) <= data["EMA200"].shift(1))
        data["Sell_Signal"] = (data["EMA8"] < data["EMA200"]) & (data["EMA8"].shift(1) >= data["EMA200"].shift(1))
        
        # Filter signals for plotting
        buy_signals = data[data["Buy_Signal"]].index
        sell_signals = data[data["Sell_Signal"]].index
        
        # --- Plotting ---
        plt.figure(figsize=(18, 8))
        plt.plot(data.index, data["Close"], label="Close Price", color="black", alpha=0.6)
        plt.plot(data.index, data["EMA8"], label="EMA 8 (Fast)", color="green", linewidth=2)
        plt.plot(data.index, data["EMA200"], label="EMA 200 (Slow)", color="red", linewidth=2)
        
        # Plot Buy Signals
        plt.scatter(buy_signals, data.loc[buy_signals]["Close"], marker="^", 
                   color="green", s=150, label="Buy Signal", zorder=5)
        
        # Plot Sell Signals
        plt.scatter(sell_signals, data.loc[sell_signals]["Close"], marker="v", 
                   color="red", s=150, label="Sell Signal", zorder=5)
        
        plt.title(f"{ticker} EMA 8/200 Crossover Strategy - Weekly Chart (Signals on Close Price)", fontsize=16)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Price (USD)", fontsize=12)
        plt.legend(loc="best")
        plt.grid(True, alpha=0.3)
        plt.show()
        
    except Exception as e:
        print(f"Error plotting {ticker}: {str(e)}")


def visualize_top_performers(df_comparison, start_date="2020-01-01", interval="1d", resample_period="W", top_n=3):
    """
    Visualizes strategy signals for top performing tickers.
    
    Args:
        df_comparison: DataFrame with comparison results (must have 'Ticker' column)
        start_date: Start date for visualization
        interval: Data interval
        resample_period: Period to resample data
        top_n: Number of top performers to visualize
    """
    print("\nRUNNING VISUALIZATION FOR TOP PERFORMERS")
    print("=" * 60)
    
    if df_comparison is None or df_comparison.empty:
        print("DataFrame 'df_comparison' not available. Run the multi-asset analysis first.")
        return
    
    if 'Ticker' not in df_comparison.columns:
        print("DataFrame must have a 'Ticker' column.")
        return
    
    # Get the top N tickers based on Total Return
    top_tickers = df_comparison["Ticker"].head(top_n).tolist()
    
    for ticker in top_tickers:
        plot_strategy_signals(ticker, start_date=start_date, interval=interval, resample_period=resample_period)
    
    print("VISUALIZATION COMPLETE.")


# Example usage for Section 2:
# plot_strategy_signals('SPY', start_date="2020-01-01", interval="1d", resample_period="W")
# 
# # If you have a comparison DataFrame from Section 1:
# # visualize_top_performers(df_comparison, top_n=3)


# ============================================================================
# Marimo cells
# ============================================================================


@app.cell
def __():
    import marimo as mo

    from notebook_helpers.multi_asset_ema_notebook import (
        plot_strategy_signals,
        run_multi_asset_analysis,
    )

    return mo, plot_strategy_signals, run_multi_asset_analysis


@app.cell
def __(mo):
    """Notebook title and description."""
    mo.md(
        "# Multi-Asset EMA Crossover Trading Strategy Analysis\n"
        "This marimo notebook compares an EMA crossover strategy against Buy & Hold "
        "across a basket of ETFs and provides visualization helpers."
    )


@app.cell
def __():
    """Configuration for assets, analysis window, and capital."""
    import pandas as pd

    assets_to_analyze = ["SPY", "QQQ", "DIA"]
    start_date = "2023-01-01"
    end_date = pd.Timestamp.today().strftime("%Y-%m-%d")
    initial_capital = 10_000
    return assets_to_analyze, start_date, end_date, initial_capital


@app.cell
def __(mo, assets_to_analyze, start_date, end_date, initial_capital):
    """Show the configured asset universe and analysis window."""
    mo.md(
        f"**Assets:** {', '.join(assets_to_analyze)}\\n"
        f"**Start date:** {start_date}\\n"
        f"**End date:** {end_date}\\n"
        f"**Initial capital:** ${initial_capital:,}"
    )


@app.cell
def __(assets_to_analyze, start_date, end_date, initial_capital, run_multi_asset_analysis):
    """Run the multi-asset backtest using the current configuration."""
    run_multi_asset_analysis(
        assets=assets_to_analyze,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
    )


@app.cell
def __(assets_to_analyze, plot_strategy_signals):
    """Visualize EMA 8/200 crossover signals for each configured asset."""
    for asset in assets_to_analyze:
        plot_strategy_signals(
            asset,
            start_date="2020-01-01",
            interval="1d",
            resample_period="W",
        )


if __name__ == "__main__":
    app.run()

