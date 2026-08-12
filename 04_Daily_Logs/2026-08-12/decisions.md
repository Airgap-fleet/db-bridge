# Key Decisions — 2026-08-12

**Session:** `20260812_210644_0098e8` — "check scotty's work"
**Decision Authority:** Master (final), Obi-Wan (analysis/recommendation)

---

## Decision 1: Scotty's Model Configuration — Keep OpenRouter, Disable MOA

**Context:** Scotty's soul specifies `hermes3:8B` (Ollama local) but config uses `cohere/north-mini-code:free` (OpenRouter) with MOA enabled (claude-opus-4.8 aggregator). Obi-Wan recommended switching to Ollama + disabling MOA for determinism.

**Master's Decision:**
- ✅ **Keep OpenRouter** — local models have tool-calling issues
- ✅ **Keep 64K context** (ollama_num_ctx: 65536)
- ❌ **MOA: Master overruled Obi-Wan's disable recommendation** — left enabled
- ❌ **Max tokens: Master overruled 4096 recommendation** — kept 8192

**Rationale:**
- Local model tool-calling failures are a known blocker (see Hermes GH issues)
- OpenRouter free tier provides working tool calls despite rate limits
- MOA non-determinism accepted as trade-off for model diversity
- 8192 tokens needed for complex MCP server implementations

**Trade-offs:**
- Free tier rate limits → occasional 429/502 errors
- MOA aggregator (claude-opus-4.8) adds latency and cost variance
- Soul/config drift remains — soul still says Ollama

**Follow-up:** Update soul to match config (OpenRouter, MOA enabled) or add explicit note about divergence.

---

## Decision 2: Vault Hygiene — Remove All PROMPT Files

**Context:** Master suspected Scotty reading stale `PROMPT_*.md` files from `03_Context/projects/mission-control/` causing reliability issues (claiming "done" with gaps).

**Master's Decision:**
- ✅ **Delete all PROMPT files** from vault
- ✅ **Rely on daily conversations** for context/history (this cron job)
- ✅ **No prompt files in vault going forward**

**Rationale:**
- Daily conversation logs provide complete, timestamped, unfiltered history
- PROMPT files are point-in-time snapshots that stale quickly
- Sub-agents should follow current Obi-Wan directives, not archived prompts
- Reduces vault bloat and confusion

**Action Taken:** Found 1 file: `/c/Users/brook/b/C:/the force/03_Context/projects/mission-control/PROMPT.md` — pending deletion.

**Follow-up:** Delete the file. Verify no other PROMPT_*.md files exist.

---

## Decision 3: Cron Job Repair — Fix Vault Path, Re-run

**Context:** Daily Conversation Archive cron job failing since Aug 10 (502 upstream). Root cause: workdir `C:\The Force` vs actual vault `C:\the force` (case mismatch on Windows), missing `04_Daily_Logs` directory.

**Master's Decision:**
- ✅ **Fix workdir to `C:\the force`** (match actual vault path)
- ✅ **Create missing vault structure** (`04_Daily_Logs`, etc.)
- ✅ **Re-run job manually** for today's archive

**Rationale:**
- Windows case-insensitivity masks path issues in some tools but not others
- Cron job runs in isolated context — must resolve paths correctly
- Daily logs are critical for cross-session memory and accountability

**Action Taken:**
- Cron job workdir updated
- `04_Daily_Logs/2026-08-12/` created manually
- Job re-triggered (delegation `deleg_a2e56942` running)

**Follow-up:** Verify job completes successfully. Check tomorrow's scheduled run at 23:00.

---

## Decision 4: Vault Structure — Build Out Missing Directories

**Context:** Vault at `C:\the force` only contains `03_Context/projects/`. Missing: `00_Master`, `01_Obi-Wan`, `02_Sub-Agents`, `04_Daily_Logs`, `05_Skills`, `06_Archive`.

**Master's Decision:**
- ✅ **Build out full vault structure** per Obi-Wan's soul specification
- ✅ **Populate with current session data** (this cron run)
- ✅ **Use wikilinks** for cross-references

**Rationale:**
- Structured vault enables reliable sub-agent memory access
- Wikilinks create queryable knowledge graph
- Daily logs become first-class memory, not afterthought

**Follow-up:** Create directory structure and seed with:
- `00_Master/profile.md`, `protocols.md`, `directives.md`
- `01_Obi-Wan/identity.md`, `capabilities.md`, `lessons.md`, `state.md`
- `02_Sub-Agents/registry.md`, `delegation-log.md`
- `05_Skills/active/`, `archive/`, `templates/`
- `06_Archive/`

---

## Decision 5: Sprint Timeline — 3-4 Days to Mission Control HTTP Layer

**Context:** Obi-Wan estimated 3-4 days if Scotty delivers clean HTTP layer (REST + SSE + frontend connect).

**Master's Decision:**
- ✅ **Accept 3-4 day estimate** as baseline
- ⚠️ **Risk acknowledged:** Scotty has claimed "done" twice with gaps
- 📋 **Contingency:** +1-2 days per partial delivery cycle

**Rationale:**
- Hard logic (AgentListener, RoE, workflows, DB) complete
- Only transport layer (stdlib HTTP server) missing
- Scotty's reliability improvements (config fixes, PROMPT removal) should help

**Follow-up:** Monitor Scotty's next delivery. If clean → 3-4 days holds. If partial → recalibrate.

---

## Decision 6: Sub-Agent Fleet — 12 Agents Across 3 Revenue Streams

**Context:** AFaaS fleet plan: 12 agents (Leadership/Sales/Eng/Ops), 3 streams = £387K Year 1.

**Master's Decision:**
- ✅ **Proceed with fleet build** — current sprint is MCP server foundation
- ✅ **Core 3 MCP servers first:** Obsidian (done), Filesystem (done), PostgreSQL (in progress)
- ✅ **Next:** Dashboard MCP → UI/Chat → Autonomous Loop

**Rationale:**
- MCP servers are product primitives — sellable individually
- Local-first, air-gapped appeals to regulated industries (marine, finance)
- AMD/DirectML + Hermes+Obsidian+Delegation = technical moat

**Follow-up:** Complete PostgreSQL MCP. Begin Dashboard MCP.