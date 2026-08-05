import pandas as pd
import numpy as np
import vectorbt as vbt
import pickle
import warnings
warnings.filterwarnings('ignore')

# Load data
with open(r'C:\the force\03_Context\projects\trading\optimization_data.pkl', 'rb') as f:
    data = pickle.load(f)

df = data['df']
unrate_mom = data['unrate_mom']
payems_mom = data['payems_mom']

close = df['close']
print(f"Running relaxed optimization on {len(close)} bars from {close.index[0].date()} to {close.index[-1].date()}")

# Parameter grid
sma_fast_list = [20, 50, 100]
sma_slow_list = [100, 150, 200, 250]
rsi_period_list = [10, 14, 21]
rsi_bounds_list = [(30, 70), (35, 65), (40, 60), (45, 55)]
macro_gates = ['unrate_only', 'payems_only', 'both', 'neither']

# Cost parameters
slippage_pct = 0.001
commission_pct = 0.0001

results = []

from itertools import product
total_combos = len(sma_fast_list) * len(sma_slow_list) * len(rsi_period_list) * len(rsi_bounds_list) * len(macro_gates)
print(f"Total combinations to test: {total_combos}")

combo_count = 0
for sma_fast, sma_slow, rsi_period, (rsi_lower, rsi_upper), macro_gate in product(
    sma_fast_list, sma_slow_list, rsi_period_list, rsi_bounds_list, macro_gates
):
    if sma_fast >= sma_slow:
        continue
    
    combo_count += 1
    if combo_count % 50 == 0:
        print(f"  Progress: {combo_count}/{total_combos}")
    
    # Calculate indicators
    sma_fast_series = close.rolling(sma_fast).mean()
    sma_slow_series = close.rolling(sma_slow).mean()
    
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Macro gates
    if macro_gate == 'unrate_only':
        macro_cond = unrate_mom < 0
    elif macro_gate == 'payems_only':
        macro_cond = payems_mom > 0
    elif macro_gate == 'both':
        macro_cond = (unrate_mom < 0) | (payems_mom > 0)
    else:  # neither
        macro_cond = pd.Series(True, index=close.index)
    
    # Entry conditions
    cond1 = (close > sma_fast_series) & (sma_fast_series > sma_slow_series)
    cond2 = (rsi >= rsi_lower) & (rsi <= rsi_upper)
    cond3 = macro_cond
    
    entries = cond1 & cond2 & cond3
    
    # Exit
    exits = (close < sma_fast_series) | (rsi < rsi_lower) | (rsi > rsi_upper)
    
    # Run vectorbt backtest
    try:
        pf = vbt.Portfolio.from_signals(
            close=close,
            entries=entries,
            exits=exits,
            fees=slippage_pct + commission_pct,
            slippage=slippage_pct,
            init_cash=10000,
            freq='D',
            direction='longonly',
            cash_sharing=True,
            group_by=True
        )
        
        stats = pf.stats()
        
        total_return = stats.get('Total Return [%]', 0)
        sharpe = stats.get('Sharpe Ratio', 0)
        max_dd = stats.get('Max Drawdown [%]', 0)
        win_rate = stats.get('Win Rate [%]', 0)
        profit_factor = stats.get('Profit Factor', 0)
        expectancy = stats.get('Expectancy', 0)
        total_trades = stats.get('Total Trades', 0)
        
        net_pnl = total_return
        
        # Record ALL results for analysis
        results.append({
            'sma_fast': sma_fast,
            'sma_slow': sma_slow,
            'rsi_period': rsi_period,
            'rsi_lower': rsi_lower,
            'rsi_upper': rsi_upper,
            'macro_gate': macro_gate,
            'total_return': total_return,
            'sharpe': sharpe,
            'max_dd': max_dd,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'total_trades': total_trades,
            'passes_filters': (sharpe > 1.0 and 
                               abs(max_dd) < 8.0 and 
                               win_rate > 35 and 
                               net_pnl > 0 and
                               profit_factor > 1.3 and
                               expectancy > 0.5 and
                               total_trades >= 30)
        })
    except Exception as e:
        pass

print(f"\nOptimization complete. {len(results)} configurations tested.")

results_df = pd.DataFrame(results)
results_df = results_df.sort_values('sharpe', ascending=False)

print("\n=== TOP 20 BY SHARPE ===")
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
print(results_df.head(20).to_string())

print("\n=== TOP 20 BY TOTAL RETURN ===")
print(results_df.sort_values('total_return', ascending=False).head(20).to_string())

print("\n=== FILTER PASSES ===")
passed = results_df[results_df['passes_filters']]
print(f"Passed: {len(passed)}")
if len(passed) > 0:
    print(passed.to_string())
else:
    print("NONE")

# Save all results
results_df.to_csv(r'C:\the force\03_Context\projects\trading\grid_search_results_full.csv', index=False)
print("\nFull results saved to grid_search_results_full.csv")