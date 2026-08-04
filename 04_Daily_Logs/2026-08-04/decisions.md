# Decisions — 2026-08-04

> *Key choices, rationale, and trade-offs recorded during daily archive*

---

## DECISION: 12-Agent Fleet Model Allocation Fixed

**Date:** 2026-08-04 21:54  
**Context:** Master asked for model list per agent for the 12-agent AFaaS fleet  
**Decision:** Published complete allocation table with primary/fallback models, RAM estimates, and reasoning

### Options Considered
1. **All cloud models** — Max reasoning, but cost/unreliability at scale
2. **All local models** — Privacy/speed, but 64GB RAM insufficient for 12 concurrent
3. **Hybrid (chosen)** — Cloud for reasoning (Obi-Wan, Anakin, Sales), Local for tool-use (Scotty, Frontend, DevOps, QA), Small for always-on (Dashboard, Archivist)

### Rationale
- **Tool-use reliability** matters most for coding agents → local deepseek-coder/qwen2.5-coder/starcoder2
- **Reasoning/planning** benefits from large context → cloud Nemotron 550B (free tier)
- **RAM budget** fits 64GB upgrade: ~40GB active, 24GB headroom
- **Current 32GB** supports 2-3 local models — upgrade unlocks full fleet

### Trade-offs
- Cloud dependency for 3 critical agents (mitigated: OpenRouter free tier + local fallbacks)
- Model swap latency when switching active pairs (mitigated: keep always-on pair loaded)
- Designer role deferred — add when client-facing work begins

### Vault Ref
`master-dialogue.md` (Model Allocation section), `03_Context/projects/afaaS/agent-models.md` (to be created)

---

## DECISION: Dashboard MCP Before Dashboard UI

**Date:** 2026-08-04 22:00  
**Context:** Master wants dashboard for fleet monitoring while sleeping  
**Decision:** Build `dashboard-mcp` server (Scotty) before Dashboard UI (Coder-Frontend)

### Options Considered
1. **UI first** — Visual progress, but no data backend
2. **MCP first (chosen)** — API exposes fleet status, tasks, health → UI consumes it
3. **File-based only** — Tail `AgentComms.md` directly, no server

### Rationale
- **MCP standardizes** agent data access — any agent can query fleet status
- **Headless operations** possible — cron/scripts can hit MCP without UI
- **Scotty's next 2 deliveries** are MCP servers (PostgreSQL → Dashboard) — natural sequence
- **Coder-Frontend** builds UI against stable API contract

### Trade-offs
- Delayed visual feedback for Master (mitigated: file-based tail works immediately for `AgentComms.md`)
- Scotty becomes critical path (already is — 3 MCP servers)

### Vault Ref
`master-dialogue.md` (Critical Path section), `03_Context/projects/afaaS/dashboard-architecture.md` (to be created)

---

## DECISION: Scotty Model = deepseek-coder:6.7b (qwen2.5-coder:14b fallback)

**Date:** 2026-08-04 21:54 (in allocation table)  
**Context:** Scotty hallucinated `filesystem-mcp/` completion — needs better tool-use reliability  
**Decision:** Switch from qwen2.5-coder:14b to deepseek-coder:6.7b as primary

### Rationale
- **deepseek-coder:6.7b** — superior tool-use, instruction following, MCP/FastAPI coding
- **qwen2.5-coder:14b** — larger context (64k), good fallback for complex refactors
- **6.7b model** = ~4 GB RAM vs 14b = ~8 GB — leaves more headroom

### Trade-offs
- Smaller context window (mitigated: MCP servers are modular, fit in 8k)
- Must pull model first (Ollama: `ollama pull deepseek-coder:6.7b`)

### Vault Ref
`03_Context/projects/afaaS/coder-backend-soul.md`, `AgentComms.md` (Scotty config update)

---

## DECISION: No Separate Designer Agent (Yet)

**Date:** 2026-08-04 21:59  
**Context:** Master asked about website designer role  
**Decision:** Coder-Frontend covers implementation; Designer deferred to client-facing phase

### Rationale
- **MCP dashboards, internal tools** → functional UI sufficient (Coder-Frontend + Tailwind/Headless UI)
- **Client-facing marketing site, product dashboard** → needs UX research, design systems, prototyping
- **Current roadmap** = MCP servers + internal fleet dashboard → no designer needed

### Trade-offs
- If client project lands early, Designer becomes blocker (mitigated: cloud Nemotron can sub in)
- Brand/visual identity undefined (mitigated: Master decides when needed)

### Vault Ref
`master-dialogue.md` (Website Designer section)

---

## DECISION: Critical Path = Scotty's 3 MCP Servers

**Date:** 2026-08-04 22:01  
**Context:** Master committed to "move as quickly as possible once bugs ironed out"  
**Decision:** Explicit critical path with Scotty as single bottleneck

### Sequence
1. **Filesystem MCP** — Real files, verified (current blocker)
2. **PostgreSQL MCP** — Structured data layer for fleet/tasks/leads
3. **Dashboard MCP** — Fleet status API, task queue, agent health endpoints
4. **Dashboard UI** — Coder-Frontend builds React/HTMX interface
5. **AgentComms MCP** — Inter-agent messaging, @mentions, handoffs
6. **Autonomous Loop** — Agents pick → execute → report → repeat

### Rationale
- All autonomy depends on **data layer** (MCP servers)
- **Scotty is only backend coder** — no parallel backend work possible
- **Verifiable milestones** — each MCP server = testable deliverable

### Trade-offs
- Single point of failure (Scotty) — mitigated: Obi-Wan can build if Scotty fails
- Frontend blocked until Dashboard MCP ready — mitigated: Coder-Frontend can scaffold UI components in parallel

### Vault Ref
`master-dialogue.md` (Critical Path), `03_Context/projects/afaaS/sprint-plan.md` (to be created)

---

## DECISION: Dashboard Research Re-Dispatch Required

**Date:** 2026-08-04 21:54 (interruption)  
**Context:** Researcher sub-agent interrupted at 202s  
**Decision:** Re-dispatch with concrete deliverables and target directory

### Issues Identified
- Target directory `03_Context/references/dashboard-research/` not created
- GitHub rate-limited, Google blocked
- No output files written before interruption

### Next Dispatch Plan
- Create directory first
- Use `web_search` skill (not browser) for examples
- Output: `approaches.md`, `hermes-integration.md`, `architecture.md`
- Reference `hermes-agent` skill → `desktop-plugins.md` for UI patterns

### Vault Ref
`subagent-traces.md` (deleg_fb1af0cc), `03_Context/references/dashboard-research/` (to be created)

---

## DECISION: K-2SO Strategy Pivot Confirmed

**Date:** 2026-08-04 02:11 (cron)  
**Context:** Daily optimization — 528 combos, ZERO passed filters  
**Decision:** Abandon SMA/RSI/macro on daily GBP/USD; pivot strategy class

### Evidence
- Best Sharpe: 0.10 (target > 1.0)
- Best Max DD: -8.70% (target < 8%)
- Only 1/528 configs positive return (+3.68% over 19 years)
- Macro gate (monthly UNRATE/PAYEMS) over-filters daily signals

### Next Cycle
- Test `macro_gate: neither` baseline
- Switch to weekly bars
- Add trend-following exits (ATR trailing)
- Expand SMA_fast to [5, 10, 20]

### Vault Ref
`04_Daily_Logs/2026-08-04/k2so-traces.md`, `Anakin/best_params.md` (REJECTED)

---

## DECISION: Vault Reindex Complete — Embeddings Skipped

**Date:** 2026-08-04 03:08 (cron)  
**Context:** Daily 03:00 reindex job  
**Decision:** Full-text search index rebuilt (55 files, 37K words); vector embeddings skipped

### Reason
- No embedding model in Ollama
- Install `nomic-embed-text` or `mxbai-embed-large` to enable

### Trade-offs
- Semantic search unavailable (mitigated: full-text + wikilinks sufficient for now)
- No additional RAM/CPU for embeddings

### Vault Ref
`04_Daily_Logs/2026-08-04/vault-health.md`, `05_Skills/search-index.json`

---

## DECISION: Git Remote Not Configured

**Date:** 2026-08-04 02:02 (cron backup)  
**Context:** Daily backup — local commit only  
**Decision:** Defer remote configuration

### Status
- Local commits working: `4d86b31` (backup), `7eae95a` (reindex)
- No `origin` remote → no off-site backup

### Action Required
```bash
cd "C:\the force"
git remote add origin <remote-url>
git push -u origin master
```

### Vault Ref
`04_Daily_Logs/2026-08-04/vault-health.md`

---

*Total decisions this session: 9 | Linked to master-dialogue.md and subagent-traces.md*