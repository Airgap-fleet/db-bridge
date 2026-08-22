# MCP Server Commercial Readiness — Research & Roadmap

**Date:** 2026-08-22
**Source:** Web research + codebase analysis + build verification
**Status:** Build/Install phase complete → Hardening sprint next

---

## Executive Summary

Three MCP servers (Obsidian, Filesystem, PostgreSQL) build and install cleanly via `pip install`. **They are demos, not products.** Commercial readiness at £2K + £500/mo requires hardening across security, observability, testing, and enterprise packaging.

**Target:** £100K Year 1 from MCP Server Products (3 streams × £33K each)

---

## Current State (Verified 2026-08-22)

| Server | Build | Install | Runs (stdio) | Tests | CI | Structured Logging | Config Schema |
|--------|-------|---------|--------------|-------|-----|-------------------|---------------|
| `obsidian-mcp` | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ (print) | ✅ (pydantic-settings) |
| `filesystem-mcp` | ✅ | ✅ | ✅* | 35/37 | ✅ (untested) | ❌ (print) | ❌ (hardcoded paths) |
| `postgresql-mcp` | ✅ | ✅ | ⚠️ needs DB | ✅ | ✅ | ✅ (structlog) | ✅ (pydantic-settings) |

*Fixed entry point: added `main()` wrapper in `__init__.py`

---

## Commercial Readiness Checklist (2026 Best Practices)

### 1. Distribution & Packaging
- [x] PyPI `pip install` — **done for all 3**
- [ ] **DXT bundle** — Claude Desktop one-click install
- [ ] **Docker image** — PostgreSQL has Dockerfile; others need
- [ ] **npm/npx wrapper** — for JS/TS clients
- [ ] **Official MCP Registry** listing — discoverability

### 2. Security Hardening (Critical for Enterprise)
| Requirement | Obsidian | Filesystem | PostgreSQL |
|---|---|---|---|
| **Auth**: OAuth 2.1 / API keys for remote | ❌ | ❌ | ❌ |
| **Transport**: TLS 1.3 for SSE/HTTP | ❌ | ❌ | ❌ |
| **Input validation**: Parameterized only | ✅ (regex) | ❌ (raw paths) | ✅ ($1, $2) |
| **Sandboxing**: Path restrictions | ✅ vault root | ❌ **full FS access** | ✅ read-only mode |
| **Audit logging**: Structured JSON | ❌ | ❌ | ✅ structlog |
| **Secrets management**: No hardcoded creds | ✅ env vars | ✅ env vars | ✅ env vars |

### 3. Observability & Operations
- [ ] **Health endpoint** (`/health`, `/ready`) — for K8s/load balancers
- [ ] **Metrics** (Prometheus) — latency, error rates, tool calls
- [ ] **Distributed tracing** (OpenTelemetry) — deps already present
- [ ] **Structured logging** — PostgreSQL ✅, others need structlog

### 4. Enterprise Features Buyers Expect
| Feature | Why It Matters | Effort |
|---|---|---|
| **Multi-tenant config** | Isolate client vaults/DBs | 2 days |
| **RBAC / Scoped permissions** | Read-only vs admin per agent | 2 days |
| **Rate limiting / quotas** | Prevent abuse, cost control | 1 day |
| **SLA / Support tiers** | Justify £500/mo | 1 day (docs) |
| **Version pinning / SemVer** | Enterprise change management | Done |

### 5. Testing & Quality Gates
- [ ] **Unit tests** ≥80% coverage — all three
- [ ] **Integration tests** with MCP Inspector — all three
- [ ] **Contract tests** — tool schemas don't break
- [ ] **Security scans** (bandit, pip-audit) — CI gate
- [ ] **Load testing** — concurrent tool calls

### 6. Documentation & Sales Enablement
- [x] README with install/config/examples — all three
- [ ] **Architecture diagram** — data flow, security boundaries
- [ ] **Threat model** — STRIDE analysis for security review
- [ ] **Runbook** — ops procedures, incident response
- [ ] **Migration guide** — v0.x → 1.0.0 breaking changes

---

## Hardening Sprint Plan (Track B — Next 2 Weeks)

### Phase 1: Obsidian MCP (Flagship — 2 days)
1. **Unit tests** — target ≥80% on `core.py` (13K), `models.py` (11K)
2. **CI workflow** — `.github/workflows/ci.yml` (test + lint + bandit + pip-audit)
3. **Structured logging** — replace `print()` with `structlog` (mirror PostgreSQL pattern)
4. **Changelog + bump to 1.0.0** — SemVer, breaking changes documented

### Phase 2: Filesystem MCP (1.5 days)
1. **Config schema** — pydantic-settings for root paths (replace hardcoded)
2. **Missing tools** — implement `fs_search` + `fs_patch` (per mcp-servers.md spec)
3. **Structured logging** — structlog
4. **Fix CI** — run and verify existing workflow

### Phase 3: All Three — Auth & Transport (2-3 days)
1. **Remote auth** — API key middleware (FastMCP supports this)
2. **SSE transport** — HTTP+SSE endpoint alongside stdio
3. **Health endpoints** — `/health`, `/ready`

### Phase 4: Packaging & Publish (1 day)
1. **TestPyPI** — verify full pipeline
2. **PyPI** — production publish
3. **DXT bundles** — desktop installers
4. **Docker images** — GHCR/Docker Hub

---

## Key Research Insights

> **"Building a demo takes a weekend while building a production-grade server takes months and costs $50K-$150K/year to maintain."** — *InstitutePM 2026*

> **Enterprise buyers require:** OAuth 2.1, audit logs, sandboxing, SLA, threat model, runbook.

> **MCP Registry + DXT + Docker** = distribution trifecta for 2026.

---

## Immediate Next Actions

1. **Create hardening tasks in `task_master.py`** — serial, one at a time
2. **Start Obsidian MCP tests + CI** — highest ROI (your daily driver, most differentiated)
3. **TestPyPI publish** — verify pipeline before real PyPI

---

## Files & References

- `mcp-servers.md` — business spec, sellable requirements §105-117
- `task_master.py` — task management CLI (enforces serial execution)
- Source: `C:/the force/03_Context/projects/afaaS/{obsidian,filesystem,postgresql}-mcp/`

---

## Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-08-22 | Prioritize Obsidian MCP hardening first | Flagship product, daily driver, most differentiated |
| 2026-08-22 | Serial hardening via task_master.py | One 14B model at a time (32GB RAM), serial execution enforced |
| 2026-08-22 | Target 1.0.0 for first sale | SemVer signals production readiness to enterprise buyers |