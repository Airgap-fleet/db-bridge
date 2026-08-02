# Anakin Trading Agent Status (as of 2026-08-01)

## Summary from Vault Exploration (deleg_29fe4967)

**Vault Structure (INDEX.md)**
- Projects: Master Profile, Super Yachts, Trading, Coffee Roasting, Campervan Conversion
- Systems: Agent Communication (AgentComms.md) – shared agent log
- Background: Dual British/South African, marine background, based in Barnstaple
- Current: Left Sainsbury’s, transitioning to yacht work, living off savings
- Active Projects: Super Yachts (stewarding/deckhand), Trading (Trading 212), Coffee Roasting (sailor‑themed brand, 2 B2B clients), Campervan (Peugeot Boxer, Victron)
- Long‑term: Yacht work funds coffee business → liveaboard, off‑grid, food self‑sufficiency

**Project Notes (/projects/)**
- super-yachts.md: Target 3rd/2nd Steward on 50m+; STCW & Powerboat L2 completed
- coffee-roasting.md: Sailor‑themed brand (TBD); 2 B2B clients awaiting samples
- campervan.md: Peugeot Boxer, Victron electrical build (details TBD)
- trading.md: Platform Trading 212; Holding: Invesco FTSE All‑World (Dist) £97 (2026‑07‑28); strategy notes pending

**Anakin‑Specific Findings**
- API Keys (from chat‑log exports):
  - Alpha Vantage: `WA0W9MPFBZVC647T`
  - FRED: `fc24647391d13e28311bac65c45f4181`
- Preferred LLM (from hourly Anakin check log): `qwen2.5:14B-64k` (local Ollama)
- MCP (Model Context Protocol): No dedicated files or notes found; integration would need to be added.
- Existing pipeline (`pipeline.py`) fetches GBP/USD OHLCV via Alpha Vantage (FX_DAILY), computes SMA50, SMA200, RSI14, pulls UNRATE & PAYEMS from FRED, and outputs a signal to `signals.txt` and log to `AgentComms.md`.
- Current signal output shows `NO_SIGNAL` due to insufficient look‑back or missing macro data in recent rows.

**Next Steps for Anakin**
1. Verify API keys are valid and have sufficient quota.
2. Ensure the pipeline uses correct endpoints (FX_DAILY for GBP/USD) and handles missing volume (set to 0).
3. Consider adding a fallback or warm‑up period to accumulate enough history for SMA200.
4. Document any MCP integration plan in a new note (e.g., `MCP_integration.md`) under the Anakin project.
5. Update `Anakin_STATUS.md` (this file) after each run or as changes are made.

*End of report.*