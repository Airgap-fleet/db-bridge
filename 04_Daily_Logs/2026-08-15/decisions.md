# Decisions & Rationale — 2026-08-15

## Decision: Local Model Tool-Calling Status Unchanged
**Time:** 11:13:20 AM  
**Context:** Master asked for fact-check on "latest update sorted local model tool call issues"

### Finding
Hermes v0.20.1 (2026-08-13) **did not fix** any of the four known local model tool-calling issues:
- #5867: Tool calls in `content` field (JSON string) → **Open**
- #25629: `stream=true` + tools deadlock → **Open**  
- #2074: Local models don't recognize Hermes environment → **Closed (no fix)**
- #8965: Raw XML tool calls (new Aug 2026) → **Open**

### Rationale
- 656 PRs in v0.20.1 focused on desktop app stability, voice streaming, plugin system, gateway fixes
- No PRs addressed Ollama's non-standard tool-call format or streaming deadlock
- Skills `hermes-local-model-tool-calling` and `hermes-local-model-workarounds` remain current and accurate

### Trade-off
- **Workaround required:** `provider: custom` + LiteLLM proxy (`stream: false`)
- **Cost:** Extra infrastructure (LiteLLM) vs. native Ollama simplicity
- **Benefit:** Reliable tool execution on qwen2.5-coder:14b (AMD 780M / 32GB)

### Linked
- [[Lesson: Local Model Workarounds]]
- [[Project: AFaaS Local-First Architecture]]

---

## Decision: Manual Cron Trigger for Missed Archive
**Time:** 11:15:38 AM  
**Context:** Master reported "ran out of requests to achieve the cron jobs last night"

### Action
Triggered Daily Conversation Archive job (`ed5aef05611a`) manually via `cronjob run`

### Rationale
- Scheduled 23:00 run missed due to rate limits
- Manual trigger ensures vault continuity
- Job runs in background (non-blocking)

### Linked
- [[System: Cron Job Reliability]]
- [[Master's Preferences: Proactive Archiving]]

---

## Decision: Web Search Backend Limitation
**Time:** 11:12:52–11:13:04 AM  
**Context:** Multiple `web_extract` calls failed

### Finding
DuckDuckGo (ddgs) backend is search-only — cannot extract page content

### Workaround
- Use `web_search` for discovery only
- For extraction: configure `firecrawl`, `tavily`, `exa`, or `parallel` backend
- GitHub release/issue pages not directly extractable via current config

### Linked
- [[Lesson: Web Extraction Backend Config]]