"""
Comprehensive EMA Crossover Trading Strategy Analysis
======================================================

This marimo notebook provides a complete trading strategy analysis toolkit with:
- Multi-timeframe EMA crossover signals (12/26 and 8/200)
- Single and multi-asset backtesting
- Performance metrics vs Buy & Hold
- Visual signal generation and wealth tracking

Author: Trading Strategy Analysis
Date: December 2025
"""

import marimo as mo

__generated_with = "0.7.9"
app = mo.App(width="full")


@app.cell
def __():
    """Import all required libraries"""
    import marimo as mo
    import yfinance as yf
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    return mo, yf, pd, np, plt


@app.cell
def __(mo):
    """Notebook header"""
    mo.md("""
    # 📈 Comprehensive EMA Trading Strategy Analysis
    
    This notebook provides complete backtesting and analysis of EMA crossover strategies:
    
    - **Signal Generation**: Visual buy/sell signals based on EMA crossovers
    - **Performance Metrics**: CAGR, Sharpe Ratio, Max Drawdown, Win Rate
    - **Strategy Comparison**: EMA Strategy vs Buy & Hold
    - **Multi-Asset Analysis**: Compare performance across different assets
    
    ---
    """)
    return


@app.cell
def __(pd):
    """Configuration: Define your analysis parameters"""
    
    # Single asset configuration
    single_asset = "BTC-USD"
    
    # Multi-asset configuration
    multi_assets = ["SPY", "QQQ", "DIA"]
    
    # Time period
    start_date = "2020-01-01"
    end_date = pd.Timestamp.today().strftime('%Y-%m-%d')
    
    # Strategy parameters
    short_ema = 12
    long_ema = 26
    initial_capital = 10_000
    
    # Data interval: "1d" for daily, "1wk" for weekly
    data_interval = "1wk"
    
    return (single_asset, multi_assets, start_date, end_date, 
            short_ema, long_ema, initial_capital, data_interval)


@app.cell
def __(mo, single_asset, multi_assets, start_date, end_date, short_ema, long_ema, initial_capital, data_interval):
    """Display configuration"""
    mo.md(f"""
    ## 🎯 Analysis Configuration
    
    **Single Asset**: {single_asset}  
    **Multi-Assets**: {', '.join(multi_assets)}  
    **Period**: {start_date} to {end_date}  
    **Strategy**: EMA {short_ema}/{long_ema} Crossover  
    **Initial Capital**: ${initial_capital:,}  
    **Data Interval**: {data_interval}
    
    ---
    """)
    return


@app.cell
def __(mo):
    """Section header for single asset"""
    mo.md("## 📊 Single Asset Analysis")
    return


@app.cell
def __(yf, pd, np, plt, single_asset, start_date, end_date, initial_capital, short_ema, long_ema, data_interval):
    """Run single asset analysis with all visualizations"""
    
    # Helper functions (local to this cell)
    def _fetch_data(asset, start, end, interval="1d"):
        print(f"📥 Fetching data for {asset}...")
        _d = yf.download(asset, start=start, end=end, interval=interval, progress=False, auto_adjust=True)
        # Ensure single-level column index
        if isinstance(_d.columns, pd.MultiIndex):
            _d.columns = _d.columns.get_level_values(0)
        return _d.ffill().dropna()
    
    def _calculate_rsl(close, length=26):
        _ema_s = close.ewm(span=length//2, adjust=False).mean()
        _ema_l = close.ewm(span=length, adjust=False).mean()
        return _ema_s / _ema_l
    
    def _calculate_signals(close, short_span=12, long_span=26):
        _ema_s = close.ewm(span=short_span, adjust=False).mean()
        _ema_l = close.ewm(span=long_span, adjust=False).mean()
        _pos = pd.Series(0, index=close.index, dtype=int)
        _mask_long = _ema_s > _ema_l
        _mask_cash = _ema_s < _ema_l
        _pos[_mask_long] = 1
        _pos[_mask_cash] = 0
        _buy = (_pos.diff() == 1)
        _sell = (_pos.diff() == -1)
        return _pos, _buy, _sell, _ema_s, _ema_l
    
    def _calculate_metrics(returns, cumulative_wealth, strategy_name):
        _total_ret = (cumulative_wealth.iloc[-1] / cumulative_wealth.iloc[0]) - 1
        _years = (cumulative_wealth.index[-1] - cumulative_wealth.index[0]).days / 365.25
        _cagr = (1 + _total_ret) ** (1/_years) - 1 if _years > 0 else 0
        _vol = returns.std() * np.sqrt(252)
        _peak = cumulative_wealth.expanding(min_periods=1).max()
        _dd = (cumulative_wealth / _peak) - 1
        _max_dd = _dd.min()
        _sharpe = _cagr / _vol if _vol != 0 else np.nan
        
        if 'Strategy' in strategy_name:
            _win_days = (returns > 0).sum()
            _tot_days = len(returns[returns != 0])
            _win_rate = _win_days / _tot_days if _tot_days > 0 else 0
        else:
            _win_rate = np.nan
        
        return {
            'Strategy': strategy_name,
            'Total Return': f'{_total_ret * 100:.2f}%',
            'CAGR': f'{_cagr * 100:.2f}%',
            'Volatility': f'{_vol * 100:.2f}%',
            'Max Drawdown': f'{_max_dd * 100:.2f}%',
            'Sharpe Ratio': f'{_sharpe:.2f}',
            'Win Rate': f'{_win_rate * 100:.1f}%' if not np.isnan(_win_rate) else 'N/A'
        }
    
    print(f"\n{'='*80}")
    print(f"📊 ANALYZING: {single_asset}")
    print(f"{'='*80}\n")
    
    # Fetch and process data
    _data_s = _fetch_data(single_asset, start_date, end_date, data_interval)
    
    _result_single = None
    if not _data_s.empty and len(_data_s) >= long_ema:
        _df_s = _data_s.copy()
        _df_s['RSL'] = _calculate_rsl(_df_s['Close'])
        _df_s['Position'], _df_s['Buy_Signal'], _df_s['Sell_Signal'], _df_s['EMA_Short'], _df_s['EMA_Long'] = \
            _calculate_signals(_df_s['Close'], short_ema, long_ema)
        
        _df_s['Strategy_Return'] = _df_s['Close'].pct_change() * _df_s['Position'].shift(1)
        _df_s['BuyHold_Return'] = _df_s['Close'].pct_change()
        _df_s['Strategy_Wealth'] = (1 + _df_s['Strategy_Return'].fillna(0)).cumprod() * initial_capital
        _df_s['BuyHold_Wealth'] = (1 + _df_s['BuyHold_Return'].fillna(0)).cumprod() * initial_capital
        _df_s = _df_s.dropna(subset=['Strategy_Wealth', 'BuyHold_Wealth'])
        
        _met_strat = _calculate_metrics(_df_s['Strategy_Return'].dropna(), _df_s['Strategy_Wealth'].dropna(), 'EMA Crossover Strategy')
        _met_buy = _calculate_metrics(_df_s['BuyHold_Return'].dropna(), _df_s['BuyHold_Wealth'].dropna(), 'Buy & Hold')
        _met_df = pd.DataFrame([_met_strat, _met_buy])
        
        print("\n📈 PERFORMANCE METRICS")
        print("="*80)
        print(_met_df.to_string(index=False))
        print()
        
        # Plot 1: Price with signals
        print("\n🎨 Generating visualizations...")
        _fig1, _ax1 = plt.subplots(figsize=(16, 8))
        _ax1.plot(_df_s.index, _df_s['Close'], label='Close Price', linewidth=2.5, color='#2E86AB', alpha=0.8)
        _ax1.plot(_df_s.index, _df_s['EMA_Short'], label=f'EMA {short_ema} (Fast)', linewidth=2, color='#06D6A0', linestyle='--')
        _ax1.plot(_df_s.index, _df_s['EMA_Long'], label=f'EMA {long_ema} (Slow)', linewidth=2, color='#EF476F', linestyle='--')
        
        _buy_idx = _df_s['Buy_Signal']
        _sell_idx = _df_s['Sell_Signal']
        _ax1.scatter(_df_s.index[_buy_idx], _df_s.loc[_buy_idx, 'Close'], marker='^', s=200, color='#06D6A0', 
                   label='Buy Signal', zorder=5, edgecolors='black', linewidths=1.5)
        _ax1.scatter(_df_s.index[_sell_idx], _df_s.loc[_sell_idx, 'Close'], marker='v', s=200, color='#EF476F', 
                   label='Sell Signal', zorder=5, edgecolors='black', linewidths=1.5)
        
        _ax1.set_title(f'{single_asset} - EMA Crossover Trading Signals', fontsize=18, fontweight='bold', pad=20)
        _ax1.set_xlabel('Date', fontsize=14)
        _ax1.set_ylabel('Price (USD)', fontsize=14)
        _ax1.legend(loc='best', fontsize=12, framealpha=0.95)
        _ax1.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.show()
        
        # Plot 2: Cumulative wealth
        _fig2, _ax2 = plt.subplots(figsize=(16, 7))
        _ax2.plot(_df_s.index, _df_s['BuyHold_Wealth'], label='Buy & Hold', color='#2E86AB', linewidth=3, alpha=0.8)
        _ax2.plot(_df_s.index, _df_s['Strategy_Wealth'], label='EMA Crossover Strategy', color='#F77F00', linewidth=2.5, linestyle='--')
        _ax2.fill_between(_df_s.index, _df_s['BuyHold_Wealth'], _df_s['Strategy_Wealth'],
                        where=(_df_s['Strategy_Wealth'] >= _df_s['BuyHold_Wealth']),
                        alpha=0.2, color='green', label='Strategy Outperformance')
        _ax2.fill_between(_df_s.index, _df_s['BuyHold_Wealth'], _df_s['Strategy_Wealth'],
                        where=(_df_s['Strategy_Wealth'] < _df_s['BuyHold_Wealth']),
                        alpha=0.2, color='red', label='Strategy Underperformance')
        
        _ax2.set_title(f'{single_asset} - Cumulative Wealth (Initial: ${initial_capital:,})', fontsize=18, fontweight='bold', pad=20)
        _ax2.set_xlabel('Date', fontsize=14)
        _ax2.set_ylabel('Portfolio Value (USD)', fontsize=14)
        _ax2.legend(loc='best', fontsize=12, framealpha=0.95)
        _ax2.grid(True, alpha=0.3, linestyle='--')
        _ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        plt.tight_layout()
        plt.show()
        
        # Plot 3: Drawdown
        _fig3, _ax3 = plt.subplots(figsize=(16, 6))
        _strat_peak = _df_s['Strategy_Wealth'].expanding(min_periods=1).max()
        _strat_dd = (_df_s['Strategy_Wealth'] / _strat_peak) - 1
        _buy_peak = _df_s['BuyHold_Wealth'].expanding(min_periods=1).max()
        _buy_dd = (_df_s['BuyHold_Wealth'] / _buy_peak) - 1
        
        _ax3.plot(_df_s.index, _strat_dd * 100, label='EMA Strategy Drawdown', color='#F77F00', linewidth=2)
        _ax3.plot(_df_s.index, _buy_dd * 100, label='Buy & Hold Drawdown', color='#2E86AB', linewidth=2, alpha=0.7)
        _ax3.fill_between(_df_s.index, _strat_dd * 100, 0, alpha=0.3, color='#F77F00')
        
        _ax3.set_title(f'{single_asset} - Drawdown Analysis', fontsize=18, fontweight='bold', pad=20)
        _ax3.set_xlabel('Date', fontsize=14)
        _ax3.set_ylabel('Drawdown (%)', fontsize=14)
        _ax3.legend(loc='best', fontsize=12, framealpha=0.95)
        _ax3.grid(True, alpha=0.3, linestyle='--')
        _ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        plt.tight_layout()
        plt.show()
        
        _result_single = (_df_s, _met_df)
    else:
        print(f"❌ Insufficient data for {single_asset}")
    
    _result_single
    return


@app.cell
def __(mo):
    """Section header for multi-asset"""
    mo.md("## 🌐 Multi-Asset Comparison")
    return


@app.cell
def __(yf, pd, np, plt, multi_assets, start_date, end_date, initial_capital, short_ema, long_ema, data_interval):
    """Run multi-asset analysis"""
    
    def _fetch_multi(asset, start, end, interval="1d"):
        print(f"📥 Fetching data for {asset}...")
        _d = yf.download(asset, start=start, end=end, interval=interval, progress=False, auto_adjust=True)
        # Ensure single-level column index
        if isinstance(_d.columns, pd.MultiIndex):
            _d.columns = _d.columns.get_level_values(0)
        return _d.ffill().dropna()
    
    def _calc_rsl_multi(close, length=26):
        _ema_s = close.ewm(span=length//2, adjust=False).mean()
        _ema_l = close.ewm(span=length, adjust=False).mean()
        return _ema_s / _ema_l
    
    def _calc_sig_multi(close, short_span=12, long_span=26):
        _ema_s = close.ewm(span=short_span, adjust=False).mean()
        _ema_l = close.ewm(span=long_span, adjust=False).mean()
        _pos = pd.Series(0, index=close.index, dtype=int)
        _mask_long = _ema_s > _ema_l
        _mask_cash = _ema_s < _ema_l
        _pos[_mask_long] = 1
        _pos[_mask_cash] = 0
        _buy = (_pos.diff() == 1)
        _sell = (_pos.diff() == -1)
        return _pos, _buy, _sell, _ema_s, _ema_l
    
    def _calc_met_multi(returns, cumulative_wealth, strategy_name):
        _total_ret = (cumulative_wealth.iloc[-1] / cumulative_wealth.iloc[0]) - 1
        _years = (cumulative_wealth.index[-1] - cumulative_wealth.index[0]).days / 365.25
        _cagr = (1 + _total_ret) ** (1/_years) - 1 if _years > 0 else 0
        _vol = returns.std() * np.sqrt(252)
        _peak = cumulative_wealth.expanding(min_periods=1).max()
        _dd = (cumulative_wealth / _peak) - 1
        _max_dd = _dd.min()
        _sharpe = _cagr / _vol if _vol != 0 else np.nan
        
        if 'Strategy' in strategy_name:
            _win_days = (returns > 0).sum()
            _tot_days = len(returns[returns != 0])
            _win_rate = _win_days / _tot_days if _tot_days > 0 else 0
        else:
            _win_rate = np.nan
        
        return {
            'Strategy': strategy_name,
            'Total Return': f'{_total_ret * 100:.2f}%',
            'CAGR': f'{_cagr * 100:.2f}%',
            'Volatility': f'{_vol * 100:.2f}%',
            'Max Drawdown': f'{_max_dd * 100:.2f}%',
            'Sharpe Ratio': f'{_sharpe:.2f}',
            'Win Rate': f'{_win_rate * 100:.1f}%' if not np.isnan(_win_rate) else 'N/A'
        }
    
    print(f"\n{'#'*80}")
    print(f"🚀 MULTI-ASSET TRADING STRATEGY ANALYSIS")
    print(f"{'#'*80}")
    print(f"\nAssets: {', '.join(multi_assets)}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Initial Capital: ${initial_capital:,}")
    print(f"Strategy: EMA {short_ema}/{long_ema} Crossover\n")
    
    _all_results = {}
    _all_metrics = []
    
    for _asset in multi_assets:
        print(f"\n{'='*80}")
        print(f"📊 ANALYZING: {_asset}")
        print(f"{'='*80}\n")
        
        _data_m = _fetch_multi(_asset, start_date, end_date, data_interval)
        
        if _data_m.empty or len(_data_m) < long_ema:
            print(f"❌ Insufficient data for {_asset}")
            continue
        
        _df_m = _data_m.copy()
        _df_m['RSL'] = _calc_rsl_multi(_df_m['Close'])
        _df_m['Position'], _df_m['Buy_Signal'], _df_m['Sell_Signal'], _df_m['EMA_Short'], _df_m['EMA_Long'] = \
            _calc_sig_multi(_df_m['Close'], short_ema, long_ema)
        
        _df_m['Strategy_Return'] = _df_m['Close'].pct_change() * _df_m['Position'].shift(1)
        _df_m['BuyHold_Return'] = _df_m['Close'].pct_change()
        _df_m['Strategy_Wealth'] = (1 + _df_m['Strategy_Return'].fillna(0)).cumprod() * initial_capital
        _df_m['BuyHold_Wealth'] = (1 + _df_m['BuyHold_Return'].fillna(0)).cumprod() * initial_capital
        _df_m = _df_m.dropna(subset=['Strategy_Wealth', 'BuyHold_Wealth'])
        
        _met_s = _calc_met_multi(_df_m['Strategy_Return'].dropna(), _df_m['Strategy_Wealth'].dropna(), 'EMA Crossover Strategy')
        _met_b = _calc_met_multi(_df_m['BuyHold_Return'].dropna(), _df_m['BuyHold_Wealth'].dropna(), 'Buy & Hold')
        _met_df = pd.DataFrame([_met_s, _met_b])
        
        print("\n📈 PERFORMANCE METRICS")
        print("="*80)
        print(_met_df.to_string(index=False))
        print()
        
        _all_results[_asset] = _df_m
        for _idx in _met_df.index:
            _row = _met_df.loc[_idx].to_dict()
            _row['Asset'] = _asset
            _all_metrics.append(_row)
        
        print("\n🎨 Generating visualizations...")
        
        # Plot 1
        _f1, _a1 = plt.subplots(figsize=(16, 8))
        _a1.plot(_df_m.index, _df_m['Close'], label='Close Price', linewidth=2.5, color='#2E86AB', alpha=0.8)
        _a1.plot(_df_m.index, _df_m['EMA_Short'], label=f'EMA {short_ema} (Fast)', linewidth=2, color='#06D6A0', linestyle='--')
        _a1.plot(_df_m.index, _df_m['EMA_Long'], label=f'EMA {long_ema} (Slow)', linewidth=2, color='#EF476F', linestyle='--')
        
        _bi = _df_m['Buy_Signal']
        _si = _df_m['Sell_Signal']
        _a1.scatter(_df_m.index[_bi], _df_m.loc[_bi, 'Close'], marker='^', s=200, color='#06D6A0', 
                   label='Buy Signal', zorder=5, edgecolors='black', linewidths=1.5)
        _a1.scatter(_df_m.index[_si], _df_m.loc[_si, 'Close'], marker='v', s=200, color='#EF476F', 
                   label='Sell Signal', zorder=5, edgecolors='black', linewidths=1.5)
        
        _a1.set_title(f'{_asset} - EMA Crossover Trading Signals', fontsize=18, fontweight='bold', pad=20)
        _a1.set_xlabel('Date', fontsize=14)
        _a1.set_ylabel('Price (USD)', fontsize=14)
        _a1.legend(loc='best', fontsize=12, framealpha=0.95)
        _a1.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.show()
        
        # Plot 2
        _f2, _a2 = plt.subplots(figsize=(16, 7))
        _a2.plot(_df_m.index, _df_m['BuyHold_Wealth'], label='Buy & Hold', color='#2E86AB', linewidth=3, alpha=0.8)
        _a2.plot(_df_m.index, _df_m['Strategy_Wealth'], label='EMA Crossover Strategy', color='#F77F00', linewidth=2.5, linestyle='--')
        _a2.fill_between(_df_m.index, _df_m['BuyHold_Wealth'], _df_m['Strategy_Wealth'],
                        where=(_df_m['Strategy_Wealth'] >= _df_m['BuyHold_Wealth']),
                        alpha=0.2, color='green', label='Strategy Outperformance')
        _a2.fill_between(_df_m.index, _df_m['BuyHold_Wealth'], _df_m['Strategy_Wealth'],
                        where=(_df_m['Strategy_Wealth'] < _df_m['BuyHold_Wealth']),
                        alpha=0.2, color='red', label='Strategy Underperformance')
        
        _a2.set_title(f'{_asset} - Cumulative Wealth (Initial: ${initial_capital:,})', fontsize=18, fontweight='bold', pad=20)
        _a2.set_xlabel('Date', fontsize=14)
        _a2.set_ylabel('Portfolio Value (USD)', fontsize=14)
        _a2.legend(loc='best', fontsize=12, framealpha=0.95)
        _a2.grid(True, alpha=0.3, linestyle='--')
        _a2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        plt.tight_layout()
        plt.show()
        
        print("\n\n")
    
    _summary = None
    if _all_metrics:
        _summary = pd.DataFrame(_all_metrics)
        _cols = ['Asset', 'Strategy'] + [c for c in _summary.columns if c not in ['Asset', 'Strategy']]
        _summary = _summary[_cols]
        
        print(f"\n{'='*80}")
        print("📊 SUMMARY: ALL ASSETS PERFORMANCE")
        print(f"{'='*80}\n")
        print(_summary.to_string(index=False))
        print()
    
    _result_multi = (_all_results, _summary)
    _result_multi
    return


@app.cell
def __(mo):
    """Section header for position visualization"""
    mo.md("## 🎨 Position Visualization (Colored by Signal)")
    return


@app.cell
def __(yf, pd, np, plt, single_asset, start_date, end_date, short_ema, long_ema, data_interval):
    """Create colored line charts showing Buy/Hold/Sell positions"""
    
    def _fetch_viz(asset, start, end, interval="1d"):
        _d = yf.download(asset, start=start, end=end, interval=interval, progress=False, auto_adjust=True)
        if isinstance(_d.columns, pd.MultiIndex):
            _d.columns = _d.columns.get_level_values(0)
        return _d.ffill().dropna()
    
    def _calc_sig_viz(close, short_span=12, long_span=26):
        _ema_s = close.ewm(span=short_span, adjust=False).mean()
        _ema_l = close.ewm(span=long_span, adjust=False).mean()
        _pos = pd.Series(0, index=close.index, dtype=int)
        _mask_long = _ema_s > _ema_l
        _mask_cash = _ema_s < _ema_l
        _pos[_mask_long] = 1
        _pos[_mask_cash] = 0
        return _pos, _ema_s, _ema_l
    
    print(f"\n{'='*80}")
    print(f"🎨 POSITION VISUALIZATION: {single_asset}")
    print(f"{'='*80}\n")
    
    _data_viz = _fetch_viz(single_asset, start_date, end_date, data_interval)
    
    _viz_result = None
    if not _data_viz.empty and len(_data_viz) >= long_ema:
        _df_viz = _data_viz.copy()
        _df_viz['Position'], _df_viz['EMA_Short'], _df_viz['EMA_Long'] = \
            _calc_sig_viz(_df_viz['Close'], short_ema, long_ema)
        
        # Create 2x2 grid of subplots
        _fig_grid, _axes = plt.subplots(2, 2, figsize=(20, 12))
        _fig_grid.suptitle(f'{single_asset} - Position Analysis (Red=Sell/Cash, Green=Buy/Long, Blue=Hold)', 
                          fontsize=20, fontweight='bold', y=0.995)
        
        # Helper function to plot colored segments
        def _plot_colored_line(ax, df, title, show_ema=False):
            # Plot EMAs first if requested
            if show_ema:
                ax.plot(df.index, df['EMA_Short'], label=f'EMA {short_ema}', 
                       color='gray', linewidth=1.5, alpha=0.3, linestyle='--')
                ax.plot(df.index, df['EMA_Long'], label=f'EMA {long_ema}', 
                       color='black', linewidth=1.5, alpha=0.3, linestyle='--')
            
            # Plot price with color segments based on position
            _prev_pos = None
            for i in range(len(df)):
                _curr_pos = df['Position'].iloc[i]
                
                # Start a new segment when position changes or at the beginning
                if i == 0 or _curr_pos != _prev_pos:
                    _segment_start = i
                
                # Plot segment when position is about to change or at the end
                if i == len(df) - 1 or (i < len(df) - 1 and df['Position'].iloc[i + 1] != _curr_pos):
                    _segment = df.iloc[_segment_start:i + 1]
                    _color = '#06D6A0' if _curr_pos == 1 else '#EF476F'
                    _label = 'Long Position' if _curr_pos == 1 else 'Cash/Out'
                    
                    # Only add label for first occurrence
                    if _prev_pos != _curr_pos or i == 0:
                        ax.plot(_segment.index, _segment['Close'], 
                               color=_color, linewidth=2.5, alpha=0.8, label=_label)
                    else:
                        ax.plot(_segment.index, _segment['Close'], 
                               color=_color, linewidth=2.5, alpha=0.8)
                
                _prev_pos = _curr_pos
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=10)
            ax.set_xlabel('Date', fontsize=11)
            ax.set_ylabel('Price (USD)', fontsize=11)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Remove duplicate labels
            _handles, _labels = ax.get_legend_handles_labels()
            _by_label = dict(zip(_labels, _handles))
            ax.legend(_by_label.values(), _by_label.keys(), loc='best', fontsize=10, framealpha=0.95)
        
        # Plot 1: Simple colored line
        _plot_colored_line(_axes[0, 0], _df_viz, 'Position Colored Price Line')
        
        # Plot 2: With EMAs
        _plot_colored_line(_axes[0, 1], _df_viz, 'Position Colored Price with EMAs', show_ema=True)
        
        # Plot 3: Fill between style
        _ax3 = _axes[1, 0]
        _ax3.fill_between(_df_viz.index, 0, _df_viz['Close'], 
                         where=(_df_viz['Position'] == 1),
                         color='#06D6A0', alpha=0.3, label='Long Position')
        _ax3.fill_between(_df_viz.index, 0, _df_viz['Close'], 
                         where=(_df_viz['Position'] == 0),
                         color='#EF476F', alpha=0.3, label='Cash/Out')
        _ax3.plot(_df_viz.index, _df_viz['Close'], color='black', linewidth=1.5, alpha=0.6, label='Price')
        _ax3.set_title('Filled Area by Position', fontsize=14, fontweight='bold', pad=10)
        _ax3.set_xlabel('Date', fontsize=11)
        _ax3.set_ylabel('Price (USD)', fontsize=11)
        _ax3.legend(loc='best', fontsize=10, framealpha=0.95)
        _ax3.grid(True, alpha=0.3, linestyle='--')
        
        # Plot 4: Position indicator subplot
        _ax4_price = _axes[1, 1]
        _ax4_pos = _ax4_price.twinx()
        
        _ax4_price.plot(_df_viz.index, _df_viz['Close'], color='#2E86AB', linewidth=2, alpha=0.8, label='Price')
        _ax4_pos.fill_between(_df_viz.index, 0, _df_viz['Position'], 
                             color='#06D6A0', alpha=0.4, step='post', label='Position (1=Long, 0=Cash)')
        
        _ax4_price.set_title('Price with Position Indicator', fontsize=14, fontweight='bold', pad=10)
        _ax4_price.set_xlabel('Date', fontsize=11)
        _ax4_price.set_ylabel('Price (USD)', fontsize=11, color='#2E86AB')
        _ax4_pos.set_ylabel('Position', fontsize=11, color='#06D6A0')
        _ax4_pos.set_ylim(-0.1, 1.1)
        _ax4_pos.set_yticks([0, 1])
        _ax4_pos.set_yticklabels(['Cash', 'Long'])
        
        _ax4_price.tick_params(axis='y', labelcolor='#2E86AB')
        _ax4_pos.tick_params(axis='y', labelcolor='#06D6A0')
        _ax4_price.grid(True, alpha=0.3, linestyle='--')
        
        # Combine legends
        _lines1, _labels1 = _ax4_price.get_legend_handles_labels()
        _lines2, _labels2 = _ax4_pos.get_legend_handles_labels()
        _ax4_price.legend(_lines1 + _lines2, _labels1 + _labels2, loc='best', fontsize=10, framealpha=0.95)
        
        plt.tight_layout()
        _viz_result = _fig_grid  # Store the figure
        plt.show()
        
        print("✅ Position visualization complete!")
    else:
        print(f"❌ Insufficient data for visualization")
    
    _viz_result
    return


@app.cell
def __(mo):
    """Footer with notes"""
    mo.md("""
    ---
    
    ## 📝 Notes
    
    - **EMA Crossover Strategy**: Goes long when fast EMA crosses above slow EMA, exits when fast crosses below slow
    - **Performance Metrics**: All returns are annualized where applicable
    - **Sharpe Ratio**: Calculated assuming 0% risk-free rate
    - **Win Rate**: Percentage of profitable trading days for the strategy
    - **Position Colors**: 🟢 Green = Long/Buy position | 🔴 Red = Cash/Sell position | 🔵 Blue = Hold (in context)
    
    💡 **Tip**: Modify the configuration cell to test different assets, time periods, or EMA parameters!
    """)
    return


if __name__ == "__main__":
    app.run()