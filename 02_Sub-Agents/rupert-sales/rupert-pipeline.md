# 🔄 AFaaS Sales Pipeline — Live Deal Tracker

**Maintained by:** Rupert (Business Manager), reviewed weekly with Sales Manager  
**Last Updated:** 2026-08-20  

---

## 📊 Current State: Ready to Load Data

All agents instantiated and ready. No live deals yet (pre-revenue).

| Stream | Pipeline Value (£) | Coverage Ratio | Deals In Pipeline |
|--------|-------------------|----------------|-------------------|
| **Fleet** (\12-agent local-first fleet) | £0 → building to £250K target | 4x | — |
| **MCP** (3 core servers → afaaS server) | £0 → building to £100K target | 4x | — |
| **LLM Opt** (DirectML on AMD hardware) | £0 → building to £37K target | 4x | — |

---

## 🗂️ Pipeline Stages & Criteria

| Stage | Criteria | Min Probability (%) | Max Days in Stage |
|-------|----------|---------------------|-------------------|
| **new-lead** | Fresh from Lead Gen; no interaction yet | <20% | 5 days |
| **qualified** | Budget, authority, need confirmed | >25% | 7 days |
| **discovery** | Technical fit checked with Geppetto | >40% | 7 days |
| **proposal** | Commercial terms drafted and sent | >60% | 14 days |
| **negotiation** | Terms under client review | >75% | 14 days |
| **closed-won** | Contract signed, payment received | 100% | — |
| **closed-lost** | Client declined, competitor won | 0% | — |

---

## 📋 Current Deals Queue (Aug 2026)

*Empty — fleet in pre-revenue launch phase. Loading prospects via Lead Gen Agent once pipeline structure ready.*

```yaml
- lead_id: "OPPF-001"
  company: "[REDACTED]"
  stream: "fleet"
  stage: "new-lead"
  probability: null
  qualified_at: null
  source: "linkedin-directory"
  status: "waiting-for-touch"

---

- lead_id: "OPPF-002"
  company: "[REDACTED]"
  stream: "mcp"
  stage: "qualified"
  probability: 30%
  qualified_at: null
  source: "funding-round-watch"
  status: "ready-for-discovery"
```

---

## 🎯 Sales Targets by Q4 2026

| Metric | Target | Current Progress |
|--------|--------|------------------|
| **Fleet Stream** | £250K (12-agent deployments) | £0 — building from pilot |
| **MCP Stream** | £100K (3 core servers) | £0 — 90-day timeline |
| **LLM Opt Stream** | £37K (DirectML hardware optimization) | £0 — DRIFTING → K-2SO pivot |
| **Total Year 1 Revenue** | ¥{¥}¥\{¥387K} | £0 — pre-revenue launch phase |

---

## 📅 Weekly Review Cadence

### Monday Morning (Rupert): Pipeline Health Check
- [ ] Update all deal stages, probabilities, close dates  
- [ ] Flag stalled deals (>14 days no movement)  
- [ ] Identify 3 priority actions for week  
- [ ] Commit to forecast coverage ratio  

### Wednesday Midpoint: Progress Scan  
- [ ] Win/loss analysis on recently closed  
- [ ] Segment objection patterns; feed back to Proposal Writer  
- [ ] Review expansion opportunities in current client base  

### Friday Closeout: Rollup & Prep  
- [ ] Forecast update with commit vs. actual variance  
- [ ] Plan next sprint for pipeline build  
- [ ] Handoff notes to next week’s team  

---

## 📌 Notes

*Pre-revenue launch phase. All infrastructure wired, agents ready. Pipeline load begins once Lead Gen Agent identifies new prospects for fleet deployment.*

