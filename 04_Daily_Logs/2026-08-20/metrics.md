# Metrics — August 20, 2026

## Token Usage & Performance

| Metric | Value | Notes |
|--------|-------|-------|
| Total API calls today | 13 | Direct tool calls + cron job attempt |
| Subagent delegation failures | 2 | Model routing to non-existent `qwen3:14b` |
| Successful direct operations | 9 | File writes, session retrieval, vault management |
| Avg latency (direct vs subagent) | N/A | Direct ops faster when model misconfigured |

## Fleet Status

- **Obi-Wan (qwen3.5:9b)** - Active primary
- **Scotty/qwen2.5-coder:14b** - Overloaded by delegation volume, monitor closely
- **Hardware constraint** - Sequential execution, no parallel 14B models

## Session Throughput

| Time | Sessions Processed | Duration | Status |
|------|-------------------|----------|--------|
| 2026-08-20 21:49 | 1 (Rupert team) | ~1hr | ✅ Completed |
| 2026-08-20 09:17 AM | 1 (Legacy dashboard) | ~3hrs | ✅ Runnable |
| 2026-08-20 Manual Cron | Direct ops | <5min | ✅ Complete |

## Error Rates

- Subagent delegation failures: 2/13 = 15%
- Cause: Model path hardcoded to non-existent Ollama model
- Resolution: Direct file operations bypass model routing
