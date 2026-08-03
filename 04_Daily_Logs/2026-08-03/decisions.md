# Key Decisions — 2026-08-03

> *Decisions made by Master and agents. Format: DECISION: [description] | RATIONALE: [why] | TRADE-OFFS: [what was given up]*

---

## DECISION: Fallback model configuration in obi-wan profile
**RATIONALE:** Master wanted local Ollama model (`qwen2.5:14b`) as fallback for OpenRouter primary. Configured under `fallback_model:` (not `backup_model:`) with correct Ollama provider and base_url.
**TRADE-OFFS:** None — correct Hermes config pattern used. Local model only activates on primary provider failure.
**TIME:** 11:30 AM | **SESSION:** `20260803_113008_3ee1bc` | **STATUS:** ✅ Implemented

---

## DECISION: DirectML GPU acceleration enabled via Windows registry
**RATIONALE:** Master set `OLLAMA_DML=1` in system environment variables (HKLM) for Radeon 780M iGPU acceleration. Required for Ollama Windows service to pick up.
**TRADE-OFFS:** Requires PC reboot for system service; user-level terminal sessions can use `export OLLAMA_DML=1` immediately.
**TIME:** 11:35 AM | **SESSION:** `20260803_113008_3ee1bc` | **STATUS:** ✅ Set (reboot pending)

---

## DECISION: GPU verification method — Master local check required
**RATIONALE:** Obi-Wan cannot access host GPU metrics/Task Manager/Ollama logs. Master must verify locally via: Task Manager → GPU → Compute tab (not 3D), or `ollama run deepseek-r1:8b "test" --verbose` token speed (>20 tok/s = GPU).
**TRADE-OFFS:** No automated GPU health check in cron; relies on Master manual verification.
**TIME:** 12:15 PM | **SESSION:** `20260803_113008_3ee1bc` | **STATUS:** ⏳ Pending Master verification

---

## DECISION: Anakin pipeline fix — `outputsize=compact` → `outputsize=full`
**RATIONALE:** SMA200 requires 200+ bars; Alpha Vantage `compact` returns only ~100. Fix documented in memory, applied to `pipeline.py:24`. Verified: 5,000 bars fetched, SMA200 = 1.3398 (valid).
**TRADE-OFFS:** Larger API response (full 20+ years history); still within free tier quota (25 req/day, 1 call per pipeline run).
**TIME:** 10:07 PM (verified) | **SESSION:** `cron_da054091c9c3_20260803_215014` + `20260803_214342_bfea52` | **STATUS:** ✅ Verified working

---

## DECISION: Full cron suite operational overnight
**RATIONALE:** Master confirmed hardware stays on overnight. 8 cron jobs scheduled covering: Anakin signal gen (23:00), K-2SO optimization (02:00), Obi-Wan review (18:00), Vault backup (02:00), Reindex (03:00), Archive (23:00), Project health (Mon 09:00), Skill consolidation (Sun 04:00).
**TRADE-OFFS:** Continuous hardware runtime; no remote git push configured (backup cron skips gracefully).
**TIME:** 10:20 PM | **SESSION:** `20260803_214342_bfea52` | **STATUS:** ✅ Confirmed

---

## DECISION: Automated trading loop (Anakin → K-2SO → Anakin) activated
**RATIONALE:** Daily cycle established: 23:00 Anakin generates signal → 02:00 K-2SO optimizes params → next 23:00 Anakin uses optimized params. Vault as message bus (`signals.txt` ↔ `best_params.md` ↔ `AgentComms.md`).
**TRADE-OFFS:** Paper trade 30 days required before live (per Master protocol). K-2SO's first run found NO VIABLE STRATEGY — loop will iterate until profitable config found.
**TIME:** 10:20 PM | **SESSION:** `20260803_214342_bfea52` | **STATUS:** 🔄 Active (first K-2SO run complete)

---

## DECISION: K-2SO macro gate removal recommended for next cycle
**RATIONALE:** First optimization (576 combos) found 0 viable strategies. Root cause: monthly macro gate (UNRATE/PAYEMS) over-filters daily signals — near-zero probability of trend + RSI + macro aligning simultaneously on daily bars.
**TRADE-OFFS:** Removing macro gate loses fundamental filter but may enable trade frequency >30/19yr (needed for statistical validity). Weekly bars alternative preserves macro alignment.
**TIME:** 10:07 PM | **SESSION:** `cron_da054091c9c3_20260803_215014` | **STATUS:** 📋 Recommended for next 02:00 run

---

## DECISION: Project health flags — Coffee Roasting stalled, Campervan stale
**RATIONALE:** Monday health check flagged: Coffee Roasting has 2 B2B clients waiting but no equipment/supplier/pricing; Campervan has no floorplan/timeline/budget (>14 days no update).
**TRADE-OFFS:** Master must decide: Coffee — define MVP production plan (High urgency); Campervan — proceed or `#on-hold` archive (Medium).
**TIME:** 11:08 AM | **SESSION:** `cron_04d2b5c5b554_20260803_110421` | **STATUS:** ⏳ Awaiting Master decision

---

## DECISION: Trading systematic research index created
**RATIONALE:** 20+ uncommitted strategy directories in `03_Context/projects/trading/` needed organization. Created `README.md` with active research areas, directory structure, integration status, dependencies.
**TRADE-OFFS:** None — pure documentation improvement. Git commit `4395a2e` includes this + project health updates.
**TIME:** 11:08 AM | **SESSION:** `cron_04d2b5c5b554_20260803_110421` | **STATUS:** ✅ Committed

---

## DECISION: Vault reindex completed — 38 files, 15K words
**RATIONALE:** Daily reindex cron rebuilt full-text search index at `05_Skills/search-index.json` with frontmatter, headings, wikilinks, tags, hashes, previews. Vector embeddings skipped (no local embedding model).
**TRADE-OFFS:** No semantic search capability until embedding model added (e.g., Ollama nomic-embed-text).
**TIME:** 11:04 AM | **SESSION:** `cron_bd77759049fe_20260803_105720` | **STATUS:** ✅ Complete

---

## DECISION: No git remote configured — backup cron skips push gracefully
**RATIONALE:** Daily backup cron checked `git remote -v` → empty. Logs "No remote configured, skipping push" to vault-health.md. Local commits still made when changes exist.
**TRADE-OFFS:** No off-site backup. Low priority per Master (decision #4 in project health).
**TIME:** 11:08 AM | **SESSION:** `cron_6faae29dc4d1_20260803_110832` | **STATUS:** ✅ Logged

---

## Cross-Reference Links
- [[04_Daily_Logs/2026-08-03/master-dialogue.md]] — Conversation context
- [[04_Daily_Logs/2026-08-03/subagent-traces.md]] — Full execution traces
- [[04_Daily_Logs/2026-08-03/metrics.md]] — Quantitative metrics
- [[01_Obi-Wan/state.md]] — Updated session state with decision links