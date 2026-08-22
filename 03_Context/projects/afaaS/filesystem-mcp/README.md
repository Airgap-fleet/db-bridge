# FileSystem MCP Server - FastMCP Tools

A FastMCP server providing filesystem operations via stdio transport.

## Installation

```bash
pip install -e ".[dev]" 
npx @modelcontextprotocol/inspector uv run python -m mcp server "C:\the force"
```

Or directly from the project directory:

```bash
cd C:\the force\03_Context\projects\afaaS\filesystem-mcp
uv sync --dev
npx @modelcontextprotocol/inspector python -m filesystem_mcp "C:\the force"
```

## Usage

### MCP Inspector

Open a terminal in the project directory and run:

```bash
cd C:\the force\03_Context\projects\afaaS\filesystem-mcp
uv sync --dev
npx @modelcontextprotocol/inspector uv run python -m filesystem_mcp "C:\the force"
```

Or use the `python -m mcp` command:

```bash
uv run python -m mcp server "C:\the force"
```

### Available Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `fs_read` | `path: str`, `max_bytes: int = 1048576` | Read file contents from the given path. Truncates to max_bytes if specified. |
| `fs_write` | `path: str`, `content: str` | Write content to a file. Creates parent directories as needed. Returns True on success. |
| `fs_list` | `dir_path: str = ""` | List files and directories at the given path. Empty string lists current directory. |
| `fs_glob` | `pattern: str` | Find files matching a glob pattern (e.g., `"*.py"`, `"**/*.md"`). Returns absolute paths. |

### Examples

```bash
# Read a file
uv run python -m mcp server "C:\the force" <<EOF
fs_read(path="C:/the force/03_Context/projects/afaaS/filesystem-mcp/pyproject.toml")
EOF

# Write a file
uv run python -m mcp server "C:\the force" <<EOF
fs_write(path="C:/the force/logs/test.log", content="Test log entry 1\nTest log entry 2\n")
EOF

# List directory contents
uv run python -m mcp server "C:\the force" <<EOF
fs_list(dir_path="C:/the force/03_Context/projects/afaaS/filesystem-mcp")
EOF

# Glob for Python files
uv run python -m mcp server "C:\the force" <<EOF
fs_glob(pattern="*.py")
EOF
```

## Project Structure

```
filesystem-mcp/
├── pyproject.toml          # Build config, dependencies
├── README.md               # This file
└── src/
    └── filesystem_mcp/
        ├── __init__.py     # Server entry point
        ├── tools/
        │   └── __init__.py # Tool schemas and metadata
        └── server.py       # FastMCP app with stdio transport
```

## Development

### Running Tests

```bash
uv sync --dev
uv run pytest -v
```

### Checking Code Quality

```bash
uv run ruff check .
uv run mypy .
uv run ruff format --check .
```

## License

MIT
