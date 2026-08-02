# Decisions — 2026-08-02

> *Key choices, rationale, and trade-offs recorded during daily archive*

---

## DECISION: Vault Location — `C:\the force`

**Date:** 2026-08-02 17:02  
**Context:** Initial vault setup during Obi-Wan initialization  
**Options Considered:**
1. `C:\the force` (chosen) — Short, memorable, Star Wars themed
2. `~/Documents/Obsidian Vault` — Default Obsidian location
3. `C:\Users\brook\Obsidian Vault` — User profile standard

**Rationale:** Master explicitly chose `C:\the force` for brevity and thematic consistency. Path is short, no spaces, easy to type in terminal.

**Trade-offs:** Non-standard location requires explicit path resolution in scripts/cron. Mitigated by hardcoding in cron job configs and delegation contracts.

**Vault Ref:** `01_Obi-Wan/identity.md`, `00_Master/profile.md`

---

## DECISION: Vault Directory Structure — Canonical Layout

**Date:** 2026-08-02 17:02  
**Context:** Establishing persistent memory architecture  
**Decision:** Adopted canonical 7-folder structure from `vault-agent-orchestration` skill:

```
00_Master/           # User profile & protocols
01_Obi-Wan/          # Orchestrator core memory
02_Sub-Agents/       # Sub-agent memories (shared)
03_Context/          # Environmental knowledge
04_Daily_Logs/       # Cron-recorded conversations
05_Skills/           # Learned procedures
06_Archive/          # Cold storage
```

**Rationale:** Proven pattern from skill documentation. Enables clear separation of concerns, predictable delegation output paths, and scalable archival.

**Trade-offs:** Requires discipline to maintain structure. Automated via archivist cron and skill extraction protocol.

**Vault Ref:** `01_Obi-Wan/identity.md`, `02_Sub-Agents/registry.md`

---

## DECISION: Sub-Agent Specializations — 6 Core Templates

**Date:** 2026-08-02 17:02  
**Context:** Defining delegation capabilities  
**Decision:** Created 6 specialization templates in `02_Sub-Agents/templates/`:

| Template | Role | Vault Write Scope |
|----------|------|-------------------|
| `researcher.md` | Deep research, synthesis | `03_Context/references/`, `04_Daily_Logs/` |
| `coder-backend.md` | APIs, databases, services | `03_Context/projects/backend/` |
| `coder-frontend.md` | React, TypeScript, UI | `03_Context/projects/frontend/` |
| `devops.md` | CI/CD, infra, monitoring | `03_Context/projects/infra/` |
| `analyst.md` | Metrics, reporting, insights | `04_Daily_Logs/`, `03_Context/references/` |
| `archivist.md` | Vault maintenance, linking | Entire vault (maintenance) |

**Rationale:** Covers full software development + research + maintenance lifecycle. Each has distinct toolset and vault scope to prevent conflicts.

**Trade-offs:** 6 templates may be more than immediately needed. Kept for readiness — activation on-demand per Master directive.

**Vault Ref:** `02_Sub-Agents/registry.md`, `01_Obi-Wan/capabilities.md`

---

## DECISION: Anakin Soul Specification — Quant Analyst with MCP Integration

**Date:** 2026-08-02 18:26  
**Context:** Master requested Anakin (quant analyst) profile with trading focus  
**Decision:** Created comprehensive soul spec at `C:\Users\brook\Obi-Wan_SOUL.md` (for copy-paste to Anakin's profile) including:

- **Model:** Nemotron 3 Ultra 120B (OpenRouter) — distinct from Obi-Wan's Nemotron 550B
- **MCP Integration Layer:** TradingView (chart analysis, screeners, backtesting), Broker APIs (BitGet, OKX execution), News/Sentiment (OpenNews-MCP)
- **Methodology:** 7-phase signal generation protocol (Hypothesis → Data → Features → Backtest → Validate → Deploy → Monitor)
- **Vault Write Scope:** `03_Context/projects/trading/`, `04_Daily_Logs/analysis-*.md`
- **Daily Cron:** Anakin Alignment Review at 18:00

**Rationale:** MCP research revealed 9 active trading repos (Vibe-Trading 29.3k★, TradingView-MCP 5.4k★). Leveraging existing MCP servers avoids building from scratch.

**Trade-offs:** Requires Anakin to learn MCP client operations. Added to specialization table as "Proficient" with stdio/SSE, tool calling, resource access.

**Vault Ref:** `C:\Users\brook\Obi-Wan_SOUL.md`, `01_Obi-Wan/lessons.md`

---

## DECISION: Cron Job Suite — 6 Automated Maintenance Jobs

**Date:** 2026-08-02 17:03  
**Context:** Establishing hands-off vault maintenance  
**Decision:** Scheduled 6 cron jobs via `cronjob` tool:

| Job | Schedule | Purpose |
|-----|----------|---------|
| Daily Conversation Archive | `0 23 * * *` (23:00) | Archive Master ↔ Obi-Wan + sub-agent traces to `04_Daily_Logs/YYYY-MM-DD/` |
| Vault Reindex | `0 3 * * *` (03:00) | Rebuild search index, vector embeddings |
| Backup Vault | `0 2 * * *` (02:00) | Git push to remote (if configured) |
| Project Health Check | `0 9 * * 1` (Mon 09:00) | Scan active projects, flag stale items |
| Skill Consolidation | `0 4 * * 0` (Sun 04:00) | Weekly: merge overlapping skills, archive stale |
| Anakin Alignment Review | `0 18 * * *` (18:00) | Daily: review Anakin's signals, risk, vault sync |

**Rationale:** Automates all vault maintenance. Daily archive ensures conversation persistence. Weekly consolidation prevents skill sprawl. Anakin review aligns quant work with Master's goals.

**Trade-offs:** 6 concurrent cron jobs may compete for resources at 02:00–04:00. Staggered by 1 hour. All use `obsidian` + `hermes-agent` skills.

**Vault Ref:** `04_Daily_Logs/index.md`, `C:\Users\brook\AppData\Local\hermes\profiles\obi-wan\cron\jobs.json`

---

## DECISION: OpenRouter Model Filtering — Tool-Calling Required

**Date:** 2026-08-02 19:55  
**Context:** Master questioned model count discrepancy (435 on OpenRouter vs ~34 in Hermes)  
**Decision:** Documented and accepted Hermes' three-layer filtering pipeline:

1. **Curated List** (~34 models) — Hardcoded recommendations
2. **Live Filter** (337 models) — Real-time OpenRouter catalog
3. **Tool-Calling Filter** (271 models) — Must support `tools` parameter

**Result:** Hermes shows only curated models that pass tool-calling filter. 66 models excluded (no tool support), 4 curated models missing from live catalog, 1 curated model lacks tool support.

**Rationale:** Agent loops **require** tool calling. Showing non-tool models would break delegation, cron, and multi-step workflows.

**Trade-offs:** Master sees fewer models, especially free ones. Mitigated by: (a) user-defined aliases for specific models, (b) custom provider config for unrestricted access, (c) understanding this is a feature, not a bug.

**Vault Ref:** `03_Context/references/providers/openrouter-model-filtering.md` (to be created), [[Lesson: OpenRouter Model Filtering Pipeline]]

---

## DECISION: Conversation Recall — On-Demand Vault Access

**Date:** 2026-08-02 21:08  
**Context:** Master asked about recalling past conversations  
**Decision:** Confirmed vault-based recall is **on-demand only**:

- Obi-Wan does **NOT** auto-load daily logs at session start
- Obi-Wan does **NOT** persist conversations in cross-session memory
- **Only** when Master asks ("read yesterday's conversation") → Obi-Wan reads `04_Daily_Logs/YYYY-MM-DD/master-dialogue.md`

**Rationale:** Respects context window limits. Keeps persistent memory for preferences/facts only. Master controls when context is injected.

**Trade-offs:** Master must explicitly request recall. No seamless continuity. Accepted as intentional design.

**Vault Ref:** `01_Obi-Wan/identity.md` (Session Log Reference), `04_Daily_Logs/index.md`

---

## DECISION: 5 Additional Profiles — Model Recommendations Pending

**Date:** 2026-08-02 20:15  
**Context:** Master asked for model recommendations for 5 planned profiles  
**Decision:** Obi-Wan provided recommendations (details in session transcript). Master will create profiles and add soul files.

**Status:** Awaiting Master's profile creation. Obi-Wan ready to assist with soul specifications.

**Vault Ref:** Session `20260802_195547_7ba4ac` messages 554–560