# Decisions — August 20, 2026

## Strategic Direction

1. **Obi-Wan = Human CEO** — final decisions on fleet architecture, budget approval, strategic pivots
2. **Rupert = AI Manager** — executes day-to-day team management, reports to Obi-Wan
3. **Sequential Execution Required** — hardware constraint (32GB RAM) limits to ONE 14B model active at a time

## Key Rationale

- Cron job archived manually due to Ollama model misconfiguration (`qwen3:14b` → `qwen3.5:9b`)
- Direct file-based archiving faster than subagent delegation when model routing misconfigured
- Legacy Mission Control needs server.py restoration before next sprint

---

## Delegation Protocol

When cronjobs fail due to model path mismatches, prefer direct tool calls:
```bash
# Instead of delegating archive task
cronjob(action='run', job_id=...)  ← fails with HTTP 404
↓
Direct file operations using vault tools (obsidian skill)
→ write_file master-dialogue.md ✅
→ read_file session transcripts in memory → process directly
```

## Approval Gates

- **Hardware constraint accepted** — sequential execution reduces context overhead
- **Manual cron runs acceptable** until Ollama model path resolved or OpenRouter default set
- **Legacy dashboard server.py fix** prioritized for next morning
