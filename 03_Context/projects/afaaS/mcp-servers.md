# AFaaS — MCP Server Product Roadmap

> Reusable Model Context Protocol servers. Each: `pip install`, config, works in Claude/Cursor/VS Code.

---

## Product Strategy
- **Core 3** (Months 1–2): Vault, Filesystem, PostgreSQL — universal needs
- **Suite v1** (Month 5): 5 servers — bundle pricing
- **Vertical packs** (Month 6+): Finance, Legal, Healthcare, DevOps
- **Recurring revenue**: £500/mo support per server (updates, hardening, priority support)

---

## Core 3 — Build Order

### 1. Obsidian Vault MCP Server — **Week 1–2**
| Tool | Description |
|------|-------------|
| `read_note(path)` | Read markdown note with frontmatter |
| `write_note(path, content, frontmatter?)` | Create/update note |
| `search_vault(query, tags?, folder?)` | Full-text + tag/folder filter |
| `list_tags()` | All tags with counts |
| `get_graph(note?, depth?)` | Wikilink graph for context |
| `list_files(folder?)` | Directory listing |

**Tech**: Python, `obsidian-client` or direct file I/O, FastMCP stdio transport
**Dogfood**: Your fleet uses it daily → live demo
**Price**: £2K setup + £500/mo support

---

### 2. Local Filesystem MCP Server — **Week 3–4**
| Tool | Description |
|------|-------------|
| `read_file(path)` | Safe read with size limit |
| `write_file(path, content)` | Atomic write |
| `list_dir(path, glob?)` | Directory listing with glob |
| `search_files(pattern, path?)` | Ripgrep-backed content search |
| `glob(pattern, path?)` | File pattern matching |
| `patch_file(path, old_str, new_str)` | Targeted edit |

**Tech**: Python, `pathlib`, `ripgrep` via `rg` binary, sandboxed root directory
**Security**: Configurable root, symlink protection, size limits
**Price**: £1.5K setup + £300/mo support

---

### 3. PostgreSQL MCP Server — **Week 5–6**
| Tool | Description |
|------|-------------|
| `query(sql, params?)` | Parameterized SELECT |
| `execute(sql, params?)` | INSERT/UPDATE/DELETE |
| `list_tables(schema?)` | Schema introspection |
| `describe_table(table, schema?)` | Columns, types, indexes |
| `run_migration(sql)` | Versioned schema changes |
| `explain_analyze(sql)` | Query plan |

**Tech**: Python, `asyncpg`, connection pooling, read-only mode option
**Security**: Parameterized only, role-based access, audit log
**Price**: £2.5K setup + £500/mo support

---

## Suite v1 — Month 5 Target (5 Servers Total)

| Server | Priority | Est. Build | Target Vertical |
|--------|----------|------------|-----------------|
| **Git MCP** | High | 1 week | All dev teams |
| **Jira/Linear MCP** | High | 1.5 weeks | Product/Eng |
| **Slack/Teams MCP** | Medium | 1 week | Ops/Support |
| **Notion MCP** | Medium | 1 week | Knowledge workers |
| **Email (IMAP/SMTP) MCP** | Medium | 1 week | Sales/Support |

**Bundle Pricing**: £8K setup + £1.5K/mo for all 5 (vs £10.5K + £2.1K individual)

---

## Vertical Packs — Month 6+

### Finance Pack
- **Alpha Vantage MCP** — Market data, fundamentals
- **FRED MCP** — Macro series (UNRATE, PAYEMS, CPI, etc.)
- **Bloomberg/Refinitiv MCP** — If client has license
- **XBRL/SEC MCP** — Filings parsing

### Legal Pack
- **Case Law MCP** — BAILII, CourtListener APIs
- **Legislation MCP** — legislation.gov.uk, EU law
- **Contract Analysis MCP** — Clause extraction, risk scoring

### Healthcare Pack
- **NHS Data MCP** — Open data APIs
- **SNOMED/ICD MCP** — Terminology lookup
- **FHIR MCP** — Healthcare interoperability

### DevOps Pack
- **Kubernetes MCP** — Cluster ops, manifests
- **AWS/Azure/GCP MCP** — Cloud resource mgmt
- **Terraform MCP** — Plan/apply, state inspection
- **Prometheus/Grafana MCP** — Metrics, dashboards

---

## Technical Standards (All Servers)

|| Requirement | Standard ||
||-------------|----------||
|| **Transport** | stdio (primary), SSE (optional) ||
|| **Auth** | None (local) → API key (remote) ||
|| **Config** | JSON file + env vars, schema validated ||
|| **Logging** | Structured JSON to stderr ||
|| **Testing** | Unit + integration (MCP inspector) ||
|| **Packaging** | `pyproject.toml`, `pip install`, GitHub Actions CI ||
|| **Docs** | README, tool schemas, examples, troubleshooting ||
|| **Versioning** | SemVer, changelog, backward compat ||

### Phase 2b Hardening (Post-First-Sale)

|| Requirement | Standard ||
||-------------|----------||
|| **Backup/Restore** | Automated vault + DB snapshots, monthly tested restore ||
|| **UPS/Graceful Shutdown** | NUT/apcupsd integration, state persistence on power loss ||
|| **Health Monitoring** | MCP server heartbeats, Prometheus/Grafana or lightweight alerting ||
|| **Disaster Recovery** | Documented DR runbook, < 4hr RTO, < 1hr RPO drill quarterly ||

---

## Build Sprint Template (Per Server)

| Day | Task |
|-----|------|
| 1 | Spec tools, schemas, error codes |
| 2 | Core implementation + unit tests |
| 3 | MCP inspector testing, edge cases |
| 4 | Packaging, CI, README, examples |
| 5 | Dogfood: install in Claude/Cursor, demo |

---

## Revenue Projection (MCP Only)

| Month | Servers Live | Subscribers | MRR | ARR |
|-------|--------------|-------------|-----|-----|
| 2 | 1 (Obsidian) | 1 pilot | £500 | £6K |
| 3 | 2 | 2 | £1,100 | £13K |
| 4 | 3 | 3 | £1,800 | £22K |
| 5 | 5 (Suite v1) | 5 | £3,500 | £42K |
| 6 | 5 + 1 vertical | 8 | £5,000 | £60K |
| 12 | 12+ | 20 | £12K | **£144K** |

---

## Links
- [[README.md]] — Business overview
- [[roadmap.md]] — Phase gates
- [[clients.md]] — Who buys these
- `../../../05_Skills/templates/` — Skill templates for builders