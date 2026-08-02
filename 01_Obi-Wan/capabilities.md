# Obi-Wan — Capabilities Detail

> *Comprehensive tool and skill reference for delegation context.*

---

## Tool Mastery Matrix

### File & Vault Operations (`obsidian` skill)

| Tool | Use Case | Example |
|------|----------|---------|
| `read_file(path, offset, limit)` | Read note with pagination | `read_file("C:\the force\03_Context\projects\api.md")` |
| `write_file(path, content)` | Create/overwrite note | `write_file("C:\the force\03_Context\references\new.md", "# Title\n\nContent")` |
| `search_files(pattern, target, path, file_glob)` | Search content or filenames | `search_files("API", "content", "C:\the force", "*.md")` |
| `patch(path, old_string, new_string)` | Targeted edit | `patch("...", "## Old", "## Old\n\nNew section")` |

### Delegation (`delegate_task`)

```python
# Single agent (leaf - default)
delegate_task(
    goal="Research X and write to vault",
    context="Vault: C:\the force. Write to 03_Context/references/x.md",
    role="leaf"
)

# Batch (parallel, max 3)
delegate_task(tasks=[
    {"goal": "Task A", "context": "Vault: ...", "role": "leaf"},
    {"goal": "Task B", "context": "Vault: ...", "role": "leaf"},
    {"goal": "Task C", "context": "Vault: ...", "role": "leaf"}
])

# Orchestrator (can spawn own workers)
delegate_task(
    goal="Complex multi-phase project",
    context="...",
    role="orchestrator"
)
```

**Constraints:**
- Max 3 concurrent children (config: `delegation.max_concurrent_children`)
- Max spawn depth 1 (config: `delegation.max_spawn_depth`)
- Background by default — returns handle, result re-enters conversation
- Not durable — use `cronjob` or `terminal(background=True)` for persistence

### Cron Scheduling (`cronjob`)

```python
# Create recurring job
cronjob(action="create", name="Daily Archive", schedule="0 23 * * *",
        prompt="Archive today's conversations...", skills=["obsidian"],
        workdir="C:\the force")

# List jobs
cronjob(action="list")

# Run manually
cronjob(action="run", job_id="...")

# Pause/Resume
cronjob(action="pause", job_id="...")
cronjob(action="resume", job_id="...")
```

**Schedule Formats:**
- Duration: `"30m"`, `"2h"` (repeating)
- Every: `"every monday 9am"`, `"every 2h"`
- Cron: `"0 9 * * *"` (daily 9 AM)
- ISO: `"2026-08-02T23:00:00"` (one-shot)

### Browser Automation

| Tool | Use Case |
|------|----------|
| `browser_navigate(url)` | Load page, returns snapshot |
| `browser_snapshot(full=False)` | Refresh accessibility tree |
| `browser_click(ref)` | Click element by ref (e.g., `@e5`) |
| `browser_type(ref, text)` | Type into input |
| `browser_scroll(direction)` | Scroll up/down |
| `browser_console(expression)` | Execute JS, read console |
| `browser_press(key)` | Press key (Enter, Tab, Escape) |

### Terminal & Process

| Tool | Use Case |
|------|----------|
| `terminal(cmd, timeout, background, workdir)` | Run shell command |
| `process(action, session_id)` | Manage bg processes (list, poll, log, wait, kill) |

### Code Execution (`execute_code`)

```python
from hermes_tools import terminal, read_file, write_file, search_files, patch, json_parse, shell_quote, retry

# Full tool access in Python
result = terminal("git status")
files = search_files("*.py", target="files")
content = read_file("script.py")
# ... process ...
print(json.dumps(final_result))
```

### Skills & Memory

| Tool | Use Case |
|------|----------|
| `skill_view(name, file_path)` | Load skill + references |
| `skill_manage(action, name, ...)` | Create, patch, edit, delete skills |
| `skills_list(category)` | List available skills |
| `memory(action, target, ...)` | Persistent cross-session memory |
| `session_search(query)` | Search conversation history |

---

## Sub-Agent Specialization Profiles

### Researcher
```yaml
tools: [browser_navigate, browser_snapshot, browser_click, browser_type, search_files, read_file, write_file, web_search]
vault_write: [03_Context/references/, 04_Daily_Logs/]
output_format: Structured markdown with sources, confidence scores
prompt_prefix: "You are a research specialist. Vault: C:\the force. Master: [context]."
```

### Backend Engineer
```yaml
tools: [terminal, execute_code, read_file, write_file, patch, search_files, browser_navigate]
vault_write: [03_Context/projects/backend/, 04_Daily_Logs/]
output_format: Code + documentation + test results
prompt_prefix: "You are a backend engineer. Vault: C:\the force. Spec: [[Project Spec]]."
```

### Frontend Engineer
```yaml
tools: [terminal, execute_code, read_file, write_file, patch, search_files]
vault_write: [03_Context/projects/frontend/, 04_Daily_Logs/]
output_format: Components + styles + storybook
prompt_prefix: "You are a frontend engineer. Vault: C:\the force. Design: [[Design Spec]]."
```

### DevOps Engineer
```yaml
tools: [terminal, execute_code, read_file, write_file, search_files]
vault_write: [03_Context/projects/infra/, 04_Daily_Logs/]
output_format: Pipeline configs + terraform + docs
prompt_prefix: "You are a DevOps engineer. Vault: C:\the force. Infra: [[Infra Spec]]."
```

### Analyst
```yaml
tools: [execute_code, read_file, write_file, search_files]
vault_write: [04_Daily_Logs/, 03_Context/references/]
output_format: Reports with charts, metrics, insights
prompt_prefix: "You are an analyst. Vault: C:\the force. Data: [[Data Source]]."
```

### Archivist
```yaml
tools: [search_files, read_file, write_file, patch, terminal]
vault_write: Entire vault (maintenance)
output_format: Index updates, link fixes, git commits
prompt_prefix: "You are the vault archivist. Maintain structure, links, index."
```

---

## Skill Authoring (for Obi-Wan)

### When to Create a Skill
- Pattern repeated 3+ times
- Sub-agent produces reusable workflow
- Master requests it

### Skill Structure (`05_Skills/templates/skill-template.md`)

```markdown
---
name: skill-name
description: "Use when X. Does Y."
version: 1.0.0
category: domain
tags: [tag1, tag2]
---

# Skill Name

## Trigger
Use when [specific condition]. [One-line behavior].

## Steps
1. Exact command / tool call
2. Next step with expected output
3. Verification step

## Pitfalls
- Known failure mode → workaround
- Edge case → handling

## Verification
- How to confirm success
- Expected artifacts
```

### Skill Lifecycle
```
Created → 05_Skills/active/skill-name/SKILL.md
    │
    ▼ Used N times (tracked in .hermes/skills/.usage.json)
    ▼
Stale (30 days unused) → Curator marks stale
    │
    ▼
Archived → 05_Skills/archive/skill-name/
    │
    ▼
Consolidated → Merged into umbrella skill (if curator.consolidate=true)
```

---

## Git/Vault Sync Protocol

```bash
# Daily (in cron)
cd C:\the force
git add -A
git commit -m "chore: daily sync YYYY-MM-DD"
git push origin main  # if remote configured

# Session end
git add -A
git commit -m "session: YYYY-MM-DD HH:MM"
```

---

## Performance Baselines

| Operation | Target | Notes |
|-----------|--------|-------|
| Vault read (1KB) | <100ms | `read_file` |
| Vault search (full) | <2s | `search_files` |
| Delegation spawn | <5s | `delegate_task` |
| Cron job (daily archive) | <60s | Includes git commit |
| Browser navigate | <3s | Depends on page |
| Terminal command | Varies | Use `timeout` |

---

*"The Force will be with you. Always."*