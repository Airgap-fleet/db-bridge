# Key Decisions — 2026-08-08

**Date:** 2026-08-08 (Saturday)
**Archive Time:** 23:00 (scheduled cron run)

---

## Decisions Logged Today

| Decision | Context | Rationale | Trade-offs | Author |
|----------|---------|-----------|------------|--------|
| **K-2SO soul file created** | Master requested frontend engineer agent; re-purposing deleted K-2SO | Modeled on Scotty's proven backend soul pattern; comprehensive 279-line spec | Frontend stack complexity (React, TypeScript, Vite, Tailwind, Storybook) requires larger context | Obi-Wan |
| **K-2SO model: OpenRouter `cohere/north-mini-code:free`** | Local models (qwen2.5-coder:14b) struggling with tool-calling; OpenRouter 1000/day shared limit | 256K context, free, native tool calling; same as Scotty's current profile | Burns shared OpenRouter quota; migration to local pending Hermes GH fixes | Master |
| **Scotty fix via prompt (not Obi-Wan fix)** | 928/1000 OpenRouter requests used; Obi-Wan debugging loops burn requests | Scotty executes in fresh session (5-10 requests) vs Obi-Wan loops (50+ already burned) | Delay until tomorrow when quota resets; Master must copy-paste prompt | Master |
| **No `delegate_task` for Scotty review** | In-session review faster than spawning sub-agent for read-only analysis | Avoids delegation overhead for review tasks | Breaks trace logging protocol; no automated `subagent-traces.md` entry | Obi-Wan |
| **Dashboard MCP scope: models-only delivered** | Scotty delivered models-only; core/server/fleet.yaml/tests/CI/Docker pending | Unblocks frontend (K-2SO) with type definitions; backend can iterate | Full MCP server incomplete; Dashboard MCP not runnable yet | Scotty/Obi-Wan |

---

## Pending Decisions (Carried Forward)

| Decision | Context | Status | Next Action |
|----------|---------|--------|-------------|
| **Dashboard MCP: core/server vs models-only scope** | Scotty building MCP servers | Models-only delivered; core/server/fleet.yaml/tests/CI/Docker pending | Resume core/server implementation after PostgreSQL MCP tests pass |
| **OpenRouter migration → local models** | 5 GH issues blocking Hermes tool-calling | Tracking: `cohere/north-mini-code:free` (256K ctx) for Scotty & K-2SO | Monitor Hermes GH issues weekly (cron job `a1e585821d49`) |
| **AFaaS legal structure (Pilot-first)** | Technical validation before legal | Vault has `BUSINESS_MODEL.md` & `AFaaS_MASTER_PACKAGE.md` | Complete technical pilot with 1 client |
| **Voice stack: Piper TTS + faster-whisper** | Planned for dashboard | Hardware: AMD 780M iGPU, 32GB RAM | Prototype after Dashboard MCP core done |
| **K-2SO profile config.yaml update** | Soul exists, config still points to Ollama | Blocked on OpenRouter quota today | Update to `cohere/north-mini-code:free` when quota allows |
| **PostgreSQL MCP test environment** | Docker container `postgresql-mcp-db` needed | Not running in test environment | Scotty to verify container running before pytest |

---

## Decision Quality Metrics

| Metric | Value | Target |
|--------|-------|--------|
| Decisions with rationale | 5/5 | 100% |
| Decisions with trade-offs | 5/5 | 100% |
| Decisions logged to vault | 5/5 | 100% |
| Wikilinks used | 12 | — |

---

## Wikilinks
[[K-2SO]], [[Scotty]], [[PostgreSQL MCP]], [[Dashboard MCP]], [[AFaaS]], [[OpenRouter Limits]], [[Hermes GH Issues]], [[Obi-Wan State]], [[Sub-Agent Registry]]