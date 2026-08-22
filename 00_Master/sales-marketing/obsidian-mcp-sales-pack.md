# Local Vault MCP — Sales One-Liner

**Local-first knowledge vault access for AI agents — air-gapped, regulated-industry ready, runs on your hardware. Model-agnostic: bring your own LLM (local Ollama, Claude, GPT-4, etc.).**

---

# Elevator Pitch (30 seconds)

> "You use a local knowledge vault — Obsidian, markdown files, structured notes. Your AI agents need access to it. But you're in finance, legal, or marine — you can't send data to the cloud. Local Vault MCP gives your agents secure, local-only read/write/search access to your vault with full frontmatter support, path sandboxing, and API-key authentication. It installs in one click via DXT, runs on commodity hardware, and costs a fraction of cloud AI solutions. **It's model-agnostic — connect any MCP-compatible LLM: local (Ollama: 7B-14B models on 32GB RAM) or cloud (Claude, GPT-4).** We're UK-based, marine-industry veterans, and we deploy on your infrastructure — not ours."

---

# Value Proposition Matrix

| Buyer Persona | Pain Point | Our Solution | Quantified Value |
|--------------|------------|--------------|------------------|
| **CTO / VP Engineering (FinTech)** | "Can't use AI agents with internal docs — data residency / compliance" | Air-gapped MCP server, runs on-prem, zero egress | Avoid £500K+ cloud AI spend; pass SOC2/ISO27001 audit |
| **Knowledge Manager (Legal)** | "Agents hallucinate on case law — need grounded RAG on our vault" | Local RAG via Obsidian vault + frontmatter search | 80% reduction in hallucination; cite actual notes |
| **Marine Fleet Operator** | "Offline at sea — cloud AI useless" | Fully local, runs on vessel hardware (AMD 780M iGPU) | Continuous ops at sea; no satellite dependency |
| **Security Officer** | "MCP servers are black boxes — no audit trail" | Structured JSON logs, path sandboxing, API keys, threat model | Passes security review in days, not months |

---

# Competitive Landscape & Positioning

| Competitor | Model | Gap We Fill |
|------------|-------|-------------|
| **Official MCP Servers** (Filesystem, GitHub, etc.) | Cloud-first, generic, no auth | **Local-first, vault-native, enterprise auth, UK support** |
| **Zapier / Make MCP** | SaaS, per-action pricing, data leaves infra | **One-time license + flat monthly, zero data egress** |
| **Custom MCP builds** | 3-6 months dev, £50K-150K/yr maintenance | **Production-ready in hours, £2K setup + £500/mo support** |
| **LangChain / LlamaIndex local** | Framework, not product — you build & maintain | **Batteries-included: install, configure, done** |
| **Cloud AI platforms** (OpenAI, Anthropic, etc.) | Model + hosting bundled, data egress required | **Model-agnostic: you choose local (Ollama) or cloud — no lock-in** |

**Our Wedge**: *The only production-grade, local-first vault MCP with enterprise auth, structured logging, UK-based support for regulated industries, and full model flexibility — run 7B for speed or 14B for quality on the same hardware.*

---

# Product Package (What They Buy)

| Tier | Price | Includes |
|------|-------|----------|
| **Starter** | £2K setup + £500/mo | DXT install, config hardening, 90-day support, 2 custom tools |
| **Professional** | £5K setup + £1.5K/mo | Starter + Docker/K8s deploy, RBAC, rate limiting, SLA, threat model review |
| **Enterprise** | £15K setup + £5K/mo | Professional + on-prem deployment, dedicated Slack, custom integrations, penetration test report |

---

## Model Selection Guide (For Clients)

**Your MCP server works with any MCP-compatible LLM.** We recommend:

| Use Case | Model | Size | Speed (AMD 780M) | Best For |
|----------|-------|------|------------------|----------|
| **Daily coding / fast responses** | `qwen2.5-coder:7b` | 4.7 GB | ~30-50 tok/s | Interactive dev, quick edits |
| **Complex refactors / architecture** | `qwen2.5-coder:14b` | 9.0 GB | ~10-20 tok/s | Deep reasoning, large changes |
| **Planning / reasoning tasks** | `deepseek-r1:14b` | 9.0 GB | ~10-20 tok/s | Chain-of-thought, design decisions |
| **General chat / long context** | `qwen3.5:9b` | 6.6 GB | ~20-35 tok/s | 256K context, balanced |

**Default recommendation**: `qwen2.5-coder:7b` for speed. Switch to `qwen2.5-coder:14b` or `deepseek-r1:14b` for quality-intensive tasks. All run locally on 32GB RAM — no cloud needed.

---

# Sales Assets Needed (Checklist)

- [ ] **One-pager PDF** — for email attachments, LinkedIn
- [ ] **Landing page** — GitHub Pages or simple site
- [ ] **Demo video** (5 min) — install via DXT, show read/write/search
- [ ] **Technical datasheet** — specs, architecture, security controls
- [ ] **Case study template** — "How [Client] secured AI access to legal vault"
- [ ] **ROI calculator** — cloud vs local cost comparison
- [ ] **Security questionnaire responses** — pre-filled for common frameworks
- [ ] **DXT listing** — Claude Desktop Extensions marketplace
- [ ] **MCP Registry entry** — official discovery
- [ ] **GitHub Marketplace listing** — enterprise discovery

---

# Distribution Channels (Priority)

1. **MCP Registry** (registry.modelcontextprotocol.io) — free, official
2. **Claude Desktop Extensions** (via DXT) — direct to 100K+ users
3. **GitHub Marketplace** — enterprise buyers search here
4. **Content marketing** — technical blog posts on:
   - "Building Air-Gapped MCP Servers for Regulated Industries"
   - "Why Your AI Agents Need Local Vault Access (Not Cloud RAG)"
   - "MCP Security: Threat Modeling for Enterprise Deployment"
5. **Direct outreach** — UK finance/legal/marine decision makers (your network)
6. **Partner channel** — MSPs serving regulated sectors

---

# Launch Timeline (Next 2 Weeks)

| Week | Focus | Deliverables |
|------|-------|--------------|
| **Week 1** | Foundation | TestPyPI → PyPI publish, DXT verified, MCP Registry submission, GitHub repo public |
| **Week 2** | Sales enablement | Landing page, one-pager, demo video, 3 blog posts drafted, security questionnaire |
| **Week 3** | Outreach | 20 target accounts identified, personalized outreach, 5 discovery calls booked |
| **Week 4** | Close | Proposals sent, first pilot signed |

---

# Team Roles for 90-Day Support Model

| Role | Responsibility | Source |
|------|---------------|--------|
| **Technical Lead** (you/Obi-Wan) | Architecture, custom tools, escalation | Internal |
| **Support Engineer** | Ticket triage, config help, log analysis | Hire/contract (UK-based) |
| **Sales Engineer** | Discovery calls, demos, proposal writing | Hire/contract (UK-based) |
| **Content/Marketing** | Blog, case studies, SEO, LinkedIn | Contract/freelance |
| **DevOps** | Docker/K8s deployments, client infra | Contract |

**First hire priority**: Sales Engineer (technical, can demo, writes proposals). Can be part-time initially.

---

# Immediate Todos (This Week)

- [ ] **Complete TestPyPI upload** (in progress)
- [ ] **Verify DXT installs in Claude Desktop** — test locally
- [ ] **Submit to MCP Registry** — create PR to registry repo
- [ ] **Make GitHub repo public** — add topics, description, badges
- [ ] **Write 3 blog posts** — save to `C:/the force/00_Master/sales-marketing/`
- [ ] **Record 5-min demo video** — Loom or similar
- [ ] **Create one-pager PDF** — from this doc
- [ ] **List 20 target accounts** — UK finance/legal/marine
- [ ] **Draft cold outreach template** — personalized, value-first
- [ ] **Set up Calendly/booking** — for discovery calls