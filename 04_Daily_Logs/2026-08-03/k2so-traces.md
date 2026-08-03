# K-2SO Daily Optimization Trace — 2026-08-03

## Mission
Optimize Anakin's SMA/RSI/macro parameters through systematic grid search and walkforward validation on GBP/USD daily bars. Write winning configuration to `best_params.md` for Anakin's next 23:00 run.

## Data
- **Source:** Alpha Vantage FX_DAILY (outputsize=full) — 5,000 bars, 2007-06-01 to 2026-07-31
- **Macro:** FRED UNRATE (941 obs), PAYEMS (1,050 obs) — forward-filled to FX calendar
- **Costs:** 0.1% slippage + $1 commission per side

## Parameter Grid
| Parameter | Values Tested |
|-----------|---------------|
| SMA Fast | [20, 50, 100] |
| SMA Slow | [100, 150, 200, 250] |
| RSI Period | [10, 14, 21] |
| RSI Bounds | [(30,70), (35,65), (40,60), (45,55)] |
| Macro Gate | [unrate_only, payems_only, both, neither] |
| **Total Combinations** | **576** (after sma_fast < sma_slow filter) |

## Profit Filters (Non-Negotiable)
- Net P&L > 0 after costs
- Sharpe > 1.0
- Max Drawdown < 8%
- Win Rate > 35%
- Profit Factor > 1.3
- Expectancy > 0.5R per trade
- Minimum 30 trades in validation window

## Grid Search Results
**Total configs tested:** 576  
**Configs passing all filters:** 0  

### Top 10 by Sharpe Ratio
| Rank | SMA Fast | SMA Slow | RSI Period | RSI Bounds | Macro Gate | Net P&L% | Sharpe | Max DD% | Win Rate% | PF | Expectancy | Trades |
|------|----------|----------|------------|------------|------------|----------|--------|---------|-----------|-----|------------|--------|
| 1 | 100 | 200 | 14 | (35,65) | unrate_only | +6.42 | 0.187 | -5.57 | 37.5 | 1.95 | 801.9R | 8 |
| 2 | 100 | 200 | 14 | (40,60) | unrate_only | +6.42 | 0.187 | -5.57 | 37.5 | 1.95 | 801.9R | 8 |
| 3 | 100 | 150 | 14 | (40,60) | unrate_only | +5.94 | 0.173 | -5.60 | 37.5 | 1.82 | 743.0R | 8 |
| 4 | 100 | 150 | 14 | (35,65) | unrate_only | +5.94 | 0.173 | -5.60 | 37.5 | 1.82 | 743.0R | 8 |
| 5 | 100 | 200 | 21 | (30,70) | unrate_only | +5.09 | 0.141 | -6.28 | 44.4 | 1.52 | 565.5R | 9 |
| 6 | 100 | 250 | 14 | (35,65) | unrate_only | +2.87 | 0.096 | -6.04 | 42.9 | 1.48 | 409.8R | 7 |
| 7 | 100 | 250 | 14 | (45,55) | unrate_only | +2.35 | 0.090 | -4.82 | 50.0 | 1.50 | 391.3R | 6 |
| 8 | 100 | 250 | 14 | (40,60) | unrate_only | +2.35 | 0.090 | -4.82 | 50.0 | 1.50 | 391.3R | 6 |
| 9 | 100 | 200 | 14 | (30,70) | unrate_only | +2.49 | 0.077 | -6.28 | 30.0 | 1.24 | 249.0R | 10 |
| 10 | 100 | 200 | 14 | (45,55) | unrate_only | +1.50 | 0.061 | -5.61 | 42.9 | 1.27 | 214.3R | 7 |

### Critical Failure Modes
1. **Insufficient Trade Frequency** — Maximum 17 trades across 19 years (2007-2026). Minimum threshold: 30 trades.
2. **Sharpe Ratio Nowhere Near Target** — Best in-sample Sharpe: 0.187. Target: > 1.0.
3. **Macro Gate Over-Filtering** — UNRATE/PAYEMS monthly data on daily bars creates sparse signals. Only 6-17 trades in 19 years.
4. **Exit Condition Too Aggressive** — Price < fast SMA exits truncate trends prematurely.

## Walkforward Validation
**Not executed** — No config passed initial filters to qualify for walkforward stage.

## Conclusion
**NO VIABLE STRATEGY FOUND** — The current parameter space and strategy logic (SMA trend + RSI mean-reversion + macro gate) cannot produce a statistically valid edge on GBP/USD daily bars with Alpha Vantage free-tier data.

### Root Cause
The macro gate (UNRATE falling / PAYEMS rising) uses **monthly** economic data aligned to **daily** price bars. This creates a signal sparsity problem: the macro condition changes only ~12 times per year, but the strategy requires simultaneous alignment of:
- Price > SMA_fast > SMA_slow (trend)
- RSI in bounds (mean-reversion)
- Macro gate active (monthly)

Probability of all three aligning = near zero on daily frequency.

### Recommendations for Next Cycle
1. **Remove macro gate** or use it as a regime filter (not entry gate) — test `macro_gate: neither` baseline
2. **Switch to weekly bars** — aligns better with monthly macro frequency
3. **Add trend-following exits** (trailing stop, ATR-based) instead of SMA cross
4. **Expand parameter space** — test SMA_fast [5, 10, 20] for higher trade frequency
5. **Consider intraday data** — but requires paid Alpha Vantage tier

## Artifacts Written
- `C:\the force\Anakin\best_params.md` → **NO VIABLE STRATEGY FOUND**
- `C:\the force\Anakin\grid_search_results.csv` → Full 576-row results
- `C:\the force\Anakin\optimize_v2.py` → Optimization script

## Next Run
Scheduled: 2026-08-04 02:00 (next daily cron)
Will re-test with adjusted parameter space per recommendations above.

---
*Probability of success with current approach: <5%. Recommendation: Structural strategy revision required.*