# Local Model Tool-Calling Fix — Vault Reference

**Date:** 2026-08-09
**Context:** OpenRouter 1000/day limit approaching; switching Scotty/K-2SO/Obi-Wan to local Ollama (qwen2.5-coder:14b)

---

## Problem

Ollama's `/v1/chat/completions` returns tool calls as **JSON string in `content` field** (non-standard), not in `tool_calls` array (OpenAI standard). Hermes' `ollama` provider only checks `tool_calls`, so it misses them and treats response as plain text.

**Affected:** Any local model via Ollama (qwen2.5-coder:14b, qwen3, llama3.1, etc.)

**GitHub Issues:** #5867, #25629, #2074, #56360

---

## Primary Fix: Change Provider to `custom`

**Config change (both Scotty & K-2SO profiles):**

```yaml
# BEFORE (ollama provider - broken tool calls)
model:
  provider: ollama
  base_url: http://localhost:11434/v1
  name: qwen2.5-coder:14b

# AFTER (custom provider - works)
model:
  provider: custom
  base_url: http://localhost:11434/v1
  name: qwen2.5-coder:14b
  temperature: 0.1
  max_tokens: 8192
  ollama_num_ctx: 65536
```

**Why it works:** `custom` provider uses OpenAI-compatible parsing which has fallback logic to detect JSON tool calls in `content` field.

**Source:** GitHub #5867 comment by ShaneOss: *"I found if you change the provider from ollama to custom, everything works again. Tool calls are now being executed."*

---

## Profile Config Locations

| Profile | Config Path |
|---------|-------------|
| Scotty | `C:\Users\brook\AppData\Local\hermes\profiles\scotty\config.yaml` |
| K-2SO | `C:\Users\brook\AppData\Local\hermes\profiles\k-2so\config.yaml` |
| Obi-Wan | `C:\Users\brook\AppData\Local\hermes\profiles\obi-wan\config.yaml` |

**Apply to all three when switching to local.**

---

## Alternative Fixes (If `custom` Provider Fails)

### 1. LiteLLM Proxy (Recommended Fallback)

Fixes Ollama streaming + tools bug (issue #25629).

```bash
# Install
pip install litellm

# Run proxy with stream=false (critical)
litellm --model ollama/qwen2.5-coder:14b \
        --api_base http://localhost:11434/v1 \
        --stream false \
        --port 4000
```

**Config:**
```yaml
model:
  provider: custom
  base_url: http://localhost:4000
  name: qwen2.5-coder:14b
```

### 2. Ollama Native Tool Calling (If Model Supports)

Some newer Ollama models (qwen3, llama3.1 with tool calling patches) work with `provider: ollama`. Test per model.

### 3. Patch Hermes Source (Last Resort)

Add content-field parsing to `ollama` provider in Hermes source. See PRs #26353, #35129 (closed but reference implementations exist).

---

## Hardware Constraints (Critical)

| Resource | Limit |
|----------|-------|
| RAM | 32GB total / ~27.8GB usable |
| VRAM | None (AMD Radeon 780M iGPU, shared system RAM) |
| Model Max | ~14B params (Q4_K_M ≈ 9GB) |
| Concurrency | **1 model at a time** — sequential only |

**Orchestration:** Kanban dispatcher queues tasks; Obi-Wan spawns Scotty → waits → reviews → spawns K-2SO → waits → reviews.

---

## Obi-Wan Local Config (When Ready)

```yaml
# C:\Users\brook\AppData\Local\hermes\profiles\obi-wan\config.yaml
model:
  provider: custom
  base_url: http://localhost:11434/v1
  name: qwen3:14b  # Different model for orchestrator
  temperature: 0.1
  max_tokens: 8192
  ollama_num_ctx: 65536
```

**Model choice:** qwen3:14b for Obi-Wan (better reasoning), qwen2.5-coder:14b for Scotty/K-2SO (coding optimized).

---

## Test Sequence (Run After Config Change)

```bash
# 1. Restart gateway
hermes gateway restart

# 2. Basic connectivity
curl -s http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5-coder:14b","messages":[{"role":"user","content":"Say hello"}],"stream":false}'

# 3. Test tool calling via Hermes
hermes --profile k-2so
# In chat: "Create a React Button component at C:\the force\03_Context\projects\afaaS\frontend\test\Button.tsx"

# 4. Verify: Actual tool calls (write_file, patch) appear in conversation
#    NOT JSON text in message content
```

---

## Rollback Plan

If local models fail completely:

```yaml
# Revert to OpenRouter (Scotty/K-2SO)
model:
  provider: openrouter
  default: cohere/north-mini-code:free
```

Obi-Wan stays on OpenRouter (Nemotron 3 Ultra) until local orchestration validated.

---

## Key Files to Update

| File | Purpose |
|------|---------|
| `C:\Users\brook\AppData\Local\hermes\profiles\scotty\config.yaml` | Scotty backend |
| `C:\Users\brook\AppData\Local\hermes\profiles\k-2so\config.yaml` | K-2SO frontend |
| `C:\Users\brook\AppData\Local\hermes\profiles\obi-wan\config.yaml` | Obi-Wan orchestrator |
| `C:\the force\03_Context\projects\afaaS\coder-backend-soul.md` | Scotty soul (model config §12) |
| `C:\the force\03_Context\projects\afaaS\frontend\k2so-soul.md` | K-2SO soul (model config §12) |

---

## Status Tracker

| Profile | Current Provider | Target Provider | Tested |
|---------|------------------|-----------------|--------|
| Scotty | openrouter | custom (local) | ⏳ After fixes |
| K-2SO | openrouter → custom | custom (local) | ⏳ After gateway restart |
| Obi-Wan | openrouter (Nemotron) | custom (qwen3:14b) | ⏳ Later |

---

**Next Action:** Scotty finishes Dashboard MCP fixes → gateway restart → K-2SO test → if passes, deliver K-2SO frontend prompt.