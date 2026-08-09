"""Filesystem MCP Server — safe file operations with configurable sandbox."""

__version__ = "0.1.0"
__author__ = "AFaaS Team"
__email__ = "engineering@afaaS.io"

from filesystem_mcp.core import FilesystemCore
from filesystem_mcp.models import FilesystemConfig

__all__ = [
    "FilesystemCore",
    "FilesystemConfig",
    "__version__",
]
