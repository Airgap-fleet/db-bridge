# Key Decisions — 2026-08-02

> *Decisions made during session `20260802_151202_27bb8f` with rationale and trade-offs*

---

## DECISION: Vault Path = `C:\the force`

**Status:** ✅ Approved
**Context:** Master specified this path in initial request.
**Rationale:**
- Short, memorable, no spaces (avoids shell quoting issues)
- Root-level for easy access from any tool
- Matches "The Force" Star Wars theme (Obi-Wan)

**Trade-offs:**
- Non-standard location (not in `~/Documents/Obsidian Vault`)
- Requires explicit path resolution in all tools (done via skill)

**Alternatives considered:** Default `~/Documents/Obsidian Vault` — rejected per Master directive.

---

## DECISION: 6 Sub-Agent Specializations (Fixed Set)

**Status:** ✅ Approved
**Context:** Derived from research on multi-agent patterns + practical decomposition.
**Rationale:**
- Covers full software lifecycle: research → backend → frontend → devops → analysis → maintenance
- Maps cleanly to `delegate_task` leaf roles
- Each has distinct tool/vault scope to minimize conflicts

**Trade-offs:**
- Fixed set vs. dynamic specialization creation
- May need `designer`, `security`, `data-engineer` later
- Current set assumes software-heavy workload

**Alternatives considered:**
- Single generalist agent with skill switching — rejected (context pollution, skill limits)
- Unlimited dynamic agents — rejected (orchestration complexity, token cost)

---

## DECISION: Daily Cron Archive at 23:00 (11 PM)

**Status:** ✅ Configured
**Context:** Master requested "cron job at end of day."
**Rationale:**
- Captures full day's conversations before midnight rollover
- Runs after typical work hours, before maintenance window
- Output feeds directly into `04_Daily_Logs/YYYY-MM-DD/`

**Trade-offs:**
- If Master works past 23:00, late conversations captured next day
- Timezone: assumes BST/UTC+1 (Master's local)

**Alternatives considered:** 00:00 (midnight) — rejected (date boundary ambiguity).

---

## DECISION: Git Commit on Every Archive

**Status:** ✅ Implemented
**Context:** Vault initialized as git repo at `775eefd`.
**Rationale:**
- Immutable history of all daily logs
- Enables vault backup/restore
- Supports future remote sync

**Trade-offs:**
- Many small commits (one per day)
- No remote configured yet (local only)

**Alternatives considered:** Weekly squash commit — rejected (loses daily granularity).

---

## DECISION: Short Answers Preferred (Tone Update)

**Status:** ✅ Applied (Msg 93–96)
**Context:** Master explicitly requested "short answers" preference.
**Rationale:**
- Reduces token usage and latency
- Matches Master's communication style
- Applied to Obi-Wan SOUL.md Tone section via patch

**Trade-offs:**
- May omit nuance in complex explanations
- Sub-agents inherit via context injection (configurable per delegation)

---

## DECISION: Wikilinks for Cross-Reference

**Status:** ✅ Standardized
**Context:** Obsidian-native linking syntax `[[Note Name]]`.
**Rationale:**
- Native Obsidian graph view support
- Human-readable in markdown
- Enables vault navigation without external tools

**Trade-offs:**
- Not standard markdown (portability)
- Requires Obsidian or compatible viewer for full utility

---

## DECISION: Session State in `01_Obi-Wan/state.md`

**Status:** ✅ Implemented
**Context:** Single source of truth for active context across sessions.
**Rationale:**
- Persists across Hermes restarts
- Human-readable + machine-parseable (YAML frontmatter)
- Updated at session start/end by Obi-Wan

**Fields tracked:** session_id, active tasks, delegated agents, focus, context stack, pending decisions, environment status, quick links.

---

## Pending Decisions (Awaiting Master)

| # | Decision | Options | Recommendation |
|---|----------|---------|----------------|
| 1 | Initial sub-agents to activate | Any subset of 6 | Start with `researcher` + `archivist` |
| 2 | Git remote for backup | GitHub, GitLab, self-hosted, none | GitHub private repo if desired |
| 3 | Vault MCP server (vector search) | `obsidian-mind`, `zvec`, none | Defer until >500 notes |
| 4 | Master profile detail level | Minimal vs. comprehensive | Current `00_Master/profile.md` is sufficient |

---

## Tags

#decisions #architecture #cron #git #tone #wikilinks #state-management