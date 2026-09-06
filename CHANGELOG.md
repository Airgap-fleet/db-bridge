# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Windows per-user installer and uninstaller (`installer/`), UNSIGNED INTERNAL
- Protocol-only and full-DB self-test (`scripts/self_test.py`, `scripts/self_test.ps1`)
- `proof-pack/` demo, signing, egress, and hash notes
- Canonical `DB_BRIDGE_*` environment prefix with legacy `POSTGRES_*` / `POSTGRESQL_MCP_*` mapping
- Regression test that structured logs go to stderr only (`tests/test_stdio_logging.py`)

### Changed
- README leads with the Windows installer; pip/uvx are documented as Advanced
- `.env.example` documents `DB_BRIDGE_*`

### Security
- stdio MCP stdout stays JSON-RPC clean (no structured logs on stdout)
- No telemetry or phone-home

## [1.0.0] - 2026-08-22

### Added
- FastMCP 3.x transport layer with stdio, SSE, and HTTP transports
- Bearer token authentication via TokenVerifier (compatible with Obsidian/Filesystem MCPs)
- Health check endpoint (`/health`) and server info endpoint (`/info`)
- Structured logging with structlog (JSON output, log levels)
- Pydantic v2 configuration via pydantic-settings (environment variable support)
- Lifespan management for connection pool initialization/cleanup
- Synchronous core module (no FastMCP dependencies) with async API
- 6 database tools: query, execute, list_tables, describe_table, run_migration, explain_analyze
- Parameterized query support for SQL injection prevention
- Read-only mode for secure deployments
- Connection pooling with configurable size
- Comprehensive unit test suite (39 tests, 78% coverage)
- Integration test suite (marked for manual execution with PostgreSQL)
- Multi-stage Dockerfile with non-root user
- Docker Compose for local development
- GitHub Actions CI/CD pipeline
- Full type safety with mypy strict mode
- 75%+ test coverage requirement
- **Stateless protocol (2026-07-28 / SEP-2575): no global session state, explicit config per request**
- **`create_core(config)` factory — fresh instance per request**
- **DXT bundle for one-click installation in Claude Desktop**

### Changed
- **BREAKING**: Core rewritten as synchronous module with async facade
- **BREAKING**: Server uses FastMCP 3.x (was 2.x)
- **BREAKING**: Authentication changed to TokenVerifier (was none)
- **BREAKING**: Configuration via pydantic-settings/env vars (was python-dotenv)
- Updated dependencies: asyncpg 0.29+, pydantic 2.10+, pydantic-settings 2.6+, structlog 25.1+
- Removed global `_core` singleton — stateless per-request instantiation

### Security
- Parameterized queries only (no string interpolation)
- Read-only mode blocks write operations
- Connection pooling with least privilege
- Bearer token authentication for all transports
- Audit logging for all operations

## [0.1.0] - 2026-08-07

### Added
- Initial release