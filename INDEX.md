# The Force — Vault Navigation Hub

> **Entry point for all vault knowledge. Every file linked with keyword summary for fast retrieval.**
> Run `search_files` on vault root for full-text; use this index for structural navigation.

---

## 🎯 Master Profile & Protocols

- [profile.md](00_Master/profile.md) — `Master identity, preferences, standing orders, communication style, tech stack (Python/TS, VS Code, Git Bash, uv)`
- [protocols.md](00_Master/protocols.md) — `Addressing rules, decision matrix, error handling, vault discipline (wikilinks, tags), delegation contracts, session startup/shutdown, skill extraction triggers`
- [secrets.md](00_Master/secrets.md) — `API keys (Alpha Vantage, FRED) — gitignored, loaded by scripts via regex`

---

## 🤖 Obi-Wan Core Memory

- [identity.md](01_Obi-Wan/identity.md) — `Name, role, vault path, purpose, capabilities matrix (vault ops, delegation, cron, web, code, git, skills), sub-agent registry (6 planned), standing orders, session log refs`
- [capabilities.md](01_Obi-Wan/capabilities.md) — `Tool mastery matrix (file ops, delegation patterns, cron formats, browser tools, terminal, execute_code, skills), sub-agent specialization profiles (researcher, backend, frontend, devops, analyst, archivist), skill authoring template, git sync protocol, performance baselines`
- [lessons.md](01_Obi-Wan/lessons.md) — `Chronological lessons: 2026-08-02 initialization complete, vault structure created, soul spec written, ready for directives`
- [state.md](01_Obi-Wan/state.md) — `Session metadata (ID, timestamps, git), active tasks (INIT-001, ARCH-001, ANAKIN-001, OPENR-001), delegated agents, current focus, context stack (8 items), pending decisions (7), environment status, quick links to all core files`

---

## 👥 Sub-Agent Registry & Templates

- [registry.md](02_Sub-Agents/registry.md) — `Active agents (none yet), 6 planned specializations (researcher, coder-backend, coder-frontend, devops, analyst, archivist) with vault scopes, delegation log, lifecycle mermaid diagram, activation protocol, resource limits (3 concurrent, depth 1, 10min timeout)`
- [templates/researcher.md](02_Sub-Agents/templates/researcher.md) — `Research specialist prompt, tools, vault write scope, output format`
- [templates/coder-backend.md](02_Sub-Agents/templates/coder-backend.md) — `Backend engineer prompt, tools, vault scope, output format`
- [templates/coder-frontend.md](02_Sub-Agents/templates/coder-frontend.md) — `Frontend engineer prompt, tools, vault scope, output format`
- [templates/devops.md](02_Sub-Agents/templates/devops.md) — `DevOps engineer prompt, tools, vault scope, output format`
- [templates/analyst.md](02_Sub-Agents/templates/analyst.md) — `Data analyst prompt, tools, vault scope, output format`
- [templates/archivist.md](02_Sub-Agents/templates/archivist.md) — `Vault archivist prompt, tools, entire vault scope, output format`

---

## 📁 Projects (Active & Planned)

- [super-yachts.md](03_Context/projects/super-yachts.md) — `STCW, Powerboat L2, ENG1 highest rating, 3rd/2nd steward target 50m+, Barnstaple, career transition from Sainsbury's, dual British/South African citizenship, marine background Aruba/Caribbean`
- [trading/README.md](03_Context/projects/trading/README.md) — `20+ strategy dirs: Faber trend-following, walkforward validation, macro factors, volatility targeting, param optimization; Trading 212, Invesco FTSE All-World; Python pandas/numpy/yfinance/vectorbt; git uncommitted, no deploy pipeline`
- [campervan.md](projects/campervan.md) — `Peugeot Boxer, Victron electrical, stale since 2026-07-28, no floorplan/timeline/budget, binary decision: proceed or #on-hold`

---

## 🖥️ Systems & Infrastructure

- [hardware.md](03_Context/systems/hardware.md) — `AMD Ryzen 7 8745H 3.8GHz, 32GB RAM (29.8GB usable), Radeon 780M iGPU 2GB VRAM, 954GB SSD, Windows 11 Pro, Ollama models (qwen2.5:14B, qwen2.5:14B-64k, qwen3.6:27B, deepseek-r1:8b planned), DirectML GPU acceleration (OLLAMA_DML=1), performance estimates CPU vs GPU`
- [AgentComms.md](AgentComms.md) — `Shared agent-to-agent messaging log, structured entries with timestamps`
- [Decisions Log.md](Decisions Log.md) — `2026-07-28 vault setup & duplicate cleanup, 2026-07-29 medical ENG1 passed (expires 2028-07-29)`

---

## 📊 Daily Logs & Indexes

- [index.md](04_Daily_Logs/index.md) — `Log structure (YYYY-MM-DD/ with master-dialogue, subagent-traces, decisions, metrics, vault-health), date index table, tags index (#initialization, #vault-setup, #obi-wan-design, etc.), search tips, cron jobs (daily archive 23:00, reindex 03:00, skill consolidation Sun 04:00, project health Mon 09:00, backup 02:00)`
- [2026-08-02/master-dialogue.md](04_Daily_Logs/2026-08-02/master-dialogue.md) — `Master ↔ Obi-Wan conversation transcript`
- [2026-08-02/subagent-traces.md](04_Daily_Logs/2026-08-02/subagent-traces.md) — `Full sub-agent delegation transcripts`
- [2026-08-02/decisions.md](04_Daily_Logs/2026-08-02/decisions.md) — `Key decisions with rationale`
- [2026-08-02/metrics.md](04_Daily_Logs/2026-08-02/metrics.md) — `Token usage, latency, success rates`
- [2026-08-02/vault-health.md](04_Daily_Logs/2026-08-02/vault-health.md) — `Archivist health report`

---

## 🧠 Skills & Skill Map

- [Skill Map.md](Skill Map.md) — `Core (obsidian, plan, web/research), delegated to sub-agents (image/video processing), situational (systematic-debugging, TDD, github-pr-workflow), disabled (macOS-only, unused), monthly review cadence logged in Decisions Log`
- [skill-template.md](05_Skills/templates/skill-template.md) — `Skill structure: frontmatter, trigger, steps, pitfalls, verification, lifecycle (active → stale → archived → consolidated)`

---

## ⚡ Anakin Trading Agent

- [Anakin_STATUS.md](Anakin/Anakin_STATUS.md) — `Vault exploration summary, API keys (Alpha Vantage, FRED), preferred LLM qwen2.5:14B-64k, pipeline.py fetches GBP/USD OHLCV + macro (UNRATE, PAYEMS), computes SMA50/200, RSI14, outputs signals.txt & AgentComms.md, current NO_SIGNAL, next steps: verify keys, fix endpoints, add warm-up, document MCP integration`
- [review_2026-08-01.md](Anakin/review_2026-08-01.md) — `Hourly cron checks 00:09–23:00, file inventory (pipeline.py, backtest_summary.txt, signals.txt, Anakin_STATUS.md, review log growing)`

---

## 💬 Chat Logs

- [Chat Logs/](Chat Logs/) — `ChatLog-2026-07-29.md through 2026-08-01.md — raw conversation history exports`

---

## 📅 Daily Notes (July 2026)

- [2026-07-27.md](July 2026/2026-07-27.md) — `Daily note`
- [2026-07-28.md](July 2026/2026-07-28.md) — `Daily note`
- [2026-07-29.md](July 2026/2026-07-29.md) — `Daily note`

---

## 🔍 Search & Navigation Tips

| Need | Method |
|------|--------|
| By topic | `search_files(pattern, target="content", path="C:\\the force")` |
| By filename | `search_files("*.md", target="files", path="C:\\the force")` |
| By tag | Search `#tag` in vault (tags in frontmatter/inline) |
| By date | Navigate `04_Daily_Logs/YYYY-MM-DD/` |
| By agent | Search `agent: researcher` in subagent-traces.md |
| By decision | Search `DECISION:` in decisions.md |
| Wikilink traversal | Click `[[Wikilink]]` in Obsidian |

---

*\"The archives are complete. If it's not in the archives, it doesn't exist.\"*