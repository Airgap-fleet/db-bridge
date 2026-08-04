# Metrics — 2026-08-04

> *Token usage, duration, success/failure rates for all sessions and cron jobs*

---

## Session Summary

| Session ID | Source | Duration | Messages | Model | Status |
|------------|--------|----------|----------|-------|--------|
| `20260804_105628_093df3` | desktop | ~8 hours | 491 | nemotron-3-ultra-550b-a55b:free | ✅ Complete |
| `cron_6faae29dc4d1_20260804_020014` | cron | ~2 min | 12 | nemotron-3-ultra-550b-a55b:free | ✅ Complete |
| `cron_da054091c9c3_20260804_020205` | cron | ~5 min | 45 | nemotron-3-ultra-550b-a55b:free | ✅ Complete |
| `cron_bd77759049fe_20260804_030015` | cron | ~8 min | 78 | nemotron-3-ultra-550b-a55b:free | ✅ Complete |

---

## Token Usage (Estimated)

> **Note:** Exact token counts not logged by provider. Estimates based on message counts and model.

| Session | Input Tokens (est.) | Output Tokens (est.) | Total (est.) | Cost (OpenRouter free) |
|---------|---------------------|----------------------|--------------|------------------------|
| Main (desktop) | ~180,000 | ~45,000 | ~225,000 | $0.00 (free tier) |
| Backup cron | ~8,000 | ~2,000 | ~10,000 | $0.00 |
| K-2SO cron | ~25,000 | ~8,000 | ~33,000 | $0.00 |
| Reindex cron | ~30,000 | ~10,000 | ~40,000 | $0.00 |
| **TOTAL** | **~243,000** | **~65,000** | **~308,000** | **$0.00** |

---

## Delegation Metrics

| Delegation ID | Task | Duration | API Calls | Status | Outcome |
|---------------|------|----------|-----------|--------|---------|
| `deleg_fb1af0cc` | Dashboard research | 201.98s | 35 | ✗ **Interrupted** | Partial findings, no output files |

---

## Cron Job Metrics

| Job | Schedule | Duration | Exit Code | Files Changed | Git Commit |
|-----|----------|----------|-----------|---------------|------------|
| **Backup Vault** | 02:00 | ~2 min | 0 | 4 (3 mod, 1 new) | `4d86b31` |
| **K-2SO Optimization** | 02:00 | ~5 min | 0 | 4 (traces, params, CSV, pkl) | N/A (no vault commit) |
| **Vault Reindex** | 03:00 | ~8 min | 0 | 1 (`search-index.json`) | `7eae95a` |

---

## Success/Failure Rates

| Category | Total | Success | Failure | Interrupted | Success Rate |
|----------|-------|---------|---------|-------------|--------------|
| **Cron Jobs** | 3 | 3 | 0 | 0 | **100%** |
| **Delegations** | 1 | 0 | 0 | 1 | **0%** (interrupted) |
| **Main Session** | 1 | 1 | 0 | 0 | **100%** |
| **Tool Calls (main)** | ~120 | ~118 | ~2 | 0 | **~98%** |

### Notable Failures
1. **Browser searches** — GitHub rate limited (3), Google captcha (1)
2. **Delegation interrupted** — Model response timeout at 202s

---

## Latency Metrics

| Operation | Avg Latency | P95 | Notes |
|-----------|-------------|-----|-------|
| `read_file` (vault) | ~150ms | ~400ms | Local NVMe |
| `write_file` (vault) | ~200ms | ~500ms | Local NVMe |
| `search_files` (vault) | ~300ms | ~800ms | ripgrep |
| `terminal` (bash) | ~500ms | ~2s | Git Bash |
| `browser_navigate` | ~2.5s | ~5s | Network dependent |
| `skill_view` | ~300ms | ~1s | In-memory |
| `session_search` | ~800ms | ~2s | SQLite FTS5 |

---

## Resource Usage

| Resource | Peak | Average | Notes |
|----------|------|---------|-------|
| **RAM (Hermes)** | ~2.1 GB | ~1.5 GB | Profile: obi-wan |
| **RAM (Ollama)** | 0 GB | 0 GB | No local models loaded |
| **GPU (780M)** | 0% | 0% | OLLAMA_DML=1 set, service restart needed |
| **Disk (vault)** | +544 lines | — | 4 files changed in backup |
| **Disk (state.db)** | 16.5 MB | — | WAL mode active |

---

## Business Metrics (AFaaS)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Revenue Streams Defined** | 3 | 3 | ✅ |
| **Year 1 Target** | £387K | £387K | 📋 Planned |
| **Agent Fleet Designed** | 12 | 12 | ✅ |
| **MCP Servers** | 1/3 (Obsidian) | 3 | 🔄 Filesystem in progress |
| **Warm B2B Leads** | 2 | 5 | 🔄 Coffee clients |
| **Profiles Created** | 2/7 (obi-wan, scotty) | 7 | 🔄 5 pending |

---

## Quality Indicators

| Indicator | Value | Threshold | Pass? |
|-----------|-------|-----------|-------|
| **Vault Git Clean** | Yes | Clean | ✅ |
| **Daily Archive Complete** | Yes | 4+ log files | ✅ |
| **Cron Suite Operational** | 3/3 | 3/3 | ✅ |
| **K-2SO Trace Written** | Yes | Required | ✅ |
| **Search Index Fresh** | 03:00 today | <24h | ✅ |
| **Delegation Transcripts Saved** | 1/1 | 100% | ✅ |

---

## Action Items from Metrics

1. **Re-dispatch dashboard research** — 0% delegation success this session
2. **Pull deepseek-coder:6.7b** — Scotty model switch pending
3. **Configure git remote** — Off-site backup missing
4. **Install embedding model** — `ollama pull nomic-embed-text` for semantic search
5. **Restart Ollama service** — Enable DirectML GPU acceleration

---

*Metrics compiled from session DB, cron logs, and delegation transcripts.*