"""Documentation and instructions for Dashboard MCP Server."""

# Dashboard MCP Server

AFaaS Dashboard MCP Server - Fleet API + AgentComms + Group Chat layer for autonomous agent orchestration.

## Overview

The Dashboard MCP Server provides a real-time monitoring and communication platform for autonomous agent fleets. It offers:

- Agent registration and status tracking
- Task creation and monitoring
- Real-time messaging and channels
- WebSocket-based real-time updates
- Fleet-wide analytics and metrics

## Quick Start

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 16+ (with asyncpg support)
- Redis 7+ (for WebSocket pub/sub)
- Docker (optional, for local development)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd dashboard-mcp
   ```

2. Install with uv (recommended):
   ```bash
   uv sync --dev
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis credentials
   ```

4. Apply database migrations:
   ```bash
   uv run alembic upgrade head
   ```

5. Start the server:
   ```bash
   uv run dashboard-mcp
   ```

### Docker Compose (Local Development)

For a full development setup with PostgreSQL and Redis:

```yaml
version: '3.8'

services:
  dashboard-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/dashboard_mcp
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=dashboard_mcp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

### MCP Inspector

To test MCP tools interactively:

```bash
npx @modelcontextprotocol/inspector uv run dashboard-mcp
```

## API Tools

The Dashboard MCP Server provides the following tools via the Model Context Protocol:

### Agent Management

#### `register_agent`

Register a new agent in the system.

**Parameters:**
- `agent_id` (string, required): Unique agent identifier (3-64 chars, alphanumeric with underscores/hyphens)
- `name` (string, required): Human-readable agent name (1-128 chars)
- `role` (string, required): Agent role/function (1-64 chars)
- `capabilities` (array of strings): List of agent capabilities
- `model` (string, required): Model identifier
- `config` (object, optional): Additional agent configuration

**Example:**
```json
{
  "agent_id": "agent-001",
  "name": "Data Processor",
  "role": "analyst",
  "capabilities": ["data_analysis", "visualization"],
  "model": "gpt-4",
  "config": {"temperature": 0.3}
}
```

#### `get_agent`

Get agent information by ID.

**Parameters:**
- `agent_id` (string, required): Agent identifier

**Returns:**
- Agent information or null if not found

#### `get_fleet_status`

Get the current status of all agents in the fleet.

**Returns:**
- Fleet statistics including total agents, healthy agents, running tasks, and token usage
- Detailed information for each agent

### Task Management

#### `create_task`

Create a new task for an agent.

**Parameters:**
- `agent_id` (string, required): Target agent ID
- `goal` (string, required): Task description (1-4096 chars)
- `context` (object, optional): Task context and parameters
- `priority` (string, optional): Task priority (low, normal, high, critical)

**Example:**
```json
{
  "agent_id": "agent-001",
  "goal": "Analyze quarterly sales data",
  "context": {"dataset": "sales_q4.csv", "format": "json"},
  "priority": "high"
}
```

### Communication

#### `send_message`

Send a message to a channel.

**Parameters:**
- `channel_id` (string, required): Target channel ID
- `from_agent` (string, required): Sender agent ID
- `content` (string, required): Message content (1-8192 chars)
- `mentions` (array of strings, optional): Agent IDs to mention
- `reply_to` (string, optional): Parent message ID

#### `create_channel`

Create a new communication channel.

**Parameters:**
- `name` (string, required): Channel name (3-64 chars, alphanumeric with underscores/hyphens)
- `description` (string, optional): Channel description (up to 512 chars)
- `members` (array of strings, optional): Initial members

#### `get_channel_history`

Get message history for a channel.

**Parameters:**
- `channel_id` (string, required): Channel identifier
- `limit` (integer, optional): Number of messages to retrieve (default: 100)
- `offset` (integer, optional): Pagination offset (default: 0)

### Real-time Communication

#### WebSocket Endpoint

The server provides a WebSocket endpoint at `/ws` for real-time updates:

**Connection:**
```
ws://localhost:8000/ws?channel=general
```

**Message Format:**
```json
{
  "type": "ping" // or "pong", "agent_status", "task_update", etc.
}
```

**WebSocket channels:**
- `all` (default): All system events
- Channel names: Any registered channel name

## Configuration

### Environment Variables

The server uses the following environment variables:

- `DATABASE_URL` (required): PostgreSQL connection string
- `REDIS_URL` (optional): Redis connection URL (default: `redis://localhost:6379`)
- `DASHBOARD_MCP_PORT` (optional): Server port (default: 8000)
- `DASHBOARD_MCP_WS_ENABLED` (optional): Enable WebSocket (default: true)
- `DASHBOARD_MCP_AGENTCOMMS_PATH` (optional): Path to AgentComms.md (default: "AgentComms.md")
- `DASHBOARD_MCP_FLEET_CONFIG` (optional): Path to fleet configuration (default: "fleet.yaml")
- `DASHBOARD_MCP_CHANNELS_DIR` (optional): Channels directory (default: "channels")
- `DASHBOARD_MCP_ENABLE_GROUP_CHAT` (optional): Enable group chat (default: true)
- `DASHBOARD_MCP_DEFAULT_CHANNELS` (optional): Default channels (default: ["general", "alerts", "handoffs"])
- `DASHBOARD_MCP_CORS_ORIGINS` (optional): CORS origins (default: ["*"])
- `DASHBOARD_MCP_AUTH_TOKEN` (optional): Authentication token

### Database Schema

The server uses the following PostgreSQL tables:

- `agent_registry`: Agent information and status
- `task_queue`: Task queue and execution details
- `channels`: Communication channels
- `messages`: Message history

### Fleet Configuration

The server can be configured via `fleet.yaml`:

```yaml
agents:
  - agent_id: "agent-001"
    name: "Data Processor"
    role: "analyst"
    capabilities: ["data_analysis", "visualization"]
    model: "gpt-4"
    config:
      temperature: 0.3
      max_tokens: 8192

default_channels: ["general", "alerts", "handoffs"]
```

## Architecture

### Components

1. **DashboardCore**: Core business logic, database operations, and WebSocket management
2. **FastMCP Server**: MCP protocol implementation with tool registration
3. **FastAPI Application**: WebSocket endpoints and health checks
4. **Database**: PostgreSQL for persistence, Redis for WebSocket pub/sub

### Data Flow

1. Agents register via MCP tools or WebSocket
2. Tasks are created via MCP tools and stored in database
3. Real-time updates are broadcast via WebSocket channels
4. Fleet status is computed and exposed via MCP tools

## Monitoring

### Health Check

The server provides a health check endpoint at `/health`:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "database": true,
  "redis": true,
  "uptime": "unknown"
}
```

### Metrics

The server tracks and reports:

- Agent registration and heartbeat status
- Task creation, execution, and completion rates
- Message throughput and channel activity
- Token usage across all agents
- System health and resource utilization

## Security

### Authentication

The server supports optional authentication via the `DASHBOARD_MCP_AUTH_TOKEN` environment variable.

### Authorization

Channels can be configured with specific members for access control.

### HTTPS

For production deployment, run behind a reverse proxy with HTTPS (nginx, Apache, etc.).

## Deployment

### Production

For production deployment:

1. Use HTTPS with a valid SSL certificate
2. Configure a reverse proxy (nginx, Apache)
3. Set up monitoring and logging
4. Configure backup and disaster recovery
5. Set appropriate resource limits

### Docker

Build and run with Docker:

```bash
docker build -t dashboard-mcp:latest .
docker run -d -p 8000:8000 dashboard-mcp
```

### Kubernetes

For Kubernetes deployment:

1. Create a Docker image with proper labels
2. Configure PersistentVolumeClaims for PostgreSQL
3. Set up ConfigMap and Secret for configuration
4. Configure HorizontalPodAutoscaler
5. Set up monitoring and alerts

## Troubleshooting

### Common Issues

#### Database Connection Errors

Check that:
- PostgreSQL is running and accessible
- Database credentials are correct
- Database exists and has proper permissions

#### WebSocket Connection Issues

Check that:
- Redis is running and accessible
- Network connectivity between services
- Firewall rules allow WebSocket connections

#### MCP Tool Errors

Check that:
- The MCP Inspector is running
- Tool schemas are valid
- Server is properly initialized

### Logging

The server logs to stdout with structured JSON format. Configure logging levels:

- `INFO`: Standard operational information
- `DEBUG`: Detailed debugging information
- `ERROR`: Error conditions and failures

## Migration Guide

### From Previous Versions

See `CHANGELOG.md` for migration information between versions.

## Support

For issues and support:

- Check the documentation
- Review the logs
- Test with MCP Inspector
- Verify database connectivity
- Ensure all dependencies are properly installed

## License

This project is licensed under the MIT License. See `LICENSE` for details.