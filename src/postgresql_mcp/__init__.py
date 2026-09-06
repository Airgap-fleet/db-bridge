"""PostgreSQL MCP Server package."""

from postgresql_mcp.env import apply_legacy_env as _apply_legacy_env
from postgresql_mcp.server import mcp

_apply_legacy_env()

__version__ = "1.0.3"
__all__ = ["mcp"]
