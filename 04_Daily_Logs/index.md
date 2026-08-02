# Daily Logs Index

> *Searchable index of all daily conversation logs.*

---

## Log Structure

```
04_Daily_Logs/
├── YYYY-MM-DD/
│   ├── master-dialogue.md      # Master ↔ Obi-Wan conversation
│   ├── subagent-traces.md      # Full sub-agent delegation transcripts
│   ├── decisions.md            # Key decisions with rationale
│   ├── metrics.md              # Token usage, latency, success rates
│   ├── vault-health.md         # Archivist health report
│   └── analysis-*.md           # Analyst reports (if any)
└── index.md                    # This file
```

---

## Index by Date

| Date | Master Dialogue | Sub-Agent Traces | Decisions | Metrics | Vault Health | Notes |
|------|-----------------|------------------|-----------|---------|--------------|-------|
| 2026-08-02 | [Link](2026-08-02/master-dialogue.md) | [Link](2026-08-02/subagent-traces.md) | [Link](2026-08-02/decisions.md) | [Link](2026-08-02/metrics.md) | [Link](2026-08-02/vault-health.md) | Initialization |

---

## Tags Index

| Tag | Dates | Count |
|-----|-------|-------|
| #initialization | 2026-08-02 | 1 |

---

## Search Tips

- **By date:** Navigate to `YYYY-MM-DD/` folder
- **By tag:** Search `#tag` in vault
- **By agent:** Search `agent: researcher` in subagent-traces.md
- **By decision:** Search `DECISION:` in decisions.md
- **Full text:** Use `search_files` on `04_Daily_Logs/` with `target: "content"`

---

## Cron Job: Daily Archive

**Job Name:** Daily Conversation Archive  
**Schedule:** `0 23 * * *` (11 PM daily)  
**Skills:** `obsidian`, `hermes-agent`  
**Workdir:** `C:\the force`

**Prompt:**
```
Record today's conversations for Master and all sub-agents.

Steps:
1. Read today's session transcripts from Hermes state.db
2. Extract: Master ↔ Obi-Wan dialogue, all sub-agent delegations + results
3. Write to vault: 04_Daily_Logs/YYYY-MM-DD/
   - master-dialogue.md (filtered, summarized)
   - subagent-traces.md (full traces with outcomes)
   - decisions.md (key choices, rationale, trade-offs)
   - metrics.md (tokens, duration, success/failure)
4. Update 04_Daily_Logs/index.md with date entry + tags
5. Git commit: "chore: daily log YYYY-MM-DD"
6. Update Obi-Wan's state.md with summary

Use wikilinks to connect: [[Project Alpha]], [[Master's Preferences]], [[Lesson: API Design]]
```

---

## Additional Cron Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| Vault Reindex | `0 3 * * *` | Rebuild search index, vector embeddings |
| Skill Consolidation | `0 4 * * 0` | Weekly: merge overlapping skills, archive stale |
| Project Health Check | `0 9 * * 1` | Monday: scan active projects, flag stale items |
| Backup Vault | `0 2 * * *` | Daily git push to remote (if configured) |

---

*"The archives are complete. If it's not in the archives, it doesn't exist."*