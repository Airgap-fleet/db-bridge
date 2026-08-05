# Obsidian Vault MCP Server

Model Context Protocol server for reading, writing, searching, and navigating Obsidian vaults.

## Features

- **Read notes** — by path or name, with parsed frontmatter
- **Write notes** — create/update with frontmatter support
- **Search vault** — full-text search with tag/folder filters
- **List tags** — all tags with note counts
- **List files** — directory listing
- **Wikilink graph** — graph of connections centered on a note

## Installation

```bash
pip install -e .
```

Or from PyPI (when published):
```bash
pip install obsidian-mcp
```

## Configuration

Set the vault path via environment variable or CLI argument:

```bash
export OBSIDIAN_VAULT_PATH="C:\the force"
obsidian-mcp
```

Or pass as first argument:
```bash
obsidian-mcp "C:\path\to\vault"
```

## MCP Client Configuration

### Claude Desktop
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "obsidian": {
      "command": "obsidian-mcp",
      "args": ["C:\\the force"]
    }
  }
}
```

### Cursor / VS Code (via `mcp` extension)
```json
{
  "mcp": {
    "servers": {
      "obsidian": {
        "command": "obsidian-mcp",
        "args": ["C:\\the force"]
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `read_note(path)` | Read a note by path or name |
| `write_note(path, content, frontmatter?)` | Create/update a note |
| `search_vault(query, tags?, folder?, limit?)` | Full-text search |
| `list_tags()` | All tags with counts |
| `list_files(folder?)` | List markdown files |
| `get_graph(center?, depth?)` | Wikilink graph |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .
ruff format .

# Type check
mypy .
```

## License

MIT