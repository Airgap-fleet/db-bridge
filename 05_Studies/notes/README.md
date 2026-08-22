# Business Studies Learning Vault

This folder serves as persistent memory for studying **Business Concepts** using Hermes Agent and the Obsidian vault. The user wants to learn business basics, starting from fundamentals and progressing deeper over time.

## Purpose & Methodology (Learned)

The skill's core workflow: Read notes with `read_file`, list/search with `search_files`, create new notes via `write_file` for append operations when needed. Wikilinks use the syntax `[[Note Name]]` to link related content and build a connected knowledge graph. I'll save key information as important within this 05_Studies/nodes folder in the vault, using all of these skills (read files/search/create/edit) along with any tools from hermes agent skill (file read/write/patches).

## Learning Strategy: Basics First → Deeper Concepts

Start at fundamentals like accounting basics and financial statements. Progress to marketing strategies, organizational behavior, management theories, operations research, business law fundamentals—moving methodically as I build understanding. For each topic, gather information from internet sources, extract key points into my structured notes that capture essential concepts without overwhelming detail so the knowledge remains actionable and useful over time rather than becoming stale quickly.

## Key Operational Documents

### 🔧 Operations Manual (Primary Reference)
- **File**: `MCP_SERVER_BUSINESS_OPERATIONS_MANUAL.md`
- **Purpose**: Complete blueprint for running an autonomous MCP server business
- **Contents**: 
  - Full agent team structure (20+ specialized roles)
  - Organizational hierarchy and reporting lines
  - Standard operating procedures (SOPs)
  - KPI dashboards and metrics definitions
  - Deployment sequences and milestones
  
### 📚 Foundation Studies (Support Resources)

1. **Accounting Basics** (`1-ACCOUNTING_BASICS.md`)
   - Financial statements, unit economics, burn analysis
   
2. **Marketing Fundamentals** (`2-MARKETING_FUNDAMENTALS.md`)
   - GTM strategies, pricing models, customer acquisition
   
3. **Management Leadership** (`3-MANAGEMENT_LEADERSHIP_FUNDAMENTALS.md`)
   - Organizational structure, team management, operations

4. **MCP Server Business Fundamentals** (`01-mcp-server-business-fundamentals.md`)
   - Protocol basics, market position, compliance landscape
   
5. **Enterprise Adoption Patterns** (`4-TECH_STARTUP_MCP_SERVER_BUSINESS.md`)
   - 9800+ server ecosystem, scaling sequences, sales cycles

6. **Business Studies Skill Definition** (`skill_definitions.md` — *see skill_manage*)
   - Formal definition for business-mcp-server-fundamentals skill

---

## Active Agent Team (From Operations Manual)

The complete autonomous team ready to run the MCP server business:

| Layer | Primary Agents | Total Roles |
|-------|---------------|-------------|
| **Leadership** | CEO (Rupert), CTO, CLO, CFO | 4 |
| **Development** | SRE, Dev, Docs, UX, QA | 5 |
| **Operations** | PM, BI, CSM, Growth | 4 |
| **Customer** | DS, Edu, Notifications | 3 |
| **Infrastructure** | Sec, DB, Cloud Ops | 3 |
| **Sales** | VP_Sales, Sales Enab, SDR, AC, Rev CSM | 5 |
| **TOTAL** | | **~24 specialized roles** |

### Quick Reference Links
- [[MCP_SERVER_BUSINESS_OPERATIONS_MANUAL]] — Full operations manual
- [[01-mcp-server-business-fundamentals]] — Protocol basics
- [[4-TECH_STARTUP_MCP_SERVER_BUSINESS]] — Enterprise patterns
- [[3-MANAGEMENT_LEADERSHIP_FUNDAMENTALS]] — Org structure guidance

---

## Usage Guide

To deploy this autonomous business:

1. **Activate CEO (Rupert)**: Load the `rupert-soul.md` skill from the Sub-Agents vault
2. **Spawn team**: Use `delegate_task` to initialize each role with appropriate goals
3. **Setup tools**: Configure Hermes + GitHub + Stripe integrations via `setup_mcp`
4. **Launch sequence**: Follow Phase 1 → 2 → 3 deployment from operations manual

The team requires no human intervention once launched — the CEO coordinates all revenue operations, sales pipelines, and customer success while technical agents handle development and deployments continuously.

---

*Created to facilitate ongoing self-study in business principles and autonomous agent operations.*
