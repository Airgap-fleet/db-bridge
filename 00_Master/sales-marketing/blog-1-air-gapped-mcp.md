# Building Air-Gapped MCP Servers for Regulated Industries

**Published:** 2026-08-22  
**Author:** AFaaS Team  
**Tags:** #MCP #AI #LocalFirst #RegulatedIndustries #Obsidian

---

## The Problem: AI Agents Can't Touch Your Data

Your team uses Obsidian. Your knowledge base — meeting notes, procedures, regulations, case law — lives in markdown files with YAML frontmatter. You want AI agents to read, search, and write to this vault.

But you're in **finance, legal, marine, or defense**. Your data cannot leave your infrastructure. Cloud RAG services (Pinecone, Weaviate, OpenAI embeddings) are non-starters. Even "private cloud" MCP servers require network egress you can't approve.

**Result**: Your agents are blind to your most valuable context.

---

## The Solution: Local-First MCP Servers

MCP (Model Context Protocol) lets AI agents call tools on your machine. An MCP server runs *locally* — no network required. Your agents connect via stdio (stdin/stdout), the same way they'd talk to a local CLI.

We built **Obsidian Vault MCP** — a production-grade MCP server that gives agents:

- **Read/write/search** any note in your vault
- **Full frontmatter support** — structured queries on tags, dates, status, custom fields
- **Daily notes** with templates
- **Path sandboxing** — agents cannot escape the vault root
- **API key auth** — secure remote access via SSE/HTTP when needed
- **Structured JSON logs** — audit trail for compliance
- **Zero cloud dependencies** — fully air-gapped

---

## Why This Matters for Regulated Industries

| Requirement | Cloud RAG | Local MCP |
|-------------|-----------|-----------|
| Data residency | ❌ Leaves your network | ✅ Never leaves |
| Audit logging | ⚠️ Vendor-dependent | ✅ Your logs, your format |
| Network egress | ❌ Required | ✅ Zero (stdio) |
| Offline operation | ❌ Impossible | ✅ Native |
| Cost predictability | ❌ Per-token/per-query | ✅ Flat license |
| Custom tooling | ❌ Vendor roadmap | ✅ Your code, your timeline |

---

## Architecture: How It Works

```mermaid
graph TB
    subgraph "YOUR INFRASTRUCTURE"
        A[AI Agent<br/>(Claude, Cursor, Custom)] <-- MCP Protocol --> B[Obsidian MCP Server<br/>(obsidian-mcp)]
        B --> C[Obsidian Vault<br/>(markdown + YAML)]
        D[Local LLM<br/>(Ollama: qwen2.5-coder:7b/14b,<br/>deepseek-r1:14b, qwen3.5:9b)]
        E[Cloud LLM<br/>(Claude, GPT-4, etc.)]
    end
    
    A -.->|Bring your model| D
    A -.->|Or cloud| E
    B -.->|Model-agnostic| A
```

**Model-agnostic by design.** The MCP server exposes tools — you bring the model. Connect local Ollama models (7B-14B on 32GB RAM) or cloud LLMs. No vendor lock-in.

---

## Security by Design

1. **Path traversal prevention** — All paths resolved relative to vault root; `../` and absolute paths rejected
2. **File size limits** — Configurable (default 10MB), prevents memory exhaustion
3. **Symlink control** — Disabled by default
4. **API key authentication** — Required for SSE/HTTP transports; stdio inherits OS permissions
5. **Structured audit logs** — Every tool call logged as JSON: timestamp, tool, parameters, result, duration
6. **No secrets in code** — All config via environment variables (`OBSIDIAN_MCP_*`)

---

## Deployment: Three Modes

### 1. Developer Mode (stdio) — Zero Config
```bash
pip install obsidian-mcp
OBSIDIAN_MCP_VAULT_PATH=/path/to/vault obsidian-mcp
```
Agent connects via stdin/stdout. Simplest, most secure.

### 2. Team Mode (SSE) — Shared Access
```bash
OBSIDIAN_MCP_TRANSPORT=sse \
OBSIDIAN_MCP_API_KEY=sk-... \
OBSIDIAN_MCP_VAULT_PATH=/shared/vault \
obsidian-mcp
```
Multiple agents connect via `http://localhost:8000/mcp` with `Authorization: Bearer sk-...`

### 3. Production Mode (Docker/K8s) — Fleet Deployment
```dockerfile
FROM ghcr.io/afaas/obsidian-mcp:1.0.0
ENV OBSIDIAN_MCP_VAULT_PATH=/vault
ENV OBSIDIAN_MCP_TRANSPORT=streamable-http
ENV OBSIDIAN_MCP_API_KEY_FILE=/run/secrets/api_key
VOLUME ["/vault"]
```
Deploy as sidecar or DaemonSet. Vault mounted as read-only or read-write volume.

---

## Real-World Use Case: Marine Fleet Operations

**Context**: 50m+ superyacht, 14-day Atlantic crossing. No reliable satellite internet.

**Before**: Crew used paper checklists. Shore-based ops team couldn't assist. Post-voyage reporting took weeks.

**After**: Obsidian vault on vessel laptop. Local LLM (qwen2.5-coder:7b for speed, qwen2.5-coder:14b for complex tasks via Ollama) + Obsidian MCP.
- Engineers query maintenance logs via agent: *"Show me all engine checks from last 30 days tagged #critical"*
- Agent writes daily noon reports directly to vault with frontmatter
- Shore team syncs vault via encrypted drive on port visits — no cloud needed

**Result**: Continuous AI-assisted ops at sea. Zero satellite dependency. **Model selection per task** — 7B for quick queries, 14B for complex analysis.

---

## Getting Started

```bash
# Install
pip install obsidian-mcp

# Configure
export OBSIDIAN_MCP_VAULT_PATH=~/Obsidian/MyVault
export OBSIDIAN_MCP_LOG_LEVEL=INFO

# Run (stdio — for Claude Desktop, Cursor, etc.)
obsidian-mcp

# Or run SSE for remote agents
export OBSIDIAN_MCP_TRANSPORT=sse
export OBSIDIAN_MCP_API_KEY=$(openssl rand -hex 32)
obsidian-mcp
```

**One-click for Claude Desktop**: Download `obsidian-mcp-1.0.0.dxt` → drag into Claude Desktop → enter vault path → done.

### Model Configuration (Client Side)

**Your MCP server doesn't run the model** — the client does. In Claude Desktop / Cursor / VS Code:

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": ["obsidian-mcp"],
      "env": {
        "OBSIDIAN_MCP_VAULT_PATH": "/path/to/vault"
      }
    }
  }
}
```

Then in your client settings, choose your model:
- **Local (Ollama)**: `qwen2.5-coder:7b` (fast), `qwen2.5-coder:14b` (quality), `deepseek-r1:14b` (reasoning)
- **Cloud**: Claude 3.5 Sonnet, GPT-4o, etc.

**No server-side model config needed.** The MCP protocol separates tools from models.

---

## What's Next

- **Filesystem MCP** — Generic file operations with same security model
- **PostgreSQL MCP** — Read-only + parameterized write access to databases
- **Fleet orchestration** — Multi-agent coordination via Hermes + Kanban

---

## About AFaaS

We're a UK-based team (Barnstaple, Devon) with marine industry backgrounds (STCW, 50m+ yachts) and deep Python/TypeScript/AI engineering experience. We build **local-first agent infrastructure** for regulated industries because we've lived the constraints.

**Contact**: mcp@afaas.io | GitHub: github.com/afaas

---

*This post is part of our "Local-First MCP" series. Next: "Why Your AI Agents Need Local Vault Access (Not Cloud RAG)"*