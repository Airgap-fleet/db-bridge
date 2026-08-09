# Filesystem MCP Server

> **Local Filesystem MCP Server** — Safe file operations with configurable sandbox for AI agents.

[![PyPI](https://img.shields.io/pypi/v/filesystem-mcp.svg)](https://pypi.org/project/filesystem-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/filesystem-mcp.svg)](https://pypi.org/project/filesystem-mcp/)
[![License](https://img.shields.io/pypi/l/filesystem-mcp.svg)](LICENSE)

A Model Context Protocol (MCP) server that provides safe, sandboxed filesystem operations for AI assistants. Built with [FastMCP](https://github.com/jlowin/fastmcp) for high performance and reliability.

## Features

- **🔒 Secure by Default** — Configurable root directory, symlink protection, size limits
- **⚡ Fast & Async** — Built on FastMCP with full async support
- **🛠️ Rich Toolset** — Read, write, list, search, glob, and patch operations
- **🔍 Ripgrep Integration** — Fast content search with regex support
- **🐳 Container Ready** — Multi-stage Dockerfile, non-root, health checks
- **📦 Modern Python** — Hatch, Pydantic v2, type hints, 90%+ test coverage

## Quick Start

### Installation

```bash
# From PyPI (when published)
pip install filesystem-mcp

# From source
git clone https://github.com/afaaS/filesystem-mcp
cd filesystem-mcp
pip install -e .
```

### Configuration

Configure via environment variables or `.env` file:

```bash
# Required: Root directory for all operations (sandbox)
export FILESYSTEM_MCP_ROOT_PATH="/path/to/sandbox"

# Optional: File size limit (default: 10MB)
export FILESYSTEM_MCP_MAX_FILE_SIZE=10485760

# Optional: Allow symlinks (default: false)
export FILESYSTEM_MCP_FOLLOW_SYMLINKS=false

# Optional: Allow absolute paths (default: false)
export FILESYSTEM_MCP_ALLOW_ABSOLUTE_PATHS=false

# Optional: Default encoding (default: utf-8)
export FILESYSTEM_MCP_DEFAULT_ENCODING=utf-8
```

### Running the Server

```bash
# Stdio transport (for MCP clients like Claude Desktop)
filesystem-mcp

# Or with explicit config
FILESYSTEM_MCP_ROOT_PATH=/my/sandbox filesystem-mcp
```

## MCP Client Configuration

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "filesystem-mcp",
      "env": {
        "FILESYSTEM_MCP_ROOT_PATH": "/home/user/projects"
      }
    }
  }
}
```

### Cursor / VS Code

```json
{
  "mcp": {
    "servers": {
      "filesystem": {
        "command": "filesystem-mcp",
        "env": {
          "FILESYSTEM_MCP_ROOT_PATH": "${workspaceFolder}"
        }
      }
    }
  }
}
```

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `read_file` | Read a file as text (binary → base64) | `path`, `encoding?`, `max_size?` |
| `write_file` | Write content atomically | `path`, `content`, `encoding?`, `create_dirs?`, `atomic?` |
| `list_dir` | List directory with filters | `path`, `recursive?`, `glob_pattern?`, `include_hidden?`, `max_depth?` |
| `search_files` | Search content with ripgrep | `pattern`, `path`, `case_sensitive?`, `glob_pattern?`, `context_lines?`, `max_results?` |
| `glob` | Find files by glob pattern | `pattern`, `path`, `recursive?`, `include_hidden?`, `max_results?` |
| `patch_file` | Targeted string replacement | `path`, `old_str`, `new_str`, `encoding?` |

## Tool Reference

### `read_file`

Read a file safely. Binary files are detected and returned as base64.

```json
{
  "path": "src/main.py",
  "encoding": "utf-8",
  "max_size": 1048576
}
```

**Response:**
```json
{
  "path": "src/main.py",
  "content": "def main():\n    print('hello')",
  "size": 28,
  "encoding": "utf-8",
  "is_binary": false
}
```

### `write_file`

Write content atomically (temp file + rename).

```json
{
  "path": "src/new.py",
  "content": "def hello():\n    return 'world'",
  "encoding": "utf-8",
  "create_dirs": true,
  "atomic": true
}
```

### `list_dir`

List directory with optional filtering.

```json
{
  "path": "src",
  "recursive": true,
  "glob_pattern": "*.py",
  "include_hidden": false,
  "max_depth": 3
}
```

### `search_files`

Search file contents using ripgrep (requires `rg` installed).

```json
{
  "pattern": "def hello",
  "path": "src",
  "case_sensitive": false,
  "glob_pattern": "*.py",
  "context_lines": 2,
  "max_results": 50
}
```

### `glob`

Find files matching a glob pattern.

```json
{
  "pattern": "**/*.py",
  "path": ".",
  "recursive": true,
  "include_hidden": false,
  "max_results": 100
}
```

### `patch_file`

Apply a targeted patch (find & replace).

```json
{
  "path": "src/main.py",
  "old_str": "print('hello')",
  "new_str": "print('world')",
  "encoding": "utf-8"
}
```

**Response:**
```json
{
  "path": "src/main.py",
  "replacements": 1,
  "old_size": 28,
  "new_size": 28
}
```

## Security Model

The server implements multiple security layers:

1. **Path Sandboxing** — All paths resolved relative to `FILESYSTEM_MCP_ROOT_PATH`
2. **Symlink Protection** — Symlinks blocked by default (`follow_symlinks=false`)
3. **Size Limits** — Configurable max file size (default 10MB)
4. **Absolute Path Control** — Absolute paths blocked by default
5. **Atomic Writes** — Prevents partial/corrupt writes

> ⚠️ **Never run with `FILESYSTEM_MCP_ROOT_PATH=/` or without a configured root in production.**

## Docker Usage

### Build

```bash
docker build -t filesystem-mcp .
```

### Run

```bash
docker run --rm \
  -v /host/path:/sandbox:ro \
  -e FILESYSTEM_MCP_ROOT_PATH=/sandbox \
  filesystem-mcp
```

### Docker Compose

```yaml
services:
  filesystem-mcp:
    build: .
    environment:
      - FILESYSTEM_MCP_ROOT_PATH=/sandbox
    volumes:
      - ./my-project:/sandbox:ro
    healthcheck:
      test: ["CMD", "python", "-c", "import filesystem_mcp; print('ok')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Development

### Setup

```bash
# Clone and install in dev mode
git clone https://github.com/afaaS/filesystem-mcp
cd filesystem-mcp
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# All tests with coverage
pytest --cov=filesystem_mcp --cov-report=term-missing

# Unit tests only
pytest tests/test_core.py tests/test_models.py

# Integration tests only
pytest tests/test_integration.py
```

### Lint & Type Check

```bash
# Lint
ruff check .
ruff format --check .

# Type check
mypy src/filesystem_mcp
```

## Project Structure

```
filesystem-mcp/
├── pyproject.toml           # Project config (hatch)
├── README.md                # This file
├── LICENSE                  # MIT License
├── .github/workflows/ci.yml # CI/CD pipeline
├── Dockerfile               # Multi-stage container
├── docker-compose.yml       # Local dev stack
├── .env.example             # Config template
├── src/
│   └── filesystem_mcp/
│       ├── __init__.py      # Package exports
│       ├── server.py        # FastMCP app + tools
│       ├── core.py          # Business logic (no MCP deps)
│       └── models.py        # Pydantic models
└── tests/
    ├── test_models.py       # Config/model tests
    ├── test_core.py         # Core logic tests
    └── test_integration.py  # MCP tool integration tests
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│ MCP Client  │────▶│ FastMCP App  │────▶│ Core Logic │
│ (Claude,    │     │ (server.py)  │     │ (core.py)  │
│  Cursor)    │     │              │     │            │
└─────────────┘     └──────────────┘     └─────┬──────┘
                                               │
                    ┌──────────────────────────┘
                    ▼
            ┌───────────────┐
            │ Pydantic      │
            │ Models        │
            │ (models.py)   │
            └───────────────┘
```

- **server.py** — Thin MCP transport layer, registers tools
- **core.py** — All business logic, zero FastMCP dependencies, fully testable
- **models.py** — Request/response validation, configuration

## Requirements

- Python 3.11+
- ripgrep (`rg`) for `search_files` tool
- Linux/macOS/Windows (WSL2 recommended on Windows)

## License

MIT License — see [LICENSE](LICENSE) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `pre-commit run --all-files`
5. Submit a PR

## Related

- [Obsidian MCP Server](../obsidian-mcp) — Vault operations
- [PostgreSQL MCP Server](../postgresql-mcp) — Database operations
- [AFaaS Roadmap](../../roadmap.md) — Product roadmap