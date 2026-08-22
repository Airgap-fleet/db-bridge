# Session Handoff — August 21, 2026

## Mission: Mission Control Dashboard → Hermes Profile Integration

**Objective:** Enable the Mission Control Dashboard (Flask + SQLite at `C:/the force/03_Context/projects/mission-control/`, port 8420) to **spawn actual Hermes profiles** (scotty, k-2so, geppetto, moneypenny, obi-wan, rupert, etc.) when AgentListener detects `@mention` + RoE match, injecting `soul.md` context from vault.

---

## What Was Completed This Session

### 1. Database Migration ✅
```sql
ALTER TABLE messages ADD COLUMN channel TEXT DEFAULT 'general';
```
Applied to `dashboard.db`. Verified column exists.

### 2. Backend Automation Already Complete (from Aug 20-21 work)
- `AgentListener` in `server.py` polls messages, detects `@mentions` in channels, evaluates RoE rules per agent
- RoE triggers seeded for all 5 agents (Obi-Wan, Scotty, K-2SO, Moneypenny, Geppetto)
- Task creation on RoE match via `evaluate_decision()` → `create_task_with_broadcast()`
- SSE endpoint `/events` broadcasts real-time updates
- API routes: `/api/messages` GET/POST with channel filter

### 3. Hermes Profiles Exist (12 profiles in `~/AppData/Local/hermes/profiles/`)
```
obi-wan, scotty, k-2so, moneypenny, geppetto, rupert, cto, pm, csm, qa, db, clo
```
Each has isolated `config.yaml` with model/provider settings (e.g., scotty uses `qwen3.5:9b` via Ollama custom endpoint).

### 4. Soul Files Ready in Vault
```
03_Context/projects/afaaS/coder-backend-soul.md        (Scotty)
03_Context/projects/afaaS/frontend/k2so-soul.md         (K-2SO)
03_Context/projects/afaaS/coder-architect-soul.md       (Geppetto)
02_Sub-Agents/rupert-sales/*/soul.md                    (Sales team)
```

### 5. Hermes CLI Profile Invocation Tested
**Working pattern:** `HERMES_PROFILE=scotty hermes chat -q "prompt" --quiet --max-turns 1`
- Returns `session_id: ...` + response
- **BUT**: Hardware constraint — only ONE 14B model fits in 32GB RAM (shared VRAM)
- Multiple concurrent Hermes invocations overload GPU/RAM → timeouts/kills needed

---

## Critical Blocker: Hardware Constraint

**32GB RAM + 780M iGPU (shared VRAM) = ONE 14B model active at a time.**

- Ollama `qwen3.5:9b` or `qwen2.5-coder:14b` consumes ~8-12GB
- Multiple `hermes chat -p <profile>` calls in parallel → OOM, GPU saturation, 180s timeouts
- **Must enforce sequential execution** — no parallel sub-agent spawning

---

## Next Session: Implementation Plan

### Priority 1: Modify AgentListener → Spawn Hermes Profile (Sequential)
**File:** `C:/the force/03_Context/projects/mission-control/server.py` → `run_agent_listener()` function (lines ~376-470)

**On RoE match (currently line 424-434):**
```python
# CURRENT: Only creates task in kanban.db
task_id = create_task_with_broadcast(...)

# REQUIRED: Also spawn Hermes profile
1. Read agent's soul.md from vault (path from agent.profile_name mapping)
2. Build prompt: soul.md + task context + vault refs
3. Spawn Hermes profile via subprocess (sequential queue)
4. Capture output → write to vault → update task status via SSE
```

**Sequential queue needed:** In-memory `asyncio.Queue` or file-based lock to ensure only ONE Hermes process runs at a time.

### Priority 2: Frontend Channel Tabs
**File:** `C:/the force/03_Context/projects/mission-control/app.js` + `index.html`
- Channel tabs: `#dev-build`, `#architecture`, `#ops-delivery`, `#sales-pipeline`, `#infra-alerts`, `#general`
- @mention autocomplete for agent names
- Per-channel message display

### Priority 3: Test Full Loop
```
Obi-Wan (dashboard) → @scotty in #dev-build → AgentListener matches RoE
→ spawns Hermes scotty profile with soul.md context
→ Scotty executes → writes code to vault → updates task → posts @geppetto
→ Loop continues
```

---

## Key Files to Modify

| File | Purpose |
|------|---------|
| `server.py` | AgentListener + Hermes spawn logic |
| `services/task_manager.py` | Task status updates from sub-agent completion |
| `app.js` | Frontend channel tabs, @mention autocomplete |
| `index.html` | Chat UI structure |

---

## Environment State

| Component | Status |
|-----------|--------|
| Mission Control Dashboard | Runnable at `http://localhost:8420` (server.py 633 lines) |
| Dashboard DB | Migration complete, `channel` column added |
| Kanban DB | Exists at `~/AppData/Local/hermes/kanban.db` |
| Hermes Profiles | 12 profiles configured, tested individually |
| Ollama | Running (ollama.exe PID 10288), `qwen3.5:9b` available |
| Vault | `C:\the force` accessible, soul files in place |

---

## Commands for Next Session

```bash
# Start dashboard
cd "C:/the force/03_Context/projects/mission-control"
python server.py
# → http://localhost:8420

# Test Hermes profile (sequential only!)
HERMES_PROFILE=scotty hermes chat -q "prompt" --quiet --max-turns 1

# Kill runaway processes if needed
tasklist | findstr python
taskkill /PID <pid> /F
```

---

## Decision Log (This Session)

1. **No sub-agent delegation** — Master mandated: only Hermes profiles, no `delegate_task`
2. **Sequential execution mandatory** — Hardware constraint accepted
3. **DB migration done** — `channel` column ready for frontend
4. **AgentListener is the integration point** — Modify `run_agent_listener()` to spawn Hermes CLI

---

## Open Questions for Master

1. **Queue mechanism:** In-memory `asyncio.Queue` in `server.py` vs file-based lock in vault?
2. **Prompt template:** Standardized format for soul.md + task + vault refs?
3. **Timeout handling:** What if Hermes profile hangs? Kill after N seconds?
4. **Result capture:** Parse Hermes output → write to vault → broadcast SSE `task_completed`?

---

**Prepared by:** Obi-Wan (Orchestrator)
**Vault Path:** `C:\the force\04_Daily_Logs\2026-08-21\session-handoff.md`
**Next Session Should:** Start with Priority 1 — modify AgentListener for sequential Hermes profile spawn