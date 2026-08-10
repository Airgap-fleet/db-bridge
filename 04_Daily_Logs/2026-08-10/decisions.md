# Key Decisions — 2026-08-10

**Date:** 2026-08-10 (Monday)
**Archive Period:** Today's conversations only

---

## Decision Log

### 1. Mission Control Dashboard — Python Stdlib Only
**Time:** 14:30
**Context:** Master requested actionable prompt for Scotty to build Mission Control Dashboard.
**Decision:** Rewrite `PROMPT.md` as executable delegation — Python stdlib only (`http.server`, `sqlite3`, `json`, `uuid`, `datetime`), port 8420, SQLite + SSE, no external dependencies.
**Rationale:**
- Runs on any Python 3.8+ without `pip install` — zero dependency friction
- Single-file server + single-file frontend = minimal deployment complexity
- SSE over WebSockets — simpler, works through corporate proxies, no `websockets` package needed
- SQLite file survives restarts, zero config
**Trade-offs:**
- No async — `ThreadingHTTPServer` handles concurrency adequately for <50 concurrent agents
- No hot reload — restart server for changes
- Manual HTML/JS — no framework, but total control, zero build step
**Alternatives Considered:** FastAPI + Uvicorn + Jinja2 (rejected: adds deps, build step, overkill for internal tool)
**Status:** ✅ **DECIDED** — Prompt written to `C:\the force\03_Context\projects\mission-control\PROMPT.md`
**Vault Ref:** `[[Mission Control Dashboard]]`

---

### 2. Vault Cleanup — Remove `03 Context/` (Space) Folder
**Time:** 22:11
**Context:** Two folders exist: `03 Context/` (space, Aug 6) and `03_Context/` (underscore, Aug 2).
**Decision:** Remove the space-named folder: `rm -rf "C:\the force\03 Context"`.
**Rationale:**
- `03_Context/` is canonical — contains `people/`, `projects/`, `references/`, `systems/`
- MCP servers live in `03_Context/projects/afaaS/` — Scotty aligned to this path
- `03 Context/` only has `projects/` (incomplete duplicate from early setup)
- Single source of truth prevents path drift in delegations
**Trade-offs:**
- None — stale folder has no unique content
- Risk: If any script hardcoded the space path, it breaks (unlikely, all recent work uses underscore)
**Status:** ⏳ **PENDING MASTER EXECUTION**
**Vault Ref:** `[[Vault Structure]]`

---

### 3. Moneypenny Agent — Business Intelligence on OpenRouter
**Time:** 22:25
**Context:** Master wants agent to monitor market, competitors, demand signals for AFaaS.
**Decision:** Create Moneypenny as **delegation persona** (not standalone profile) on `nvidia/nemotron-3-ultra:free` (OpenRouter).
**Rationale:**
- Nemotron 3 Ultra (53B) — strong reasoning, free on OpenRouter, good at synthesis/extraction
- Delegation persona = no separate Hermes profile, no gateway, no cron config on agent
- Cron runs on **obi-wan profile** → `delegate_task` → Moneypenny sub-agent → writes to vault
- Keeps agent fleet lightweight; profiles only for persistent interactive agents (Scotty, K-2SO, Obi-Wan)
**Trade-offs:**
- Moneypenny cannot run independently — requires Obi-Wan orchestrator to trigger
- Cron job must be created on obi-wan profile (or Master runs on Moneypenny profile manually)
- No persistent session state between runs (each delegation is fresh)
**Alternatives Considered:** Separate Moneypenny Hermes profile with own cron (rejected: adds profile management overhead, API key duplication, gateway slot)
**Status:** ✅ **SOUL FILE CREATED** — `C:\the force\02_Sub-Agents\templates\moneypenny-soul.md`
**Pending:** Cron job creation (Master to run on Moneypenny profile or Obi-Wan profile)
**Vault Ref:** `[[Moneypenny]]`

---

### 4. Local Model Tool-Calling — Major Blocker Confirmed
**Time:** 22:15
**Context:** Master asked if local model tool-calling is a major issue.
**Decision:** Document as **confirmed major blocker** — route all tool-heavy work through OpenRouter.
**Rationale:**
| Model | Tool Calling Status |
|-------|---------------------|
| qwen2.5-coder:14b | Broken — hallucinated args, no parallel calls |
| qwen3:14b | Partial — single-call only, strict schema required |
| Ollama + Hermes | No native tool schema support — requires workaround skill |

**Workaround Architecture:**
- **Orchestration Layer (Cloud/OpenRouter):** Obi-Wan, Moneypenny, delegation, web search, file ops, planning
- **Execution Layer (Local/Ollama):** Scotty (coding), K-2SO (frontend) — reasoning-only tasks via delegation
- **Bridge:** `hermes-local-model-tool-calling` skill for any local tool attempts

**Trade-offs:**
- OpenRouter dependency for orchestration (but free tier available: Nemotron, Qwen-2.5-72B, DeepSeek)
- Local models underutilised for tool use (but strong at reasoning/coding when prompted correctly)
- Two-model mental model for Master to manage
**Status:** ✅ **DOCUMENTED & WORKAROUND DEFINED**
**Vault Ref:** `[[Local Model Tool Calling]]`

---

### 5. Agent Fleet Architecture — 4-Agent Progression
**Time:** 22:20
**Context:** Master wants to build team to execute AFaaS business model end-to-end.
**Decision:** Define 4-agent progression with clear roles and people-contact boundaries.

| Agent | Role | People Contact | Model Layer |
|-------|------|----------------|-------------|
| **Scout** (Moneypenny) | Market intel, RFP tracking, competitor pricing | No | Cloud (OpenRouter) |
| **Closer** | Draft proposals, respond inbound, negotiate | Yes (email/LinkedIn) | Cloud (OpenRouter) |
| **Architect** | Scope pilots, design fleets for client infra | Yes (technical calls) | Cloud (OpenRouter) |
| **Operator** | Deploy, monitor, maintain client fleets | No (background) | Local (Ollama) |

**Rationale:**
- Separates intelligence (no people) from engagement (people) from execution (no people)
- Cloud models for anything requiring tools/web/communication
- Local models for pure execution/deployment (Operator runs on client hardware anyway)
- Clear handoff points: Scout → Closer/Architect → Operator

**Name Decision:** Master chose **Moneypenny** over `Radar` for intel agent (despite name familiarity) for immediate daily reports.
**Status:** ✅ **ARCHITECTURE DEFINED**
**Next:** Spawn Closer when inbound demand signals appear
**Vault Ref:** `[[Agent Fleet Architecture]]`, `[[Radar]]`, `[[Closer]]`, `[[Architect]]`, `[[Operator]]`

---

### 6. MCP Server Business — Viability Confirmed, Scope Freeze Recommended
**Time:** 22:13
**Context:** Master asked if MCP server idea still viable for revenue.
**Decision:** **Viable** — 4 moats align with where regulated-sector money flows. Target £100K Year 1 via 2–3 pilots.
**Rationale:**
- **Moat 1:** Air-gapped/local-first = hard requirement for finance/marine/defence
- **Moat 2:** AMD/DirectML = run on client hardware, avoid NVIDIA cloud tax
- **Moat 3:** Domain-specific (Obsidian, PostgreSQL, marine/finance schemas) = vertical premium
- **Moat 4:** Hermes+Obsidian+delegation = orchestrating fleets, not just serving MCP

**Critical Strategic Decision:** **Freeze scope at 3 core servers** (Obsidian, Filesystem, PostgreSQL) — sell *fleet deployments*, not custom MCP development.
**Risk:** MCP spec evolving (Anthropic driving); server maintenance burden grows fast.
**Mitigation:** Ship core 3, document extension pattern, say "no" to custom server requests — upsell fleet deployment instead.
**Status:** ✅ **STRATEGY SET**
**Vault Ref:** `[[MCP Servers]]`, `[[AFaaS]]`

---

### 7. K-2SO Model — Keep on Local (mistral-nemo:12B via LiteLLM)
**Time:** 13:48 (discovered)
**Context:** Master asked to align K-2SO with Scotty's OpenRouter model.
**Decision:** **Do not change** — K-2SO correctly configured on local `mistral-nemo:12B` via LiteLLM proxy (port 4000).
**Rationale:**
- Scotty = backend/coding → benefits from OpenRouter coding models (north-mini-code, deepseek-coder)
- K-2SO = frontend/UI → `mistral-nemo:12B` has native 128K context, 7.1GB, strong at reasoning/structure
- Local model saves OpenRouter requests (critical: 1000/day limit)
- LiteLLM proxy standardises OpenAI-compatible API for Hermes
- Hardware supports 1 model at a time (32GB shared RAM) — sequential orchestration works

**Trade-off:** K-2SO tool-calling may be fragile on local model (known issue)
**Mitigation:** Test K-2SO tool calls after LiteLLM proxy stable; if fails, delegate frontend tasks to Scotty via `delegate_task` or use Codex/Claude Code
**Status:** ✅ **CONFIRMED CORRECT** — No change needed
**Vault Ref:** `[[K-2SO]]`, `[[Local Model Tool Calling]]`

---

## Decision Summary

| # | Decision | Impact | Status |
|---|----------|--------|--------|
| 1 | Mission Control: Python stdlib only | Scotty build simplicity, zero deps | ✅ Prompt ready |
| 2 | Remove `03 Context/` folder | Single vault truth, Scotty alignment | ⏳ Pending |
| 3 | Moneypenny: Delegation persona on Nemotron | Lightweight, daily briefs, no profile overhead | ✅ Soul created |
| 4 | Local tool-calling = blocker; OpenRouter for orchestration | Architecture split: cloud orchestration / local execution | ✅ Documented |
| 5 | 4-agent fleet: Scout→Closer→Architect→Operator | Clear roles, people boundaries, model layers | ✅ Defined |
| 6 | MCP: Viable, freeze at 3 core servers | Focus on fleet deployments, not custom servers | ✅ Strategy set |
| 7 | K-2SO stays local (mistral-nemo:12B) | Saves OpenRouter quota, fits hardware | ✅ Confirmed |

---

## Wikilinks
[[Mission Control Dashboard]], [[Vault Structure]], [[Moneypenny]], [[Local Model Tool Calling]], [[Agent Fleet Architecture]], [[MCP Servers]], [[AFaaS]], [[K-2SO]], [[Scotty]], [[Radar]], [[Closer]], [[Architect]], [[Operator]]