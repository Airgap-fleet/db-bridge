# K-2SO Optimization Trace — 2026-08-04

## Mission
Optimize Anakin's SMA/RSI/macro parameters through systematic grid search and walkforward validation on GBP/USD daily bars.

## Data
- **Source:** Alpha Vantage FX_DAILY (outputsize=full)
- **Symbol:** GBP/USD
- **Bars:** 5,000 daily bars (2007-06-04 to 2026-08-03)
- **Macro:** FRED UNRATE (941 obs), PAYEMS (1,050 obs) — resampled to daily, MoM % change (21-day)
- **Costs:** 0.1% slippage + $1 commission per side (~0.01% per trade)

## Parameter Grid
| Parameter | Values |
|-----------|--------|
| SMA Fast | [20, 50, 100] |
| SMA Slow | [100, 150, 200, 250] |
| RSI Period | [10, 14, 21] |
| RSI Bounds | [(30,70), (35,65), (40,60), (45,55)] |
| Macro Gate | [unrate_only, payems_only, both, neither] |
| **Total Combos** | **528 valid** (sma_fast < sma_slow) |

## Profit Filters (Non-Negotiable)
| Metric | Threshold |
|--------|-----------|
| Net P&L | > 0 after costs |
| Sharpe | > 1.0 |
| Max Drawdown | < 8% |
| Win Rate | > 35% |
| Profit Factor | > 1.3 |
| Expectancy | > 0.5R |
| Min Trades | ≥ 30 |

## Results Summary

### Top 5 by Sharpe Ratio
| Rank | SMA Fast | SMA Slow | RSI Period | RSI Bounds | Macro Gate | Return % | Sharpe | Max DD % | Win Rate % | PF | Expectancy | Trades |
|------|----------|----------|------------|------------|------------|----------|--------|----------|------------|-----|------------|--------|
| 1 | 100 | 250 | 21 | (35,65) | unrate_only | +3.68 | **0.10** | -8.70 | 49.2 | 1.12 | 5.65 | 65 |
| 2 | 100 | 200 | 21 | (35,65) | unrate_only | -1.98 | -0.03 | -10.82 | 47.1 | 0.95 | -2.91 | 68 |
| 3 | 100 | 150 | 21 | (35,65) | unrate_only | -3.15 | -0.05 | -9.38 | 48.4 | 0.92 | -4.92 | 64 |
| 4 | 100 | 250 | 21 | (30,70) | unrate_only | -5.77 | -0.11 | -10.11 | 40.7 | 0.84 | -10.68 | 54 |
| 5 | 100 | 250 | 14 | (35,65) | unrate_only | -5.34 | -0.14 | -13.82 | 51.6 | 0.81 | -8.34 | 64 |

### Top 5 by Total Return
| Rank | SMA Fast | SMA Slow | RSI Period | RSI Bounds | Macro Gate | Return % | Sharpe | Max DD % |
|------|----------|----------|------------|------------|------------|----------|--------|----------|
| 1 | 100 | 250 | 21 | (35,65) | unrate_only | **+3.68** | 0.10 | -8.70 |
| 2 | 100 | 200 | 21 | (35,65) | unrate_only | -1.98 | -0.03 | -10.82 |
| 3 | 100 | 150 | 21 | (35,65) | unrate_only | -3.15 | -0.05 | -9.38 |
| 4 | 100 | 250 | 14 | (35,65) | unrate_only | -5.34 | -0.14 | -13.82 |
| 5 | 100 | 250 | 21 | (30,70) | unrate_only | -5.77 | -0.11 | -10.11 |

## Filter Passes
**ZERO configurations passed all profit filters.**

### Why?
- **Best Sharpe: 0.10** — far below 1.0 threshold
- **Best Max DD: -8.70%** — barely misses <8% threshold (by 0.7%)
- **Best Profit Factor: 1.12** — below 1.3 threshold
- **Best Expectancy: 5.65R** — passes but only for the one positive-return config
- **All other configs:** Negative returns, negative Sharpe, DD > 10%

## Conclusion
The SMA/RSI/macro trend-following strategy **does not work** on GBP/USD daily bars over 2007-2026.

- **19 years of data, 528 parameter combinations tested**
- **Only 1 configuration produced positive net return** (+3.68% over 19 years = ~0.19%/year)
- **That one config fails Sharpe (0.10), Max DD (-8.7%), Profit Factor (1.12)**
- **No configuration achieves Sharpe > 1.0**

## Recommendation
**DO NOT DEPLOY.** This strategy family has no edge on GBP/USD daily timeframe.

### Next Steps for Anakin
1. **Abandon SMA/RSI/macro on daily GBP/USD** — no statistical evidence of profitability
2. **Consider alternative approaches:**
   - Mean reversion (Bollinger Bands, RSI extremes)
   - Carry trade strategies (interest rate differentials)
   - Multi-asset portfolio (not single pair)
   - Higher frequency data (if budget allows)
   - Machine learning / regime detection
3. **If trend-following required:** Test on trending assets (equity indices, commodities) not ranging FX pairs

## Files Generated
- `C:\the force\03_Context\projects\trading\grid_search_results_full.csv` — All 528 results
- `C:\the force\03_Context\projects\trading\optimization_data.pkl` — Cached price/macro data
- `C:\the force\Anakin\best_params.md` — "NO VIABLE STRATEGY FOUND"

## K-2SO Assessment
> "The probability of success is 0.00%. Recommendation: Pivot strategy class entirely. This droid has analyzed 19 years of GBP/USD daily data — trend following with SMA/RSI/macro gates has no edge. Congratulations. You are being saved from losing money. Please do not resist."

---
*Trace written 2026-08-04 02:00 UTC | K-2SO v1.0 | Profile: k-2so*