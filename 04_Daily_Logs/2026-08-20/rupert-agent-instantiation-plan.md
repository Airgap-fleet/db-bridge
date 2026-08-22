# 🚀 Rupert Agent Fleet: Instantiation & Deployment Plan

**Date:** August 20, 2026  
**Owner:** Obi-Wan (Orchestrator) / Rupert (Business Manager)  
**Target:** Activate 5 new sales agents under Rupert within 5 business days  

---

## 📋 Executive Summary

Rupert is instantiated and ready. **Phase 1** requires instantiating 5 specialized sales support agents:
- **Sales Manager** — Overall sales strategy, quota tracking, coaching
- **Lead Gen Agent** — Prospecting, enrichment, list building  
- **CRM Agent** — Pipeline hygiene, stage progression, activity logging
- **Proposal Writer** — Technical specs + commercial terms drafting
- **Account Executive** — Client relationships, negotiation, close

These agents operate in parallel under Rupert's direction but with distinct roles.

---

## 🎯 Phase 1: Team Assembly & Instantiation (Days 1-2)

### Day 1: Foundation & Lead Gen Agent
**Objectives:**
- [ ] Write Sales Manager soul spec
- [ ] Write Lead Gen Agent soul spec  
- [ ] Create agent folders in `C:\the force\02_Sub-Agents\rupert-sales/`
- [ ] Provision Lead Gen Agent (delegate_task to instantiate)

**Deliverables:**
- 2 soul.md files  
- 1 delegate_task log showing Lead Gen instantiation

### Day 2: CRM & Proposal Team
**Objectives:**
- [ ] Write CRM Agent soul spec
- [ ] Write Proposal Writer soul spec
- [ ] Provision CRM Agent (delegate_task)
- [ ] Provision Proposal Writer (delegate_task)

**Deliverables:**
- 2 soul.md files  
- 2 instantiation logs

---

## 🏗️ Phase 2: Infrastructure Wiring (Days 3-4)

### Day 3: Dashboard Integration
**Objectives:**
- [ ] Verify Flask server at port 8420 routes are clean (move from module-local to app-level)
- [ ] Wire each agent's SSE endpoint → `/api/sse/{agent_id}`
- [ ] Implement RoE enforcement middleware (RBAC checks)
- [ ] Create `C:\the force\03_Context\rupert-sales-dashboard/` for shared state

**Deliverables:**
- Functional dashboard with Kanban + agent sidebar  
- SSE connection logs (all 5 agents connected)  
- RoE enforcement verified

### Day 4: Pipeline & Workflow Config
**Objectives:**
- [ ] Rupert populates `C:\the force\02_Sub-Agents\rupert-sales/pipeline.md`
- [ ] Lead Gen Agent triggers on fresh lists → CRM
- [ ] CRM stages prospects → Proposal queue
- [ ] Proposal Writer drafts → Account Executive reviews

**Deliverables:**
- Pipeline structure  
- Event-driven workflow diagram  
- End-to-end trace log

---

## 🔄 Phase 3: Work Delegation & Live Cycle (Day 5+)

### Day 5: Go-Live Simulation
**Objectives:**
- [ ] Load mock prospect list (10 targets)
- [ ] Run end-to-end pipeline test cycle
- [ ] Measure latency lead → close (benchmark)
- [ ] Identify bottlenecks

**Deliverables:**
- Test results report  
- Bottleneck analysis  
- Optimization recommendations

### Day 6+: Production Handover
**Objectives:**
- [ ] Rupert ingests real pipeline data
- [ ] Agents handle live traffic
- [ ] Master approves pricing/contract templates

**Deliverables:**
- Live production metrics  
- Weekly performance review  

---

## 📁 Vault Structure (Phase 1 Output)

```
C:\the force\02_Sub-Agents\rupert-sales/
├── sales-manager/
│   ├── soul.md          # Created Day 2
│   └── config.yaml      # Agent model: claude-3.5-sonnet / toolsets
├── lead-gen-agent/
│   ├── soul.md          # Created Day 1
│   └── enrichment-templates/
├── crm-agent/
│   ├── soul.md          # Created Day 2
│   └── stages/
├── proposal-writer/
│   ├── soul.md          # Created Day 2
│   ├── templates/       # Commercial proposals
│   └── technical-specs/ # For Geppetto wiring
├── account-executive/
│   ├── soul.md          # Created Day 3
│   └── negotiation-guides/
└── pipeline.md          # Live deal tracker (Rupert maintains)
```

---

## ⚠️ Blockers & Risks

| Risk | Mitigation |
|-------|------------|
| Flask routes still module-local | Move to app-level on Day 3 morning |
| SSE connections timeout | Test with curl + `timeout=60` |
| RoE policy conflicts | Draft in proposal phase, test before deploy |
| Tool call limits per agent | Batch tool calls across parallel agents |

---

## 🎯 Success Metrics (Phase 1)

- **Coverage:** All 5 agents instantiated with soul specs  
- **Integration:** SSE connections confirmed for all  
- **Latency:** Lead → Close <48 hrs on test cycle  
- **Reliability:** RoE enforcement passing 95%+ rate  

---

## 📅 Immediate Actions (Next 2 Hours)

1. Create `C:\the force\02_Sub-Agents\rupert-sales/` directory
2. Write Sales Manager soul.md
3. Write Lead Gen Agent soul.md  
4. Delegate instantiation via `delegate_task`
5. Verify with `process(action='list')`

Let's begin.
