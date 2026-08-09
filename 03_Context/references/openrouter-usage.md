# OpenRouter Usage Tracking
> **Daily limit:** 1000 requests/day (SHARED across all profiles)
> **Current usage (2026-08-07):** 564 requests
> **Remaining:** 436 requests

## Tracking Format

| Date | Total Used | Remaining | Notes |
|------|------------|-----------|-------|
| 2026-08-07 | 564 | 436 | Filesystem MCP ✅, PostgreSQL MCP ✅, Dashboard MCP spec ready |

## Issue Tracking

**Hermes GitHub Issues (Weekly Check Cron: a1e585821d49)**
1. #25629 - Hermes + Ollama hangs with tool definitions
2. #63477 - Desktop: terminal tool output not returned to model
3. #43900 - Ollama silently capped at 4096-token context
4. #2074 - Ollama models don't recognize hermes-agent environment
5. #879 - Local model routing for auxiliary tasks

## Local Model Migration Trigger

When any of the above issues are **closed/fixed** → re-evaluate Scotty (and fleet) migration back to local models (deepseek-coder:6.7b, qwen2.5-coder:14b).