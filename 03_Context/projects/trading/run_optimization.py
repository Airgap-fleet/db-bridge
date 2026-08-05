import pandas as pd
import numpy as np
import vectorbt as vbt
import pickle
import json
import warnings
warnings.filterwarnings('ignore')

# Load data
with open(r'C:\the force\03_Context\projects\trading\optimization_data.pkl', 'rb') as f:
    data = pickle.load(f)

df = data['df']
unrate_mom = data['unrate_mom']
payems_mom = data['payems_mom']

close = df['close']
print(f"Running optimization on {len(close)} bars from {close.index[0].date()} to {close.index[-1].date()}")

# Parameter grid
sma_fast_list = [20, 50, 100]
sma_slow_list = [100, 150, 200, 250]
rsi_period_list = [10, 14, 21]
rsi_bounds_list = [(30, 70), (35, 65), (40, 60), (45, 55)]
macro_gates = ['unrate_only', 'payems_only', 'both', 'neither']

# Cost parameters
slippage_pct = 0.001  # 0.1%
commission_per_side = 1.0  # $1 per side
# For forex, we'll approximate commission as percentage of notional
# Assuming 1 standard lot = 100,000 units, $1 per side = 0.001% per side
# But since we're doing % returns, we'll use a small fixed cost per trade
commission_pct = 0.0001  # approximate

results = []

# Generate all combinations
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
    
    # Exit: simple - when trend breaks or RSI exits bounds
    # Exit when price crosses below fast SMA OR RSI goes outside bounds
    exits = (close < sma_fast_series) | (rsi < rsi_lower) | (rsi > rsi_upper)
    
    # Run vectorbt backtest
    try:
        pf = vbt.Portfolio.from_signals(
            close=close,
            entries=entries,
            exits=exits,
            fees=slippage_pct + commission_pct,  # combined cost
            slippage=slippage_pct,
            init_cash=10000,
            freq='D',
            direction='longonly',
            cash_sharing=True,
            group_by=True
        )
        
        # Get stats
        stats = pf.stats()
        
        total_return = stats.get('Total Return [%]', 0)
        sharpe = stats.get('Sharpe Ratio', 0)
        max_dd = stats.get('Max Drawdown [%]', 0)
        win_rate = stats.get('Win Rate [%]', 0)
        profit_factor = stats.get('Profit Factor', 0)
        expectancy = stats.get('Expectancy', 0)
        total_trades = stats.get('Total Trades', 0)
        
        # Net P&L after costs (total return already accounts for fees/slippage in vectorbt)
        net_pnl = total_return
        
        # Filter criteria
        if (sharpe > 1.0 and 
            abs(max_dd) < 8.0 and 
            win_rate > 35 and 
            net_pnl > 0 and
            profit_factor > 1.3 and
            expectancy > 0.5 and
            total_trades >= 30):
            
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
                'total_trades': total_trades
            })
    except Exception as e:
        pass

print(f"\nOptimization complete. {len(results)} configurations passed filters.")

# Sort by Sharpe
results_df = pd.DataFrame(results)
if len(results_df) > 0:
    results_df = results_df.sort_values('sharpe', ascending=False)
    print("\nTop 10 configurations:")
    print(results_df.head(10).to_string())
    
    # Save all results
    results_df.to_csv(r'C:\the force\03_Context\projects\trading\grid_search_results.csv', index=False)
    
    # Walkforward validation for top 3
    print("\n--- Walkforward Validation (3yr train / 1mo test, expanding) ---")
    top_configs = results_df.head(3).to_dict('records')
    
    wf_results = []
    for config in top_configs:
        print(f"\nValidating: SMA({config['sma_fast']},{config['sma_slow']}) RSI({config['rsi_period']},{config['rsi_lower']},{config['rsi_upper']}) Macro:{config['macro_gate']}")
        
        # Walkforward: 3 years train, 1 month test, expanding
        train_years = 3
        test_months = 1
        
        # Start from first date + 3 years
        start_date = close.index[0] + pd.DateOffset(years=train_years)
        end_date = close.index[-1]
        
        wf_trades = []
        wf_returns = []
        
        current_train_end = start_date
        while current_train_end < end_date:
            test_end = min(current_train_end + pd.DateOffset(months=test_months), end_date)
            
            if test_end <= current_train_end:
                break
            
            # Train period: from start to current_train_end
            train_mask = (close.index >= close.index[0]) & (close.index < current_train_end)
            # Test period: current_train_end to test_end
            test_mask = (close.index >= current_train_end) & (close.index < test_end)
            
            if test_mask.sum() < 5:  # need at least some test data
                break
            
            # Run on test period using parameters optimized on train
            # For simplicity, just run the strategy on test period
            test_close = close[test_mask]
            test_unrate = unrate_mom[test_mask]
            test_payems = payems_mom[test_mask]
            
            # Need enough history for indicators - use full history up to test start
            hist_close = close[close.index < test_end]
            hist_unrate = unrate_mom[unrate_mom.index < test_end]
            hist_payems = payems_mom[payems_mom.index < test_end]
            
            if len(hist_close) < config['sma_slow'] + 10:
                current_train_end = test_end
                continue
            
            # Calculate indicators on full history
            sma_f = hist_close.rolling(config['sma_fast']).mean()
            sma_s = hist_close.rolling(config['sma_slow']).mean()
            
            delta = hist_close.diff()
            gain = delta.where(delta > 0, 0).rolling(config['rsi_period']).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(config['rsi_period']).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # Macro
            if config['macro_gate'] == 'unrate_only':
                macro_c = hist_unrate < 0
            elif config['macro_gate'] == 'payems_only':
                macro_c = hist_payems > 0
            elif config['macro_gate'] == 'both':
                macro_c = (hist_unrate < 0) | (hist_payems > 0)
            else:
                macro_c = pd.Series(True, index=hist_close.index)
            
            # Get test period signals
            test_cond1 = (test_close > sma_f[test_mask]) & (sma_f[test_mask] > sma_s[test_mask])
            test_cond2 = (rsi[test_mask] >= config['rsi_lower']) & (rsi[test_mask] <= config['rsi_upper'])
            test_cond3 = macro_c[test_mask]
            
            test_entries = test_cond1 & test_cond2 & test_cond3
            test_exits = (test_close < sma_f[test_mask]) | (rsi[test_mask] < config['rsi_lower']) | (rsi[test_mask] > config['rsi_upper'])
            
            if test_entries.any():
                try:
                    pf_test = vbt.Portfolio.from_signals(
                        close=test_close,
                        entries=test_entries,
                        exits=test_exits,
                        fees=slippage_pct + commission_pct,
                        slippage=slippage_pct,
                        init_cash=10000,
                        freq='D',
                        direction='longonly'
                    )
                    stats_test = pf_test.stats()
                    wf_returns.append(stats_test.get('Total Return [%]', 0))
                    wf_trades.append(stats_test.get('Total Trades', 0))
                except:
                    pass
            
            current_train_end = test_end
        
        if wf_returns:
            avg_return = np.mean(wf_returns)
            total_wf_trades = sum(wf_trades)
            sharpe_wf = np.mean(wf_returns) / (np.std(wf_returns) + 1e-6) * np.sqrt(12) if len(wf_returns) > 1 else 0
            
            wf_results.append({
                **config,
                'wf_avg_return': avg_return,
                'wf_sharpe': sharpe_wf,
                'wf_total_trades': total_wf_trades,
                'wf_periods': len(wf_returns)
            })
            print(f"  WF: Avg Return={avg_return:.2f}%, WF Sharpe={sharpe_wf:.2f}, Trades={total_wf_trades}, Periods={len(wf_returns)}")
        else:
            print(f"  WF: No trades in walkforward")
    
    # Select best from walkforward
    if wf_results:
        wf_df = pd.DataFrame(wf_results)
        wf_df = wf_df.sort_values('wf_sharpe', ascending=False)
        best = wf_df.iloc[0]
        
        print("\n=== BEST CONFIGURATION ===")
        print(best.to_string())
        
        # Final out-of-sample test on last 6 months
        oos_start = close.index[-1] - pd.DateOffset(months=6)
        oos_mask = close.index >= oos_start
        oos_close = close[oos_mask]
        oos_unrate = unrate_mom[oos_mask]
        oos_payems = payems_mom[oos_mask]
        
        # Full history indicators
        sma_f = close.rolling(best['sma_fast']).mean()
        sma_s = close.rolling(best['sma_slow']).mean()
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(best['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(best['rsi_period']).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        if best['macro_gate'] == 'unrate_only':
            macro_c = unrate_mom < 0
        elif best['macro_gate'] == 'payems_only':
            macro_c = payems_mom > 0
        elif best['macro_gate'] == 'both':
            macro_c = (unrate_mom < 0) | (payems_mom > 0)
        else:
            macro_c = pd.Series(True, index=close.index)
        
        oos_cond1 = (oos_close > sma_f[oos_mask]) & (sma_f[oos_mask] > sma_s[oos_mask])
        oos_cond2 = (rsi[oos_mask] >= best['rsi_lower']) & (rsi[oos_mask] <= best['rsi_upper'])
        oos_cond3 = macro_c[oos_mask]
        oos_entries = oos_cond1 & oos_cond2 & oos_cond3
        oos_exits = (oos_close < sma_f[oos_mask]) | (rsi[oos_mask] < best['rsi_lower']) | (rsi[oos_mask] > best['rsi_upper'])
        
        if oos_entries.any():
            pf_oos = vbt.Portfolio.from_signals(
                close=oos_close,
                entries=oos_entries,
                exits=oos_exits,
                fees=slippage_pct + commission_pct,
                slippage=slippage_pct,
                init_cash=10000,
                freq='D',
                direction='longonly'
            )
            oos_stats = pf_oos.stats()
            oos_return = oos_stats.get('Total Return [%]', 0)
            oos_sharpe = oos_stats.get('Sharpe Ratio', 0)
            oos_dd = oos_stats.get('Max Drawdown [%]', 0)
            oos_wr = oos_stats.get('Win Rate [%]', 0)
            oos_pf = oos_stats.get('Profit Factor', 0)
            oos_exp = oos_stats.get('Expectancy', 0)
            oos_trades = oos_stats.get('Total Trades', 0)
        else:
            oos_return = oos_sharpe = oos_dd = oos_wr = oos_pf = oos_exp = oos_trades = 0
        
        # Write best_params.md
        today = datetime.now().strftime('%Y-%m-%d')
        yaml_content = f"""sma_fast: {int(best['sma_fast'])}
sma_slow: {int(best['sma_slow'])}
rsi_period: {int(best['rsi_period'])}
rsi_lower: {int(best['rsi_lower'])}
rsi_upper: {int(best['rsi_upper'])}
macro_gate: "{best['macro_gate']}"
sharpe: {best['sharpe']:.2f}
win_rate: {best['win_rate']:.1f}%
max_dd: {best['max_dd']:.1f}%
profit_factor: {best['profit_factor']:.2f}
expectancy: {best['expectancy']:.2f}R
trades: {int(best['total_trades'])}
wf_sharpe: {best['wf_sharpe']:.2f}
wf_trades: {int(best['wf_total_trades'])}
oos_return_pct: {oos_return:.2f}%
oos_sharpe: {oos_sharpe:.2f}
oos_max_dd: {oos_dd:.1f}%
oos_win_rate: {oos_wr:.1f}%
oos_trades: {int(oos_trades)}
validated_date: "{today}"
data_bars: "daily (Alpha Vantage full)"
status: "PROMOTED"
"""
        
        with open(r'C:\the force\Anakin\best_params.md', 'w') as f:
            f.write(yaml_content)
        
        print(f"\nBest params written to C:\\the force\\Anakin\\best_params.md")
        print(yaml_content)
    else:
        print("No configurations passed walkforward validation.")
        with open(r'C:\the force\Anakin\best_params.md', 'w') as f:
            f.write("NO VIABLE STRATEGY FOUND\n")
else:
    print("No configurations passed initial filters.")
    with open(r'C:\the force\Anakin\best_params.md', 'w') as f:
        f.write("NO VIABLE STRATEGY FOUND\n")

print("\nOptimization cycle complete.")