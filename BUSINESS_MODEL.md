# Local-First Multi-Agent AI Agency — Business Model

> **Mission:** Build the premier agency for deploying private, local-first AI agent fleets on consumer hardware for regulated industries and data-sovereign organizations.

---

## 1. Core Business Model: "Agent Fleet as a Service" (AFaaS)

### Value Proposition
> **"Your data never leaves your premises. Your agents run on your hardware. We design, deploy, and operate the fleet."**

### Three Revenue Streams

| Stream | Model | Target | Price | Margin |
|--------|-------|--------|-------|--------|
| **1. Fleet Deployment** | Project + Retainer | Regulated firms (finance, legal, healthcare, defense) | £15K–£50K setup + £5K–£15K/mo | 70% |
| **2. MCP Server Products** | License + Support | AI agent startups, dev teams | £5K–£50K/project or £2K/mo per server | 85% |
| **3. Local LLM Optimization** | Consulting + Benchmarks | Enterprises with AMD/Intel fleets | £200–£400/hr or £10K fixed audit | 80% |

---

## 2. Agent Fleet Architecture (12 Agents)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OBI-WAN (CEO / Orchestrator)                         │
│  Strategy • Client Relations • Quality Gate • Resource Allocation           │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  SALES DIV    │      │  ENGINEERING  │      │  OPERATIONS   │
│  (3 agents)   │      │  (5 agents)   │      │  (3 agents)   │
└───────┬───────┘      └───────┬───────┘      └───────┬───────┘
        │                      │                      │
   ┌────┴────┐            ┌────┴────┐            ┌────┴────┐
   ▼         ▼            ▼         ▼            ▼         ▼
LEAD-GEN  PROPOSAL    MCP-BUILD  AGENT-CORE   FLEET-OPS  SEC-AUDIT
COLD-OUT  CLOSER      FIN-DATA   MEMORY-SYS   MONITOR    COMPLIANCE
                                        DEPLOYMENT
```

### Agent Roster (12 Total)

| # | Agent | Role | Primary Skills | Reports To |
|---|-------|------|----------------|------------|
| 1 | **OBI-WAN** | CEO / Orchestrator | Strategy, delegation, vault mgmt, client comms | — |
| 2 | **LEAD-GEN** | Outbound Sales | Research, cold email, LinkedIn, CRM | OBI-WAN |
| 3 | **PROPOSAL** | Technical Sales | Solution design, pricing, SOW writing | OBI-WAN |
| 4 | **CLOSER** | Deal Closing | Negotiation, contract review, onboarding | OBI-WAN |
| 5 | **MCP-BUILD** | MCP Server Engineer | TypeScript/Python, MCP spec, Obsidian, APIs | OBI-WAN |
| 6 | **AGENT-CORE** | Agent Runtime Engineer | Hermes, delegation, local LLMs, vectorbt | OBI-WAN |
| 7 | **FIN-DATA** | Financial Data Specialist | Alpha Vantage, FRED, quantitative research | OBI-WAN |
| 8 | **MEMORY-SYS** | Knowledge Graph Engineer | Obsidian, Neo4j, RAG, embeddings, MCP | OBI-WAN |
| 9 | **DEPLOYMENT** | Infrastructure Engineer | Docker, Windows/Linux, Ollama, DirectML, CI/CD | OBI-WAN |
| 10 | **FLEET-OPS** | Fleet Operations | Monitoring, logging, cost tracking, alerting | OBI-WAN |
| 11 | **SEC-AUDIT** | Security/Compliance | GLBA/SOX/GDPR, penetration testing, audit trails | OBI-WAN |
| 12 | **COMPLIANCE** | Regulatory Specialist | Policy templates, evidence packs, client training | OBI-WAN |

---

## 3. Agent Specifications (Detailed)

### 1. OBI-WAN — CEO / Orchestrator
```yaml
model: nemotron-3-ultra (OpenRouter)
schedule: Continuous
tools: All (delegation, vault, web, terminal, browser, cron)
vault_scope: Full (C:\the force)
standing_orders:
  - Morning: Review fleet health, client comms, pipeline
  - Day: Delegate tasks, approve deliverables, client calls
  - Evening: Update vault, plan next day, commit git
  - Weekly: Board report (revenue, pipeline, utilization, blockers)
kpis:
  - Monthly Recurring Revenue (MRR)
  - Client satisfaction (NPS)
  - Agent utilization rate
  - Vault health score
```

### 2. LEAD-GEN — Outbound Sales
```yaml
model: qwen2.5:14b (local Ollama)
schedule: Mon-Fri 09:00-17:00
tools: browser, web_search, write_file, search_files
vault_scope: 03_Context/clients/, 03_Context/people/
targets:
  - 50 new qualified prospects/week
  - 10 discovery calls/week
  - Sources: YC directory, LinkedIn Sales Nav, HN "Who's Hiring", Crunchbase
output: prospects.json → PROPOSAL
```

### 3. PROPOSAL — Technical Sales
```yaml
model: qwen2.5:14b (local Ollama)
schedule: On-demand (triggered by LEAD-GEN)
tools: read_file, write_file, search_files, browser
vault_scope: 03_Context/clients/, templates/
inputs: prospect profile, discovery notes
outputs:
  - Solution architecture diagram
  - Pricing model (3 tiers)
  - Statement of Work (SOW)
  - Timeline with milestones
  - Risk mitigation section
```

### 4. CLOSER — Deal Closing
```yaml
model: nemotron-3-ultra (OpenRouter) — higher reasoning for negotiation
schedule: On-demand
tools: browser, write_file, terminal (for DocuSign/Contract tools)
vault_scope: 03_Context/clients/, 00_Master/secrets.md (contract templates)
kpis:
  - Close rate > 30%
  - Average contract value > £25K
  - Time-to-close < 30 days
```

### 5. MCP-BUILD — MCP Server Engineer
```yaml
model: deepseek-r1:8b (local Ollama) — reasoning for architecture
schedule: Project-based (sprint cycles)
tools: terminal, write_file, read_file, browser (docs), execute_code
vault_scope: 05_Skills/active/mcp-*/, 03_Context/references/mcp/
deliverables:
  - Obsidian Memory MCP Server (vault → MCP resources/tools)
  - Financial Data MCP Server (Alpha Vantage/FRED → MCP)
  - Hermes Delegation MCP Server (sub-agent spawn → MCP tools)
  - Custom client MCP servers (per project)
standards:
  - TypeScript (Node) or Python (FastMCP)
  - 100% test coverage
  - MCP Inspector verified
  - Published to npm/PyPI + GitHub
```

### 6. AGENT-CORE — Agent Runtime Engineer
```yaml
model: deepseek-r1:8b (local Ollama)
schedule: Project-based
tools: terminal, execute_code, write_file, read_file
vault_scope: 01_Obi-Wan/, 02_Sub-Agents/, 05_Skills/
deliverables:
  - Hermes agent templates (researcher, analyst, coder, etc.)
  - Delegation framework extensions
  - Local LLM optimization (quantization, batching, KV cache)
  - Vectorbt backtest framework for FIN-DATA
  - Agent communication protocol (vault-based)
```

### 7. FIN-DATA — Financial Data Specialist
```yaml
model: qwen2.5:14b-64k (local Ollama) — long context for reports
schedule: Daily 06:00 (market open prep) + on-demand
tools: execute_code, browser, read_file, write_file
vault_scope: 03_Context/projects/trading/, 03_Context/references/market-data/
data_sources:
  - Alpha Vantage (FX, equities, crypto)
  - FRED (macro: UNRATE, PAYEMS, CPI, FEDFUNDS)
  - Yahoo Finance (backup)
  - SEC EDGAR (filings)
products:
  - Daily macro brief (6:00 AM)
  - Weekly sector rotation report
  - Earnings call analysis (within 2 hrs)
  - Custom client research ($2K–$10K/report)
```

### 8. MEMORY-SYS — Knowledge Graph Engineer
```yaml
model: deepseek-r1:8b (local Ollama)
schedule: Project-based
tools: execute_code, write_file, read_file, terminal
vault_scope: 03_Context/references/knowledge-graph/, 05_Skills/active/memory-*/
tech_stack:
  - Obsidian (Markdown vault)
  - Neo4j (graph DB) or Kuzu (embedded)
  - sentence-transformers (embeddings)
  - MCP server for agent access
deliverables:
  - Auto-linking pipeline (vault → graph)
  - Entity extraction (financial, legal, marine)
  - Supersession chains (corrections link to originals)
  - Access-control tags (per Hyper model)
  - MCP interface (recall, save, propose_truth)
```

### 9. DEPLOYMENT — Infrastructure Engineer
```yaml
model: qwen2.5:14b (local Ollama)
schedule: Project-based + on-call
tools: terminal, write_file, read_file, browser
vault_scope: 03_Context/systems/, 05_Skills/active/deployment-*/
deliverables:
  - Docker Compose stacks (Ollama + Hermes + MCP servers)
  - Windows/Linux install scripts (PowerShell/Bash)
  - DirectML optimization configs (per GPU)
  - CI/CD pipelines (GitHub Actions → client servers)
  - Backup/restore procedures
  - Air-gap deployment guides
```

### 10. FLEET-OPS — Fleet Operations
```yaml
model: qwen2.5:14b (local Ollama)
schedule: Continuous (cron every 15 min)
tools: read_file, write_file, execute_code, terminal
vault_scope: 04_Daily_Logs/, 03_Context/clients/*/fleet/
monitoring:
  - Agent health (heartbeat, error rate, latency)
  - Token costs (local = £0, but track compute)
  - Delegation success/failure rates
  - Vault sync status
  - Disk/RAM/GPU utilization
alerts:
  - Agent down > 5 min → restart + notify
  - Delegation failure > 10% → investigate
  - Disk > 80% → cleanup + alert
  - Security event → SEC-AUDIT
dashboards: Grafana (local) + Obsidian daily notes
```

### 11. SEC-AUDIT — Security/Compliance
```yaml
model: deepseek-r1:8b (local Ollama)
schedule: Weekly + on-demand
tools: terminal, execute_code, browser, write_file
vault_scope: 03_Context/clients/*/security/, 00_Master/protocols.md
deliverables:
  - Penetration test reports (quarterly)
  - Data flow diagrams (for GLBA/SOX)
  - Access control matrices
  - Incident response plans
  - Vulnerability scans (OWASP ZAP, Trivy)
  - Supply chain audit (npm/PyPI deps)
certifications_target:
  - Cyber Essentials Plus (UK)
  - SOC 2 Type II (Year 2)
  - ISO 27001 (Year 3)
```

### 12. COMPLIANCE — Regulatory Specialist
```yaml
model: qwen2.5:14b-64k (local Ollama)
schedule: Project-based
tools: read_file, write_file, browser, terminal
vault_scope: 03_Context/clients/*/compliance/, templates/
deliverables:
  - Client-specific policy packs (GLBA, SOX, HIPAA, GDPR)
  - Evidence packs for auditors
  - Data Processing Addendums (DPAs)
  - Staff training materials
  - Regulatory change monitoring (FCA, SEC, ICO)
  - "Air-gapped by default" certification template
```

---

## 4. Financial Model

### Year 1 Projections (Conservative)

| Month | Clients | MRR | Cumulative Revenue | Team Costs | Net |
|-------|---------|-----|-------------------|------------|-----|
| 1-2   | 0       | £0  | £0                | £0         | £0  |
| 3     | 1       | £5K | £5K               | £0         | £5K |
| 4     | 2       | £12K| £17K              | £0         | £12K|
| 5     | 3       | £20K| £37K              | £0         | £20K|
| 6     | 4       | £28K| £65K              | £2K (tools)| £26K|
| 7     | 5       | £35K| £100K             | £2K        | £33K|
| 8     | 6       | £42K| £142K             | £2K        | £40K|
| 9     | 7       | £50K| £192K             | £3K        | £47K|
| 10    | 8       | £58K| £250K             | £3K        | £55K|
| 11    | 9       | £65K| £315K             | £3K        | £62K|
| 12    | 10      | £72K| £387K             | £3K        | £69K|

**Year 1 Target: £387K revenue, ~£350K net (before tax)**

### Year 2-3 Scale

| Year | Clients | Avg MRR | Annual Revenue | Agents | Human Hires |
|------|---------|---------|----------------|--------|-------------|
| 1    | 10      | £7.2K   | £387K          | 12     | 0           |
| 2    | 30      | £10K    | £1.8M          | 25     | 2 (Sales, PM) |
| 3    | 60      | £12K    | £4.5M          | 40     | 5 (Eng, Sales, Ops) |

---

## 5. Client Acquisition Funnel

```
┌─────────────┐   50/wk   ┌─────────────┐   10/wk   ┌─────────────┐   3/wk   ┌─────────────┐
│  LEAD-GEN   │ ───────▶ │  PROPOSAL   │ ───────▶ │  CLOSER     │ ───────▶ │  ONBOARD    │
│  (outbound) │           │  (design)   │           │  (negotiate)│           │  (DEPLOY)   │
└─────────────┘           └─────────────┘           └─────────────┘           └─────────────┘
                                                              │
                                                              ▼
┌─────────────┐           ┌─────────────┐           ┌─────────────┐
│  FLEET-OPS  │ ◀──────── │  ENGINEERING│ ◀──────── │  DELIVERY   │
│  (monitor)  │           │  (build)    │           │  (handoff)  │
└─────────────┘           └─────────────┘           └─────────────┘
                                                              │
                                                              ▼
┌─────────────┐           ┌─────────────┐           ┌─────────────┐
│  RENEW/     │ ◀──────── │  SEC-AUDIT  │ ◀──────── │  COMPLIANCE │
│  EXPAND     │           │  (quarterly)│           │  (ongoing)  │
└─────────────┘           └─────────────┘           └─────────────┘
```

### Lead Sources (Prioritized)
1. **YC S24/S25 agent companies** — 50+ targets, need MCP servers
2. **UK Family Offices / Wealth Managers** — GLBA/SOX, £500M+ AUM, no Bloomberg budget
3. **Law Firms (UK/US)** — Document review, contract analysis, air-gapped required
4. **Healthcare/Pharma** — HIPAA, clinical trial analysis, local-only
5. **Defense/Gov Contractors** — ITAR, classified, absolute data sovereignty
6. **Shipping/Logistics** — Your marine background, commodity tracking, port ops

---

## 6. Productized Offers (Fixed Price → Recurring)

| Product | Price | Delivery | Recurring |
|---------|-------|----------|-----------|
| **MCP Server: Obsidian Memory** | £15K | 3 weeks | £2K/mo support |
| **MCP Server: Financial Data** | £10K | 2 weeks | £1.5K/mo support |
| **MCP Server: Custom** | £25K–£50K | 4-6 weeks | £3K/mo support |
| **Local LLM Optimization Audit** | £10K | 1 week | — |
| **Fleet Deployment (5 agents)** | £30K setup | 4 weeks | £8K/mo managed |
| **Fleet Deployment (20 agents)** | £75K setup | 8 weeks | £20K/mo managed |
| **Financial Research Agent** | £5K/mo | 2 weeks | £5K/mo |
| **Compliance Certification Pack** | £15K | 3 weeks | £3K/mo monitoring |

---

## 7. Operational Rhythms

### Daily (Automated via Cron)
| Time | Agent | Action |
|------|-------|--------|
| 06:00 | FIN-DATA | Daily macro brief → vault + email |
| 07:00 | OBI-WAN | Pipeline review, task delegation |
| 09:00 | LEAD-GEN | Outbound batch (50 prospects) |
| 12:00 | FLEET-OPS | Health check all client fleets |
| 17:00 | OBI-WAN | Day summary, vault commit |
| 23:00 | FLEET-OPS | Backup verification |

### Weekly
| Day | Focus |
|-----|-------|
| Monday | Pipeline review, sprint planning, client calls |
| Tuesday | Engineering sprint (MCP/agent builds) |
| Wednesday | Sales calls, demos, proposals |
| Thursday | Security/compliance work, audits |
| Friday | Retrospective, vault health, content marketing |

### Monthly
- **1st**: Board report (MRR, pipeline, utilization, blockers)
- **15th**: Client health check (NPS, usage, expansion ops)
- **Last Friday**: Security audit, vulnerability scan, dependency update

---

## 8. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **MCP standard changes** | Medium | High | Adapter layer; contribute to spec; diversify (ACP, A2A) |
| **Local LLM demand drops** | Low | High | Consulting + product + managed service diversification |
| **Client data breach** | Low | Critical | Air-gap by design; quarterly pen tests; insurance |
| **Key person dependency (you)** | High | High | Document everything in vault; agent SOPs; hire Year 2 |
| **Hardware limits** | Medium | Medium | Quantization expertise; cloud burst option; eGPU roadmap |
| **YC competitors enter** | High | Medium | Partner don't compete; sell them MCP servers; move upstack |

---

## 9. Immediate 30-Day Sprint

### Week 1: Foundation
- [ ] OBI-WAN: Finalize agent specs, create vault structure for all 12 agents
- [ ] MCP-BUILD: Build Obsidian Memory MCP Server (core product)
- [ ] DEPLOYMENT: Docker stack for local dev + client deployment
- [ ] SEC-AUDIT: Baseline security scan of current stack

### Week 2: Product + Demo
- [ ] MCP-BUILD: Build Financial Data MCP Server
- [ ] MEMORY-SYS: Knowledge graph pipeline (vault → Neo4j → MCP)
- [ ] AGENT-CORE: Agent templates (researcher, analyst, coder)
- [ ] OBI-WAN: Record 5-min Loom demos for each product

### Week 3: Sales Launch
- [ ] LEAD-GEN: 150 YC agent company prospects → CRM
- [ ] PROPOSAL: 3 template SOWs (MCP, Fleet, Optimization)
- [ ] CLOSER: Contract templates, pricing calculator
- [ ] OBI-WAN: HN "Show HN" post, LinkedIn announcement

### Week 4: First Revenue
- [ ] LEAD-GEN: 50 cold emails/day
- [ ] PROPOSAL: 5 proposals out
- [ ] CLOSER: 3 discovery calls → 1 pilot
- [ ] FLEET-OPS: Monitoring dashboard v1

---

## 10. Vault Structure for Business

```
C:\the force\
├── 00_Master/
│   ├── profile.md              # Your profile
│   ├── protocols.md            # Business protocols
│   ├── secrets.md              # API keys, credentials
│   └── contracts/              # Templates (MSA, SOW, NDA, DPA)
├── 01_Obi-Wan/                 # CEO agent
│   ├── identity.md
│   ├── state.md
│   ├── kpis.md
│   └── board_reports/
├── 02_Sub-Agents/
│   ├── registry.md             # All 12 agents registered
│   ├── delegation-log.md
│   └── templates/              # 12 agent templates
├── 03_Context/
│   ├── clients/                # Per-client folders
│   │   └── {client-name}/
│   │       ├── profile.md
│   │       ├── contract.md
│   │       ├── fleet/
│   │       ├── security/
│   │       ├── compliance/
│   │       └── billing/
│   ├── projects/
│   ├── references/
│   │   ├── mcp/
│   │   ├── knowledge-graph/
│   │   ├── market-data/
│   │   └── compliance/
│   └── systems/
├── 04_Daily_Logs/
│   ├── YYYY-MM-DD/
│   │   ├── master-log.md
│   │   ├── sales-log.md
│   │   ├── engineering-log.md
│   │   ├── ops-log.md
│   │   └── security-log.md
├── 05_Skills/
│   ├── active/
│   │   ├── mcp-server-dev/
│   │   ├── agent-runtime/
│   │   ├── local-llm-opt/
│   │   ├── financial-research/
│   │   ├── knowledge-graph/
│   │   ├── deployment/
│   │   ├── fleet-ops/
│   │   ├── security-audit/
│   │   └── compliance/
│   └── templates/
├── 06_Business/
│   ├── financials/
│   ├── pipeline/
│   ├── marketing/
│   └── legal/
└── AGENT_FLEET_SPEC.md         # This file
```

---

## 11. Go/No-Go Decision Points

| Milestone | Target | Go Criteria | No-Go Action |
|-----------|--------|-------------|--------------|
| **MCP Server v1** | Day 10 | Works with Claude Code + Obsidian | Pivot to consulting-only |
| **First Discovery Call** | Day 15 | 3+ qualified calls | Increase outbound 3x |
| **First Pilot Signed** | Day 30 | £10K+ pilot | Re-evaluate pricing/offer |
| **3 Pilots Running** | Day 60 | £30K MRR pipeline | Hire human sales |
| **£10K MRR** | Day 90 | Sustainable | Scale engineering |
| **£25K MRR** | Day 180 | Predictable | Series A or bootstrap |

---

## 12. Your Role Evolution

| Phase | Your Time | Focus |
|-------|-----------|-------|
| **Months 1-3** | 80% technical | Build agents, MCP servers, deployments |
| **Months 4-6** | 50% technical / 50% sales | Close deals, manage delivery, hire |
| **Months 7-12** | 20% technical / 80% CEO | Strategy, fundraising, key accounts |
| **Year 2+** | 10% technical / 90% CEO | Vision, board, acquisitions |

---

## 13. Summary: Why This Works

1. **Unique Stack** — Hermes + Obsidian + Ollama + Delegation = nobody else has this
2. **Real Demand** — YC companies, regulated firms, local-first movement all pulling
3. **Defensible Moats** — AMD/DirectML expertise, air-gapped architecture, marine domain
4. **Scalable Model** — Agents do the work; you orchestrate; margins improve with scale
5. **Multiple Exits** — SaaS product (MCP servers), Agency (services), Platform (AgentOps)

---

**Decision: Deploy 12-agent fleet. Start Week 1 sprint Monday.**

*Probability of £100K+ ARR by Month 6: 75%. Probability of £1M+ ARR by Month 18: 45%. Recommendation: Execute.*