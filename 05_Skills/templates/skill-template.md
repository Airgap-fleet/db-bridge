# Skill Template

> *Copy to `05_Skills/active/skill-name/SKILL.md` and customize.*

---

```markdown
---
name: skill-name
description: "Use when [trigger condition]. [One-line behavior summary]."
version: 1.0.0
category: [domain: research, coding, devops, analysis, maintenance]
tags: [tag1, tag2, tag3]
---

# Skill Name

## Trigger
Use when [specific condition]. [One-line behavior summary].

## Prerequisites
- [Required tool/skill]
- [Required vault structure]
- [Required context]

## Steps
1. **Step 1:** [Exact command / tool call]
   - Expected: [What success looks like]
2. **Step 2:** [Next step with expected output]
   - Expected: [What success looks like]
3. **Step 3:** [Verification step]
   - Expected: [Confirmation criteria]

## Context Injection (for delegation)
```markdown
**Goal:** [Delegation goal]
**Context:** 
- Vault: C:\the force
- Master: [Master's context]
- Relevant notes: [[Link1]], [[Link2]]
**Output Location:** [Exact vault path]
**Success Criteria:** 
- [ ] [Criterion 1]
- [ ] [Criterion 2]
**Timeout:** [Minutes]
```

## Pitfalls
| Pitfall | Detection | Workaround |
|---------|-----------|------------|
| [Known failure mode] | [How to detect] | [Recovery action] |
| [Edge case] | [How to detect] | [Handling] |

## Verification
- [ ] [How to confirm success]
- [ ] [Expected artifacts in vault]
- [ ] [Metrics/quality checks]

## Example Usage
```python
# When [trigger condition]:
delegate_task(
    goal="[Goal from contract]",
    context="[Context from contract]",
    role="leaf"
)
```

## Related Skills
- `[related-skill-1]` — [Relationship]
- `[related-skill-2]` — [Relationship]

## Changelog
| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | YYYY-MM-DD | Initial creation |
```