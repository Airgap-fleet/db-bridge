# Anakin Daily Review — 2026-08-03

**Status: DRIFTING** ⚠️

---

## Findings

### 🔴 Critical: SMA200 NaN — No Valid Signals Possible
- `pipeline.py:24` uses `outputsize=compact` (Alpha Vantage FX_DAILY) → returns only ~100 bars
- SMA200 requires 200+ observations → `NaN` propagates, `price > SMA50 > SMA200` always `False`
- **Fix documented in memory but not applied**: change to `outputsize=full` for 20+ years of history
- Latest signal (2026-08-02 17:20:53): `NO_SIGNAL` — SMA200: `nan`, RSI: 60.24 (barely above 60 gate)

### 🟡 Backtest Quality Below Target
- Sharpe: **0.38** (target >1.0 for K-2SO optimization loop)
- Win rate: **3.86%** — extremely low, suggests overfitting or missing exit rules
- Max DD: -5.96% (acceptable)
- No evidence of walk-forward validation, OOS testing, or transaction cost modeling
- Backtest summary lacks parameter versioning — cannot trace which params produced results

### 🟡 Pipeline Correctness Gaps
- No retry/backoff for Alpha Vantage / FRED API calls (quota/rate-limit risk)
- No position sizing, max drawdown limits, or correlation checks in signal generation
- Macro gate logic: `cond3` uses OR across UNRATE/PAYEMS — may be too permissive
- RSI bounds (40–60) very tight; RSI 60.24 fails by 0.24 points

### 🟡 K-2SO ↔ Anakin Handoff Unverified
- Memory: K-2SO (02:00 cron) reads Anakin outputs → writes `best_params.md` → Anakin (23:00) consumes
- **No `best_params.md` exists** in `Anakin/` directory
- Loop not yet tested end-to-end
- Vault as message bus: `signals.txt` written, but no param consumption logic in pipeline

### 🟢 Vault Documentation — Partial
- ✅ Signals logged to `AgentComms.md` and `signals.txt`
- ✅ `Anakin_STATUS.md` tracks state (last updated 2026-08-01)
- ❌ No versioned backtest artifacts (params, equity curve, trade list)
- ❌ No decision log for parameter changes

---

## Required Actions

| Priority | Action | Owner |
|----------|--------|-------|
| **P0** | Fix `pipeline.py:24` → `outputsize=full` | Anakin |
| **P0** | Add API retry/backoff (exponential, max 3) | Anakin |
| **P1** | Implement position sizing (vol-targeted, max 2% risk/trade) | Anakin |
| **P1** | Add walk-forward backtest with costs (spread + slippage) | Anakin/K-2SO |
| **P1** | Create `best_params.md` schema & consumption in pipeline | Anakin/K-2SO |
| **P2** | Version backtest results: `backtest_YYYY-MM-DD_params.json` | Anakin |
| **P2** | Relax RSI gate (e.g., 35–65) or make configurable | K-2SO optimization |
| **P2** | Document macro gate rationale in `pipeline.py` | Anakin |

---

## Next Review Focus
1. Verify `outputsize=full` fix deployed and SMA200 populates
2. Confirm K-2SO → Anakin param handoff working (check `best_params.md` exists and is read)
3. Walk-forward backtest results with transaction costs
4. Sharpe progression toward >1.0 target

---

## Cross-References
- [[Anakin/pipeline.py]] — source code
- [[Anakin/signals.txt]] — latest signal output
- [[Anakin/backtest_summary.txt]] — backtest metrics
- [[Anakin/Anakin_STATUS.md]] — agent status log
- [[01_Obi-Wan/state.md]] — Obi-Wan session state
- [[02_Sub-Agents/registry.md]] — K-2SO agent spec
- [[00_Master/secrets.md]] — API keys (gitignored)