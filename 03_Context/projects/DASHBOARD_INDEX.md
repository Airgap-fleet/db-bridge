# Dashboard Project Index — Single Source of Truth

> **Purpose:** Eliminate confusion between the two distinct "Mission Control" projects. This document is the canonical reference.

---

## Project 1: Mission Control Dashboard (Legacy / Internal)

**For:** Us — local team dashboard, Kanban + group chat + agent status
**Path:** `C:/Users/brook/b/C:/the force/03_Context/projects/mission-control/`
**Stack:** Flask + vanilla HTML/JS + SQLite (stdlib-only, no build step)
**Port:** 8420
**Status:** ✅ **COMPLETE & RUNNABLE** — `python server.py` → http://localhost:8420

### Files
- `server.py` (59 KB, 1665 lines) — Flask + SSE, agents, tasks, messages, channels, rate limiting, webhooks, AgentListener, RoE enforcement
- `index.html` (91 KB, 2706 lines) — Full Kanban board, agent sidebar, chat panel, modals, toasts, dark/light theme
- `mission_control.db` — SQLite with agents, tasks, messages, workflows tables
- `RULES_OF_ENGAGEMENT.md` — Agent RoE definitions

### Capabilities
- Kanban board (Backlog/Todo/In Progress/Review/Done) with drag-drop
- Agent sidebar with live status dots (active/idle/dormant/offline)
- Group chat panel with channel support
- Task creation, assignment, priority, persistence
- SSE real-time updates every 10s
- AgentListener with rule evaluation, rate limiting, circuit breakers
- Webhook endpoints (GitHub, GitLab, Jira, PagerDuty, Datadog, AWS, Stripe)

### Run Command
```bash
cd "C:/Users/brook/b/C:/the force/03_Context/projects/mission-control/"
pip install flask pyyaml  # if not installed
python server.py
# Open http://localhost:8420
```

---

## Project 2: Dashboard MCP Server (afaaS / Client Product)

**For:** Clients — MCP server product (sellable, installable via `pip install dashboard-mcp`)
**Path:** `C:/Users/brook/03_Context/projects/afaaS/dashboard-mcp/`
**Stack:** FastMCP + FastAPI + PostgreSQL + Redis + WebSocket
**Port:** 8000
**Status:** 🔄 **BACKEND COMPLETE** — needs React frontend

### Files
- `src/dashboard_mcp/server.py` (28 KB) — FastMCP app with MCP tools, FastAPI, WebSocket `/ws`, SSE `/events`
- `src/dashboard_mcp/core.py` — Business logic
- `src/dashboard_mcp/models.py` — Pydantic models
- `fleet.yaml` — Agent fleet config (Obi-Wan, Scotty, K-2SO, Geppetto, Moneypenny)
- `AgentComms.md` — Group chat spec
- `README.md` — Full documentation

### MCP Tools
- `register_agent`, `get_agent`, `get_fleet_status`
- `create_task`, `update_task`
- `send_message`, `create_channel`, `get_channel_history`
- WebSocket `/ws` for real-time updates

### Frontend (TO BUILD)
**Path:** `C:/Users/brook/03_Context/projects/afaaS/frontend/`
**Stack:** React 18 + TypeScript + Vite + Tailwind + Headless UI
**Port:** 5173 (dev), proxies to Dashboard MCP on 8000
**Current State:** `package.json` exists, `src/components/`, `src/hooks/`, `src/services/` are **empty directories**

---

## No Crossover Verification

| Check | Mission Control (Legacy) | Dashboard MCP (afaaS) | Result |
|-------|--------------------------|----------------------|--------|
| Flask imports | ✅ Yes | ❌ No (FastAPI only) | ✅ Clean |
| FastMCP imports | ❌ No | ✅ Yes | ✅ Clean |
| SQLite direct | ✅ Yes | ❌ No (PostgreSQL via asyncpg) | ✅ Clean |
| React/TypeScript | ❌ No (vanilla JS) | ✅ Yes (planned) | ✅ Clean |
| Port | 8420 | 8000 | ✅ Clean |
| Database file | `mission_control.db` | PostgreSQL (no local file) | ✅ Clean |
| MCP protocol | ❌ No | ✅ Yes (2026-07-28 compliant) | ✅ Clean |
| Fleet.yaml used | ❌ No | ✅ Yes | ✅ Clean |
| AgentComms.md used | ❌ No | ✅ Yes | ✅ Clean |

**Conclusion: Zero code crossover. The projects are completely separate.**

---

## Quick Decision Guide

| Need | Use |
|------|-----|
| Local team Kanban + chat **today**, zero setup | **Mission Control (Legacy)** — run `python server.py` |
| Sellable MCP server product for clients | **Dashboard MCP (afaaS)** — backend done, needs React frontend |
| Agent fleet monitoring via MCP tools | **Dashboard MCP (afaaS)** |
| WebSocket/SSE real-time for agents | Both (different implementations) |

---

## Current Status (2026-08-17)

| Project | Status | Next Action |
|---------|--------|-------------|
| Mission Control (Legacy) | 🔄 Server.py fix needed | Restructure Flask app to module level, run on 8420 |
| Dashboard MCP (afaaS) Backend | ✅ Complete | — |
| Dashboard MCP (afaaS) Frontend | ⏳ Not started | Build React/TS at `afaaS/frontend/` |

---

*Last updated: 2026-08-17 by Obi-Wan*
*This document lives at `03_Context/projects/DASHBOARD_INDEX.md`*