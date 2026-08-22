# Session Handoff — 2026-08-21

> **Status:** Phase 1 Complete → Phase 2 In Progress
> **Active Task:** `t_phase2_publish` (RUNNING) — Package & publish Core 3 MCP servers to PyPI
> **Next Revenue Task:** `t_phase2_sale1` (READY) — Close 1st MCP server sale (£2K + £500/mo)

---

## 🎯 Business Goal
**AFaaS — Agent Fleet as a Service** — £387K Year 1 via 3 streams:
1. **Fleet Deployment** — £250K (4 projects × £25–100K)
2. **MCP Server Products** — £100K (6 servers × £2K + £500/mo)
3. **Local LLM Optimization** — £37K (4 engagements × £15K)

---

## ✅ Phase 1 Complete — Core 3 MCP Servers

| Server | Status | Location | Tests |
|--------|--------|----------|-------|
| **Obsidian Vault MCP** | ✅ Complete, installed | `03_Context/projects/afaaS/obsidian-mcp/` | Manual verified |
| **Filesystem MCP** | ✅ Complete | `03_Context/projects/afaaS/filesystem-mcp/` | 35/37 pass |
| **PostgreSQL MCP** | ✅ Code complete | `03_Context/projects/afaaS/postgresql-mcp/` | Fixtures fixed |

**All three servers built to spec from `mcp-servers.md` with FastMCP, stdio transport, Pydantic schemas.**

---

## 🧹 Vault Cleanup — Coffee Roasting Removed

| File | Action |
|------|--------|
| `projects/coffee-roasting.md` | Deleted |
| `afaaS/README.md` | Risk mitigation updated |
| `afaaS/roadmap.md` | Week 4 & 10–12 de-coffeed |
| `afaaS/clients.md` | Pipeline: Coffee → Tier 1 Financial/Legal |
| `INDEX.md` | Coffee link removed |

**Vault now purely MCP Server Business focused.**

---

## 📋 Phase 2 Task Queue (Kanban + task_master.py)

| Task ID | Title | Status | Assignee |
|---------|-------|--------|----------|
| `t_phase2_publish` | Package & publish Core 3 MCP servers to PyPI | **RUNNING** | master |
| `t_phase2_sale1` | Close 1st MCP server sale (£2K + £500/mo) | READY | master |
| `t_phase2_fleet1` | Deliver 1st Fleet Deployment pilot | READY | master |
| `t_phase2_llm1` | Close 1st Local LLM Optimization (£15K) | READY | master |
| `t_phase2_sops` | Document delivery playbooks (3 SOPs) | READY | master |
| `t_phase2_remote` | Build MCP remote connector (Messages API) | CREATED | master |

---

## 🔬 MoneyPenny Research (2026-08-12) — Key Signals

- **MCP → Linux Foundation (AAIF)** — Community governance, build defensively
- **MCP Remote + Code Execution** — Cuts context 98.7%, critical for deployments
- **EU AI Act LIVE (2 Aug 2026)** — Regulated sectors need compliant local AI
- **UK Pricing Validated** — Discovery £5-15K, Pilot £20-50K, Retainers £350-1.5K/mo
- **177+ Frameworks** — Differentiation: Local-first + MCP-native + Persistent memory

---

## 🖥️ Hardware State
- **32GB RAM** — Only ONE 14B model at a time (qwen2.5-coder:14b / qwen3:14b)
- **Ollama** — Idle (no model loaded)
- **DirectML** — Enabled (AMD 780M iGPU)
- **Single-task enforcement** — Active via `task_master.py`

---

## 📁 Key Files for Next Session

| File | Purpose |
|------|---------|
| `01_Obi-Wan/task_master.py` | Single-task orchestrator (Kanban DB + vault sync) |
| `03_Context/projects/afaaS/roadmap.md` | 12-month phased plan |
| `03_Context/projects/afaaS/mcp-servers.md` | Product specs & build standards |
| `03_Context/market-intel/2026-08-12.md` | MoneyPenny research |
| `03_Context/projects/afaaS/README.md` | Business overview |
| `03_Context/projects/afaaS/clients.md` | Pipeline (now Tier 1 targets) |

---

## 🚀 Resume Commands (Next Session)

```bash
# 1. Check status
cd "C:/the force/01_Obi-Wan" && python task_master.py status

# 2. Continue publish task (currently RUNNING)
#    Work on: obsidian-mcp pyproject.toml publish config
#    Then: filesystem-mcp, postgresql-mcp
#    Then: pip install test → TestPyPI → PyPI

# 3. When publish done:
python task_master.py complete t_phase2_publish true "All 3 MCP servers published to PyPI"
python task_master.py start t_phase2_sale1
```

---

## ⚠️ Constraints to Remember
1. **One task at a time** — `task_master.py` enforces serial execution
2. **One model at a time** — 32GB RAM, no concurrent Ollama workers
3. **Scotty write scope** — `03_Context/projects/afaaS/`, `05_Skills/active/`, `03_Context/systems/`
4. **Mission Control Dashboard** — Abandoned (distraction), do not revive
5. **Vault discipline** — Every decision, reference, learning goes in vault

---

*"The archives are complete. If it's not in the archives, it doesn't exist."*