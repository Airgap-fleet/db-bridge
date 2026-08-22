"""Filesystem MCP Server - FastMCP 3.x with TokenVerifier auth, structured logging, and multiple transports.
Stateless protocol (2026-07-28): no global session state, explicit config per request.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional

import structlog
from fastmcp import FastMCP
from fastmcp.server.auth import TokenVerifier
from fastmcp.server.dependencies import get_access_token
from pydantic_settings import BaseSettings, SettingsConfigDict

from filesystem_mcp.core import FilesystemCore
from filesystem_mcp.models import (
    DirEntry,
    FilesystemConfig,
    GlobRequest,
    GlobResponse,
    ListDirRequest,
    ListDirResponse,
    PatchFileRequest,
    PatchFileResponse,
    ReadFileRequest,
    ReadFileResponse,
    SearchFilesRequest,
    SearchFilesResponse,
    SearchMatch,
    WriteFileRequest,
    WriteFileResponse,
)

log = structlog.get_logger()


class ServerSettings(BaseSettings):
    """Server configuration via environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="FILESYSTEM_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Auth
    auth_enabled: bool = True
    auth_tokens: list[str] = []

    # Transport
    transport: str = "stdio"  # stdio, sse, http
    host: str = "127.0.0.1"
    port: int = 8422

    # Logging
    log_level: str = "INFO"
    log_json: bool = True

    # Filesystem (delegated to FilesystemConfig)
    root_path: str = "."
    max_file_size: int = 10 * 1024 * 1024
    follow_symlinks: bool = False
    allow_absolute_paths: bool = False
    default_encoding: str = "utf-8"


def get_filesystem_config() -> FilesystemConfig:
    """Create FilesystemConfig from server settings (stateless - no caching)."""
    settings = ServerSettings()
    return FilesystemConfig(
        root_path=Path(settings.root_path),
        max_file_size=settings.max_file_size,
        follow_symlinks=settings.follow_symlinks,
        allow_absolute_paths=settings.allow_absolute_paths,
        default_encoding=settings.default_encoding,
    )


def create_core() -> FilesystemCore:
    """Create a fresh FilesystemCore instance (stateless - no global state)."""
    return FilesystemCore(get_filesystem_config())


# Token verifier for authentication
class FilesystemTokenVerifier(TokenVerifier):
    """Token verifier that checks against configured tokens."""

    async def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify a bearer token."""
        settings = ServerSettings()
        if not settings.auth_enabled:
            return {"sub": "anonymous", "scopes": ["filesystem:read", "filesystem:write"]}

        if token in settings.auth_tokens:
            return {"sub": "api-client", "scopes": ["filesystem:read", "filesystem:write"]}

        return None


# FastMCP app with auth
mcp = FastMCP(
    "Filesystem MCP Server",
    auth=FilesystemTokenVerifier() if ServerSettings().auth_enabled else None,
)


# Tool implementations
@mcp.tool()
async def read_file(
    path: str,
    encoding: Optional[str] = None,
    max_size: Optional[int] = None,
) -> ReadFileResponse:
    """Read a file safely with size limits and binary detection."""
    core = create_core()
    request = ReadFileRequest(path=path, encoding=encoding, max_size=max_size)
    return core.read_file(request)


@mcp.tool()
async def write_file(
    path: str,
    content: str,
    encoding: Optional[str] = None,
    create_dirs: bool = True,
    atomic: bool = True,
) -> WriteFileResponse:
    """Write a file atomically with size limits."""
    core = create_core()
    request = WriteFileRequest(
        path=path,
        content=content,
        encoding=encoding,
        create_dirs=create_dirs,
        atomic=atomic,
    )
    return core.write_file(request)


@mcp.tool()
async def list_dir(
    path: str = ".",
    glob_pattern: Optional[str] = None,
    recursive: bool = False,
    include_hidden: bool = False,
    max_depth: Optional[int] = None,
) -> ListDirResponse:
    """List directory contents with optional filtering and recursion."""
    core = create_core()
    request = ListDirRequest(
        path=path,
        glob_pattern=glob_pattern,
        recursive=recursive,
        include_hidden=include_hidden,
        max_depth=max_depth,
    )
    return core.list_dir(request)


@mcp.tool()
async def search_files(
    pattern: str,
    path: str = ".",
    glob_pattern: Optional[str] = None,
    case_sensitive: bool = True,
    max_results: int = 100,
    context_lines: int = 2,
) -> SearchFilesResponse:
    """Search file contents using ripgrep."""
    core = create_core()
    request = SearchFilesRequest(
        pattern=pattern,
        path=path,
        glob_pattern=glob_pattern,
        case_sensitive=case_sensitive,
        max_results=max_results,
        context_lines=context_lines,
    )
    return core.search_files(request)


@mcp.tool()
async def glob(
    pattern: str,
    path: str = ".",
    recursive: bool = True,
    include_hidden: bool = False,
    max_results: int = 1000,
) -> GlobResponse:
    """Find files matching a glob pattern."""
    core = create_core()
    request = GlobRequest(
        pattern=pattern,
        path=path,
        recursive=recursive,
        include_hidden=include_hidden,
        max_results=max_results,
    )
    return core.glob(request)


@mcp.tool()
async def patch_file(
    path: str,
    old_str: str,
    new_str: str,
    encoding: Optional[str] = None,
) -> PatchFileResponse:
    """Apply a targeted patch to a file (find and replace)."""
    core = create_core()
    request = PatchFileRequest(
        path=path,
        old_str=old_str,
        new_str=new_str,
        encoding=encoding,
    )
    return core.patch_file(request)


# Health check endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request) -> dict[str, Any]:
    """Health check endpoint."""
    core = create_core()
    return {
        "status": "healthy",
        "server": "Filesystem MCP Server",
        "version": "1.0.0",
        "root_path": str(core.config.root_path),
    }


# Server info endpoint
@mcp.custom_route("/info", methods=["GET"])
async def server_info(request) -> dict[str, Any]:
    """Server information endpoint."""
    settings = ServerSettings()
    core = create_core()
    return {
        "name": "Filesystem MCP Server",
        "version": "1.0.0",
        "transport": settings.transport,
        "auth_enabled": settings.auth_enabled,
        "root_path": str(core.config.root_path),
        "max_file_size": core.config.max_file_size,
        "follow_symlinks": core.config.follow_symlinks,
        "allow_absolute_paths": core.config.allow_absolute_paths,
        "tools": [
            "read_file",
            "write_file",
            "list_dir",
            "search_files",
            "glob",
            "patch_file",
        ],
    }


def main():
    """Main entry point."""
    import uvicorn
    import logging

    settings = ServerSettings()

    # Configure structlog - use logging module level constants
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            log_level
        ),
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer() if settings.log_json else structlog.dev.ConsoleRenderer(),
        ],
    )

    log.info("server_startup", transport=settings.transport, host=settings.host, port=settings.port)

    if settings.transport == "stdio":
        mcp.run()
    elif settings.transport == "sse":
        mcp.run(transport="sse", host=settings.host, port=settings.port)
    elif settings.transport == "http":
        uvicorn.run(mcp.streamable_http_app(), host=settings.host, port=settings.port)
    else:
        raise ValueError(f"Unknown transport: {settings.transport}")


if __name__ == "__main__":
    main()