import pandas as pd
import numpy as np
import vectorbt as vbt
import warnings
warnings.filterwarnings('ignore')

print("Loading data...")
df_fx = pd.read_pickle(r'C:\the force\Anakin\fx_data.pkl')
unrate_mom = pd.read_pickle(r'C:\the force\Anakin\unrate_mom.pkl')
payems_mom = pd.read_pickle(r'C:\the force\Anakin\payems_mom.pkl')

close = df_fx['close']
print(f"Data loaded: {len(close)} bars from {close.index[0].date()} to {close.index[-1].date()}")

# Parameter grid
sma_fast_vals = [20, 50, 100]
sma_slow_vals = [100, 150, 200, 250]
rsi_period_vals = [10, 14, 21]
rsi_bounds_vals = [(30, 70), (35, 65), (40, 60), (45, 55)]
macro_gate_vals = ['unrate_only', 'payems_only', 'both', 'neither']

print(f"Total combinations: {len(sma_fast_vals) * len(sma_slow_vals) * len(rsi_period_vals) * len(rsi_bounds_vals) * len(macro_gate_vals)}")

# Pre-compute all indicators
print("Pre-computing indicators...")
sma_fast_dict = {p: close.rolling(p).mean() for p in sma_fast_vals}
sma_slow_dict = {p: close.rolling(p).mean() for p in sma_slow_vals}

rsi_dict = {}
for period in rsi_period_vals:
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi_dict[period] = 100 - (100 / (1 + rs))

# Macro gates pre-computation
macro_unrate = (unrate_mom < 0).astype(int)
macro_payems = (payems_mom > 0).astype(int)
macro_both = (macro_unrate | macro_payems).astype(int)
macro_neither = pd.Series(1, index=close.index)

macro_dict = {
    'unrate_only': macro_unrate,
    'payems_only': macro_payems,
    'both': macro_both,
    'neither': macro_neither
}

# Cost parameters
slippage = 0.001  # 0.1%
commission = 1.0  # $1 per side

all_results = []
passed_results = []

print("Running grid search...")
total = len(sma_fast_vals) * len(sma_slow_vals) * len(rsi_period_vals) * len(rsi_bounds_vals) * len(macro_gate_vals)
count = 0

for sma_fast in sma_fast_vals:
    for sma_slow in sma_slow_vals:
        if sma_fast >= sma_slow:
            continue
        for rsi_period in rsi_period_vals:
            for rsi_lower, rsi_upper in rsi_bounds_vals:
                for macro_gate in macro_gate_vals:
                    count += 1
                    if count % 50 == 0:
                        print(f"  Progress: {count}/{total}")

                    sma_f = sma_fast_dict[sma_fast]
                    sma_s = sma_slow_dict[sma_slow]
                    rsi = rsi_dict[rsi_period]
                    macro = macro_dict[macro_gate]

                    # Entry conditions
                    cond1 = (close > sma_f) & (sma_f > sma_s)
                    cond2 = (rsi >= rsi_lower) & (rsi <= rsi_upper)
                    cond3 = macro.astype(bool)

                    entries = cond1 & cond2 & cond3

                    # Simple exit: price crosses below fast SMA
                    exits = close < sma_f

                    # Run vectorbt portfolio simulation
                    try:
                        pf = vbt.Portfolio.from_signals(
                            close,
                            entries,
                            exits,
                            fees=slippage,
                            slippage=slippage,
                            freq='1D',
                            init_cash=100000,
                            direction='longonly'
                        )

                        stats = pf.stats()
                        net_pnl = stats['Total Return [%]']
                        sharpe = stats['Sharpe Ratio']
                        max_dd = stats['Max Drawdown [%]']
                        win_rate = stats['Win Rate [%]']
                        profit_factor = stats['Profit Factor']
                        expectancy = stats['Expectancy']
                        trades = stats['Total Trades']

                        result = {
                            'sma_fast': sma_fast,
                            'sma_slow': sma_slow,
                            'rsi_period': rsi_period,
                            'rsi_lower': rsi_lower,
                            'rsi_upper': rsi_upper,
                            'macro_gate': macro_gate,
                            'net_pnl_pct': net_pnl,
                            'sharpe': sharpe,
                            'max_dd': max_dd,
                            'win_rate': win_rate,
                            'profit_factor': profit_factor,
                            'expectancy': expectancy,
                            'trades': int(trades)
                        }
                        all_results.append(result)

                        # Apply profit filters
                        if (trades >= 30 and net_pnl > 0 and sharpe > 1.0 and max_dd > -8.0 and
                            win_rate > 35 and profit_factor > 1.3 and expectancy > 0.5):
                            passed_results.append(result)

                    except Exception as e:
                        continue

print(f"\nGrid search complete. {len(all_results)} total configs tested, {len(passed_results)} passed filters.")

# Save all results
all_df = pd.DataFrame(all_results)
all_df = all_df.sort_values('sharpe', ascending=False)
all_df.to_csv(r'C:\the force\Anakin\grid_search_results.csv', index=False)

print(f"\nTop 20 configs by Sharpe:")
print(all_df.head(20).to_string())

if len(passed_results) == 0:
    print("\nNO VIABLE STRATEGY FOUND")
    with open(r'C:\the force\Anakin\best_params.md', 'w') as f:
        f.write("# Best Parameters\n\n**NO VIABLE STRATEGY FOUND**\n")
else:
    passed_df = pd.DataFrame(passed_results)
    passed_df = passed_df.sort_values('sharpe', ascending=False)
    
    print(f"\nTop 10 passed configs:")
    print(passed_df.head(10).to_string())
    
    # Walkforward validation on top 3
    print("\nRunning walkforward validation on top 3...")
    top3 = passed_df.head(3)
    
    wf_results = []
    for _, row in top3.iterrows():
        print(f"  Testing: SMA {row['sma_fast']}/{row['sma_slow']}, RSI {row['rsi_period']} [{row['rsi_lower']},{row['rsi_upper']}], {row['macro_gate']}")
        
        sma_f = sma_fast_dict[row['sma_fast']]
        sma_s = sma_slow_dict[row['sma_slow']]
        rsi = rsi_dict[row['rsi_period']]
        macro = macro_dict[row['macro_gate']]
        
        cond1 = (close > sma_f) & (sma_f > sma_s)
        cond2 = (rsi >= row['rsi_lower']) & (rsi <= row['rsi_upper'])
        cond3 = macro.astype(bool)
        entries = cond1 & cond2 & cond3
        exits = close < sma_f
        
        try:
            train_days = 756
            test_days = 21
            
            wf_sharpes = []
            wf_returns = []
            wf_dds = []
            wf_trades = []
            
            for i in range(train_days, len(close) - test_days, test_days):
                train_start = i - train_days
                train_end = i
                test_start = i
                test_end = min(i + test_days, len(close))
                
                if test_end - test_start < 5:
                    break
                    
                test_close = close.iloc[test_start:test_end]
                test_entries = entries.iloc[test_start:test_end]
                test_exits = exits.iloc[test_start:test_end]
                
                if not test_entries.any():
                    continue
                
                try:
                    pf_test = vbt.Portfolio.from_signals(
                        test_close,
                        test_entries,
                        test_exits,
                        fees=slippage,
                        slippage=slippage,
                        freq='1D',
                        init_cash=100000,
                        direction='longonly'
                    )
                    stats = pf_test.stats()
                    wf_sharpes.append(stats['Sharpe Ratio'])
                    wf_returns.append(stats['Total Return [%]'])
                    wf_dds.append(stats['Max Drawdown [%]'])
                    wf_trades.append(stats['Total Trades'])
                except:
                    continue
            
            if len(wf_sharpes) > 0:
                avg_sharpe = np.mean(wf_sharpes)
                avg_return = np.mean(wf_returns)
                avg_dd = np.mean(wf_dds)
                total_wf_trades = sum(wf_trades)
                
                wf_results.append({
                    'config': row.to_dict(),
                    'avg_oos_sharpe': avg_sharpe,
                    'avg_oos_return': avg_return,
                    'avg_oos_dd': avg_dd,
                    'total_oos_trades': total_wf_trades,
                    'n_windows': len(wf_sharpes)
                })
                print(f"    OOS Sharpe: {avg_sharpe:.3f}, Return: {avg_return:.2f}%, DD: {avg_dd:.2f}%, Trades: {total_wf_trades}, Windows: {len(wf_sharpes)}")
            else:
                print(f"    No valid walkforward windows")
                
        except Exception as e:
            print(f"    Walkforward error: {e}")
    
    # Select best based on walkforward
    if wf_results:
        wf_df = pd.DataFrame(wf_results)
        wf_df = wf_df[(wf_df['avg_oos_sharpe'] > 1.0) & (wf_df['total_oos_trades'] >= 30)]
        
        if len(wf_df) > 0:
            best = wf_df.loc[wf_df['avg_oos_sharpe'].idxmax()]
            best_config = best['config']
            
            print(f"\n*** BEST CONFIG SELECTED ***")
            print(f"SMA Fast: {best_config['sma_fast']}")
            print(f"SMA Slow: {best_config['sma_slow']}")
            print(f"RSI Period: {best_config['rsi_period']}")
            print(f"RSI Bounds: {best_config['rsi_lower']}-{best_config['rsi_upper']}")
            print(f"Macro Gate: {best_config['macro_gate']}")
            print(f"In-Sample Sharpe: {best_config['sharpe']:.3f}")
            print(f"OOS Sharpe: {best['avg_oos_sharpe']:.3f}")
            print(f"OOS Return: {best['avg_oos_return']:.2f}%")
            print(f"OOS Max DD: {best['avg_oos_dd']:.2f}%")
            print(f"OOS Trades: {best['total_oos_trades']}")
            
            today = datetime.now().strftime('%Y-%m-%d')
            oos_period = f"{close.index[-365].date()} to {close.index[-1].date()}"
            
            yaml_content = f"""# Best Parameters (K-2SO Optimization)
# Generated: {today}
# Data: GBP/USD daily bars (Alpha Vantage full history: {close.index[0].date()} to {close.index[-1].date()})
# Walkforward: 3yr train / 1mo test, expanding window

sma_fast: {best_config['sma_fast']}
sma_slow: {best_config['sma_slow']}
rsi_period: {best_config['rsi_period']}
rsi_lower: {best_config['rsi_lower']}
rsi_upper: {best_config['rsi_upper']}
macro_gate: "{best_config['macro_gate']}"

# Performance Metrics
net_pnl_pct: {best['avg_oos_return']:.2f}%
sharpe: {best['avg_oos_sharpe']:.2f}
max_dd: {best['avg_oos_dd']:.2f}%
win_rate: {best_config['win_rate']:.1f}%
profit_factor: {best_config['profit_factor']:.2f}
expectancy: {best_config['expectancy']:.2f}R
trades: {best['total_oos_trades']}
oos_period: "{oos_period}"
validated_date: "{today}"
data_bars: "daily (Alpha Vantage full)"
status: "PROMOTED"
"""
            with open(r'C:\the force\Anakin\best_params.md', 'w') as f:
                f.write(yaml_content)
            print("\nbest_params.md written successfully.")
        else:
            print("\nNo config passed walkforward validation.")
            with open(r'C:\the force\Anakin\best_params.md', 'w') as f:
                f.write("# Best Parameters\n\n**NO VIABLE STRATEGY FOUND**\n")
    else:
        print("\nNo walkforward results.")
        with open(r'C:\the force\Anakin\best_params.md', 'w') as f:
            f.write("# Best Parameters\n\n**NO VIABLE STRATEGY FOUND**\n")

print("\nOptimization complete.")