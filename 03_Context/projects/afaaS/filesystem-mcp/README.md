# File Bridge

Bridge your AI assistant to local files — read, write, search, and manage files securely without cloud dependencies.

## Installation

```bash
pip install file-bridge
```

## Usage

```bash
file-bridge
```

Or configure in your MCP client:

```json
{
  "mcpServers": {
    "files": {
      "command": "file-bridge",
      "env": {
        "FILE_BRIDGE_ROOT_PATH": "C:/path/to/files"
      }
    }
  }
}
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `FILE_BRIDGE_ROOT_PATH` | Current directory | Root directory for file operations |
| `FILE_BRIDGE_MAX_FILE_SIZE` | 10MB | Max file size for operations |
| `FILE_BRIDGE_FOLLOW_SYMLINKS` | false | Follow symlinks |
| `FILE_BRIDGE_ALLOW_ABSOLUTE_PATHS` | false | Allow absolute paths outside root |
| `FILE_BRIDGE_DEFAULT_ENCODING` | utf-8 | Text encoding |

## Available Tools

| Tool | Description |
|------|-------------|
| `read_file` | Read a file safely with size limits and binary detection |
| `write_file` | Write a file atomically with size limits |
| `list_dir` | List directory contents with optional filtering and recursion |
| `search_files` | Search file contents using ripgrep |
| `glob` | Find files matching a glob pattern |
| `patch_file` | Apply a targeted patch to a file (find and replace) |

## Transport Modes

- **stdio** (default) — For local MCP clients (Claude Desktop, etc.)
- **sse** — Server-Sent Events for HTTP clients
- **http** — Streamable HTTP for modern clients

Set via `FILE_BRIDGE_TRANSPORT` environment variable.

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
uv run pytest -v

# Check code quality
uv run ruff check .
uv run mypy .
```

## License

MIT
