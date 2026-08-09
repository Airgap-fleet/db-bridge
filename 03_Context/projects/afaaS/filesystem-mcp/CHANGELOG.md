# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-07

### Added
- Initial release of Filesystem MCP Server
- FastMCP-based server with stdio transport
- Core filesystem operations:
  - `read_file` — Read files safely (binary → base64)
  - `write_file` — Atomic writes with directory creation
  - `list_dir` — Directory listing with glob filtering and recursion
  - `search_files` — Content search via ripgrep
  - `glob` — File pattern matching
  - `patch_file` — Targeted string replacement
- Security features:
  - Configurable sandbox root directory
  - Symlink protection (disabled by default)
  - File size limits (default 10MB)
  - Absolute path blocking (disabled by default)
- Pydantic v2 models for all requests/responses
- Comprehensive test suite (unit + integration, >90% coverage)
- Multi-stage Dockerfile (non-root, health checks)
- GitHub Actions CI/CD pipeline (lint, typecheck, test, build, publish)
- Development tooling (ruff, mypy, pytest, pre-commit)

### Security
- Path traversal prevention via sandbox root enforcement
- Symlink attack mitigation
- Atomic write operations to prevent corruption
- Size limits to prevent resource exhaustion

### Documentation
- README with quick start, configuration, and tool reference
- Docker and docker-compose examples
- Environment variable configuration template
- Architecture overview

## [Unreleased]

### Planned
- Windows-specific path handling improvements
- Additional file metadata in responses
- Watch/notify for file changes
- Batch operations support
- Custom ignore patterns (.gitignore style)