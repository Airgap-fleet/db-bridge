# Changelog

All notable changes to the Dashboard MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-09

### Added
- Core Dashboard MCP Server implementation with PostgreSQL backend
- FastMCP server with registered tools:
  - `register_agent` - Register new agents
  - `get_fleet_status` - Get agent fleet status
  - `create_task` - Create tasks for agents
  - `send_message` - Send messages to channels
  - `create_channel` - Create new channels
  - `get_channel_history` - Get channel message history
  - `get_agent` - Get agent by ID
- WebSocket server for real-time communication
- Docker support with multi-stage builds
- Docker Compose for local development (PostgreSQL + Redis)
- Comprehensive test coverage (90%+)
- CI/CD pipeline with GitHub Actions
- Structured logging with structlog
- Environment-based configuration
- WebSocket hub with Redis pub/sub

### Fixed
- Database schema fixes for PostgreSQL compatibility
- Agent registration logic with proper validation
- Task creation with agent existence checks
- Channel creation with duplicate name prevention

### Changed
- Improved error handling and HTTP status codes
- Enhanced logging with structured output
- Optimized database queries with eager loading
- Better WebSocket connection management

### Dependencies
- fastmcp>=3.4
- pydantic>=2.6
- pydantic-settings>=2.0
- structlog>=24.0
- python-dotenv>=1.0
- websockets>=12.0
- pyyaml>=6.0
- httpx>=0.27
- asyncio-mqtt>=0.12

## [0.0.1] - 2026-08-07

### Added
- Initial prototype with basic models and database integration
- Pydantic models for all core entities (agents, tasks, messages, channels)
- Basic FastMCP setup with tool stubs
- PostgreSQL database schema
- Redis integration for WebSocket pub/sub
- Basic WebSocket server infrastructure