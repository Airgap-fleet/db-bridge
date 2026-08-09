# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial PostgreSQL MCP Server implementation
- 6 database tools: query, execute, list_tables, describe_table, run_migration, explain_analyze
- Parameterized query support for SQL injection prevention
- Read-only mode for secure deployments
- Connection pooling with configurable size
- Structured JSON logging with structlog
- Comprehensive test suite (unit + integration)
- Multi-stage Dockerfile with non-root user
- Docker Compose for local development
- GitHub Actions CI/CD pipeline
- Full type safety with mypy strict mode
- 90%+ test coverage requirement

### Security
- Parameterized queries only (no string interpolation)
- Read-only mode blocks write operations
- Connection pooling with least privilege
- Audit logging for all operations

## [0.1.0] - 2026-08-07

### Added
- Initial release