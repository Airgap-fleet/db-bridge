# Systematic Trading Research

## Overview
Quantitative strategy research and backtesting framework. 20+ strategy directories covering Faber trend-following, macro factors, momentum, walkforward validation, volatility targeting, and multi-asset allocation.

## Active Research Areas
- **Faber Trend-Following Variants**: Original, expanded universe, IVOL-adjusted, macro-filtered, leveraged-capped
- **Walkforward Validation**: Multiple windows (3yr/1mo, expanding, fixed SMA200/vol60/252, slow)
- **Macro Factor Integration**: Unemployment, yield curve, multi-factor combinations
- **Volatility Targeting**: Fixed vol, expanded comparison, IVOL adjustments
- **Parameter Optimization**: Grid search (faber, alt vol, focused, refined), multi-asset IVOL

## Latest Activity
- `grid_search_faber.py` modified 2026-08-03
- `grid_search_alt_vol.py` modified 2026-08-03
- `walkforward_expanded_48assets` updated 2026-08-02

## Health Status (2026-08-03)
- **Status**: 🟢 Very Active
- **Last Activity**: 2026-08-03
- **Flags**: 20+ strategy directories; uncommitted changes; no research→deployment pipeline documented
- **Next Actions**: Commit winning configs to git; document research-to-live pipeline; paper-trade validation before live allocation

## Directory Structure
```
03_Context/projects/trading/
├── *.py                 # Grid search and analysis scripts
├── *_faber*/            # Faber strategy variants
├── *_walkforward*/      # Walkforward validation studies
├── *_macro*/            # Macro factor tests
├── *_vol*/              # Volatility targeting
├── *_momentum*/         # Momentum strategies
├── *_multifactor*/      # Multi-factor combinations
├── *_param*/            # Parameter optimization
├── *_strategy_combo*/   # Strategy combinations
└── __pycache__/         # Python cache (ignored)
```

## Integration Status
- **Discretionary Account (Trading 212)**: Not connected
- **Paper Trading**: Not configured
- **Live Deployment**: No pipeline defined
- **Git Tracking**: Uncommitted (experimental directories)

## Dependencies
- Python: pandas, numpy, yfinance, vectorbt (implied)
- Data: Yahoo Finance (yfinance)
- Compute: Local (no cloud infrastructure)