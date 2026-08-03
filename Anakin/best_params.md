# Best Parameters (K-2SO Optimization)
# Generated: 2026-08-03
# Data: GBP/USD daily bars (Alpha Vantage full history: 2007-06-01 to 2026-07-31)
# Walkforward: Not executed — no config passed initial filters

# NO VIABLE STRATEGY FOUND
# Root cause: Macro gate (monthly UNRATE/PAYEMS) over-filters daily signals
# Max trades in 19 years: 17 (threshold: 30)
# Best in-sample Sharpe: 0.187 (threshold: 1.0)

status: "REJECTED: No config passed profit filters (max trades=17, best Sharpe=0.187)"
validated_date: "2026-08-03"
data_bars: "daily (Alpha Vantage full)"
notes: |
  Macro gate creates signal sparsity: monthly economic data on daily bars
  yields near-zero simultaneous alignment of trend + RSI + macro conditions.
  Recommendation: Test without macro gate, or switch to weekly bars.