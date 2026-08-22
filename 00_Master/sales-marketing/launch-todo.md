# MCP Product Launch — Master Todo List

## Obsidian MCP v1.0.0 — Launch Checklist

### Distribution & Packaging (Week 1)
- [ ] **TestPyPI upload** — verify package installs cleanly (`pip install -i https://test.pypi.org/simple/ obsidian-mcp`)
- [ ] **PyPI production publish** — `twine upload dist/*` (requires PyPI account + API token)
- [ ] **DXT bundle verification** — install `obsidian-mcp-1.0.0.dxt` in Claude Desktop, test all 6 tools
- [ ] **MCP Registry submission** — PR to https://github.com/modelcontextprotocol/registry
- [ ] **GitHub repo public** — push to `github.com/afaas/obsidian-mcp`, add topics: `mcp`, `obsidian`, `mcp-server`, `local-first`, `air-gapped`
- [ ] **Docker image** — build/push to GHCR (`ghcr.io/afaas/obsidian-mcp:1.0.0`)
- [ ] **npm/npx wrapper** — optional, for JS clients

### Sales Enablement (Week 1-2)
- [ ] **Landing page** — GitHub Pages at `afaas.github.io/obsidian-mcp/` or custom domain
- [ ] **One-pager PDF** — export from `obsidian-mcp-sales-pack.md`
- [ ] **Demo video (5 min)** — record Loom: DXT install → configure vault → read/write/search
- [ ] **Technical datasheet** — architecture, security controls, specs
- [ ] **Security questionnaire** — pre-fill for SOC2, ISO27001, Cyber Essentials
- [ ] **ROI calculator** — simple spreadsheet: cloud AI vs local MCP TCO
- [ ] **Case study template** — ready for first pilot client

### Content Marketing (Week 2)
- [ ] **Blog Post 1**: "Building Air-Gapped MCP Servers for Regulated Industries" 
- [ ] **Blog Post 2**: "Why Your AI Agents Need Local Vault Access (Not Cloud RAG)"
- [ ] **Blog Post 3**: "MCP Security: Threat Modeling for Enterprise Deployment"
- [ ] **LinkedIn posts** — 3 posts from blog content, tag #MCP #AI #LocalFirst
- [ ] **Hacker News submission** — technical post (Blog 1)
- [ ] **Reddit/Lobsters** — relevant communities

### Direct Sales (Week 2-3)
- [ ] **Target account list** — 20 UK companies (finance, legal, marine, defense)
- [ ] **Decision maker research** — LinkedIn: CTO, VP Eng, Head of AI, Knowledge Manager
- [ ] **Cold outreach sequence** — 3-touch: value → demo → case study
- [ ] **Calendly link** — 30-min discovery calls
- [ ] **Proposal template** — Starter/Professional/Enterprise tiers
- [ ] **NDA template** — for technical deep-dives

### Team & Operations (Week 3-4)
- [ ] **Sales Engineer job spec** — part-time, UK-based, technical + sales
- [ ] **Support Engineer job spec** — part-time, UK-based, MCP/Linux/Python
- [ ] **Contractor agreements** — IP assignment, confidentiality
- [ ] **Support runbook** — common issues, escalation paths, SLA definitions
- [ ] **Monitoring/alerting** — for deployed instances (health checks, error rates)
- [ ] **Billing/invoicing** — Stripe or GoCardless for £500/mo recurring

### Post-First-Sale Hardening (Phase 2b — Month 4–5)
- [ ] **Backup/Restore SOP** — automated vault + DB snapshots, monthly tested restore
- [ ] **UPS Integration** — NUT/apcupsd graceful shutdown, state persistence on power loss
- [ ] **Health Monitoring** — MCP server heartbeats, Prometheus/Grafana or lightweight alerting
- [ ] **Disaster Recovery Drill** — full restore to fresh hardware, < 4hr RTO, < 1hr RPO
- [ ] **DR Runbook** — documented, added to delivery playbook

### Filesystem MCP Hardening (Parallel Track)
- [ ] Config schema (pydantic-settings)
- [ ] Missing tools: `fs_search`, `fs_patch`
- [ ] Structured logging (structlog)
- [ ] CI workflow verification
- [ ] Tests ≥80% coverage
- [ ] CHANGELOG + 1.0.0
- [ ] DXT bundle + TestPyPI + PyPI

### PostgreSQL MCP Hardening (Parallel Track)
- [ ] API key auth for HTTP/SSE
- [ ] Health endpoints
- [ ] Rate limiting
- [ ] DXT bundle
- [ ] TestPyPI + PyPI

---

## Account Setup Required

| Platform | Account Needed | Purpose | Status |
|----------|---------------|---------|--------|
| **PyPI** | Organization + API token | Production package publishing | ❌ |
| **TestPyPI** | Account + API token | Staging verification | ✅ (in progress) |
| **GitHub** | `afaas` org + repo | Source, CI, Docker, Marketplace | ❌ |
| **MCP Registry** | GitHub PR access | Official discovery | ❌ |
| **Claude Desktop Extensions** | DXT submission | 1-click install for users | ❌ |
| **GHCR / Docker Hub** | Org + PAT | Container images | ❌ |
| **Stripe / GoCardless** | Business account | Recurring billing (£500/mo) | ❌ |
| **Calendly** | Pro account | Discovery call booking | ❌ |
| **Loom / Vidyard** | Pro account | Demo video hosting | ❌ |
| **LinkedIn Sales Nav** | Team account | Prospect research/outreach | ❌ |

---

## One-Liner Variations (Test These)

| Channel | One-Liner |
|---------|-----------|
| **MCP Registry** | "Local-first Obsidian vault MCP — air-gapped, enterprise auth, UK support" |
| **GitHub Marketplace** | "Secure Obsidian vault access for AI agents. Zero cloud. Full frontmatter. 1-click DXT install." |
| **LinkedIn** | "Your AI agents can finally read your Obsidian vault — locally, securely, compliantly." |
| **Cold Email** | "Helping [FinTech/Legal/Marine] teams give AI agents vault access without cloud egress." |
| **Hacker News** | "Show HN: Production-grade local MCP server for Obsidian — air-gapped, auth, structured logs" |

---

## Success Metrics (90 Days)

| Metric | Target |
|--------|--------|
| PyPI downloads/month | 500+ |
| DXT installs | 100+ |
| Discovery calls booked | 20 |
| Pilot proposals sent | 10 |
| Paid pilots signed | 3 |
| Monthly recurring revenue | £1,500+ (3 × £500) |
| Blog post views | 5,000+ total |
| MCP Registry stars | 50+ |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| TestPyPI upload fails | Medium | Low | Retry with longer timeout; verify credentials |
| DXT doesn't install in Claude | Low | High | Test locally first; document manual fallback |
| No inbound leads | Medium | High | Direct outreach + content marketing dual track |
| Can't hire Sales Engineer | Medium | Medium | Founder-led sales first; contractor backup |
| Competitor launches similar | Low | Medium | Speed to market; domain expertise (marine/finance) moat |
| Client requires feature we lack | High | Medium | 90-day support includes 2 custom tools — build fast |

---

## Next Immediate Actions (Today)

1. **Wait for TestPyPI upload** — check `proc_ea636acfede4` completion
2. **Verify DXT locally** — drag `obsidian-mcp-1.0.0.dxt` into Claude Desktop
3. **Create PyPI account** — pypi.org, enable 2FA, create API token
4. **Create GitHub org** — `afaas`, push obsidian-mcp repo
5. **Schedule 1hr** — record demo video (Loom free tier works)