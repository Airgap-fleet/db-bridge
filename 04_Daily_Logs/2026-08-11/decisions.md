# Decisions — 2026-08-11

> **Date:** August 11, 2026
> **Key Decisions:** 3

---

## DECISION-001: Mission Control Dashboard Path Bug Fix

**Timestamp:** 2026-08-11 16:07:29
**Context:** K-2SO reported "index.html written successfully to correct path" but dashboard failed to load.
**Root Cause:** `server.py:555` used relative path `open('index.html', 'rb')` instead of absolute path.
**Comparison:** `DB_PATH` on line 13 correctly uses `os.path.join(os.path.dirname(__file__), 'mission_control.db')`.

**Decision:** Patch `server.py` to use absolute path for index.html:
```python
index_path = os.path.join(os.path.dirname(__file__), 'index.html')
with open(index_path, 'rb') as f:
    self.wfile.write(f.read())
```

**Rationale:**
- Consistency with existing `DB_PATH` pattern
- Eliminates CWD dependency (server can be started from any directory)
- Single-line fix, zero risk

**Trade-offs:** None — pure bug fix.

**Outcome:** ✅ Server starts successfully, serves index.html from correct location.

---

## DECISION-002: Add Moneypenny (Business Intelligence) Agent RoE

**Timestamp:** 2026-08-11 18:51:00
**Context:** Master asked to add business-facing agents to cover "business aspects we will be using for building the business and product correctly."

**Decision:** Define Moneypenny RoE with 7 trigger rules covering:
1. **Scheduled daily brief** (06:10 London) — proactive market radar
2. **MCP ecosystem signals** — track protocol/tooling shifts
3. **Competitor detection** — Screenpipe, Rowboat, Hyper, LangChain, CrewAI, AutoGen, Letta
4. **Demand signals** — RFPs, tenders, G-Cloud, DOS, "hiring AI agent" posts
5. **Pricing intelligence** — pilot costs, retainers, ARR/MRR data points
6. **Regulatory shifts** — FCA, PRA, GDPR, GLBA, SOX, HIPAA, ITAR, ISO 27001, Cyber Essentials, UK defence, marine compliance
7. **@mention fallback** — acknowledgment + context capture

**Rationale:**
- Covers full market intelligence spectrum: supply (competitors), demand (RFPs), pricing, regulatory
- Scheduled brief creates reliable daily heartbeat
- Keyword triggers capture organic chat signals
- Tasks flow directly to Geppetto for fleet specification

**Trade-offs:**
- High trigger sensitivity → may create noise tasks (mitigated by priority tiers)
- Requires external source integration (HackerNews, GitHub, LinkedIn, Reddit) not yet built
- `workflow` action type not yet implemented in backend

**Outcome:** ✅ RoE added to `RULES_OF_ENGAGEMENT.md` after FinOps section.

---

## DECISION-003: Add Geppetto (Solution Architect) Agent RoE

**Timestamp:** 2026-08-11 18:51:00 (same session)
**Context:** Complement Moneypenny's intel → spec pipeline.

**Decision:** Define Geppetto RoE with 5 trigger rules covering:
1. **Event-driven from Moneypenny** — `task.created` with market intel tags → fleet spec
2. **Client RFP handling** — RFP + requirements + client + fleet/agents/MCP keywords → client fleet spec (Critical)
3. **Internal architecture needs** — tech debt, standardization, new MCP, architecture review → architecture initiative
4. **Moneypenny brief completion** — `workflow.completed` for daily brief → extract action items for geppetto/closer/architect
5. **@mention fallback** — acknowledgment + spec drafting promise

**Rationale:**
- Closes the **intel → spec** loop automatically
- Event-driven from Moneypenny tasks ensures zero-latency handoff
- Client RFP path enables rapid proposal response
- Internal tech debt capture prevents architecture rot

**Trade-offs:**
- Depends on `workflow.completed` event type not yet implemented
- `run_analysis` action type not yet implemented
- Creates tasks for agents (closer, architect) not yet defined

**Outcome:** ✅ RoE added to `RULES_OF_ENGAGEMENT.md` after Moneypenny section.

---

## Business Loop Validation

**Master Question:** *"These agents are meant to be covering the business aspects we will be using for building the business and product correctly, do you agree they would?"*

**Answer:** **Yes.** The Moneypenny → Geppetto pipeline covers:

| Phase | Agent | Output |
|-------|-------|--------|
| **Intel** | Moneypenny | Market signals → categorized tasks |
| **Spec** | Geppetto | Fleet specs (topology, MCP servers, deploy arch) |
| **Build** | Scotty / MCP-BUILD | Implementation |
| **Deploy** | Deployment | Infrastructure provisioning |
| **Monitor** | Fleet-Ops | Health, cost, performance |

**Gaps Identified:**
1. Closer (sales/proposal) agent not yet defined — needed for RFP response
2. Architect (technical) agent not yet defined — needed for detailed design
3. Deployment agent not yet defined — needed for infra
4. Fleet-Ops agent not yet defined — needed for monitoring
5. External source connectors (HackerNews, GitHub, LinkedIn, Reddit) not built
6. Workflow engine (`workflow.completed`, `run_analysis`) not implemented

**Next Steps:** Define remaining 4 agents, build workflow engine, implement source connectors.

---

## Wikilinks

- [[Mission Control Dashboard]]
- [[RULES_OF_ENGAGEMENT]]
- [[Moneypenny (Business Intelligence)]]
- [[Geppetto (Solution Architect)]]
- [[Server.py Bug Fix]]
- [[Business Loop Architecture]]