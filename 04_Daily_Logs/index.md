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

||| Date | Master Dialogue | Sub-Agent Traces | Decisions | Metrics | Vault Health | Notes ||
|------|-----------------|------------------|-----------|---------|--------------|-------|
||| 2026-08-11 | [[2026-08-11/master-dialogue.md]] | [[2026-08-11/subagent-traces.md]] | [[2026-08-11/decisions.md]] | [[2026-08-11/metrics.md]] | — | **Complete archive**. 2 Master sessions (266 msgs), Mission Control Dashboard path bug fixed, Moneypenny + Geppetto RoE added, business intel→spec loop defined #mission-control-bugfix #moneypenny-roe #geppetto-roe #business-loop-defined |
||| 2026-08-10 | [[2026-08-10/master-dialogue.md]] | [[2026-08-10/subagent-traces.md]] | [[2026-08-10/decisions.md]] | [[2026-08-10/metrics.md]] | — | **Complete archive**. 3 Master sessions (826 msgs), Mission Control prompt for Scotty, Moneypenny soul created, MCP viability confirmed, vault dual-folder diagnosed, local tool-calling blocker documented, 4-agent fleet architecture defined #mission-control-prompt #moneypenny-created #mcp-viable #vault-cleanup #local-tool-blocker #fleet-architecture |
|| 2026-08-08 | [[2026-08-08/master-dialogue.md]] | [[2026-08-08/subagent-traces.md]] | [[2026-08-08/decisions.md]] | [[2026-08-08/metrics.md]] | — | **Complete archive** (23:00). 2 Master sessions (667 msgs), K-2SO soul created, Scotty PostgreSQL MCP DSN fix identified, OpenRouter 928/1000 used #k2so-created #scotty-mcp-blocked #openrouter-critical #scotty-fix-prompt-ready |
|| 2026-08-04 | [[2026-08-04/master-dialogue.md]] | [[2026-08-04/subagent-traces.md]] | [[2026-08-04/decisions.md]] | [[2026-08-04/metrics.md]] | [[2026-08-04/vault-health.md]] | AFaaS business model finalized; 12-agent fleet model allocation; dashboard architecture; Scotty MCP critical path; dashboard research delegated (interrupted); K-2SO strategy pivot; vault reindex; git backup |
| 2026-08-03 | [[2026-08-03/master-dialogue.md]] | [[2026-08-03/subagent-traces.md]] | [[2026-08-03/decisions.md]] | [[2026-08-03/metrics.md]] | [[2026-08-03/vault-health.md]] | Fallback model config; GPU DirectML; Anakin pipeline fix verified; full cron suite operational; K-2SO first optimization (rejected); trading loop activated; project health flags |
| 2026-08-02 | [[2026-08-02/master-dialogue.md]] | [[2026-08-02/subagent-traces.md]] | [[2026-08-02/decisions.md]] | [[2026-08-02/metrics.md]] | [[2026-08-02/vault-health.md]] | Initialization; vault setup; 6 sub-agent templates; Anakin soul spec + MCP trading; OpenRouter model filtering explained; conversation recall confirmed |

---

## Tags Index

||| Tag | Dates | Count ||
|-----|-------|-------|
| #mission-control-bugfix | 2026-08-11 | 1 |
| #moneypenny-roe | 2026-08-11 | 1 |
| #geppetto-roe | 2026-08-11 | 1 |
| #business-loop-defined | 2026-08-11 | 1 |
| #mission-control-prompt | 2026-08-10 | 1 |
| #moneypenny-created | 2026-08-10 | 1 |
| #mcp-viable | 2026-08-10 | 1 |
| #vault-cleanup | 2026-08-10 | 1 |
| #local-tool-blocker | 2026-08-10 | 1 |
| #fleet-architecture | 2026-08-10 | 1 |
| #k2so-created | 2026-08-08 | 1 |
| #scotty-mcp-blocked | 2026-08-08 | 1 |
| #openrouter-critical | 2026-08-08 | 1 |
| #scotty-fix-prompt-ready | 2026-08-08 | 1 |
| #early-archive | 2026-08-08 | 1 |
| #partial-day | 2026-08-08 | 1 |
| #afaaS-business-model | 2026-08-04 | 1 |
| #12-agent-fleet | 2026-08-04 | 1 |
| #model-allocation | 2026-08-04 | 1 |
| #dashboard-architecture | 2026-08-04 | 1 |
| #scotty-mcp-critical-path | 2026-08-04 | 1 |
| #dashboard-research | 2026-08-04 | 1 |
| #k2so-strategy-pivot | 2026-08-04 | 1 |
| #vault-reindex | 2026-08-04 | 1 |
| #git-backup | 2026-08-04 | 1 |
| #fallback-model | 2026-08-03 | 1 |
| #gpu-directml | 2026-08-03 | 1 |
| #anakin-pipeline-fix | 2026-08-03 | 1 |
| #cron-suite-operational | 2026-08-03 | 1 |
| #k2so-optimization | 2026-08-03 | 1 |
| #trading-loop-activated | 2026-08-03 | 1 |
| #project-health-flags | 2026-08-03 | 1 |
| #initialization | 2026-08-02 | 1 |
| #vault-setup | 2026-08-02 | 1 |
| #obi-wan-design | 2026-08-02 | 1 |
| #cron-archive | 2026-08-02 | 1 |
| #sub-agent-architecture | 2026-08-02 | 1 |
| #anakin-soul | 2026-08-02 | 1 |
| #mcp-trading | 2026-08-02 | 1 |
| #openrouter-filtering | 2026-08-02 | 1 |
| #conversation-recall | 2026-08-02 | 1 |

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