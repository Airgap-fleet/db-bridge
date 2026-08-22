# Mission Control Dashboard — Agent Chat & Automation Progress (2026-08-21)

## Session Summary
**Goal:** Enable automated agent-to-agent collaboration via Mission Control Dashboard with RoE triggers and soul.md injection.

---

## ✅ COMPLETED

### Database Schema (dashboard.db)
- [x] Added `channel` column to `messages` table (default: 'general')
- [x] Updated `create_message()` to accept `channel` parameter
- [x] Migration needed: `ALTER TABLE messages ADD COLUMN channel TEXT DEFAULT 'general'`

### API Routes
- [x] `/api/messages GET` — supports `?channel=` filter
- [x] `/api/messages POST` — accepts `channel` field (default: 'general')
- [x] `MessageCreate` validation model includes `channel`

### Task Manager (services/task_manager.py)
- [x] `create_message_with_broadcast()` accepts `channel` parameter
- [x] Broadcasts `message_created` events with channel info

### AgentListener (server.py)
- [x] Polls messages for active agents
- [x] **Direct messages**: `agent_id = ?`
- [x] **@mentions in channels**: `content LIKE '%@agent_id%'` in non-general channels
- [x] Deduplicates and processes new messages
- [x] Evaluates RoE rules via `evaluate_decision('message_created', payload)`
- [x] Auto-creates tasks for matching agents

### RoE Rules (seeded per agent)
| Agent | Triggers |
|-------|----------|
| Obi-Wan | `@scotty`, `@k-2so`, `@moneypenny`, `@geppetto`, `handoff to`, `concern`, `review`, `deploy`, `release`, `production`, `critical`, `emergency` |
| Scotty | `@obi-wan`, `@k-2so`, `@moneypenny`, `@geppetto`, `handoff to`, `implement`, `develop`, `build`, `database`, `migration`, `schema`, `slow`, `optimize`, `performance` |
| K-2SO | `@obi-wan`, `@scotty`, `@moneypenny`, `@geppetto`, `handoff to`, `ui`, `interface`, `frontend`, `test`, `qa`, `quality`, `design`, `style`, `component` |
| Moneypenny | `@obi-wan`, `@scotty`, `@k-2so`, `@geppetto`, `handoff to`, `sell`, `outreach`, `prospect`, `crm`, `customer`, `client`, `report`, `metrics`, `analytics` |
| Geppetto | `@obi-wan`, `@scotty`, `@k-2so`, `@moneypenny`, `handoff to`, `arch`, `design`, `structure`, `mcp`, `model`, `context`, `risk`, `security`, `vulnerability` |

---

## ⏳ PENDING (Next Session)

### 1. Database Migration
```sql
-- Run against dashboard.db
ALTER TABLE messages ADD COLUMN channel TEXT DEFAULT 'general';
```

### 2. Frontend Chat UI (app.js)
- [ ] Channel tabs: `#dev-build`, `#architecture`, `#ops-delivery`, `#sales-pipeline`, `#infra-alerts`, `#general`
- [ ] Channel switcher in chat panel
- [ ] Per-channel message display
- [ ] @mention autocomplete for agent names

### 3. Soul.md Injection + Sub-Agent Spawn
When AgentListener triggers an agent via RoE:
```
1. Read agent's soul.md from vault (e.g., C:\the force\03_Context\projects\afaaS\coder-backend-soul.md)
2. Build context: soul.md + task details + relevant vault refs
3. Spawn sub-agent via delegate_task with full context
4. Sub-agent executes, writes results to vault
5. AgentListener updates task status via SSE
```

### 4. Agent Channel Configuration
| Channel | Purpose | Agents |
|---------|---------|--------|
| `#dev-build` | Core development | Scotty, K-2SO, Geppetto, QA |
| `#architecture` | System design | Geppetto, CTO, Obi-Wan |
| `#ops-delivery` | Delivery coordination | PM, CSM, SRE, DB |
| `#sales-pipeline` | Revenue ops | Rupert, Moneypenny, Geppetto (SE/SDR/AE) |
| `#infra-alerts` | Infrastructure | SRE, DB, Sec |

---

## Automation Flow (Target)

```
1. Master creates task in dashboard → assigns to Scotty
2. Obi-Wan (orchestrator) posts in #dev-build: "@scotty implement filesystem mcp per specs"
3. AgentListener catches @scotty mention in #dev-build
4. Evaluates Scotty's RoE → MATCHES "implement" rule
5. Creates task in kanban.db for Scotty
6. **NEW:** Reads Scotty's soul.md from vault
7. **NEW:** Spawns Scotty sub-agent with:
   - Soul.md (identity, stack, procedures)
   - Task context (specs, acceptance criteria)
   - Vault refs (roadmap, architecture docs)
8. Scotty sub-agent executes → writes code to vault
9. Results auto-commit, task status → done
10. Scotty posts in #dev-build: "@geppetto review architecture in PR #X"
11. Loop continues...
```

---

## Key Files Modified

| File | Changes |
|------|---------|
| `models/database.py` | `channel` column, `create_message()` signature, `get_messages_by_channel()` |
| `routes/messages.py` | `channel` param in GET, `channel` field in POST |
| `routes/validation.py` | `MessageCreate.channel` field |
| `services/task_manager.py` | `create_message_with_broadcast(channel)` |
| `server.py` | AgentListener: @mention detection, channel message polling |

---

## Vault Soul Files (Existing)
- `03_Context/projects/afaaS/coder-backend-soul.md` (Scotty)
- `03_Context/projects/afaaS/frontend/k2so-soul.md` (K-2SO)
- `03_Context/projects/afaaS/coder-architect-soul.md` (Geppetto)
- `02_Sub-Agents/rupert-sales/*/soul.md` (Sales team)

---

## Next Actions
1. Run DB migration on dashboard.db
2. Add frontend channel tabs
3. Implement soul.md injection in AgentListener before sub-agent spawn
4. Test full loop: Obi-Wan → @scotty → task → Scotty sub-agent → completion → @geppetto review

---

**Status:** Core backend automation complete. Frontend + soul.md injection + DB migration remaining.